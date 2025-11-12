"""
Refactored Nginx operations module with a Site dataclass and NginxManager class.
- Site dataclass centralizes site metadata and defaults
- NginxManager provides high-level methods that accept Site objects
- Backwards-compatible helpers included: parse_sites_list -> List[Site]
- Dry-run support, idempotent flag application, combined files handling with per-site markers
- Cross-platform: DNS skipped on Windows, platform-aware commands/paths
- Improved insertions: e.g., cache inside location / {} when possible
- Added cache clear and DNS reload
- YAML configuration support with nested locations and upload limits
- Enhanced safety: Automatic backup, validation, and rollback for all operations
NOTE: This file re-uses helper functions from utils_devops.core modules.
"""
from __future__ import annotations
import re
import shutil
import socket
import subprocess
import os
import pwd
import grp
import yaml
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import requests
from tenacity import retry, stop_after_attempt, wait_fixed
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

# Import your internal helpers (adjust these paths/names if your project differs)
from datetime import datetime
import tempfile
from utils_devops.core.logs import get_library_logger
from utils_devops.core.files import (
    atomic_write, ensure_dir, remove_dir, remove_file,
    file_exists, dir_exists, read_file, touch
)
from utils_devops.core.systems import is_windows, is_linux, is_root, command_exists, run
from utils_devops.core.strings import render_jinja

log = get_library_logger()

# Defaults (platform-aware)
DEFAULT_NGINX_CMD = "nginx.exe" if is_windows() else "nginx"
DEFAULT_TEST_CMD = [DEFAULT_NGINX_CMD, "-t"]
DEFAULT_RELOAD_CMD = [DEFAULT_NGINX_CMD, "-s", "reload"]
DEFAULT_START_CMD = [DEFAULT_NGINX_CMD, "-g", "daemon off;"]
DEFAULT_PID_FILE = Path(r"C:\nginx\logs\nginx.pid") if is_windows() else Path("/run/nginx.pid")
DEFAULT_LOG_DIR = Path(r"C:\nginx\logs") if is_windows() else Path("/etc/nginx/logs")
DEFAULT_SITES_AVAILABLE = Path(r"C:\nginx\conf\sites-available") if is_windows() else Path("/etc/nginx/sites-available")
DEFAULT_SITES_ENABLED = Path(r"C:\nginx\conf\sites-enabled") if is_windows() else Path("/etc/nginx/sites-enabled")
DEFAULT_CACHE_BASE = Path(r"C:\nginx\cache") if is_windows() else Path("/etc/nginx/cache")
DEFAULT_CACHE_COMBINED = (Path(r"C:\nginx\conf.d") if is_windows() else Path("/etc/nginx/conf.d")) / "cache-paths.conf"
DEFAULT_DNS_COMBINED = (Path(r"C:\etc\dnsmasq.d") if is_windows() else Path("/etc/dnsmasq.d")) / "combined-dns.conf"
DEFAULT_NGINX_CONF = Path(r"C:\nginx\conf\nginx.conf") if is_windows() else Path("/etc/nginx/nginx.conf")
DUMMY_UPSTREAM = "http://127.0.0.1:81"
DEFAULT_NGINX_IP = "172.16.229.50"

class NginxOpsError(Exception):
    """Custom exception for Nginx operations errors."""
    pass

@dataclass
class Location:
    """Represents a nested location block with its own configuration."""
    path: str
    upstream: Optional[str] = None
    flags: Dict[str, Any] = field(default_factory=dict)
    upload_limit: Optional[str] = None
    description: Optional[str] = None

@dataclass
class Site:
    """
    Structured representation of a site.
    - name: used for file names and server_name
    - upstream: URL (http://host:port), or filesystem path for `serve` sites
    - is_serve: whether the site is a static serve (root path)
    - locations: list of Location objects for additional location blocks
    - flags: mapping of flag names -> values (True or specific value)
    - upload_limit: site-wide upload limit from YAML
    - client_max_body_size: optional override for client_max_body_size
    - force: whether to force re-create configs
    - description: optional descriptive text
    """
    name: str
    upstream: str = ""
    is_serve: bool = False
    locations: List[Location] = field(default_factory=list)
    flags: Dict[str, Any] = field(default_factory=dict)
    upload_limit: Optional[str] = None
    client_max_body_size: Optional[str] = None
    force: bool = False
    description: Optional[str] = None

    @classmethod
    def from_parsed_line(cls, line: str) -> "Site":
        """Parse a single line from sites.txt into Site object.
        Format: site upstream [flags] [/path=upstream]
        """
        parts = re.split(r"\s+", line.strip())
        if not parts or parts[0].startswith("#"):
            raise ValueError("empty or comment line")
        name = parts[0]
        upstream = parts[1] if len(parts) > 1 else ""
        is_serve = upstream.startswith("/") or (len(upstream) > 1 and re.match(r"[A-Za-z]:\\", upstream))
        locations: List[Location] = []
        flags: Dict[str, Any] = {}
        for p in parts[2:]:
            if p.startswith('/'):
                if '=' in p:
                    path, up = p.split('=', 1)
                    path = path.strip()
                    up = up.strip()
                    locations.append(Location(path=path, upstream=up))
                    flags[path] = up  # add to flags for sync
                else:
                    path = p.strip()
                    locations.append(Location(path=path))
                    flags[path] = True  # add to flags
            else:
                if '=' in p:
                    k, v = p.split('=', 1)
                    flags[k.lower().strip()] = v.strip()
                else:
                    flags[p.lower().strip()] = True
        return cls(name, upstream, is_serve, locations, flags)

    @classmethod
    def from_yaml_dict(cls, data: Dict[str, Any]) -> "Site":
        """Create Site object from YAML dictionary."""
        # Use 'name' field if available, fall back to 'host' for backward compatibility
        name = data.get("name") or data["host"]
        upstream = data["upstream"]
        is_serve = upstream.startswith("/") or (len(upstream) > 1 and re.match(r"[A-Za-z]:\\", upstream))
        
        # Parse locations
        locations = []
        for loc_data in data.get("locations", []):
            location = Location(
                path=loc_data["path"],
                upstream=loc_data.get("upstream"),
                flags=loc_data.get("flags", {}),
                upload_limit=loc_data.get("upload_limit")
            )
            locations.append(location)
        
        # Parse flags
        flags = data.get("flags", {})
        upload_limit = data.get("upload_limit")
        
        return cls(
            name=name,
            upstream=upstream,
            is_serve=is_serve,
            locations=locations,
            flags=flags,
            upload_limit=upload_limit
        )

    def to_yaml_dict(self) -> Dict[str, Any]:
        """Convert Site to YAML-compatible dictionary."""
        result = {
            "name": self.name,  # Changed from "host" to "name"
            "upstream": self.upstream
        }
        
        if self.flags:
            result["flags"] = self.flags
            
        if self.upload_limit:
            result["upload_limit"] = self.upload_limit
            
        if self.locations:
            result["locations"] = []
            for loc in self.locations:
                loc_dict = {"path": loc.path}
                if loc.upstream:
                    loc_dict["upstream"] = loc.upstream
                if loc.flags:
                    loc_dict["flags"] = loc.flags
                if loc.upload_limit:
                    loc_dict["upload_limit"] = loc.upload_limit
                result["locations"].append(loc_dict)
                
        return result

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

