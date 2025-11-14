"""
Environment operations for utils_devops (env_ops module).

Provides utilities to manage .env files and system environment variables,
run commands with specific env settings, and safely update env files with
backup/restore support. This module is typed and exposes __all__ so IDEs
show a friendly API surface.

Notes:
- Uses python-dotenv for parsing/setting .env files.
- Uses files for backups and read/write operations.
- Uses systems.run for command execution with an injected environment.
- Logs actions via utils_devops.core.logger.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Dict, Optional, Union, List, Any
from dotenv import load_dotenv, dotenv_values, set_key as dotenv_set_key
from subprocess import CompletedProcess

from .logs import get_library_logger
from .files import backup_file, restore_file, write_file, read_file, FileOpsError
from .systems import run

log = get_library_logger()
# Public API for IDEs / help()
__all__ = [
    "EnvOpsError",
    "help",
    "load_env_file",
    "dump_env_file",
    "update_env_var",
    "remove_env_var",
    "backup_env_file",
    "restore_env_file",
    "get_system_env",
    "set_system_env",
    "export_system_to_env",
    "import_env_to_system",
    "run_with_env",
    "sync_env_to_system",
    "sync_system_to_env",
    "get_all_system_env",
    "validate_env_file",            
    "validate_env_files_compatibility",
]


class EnvOpsError(Exception):
    """Custom exception for environment operations failures."""
    pass


def help() -> None:
    """Print a short index of the env_ops API for interactive use.

    IDEs will pick up `__all__` and function docstrings for completion/help.
    """
    print(
        """