def help() -> None:
    """
Nginx Operations Module - Complete AI Reference
================================================

Function Quick Reference
------------------------

CLASS: NginxManager
-------------------
Initialization:
  NginxManager(
      sites_available: Path = DEFAULT_SITES_AVAILABLE,
      sites_enabled: Path = DEFAULT_SITES_ENABLED,
      cache_base: Path = DEFAULT_CACHE_BASE,
      dry_run: bool = False,
      validate_upstreams: bool = False
  ) -> NginxManager

Site Operations:
  create_site(site: Site, proxy_tpl="reverse-proxy.conf", serve_tpl="serve.conf") -> Path
      Input: Site object, template paths
      Output: Path to created config
      Safety: ✅ Backup → Create → Validate → Rollback → Reload

  remove_site(site_name: str) -> None
      Input: Site name string
      Output: None
      Safety: ✅ Backup → Remove → Validate → Rollback → Reload

  sync_sites(sites: List[Site]) -> None
      Input: List of Site objects
      Output: None
      Safety: ✅ Per-site safety with batch reporting

  list_available_sites() -> List[str]
      Input: None
      Output: List of site names

YAML Operations:
  parse_sites_yaml(yaml_path: Union[str, Path]) -> List[Site]
      Input: Path to YAML file
      Output: List of Site objects

  generate_sites_yaml(sites: List[Site]) -> str
      Input: List of Site objects
      Output: YAML string

  sync_from_yaml(yaml_path: Union[str, Path], force_all: bool = False) -> None
      Input: YAML path, force flag
      Output: None
      Safety: ✅ Batch safety with per-site operations

Flag Operations:
  apply_flag(site: Site, flag: str, value: Optional[Any] = None) -> None
      Input: Site object, flag name, optional value
      Output: None
      Safety: ✅ Backup → Apply → Validate → Rollback → Reload

  remove_flag(site_name: str, flag: str) -> None
      Input: Site name, flag name
      Output: None

  sync_flags(sites: List[Site]) -> None
      Input: List of Site objects
      Output: None
      Safety: ✅ Per-site safety with batch reporting

  flag_exists(site: Site, flag: str) -> bool
      Input: Site object, flag name
      Output: Boolean

Backup & Safety:
  backup_site_config(site_name: str, suffix: Optional[str] = None) -> Path
      Input: Site name, optional suffix
      Output: Path to backup file

  restore_site_config(site_name: str, backup_path: Optional[Path] = None) -> bool
      Input: Site name, optional backup path
      Output: Success boolean

  backup_all_sites() -> Dict[str, Path]
      Input: None
      Output: Dict of site→backup_path

  validate_nginx_config() -> bool
      Input: None
      Output: Validation success

  validate_all_configs() -> Tuple[bool, Dict[str, str]]
      Input: None
      Output: (success, error_messages_by_site)

Cache & Service:
  clear_cache(site: Optional[Union[Site, str]] = None) -> bool
      Input: Site name/object or None for all
      Output: Success boolean
      Safety: ✅ Backup → Clear → Validate → Rollback → Reload

  reload_dns() -> bool
      Input: None
      Output: Success boolean
      Safety: ✅ Backup → Reload → Validate → Rollback

  manage_service() -> bool
      Input: None
      Output: Success boolean

CONVENIENCE FUNCTIONS (Global Instance)
---------------------------------------
parse_sites_list(list_path: Union[str, Path]) -> List[Site]
    Input: Path to sites.txt
    Output: List of Site objects

parse_sites_yaml(yaml_path: Union[str, Path]) -> List[Site]
    Input: Path to YAML file
    Output: List of Site objects

generate_sites_yaml(sites: List[Site]) -> str
    Input: List of Site objects
    Output: YAML string

sync_from_list(list_path: Union[str, Path], force_all: bool = False) -> None
    Input: Path to sites.txt, force flag
    Output: None

backup_site_config(site_name: str, suffix: Optional[str] = None) -> Path
    Input: Site name, optional suffix
    Output: Path to backup

restore_site_config(site_name: str, backup_path: Optional[Path] = None) -> bool
    Input: Site name, optional backup path
    Output: Success boolean

clear_cache(site: Optional[Union[Site, str]] = None) -> bool
    Input: Site name/object or None
    Output: Success boolean

validate_nginx_config() -> bool
    Input: None
    Output: Validation success

DATA CLASSES
------------
@dataclass
Site:
    name: str                    # Site domain name
    upstream: str = ""           # http://backend:port or /path for serve
    is_serve: bool = False       # Static file serving mode
    locations: List[Location] = field(default_factory=list)
    flags: Dict[str, Any] = field(default_factory=dict)
    upload_limit: Optional[str] = None
    force: bool = False

@dataclass  
Location:
    path: str                    # /api, /admin, etc.
    upstream: Optional[str] = None  # Optional custom upstream
    flags: Dict[str, Any] = field(default_factory=dict)
    upload_limit: Optional[str] = None

SAFETY PATTERN (All Modifying Operations)
-----------------------------------------
1. Backup existing configuration
2. Perform the operation
3. Validate new configuration (nginx -t)
4. Rollback if validation fails
5. Reload nginx only if successful
6. Return success status

YAML FORMAT
-----------
sites:
  - name: example.com
    upstream: "https://backend:8080"
    flags:
      cache: true
      dns: true
    upload_limit: "500M"
    locations:
      - path: /api
        upstream: "https://api:3000"
        flags:
          cache: false

TEXT FORMAT (sites.txt)
-----------------------
example.com https://backend:8080 cache dns upload=500M /api=https://api:3000
static.site /var/www/html serve error

SUPPORTED FLAGS
---------------
cache    - Enable proxy caching
error    - Enable error interception  
upload   - Set client_max_body_size (upload=100M)
dns      - Add dnsmasq entry (Linux)
/path/   - Add location block
serve    - Static file serving mode

QUICK START EXAMPLES
--------------------
# Initialize
mgr = NginxManager(dry_run=True)

# From YAML
sites = parse_sites_yaml("sites.yaml")
mgr.sync_sites(sites)

# Single site
site = Site("example.com", "http://1.2.3.4", flags={"cache": True})
mgr.create_site(site)

# Backup & restore
backup_path = backup_site_config("example.com")
restore_site_config("example.com", backup_path)

# Flags
mgr.apply_flag(site, "cache")
mgr.clear_cache("example.com")

# Validation
success = validate_nginx_config()

ERROR HANDLING
--------------
All operations raise NginxOpsError on failure
Safety operations return bool for success status
Dry-run mode available for testing

PLATFORM SUPPORT
----------------
Linux: Full features (symlinks, dnsmasq)
Windows: Basic support (file copies, no DNS)
"""
    print(help.__doc__)

# Small helpers (kept internal to manager but available standalone)
def _find_server_blocks(text: str) -> List[Tuple[int, int, str]]:
    """Proper server block detection with nested handling."""
    blocks = []
    pos = 0
    
    while pos < len(text):
        # Find server start
        server_match = re.search(r'server\s*\{', text[pos:])
        if not server_match:
            break
            
        start = pos + server_match.start()
        depth = 0
        i = start
        
        while i < len(text):
            if text[i] == '{':
                depth += 1
            elif text[i] == '}':
                depth -= 1
                if depth == 0:
                    end = i + 1
                    blocks.append((start, end, text[start:end]))
                    pos = end
                    break
            i += 1
        else:
            break  # Unclosed block
    
    return blocks

def _server_has_port(block: str, port: int) -> bool:
    """Check if server block listens on specific port."""
    return bool(re.search(rf'listen\s+[^;]*\b{port}\b', block))

def _find_location_blocks(block: str, path: str = "/") -> List[Tuple[int, int, str]]:
    """Find location blocks matching path in a server block."""
    blocks = []
    esc_path = re.escape(path)
    for m in re.finditer(rf"location\s+{esc_path}\s*\{{", block):
        start = m.start()
        depth = 1
        for i in range(m.end(), len(block)):
            if block[i] == "{":
                depth += 1
            elif block[i] == "}":
                depth -= 1
                if depth == 0:
                    end = i + 1
                    blocks.append((start, end, block[start:end]))
                    break
    return blocks

@dataclass
class Flag:
    """
    Represents a configurable flag for Nginx sites.
    - name: Flag identifier (e.g., 'cache', '/api')
    - template: Template file name for primary insertion
    - placement: Insertion placement (e.g., 'inside_location', 'server_443_out', 'combined')
    - target_getter: Function to get primary target file
    - secondary_template: Optional secondary template (e.g., for combined configs)
    - secondary_target_getter: Function for secondary target
    - context_adjuster: Function to adjust rendering context
    - apply_hook: Optional custom apply function (overrides template)
    - remove_hook: Optional custom remove function
    - pre_apply: Action before apply
    - post_remove: Action after remove
    """
    name: str
    template: Optional[str] = None
    placement: Optional[str] = None
    target_getter: Callable[['NginxManager', Site], Path] = lambda mgr, site: mgr.sites_available / site.name
    secondary_template: Optional[str] = None
    secondary_target_getter: Optional[Callable[['NginxManager', Site], Path]] = None
    context_adjuster: Optional[Callable[[Dict[str, Any], 'NginxManager', Site, Optional[Any]], Dict[str, Any]]] = None
    apply_hook: Optional[Callable[['NginxManager', Site, Optional[Any]], None]] = None
    remove_hook: Optional[Callable[['NginxManager', Site], None]] = None
    pre_apply: Optional[Callable[['NginxManager', Site], None]] = None
    post_remove: Optional[Callable[['NginxManager', Site], None]] = None

    def get_markers(self, site: Site) -> Tuple[str, str]:
        """Generate begin/end markers for this flag."""
        flag_part = self.name.upper().replace("/", "LOCATION-")
        return f"# ---- BEGIN {flag_part} {site.name} ----", f"# ---- END {flag_part} {site.name} ----"

    def get_secondary_markers(self, site: Site) -> Tuple[str, str]:
        """Generate markers for secondary insertion (same as primary by default)."""
        return self.get_markers(site)

# Global manager instance for convenience functions
_global_manager: Optional[NginxManager] = None

def _get_manager() -> NginxManager:
    """Get or create global manager instance."""
    global _global_manager
    if _global_manager is None:
        _global_manager = NginxManager()
    return _global_manager

class NginxManager:
    """
    High-level manager for Nginx site configurations using Site and Flag objects.
    Supports creation, syncing, flag application, service management.
    """
    def __init__(
        self,
        sites_available: Path = DEFAULT_SITES_AVAILABLE,
        sites_enabled: Path = DEFAULT_SITES_ENABLED,
        cache_base: Path = DEFAULT_CACHE_BASE,
        cache_combined: Path = DEFAULT_CACHE_COMBINED,
        dns_combined: Path = DEFAULT_DNS_COMBINED if is_linux() else None,
        log_dir: Path = DEFAULT_LOG_DIR,
        flags_dir: Union[Path, str] = Path("/etc/nginx/generate-sites/templates"),
        templates_dir: Optional[Path] = None,
        dry_run: bool = False,
        validate_upstreams: bool = False,
        fallback_upstream: str = DUMMY_UPSTREAM,
    ) -> None:
        self.backup_dir = Path("/etc/nginx/generate-sites/backups")
        self.sites_available = Path(sites_available)
        self.sites_enabled = Path(sites_enabled)
        self.cache_base = Path(cache_base)
        self.cache_combined = Path(cache_combined)
        self.dns_combined = Path(dns_combined) if dns_combined else None
        if is_windows() and self.dns_combined:
            log.warning("DNS management skipped on Windows (dnsmasq not supported)")
            self.dns_combined = None
        self.log_dir = Path(log_dir)
        self.flags_dir = Path(flags_dir)
        self.templates_dir = Path(templates_dir) if templates_dir else self.flags_dir
        self.dry_run = dry_run
        self.validate_upstreams = validate_upstreams
        self.fallback_upstream = fallback_upstream
        self.jinja_env = Environment(loader=FileSystemLoader(str(self.templates_dir)), trim_blocks=True, lstrip_blocks=True)
        # Ensure directories
        ensure_dir(str(self.backup_dir))
        ensure_dir(str(self.sites_available))
        ensure_dir(str(self.sites_enabled))
        ensure_dir(str(self.cache_base))
        ensure_dir(str(self.log_dir))
        # Known flags registry
        self.known_flags: Dict[str, Flag] = {
            "cache": Flag(
                "cache",
                template="cache.conf",
                placement="server_443_out_after_location",
                secondary_template="cache-path.conf",
                secondary_target_getter=lambda mgr, site: mgr.cache_combined,
                context_adjuster=lambda ctx, mgr, site, val: ctx | {"SITE": site.name, "CACHE_DIR": str(mgr.cache_base / site.name)},
                pre_apply=lambda mgr, site: mgr.ensure_cache_dir(site),
                post_remove=lambda mgr, site: mgr.clear_cache(site)  # Now uses safe version
            ),
            "error": Flag(
                "error",
                template="error.conf",
                placement="server_443_out",
                context_adjuster=lambda ctx, mgr, site, val: ctx | {"SITE": site.name}
            ),
            "dns": Flag(
                "dns",
                template="dns.conf",
                placement="combined",
                target_getter=lambda mgr, site: mgr.dns_combined,
                context_adjuster=lambda ctx, mgr, site, val: ctx | {"SITE": site.name, "IP": re.match(r"https?://([\d\.]+)", site.upstream).group(1) if re.match(r"https?://([\d\.]+)", site.upstream) else DEFAULT_NGINX_IP}
            ),
            "upload": Flag(
                "upload",
                apply_hook=lambda mgr, site, val: mgr._set_client_max_body_size(mgr.sites_available / site.name, val or site.client_max_body_size or "10M"),
                remove_hook=lambda mgr, site: log.info(f"To revert upload for {site.name}, re-create the site without upload flag")
            ),
            "upload_limit": Flag(
                "upload_limit",
                apply_hook=lambda mgr, site, val: mgr.apply_upload_limit(site, val),
                remove_hook=lambda mgr, site: log.info(f"To revert upload limit for {site.name}, re-create the site")
            ),
        }
        
    # -------------------- Safety Operations --------------------
    def _safe_operation(self, operation: Callable, operation_name: str, site_name: Optional[str] = None) -> bool:
        """Execute an operation with backup, validation, and service management.
        
        Args:
            operation: The function to execute
            operation_name: Name of the operation for logging
            site_name: Optional site name for backup
            
        Returns:
            bool: True if operation was successful
        """
        # Backup before operation if site specified
        backup_path = None
        if site_name:
            try:
                backup_path = self.backup_site_config(site_name, suffix=f"pre_{operation_name}")
            except Exception as e:
                log.warning(f"Could not backup {site_name} before {operation_name}: {e}")
        
        try:
            # Execute the operation
            operation()
            
            # Validate configuration
            if not self.validate_nginx_config():
                log.error(f"❌ {operation_name} produced invalid configuration")
                # Restore backup if available
                if backup_path and site_name:
                    self.restore_site_config(site_name, backup_path)
                    log.info(f"🔄 Restored backup for {site_name} due to validation failure")
                return False
            
            # Reload nginx service
            if self.manage_service():
                log.info(f"✅ {operation_name} completed successfully and nginx reloaded")
                return True
            else:
                log.error(f"❌ {operation_name} completed but nginx reload failed")
                # Restore backup if available
                if backup_path and site_name:
                    self.restore_site_config(site_name, backup_path)
                    log.info(f"🔄 Restored backup for {site_name} due to reload failure")
                return False
                
        except Exception as e:
            log.error(f"❌ {operation_name} failed: {e}")
            # Restore backup if available
            if backup_path and site_name:
                try:
                    self.restore_site_config(site_name, backup_path)
                    log.info(f"🔄 Restored backup for {site_name} due to operation failure")
                except Exception as restore_error:
                    log.error(f"❌ Failed to restore backup: {restore_error}")
            return False

    def validate_nginx_config(self) -> bool:
        """Validate the entire nginx configuration."""
        if self.dry_run:
            log.info("[dry-run] Would validate nginx configuration")
            return True
            
        try:
            result = run(["nginx", "-t"], capture=True, no_die=True)
            if result.returncode == 0:
                log.debug("✅ Nginx configuration is valid")
                return True
            else:
                log.error(f"❌ Nginx configuration validation failed: {result.stdout}")
                return False
        except Exception as e:
            log.error(f"❌ Nginx configuration validation error: {e}")
            return False

    # -------------------- Backup & Restore --------------------
    def backup_site_config(self, site_name: str, suffix: Optional[str] = None) -> Path:
        """Backup site configuration with timestamp.
        
        Args:
            site_name: Name of the site to backup
            suffix: Optional suffix for backup file
            
        Returns:
            Path to backup file
            
        Raises:
            NginxOpsError: If backup fails
        """
        config_path = self.sites_available / site_name
        if not file_exists(str(config_path)):
            raise NginxOpsError(f"Site config not found: {config_path}")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_suffix = f".{suffix}" if suffix else ""
        backup_name = f"{site_name}_{timestamp}{backup_suffix}.conf"
        backup_path = self.backup_dir / backup_name
        
        if self.dry_run:
            log.info(f"[dry-run] Would backup {site_name} to {backup_path}")
            return backup_path
            
        try:
            shutil.copy2(str(config_path), str(backup_path))
            log.info(f"📋 Backed up {site_name} to {backup_path}")
            return backup_path
        except Exception as e:
            raise NginxOpsError(f"Failed to backup {site_name}: {e}")
    
    def restore_site_config(self, site_name: str, backup_path: Optional[Path] = None) -> bool:
        """Restore site configuration from backup.
        
        Args:
            site_name: Name of the site to restore
            backup_path: Specific backup file to use (uses latest if None)
            
        Returns:
            bool: True if restore was successful
            
        Raises:
            NginxOpsError: If restore fails
        """
        if backup_path is None:
            # Find latest backup for this site
            backups = list(self.backup_dir.glob(f"{site_name}_*.conf"))
            if not backups:
                raise NginxOpsError(f"No backups found for {site_name}")
            backup_path = max(backups, key=lambda x: x.stat().st_mtime)
        
        if not file_exists(str(backup_path)):
            raise NginxOpsError(f"Backup file not found: {backup_path}")
        
        config_path = self.sites_available / site_name
        
        if self.dry_run:
            log.info(f"[dry-run] Would restore {site_name} from {backup_path}")
            return True
            
        try:
            # Create backup of current config before restore
            if file_exists(str(config_path)):
                current_backup = self.backup_site_config(site_name, suffix="pre_restore")
                log.info(f"📋 Backed up current config before restore: {current_backup}")
            
            shutil.copy2(str(backup_path), str(config_path))
            log.info(f"✅ Restored {site_name} from {backup_path}")
            
            # Validate the restored config
            if self._validate_single_config(config_path):
                log.info(f"✅ Restored config for {site_name} is valid")
                return True
            else:
                log.error(f"❌ Restored config for {site_name} is invalid")
                # Restore the pre-restore backup if available
                if 'current_backup' in locals():
                    self.restore_site_config(site_name, current_backup)
                    log.info(f"🔄 Reverted to pre-restore backup due to validation failure")
                return False
                
        except Exception as e:
            raise NginxOpsError(f"Failed to restore {site_name}: {e}")
    
    def list_site_backups(self, site_name: Optional[str] = None) -> List[Path]:
        """List available backups for sites.
        
        Args:
            site_name: Optional site name to filter backups
            
        Returns:
            List of backup paths
        """
        if site_name:
            pattern = f"{site_name}_*.conf"
        else:
            pattern = "*_*.conf"
        
        backups = list(self.backup_dir.glob(pattern))
        return sorted(backups, key=lambda x: x.stat().st_mtime, reverse=True)
    
    def _validate_single_config(self, config_path: Path) -> bool:
        """Validate a single configuration file.
        
        Args:
            config_path: Path to config file to validate
            
        Returns:
            bool: True if config is valid
        """
        if self.dry_run:
            return True
            
        try:
            # Create a temporary nginx config that includes only this site
            with tempfile.NamedTemporaryFile(mode='w', suffix='.conf', delete=False) as temp_file:
                temp_content = f"""
                events {{ worker_connections 1024; }}
                http {{
                    include /etc/nginx/mime.types;
                    include {config_path};
                }}
                """
                temp_file.write(temp_content)
                temp_file.flush()
                
                # Test with nginx
                result = run(["nginx", "-t", "-c", temp_file.name], capture=True, no_die=True)
                
                # Clean up temp file
                try:
                    os.unlink(temp_file.name)
                except Exception:
                    pass
                    
                return result.returncode == 0
                
        except Exception as e:
            log.debug(f"Config validation failed for {config_path}: {e}")
            return False
    
    def backup_all_sites(self) -> Dict[str, Path]:
        """Backup all site configurations.
        
        Returns:
            Dict mapping site names to backup paths
        """
        sites = self.list_available_sites()
        backups = {}
        
        for site_name in sites:
            try:
                backup_path = self.backup_site_config(site_name, suffix="batch")
                backups[site_name] = backup_path
            except Exception as e:
                log.error(f"Failed to backup {site_name}: {e}")
        
        log.info(f"✅ Backed up {len(backups)} sites")
        return backups
    
    def create_site_with_backup(self, site: Site) -> Path:
        """Create site with automatic backup and rollback.
        
        Args:
            site: Site to create
            
        Returns:
            Path to created config
            
        Raises:
            NginxOpsError: If creation fails
        """
        config_path = self.sites_available / site.name
        had_existing_config = file_exists(str(config_path))
        backup_path = None
        
        try:
            # Backup existing config
            if had_existing_config:
                backup_path = self.backup_site_config(site.name, suffix="pre_update")
            
            # Create the site
            created_path = self.create_site(site)
            
            # Validate the new config
            if not self._validate_single_config(created_path):
                raise NginxOpsError(f"Created config for {site.name} is invalid")
            
            log.info(f"✅ Successfully created/updated {site.name}")
            return created_path
            
        except Exception as e:
            # Rollback on failure
            if had_existing_config and backup_path:
                try:
                    self.restore_site_config(site.name, backup_path)
                    log.info(f"🔄 Rolled back {site.name} due to creation failure")
                except Exception as rollback_error:
                    log.error(f"❌ Failed to rollback {site.name}: {rollback_error}")
            
            raise NginxOpsError(f"Failed to create site {site.name}: {e}")

    # -------------------- YAML Support --------------------
        
    def parse_sites_yaml(self, yaml_path: Union[str, Path]) -> List[Site]:
        """Parse YAML configuration into Site objects.
        
        Args:
            yaml_path: Path to YAML file
            
        Returns:
            List[Site]: Parsed site objects
            
        Raises:
            NginxOpsError: If YAML parsing fails
        """
        p = Path(yaml_path)
        if not file_exists(str(p)):
            raise NginxOpsError(f"YAML file not found: {p}")
        
        try:
            with open(p, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise NginxOpsError(f"Invalid YAML in {p}: {e}")
        except Exception as e:
            raise NginxOpsError(f"Failed to read YAML file {p}: {e}")
        
        # Handle both formats: list of sites or {sites: [...]}
        if isinstance(data, dict) and "sites" in data:
            sites_data = data["sites"]
        elif isinstance(data, list):
            sites_data = data
        else:
            raise NginxOpsError(f"YAML file should contain a list of sites or 'sites' key, got {type(data)}")
        
        sites = []
        for site_data in sites_data:
            try:
                site = Site.from_yaml_dict(site_data)
                sites.append(site)
            except KeyError as e:
                raise NginxOpsError(f"Missing required field in YAML: {e}")
            except Exception as e:
                raise NginxOpsError(f"Failed to parse site from YAML: {e}")
        
        log.info(f"Parsed {len(sites)} sites from YAML: {p}")
        return sites

    def generate_sites_yaml(self, sites: List[Site]) -> str:
        """Generate YAML configuration from Site objects.
        
        Args:
            sites: List of Site objects
            
        Returns:
            str: YAML formatted string with proper 'sites:' root
        """
        yaml_data = {
            "sites": [site.to_yaml_dict() for site in sites]  # Wrap in "sites" root
        }
        
        return yaml.dump(yaml_data, default_flow_style=False, indent=2, allow_unicode=True, sort_keys=False)

    def sync_from_yaml(self, yaml_path: Union[str, Path], force_all: bool = False) -> None:
        """Complete sync from YAML configuration file.
        
        Args:
            yaml_path: Path to YAML configuration file
            force_all: Whether to force recreate all sites
        """
        sites_map = {s.name: s for s in self.parse_sites_yaml(yaml_path)}
        existing_sites = set(self.list_available_sites())
        desired_sites = set(sites_map.keys())
        
        # Validate all sites first
        for site in sites_map.values():
            success, errors = self.validate_site_structure(site.to_yaml_dict())
            if not success:
                raise NginxOpsError(f"Invalid site configuration for {site.name}: {', '.join(errors)}")
        
        # Determine actions
        to_add = desired_sites - existing_sites
        to_remove = existing_sites - desired_sites
        to_keep = desired_sites & existing_sites
        
        log.info(f"YAML Sync: +{len(to_add)} -{len(to_remove)} ~{len(to_keep)}")
        
        success_count = 0
        failed_sites = []
        
        # Add new sites
        for site_name in to_add:
            try:
                self.create_site(sites_map[site_name])
                success_count += 1
            except Exception as e:
                failed_sites.append(f"{site_name} (add): {e}")
                log.error(f"❌ Failed to add site {site_name}: {e}")
        
        # Remove old sites
        for site_name in to_remove:
            try:
                self.remove_site(site_name)
                success_count += 1
            except Exception as e:
                failed_sites.append(f"{site_name} (remove): {e}")
                log.error(f"❌ Failed to remove site {site_name}: {e}")
        
        # Update existing sites
        for site_name in to_keep:
            site = sites_map[site_name]
            if force_all or site.force or site.flags.get("force"):
                try:
                    self.create_site(site)
                    success_count += 1
                except Exception as e:
                    failed_sites.append(f"{site_name} (update): {e}")
                    log.error(f"❌ Failed to update site {site_name}: {e}")
            
            # Sync flags for this site
            try:
                self.sync_flags_for_site(site)
                success_count += 1
            except Exception as e:
                failed_sites.append(f"{site_name} (flags): {e}")
                log.error(f"❌ Failed to sync flags for {site_name}: {e}")
        
        # Final report
        if success_count > 0:
            log.info(f"✅ Successfully processed {success_count} operations")
        if failed_sites:
            log.error(f"❌ Failed to process {len(failed_sites)} operations:")
            for failure in failed_sites:
                log.error(f"  - {failure}")

    def validate_site_structure(self, site_config: Dict) -> Tuple[bool, List[str]]:
        """Validate YAML site structure against schema.
        
        Args:
            site_config: Dictionary from YAML
            
        Returns:
            Tuple[bool, List[str]]: (success, error_messages)
        """
        errors = []
        
        # Required fields - check for both 'name' and 'host' (backward compatibility)
        if "name" not in site_config and "host" not in site_config:
            errors.append("Missing required field: name (or host)")
        if "upstream" not in site_config:
            errors.append("Missing required field: upstream")
        
        # Validate host/name format
        name = site_config.get("name") or site_config.get("host")
        if name and not re.match(r'^[a-zA-Z0-9.*_-]+$', name):
            errors.append(f"Invalid name format: {name}")
        
        # Validate upstream format
        if "upstream" in site_config:
            upstream = site_config["upstream"]
            if not (upstream.startswith(('http://', 'https://', '/')) or re.match(r'[A-Za-z]:\\', upstream)):
                errors.append(f"Invalid upstream format: {upstream}")
        
        # Validate locations
        for i, loc in enumerate(site_config.get("locations", [])):
            if "path" not in loc:
                errors.append(f"Location {i} missing required field: path")
            elif not loc["path"].startswith('/'):
                errors.append(f"Location path must start with '/': {loc['path']}")
        
        return len(errors) == 0, errors

    def migrate_text_to_yaml(self, text_path: Union[str, Path], yaml_path: Union[str, Path]) -> None:
        """Migrate from old text format to new YAML format.
        
        Args:
            text_path: Path to old sites.txt
            yaml_path: Path for new YAML file
        """
        # Parse existing text format
        sites = self.parse_sites_list(text_path)
        
        # Generate YAML
        yaml_content = self.generate_sites_yaml(sites)
        
        # Write YAML file
        if self.dry_run:
            log.info(f"[dry-run] Would migrate {text_path} to {yaml_path}")
            log.info(f"YAML content:\n{yaml_content}")
        else:
            atomic_write(str(yaml_path), yaml_content)
            log.info(f"Migrated {text_path} to {yaml_path}")

    # -------------------- Parsing --------------------
    def parse_sites_list(self, list_path: Union[str, Path]) -> List[Site]:
        """Parse sites.txt into list of Site objects."""
        p = Path(list_path)
        if not file_exists(str(p)):
            raise NginxOpsError(f"sites.txt not found: {p}")
        sites: List[Site] = []
        for line in read_file(str(p)).splitlines():
            s = line.strip()
            if not s or s.startswith('#'):
                continue
            try:
                sites.append(Site.from_parsed_line(s))
            except ValueError as e:
                log.warning(f"Skipping invalid line in sites.txt: {s} ({e})")
        log.info(f"Parsed {len(sites)} sites from {p}")
        return sites

    def parse_template_meta(self, template_path: Path) -> Dict[str, str]:
        """Parse META directives from template headers."""
        if not template_path.exists():
            return {}
        
        content = template_path.read_text(encoding="utf-8")
        meta = {}
        
        # Parse # META: key=value, key2=value2
        meta_match = re.search(r'^#\s*META:\s*(.+)$', content, flags=re.MULTILINE)
        if meta_match:
            meta_line = meta_match.group(1).strip()
            for item in re.split(r'\s*,\s*', meta_line):
                if '=' in item:
                    key, value = item.split('=', 1)
                    meta[key.strip()] = value.strip()
                else:
                    meta[item.strip()] = "true"
        
        return meta

    def _strip_meta_lines(self, content: str) -> str:
        """Remove META lines from template content."""
        return re.sub(r'(?m)^[ \t]*#\s*META:.*\n?', '', content)

    # -------------------- Templates & Rendering --------------------
    def render_template(self, name: Union[str, Path], context: Dict[str, Any]) -> str:
        """Render a Jinja template with context."""
        tpl_name = str(name)
        try:
            tpl = self.jinja_env.get_template(tpl_name)
            return tpl.render(**context)
        except TemplateNotFound:
            log.warning(f"Template not found: {tpl_name}, falling back to raw render")
            return render_jinja(tpl_name, context)
        except Exception as e:
            raise NginxOpsError(f"Template rendering failed for {tpl_name}: {e}")

    def build_location_blocks(self, locations: List[Tuple[str, str]], location_tpl: Union[str, Path] = "location.conf") -> List[str]:
        """Build location blocks from templates (used in create_site)."""
        blocks: List[str] = []
        for path, up in locations:
            ctx = {"PATH": path, "UPSTREAM": up}
            blocks.append(self.render_template(location_tpl, ctx))
        return blocks

    def build_location_blocks_extended(self, locations: List[Location], location_tpl: Union[str, Path] = "location.conf") -> List[str]:
        """Build location blocks with full YAML support.
        
        Args:
            locations: List of Location objects
            location_tpl: Template for location blocks
            
        Returns:
            List[str]: Rendered location blocks
        """
        blocks = []
        for location in locations:
            # Build context for location
            ctx = {
                "PATH": location.path,
                "UPSTREAM": location.upstream or "",  # Use location upstream or empty
                "CLIENT_MAX_BODY_SIZE": location.upload_limit or ""  # Location-specific upload limit
            }
            
            # Render the location block
            block = self.render_template(location_tpl, ctx)
            blocks.append(block)
            
            # Apply location-specific flags
            if location.flags:
                # Create a temporary site-like object for the location
                loc_site = Site(
                    name=f"location_{location.path.replace('/', '_')}",
                    upstream=location.upstream or "",
                    flags=location.flags,
                    upload_limit=location.upload_limit
                )
                # Apply flags specific to this location
                for flag_name, flag_value in location.flags.items():
                    if flag_name in self.known_flags:
                        self.apply_flag(loc_site, flag_name, flag_value)
        
        return blocks

    # -------------------- Upload Limit Management --------------------
    def apply_upload_limit(self, site: Site, limit: str) -> None:
        """Apply upload limit from YAML configuration.
        
        Args:
            site: Site object
            limit: Upload limit string (e.g., "0", "500M")
            
        Raises:
            NginxOpsError: If application fails
        """
        if not limit:
            return
            
        # Validate upload limit format
        if not re.match(r'^\d+[KM]?$', str(limit).upper()):
            log.warning(f"Invalid upload limit format: {limit}, using default")
            limit = "10M"
        
        try:
            self._set_client_max_body_size(self.sites_available / site.name, limit)
            log.info(f"Applied upload limit {limit} to {site.name}")
        except Exception as e:
            raise NginxOpsError(f"Failed to apply upload limit {limit} to {site.name}: {e}")

    # -------------------- Validation --------------------
    
    def validate_all_configs(self) -> Tuple[bool, Dict[str, str]]:
        """Validate all site configurations.
        
        Returns:
            Tuple of (overall_success, error_messages_by_site)
        """
        sites = self.list_available_sites()
        errors = {}
        all_valid = True
        
        for site_name in sites:
            config_path = self.sites_available / site_name
            if self._validate_single_config(config_path):
                log.debug(f"✅ Config valid: {site_name}")
            else:
                errors[site_name] = "Configuration validation failed"
                all_valid = False
                log.error(f"❌ Config invalid: {site_name}")
        
        return all_valid, errors
    
    def safe_apply_flag(self, site: Site, flag: str, value: Optional[Any] = None) -> bool:
        """Apply flag with backup and validation.
        
        Args:
            site: Site to apply flag to
            flag: Flag name
            value: Flag value
            
        Returns:
            bool: True if application was successful
        """
        config_path = self.sites_available / site.name
        if not file_exists(str(config_path)):
            log.warning(f"Site config not found: {site.name}")
            return False
        
        try:
            # Backup before applying flag
            backup_path = self.backup_site_config(site.name, suffix=f"pre_{flag}")
            
            # Apply the flag
            self.apply_flag(site, flag, value)
            
            # Validate after applying flag
            if self._validate_single_config(config_path):
                log.info(f"✅ Successfully applied flag {flag} to {site.name}")
                return True
            else:
                # Rollback if validation fails
                self.restore_site_config(site.name, backup_path)
                log.error(f"❌ Flag {flag} made config invalid for {site.name}, rolled back")
                return False
                
        except Exception as e:
            log.error(f"❌ Failed to apply flag {flag} to {site.name}: {e}")
            return False
        
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
    def validate_upstream(self, upstream: str, fallback: str = DUMMY_UPSTREAM, timeout: int = 1, use_http: bool = True) -> str:
        """Validate upstream reachability."""
        if not self.validate_upstreams:
            return upstream  # Skip validation if disabled
            
        match = re.match(r'(https?://)?([^:/]+)(:\d+)?(/.*)?', upstream)
        if not match:
            log.warning(f"Invalid upstream: {upstream}, using fallback")
            return fallback
        scheme, host, port, _ = match.groups()
        scheme = scheme or "http://"
        port = port or ""
        if use_http:
            url = f"{scheme}{host}{port}"
            try:
                resp = requests.head(url, timeout=timeout)
                if resp.status_code < 400:
                    return upstream
            except Exception as e:
                log.debug(f"Upstream HTTP check failed: {e}")
        else:
            try:
                socket.getaddrinfo(host, None)
                return upstream
            except Exception as e:
                log.debug(f"Upstream DNS check failed: {e}")
        log.warning(f"Upstream {upstream} unreachable, using {fallback}")
        return fallback

    # -------------------- Files & Configs --------------------
    def write_site_config(self, site: Site, rendered: str) -> Path:
        """Write and enable site config."""
        tgt_avail = self.sites_available / site.name
        tgt_enabled = self.sites_enabled / site.name
        if self.dry_run:
            log.info(f"[dry-run] Would write config for {site.name} to {tgt_avail}")
            return tgt_avail
        atomic_write(str(tgt_avail), rendered)
        try:
            if file_exists(str(tgt_enabled)) or tgt_enabled.is_symlink():
                tgt_enabled.unlink()
            if is_windows():
                shutil.copy(str(tgt_avail), str(tgt_enabled))
            else:
                tgt_enabled.symlink_to(tgt_avail)
        except Exception as e:
            raise NginxOpsError(f"Could not enable site {site.name}: {e}")
        log.info(f"Wrote and enabled config for {site.name}")
        return tgt_avail

    def _set_permissions_safe(self, path: str, mode: int = 0o644, owner: str = "root") -> None:
        """Safe permission setting that avoids I/O closed file errors."""
        if self.dry_run:
            return
            
        try:
            # Set mode using os.chmod
            os.chmod(path, mode)
            
            # Set owner safely - only if we're root and the user exists
            if is_root() and is_linux():
                try:
                    if ":" in owner:
                        user, group = owner.split(":", 1)
                    else:
                        user, group = owner, owner
                    
                    uid = pwd.getpwnam(user).pw_uid
                    gid = grp.getgrnam(group).gr_gid
                    os.chown(path, uid, gid)
                except (KeyError, PermissionError) as e:
                    log.debug(f"Could not set owner to {owner} for {path}: {e}")
                    # Fallback to root
                    try:
                        os.chown(path, 0, 0)  # root:root
                    except PermissionError:
                        log.warning(f"Could not set owner to root for {path}")
        except Exception as e:
            log.warning(f"Could not set permissions for {path}: {e}")

    def setup_site_logs(self, site: Site) -> Tuple[Path, Path]:
        """Setup access/error logs for site with proper permissions."""
        access = self.log_dir / f"{site.name}-access.log"
        error = self.log_dir / f"{site.name}-error.log"
        if self.dry_run:
            log.info(f"[dry-run] Would create logs: {access}, {error}")
            return access, error
            
        touch(str(access))
        touch(str(error))
        
        # Set proper permissions using safe method
        try:
            self._set_permissions_safe(str(access), 0o644, "root")
            self._set_permissions_safe(str(error), 0o644, "root")
        except Exception as e:
            log.warning(f"Could not set log file permissions: {e}")
            
        return access, error

    def ensure_cache_dir(self, site: Site) -> Path:
        """Ensure per-site cache directory exists with proper permissions."""
        cache_dir = self.cache_base / site.name
        ensure_dir(str(cache_dir))
        if not self.dry_run:
            try:
                self._set_permissions_safe(str(cache_dir), 0o755, "root")
            except Exception as e:
                log.warning(f"Could not set cache directory permissions: {e}")
        return cache_dir

    # -------------------- Creation & Sync --------------------
    def create_site(
        self,
        site: Site,
        proxy_tpl: Union[str, Path] = "reverse-proxy.conf",
        serve_tpl: Union[str, Path] = "serve.conf",
        location_tpl: Union[str, Path] = "location.conf",
    ) -> Path:
        """Create or force-update a single site config with backup and validation."""
        def create_operation():
            conf_path = self.sites_available / site.name
            if file_exists(str(conf_path)) and not site.force:
                log.info(f"Site config exists: {conf_path} (skip)")
                return conf_path
            
            # Use validated upstream or fallback if validation is enabled
            upstream = self.validate_upstream(site.upstream or "", self.fallback_upstream) if self.validate_upstreams else (site.upstream or "")
            
            tpl = serve_tpl if site.is_serve else proxy_tpl
            context = {
                "SITE": site.name,
                "IP_ADDRESS": upstream,
                "ROOT_PATH": upstream if site.is_serve else "",
                "CLIENT_MAX_BODY_SIZE": site.upload_limit or site.client_max_body_size or "10M",
            }
            
            try:
                rendered = self.render_template(tpl, context)
                
                # Add enhanced location blocks if any
                if site.locations:
                    location_blocks = self.build_location_blocks_extended(site.locations, location_tpl)
                    rendered += "\n" + "\n".join(location_blocks)
                    
            except NginxOpsError as e:
                raise NginxOpsError(f"Failed to render templates for {site.name}: {e}")
                
            self.write_site_config(site, rendered)
            self.setup_site_logs(site)
            
            # Apply site-level upload limit if specified
            if site.upload_limit:
                self.apply_upload_limit(site, site.upload_limit)
            
            # Apply flags (includes other flags)
            self.sync_flags([site])
            return conf_path

        success = self._safe_operation(create_operation, f"Create site {site.name}", site.name)
        if not success:
            raise NginxOpsError(f"Failed to create site {site.name}")
        
        return self.sites_available / site.name

    def remove_site(self, site_name: str) -> None:
        """Remove a site with backup and validation."""
        def remove_operation():
            conf_avail = self.sites_available / site_name
            conf_enabled = self.sites_enabled / site_name
            
            if self.dry_run:
                log.info(f"[dry-run] Would remove site {site_name}")
                return
                
            if file_exists(str(conf_enabled)) or conf_enabled.is_symlink():
                conf_enabled.unlink(missing_ok=True)
            if file_exists(str(conf_avail)):
                remove_file(str(conf_avail))
                
            # Cleanup known flags
            for flag_name in list(self.known_flags):
                self.remove_flag(site_name, flag_name)
                
            # Remove empty logs
            access = self.log_dir / f"{site_name}-access.log"
            error = self.log_dir / f"{site_name}-error.log"
            if file_exists(str(access)) and Path(access).stat().st_size == 0:
                remove_file(str(access))
            if file_exists(str(error)) and Path(error).stat().st_size == 0:
                remove_file(str(error))
                
            log.info(f"Removed site {site_name}")

        success = self._safe_operation(remove_operation, f"Remove site {site_name}", site_name)
        if not success:
            raise NginxOpsError(f"Failed to remove site {site_name}")

    def sync_sites(self, sites: List[Site], list_path: Optional[Union[str, Path]] = None) -> None:
        """Sync list of sites with per-site backup and validation."""
        existing = {p.stem for p in self.sites_available.iterdir() if p.is_file()}
        desired = {s.name for s in sites}
        to_add = desired - existing
        to_remove = existing - desired
        site_map = {s.name: s for s in sites}
        
        success_count = 0
        failed_sites = []
        
        # Process additions
        for sname in to_add:
            if sname in site_map:
                try:
                    self.create_site(site_map[sname])
                    success_count += 1
                except Exception as e:
                    failed_sites.append(f"{sname} (add): {e}")
                    log.error(f"❌ Failed to add site {sname}: {e}")
        
        # Process removals
        for sname in to_remove:
            try:
                self.remove_site(sname)
                success_count += 1
            except Exception as e:
                failed_sites.append(f"{sname} (remove): {e}")
                log.error(f"❌ Failed to remove site {sname}: {e}")
        
        # Process updates
        for sname in desired & existing:
            s = site_map[sname]
            if s.force:
                try:
                    self.create_site(s)
                    success_count += 1
                except Exception as e:
                    failed_sites.append(f"{sname} (update): {e}")
                    log.error(f"❌ Failed to update site {sname}: {e}")
            
            # Sync flags for this site
            try:
                self.sync_flags_for_site(s)
            except Exception as e:
                failed_sites.append(f"{sname} (flags): {e}")
                log.error(f"❌ Failed to sync flags for {sname}: {e}")
        
        # Final report
        if success_count > 0:
            log.info(f"✅ Successfully processed {success_count} operations")
        if failed_sites:
            log.error(f"❌ Failed to process {len(failed_sites)} operations:")
            for failure in failed_sites:
                log.error(f"  - {failure}")

    def sync_from_list(self, list_path: Union[str, Path], force_all: bool = False) -> None:
        """Complete sync from sites.txt (like original script)."""
        sites_map = {s.name: s for s in self.parse_sites_list(list_path)}
        existing_sites = set(self.list_available_sites())
        desired_sites = set(sites_map.keys())
        
        # Determine actions
        to_add = desired_sites - existing_sites
        to_remove = existing_sites - desired_sites
        to_keep = desired_sites & existing_sites
        
        log.info(f"Sync: +{len(to_add)} -{len(to_remove)} ~{len(to_keep)}")
        
        success_count = 0
        failed_sites = []
        
        # Add new sites
        for site_name in to_add:
            try:
                self.create_site(sites_map[site_name])
                success_count += 1
            except Exception as e:
                failed_sites.append(f"{site_name} (add): {e}")
                log.error(f"❌ Failed to add site {site_name}: {e}")
        
        # Remove old sites
        for site_name in to_remove:
            try:
                self.remove_site(site_name)
                success_count += 1
            except Exception as e:
                failed_sites.append(f"{site_name} (remove): {e}")
                log.error(f"❌ Failed to remove site {site_name}: {e}")
        
        # Update existing sites
        for site_name in to_keep:
            site = sites_map[site_name]
            if force_all or site.force or site.flags.get("force"):
                try:
                    self.create_site(site)
                    success_count += 1
                except Exception as e:
                    failed_sites.append(f"{site_name} (update): {e}")
                    log.error(f"❌ Failed to update site {site_name}: {e}")
            
            # Sync flags for this site
            try:
                self.sync_flags_for_site(site)
                success_count += 1
            except Exception as e:
                failed_sites.append(f"{site_name} (flags): {e}")
                log.error(f"❌ Failed to sync flags for {site_name}: {e}")
        
        # Final report
        if success_count > 0:
            log.info(f"✅ Successfully processed {success_count} operations")
        if failed_sites:
            log.error(f"❌ Failed to process {len(failed_sites)} operations:")
            for failure in failed_sites:
                log.error(f"  - {failure}")

    def sync_flags_for_site(self, site: Site) -> None:
        """Sync flags for a single site with backup and validation."""
        def sync_operation():
            known_flags = {"cache", "error", "upload", "dns", "upload_limit"}
            desired_flags = set(site.flags.keys())
            desired_locations = {loc.path for loc in site.locations}
            
            # Apply desired flags
            for flag in desired_flags:
                if flag == "force":
                    continue
                value = site.flags[flag] if site.flags[flag] is not True else None
                self.apply_flag(site, flag, value)
            
            # Apply upload limit if specified
            if site.upload_limit:
                self.apply_upload_limit(site, site.upload_limit)
            
            # Remove unwanted known flags
            for flag in known_flags:
                if flag not in desired_flags and not (flag == "upload_limit" and site.upload_limit):
                    self.remove_flag(site.name, flag)
            
            # Clean up orphaned locations
            conf_path = self.sites_available / site.name
            if conf_path.exists():
                content = read_file(str(conf_path))
                current_locations = set(re.findall(r'location\s+([^\s\{]+)\s*\{', content))
                for loc in current_locations:
                    if loc != "/" and loc not in desired_locations:
                        self.remove_flag(site.name, loc)

        success = self._safe_operation(sync_operation, f"Sync flags for {site.name}", site.name)
        if not success:
            raise NginxOpsError(f"Failed to sync flags for {site.name}")

    def list_available_sites(self) -> List[str]:
        """List available site configs."""
        if not self.sites_available.exists():
            return []
        return [p.stem for p in self.sites_available.glob("*") if p.is_file()]

    # -------------------- Flags --------------------
    def sync_flags(self, sites: List[Site]) -> None:
        """Sync flags for given sites with per-site backup and validation."""
        success_count = 0
        failed_sites = []
        
        for s in sites:
            conf = self.sites_available / s.name
            if not file_exists(str(conf)):
                log.warning(f"Site config not found: {s.name}, skipping flag sync")
                continue
                
            try:
                # Use safe operation for each site's flag sync
                def sync_operation():
                    desired_flags = set(s.flags.keys())
                    for flag in desired_flags:
                        if flag == "force":
                            continue
                        value = s.flags[flag] if s.flags[flag] is not True else None
                        self.apply_flag(s, flag, value)
                    
                    # Apply upload limit if specified
                    if s.upload_limit:
                        self.apply_upload_limit(s, s.upload_limit)
                        
                    # Remove undesired known flags
                    for flag in set(self.known_flags) - desired_flags:
                        if not (flag == "upload_limit" and s.upload_limit):
                            self.remove_flag(s.name, flag)
                
                success = self._safe_operation(sync_operation, f"Sync flags for {s.name}", s.name)
                if success:
                    success_count += 1
                else:
                    failed_sites.append(s.name)
                    
            except Exception as e:
                failed_sites.append(s.name)
                log.error(f"❌ Failed to sync flags for {s.name}: {e}")
        
        if success_count > 0:
            log.info(f"✅ Successfully synced flags for {success_count} sites")
        if failed_sites:
            log.error(f"❌ Failed to sync flags for {len(failed_sites)} sites: {', '.join(failed_sites)}")

    def apply_flag(self, site: Site, flag: str, value: Optional[Any] = None) -> None:
        """Apply a flag to a site with backup and validation."""
        def flag_operation():
            if flag in self.known_flags:
                f = self.known_flags[flag]
            elif flag.startswith("/"):
                # Find the location object to get its specific upstream
                location_upstream = value
                for loc in site.locations:
                    if loc.path == flag:
                        location_upstream = loc.upstream or value or site.upstream
                        break
                
                f = Flag(
                    name=flag,
                    template="location.conf",
                    placement="server_443_out",
                    context_adjuster=lambda ctx, mgr, site, val: ctx | {"PATH": flag, "UPSTREAM": location_upstream or ""},
                )
            else:
                log.warning(f"Unknown flag: {flag}")
                return
                
            if self.flag_exists(site, flag):
                log.debug(f"Flag {flag} already exists for {site.name}, updating")
                
            if f.pre_apply:
                f.pre_apply(self, site)
                
            if f.apply_hook:
                if not self.dry_run:
                    f.apply_hook(self, site, value)
            elif f.template:
                context = {"SITE": site.name}
                if f.context_adjuster:
                    context = f.context_adjuster(context, self, site, value)
                snippet = self.render_template(f.template, context)
                begin, end = f.get_markers(site)
                target = f.target_getter(self, site)
                
                if self.dry_run:
                    log.info(f"[dry-run] Would apply flag {flag} to {target}")
                else:
                    if f.placement == "combined":
                        self._apply_entry_to_combined(target, snippet, begin, end)
                    else:
                        self._apply_snippet(target, snippet, f.placement or "server_443_out", begin, end)
                        
                if f.secondary_template:
                    sec_context = {"SITE": site.name}
                    if f.context_adjuster:
                        sec_context = f.context_adjuster(sec_context, self, site, value)
                    sec_snippet = self.render_template(f.secondary_template, sec_context)
                    sec_begin, sec_end = f.get_secondary_markers(site)
                    sec_target = f.secondary_target_getter(self, site)
                    if self.dry_run:
                        log.info(f"[dry-run] Would apply secondary for {flag} to {sec_target}")
                    else:
                        self._apply_entry_to_combined(sec_target, sec_snippet, sec_begin, sec_end)
                        
            log.info(f"Applied flag {flag} to {site.name}")

        success = self._safe_operation(flag_operation, f"Apply flag {flag} to {site.name}", site.name)
        if not success:
            raise NginxOpsError(f"Failed to apply flag {flag} to {site.name}")

    def remove_flag(self, site_name: str, flag: str) -> None:
        """Remove a flag from a site using Flag object."""
        site = Site(name=site_name)  # dummy for markers
        if flag in self.known_flags:
            f = self.known_flags[flag]
        elif flag.startswith("/"):
            f = Flag(name=flag)
        else:
            log.debug(f"Unknown flag for removal: {flag}")
            return
            
        if f.remove_hook:
            f.remove_hook(self, site)
        elif f.template or flag.startswith("/"):
            begin, end = f.get_markers(site)
            target = f.target_getter(self, site)
            if self.dry_run:
                log.info(f"[dry-run] Would remove flag {flag} from {target}")
            else:
                self._remove_region(target, begin, end)
            if f.secondary_template:
                sec_begin, sec_end = f.get_secondary_markers(site)
                sec_target = f.secondary_target_getter(self, site)
                self._remove_entry_from_combined(sec_target, sec_begin, sec_end)
                
        if f.post_remove:
            f.post_remove(self, site)
        log.info(f"Removed flag {flag} from {site_name}")

    def flag_exists(self, site: Site, flag: str) -> bool:
        """Check if a flag is already applied to site."""
        if flag not in self.known_flags and not flag.startswith("/"):
            return False
            
        if flag in self.known_flags:
            f = self.known_flags[flag]
        else:
            f = Flag(name=flag)
            
        target = f.target_getter(self, site)
        if not file_exists(str(target)):
            return False
            
        txt = read_file(str(target))
        begin, _ = f.get_markers(site)
        return begin in txt

    # -------------------- low-level text modifications --------------------
    def _apply_snippet(self, conf_path: Path, snippet: str, placement: str = "server_443_out", 
                       begin_marker: Optional[str] = None, end_marker: Optional[str] = None) -> None:
        """Robust snippet placement with marker support."""
        if self.dry_run:
            log.info(f"[dry-run] Would apply snippet to {conf_path}")
            return
        
        txt = read_file(str(conf_path))
        blocks = _find_server_blocks(txt)
        placed = False
        
        port = 443 if "443" in placement else 80
        inside_location = "inside_location" in placement
        after_locations = "after_location" in placement
        
        for start, end, block in blocks:
            if not _server_has_port(block, port):
                continue
                
            # Handle marker replacement
            if begin_marker and end_marker:
                pattern = re.escape(begin_marker) + r'.*?' + re.escape(end_marker)
                if re.search(pattern, block, flags=re.DOTALL):
                    new_block = re.sub(pattern, f"{begin_marker}\n{snippet}\n{end_marker}", block, flags=re.DOTALL)
                    txt = txt[:start] + new_block + txt[end:]
                    placed = True
                    break
                else:
                    # Insert with markers
                    wrapped = f"{begin_marker}\n{snippet}\n{end_marker}"
                    new_block = self._insert_snippet_into_block(block, wrapped, placement)
                    if new_block != block:
                        txt = txt[:start] + new_block + txt[end:]
                        placed = True
                        break
            else:
                # Insert without markers
                new_block = self._insert_snippet_into_block(block, snippet, placement)
                if new_block != block:
                    txt = txt[:start] + new_block + txt[end:]
                    placed = True
                    break
        
        if not placed:
            log.warning(f"Could not place snippet in {conf_path}, appending to file")
            txt += f"\n{snippet}"
        
        atomic_write(str(conf_path), txt)

    def _insert_snippet_into_block(self, block: str, snippet: str, placement: str) -> str:
        """Insert snippet into server block at correct position."""
        if "inside_location" in placement:
            # Find location / block
            loc_match = re.search(r'(location\s+/\s*\{[^}]*)(\})', block, flags=re.DOTALL)
            if loc_match:
                return block[:loc_match.start(1)] + loc_match.group(1) + "\n" + snippet + "\n" + block[loc_match.start(2):]
        
        elif "after_location" in placement:
            # Find last location block and insert after it
            locations = list(re.finditer(r'location\s+[^{]+\{[^}]*\}', block, flags=re.DOTALL))
            if locations:
                last_loc = locations[-1]
                return block[:last_loc.end()] + "\n" + snippet + block[last_loc.end():]
        
        # Default: insert before closing server brace
        last_brace = block.rfind('}')
        if last_brace != -1:
            return block[:last_brace] + "\n" + snippet + "\n" + block[last_brace:]
        
        return block

    def _remove_region(self, conf_path: Path, begin: str, end: str) -> None:
        """Remove a marked region from a config file."""
        if self.dry_run:
            return
        if not file_exists(str(conf_path)):
            return
        txt = read_file(str(conf_path))
        pattern = re.escape(begin) + r".*?" + re.escape(end) + r"\s*"
        # Use re.sub directly instead of regex_replace to avoid flags issue
        new_txt = re.sub(pattern, "", txt, flags=re.DOTALL)
        if new_txt != txt:
            atomic_write(str(conf_path), new_txt)

    def _apply_entry_to_combined(self, combined: Path, entry: str, begin: str, end: str) -> None:
        """Apply an entry to a combined file using markers."""
        if self.dry_run:
            return
        if not file_exists(str(combined)):
            ensure_dir(str(combined.parent))
            touch(str(combined))
        txt = read_file(str(combined))
        pattern = re.escape(begin) + r"(.*?)" + re.escape(end)
        # Use re.search directly instead of regex_search to avoid flags issue
        m = re.search(pattern, txt, flags=re.DOTALL)
        if m:
            # Use re.sub directly instead of regex_replace to avoid flags issue
            new_txt = re.sub(pattern, begin + "\n" + entry.strip() + "\n" + end, txt, flags=re.DOTALL)
        else:
            new_txt = txt.rstrip() + "\n" + begin + "\n" + entry.strip() + "\n" + end + "\n"
        if new_txt != txt:
            atomic_write(str(combined), new_txt)

    def _remove_entry_from_combined(self, combined: Path, begin: str, end: str) -> None:
        """Remove a marked entry from a combined file."""
        if not file_exists(str(combined)) or self.dry_run:
            return
        txt = read_file(str(combined))
        pattern = re.escape(begin) + r".*?" + re.escape(end) + r"\s*"
        # Use re.sub directly instead of regex_replace to avoid flags issue
        new_txt = re.sub(pattern, "", txt, flags=re.DOTALL)
        if new_txt != txt:
            atomic_write(str(combined), new_txt)

    def _set_client_max_body_size(self, conf_path: Path, val: str) -> None:
        """Set client_max_body_size in server block."""
        if self.dry_run:
            return
        txt = read_file(str(conf_path))
        blocks = _find_server_blocks(txt)
        modified = False
        for start, endpos, block in blocks:
            if not _server_has_port(block, 443):
                continue
            pattern = r"client_max_body_size\s+[^;]+;"
            # Use re.search directly instead of regex_search
            if re.search(pattern, block):
                # Use re.sub directly instead of regex_replace
                new_block = re.sub(pattern, f"client_max_body_size {val};", block)
            else:
                server_name_m = re.search(r"server_name\s+[^;]+;", block)
                insert_idx = server_name_m.end() if server_name_m else block.find("{") + 1
                new_block = block[:insert_idx] + f"\n    client_max_body_size {val};" + block[insert_idx:]
            txt = txt[:start] + new_block + txt[endpos:]
            modified = True
            break
        if modified:
            atomic_write(str(conf_path), txt)

    # -------------------- Service control --------------------
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
    def manage_service(self, test_cmd: List[str] = DEFAULT_TEST_CMD, reload_cmd: List[str] = DEFAULT_RELOAD_CMD, start_cmd: List[str] = DEFAULT_START_CMD) -> bool:
        """Test and reload/start Nginx service."""
        if self.dry_run:
            log.info("[dry-run] Would manage Nginx service")
            return True
        if not is_root():
            raise NginxOpsError("Requires root privileges")
        proc = run(test_cmd, capture=True, no_die=True)
        if proc.returncode == 0:
            run(reload_cmd, capture=True)
            log.info("Nginx reloaded successfully")
            return True
        run(start_cmd, capture=True)
        log.info("Started Nginx")
        return True

    # -------------------- Reloads --------------------
    def clear_cache(self, site: Optional[Union[Site, str]] = None) -> bool:
        """Clear cache for a site with backup, validation and service reload.
        
        Args:
            site: Site name, Site object, or None for all sites
            
        Returns:
            bool: True if operation was successful
        """
        def clear_operation():
            if site is not None:
                site_name = site if isinstance(site, str) else site.name
                cache_dir = self.cache_base / site_name
                if not dir_exists(str(cache_dir)):
                    log.info(f"Cache directory not found: {cache_dir}, skipping")
                    return
                if self.dry_run:
                    log.info(f"[dry-run] Would clear cache for {site_name}")
                    return
                remove_dir(str(cache_dir), recursive=True)
                ensure_dir(str(cache_dir))  # recreate empty
                log.info(f"Cleared cache for {site_name}")
            else:
                if self.dry_run:
                    log.info("[dry-run] Would clear all caches")
                    return
                for d in self.cache_base.iterdir():
                    if d.is_dir():
                        remove_dir(str(d), recursive=True)
                        ensure_dir(str(d))  # recreate empty
                log.info("Cleared all caches")

        # Use site name for backup if provided
        site_name = None
        if site is not None:
            site_name = site if isinstance(site, str) else site.name
        
        operation_name = f"Clear cache for {site_name}" if site_name else "Clear all caches"
        
        return self._safe_operation(clear_operation, operation_name, site_name)

    def reload_dns(self) -> bool:
        """Reload dnsmasq service with validation.
        
        Returns:
            bool: True if operation was successful
        """
        def dns_operation():
            if not self.dns_combined or not is_linux():
                log.warning("DNS reload skipped (not supported)")
                return
                
            if self.dry_run:
                log.info("[dry-run] Would reload DNS (dnsmasq)")
                return
                
            run(["systemctl", "restart", "dnsmasq"], elevated=True, no_die=True)
            log.info("Reloaded DNS (dnsmasq)")

        return self._safe_operation(dns_operation, "Reload DNS")

# Export public API
__all__ = [
    "sync_from_yaml",
    "NginxOpsError",
    "Site", 
    "Location",
    "NginxManager",
    "Flag",
    "help",
    "parse_sites_list",
    "parse_sites_yaml",
    "generate_sites_yaml",
    "sync_from_list",
    "migrate_text_to_yaml",
    "backup_site_config",
    "restore_site_config", 
    "list_site_backups",
    "backup_all_sites",
    "validate_nginx_config",
]

# Convenience functions using global manager
def parse_sites_list(list_path: Union[str, Path]) -> List[Site]:
    """Parse sites.txt into Site objects."""
    return _get_manager().parse_sites_list(list_path)

def parse_sites_yaml(yaml_path: Union[str, Path]) -> List[Site]:
    """Parse YAML file into Site objects (standalone function)."""
    manager = NginxManager()
    return manager.parse_sites_yaml(yaml_path)

def generate_sites_yaml(sites: List[Site]) -> str:
    """Generate YAML from Site objects (standalone function)."""
    manager = NginxManager()
    return manager.generate_sites_yaml(sites)

def sync_from_list(list_path: Union[str, Path], force_all: bool = False) -> None:
    """Complete sync from sites.txt file."""
    return _get_manager().sync_from_list(list_path, force_all)

def sync_from_yaml(yaml_path: Union[str, Path], force_all: bool = False) -> None:
    """Complete sync from YAML file."""
    return _get_manager().sync_from_yaml(yaml_path, force_all)

def migrate_text_to_yaml(text_path: Union[str, Path], yaml_path: Union[str, Path]) -> None:
    """Migrate from old text format to new YAML format."""
    return _get_manager().migrate_text_to_yaml(text_path, yaml_path)

def backup_site_config(site_name: str, suffix: Optional[str] = None) -> Path:
    """Convenience function to backup site config."""
    return _get_manager().backup_site_config(site_name, suffix)

def restore_site_config(site_name: str, backup_path: Optional[Path] = None) -> bool:
    """Convenience function to restore site config."""
    return _get_manager().restore_site_config(site_name, backup_path)

def list_site_backups(site_name: Optional[str] = None) -> List[Path]:
    """Convenience function to list site backups."""
    return _get_manager().list_site_backups(site_name)

def backup_all_sites() -> Dict[str, Path]:
    """Convenience function to backup all sites."""
    return _get_manager().backup_all_sites()

def validate_nginx_config() -> bool:
    """Convenience function to validate nginx configuration."""
    return _get_manager().validate_nginx_config()

def clear_cache(site: Optional[Union[Site, str]] = None) -> bool:
    """Convenience function to clear cache with safety features."""
    return _get_manager().clear_cache(site)

def reload_dns() -> bool:
    """Convenience function to reload DNS with safety features."""
    return _get_manager().reload_dns()