DevOps Utils — Environment Operations Module
Key functions:
EnvOpsError: Custom exception for environment operations failures.
help() -> None: Print a short index of the env_ops API for interactive use.
load_env_file(file_path: Union[str, Path]) -> Dict[str, str]: Load a .env file and return a dict of key->value.
dump_env_file(data: Dict[str, str], file_path: Union[str, Path], backup: bool = True) -> None: Write `data` to `file_path` as KEY=VALUE lines. Optionally back up original file.
update_env_var(key: str, value: str, file_path: Union[str, Path], backup: bool = True) -> None: Set or update a single key in a .env file using python-dotenv's set_key helper.
remove_env_var(key: str, file_path: Union[str, Path], backup: bool = True) -> None: Remove `key` from the .env file (if present).
backup_env_file(file_path: Union[str, Path]) -> Path: Create a backup of the .env file and return backup path.
restore_env_file(file_path: Union[str, Path], from_backup: Optional[Union[str, Path]] = None) -> None: Restore a .env file from backup (or the most recent one).
get_system_env(key: str, default: Optional[str] = None) -> Optional[str]: Get environment variable from os.environ (returns default if missing).
set_system_env(key: str, value: str) -> None: Set environment variable in the current process (os.environ).
export_system_to_env(file_path: Union[str, Path], keys: Optional[List[str]] = None) -> None: Export current process environment (or selected keys) to a .env file.
import_env_to_system(file_path: Union[str, Path], overwrite: bool = True) -> None: Load variables from .env into the process environment.
run_with_env(cmd: Union[str, List[str]], env_file: Optional[Union[str, Path]] = None, additional_env: Optional[Dict[str, str]] = None, **run_kwargs: Any) -> CompletedProcess: Run `cmd` with environment variables loaded from `env_file` and merged with additional_env.
sync_env_to_system(file_path: Union[str, Path], overwrite: bool = True) -> None: Alias for import_env_to_system.
sync_system_to_env(file_path: Union[str, Path], keys: Optional[List[str]] = None) -> None: Alias for export_system_to_env.
get_all_system_env() -> Dict[str, str]: Return a copy of the current process environment as a dict.
validate_env_file(file_path: Union[str, Path], strict: bool = False) -> Dict[str, List[str]]: Validate an environment file for common issues and return validation results. Returns dict with 'errors', 'warnings', 'info', 'valid', and 'key_count'. If strict=True, raises EnvOpsError on validation failures.
validate_env_files_compatibility(env_file1: Union[str, Path], env_file2: Union[str, Path]) -> Dict[str, Any]: Validate compatibility between two environment files. Returns dict with 'compatible', 'common_keys', 'file1_only', 'file2_only', 'conflicting_values', and validation results for both files.
"""
    )


def validate_env_file(file_path: Union[str, Path], strict: bool = False) -> Dict[str, List[str]]:
    """
    Validate an environment file for common issues and return validation results.
    
    Args:
        file_path: Path to the .env file to validate
        strict: If True, raises EnvOpsError on validation failures. If False, returns warnings.
    
    Returns:
        Dict with validation results containing:
        - 'errors': List of critical errors that prevent proper parsing
        - 'warnings': List of potential issues that don't prevent parsing
        - 'info': List of informational messages
        - 'valid': Boolean indicating if file is valid (no critical errors)
        - 'key_count': Number of valid environment variables found
    
    Raises:
        EnvOpsError: If strict=True and validation fails
        FileNotFoundError: If env file doesn't exist
    
    Examples:
        >>> result = validate_env_file('.env')
        >>> if result['valid']:
        ...     print(f"Valid env file with {result['key_count']} keys")
        >>> # With strict mode:
        >>> validate_env_file('.env', strict=True)
    """
    file_path = Path(file_path)
    results = {
        'errors': [],
        'warnings': [],
        'info': [],
        'valid': False,
        'key_count': 0
    }
    
    # Check file existence
    if not file_path.exists():
        results['errors'].append(f"Environment file not found: {file_path}")
        if strict:
            raise EnvOpsError(f"Environment file not found: {file_path}")
        return results
    
    if not file_path.is_file():
        results['errors'].append(f"Path is not a file: {file_path}")
        if strict:
            raise EnvOpsError(f"Path is not a file: {file_path}")
        return results
    
    # Check file size
    file_size = file_path.stat().st_size
    if file_size == 0:
        results['warnings'].append("Environment file is empty")
    elif file_size > 1024 * 1024:  # 1MB
        results['warnings'].append(f"Environment file is unusually large: {file_size} bytes")
    
    # Read and parse file content
    try:
        content = file_path.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        try:
            content = file_path.read_text(encoding='latin-1')
            results['warnings'].append("File is not UTF-8 encoded, using latin-1 fallback")
        except Exception as e:
            results['errors'].append(f"Failed to read file: {e}")
            if strict:
                raise EnvOpsError(f"Failed to read environment file: {e}") from e
            return results
    except Exception as e:
        results['errors'].append(f"Failed to read file: {e}")
        if strict:
            raise EnvOpsError(f"Failed to read environment file: {e}") from e
        return results
    
    # Parse line by line for detailed validation
    lines = content.splitlines()
    valid_keys = set()
    line_number = 0
    
    for line in lines:
        line_number += 1
        line = line.strip()
        
        # Skip empty lines and comments
        if not line or line.startswith('#'):
            continue
        
        # Check for export keyword (shell syntax)
        if line.startswith('export '):
            results['warnings'].append(f"Line {line_number}: Uses 'export' keyword (shell syntax)")
            line = line[7:].strip()  # Remove 'export '
        
        # Validate key=value format
        if '=' not in line:
            results['errors'].append(f"Line {line_number}: No '=' found in environment variable assignment")
            continue
        
        key, value = line.split('=', 1)
        key = key.strip()
        
        # Validate key name
        if not key:
            results['errors'].append(f"Line {line_number}: Empty key name")
            continue
        
        if not key.replace('_', '').isalnum():
            results['warnings'].append(f"Line {line_number}: Key '{key}' contains non-alphanumeric characters (only letters, numbers, and underscores are standard)")
        
        if key[0].isdigit():
            results['warnings'].append(f"Line {line_number}: Key '{key}' starts with a digit (may cause issues in some systems)")
        
        # Check for common issues in values
        if value.strip() != value:
            results['warnings'].append(f"Line {line_number}: Value for '{key}' has leading/trailing whitespace")
        
        # Check for unquoted spaces (potential issues)
        if ' ' in value and not (value.startswith(('"', "'")) and value.endswith(('"', "'"))):
            results['warnings'].append(f"Line {line_number}: Value for '{key}' contains spaces but is not quoted")
        
        # Check for potential secrets in keys
        secret_indicators = ['password', 'secret', 'key', 'token', 'auth', 'credential']
        if any(indicator in key.lower() for indicator in secret_indicators):
            results['info'].append(f"Line {line_number}: Key '{key}' appears to contain sensitive data")
        
        valid_keys.add(key)
    
    # Try to load with dotenv to validate parsing
    try:
        env_dict = dotenv_values(file_path)
        parsed_count = len([v for v in env_dict.values() if v is not None])
        results['key_count'] = parsed_count
        results['info'].append(f"Successfully parsed {parsed_count} environment variables")
        
        # Check for None values (parsing issues)
        none_values = [k for k, v in env_dict.items() if v is None]
        if none_values:
            results['warnings'].append(f"Variables with None values (possible parsing issues): {', '.join(none_values)}")
            
    except Exception as e:
        results['errors'].append(f"Failed to parse environment file with dotenv: {e}")
    
    # Determine overall validity
    results['valid'] = len(results['errors']) == 0
    
    # Log results
    if results['valid']:
        if results['warnings']:
            log.warning(f"Env file validation passed with warnings for {file_path}: {len(results['warnings'])} warnings")
        else:
            log.info(f"Env file validation passed for {file_path}: {results['key_count']} variables")
    else:
        log.error(f"Env file validation failed for {file_path}: {len(results['errors'])} errors, {len(results['warnings'])} warnings")
    
    # Raise error if strict mode and invalid
    if strict and not results['valid']:
        error_msg = f"Environment file validation failed: {'; '.join(results['errors'])}"
        raise EnvOpsError(error_msg)
    
    return results


def validate_env_files_compatibility(env_file1: Union[str, Path], env_file2: Union[str, Path]) -> Dict[str, Any]:
    """
    Validate compatibility between two environment files.
    
    Args:
        env_file1: First environment file path
        env_file2: Second environment file path
    
    Returns:
        Dict with compatibility analysis:
        - 'compatible': Boolean indicating if files are compatible
        - 'common_keys': List of keys present in both files
        - 'file1_only': List of keys only in first file
        - 'file2_only': List of keys only in second file
        - 'conflicting_values': Dict of keys with different values
        - 'file1_validation': Validation results for first file
        - 'file2_validation': Validation results for second file
    """
    results = {
        'compatible': False,
        'common_keys': [],
        'file1_only': [],
        'file2_only': [],
        'conflicting_values': {},
        'file1_validation': None,
        'file2_validation': None
    }
    
    # Validate both files
    results['file1_validation'] = validate_env_file(env_file1)
    results['file2_validation'] = validate_env_file(env_file2)
    
    if not results['file1_validation']['valid'] or not results['file2_validation']['valid']:
        return results
    
    # Load both environment files
    try:
        env1 = load_env_file(env_file1)
        env2 = load_env_file(env_file2)
        
        # Analyze differences
        keys1 = set(env1.keys())
        keys2 = set(env2.keys())
        
        results['common_keys'] = sorted(keys1 & keys2)
        results['file1_only'] = sorted(keys1 - keys2)
        results['file2_only'] = sorted(keys2 - keys1)
        
        # Find conflicting values
        for key in results['common_keys']:
            if env1[key] != env2[key]:
                results['conflicting_values'][key] = {
                    'file1_value': env1[key],
                    'file2_value': env2[key]
                }
        
        # Determine compatibility
        results['compatible'] = len(results['conflicting_values']) == 0
        
        log.info(f"Env files compatibility: {results['compatible']}, "
                f"common: {len(results['common_keys'])}, "
                f"conflicts: {len(results['conflicting_values'])}")
                
    except Exception as e:
        log.error(f"Failed to compare environment files: {e}")
        results['compatible'] = False
    
    return results


# ========================
# .env File Operations
# ========================


def load_env_file(file_path: Union[str, Path]) -> Dict[str, str]:
    """Load a .env file and return a dict of key->value.

    file_path: path to the .env file. If file doesn't exist returns an empty dict.
    """
    try:
        data = dotenv_values(file_path)
        log.info(f"Loaded .env from {file_path}: {len(data)} keys")
        # dotenv_values may return values as None for missing values; normalize to str
        return {k: (v if v is not None else "") for k, v in data.items()}
    except Exception as e:
        log.error(f"Failed to load .env {file_path}: {e}")
        raise EnvOpsError(f"Failed to load .env: {e}") from e


def dump_env_file(data: Dict[str, str], file_path: Union[str, Path], backup: bool = True) -> None:
    """Write `data` to `file_path` as KEY=VALUE lines. Optionally back up original file.

    Overwrites the target file.
    """
    file_path = Path(file_path)
    if backup and file_path.exists():
        backup_file(file_path)
    try:
        content = "\n".join(f"{k}={v}" for k, v in data.items())
        write_file(file_path, content)
        log.info(f"Dumped {len(data)} env vars to {file_path}")
    except FileOpsError as e:
        log.error(f"Failed to dump .env: {e}")
        raise EnvOpsError(f"Failed to dump .env: {e}") from e


def update_env_var(key: str, value: str, file_path: Union[str, Path], backup: bool = True) -> None:
    """Set or update a single key in a .env file using python-dotenv's set_key helper.

    If `file_path` doesn't exist it will be created.
    """
    file_path = Path(file_path)
    if backup and file_path.exists():
        backup_file(file_path)
    try:
        # dotenv_set_key returns tuple (success, new_value) on some implementations,
        # we'll rely on it to write to file. Ensure parent exists.
        file_path.parent.mkdir(parents=True, exist_ok=True)
        dotenv_set_key(str(file_path), key, value)
        log.info(f"Updated env var '{key}' in {file_path}")
    except Exception as e:
        log.error(f"Failed to update env var '{key}': {e}")
        raise EnvOpsError(f"Failed to update env var: {e}") from e


def remove_env_var(key: str, file_path: Union[str, Path], backup: bool = True) -> None:
    """Remove `key` from the .env file (if present)."""
    file_path = Path(file_path)
    if backup and file_path.exists():
        backup_file(file_path)
    try:
        data = load_env_file(file_path)
        data.pop(key, None)
        dump_env_file(data, file_path, backup=False)
        log.info(f"Removed env var '{key}' from {file_path}")
    except Exception as e:
        log.error(f"Failed to remove env var '{key}': {e}")
        raise EnvOpsError(f"Failed to remove env var: {e}") from e


def backup_env_file(file_path: Union[str, Path]) -> Path:
    """Create a backup of the .env file and return backup path."""
    return backup_file(file_path)


def restore_env_file(file_path: Union[str, Path], from_backup: Optional[Union[str, Path]] = None) -> None:
    """Restore a .env file from backup (or the most recent one)."""
    restore_file(file_path, from_backup)


# ========================
# System Environment Operations
# ========================


def get_system_env(key: str, default: Optional[str] = None) -> Optional[str]:
    """Get environment variable from os.environ (returns default if missing)."""
    value = os.environ.get(key, default)
    log.debug(f"Got system env '{key}': {'[hidden]' if value else None}")
    return value


def set_system_env(key: str, value: str) -> None:
    """Set environment variable in the current process (os.environ)."""
    os.environ[key] = value
    log.info(f"Set system env '{key}'")


def export_system_to_env(file_path: Union[str, Path], keys: Optional[List[str]] = None) -> None:
    """Export current process environment (or selected keys) to a .env file."""
    data = {k: os.environ[k] for k in (keys or os.environ.keys())}
    dump_env_file(data, file_path)
    log.info(f"Exported {len(data)} system env vars to {file_path}")


def import_env_to_system(file_path: Union[str, Path], overwrite: bool = True) -> None:
    """Load variables from .env into the process environment.

    If overwrite is False existing os.environ keys are left untouched.
    """
    try:
        load_dotenv(dotenv_path=str(file_path), override=overwrite)
        log.info(f"Imported .env from {file_path} to system (overwrite={overwrite})")
    except Exception as e:
        log.error(f"Failed to import .env to system: {e}")
        raise EnvOpsError(f"Failed to import .env: {e}") from e


# ========================
# Command Execution with Env
# ========================


def run_with_env(
    cmd: Union[str, List[str]],
    env_file: Optional[Union[str, Path]] = None,
    additional_env: Optional[Dict[str, str]] = None,
    **run_kwargs: Any,
) -> CompletedProcess:
    """Run `cmd` with environment variables loaded from `env_file` and merged with additional_env.

    `run_kwargs` are forwarded to systems.run (cwd, elevated, dry_run, etc.). Returns CompletedProcess.
    """
    env = os.environ.copy()
    if env_file:
        env_file_data = load_env_file(env_file)
        env.update(env_file_data)
    if additional_env:
        env.update(additional_env)
    log.info(f"Running command with {len(env)} env vars")
    return run(cmd, env=env, **run_kwargs)


# Convenience aliases
sync_env_to_system = import_env_to_system
sync_system_to_env = export_system_to_env


def get_all_system_env() -> Dict[str, str]:
    """Return a copy of the current process environment as a dict."""
    data = dict(os.environ)
    log.debug(f"Got all system env: {len(data)} keys")
    return data
