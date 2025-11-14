"""
docker_ops.py
High-level Docker Compose operations helper module for utils_devops.
Recommended dependencies (optional): docker (docker-py), ruamel-yaml (for YAML preservation), tenacity (for retries)
This implementation provides a practical, well-tested core surface with helpers
that fall back to CLI where appropriate. Heavy/complex behaviors are included
as implemented helpers and safe stubs with clear TODOs.
Improved with integration to core modules (logs, files, systems, strings, envs, datetime, script_helpers).
Uses ruamel.yaml for YAML parsing/writing to preserve comments/formatting.
Uses tenacity for retrying operations like pull.
Uses concurrent.futures for parallel ops.
Handles optional docker SDK; falls back to CLI if not available.
"""
from __future__ import annotations
import subprocess
import shlex
import json
import os
import datetime
import tempfile
import logging
import re
import tarfile
import glob
import uuid  
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Iterator, Tuple, Union, Callable
from pathlib import Path
import concurrent.futures
from functools import wraps

# Core imports (assume utils_devops.core structure)
from utils_devops.core import logs
from utils_devops.core import files
from utils_devops.core import systems
from utils_devops.core import strings
from utils_devops.core import envs
from utils_devops.core import datetimes as dt_ops
from utils_devops.core import script_helpers as script


# Optional imports
try:
    import docker
    from docker.models.containers import Container
    from docker.models.images import Image
    from docker.errors import DockerException
except ImportError:  # pragma: no cover - optional
    docker = None

try:
    from ruamel.yaml import YAML
except ImportError:  # pragma: no cover - optional, fallback to pyyaml
    import yaml as pyyaml
    YAML = None

try:
    from tenacity import retry, stop_after_attempt, wait_exponential
except ImportError:  # pragma: no cover - optional
    retry = lambda *a, **k: lambda f: f  # no-op decorator

# Module logger
_MODULE_LOGGER = logs.get_library_logger()

# Constants
DEFAULT_DOCKER_TIMEOUT = 300
DEFAULT_CONCURRENCY_LIMIT = 4
DEFAULT_COMPOSE_VERSION = "3.8"
DEFAULT_PULL_RETRIES = 3
DEFAULT_HEALTH_INTERVAL = 2.0

# Exceptions
class DockerOpsError(Exception):
    pass

class ComposeConflictError(DockerOpsError):
    pass

class HealthCheckFailed(DockerOpsError):
    pass

class RollbackFailed(DockerOpsError):
    pass

class ImageRetentionError(DockerOpsError):
    pass

# --- Auxiliary small dataclasses ---
@dataclass
class BuildSpec:
    context: Optional[str] = None
    dockerfile: Optional[str] = None
    args: Dict[str, str] = field(default_factory=dict)
    target: Optional[str] = None

@dataclass
class PortBinding:
    host_port: int
    container_port: int
    protocol: str = "tcp"

@dataclass
class VolumeMount:
    source: str
    target: str
    type: str = "volume"
    readonly: bool = False

@dataclass
class HealthCheckSpec:
    test: List[str]
    interval: int = 30
    timeout: int = 10
    retries: int = 3
    start_period: int = 0

@dataclass
class NetworkSpec:
    name: str
    driver: Optional[str] = "bridge"
    external: bool = False
    labels: Dict[str, str] = field(default_factory=dict)

@dataclass
class VolumeSpec:
    name: str
    driver: Optional[str] = "local"
    external: bool = False
    labels: Dict[str, str] = field(default_factory=dict)

@dataclass
class ServiceRevision:
    timestamp: str = field(default_factory=lambda: dt_ops.current_datetime().isoformat())
    spec: Dict[str, Any] = field(default_factory=dict)
    description: Optional[str] = None

@dataclass
class DockerComposeRevision:
    timestamp: str = field(default_factory=lambda: dt_ops.current_datetime().isoformat())
    spec: Dict[str, Any] = field(default_factory=dict)
    description: Optional[str] = None

@dataclass
class ExecResult:
    rc: int
    stdout: str
    stderr: str

@dataclass
class LogLine:
    timestamp: Optional[str] = None
    service: Optional[str] = None
    message: str = ""

# --- Core dataclasses ---
@dataclass
class DockerImage:
    name: str
    tag: Optional[str] = None
    digest: Optional[str] = None
    size: Optional[int] = None
    created: Optional[datetime.datetime] = None
    labels: Dict[str, str] = field(default_factory=dict)

    @property
    def fullname(self) -> str:
        if self.tag:
            return f"{self.name}:{self.tag}"
        return self.name

    def pull(self, auth: Optional[Dict] = None, retry_attempts: int = DEFAULT_PULL_RETRIES, logger: Optional[logging.Logger] = None, dry_run: bool = False) -> "DockerImage":
        logger = logger or _MODULE_LOGGER
        if dry_run:
            logger.info(f"Dry-run: Would pull image {self.fullname}")
            return self
        return pull_image(self.name, tag=self.tag, auth=auth, retries=retry_attempts, logger=logger)

    def push(self, auth: Optional[Dict] = None, retry_attempts: int = DEFAULT_PULL_RETRIES, logger: Optional[logging.Logger] = None, dry_run: bool = False) -> None:
        logger = logger or _MODULE_LOGGER
        if dry_run:
            logger.info(f"Dry-run: Would push image {self.fullname}")
            return
        push_image(self.name, tag=self.tag, auth=auth, retries=retry_attempts, logger=logger)

    def save(self, path: str, compress: bool = True, logger: Optional[logging.Logger] = None, dry_run: bool = False) -> str:
        logger = logger or _MODULE_LOGGER
        if dry_run:
            logger.info(f"Dry-run: Would save image {self.fullname} to {path}")
            return path
        return save_image(self.name, tag=self.tag, path=path, compress=compress, logger=logger)

    def load(self, path: str, logger: Optional[logging.Logger] = None, dry_run: bool = False) -> "DockerImage":
        logger = logger or _MODULE_LOGGER
        if dry_run:
            logger.info(f"Dry-run: Would load image from {path}")
            return self
        return load_image(path, logger=logger)

    def tag(self, new_tag: str, force: bool = False, logger: Optional[logging.Logger] = None, dry_run: bool = False) -> "DockerImage":
        logger = logger or _MODULE_LOGGER
        if dry_run:
            logger.info(f"Dry-run: Would tag image {self.fullname} as {new_tag}")
            return DockerImage(name=self.name, tag=new_tag)
        return tag_image(self.name, tag=self.tag, new_tag=new_tag, force=force, logger=logger)

    def remove(self, force: bool = False, logger: Optional[logging.Logger] = None, dry_run: bool = False) -> None:
        logger = logger or _MODULE_LOGGER
        if dry_run:
            logger.info(f"Dry-run: Would remove image {self.fullname}")
            return
        remove_image(self.name, tag=self.tag, force=force, logger=logger)

@dataclass
class DockerContainer:
    id: str
    name: str
    image: str
    status: str
    started_at: Optional[str] = None
    ports: Dict[str, str] = field(default_factory=dict)
    inspect: Optional[Dict[str, Any]] = None

    def start(self, logger: Optional[logging.Logger] = None) -> None:
        logger = logger or _MODULE_LOGGER
        start_container(self.id, logger=logger)

    def stop(self, timeout: int = 10, logger: Optional[logging.Logger] = None) -> None:
        logger = logger or _MODULE_LOGGER
        stop_container(self.id, timeout=timeout, logger=logger)

    def restart(self, timeout: int = 10, logger: Optional[logging.Logger] = None) -> None:
        logger = logger or _MODULE_LOGGER
        restart_container(self.id, timeout=timeout, logger=logger)

    def kill(self, signal: str = 'SIGKILL', logger: Optional[logging.Logger] = None) -> None:
        logger = logger or _MODULE_LOGGER
        kill_container(self.id, signal=signal, logger=logger)

    def logs(self, follow: bool = False, tail: Optional[Union[str, int]] = 'all', since: Optional[int] = None, logger: Optional[logging.Logger] = None) -> Iterator[LogLine]:
        logger = logger or _MODULE_LOGGER
        return container_logs(self.id, follow=follow, tail=tail, since=since, logger=logger)

    def exec(self, cmd: List[str], user: Optional[str] = None, stream: bool = False, tty: bool = False, logger: Optional[logging.Logger] = None) -> ExecResult:
        logger = logger or _MODULE_LOGGER
        return exec_command(self.id, cmd, user=user, stream=stream, tty=tty, logger=logger)

    def commit(self, tag: str, message: Optional[str] = None, logger: Optional[logging.Logger] = None) -> DockerImage:
        logger = logger or _MODULE_LOGGER
        return commit_container(self.id, tag=tag, message=message, logger=logger)

    def attach(self, logs: bool = False, stream: bool = True, logger: Optional[logging.Logger] = None) -> None:
        logger = logger or _MODULE_LOGGER
        attach_container(self.id, logs=logs, stream=stream, logger=logger)

    def remove(self, force: bool = False, remove_volumes: bool = False, logger: Optional[logging.Logger] = None) -> None:
        logger = logger or _MODULE_LOGGER
        remove_container(self.id, force=force, remove_volumes=remove_volumes, logger=logger)

@dataclass
class ComposeService:
    name: str
    image: Optional[str] = None
    container_name: Optional[str] = None
    build: Optional[BuildSpec] = None
    ports: List[PortBinding] = field(default_factory=list)
    networks: List[str] = field(default_factory=list)
    volumes: List[VolumeMount] = field(default_factory=list)
    env_file: Optional[str] = None
    environment: Dict[str, str] = field(default_factory=dict)
    command: Optional[Union[str, List[str]]] = None
    entrypoint: Optional[Union[str, List[str]]] = None
    healthcheck: Optional[HealthCheckSpec] = None
    depends_on: List[str] = field(default_factory=list)
    restart_policy: Optional[str] = None
    expose: List[int] = field(default_factory=list)
    labels: Dict[str, str] = field(default_factory=dict)
    secrets: List[str] = field(default_factory=list)
    configs: List[str] = field(default_factory=list)
    logging: Optional[Dict[str, Any]] = None
    deploy: Optional[Dict[str, Any]] = None
    privileged: Optional[bool] = None
    user: Optional[str] = None
    ulimits: Optional[Dict[str, Any]] = None
    tmpfs: Optional[List[str]] = field(default_factory=list)
    readonly_rootfs: Optional[bool] = None
    # runtime attrs
    container: Optional[DockerContainer] = None
    image_obj: Optional[DockerImage] = None
    history: List[ServiceRevision] = field(default_factory=list)

    def to_compose_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.image:
            d["image"] = self.image
        if self.build:
            b: Dict[str, Any] = {}
            if self.build.context:
                b["context"] = self.build.context
            if self.build.dockerfile:
                b["dockerfile"] = self.build.dockerfile
            if self.build.args:
                b["args"] = self.build.args
            if self.build.target:
                b["target"] = self.build.target
            d["build"] = b
        if self.container_name:
            d["container_name"] = self.container_name
        if self.ports:
            d["ports"] = [f"{p.host_port}:{p.container_port}/{p.protocol}" for p in self.ports]
        if self.networks:
            d["networks"] = self.networks
        if self.volumes:
            d["volumes"] = [f"{v.source}:{v.target}:{'ro' if v.readonly else 'rw'}" for v in self.volumes]
        if self.env_file:
            d["env_file"] = self.env_file
        if self.environment:
            d["environment"] = self.environment
        if self.command:
            d["command"] = self.command
        if self.entrypoint:
            d["entrypoint"] = self.entrypoint
        if self.healthcheck:
            d["healthcheck"] = {
                "test": self.healthcheck.test,
                "interval": f"{self.healthcheck.interval}s",
                "timeout": f"{self.healthcheck.timeout}s",
                "retries": self.healthcheck.retries,
                "start_period": f"{self.healthcheck.start_period}s",
            }
        if self.depends_on:
            d["depends_on"] = self.depends_on
        if self.restart_policy:
            d["restart"] = self.restart_policy
        if self.expose:
            d["expose"] = [str(e) for e in self.expose]
        if self.labels:
            d["labels"] = self.labels
        if self.secrets:
            d["secrets"] = self.secrets
        if self.configs:
            d["configs"] = self.configs
        if self.logging:
            d["logging"] = self.logging
        if self.deploy:
            d["deploy"] = self.deploy
        if self.privileged is not None:
            d["privileged"] = self.privileged
        if self.user:
            d["user"] = self.user
        if self.ulimits:
            d["ulimits"] = self.ulimits
        if self.tmpfs:
            d["tmpfs"] = self.tmpfs
        if self.readonly_rootfs is not None:
            d["read_only"] = self.readonly_rootfs
        return d

    def validate(self) -> List[str]:
        errs: List[str] = []
        if not (self.image or self.build):
            errs.append(f"Service {self.name} must have either image or build spec")
        for p in self.ports:
            if p.container_port <= 0 or p.host_port <= 0:
                errs.append(f"Invalid port in {self.name}: {p}")
        for v in self.volumes:
            if not v.source or not v.target:
                errs.append(f"Invalid volume in {self.name}: {v}")
        if self.healthcheck and not self.healthcheck.test:
            errs.append(f"Healthcheck in {self.name} missing test command")
        return errs

    # Convenience wrappers
    def up(self, detach: bool = True, build: bool = False, pull: bool = False, dry_run: bool = False, logger: Optional[logging.Logger] = None) -> DockerContainer:
        return service_up(self, detach=detach, build_if_missing=build, pull=pull, dry_run=dry_run, logger=logger)

    def down(self, remove_volumes: bool = False, force: bool = False, dry_run: bool = False, logger: Optional[logging.Logger] = None) -> None:
        service_down(self, remove_volumes=remove_volumes, force=force, dry_run=dry_run, logger=logger)

    def restart(self, timeout: int = 10, dry_run: bool = False, logger: Optional[logging.Logger] = None) -> None:
        service_restart(self, timeout=timeout, dry_run=dry_run, logger=logger)

    def logs(self, follow: bool = False, tail: Optional[Union[str, int]] = 'all', logger: Optional[logging.Logger] = None) -> Iterator[LogLine]:
        return service_logs(self, follow=follow, tail=tail, logger=logger)

    def exec(self, command: Union[str, List[str]], user: Optional[str] = None, stream: bool = False, tty: bool = False, logger: Optional[logging.Logger] = None) -> ExecResult:
        return service_exec(self, command=command, user=user, stream=stream, tty=tty, logger=logger)

    def pull(self, retry: int = DEFAULT_PULL_RETRIES, dry_run: bool = False, logger: Optional[logging.Logger] = None) -> DockerImage:
        return service_pull(self, retry=retry, dry_run=dry_run, logger=logger)

    def push(self, auth: Optional[Dict] = None, retry: int = DEFAULT_PULL_RETRIES, dry_run: bool = False, logger: Optional[logging.Logger] = None) -> None:
        service_push(self, auth=auth, retry=retry, dry_run=dry_run, logger=logger)

    def build(self, nocache: bool = False, pull: bool = False, build_args: Optional[Dict] = None, dry_run: bool = False, logger: Optional[logging.Logger] = None) -> DockerImage:
        return service_build(self, nocache=nocache, pull=pull, build_args=build_args, dry_run=dry_run, logger=logger)

    def commit(self, tag: str, message: Optional[str] = None, dry_run: bool = False, logger: Optional[logging.Logger] = None) -> DockerImage:
        return service_commit(self, tag=tag, message=message, dry_run=dry_run, logger=logger)

@dataclass
class DockerCompose:
    name: str
    file_path: str
    version: Optional[str] = DEFAULT_COMPOSE_VERSION
    services: Dict[str, ComposeService] = field(default_factory=dict)
    networks: Dict[str, NetworkSpec] = field(default_factory=dict)
    volumes: Dict[str, VolumeSpec] = field(default_factory=dict)
    env_files: List[str] = field(default_factory=list)
    labels: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    history: List[DockerComposeRevision] = field(default_factory=list)

    def to_yaml_dict(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {"version": self.version, "services": {n: s.to_compose_dict() for n, s in self.services.items()}}
        if self.networks:
            out["networks"] = {n: {"driver": spec.driver, "external": spec.external, "labels": spec.labels} for n, spec in self.networks.items()}
        if self.volumes:
            out["volumes"] = {n: {"driver": spec.driver, "external": spec.external, "labels": spec.labels} for n, spec in self.volumes.items()}
        return out

    def validate(self) -> List[str]:
        errs: List[str] = []
        for _, svc in self.services.items():
            errs.extend(svc.validate())
        for dep in [d for s in self.services.values() for d in s.depends_on]:
            if dep not in self.services:
                errs.append(f"Depends_on {dep} not found in services")
        return errs

    # Convenience wrappers
    def up(self, services: Optional[List[str]] = None, build: bool = False, pull: bool = False, detach: bool = True, dry_run: bool = False, logger: Optional[logging.Logger] = None) -> Dict[str, Any]:
        return compose_up(self, services=services, build=build, pull=pull, detach=detach, dry_run=dry_run, logger=logger)

    def down(self, remove_volumes: bool = False, remove_images: Optional[str] = None, dry_run: bool = False, logger: Optional[logging.Logger] = None) -> Dict[str, Any]:
        return compose_down(self, remove_volumes=remove_volumes, remove_images=remove_images, dry_run=dry_run, logger=logger)

    def ps(self, logger: Optional[logging.Logger] = None) -> Dict[str, DockerContainer]:
        return compose_ps(self, logger=logger)

    def logs(self, services: Optional[List[str]] = None, follow: bool = False, tail: Optional[Union[str, int]] = 'all', logger: Optional[logging.Logger] = None) -> Iterator[LogLine]:
        return compose_logs(self, services=services, follow=follow, tail=tail, logger=logger)

    def backup(self, backup_dir: str, include_images: bool = False, compress: bool = True, dry_run: bool = False, logger: Optional[logging.Logger] = None) -> str:
        return backup_compose(self, backup_dir=backup_dir, include_images=include_images, compress=compress, dry_run=dry_run, logger=logger)

    def restore(self, backup_path: str, load_images: bool = True, dry_run: bool = False, logger: Optional[logging.Logger] = None) -> "DockerCompose":
        return restore_compose(backup_path, restore_dir=Path(self.file_path).parent, load_images=load_images, dry_run=dry_run, logger=logger)

# --- Low-level helpers ---
def _get_docker_client(logger: Optional[logging.Logger] = None) -> Optional["docker.DockerClient"]:
    logger = logger or _MODULE_LOGGER
    if docker is None:
        logger.warning("docker-py not available; falling back to CLI")
        return None
    try:
        client = docker.from_env(timeout=DEFAULT_DOCKER_TIMEOUT)
        return client
    except DockerException as e:
        logger.error("Failed to create Docker client: %s", e)
        return None

def _run_cli(cmd: Union[str, List[str]], capture: bool = True, timeout: Optional[int] = None, env: Optional[Dict[str, str]] = None, logger: Optional[logging.Logger] = None) -> systems.CompletedProcess:
    logger = logger or _MODULE_LOGGER
    logs.task_start("Running CLI: " + (cmd if isinstance(cmd, str) else ' '.join(cmd)))
    try:
        proc = systems.run(cmd, capture=capture, timeout=timeout or DEFAULT_DOCKER_TIMEOUT, env=env)
        if proc.returncode != 0:
            logger.error("CLI failed: %s - stderr: %s", ' '.join(cmd) if isinstance(cmd, list) else cmd, proc.stderr)
            raise DockerOpsError(f"CLI failed with code {proc.returncode}")
        logs.task_pass("CLI succeeded")
        return proc
    except Exception as e:
        logs.task_fail("CLI failed")
        raise DockerOpsError(f"CLI execution error: {e}") from e

def _normalize_image_name(name: str, tag: Optional[str] = 'latest') -> str:
    return f"{name}:{tag}" if tag else name

def _list_images(filters: Optional[Dict] = None, logger: Optional[logging.Logger] = None) -> List[DockerImage]:
    logger = logger or _MODULE_LOGGER
    client = _get_docker_client(logger=logger)
    if client:
        try:
            images = client.images.list(filters=filters)
            return [DockerImage(name=i.tags[0].split(':')[0] if i.tags else 'untagged', tag=i.tags[0].split(':')[1] if i.tags and ':' in i.tags[0] else None, digest=i.id, size=i.attrs['Size'], created=dt_ops.timestamp_to_datetime(i.attrs['Created']), labels=i.labels) for i in images]
        except DockerException as e:
            logger.error("SDK list images failed: %s", e)
    # Fallback to CLI
    proc = _run_cli(["docker", "images", "--format", "{{json .}}"], logger=logger)
    lines = proc.stdout.splitlines()
    images = []
    for line in lines:
        try:
            obj = json.loads(line)
            name = obj['Repository']
            tag = obj['Tag']
            digest = obj.get('Digest', '')
            size_str = obj['Size']
            if 'MB' in size_str:
                size = int(float(size_str.replace('MB', '').strip()) * 1024 * 1024)
            elif 'GB' in size_str:
                size = int(float(size_str.replace('GB', '').strip()) * 1024 * 1024 * 1024)
            else:
                size = 0
            created = dt_ops.parse_datetime(obj['CreatedAt'])
            images.append(DockerImage(name=name, tag=tag, digest=digest, size=size, created=created))
        except Exception as e:
            logger.debug(f"Failed to parse image line: {line}, error: {e}")
            continue
    return images

def _inspect_image(image: str, logger: Optional[logging.Logger] = None) -> Dict[str, Any]:
    logger = logger or _MODULE_LOGGER
    client = _get_docker_client(logger=logger)
    if client:
        try:
            return client.images.get(image).attrs
        except DockerException as e:
            logger.error("SDK inspect image failed: %s", e)
    proc = _run_cli(["docker", "image", "inspect", image], logger=logger)
    try:
        return json.loads(proc.stdout)[0]
    except Exception:
        raise DockerOpsError("Failed to inspect image")

def _inspect_container(container: str, logger: Optional[logging.Logger] = None) -> Dict[str, Any]:
    logger = logger or _MODULE_LOGGER
    client = _get_docker_client(logger=logger)
    if client:
        try:
            return client.containers.get(container).attrs
        except DockerException as e:
            logger.error("SDK inspect container failed: %s", e)
    proc = _run_cli(["docker", "inspect", container], logger=logger)
    try:
        return json.loads(proc.stdout)[0]
    except Exception:
        raise DockerOpsError("Failed to inspect container")

def _parse_compose_yaml(path: str, logger: Optional[logging.Logger] = None) -> Dict[str, Any]:
    logger = logger or _MODULE_LOGGER
    text = files.read_file(path)
    if YAML is not None:
        yaml = YAML(typ='safe')
        return yaml.load(text)
    else:
        if 'pyyaml' in globals():
            return pyyaml.safe_load(text)
        else:
            raise DockerOpsError("No YAML parser available")

def _write_yaml(data: Dict[str, Any], path: str, backup: bool = True, logger: Optional[logging.Logger] = None) -> None:
    logger = logger or _MODULE_LOGGER
    if backup:
        files.backup_file(path)
    if YAML is not None:
        yaml = YAML()
        yaml.indent(mapping=2, sequence=4, offset=2)
        yaml.preserve_quotes = True
        with open(path, 'w') as f:
            yaml.dump(data, f)
    else:
        if 'pyyaml' in globals():
            with open(path, 'w') as f:
                pyyaml.safe_dump(data, f, sort_keys=False)
        else:
            raise DockerOpsError("No YAML writer available")

def _parse_healthcheck(healthcheck_data: Any) -> Optional[HealthCheckSpec]:
    if not healthcheck_data:
        return None
    if isinstance(healthcheck_data, dict):
        test = healthcheck_data.get('test', [])
        if isinstance(test, str):
            test = ['CMD-SHELL', test]
        elif isinstance(test, list) and test and test[0].startswith('CMD'):
            test = test
        else:
            test = ['CMD'] + test if test else []
        
        interval = healthcheck_data.get('interval', 30)
        if isinstance(interval, str) and interval.endswith('s'):
            interval = int(interval[:-1])
        
        timeout = healthcheck_data.get('timeout', 10)
        if isinstance(timeout, str) and timeout.endswith('s'):
            timeout = int(timeout[:-1])
        
        retries = healthcheck_data.get('retries', 3)
        start_period = healthcheck_data.get('start_period', 0)
        if isinstance(start_period, str) and start_period.endswith('s'):
            start_period = int(start_period[:-1])
        
        return HealthCheckSpec(
            test=test,
            interval=interval,
            timeout=timeout,
            retries=retries,
            start_period=start_period
        )
    return None

def _parse_ports(ports_data: Any) -> List[PortBinding]:
    ports = []
    if not ports_data:
        return ports
    
    for port_def in ports_data if isinstance(ports_data, list) else [ports_data]:
        if isinstance(port_def, str):
            # Parse "host:container/protocol" format
            parts = port_def.split('/')
            protocol = parts[1] if len(parts) > 1 else 'tcp'
            host_container = parts[0].split(':')
            if len(host_container) == 2:
                host_port = int(host_container[0])
                container_port = int(host_container[1])
                ports.append(PortBinding(host_port=host_port, container_port=container_port, protocol=protocol))
        elif isinstance(port_def, dict):
            # Parse {target: , published: , protocol: } format
            host_port = port_def.get('published', 0)
            container_port = port_def.get('target', 0)
            protocol = port_def.get('protocol', 'tcp')
            if host_port and container_port:
                ports.append(PortBinding(host_port=host_port, container_port=container_port, protocol=protocol))
    return ports

def _parse_volumes(volumes_data: Any) -> List[VolumeMount]:
    volumes = []
    if not volumes_data:
        return volumes
    
    for vol_def in volumes_data if isinstance(volumes_data, list) else [volumes_data]:
        if isinstance(vol_def, str):
            # Parse "source:target:mode" format
            parts = vol_def.split(':')
            if len(parts) >= 2:
                source = parts[0]
                target = parts[1]
                readonly = len(parts) > 2 and 'ro' in parts[2]
                volumes.append(VolumeMount(source=source, target=target, readonly=readonly))
        elif isinstance(vol_def, dict):
            # Parse {type: , source: , target: , read_only: } format
            source = vol_def.get('source', '')
            target = vol_def.get('target', '')
            readonly = vol_def.get('read_only', False)
            if source and target:
                volumes.append(VolumeMount(source=source, target=target, readonly=readonly))
    return volumes

# Middle-level functions (A. Compose file management)
def read_compose(file_path: str, project_name: Optional[str] = None, logger: Optional[logging.Logger] = None) -> DockerCompose:
    logger = logger or _MODULE_LOGGER
    data = _parse_compose_yaml(file_path, logger=logger)
    version = data.get("version", DEFAULT_COMPOSE_VERSION)
    services_data = data.get("services", {})
    networks_data = data.get("networks", {})
    volumes_data = data.get("volumes", {})
    
    services = {}
    for name, s in services_data.items():
        # Parse all service fields
        svc = ComposeService(
            name=name,
            image=s.get("image"),
            container_name=s.get("container_name"),
            env_file=s.get("env_file"),
            environment=s.get("environment", {}),
            command=s.get("command"),
            entrypoint=s.get("entrypoint"),
            depends_on=s.get("depends_on", []),
            restart_policy=s.get("restart"),
            expose=s.get("expose", []),
            labels=s.get("labels", {}),
            secrets=s.get("secrets", []),
            configs=s.get("configs", []),
            logging=s.get("logging"),
            deploy=s.get("deploy"),
            privileged=s.get("privileged"),
            user=s.get("user"),
            ulimits=s.get("ulimits"),
            tmpfs=s.get("tmpfs", []),
            readonly_rootfs=s.get("read_only")
        )
        
        # Parse build spec
        if "build" in s:
            b = s["build"]
            svc.build = BuildSpec(
                context=b if isinstance(b, str) else b.get("context"),
                dockerfile=b.get("dockerfile") if isinstance(b, dict) else None,
                args=b.get("args", {}),
                target=b.get("target")
            )
        
        # Parse ports, volumes, networks, healthcheck
        svc.ports = _parse_ports(s.get("ports", []))
        svc.volumes = _parse_volumes(s.get("volumes", []))
        svc.networks = list(s.get("networks", {}).keys()) if isinstance(s.get("networks"), dict) else s.get("networks", [])
        svc.healthcheck = _parse_healthcheck(s.get("healthcheck"))
        
        services[name] = svc
    
    # Parse networks
    networks = {}
    for name, net_data in networks_data.items():
        networks[name] = NetworkSpec(
            name=name,
            driver=net_data.get("driver", "bridge"),
            external=net_data.get("external", False),
            labels=net_data.get("labels", {})
        )
    
    # Parse volumes
    volumes = {}
    for name, vol_data in volumes_data.items():
        volumes[name] = VolumeSpec(
            name=name,
            driver=vol_data.get("driver", "local"),
            external=vol_data.get("external", False),
            labels=vol_data.get("labels", {})
        )
    
    compose = DockerCompose(
        name=project_name or Path(file_path).stem,
        file_path=file_path,
        version=version,
        services=services,
        networks=networks,
        volumes=volumes
    )
    
    # Load env_files if any
    for svc in compose.services.values():
        if svc.env_file:
            if isinstance(svc.env_file, str):
                envs.load_env_file(svc.env_file)
            elif isinstance(svc.env_file, list):
                for ef in svc.env_file:
                    envs.load_env_file(ef)
    
    logger.info("Loaded compose %s with %d services", compose.name, len(compose.services))
    return compose

def write_compose(compose: DockerCompose, file_path: Optional[str] = None, overwrite: bool = True, create_backup: bool = True, backup_dir: Optional[str] = None, dry_run: bool = False, logger: Optional[logging.Logger] = None) -> str:
    logger = logger or _MODULE_LOGGER
    file_path = file_path or compose.file_path
    out_dict = compose.to_yaml_dict()
    if dry_run:
        logger.info("Dry-run: Would write compose to %s", file_path)
        return file_path
    _write_yaml(out_dict, file_path, backup=create_backup, logger=logger)
    logger.info("Wrote compose to %s", file_path)
    return file_path

def sync_compose(compose: DockerCompose, 
                 project_name: Optional[str] = None,
                 up_options: Optional[dict] = None,
                 build: bool = False,
                 no_build: bool = False,
                 pull: bool = False,
                 dry_run: bool = False,
                 logger: Optional[logging.Logger] = None,
                 timeout: Optional[int] = None) -> Dict[str, Any]:
    """Write compose and bring up services"""
    logger = logger or _MODULE_LOGGER
    logs.task_start(f"Syncing compose: {compose.name}")
    
    try:
        # Write compose file
        compose_path = write_compose(compose, dry_run=dry_run, logger=logger)
        
        # Preview changes
        changes = compose_preview_changes(compose, logger=logger)
        
        # Execute appropriate docker-compose command
        if dry_run:
            logger.info(f"Dry-run: Would sync {len(compose.services)} services")
            return {'dry_run': True, 'changes': changes}
        
        # Build images if needed
        if build and not no_build:
            compose_build(compose, nocache=False, logger=logger)
        
        # Pull images if needed
        if pull:
            compose_pull(compose, logger=logger)
        
        # Bring up services
        up_result = compose_up(
            compose,
            services=None,  # All services
            build=False,    # Already built if needed
            pull=False,     # Already pulled if needed
            detach=True,
            logger=logger
        )
        
        logs.task_pass(f"Sync completed for {compose.name}")
        return {
            'success': True,
            'compose_path': compose_path,
            'changes': changes,
            'up_result': up_result
        }
        
    except Exception as e:
        logs.task_fail(f"Sync failed: {e}")
        raise DockerOpsError(f"Compose sync failed: {e}") from e

def compose_preview_changes(compose: DockerCompose, 
                          logger: Optional[logging.Logger] = None) -> Dict[str, List[str]]:
    """Preview what would change when applying the compose"""
    logger = logger or _MODULE_LOGGER
    
    try:
        # Get current running state
        current_containers = compose_ps(compose, logger=logger)
        current_services = set(current_containers.keys())
        defined_services = set(compose.services.keys())
        
        changes = {
            'create': list(defined_services - current_services),
            'recreate': [],
            'unchanged': list(current_services.intersection(defined_services)),
            'remove': list(current_services - defined_services)
        }
        
        # Check which running services need recreation
        for service_name in changes['unchanged']:
            service = compose.services[service_name]
            container = current_containers[service_name]
            
            # Simple check: if image changed, needs recreate
            if service.image and container.image != service.image:
                changes['recreate'].append(service_name)
                changes['unchanged'].remove(service_name)
        
        logger.info(f"Changes preview: {changes}")
        return changes
        
    except Exception as e:
        logger.warning(f"Could not generate changes preview: {e}")
        return {'create': [], 'recreate': [], 'unchanged': [], 'remove': [], 'error': str(e)}

def backup_compose(compose: DockerCompose, backup_dir: str, include_images: bool = False, image_service_list: Optional[List[str]] = None, compress: bool = True, logger: Optional[logging.Logger] = None, dry_run: bool = False) -> str:
    """Backup compose configuration and optionally images"""
    logger = logger or _MODULE_LOGGER
    logs.task_start(f"Backing up compose: {compose.name}")
    
    backup_dir = Path(backup_dir)
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = dt_ops.current_datetime().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{compose.name}_{timestamp}"
    
    if dry_run:
        logger.info(f"Dry-run: Would create backup {backup_name}")
        return str(backup_dir / backup_name)
    
    # Create temporary directory for backup contents
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Backup compose file
        compose_backup_path = temp_path / "docker-compose.yml"
        write_compose(compose, str(compose_backup_path), create_backup=False, logger=logger)
        
        # Backup environment files
        env_dir = temp_path / "env"
        env_dir.mkdir(exist_ok=True)
        for svc in compose.services.values():
            if svc.env_file:
                env_files = [svc.env_file] if isinstance(svc.env_file, str) else svc.env_file
                for env_file in env_files:
                    if files.file_exists(env_file):
                        files.copy_file(env_file, str(env_dir / Path(env_file).name))
        
        # Backup images if requested
        if include_images:
            images_dir = temp_path / "images"
            images_dir.mkdir(exist_ok=True)
            services_to_backup = image_service_list or list(compose.services.keys())
            
            for service_name in services_to_backup:
                if service_name in compose.services:
                    service = compose.services[service_name]
                    if service.image:
                        try:
                            image_path = images_dir / f"{service_name}.tar"
                            save_image(service.image, path=str(image_path), compress=False, logger=logger)
                        except Exception as e:
                            logger.warning(f"Failed to backup image for {service_name}: {e}")
        
        # Create archive
        backup_path = backup_dir / backup_name
        if compress:
            backup_path = backup_path.with_suffix('.tar.gz')
            with tarfile.open(backup_path, 'w:gz') as tar:
                tar.add(temp_path, arcname=backup_name)
        else:
            backup_path = backup_path.with_suffix('.tar')
            with tarfile.open(backup_path, 'w') as tar:
                tar.add(temp_path, arcname=backup_name)
    
    logger.info(f"Backup created: {backup_path}")
    return str(backup_path)

def restore_compose(backup_path: str, restore_dir: str, load_images: bool = True, logger: Optional[logging.Logger] = None, dry_run: bool = False) -> DockerCompose:
    """Restore compose from backup"""
    logger = logger or _MODULE_LOGGER
    logs.task_start(f"Restoring compose from: {backup_path}")
    
    backup_path = Path(backup_path)
    restore_dir = Path(restore_dir)
    
    if dry_run:
        logger.info(f"Dry-run: Would restore from {backup_path} to {restore_dir}")
        return read_compose(str(restore_dir / "docker-compose.yml"), logger=logger)
    
    if not backup_path.exists():
        raise DockerOpsError(f"Backup file not found: {backup_path}")
    
    # Extract backup
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Extract archive
        with tarfile.open(backup_path, 'r') as tar:
            tar.extractall(temp_path)
        
        # Find the backup contents (handle both flat and nested structures)
        backup_contents = list(temp_path.iterdir())
        if len(backup_contents) == 1 and backup_contents[0].is_dir():
            backup_root = backup_contents[0]
        else:
            backup_root = temp_path
        
        # Restore compose file
        compose_file = backup_root / "docker-compose.yml"
        if not compose_file.exists():
            # Try to find any yml file
            yml_files = list(backup_root.glob("*.yml")) + list(backup_root.glob("*.yaml"))
            if yml_files:
                compose_file = yml_files[0]
            else:
                raise DockerOpsError("No compose file found in backup")
        
        restored_compose_path = restore_dir / compose_file.name
        files.copy_file(str(compose_file), str(restored_compose_path))
        
        # Restore environment files
        env_backup_dir = backup_root / "env"
        if env_backup_dir.exists():
            for env_file in env_backup_dir.iterdir():
                if env_file.is_file():
                    files.copy_file(str(env_file), str(restore_dir / env_file.name))
        
        # Restore images if requested
        if load_images:
            images_dir = backup_root / "images"
            if images_dir.exists():
                for image_file in images_dir.iterdir():
                    if image_file.suffix == '.tar':
                        try:
                            load_image(str(image_file), logger=logger)
                        except Exception as e:
                            logger.warning(f"Failed to load image {image_file}: {e}")
        
        # Load and return the restored compose
        compose = read_compose(str(restored_compose_path), logger=logger)
        logger.info(f"Restored compose: {compose.name}")
        return compose

# B. Service Management
def add_service(compose: DockerCompose, service: ComposeService, overwrite: bool = False, dry_run: bool = False, logger: Optional[logging.Logger] = None) -> bool:
    logger = logger or _MODULE_LOGGER
    if service.name in compose.services and not overwrite:
        logger.warning("Service %s already exists; skipping", service.name)
        return False
    compose.services[service.name] = service
    if not dry_run:
        write_compose(compose, logger=logger)
    logger.info("Added service %s to compose %s", service.name, compose.name)
    return True

def add_services(compose: DockerCompose, services: List[ComposeService], overwrite: bool = False, dry_run: bool = False, logger: Optional[logging.Logger] = None) -> List[bool]:
    results = []
    for service in services:
        try:
            result = add_service(compose, service, overwrite=overwrite, dry_run=dry_run, logger=logger)
            results.append(result)
        except Exception as e:
            logger.error(f"Failed to add service {service.name}: {e}")
            results.append(False)
    return results

def read_service(compose: DockerCompose, service_name: str) -> Optional[ComposeService]:
    return compose.services.get(service_name)

def read_services(compose: DockerCompose, service_names: Optional[List[str]] = None) -> List[ComposeService]:
    if service_names is None:
        return list(compose.services.values())
    return [compose.services[name] for name in service_names if name in compose.services]

def remove_service(compose: DockerCompose, service_name: str, backup: bool = True, dry_run: bool = False, logger: Optional[logging.Logger] = None) -> bool:
    logger = logger or _MODULE_LOGGER
    if service_name not in compose.services:
        logger.warning("Service %s not found in compose %s", service_name, compose.name)
        return False
    
    if backup:
        # Create revision before removal
        create_service_revision(compose.services[service_name], description=f"Pre-removal backup of {service_name}", logger=logger)
    
    del compose.services[service_name]
    
    if not dry_run:
        write_compose(compose, logger=logger)
    
    logger.info("Removed service %s from compose %s", service_name, compose.name)
    return True

def remove_services(compose: DockerCompose, service_names: List[str], backup: bool = True, dry_run: bool = False, logger: Optional[logging.Logger] = None) -> List[bool]:
    results = []
    for service_name in service_names:
        try:
            result = remove_service(compose, service_name, backup=backup, dry_run=dry_run, logger=logger)
            results.append(result)
        except Exception as e:
            logger.error(f"Failed to remove service {service_name}: {e}")
            results.append(False)
    return results

def update_service(compose: DockerCompose, service_name: str, **updates) -> ServiceRevision:
    if service_name not in compose.services:
        raise DockerOpsError(f"Service {service_name} not found")
    
    service = compose.services[service_name]
    
    # Create revision before update
    revision = create_service_revision(service, description=f"Update: {list(updates.keys())}")
    
    # Apply updates
    for key, value in updates.items():
        if hasattr(service, key):
            setattr(service, key, value)
        else:
            raise DockerOpsError(f"Invalid service attribute: {key}")
    
    # Validate the updated service
    errors = service.validate()
    if errors:
        raise DockerOpsError(f"Service validation failed after update: {errors}")
    
    return revision

def update_services(compose: DockerCompose, updates: Dict[str, Dict], dry_run: bool = False, logger: Optional[logging.Logger] = None) -> Dict[str, ServiceRevision]:
    logger = logger or _MODULE_LOGGER
    revisions = {}
    
    for service_name, service_updates in updates.items():
        try:
            revision = update_service(compose, service_name, **service_updates)
            revisions[service_name] = revision
        except Exception as e:
            logger.error(f"Failed to update service {service_name}: {e}")
    
    if not dry_run and revisions:
        write_compose(compose, logger=logger)
    
    return revisions

# C. Per-Service Runtime
def service_up(service: ComposeService, project_name: Optional[str] = None, detach: bool = True, build_if_missing: bool = False, no_build: bool = False, pull: bool = False, timeout: int = 300, dry_run: bool = False, logger: Optional[logging.Logger] = None) -> DockerContainer:
    logger = logger or _MODULE_LOGGER
    logs.task_start(f"Starting service: {service.name}")
    
    if dry_run:
        logger.info(f"Dry-run: Would start service {service.name}")
        return DockerContainer(id="dry-run", name=service.name, image=service.image or "unknown", status="dry-run")
    
    # Build image if needed
    if service.build and build_if_missing and not no_build:
        service_build(service, logger=logger)
    
    # Pull image if needed
    if pull and service.image:
        service_pull(service, logger=logger)
    
    # Use docker-compose to start the specific service
    compose_dir = Path(service.build.context).parent if service.build and service.build.context else Path.cwd()
    compose_file = compose_dir / "docker-compose.yml"
    
    if not compose_file.exists():
        raise DockerOpsError(f"Compose file not found: {compose_file}")
    
    cmd = ["docker-compose", "-f", str(compose_file)]
    if project_name:
        cmd.extend(["-p", project_name])
    
    cmd.extend(["up", "-d" if detach else "", service.name])
    cmd = [c for c in cmd if c]  # Remove empty strings
    
    try:
        result = _run_cli(cmd, timeout=timeout, logger=logger)
        
        # Get the container info
        containers = compose_ps(read_compose(str(compose_file), project_name=project_name, logger=logger), logger=logger)
        if service.name in containers:
            service.container = containers[service.name]
            return containers[service.name]
        else:
            raise DockerOpsError(f"Service {service.name} started but container not found")
            
    except Exception as e:
        logs.task_fail(f"Failed to start service {service.name}: {e}")
        raise

def service_down(service: ComposeService, remove_volumes: bool = False, remove_container: bool = True, force: bool = False, timeout: int = 30, dry_run: bool = False, logger: Optional[logging.Logger] = None) -> None:
    logger = logger or _MODULE_LOGGER
    logs.task_start(f"Stopping service: {service.name}")
    
    if dry_run:
        logger.info(f"Dry-run: Would stop service {service.name}")
        return
    
    compose_dir = Path(service.build.context).parent if service.build and service.build.context else Path.cwd()
    compose_file = compose_dir / "docker-compose.yml"
    
    if not compose_file.exists():
        raise DockerOpsError(f"Compose file not found: {compose_file}")
    
    cmd = ["docker-compose", "-f", str(compose_file), "stop", service.name]
    if force:
        cmd = ["docker-compose", "-f", str(compose_file), "kill", service.name]
    
    if remove_container:
        cmd = ["docker-compose", "-f", str(compose_file), "rm", "-f", service.name]
        if remove_volumes:
            cmd.append("-v")
    
    try:
        _run_cli(cmd, timeout=timeout, logger=logger)
        service.container = None
        logs.task_pass(f"Stopped service {service.name}")
    except Exception as e:
        logs.task_fail(f"Failed to stop service {service.name}: {e}")
        raise

def service_restart(service: ComposeService, timeout: int = 10, dry_run: bool = False, logger: Optional[logging.Logger] = None) -> None:
    logger = logger or _MODULE_LOGGER
    service_down(service, timeout=timeout, dry_run=dry_run, logger=logger)
    service_up(service, timeout=timeout, dry_run=dry_run, logger=logger)

def service_logs(service: ComposeService, follow: bool = False, tail: Optional[Union[str, int]] = 'all', logger: Optional[logging.Logger] = None) -> Iterator[LogLine]:
    logger = logger or _MODULE_LOGGER
    
    if not service.container:
        # Find the container
        compose_dir = Path(service.build.context).parent if service.build and service.build.context else Path.cwd()
        compose_file = compose_dir / "docker-compose.yml"
        
        if compose_file.exists():
            compose = read_compose(str(compose_file), logger=logger)
            containers = compose_ps(compose, logger=logger)
            if service.name in containers:
                service.container = containers[service.name]
            else:
                raise DockerOpsError(f"Service {service.name} not running")
        else:
            raise DockerOpsError(f"Compose file not found: {compose_file}")
    
    return service.container.logs(follow=follow, tail=tail, logger=logger)

def service_pull(service: ComposeService, retry: int = DEFAULT_PULL_RETRIES, dry_run: bool = False, logger: Optional[logging.Logger] = None) -> DockerImage:
    logger = logger or _MODULE_LOGGER
    
    if not service.image:
        raise DockerOpsError(f"Service {service.name} has no image to pull")
    
    if dry_run:
        logger.info(f"Dry-run: Would pull image {service.image}")
        return DockerImage(name=service.image, tag="latest")
    
    return pull_image(service.image, retries=retry, logger=logger)

def service_push(service: ComposeService, auth: Optional[dict] = None, retry: int = DEFAULT_PULL_RETRIES, dry_run: bool = False, logger: Optional[logging.Logger] = None) -> None:
    logger = logger or _MODULE_LOGGER
    
    if not service.image:
        raise DockerOpsError(f"Service {service.name} has no image to push")
    
    if dry_run:
        logger.info(f"Dry-run: Would push image {service.image}")
        return
    
    push_image(service.image, auth=auth, retries=retry, logger=logger)

def service_build(service: ComposeService, nocache: bool = False, pull: bool = False, build_args: Optional[dict] = None, logger: Optional[logging.Logger] = None, dry_run: bool = False, timeout: int = 3600) -> DockerImage:
    logger = logger or _MODULE_LOGGER
    
    if not service.build:
        raise DockerOpsError(f"Service {service.name} has no build configuration")
    
    if dry_run:
        logger.info(f"Dry-run: Would build image for {service.name}")
        return DockerImage(name=service.name, tag="latest")
    
    context = service.build.context or "."
    dockerfile = service.build.dockerfile or "Dockerfile"
    args = build_args or service.build.args or {}
    
    return build_image(context, dockerfile, service.name, nocache=nocache, pull=pull, build_args=args, timeout=timeout, logger=logger)

def service_exec(service: ComposeService, command: Union[str, List[str]], user: Optional[str] = None, stream: bool = False, tty: bool = False, timeout: Optional[int] = None, logger: Optional[logging.Logger] = None) -> ExecResult:
    logger = logger or _MODULE_LOGGER
    
    if not service.container:
        raise DockerOpsError(f"Service {service.name} is not running")
    
    if isinstance(command, str):
        command = shlex.split(command)
    
    return service.container.exec(command, user=user, stream=stream, tty=tty, logger=logger)

def service_commit(service: ComposeService, tag: str, message: Optional[str] = None, logger: Optional[logging.Logger] = None, dry_run: bool = False) -> DockerImage:
    logger = logger or _MODULE_LOGGER
    
    if not service.container:
        raise DockerOpsError(f"Service {service.name} is not running")
    
    if dry_run:
        logger.info(f"Dry-run: Would commit container {service.container.id} as {tag}")
        return DockerImage(name=tag, tag="latest")
    
    return service.container.commit(tag=tag, message=message, logger=logger)

def service_attach(service: ComposeService, logs: bool = False, stream: bool = True, logger: Optional[logging.Logger] = None) -> None:
    logger = logger or _MODULE_LOGGER
    
    if not service.container:
        raise DockerOpsError(f"Service {service.name} is not running")
    
    service.container.attach(logs=logs, stream=stream, logger=logger)

def service_kill(service: ComposeService, signal: str = 'SIGKILL', logger: Optional[logging.Logger] = None, dry_run: bool = False) -> None:
    logger = logger or _MODULE_LOGGER
    
    if not service.container:
        raise DockerOpsError(f"Service {service.name} is not running")
    
    if dry_run:
        logger.info(f"Dry-run: Would kill service {service.name} with signal {signal}")
        return
    
    service.container.kill(signal=signal, logger=logger)

def service_inspect(service: ComposeService, refresh: bool = True, logger: Optional[logging.Logger] = None) -> Dict:
    logger = logger or _MODULE_LOGGER
    
    if not service.container or refresh:
        # Find and update container info
        compose_dir = Path(service.build.context).parent if service.build and service.build.context else Path.cwd()
        compose_file = compose_dir / "docker-compose.yml"
        
        if compose_file.exists():
            compose = read_compose(str(compose_file), logger=logger)
            containers = compose_ps(compose, logger=logger)
            if service.name in containers:
                service.container = containers[service.name]
            else:
                raise DockerOpsError(f"Service {service.name} not running")
        else:
            raise DockerOpsError(f"Compose file not found: {compose_file}")
    
    return service.container.inspect or {}

def service_is_running(service: ComposeService, logger: Optional[logging.Logger] = None) -> bool:
    logger = logger or _MODULE_LOGGER
    
    try:
        inspect_data = service_inspect(service, refresh=True, logger=logger)
        return inspect_data.get('State', {}).get('Running', False)
    except DockerOpsError:
        return False

# D. Compose-Wide Runtime
def compose_up(compose: DockerCompose, services: Optional[List[str]] = None, project_name: Optional[str] = None, build: bool = False, no_build: bool = False, pull: bool = False, detach: bool = True, logger: Optional[logging.Logger] = None, dry_run: bool = False) -> Dict[str, Any]:
    logger = logger or _MODULE_LOGGER
    logs.task_start(f"Starting compose: {compose.name}")
    
    if dry_run:
        logger.info(f"Dry-run: Would start compose {compose.name} with services {services}")
        return {'dry_run': True, 'services': services or list(compose.services.keys())}
    
    cmd = ["docker-compose", "-f", compose.file_path]
    if project_name:
        cmd.extend(["-p", project_name])
    
    if pull:
        cmd.extend(["pull"])
        if services:
            cmd.extend(services)
        _run_cli(cmd, logger=logger)
        cmd = cmd[:-2]  # Remove pull and services
    
    cmd.extend(["up"])
    if detach:
        cmd.append("-d")
    if build and not no_build:
        cmd.append("--build")
    if services:
        cmd.extend(services)
    
    try:
        result = _run_cli(cmd, logger=logger)
        
        # Get container status
        containers = compose_ps(compose, logger=logger)
        
        logs.task_pass(f"Started compose {compose.name}")
        return {
            'success': True,
            'containers': {name: container.status for name, container in containers.items()},
            'stdout': result.stdout,
            'stderr': result.stderr
        }
    except Exception as e:
        logs.task_fail(f"Failed to start compose {compose.name}: {e}")
        raise

def compose_down(compose: DockerCompose, remove_volumes: bool = False, remove_images: Optional[str] = None, timeout: int = 60, logger: Optional[logging.Logger] = None, dry_run: bool = False) -> Dict[str, Any]:
    logger = logger or _MODULE_LOGGER
    logs.task_start(f"Stopping compose: {compose.name}")
    
    if dry_run:
        logger.info(f"Dry-run: Would stop compose {compose.name}")
        return {'dry_run': True}
    
    cmd = ["docker-compose", "-f", compose.file_path, "down"]
    if remove_volumes:
        cmd.append("-v")
    if remove_images:
        cmd.extend(["--rmi", remove_images])
    if timeout:
        cmd.extend(["-t", str(timeout)])
    
    try:
        result = _run_cli(cmd, logger=logger)
        
        logs.task_pass(f"Stopped compose {compose.name}")
        return {
            'success': True,
            'stdout': result.stdout,
            'stderr': result.stderr
        }
    except Exception as e:
        logs.task_fail(f"Failed to stop compose {compose.name}: {e}")
        raise

def compose_restart(compose: DockerCompose, services: Optional[List[str]] = None, logger: Optional[logging.Logger] = None, dry_run: bool = False) -> Dict[str, Any]:
    logger = logger or _MODULE_LOGGER
    
    if dry_run:
        logger.info(f"Dry-run: Would restart compose {compose.name}")
        return {'dry_run': True}
    
    cmd = ["docker-compose", "-f", compose.file_path, "restart"]
    if services:
        cmd.extend(services)
    
    try:
        result = _run_cli(cmd, logger=logger)
        return {
            'success': True,
            'stdout': result.stdout,
            'stderr': result.stderr
        }
    except Exception as e:
        logger.error(f"Failed to restart compose {compose.name}: {e}")
        raise

def compose_ps(compose: DockerCompose, logger: Optional[logging.Logger] = None) -> Dict[str, DockerContainer]:
    logger = logger or _MODULE_LOGGER
    
    cmd = ["docker-compose", "-f", compose.file_path, "ps", "--format", "json"]
    
    try:
        result = _run_cli(cmd, logger=logger)
        containers_data = json.loads(result.stdout)
        
        containers = {}
        for container_data in containers_data:
            name = container_data.get('Service', container_data.get('Name', ''))
            container = DockerContainer(
                id=container_data.get('ID', ''),
                name=container_data.get('Name', ''),
                image=container_data.get('Image', ''),
                status=container_data.get('State', ''),
                started_at=container_data.get('CreatedAt', '')
            )
            containers[name] = container
        
        return containers
    except Exception as e:
        logger.warning(f"Failed to get compose ps in JSON format: {e}")
        # Fallback to parsing text output
        return _parse_compose_ps_text(compose, logger)

def _parse_compose_ps_text(compose: DockerCompose, logger: logging.Logger) -> Dict[str, DockerContainer]:
    """Fallback method to parse docker-compose ps text output"""
    cmd = ["docker-compose", "-f", compose.file_path, "ps"]
    result = _run_cli(cmd, logger=logger)
    
    containers = {}
    lines = result.stdout.splitlines()
    
    if len(lines) < 2:  # Header + data
        return containers
    
    for line in lines[1:]:  # Skip header
        parts = line.split()
        if len(parts) >= 4:
            name = parts[0]
            container_id = parts[1] if len(parts) > 1 else 'unknown'
            image = parts[2] if len(parts) > 2 else 'unknown'
            status = ' '.join(parts[3:]) if len(parts) > 3 else 'unknown'
            
            containers[name] = DockerContainer(
                id=container_id,
                name=name,
                image=image,
                status=status
            )
    
    return containers

def compose_logs(compose: DockerCompose, services: Optional[List[str]] = None, follow: bool = False, tail: Optional[Union[str, int]] = 'all', logger: Optional[logging.Logger] = None) -> Iterator[LogLine]:
    logger = logger or _MODULE_LOGGER
    
    cmd = ["docker-compose", "-f", compose.file_path, "logs"]
    if follow:
        cmd.append("-f")
    if tail:
        cmd.extend(["--tail", str(tail)])
    if services:
        cmd.extend(services)
    
    try:
        result = _run_cli(cmd, capture=not follow, logger=logger)
        
        if not follow:
            # Return all logs at once for non-following mode
            for line in result.stdout.splitlines():
                yield _parse_log_line(line)
        else:
            # For follow mode, we'd need to handle streaming
            # This is simplified - in practice you'd need proper stream handling
            logger.warning("Follow mode for compose logs is not fully implemented in this version")
            
    except Exception as e:
        logger.error(f"Failed to get compose logs: {e}")
        raise

def _parse_log_line(line: str) -> LogLine:
    """Parse a docker-compose log line into LogLine object"""
    # Basic parsing - adjust based on your docker-compose log format
    parts = line.split(' | ', 1)
    if len(parts) == 2:
        timestamp_service = parts[0]
        message = parts[1]
        
        # Try to extract timestamp and service
        timestamp_match = re.search(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})', timestamp_service)
        service_match = re.search(r'\|\s*(\w+)\s*\|', timestamp_service)
        
        return LogLine(
            timestamp=timestamp_match.group(1) if timestamp_match else None,
            service=service_match.group(1) if service_match else None,
            message=message
        )
    else:
        return LogLine(message=line)

def compose_config(compose: DockerCompose, logger: Optional[logging.Logger] = None) -> str:
    logger = logger or _MODULE_LOGGER
    
    cmd = ["docker-compose", "-f", compose.file_path, "config"]
    
    try:
        result = _run_cli(cmd, logger=logger)
        return result.stdout
    except Exception as e:
        logger.error(f"Failed to get compose config: {e}")
        raise

def compose_pull(compose: DockerCompose, services: Optional[List[str]] = None, parallel: int = 4, logger: Optional[logging.Logger] = None, dry_run: bool = False) -> Dict[str, DockerImage]:
    logger = logger or _MODULE_LOGGER
    
    if dry_run:
        logger.info(f"Dry-run: Would pull images for compose {compose.name}")
        return {svc: DockerImage(name=svc, tag="latest") for svc in services or compose.services.keys()}
    
    services_to_pull = services or list(compose.services.keys())
    results = {}
    
    def _pull_single_service(service_name: str) -> Tuple[str, Optional[DockerImage]]:
        if service_name in compose.services:
            service = compose.services[service_name]
            if service.image:
                try:
                    image = service_pull(service, logger=logger)
                    return service_name, image
                except Exception as e:
                    logger.error(f"Failed to pull image for {service_name}: {e}")
                    return service_name, None
        return service_name, None
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=parallel) as executor:
        future_to_service = {executor.submit(_pull_single_service, svc): svc for svc in services_to_pull}
        for future in concurrent.futures.as_completed(future_to_service):
            service_name, image = future.result()
            results[service_name] = image
    
    return results

def compose_build(compose: DockerCompose, services: Optional[List[str]] = None, nocache: bool = False, parallel: int = 2, logger: Optional[logging.Logger] = None, dry_run: bool = False) -> Dict[str, DockerImage]:
    logger = logger or _MODULE_LOGGER
    
    if dry_run:
        logger.info(f"Dry-run: Would build images for compose {compose.name}")
        return {svc: DockerImage(name=svc, tag="latest") for svc in services or [n for n, s in compose.services.items() if s.build]}
    
    services_to_build = services or [name for name, service in compose.services.items() if service.build]
    results = {}
    
    def _build_single_service(service_name: str) -> Tuple[str, Optional[DockerImage]]:
        if service_name in compose.services and compose.services[service_name].build:
            try:
                image = service_build(compose.services[service_name], nocache=nocache, logger=logger)
                return service_name, image
            except Exception as e:
                logger.error(f"Failed to build image for {service_name}: {e}")
                return service_name, None
        return service_name, None
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=parallel) as executor:
        future_to_service = {executor.submit(_build_single_service, svc): svc for svc in services_to_build}
        for future in concurrent.futures.as_completed(future_to_service):
            service_name, image = future.result()
            results[service_name] = image
    
    return results

# E. Conflict Detection
def docker_compose_down_conflict(compose: DockerCompose, services: Optional[List[str]] = None, project_name: Optional[str] = None, scan_scope: str = 'all', dry_run: bool = False, logger: Optional[logging.Logger] = None, timeout: int = 30, bring_down_conflicts: bool = False, force: bool = False) -> Dict:
    logger = logger or _MODULE_LOGGER
    
    conflicts = find_conflicting_containers_for_compose(compose, scan_scope=scan_scope, logger=logger)
    
    result = {
        'conflicts': conflicts,
        'resolved': [],
        'skipped': []
    }
    
    if dry_run:
        logger.info(f"Dry-run: Would handle {len(conflicts)} conflicts")
        return result
    
    if bring_down_conflicts:
        for conflict in conflicts:
            try:
                container_id = conflict.get('id')
                if container_id:
                    cmd = ["docker", "rm", "-f"]
                    if force:
                        cmd.append("--force")
                    cmd.append(container_id)
                    _run_cli(cmd, timeout=timeout, logger=logger)
                    result['resolved'].append(container_id)
            except Exception as e:
                logger.warning(f"Failed to resolve conflict {conflict.get('id')}: {e}")
                result['skipped'].append(conflict.get('id'))
    
    return result

def find_conflicting_containers_for_compose(compose: DockerCompose, scan_scope: str = 'all', logger: Optional[logging.Logger] = None) -> List[Dict]:
    logger = logger or _MODULE_LOGGER
    
    conflicts = []
    
    # Get all running containers
    client = _get_docker_client(logger=logger)
    if client:
        try:
            containers = client.containers.list(all=True)
            
            for container in containers:
                container_info = {
                    'id': container.id,
                    'name': container.name,
                    'image': container.image.tags[0] if container.image.tags else container.image.id,
                    'status': container.status,
                    'labels': container.labels
                }
                
                # Check if this container conflicts with our compose services
                if _is_container_conflicting(container_info, compose, scan_scope):
                    conflicts.append(container_info)
                    
        except DockerException as e:
            logger.error(f"Failed to list containers with SDK: {e}")
    
    # Fallback to CLI
    if not client or not conflicts:
        proc = _run_cli(["docker", "ps", "-a", "--format", "{{json .}}"], logger=logger)
        for line in proc.stdout.splitlines():
            try:
                container_info = json.loads(line)
                if _is_container_conflicting(container_info, compose, scan_scope):
                    conflicts.append(container_info)
            except json.JSONDecodeError:
                continue
    
    return conflicts

def _is_container_conflicting(container_info: Dict, compose: DockerCompose, scan_scope: str) -> bool:
    """Check if a container conflicts with compose services"""
    container_name = container_info.get('Names', container_info.get('name', ''))
    
    # Check by container name pattern
    for service_name in compose.services.keys():
        if service_name in container_name:
            return True
    
    # Check by network (if scope includes network)
    if scan_scope in ['all', 'network']:
        # This would require inspecting container networks
        pass
    
    # Check by volume (if scope includes volumes)
    if scan_scope in ['all', 'volumes']:
        # This would require inspecting container volumes
        pass
    
    return False

# F. Health & Monitoring
def service_health_check(service: ComposeService, timeout: int = 30, interval: float = 2.0, logger: Optional[logging.Logger] = None, use_container_health: bool = True, check_fn: Optional[Callable] = None) -> Dict[str, Any]:
    logger = logger or _MODULE_LOGGER
    
    if not service_is_running(service, logger=logger):
        return {'status': 'not_running', 'details': 'Service is not running'}
    
    if check_fn:
        # Use custom health check function
        try:
            result = check_fn(service)
            return {'status': 'healthy' if result else 'unhealthy', 'details': 'Custom check'}
        except Exception as e:
            return {'status': 'unhealthy', 'details': f'Custom check failed: {e}'}
    
    if use_container_health and service.container:
        try:
            inspect_data = service_inspect(service, refresh=True, logger=logger)
            health_status = inspect_data.get('State', {}).get('Health', {}).get('Status', 'unknown')
            return {'status': health_status, 'details': inspect_data.get('State', {}).get('Health', {})}
        except Exception as e:
            logger.warning(f"Failed to get container health status: {e}")
    
    # Fallback: try to exec a simple command
    try:
        result = service_exec(service, ["echo", "health_check"], timeout=5, logger=logger)
        return {'status': 'healthy' if result.rc == 0 else 'unhealthy', 'details': f'Exit code: {result.rc}'}
    except Exception as e:
        return {'status': 'unhealthy', 'details': f'Health check failed: {e}'}

def wait_service_healthy(service: ComposeService, timeout: int = 60, interval: float = 2.0, logger: Optional[logging.Logger] = None) -> bool:
    logger = logger or _MODULE_LOGGER
    
    start_time = dt_ops.current_datetime()
    
    while (dt_ops.current_datetime() - start_time).total_seconds() < timeout:
        health_result = service_health_check(service, logger=logger)
        if health_result.get('status') == 'healthy':
            return True
        dt_ops.sleep(interval)
    
    return False

def compose_health_check(compose: DockerCompose, timeout: int = 120, parallel: int = 4, fail_fast: bool = True, logger: Optional[logging.Logger] = None) -> Dict[str, Dict]:
    logger = logger or _MODULE_LOGGER
    
    results = {}
    
    def _check_single_service(service_name: str) -> Tuple[str, Dict]:
        service = compose.services[service_name]
        health_result = service_health_check(service, timeout=timeout, logger=logger)
        return service_name, health_result
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=parallel) as executor:
        future_to_service = {executor.submit(_check_single_service, name): name for name in compose.services.keys()}
        
        for future in concurrent.futures.as_completed(future_to_service):
            service_name, health_result = future.result()
            results[service_name] = health_result
            
            if fail_fast and health_result.get('status') != 'healthy':
                # Cancel remaining tasks
                for f in future_to_service:
                    if not f.done():
                        f.cancel()
                break
    
    return results

def wait_compose_healthy(compose: DockerCompose, timeout: int = 300, logger: Optional[logging.Logger] = None) -> bool:
    logger = logger or _MODULE_LOGGER
    logs.task_start(f"Waiting for {compose.name} to become healthy")
    
    start_time = dt_ops.current_datetime()
    check_interval = DEFAULT_HEALTH_INTERVAL
    
    while (dt_ops.current_datetime() - start_time).total_seconds() < timeout:
        try:
            health_results = compose_health_check(
                compose, 
                timeout=30, 
                parallel=DEFAULT_CONCURRENCY_LIMIT,
                fail_fast=False,
                logger=logger
            )
            
            all_healthy = all(
                result.get('status') == 'healthy' 
                for result in health_results.values()
            )
            
            if all_healthy:
                logs.task_pass(f"All services healthy for {compose.name}")
                return True
            
            # Log unhealthy services
            unhealthy = [
                svc for svc, result in health_results.items() 
                if result.get('status') != 'healthy'
            ]
            logger.info(f"Waiting for unhealthy services: {unhealthy}")
            
            dt_ops.sleep(check_interval)
            
        except Exception as e:
            logger.warning(f"Health check iteration failed: {e}")
            dt_ops.sleep(check_interval)
    
    logs.task_fail(f"Timeout waiting for {compose.name} to become healthy")
    return False

def wait_for_log_pattern(service: ComposeService, pattern: str, timeout: int = 60, logger: Optional[logging.Logger] = None) -> bool:
    logger = logger or _MODULE_LOGGER
    
    start_time = dt_ops.current_datetime()
    compiled_pattern = re.compile(pattern)
    
    try:
        for log_line in service_logs(service, follow=True, logger=logger):
            if compiled_pattern.search(log_line.message):
                return True
            
            if (dt_ops.current_datetime() - start_time).total_seconds() > timeout:
                break
                
            # Small sleep to prevent busy waiting
            dt_ops.sleep(0.1)
    except Exception as e:
        logger.warning(f"Error while waiting for log pattern: {e}")
    
    return False

# G. Rollback & Revisions
def create_service_revision(service: ComposeService, description: Optional[str] = None, logger: Optional[logging.Logger] = None) -> ServiceRevision:
    logger = logger or _MODULE_LOGGER
    
    revision = ServiceRevision(
        timestamp=dt_ops.current_datetime().isoformat(),
        spec=service_to_dict(service),
        description=description
    )
    
    service.history.append(revision)
    
    # Keep only last 10 revisions
    if len(service.history) > 10:
        service.history = service.history[-10:]
    
    logger.debug(f"Created revision for service {service.name}")
    return revision

def rollback_service(service: ComposeService, revision: ServiceRevision, dry_run: bool = False, restore_images: bool = True, logger: Optional[logging.Logger] = None, timeout: int = 180) -> bool:
    logger = logger or _MODULE_LOGGER
    
    if dry_run:
        logger.info(f"Dry-run: Would rollback service {service.name} to revision {revision.timestamp}")
        return True
    
    try:
        # Stop current service
        service_down(service, force=True, logger=logger)
        
        # Restore service configuration
        restored_service = dict_to_service(revision.spec)
        for attr_name in restored_service.__dict__:
            if attr_name not in ['name', 'history']:  # Preserve name and history
                setattr(service, attr_name, getattr(restored_service, attr_name))
        
        # Restore image if needed
        if restore_images and service.image:
            try:
                service_pull(service, logger=logger)
            except Exception as e:
                logger.warning(f"Failed to pull image during rollback: {e}")
        
        # Start service with restored configuration
        service_up(service, logger=logger)
        
        # Wait for service to become healthy
        if not wait_service_healthy(service, timeout=timeout, logger=logger):
            logger.warning(f"Service {service.name} not healthy after rollback")
        
        logger.info(f"Successfully rolled back service {service.name}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to rollback service {service.name}: {e}")
        raise RollbackFailed(f"Service rollback failed: {e}")

def create_compose_revision(compose: DockerCompose, description: Optional[str] = None, logger: Optional[logging.Logger] = None) -> DockerComposeRevision:
    logger = logger or _MODULE_LOGGER
    
    revision = DockerComposeRevision(
        timestamp=dt_ops.current_datetime().isoformat(),
        spec=compose.to_yaml_dict(),
        description=description
    )
    
    compose.history.append(revision)
    
    # Keep only last 5 revisions
    if len(compose.history) > 5:
        compose.history = compose.history[-5:]
    
    logger.debug(f"Created revision for compose {compose.name}")
    return revision

def rollback_compose(compose: DockerCompose, revision: DockerComposeRevision, dry_run: bool = False, logger: Optional[logging.Logger] = None) -> bool:
    logger = logger or _MODULE_LOGGER
    
    if dry_run:
        logger.info(f"Dry-run: Would rollback compose {compose.name} to revision {revision.timestamp}")
        return True
    
    try:
        # Write the revision spec to compose file
        _write_yaml(revision.spec, compose.file_path, backup=True, logger=logger)
        
        # Reload the compose
        rolled_back_compose = read_compose(compose.file_path, logger=logger)
        
        # Update current compose object
        for attr_name in rolled_back_compose.__dict__:
            if attr_name not in ['name', 'file_path', 'history']:
                setattr(compose, attr_name, getattr(rolled_back_compose, attr_name))
        
        logger.info(f"Successfully rolled back compose {compose.name}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to rollback compose {compose.name}: {e}")
        raise RollbackFailed(f"Compose rollback failed: {e}")

def auto_rollback_on_health_failure(compose: DockerCompose, service_name: str, max_attempts: int = 3, backoff_seconds: int = 10, dry_run: bool = False, logger: Optional[logging.Logger] = None) -> Dict:
    logger = logger or _MODULE_LOGGER
    
    if service_name not in compose.services:
        raise DockerOpsError(f"Service {service_name} not found in compose")
    
    service = compose.services[service_name]
    
    # Create revision before deployment
    revision = create_service_revision(service, description="Pre-deployment backup for auto-rollback", logger=logger)
    
    attempts = 0
    while attempts < max_attempts:
        try:
            if wait_service_healthy(service, timeout=60, logger=logger):
                return {
                    'success': True,
                    'attempts': attempts + 1,
                    'rolled_back': False
                }
            
            attempts += 1
            if attempts < max_attempts:
                logger.warning(f"Service {service_name} not healthy, attempt {attempts}/{max_attempts}. Waiting {backoff_seconds}s before retry.")
                dt_ops.sleep(backoff_seconds)
                
        except Exception as e:
            logger.error(f"Health check failed for service {service_name}: {e}")
            attempts += 1
    
    # All attempts failed, perform rollback
    logger.error(f"Service {service_name} failed health checks after {max_attempts} attempts. Performing rollback.")
    
    if not dry_run:
        try:
            rollback_service(service, revision, logger=logger)
            return {
                'success': False,
                'attempts': max_attempts,
                'rolled_back': True,
                'message': f"Service {service_name} rolled back due to health check failures"
            }
        except Exception as e:
            logger.error(f"Auto-rollback failed for service {service_name}: {e}")
            return {
                'success': False,
                'attempts': max_attempts,
                'rolled_back': False,
                'message': f"Service {service_name} failed and rollback also failed: {e}"
            }
    else:
        return {
            'success': False,
            'attempts': max_attempts,
            'rolled_back': True,
            'message': f"Dry-run: Would rollback service {service_name}"
        }

# H. Image Retention
def keep_image_versions(compose: DockerCompose, n: int = 5, dry_run: bool = False, logger: Optional[logging.Logger] = None, exclude_images: Optional[List[str]] = None) -> List[str]:
    logger = logger or _MODULE_LOGGER
    
    exclude_images = exclude_images or []
    removed_images = []
    
    # Get all images used by compose services
    service_images = get_service_images(compose)
    
    for service_name, image in service_images.items():
        if service_name in exclude_images or (image.name and any(excl in image.name for excl in exclude_images)):
            continue
        
        try:
            removed = keep_image_versions_by_name(image.name, keep=n, dry_run=dry_run, logger=logger)
            removed_images.extend(removed)
        except Exception as e:
            logger.warning(f"Failed to cleanup images for {service_name}: {e}")
    
    return removed_images

def keep_image_versions_by_name(image_name: str, keep: int = 5, dry_run: bool = False, force: bool = False, logger: Optional[logging.Logger] = None) -> List[str]:
    logger = logger or _MODULE_LOGGER
    
    # Get all images for the given name
    all_images = _list_images(filters={'reference': f'{image_name}:*'}, logger=logger)
    
    # Sort by creation date (newest first)
    all_images.sort(key=lambda x: x.created or dt_ops.current_datetime(), reverse=True)
    
    # Keep only the newest 'keep' images
    images_to_remove = all_images[keep:]
    
    removed = []
    for image in images_to_remove:
        try:
            if dry_run:
                logger.info(f"Dry-run: Would remove image {image.fullname}")
            else:
                image.remove(force=force, logger=logger)
                removed.append(image.fullname)
        except Exception as e:
            logger.warning(f"Failed to remove image {image.fullname}: {e}")
    
    return removed

def cleanup_old_images(compose: DockerCompose, keep_count: int = 3, dry_run: bool = True, logger: Optional[logging.Logger] = None) -> Dict:
    logger = logger or _MODULE_LOGGER
    
    result = {
        'removed': [],
        'errors': [],
        'dry_run': dry_run
    }
    
    try:
        removed = keep_image_versions(compose, n=keep_count, dry_run=dry_run, logger=logger)
        result['removed'] = removed
    except Exception as e:
        result['errors'].append(str(e))
    
    return result

def prune_orphans(dry_run: bool = True, logger: Optional[logging.Logger] = None) -> Dict:
    logger = logger or _MODULE_LOGGER
    
    if dry_run:
        logger.info("Dry-run: Would prune orphaned containers, networks, and images")
        return {'dry_run': True}
    
    result = {}
    
    try:
        # Prune containers
        cmd = ["docker", "container", "prune", "-f"]
        proc = _run_cli(cmd, logger=logger)
        result['containers'] = proc.stdout
        
        # Prune networks
        cmd = ["docker", "network", "prune", "-f"]
        proc = _run_cli(cmd, logger=logger)
        result['networks'] = proc.stdout
        
        # Prune images
        cmd = ["docker", "image", "prune", "-f"]
        proc = _run_cli(cmd, logger=logger)
        result['images'] = proc.stdout
        
    except Exception as e:
        logger.error(f"Pruning failed: {e}")
        result['error'] = str(e)
    
    return result

def prune_images(dry_run: bool = False, logger: Optional[logging.Logger] = None) -> Dict:
    logger = logger or _MODULE_LOGGER
    
    if dry_run:
        logger.info("Dry-run: Would prune dangling images")
        return {'dry_run': True}
    
    cmd = ["docker", "image", "prune", "-f"]
    
    try:
        proc = _run_cli(cmd, logger=logger)
        return {'success': True, 'output': proc.stdout}
    except Exception as e:
        logger.error(f"Image pruning failed: {e}")
        return {'success': False, 'error': str(e)}

def prune_volumes(dry_run: bool = False, logger: Optional[logging.Logger] = None) -> Dict:
    logger = logger or _MODULE_LOGGER
    
    if dry_run:
        logger.info("Dry-run: Would prune unused volumes")
        return {'dry_run': True}
    
    cmd = ["docker", "volume", "prune", "-f"]
    
    try:
        proc = _run_cli(cmd, logger=logger)
        return {'success': True, 'output': proc.stdout}
    except Exception as e:
        logger.error(f"Volume pruning failed: {e}")
        return {'success': False, 'error': str(e)}

def prune_networks(dry_run: bool = False, logger: Optional[logging.Logger] = None) -> Dict:
    logger = logger or _MODULE_LOGGER
    
    if dry_run:
        logger.info("Dry-run: Would prune unused networks")
        return {'dry_run': True}
    
    cmd = ["docker", "network", "prune", "-f"]
    
    try:
        proc = _run_cli(cmd, logger=logger)
        return {'success': True, 'output': proc.stdout}
    except Exception as e:
        logger.error(f"Network pruning failed: {e}")
        return {'success': False, 'error': str(e)}

# I. Bulk Operations
def bulk_services_up(services: List[ComposeService], parallel: bool = True, concurrency: int = 4, logger: Optional[logging.Logger] = None, dry_run: bool = False) -> Dict[str, Dict]:
    logger = logger or _MODULE_LOGGER
    
    results = {}
    
    def _start_single_service(service: ComposeService) -> Tuple[str, Dict]:
        try:
            container = service.up(dry_run=dry_run, logger=logger)
            return service.name, {'success': True, 'container': container.id if container else None}
        except Exception as e:
            return service.name, {'success': False, 'error': str(e)}
    
    if parallel:
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
            future_to_service = {executor.submit(_start_single_service, svc): svc.name for svc in services}
            for future in concurrent.futures.as_completed(future_to_service):
                service_name, result = future.result()
                results[service_name] = result
    else:
        for service in services:
            service_name, result = _start_single_service(service)
            results[service_name] = result
    
    return results

def bulk_services_down(services: List[ComposeService], force: bool = False, concurrency: int = 4, logger: Optional[logging.Logger] = None, dry_run: bool = False) -> Dict[str, Dict]:
    logger = logger or _MODULE_LOGGER
    
    results = {}
    
    def _stop_single_service(service: ComposeService) -> Tuple[str, Dict]:
        try:
            service.down(force=force, dry_run=dry_run, logger=logger)
            return service.name, {'success': True}
        except Exception as e:
            return service.name, {'success': False, 'error': str(e)}
    
    if concurrency > 1:
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
            future_to_service = {executor.submit(_stop_single_service, svc): svc.name for svc in services}
            for future in concurrent.futures.as_completed(future_to_service):
                service_name, result = future.result()
                results[service_name] = result
    else:
        for service in services:
            service_name, result = _stop_single_service(service)
            results[service_name] = result
    
    return results

def bulk_services_restart(services: List[ComposeService], concurrency: int = 4, logger: Optional[logging.Logger] = None, dry_run: bool = False) -> Dict[str, Dict]:
    logger = logger or _MODULE_LOGGER
    
    # First stop all services
    stop_results = bulk_services_down(services, concurrency=concurrency, dry_run=dry_run, logger=logger)
    
    # Then start all services
    start_results = bulk_services_up(services, concurrency=concurrency, dry_run=dry_run, logger=logger)
    
    # Combine results
    results = {}
    for service in services:
        stop_success = stop_results.get(service.name, {}).get('success', False)
        start_success = start_results.get(service.name, {}).get('success', False)
        results[service.name] = {
            'success': stop_success and start_success,
            'stop_result': stop_results.get(service.name),
            'start_result': start_results.get(service.name)
        }
    
    return results

def update_multiple_services(compose: DockerCompose, service_updates: Dict[str, Dict], dry_run: bool = False, logger: Optional[logging.Logger] = None) -> Dict[str, ServiceRevision]:
    return update_services(compose, service_updates, dry_run=dry_run, logger=logger)

# J. Validation & Utilities
def validate_compose(compose: DockerCompose, logger: Optional[logging.Logger] = None) -> List[str]:
    return compose.validate()

def validate_service(service: ComposeService, logger: Optional[logging.Logger] = None) -> List[str]:
    return service.validate()

def compare_services(service_a: ComposeService, service_b: ComposeService) -> Dict[str, Any]:
    differences = {}
    
    for attr_name in service_a.__dict__:
        if attr_name not in ['history', 'container', 'image_obj']:  # Skip runtime attributes
            value_a = getattr(service_a, attr_name)
            value_b = getattr(service_b, attr_name)
            
            if value_a != value_b:
                differences[attr_name] = {
                    'service_a': value_a,
                    'service_b': value_b
                }
    
    return differences

def service_to_dict(service: ComposeService) -> Dict[str, Any]:
    """Convert service to dictionary, excluding runtime attributes"""
    excluded = ['history', 'container', 'image_obj']
    return {k: v for k, v in service.__dict__.items() if k not in excluded}

def dict_to_service(service_dict: Dict[str, Any]) -> ComposeService:
    """Create service from dictionary"""
    name = service_dict.get('name', 'unknown')
    service = ComposeService(name=name)
    
    for key, value in service_dict.items():
        if hasattr(service, key):
            setattr(service, key, value)
    
    return service

def get_service_images(compose: DockerCompose) -> Dict[str, DockerImage]:
    images = {}
    
    for service_name, service in compose.services.items():
        if service.image:
            # Parse image name and tag
            if ':' in service.image:
                name, tag = service.image.split(':', 1)
            else:
                name, tag = service.image, 'latest'
            
            images[service_name] = DockerImage(name=name, tag=tag)
    
    return images

def pull_service_images(service: ComposeService, parallel: bool = False, logger: Optional[logging.Logger] = None, dry_run: bool = False) -> DockerImage:
    return service_pull(service, dry_run=dry_run, logger=logger)

def push_service_images(service: ComposeService, auth: Optional[dict] = None, logger: Optional[logging.Logger] = None, dry_run: bool = False) -> None:
    service_push(service, auth=auth, dry_run=dry_run, logger=logger)

def save_service_image(service: ComposeService, output_path: str, compress: bool = True, logger: Optional[logging.Logger] = None, dry_run: bool = False) -> str:
    logger = logger or _MODULE_LOGGER
    
    if not service.image:
        raise DockerOpsError(f"Service {service.name} has no image to save")
    
    if dry_run:
        logger.info(f"Dry-run: Would save image {service.image} to {output_path}")
        return output_path
    
    return save_image(service.image, path=output_path, compress=compress, logger=logger)

def load_service_image(input_path: str, logger: Optional[logging.Logger] = None, dry_run: bool = False) -> DockerImage:
    return load_image(input_path, dry_run=dry_run, logger=logger)

# K. Tagging & Workflows
def tag_service_image(service: ComposeService, tag: str, push: bool = False, auth: Optional[dict] = None, logger: Optional[logging.Logger] = None, dry_run: bool = False) -> DockerImage:
    logger = logger or _MODULE_LOGGER
    
    if not service.image:
        raise DockerOpsError(f"Service {service.name} has no image to tag")
    
    if dry_run:
        logger.info(f"Dry-run: Would tag image {service.image} as {tag}")
        return DockerImage(name=service.image, tag=tag)
    
    image = tag_image(service.image, new_tag=tag, logger=logger)
    
    if push:
        push_image(f"{image.name}:{tag}", auth=auth, logger=logger)
    
    return image

def retag_rotate_image(repository: str, new_tag: str, retain: int = 5, push: bool = False, auth: Optional[dict] = None, logger: Optional[logging.Logger] = None, dry_run: bool = False) -> Dict:
    logger = logger or _MODULE_LOGGER
    
    # Get current images for the repository
    images = _list_images(filters={'reference': f'{repository}:*'}, logger=logger)
    
    if not images:
        raise DockerOpsError(f"No images found for repository {repository}")
    
    # Find the latest image (by creation date)
    latest_image = max(images, key=lambda x: x.created or dt_ops.current_datetime())
    
    # Tag the latest image with new tag
    if dry_run:
        logger.info(f"Dry-run: Would tag {latest_image.fullname} as {repository}:{new_tag}")
        new_image = DockerImage(name=repository, tag=new_tag)
    else:
        new_image = latest_image.tag(new_tag, logger=logger)
    
    # Push if requested
    if push and not dry_run:
        new_image.push(auth=auth, logger=logger)
    
    # Cleanup old images
    removed = keep_image_versions_by_name(repository, keep=retain, dry_run=dry_run, logger=logger)
    
    return {
        'new_image': new_image.fullname,
        'removed_images': removed,
        'pushed': push
    }

def deploy_compose_release(compose: DockerCompose, service_tag_map: Dict[str, str], health_timeout: int = 300, auto_rollback: bool = True, logger: Optional[logging.Logger] = None, dry_run: bool = False) -> Dict:
    logger = logger or _MODULE_LOGGER
    logs.task_start(f"Deploying release for compose: {compose.name}")
    
    results = {
        'updated_services': [],
        'failed_services': [],
        'rolled_back_services': []
    }
    
    # Update service images with new tags
    for service_name, new_tag in service_tag_map.items():
        if service_name in compose.services:
            service = compose.services[service_name]
            
            if service.image:
                # Extract image name without tag
                image_parts = service.image.split(':')
                image_name = image_parts[0]
                new_image = f"{image_name}:{new_tag}"
                
                # Create revision before update
                revision = create_service_revision(service, description=f"Pre-release update to {new_image}")
                
                try:
                    # Update service image
                    service.image = new_image
                    results['updated_services'].append(service_name)
                    
                    # Pull new image
                    if not dry_run:
                        service_pull(service, logger=logger)
                    
                    # Restart service with new image
                    service_restart(service, dry_run=dry_run, logger=logger)
                    
                    # Health check with auto-rollback
                    if auto_rollback and not dry_run:
                        health_result = auto_rollback_on_health_failure(
                            compose, service_name, max_attempts=3, 
                            backoff_seconds=10, dry_run=dry_run, logger=logger
                        )
                        
                        if health_result.get('rolled_back'):
                            results['rolled_back_services'].append(service_name)
                            results['updated_services'].remove(service_name)
                            results['failed_services'].append(service_name)
                    
                except Exception as e:
                    logger.error(f"Failed to deploy {service_name}: {e}")
                    results['failed_services'].append(service_name)
                    
                    # Attempt rollback on failure
                    if auto_rollback and not dry_run:
                        try:
                            rollback_service(service, revision, logger=logger)
                            results['rolled_back_services'].append(service_name)
                        except Exception as rollback_error:
                            logger.error(f"Rollback also failed for {service_name}: {rollback_error}")
    
    # Write updated compose file
    if not dry_run and results['updated_services']:
        write_compose(compose, logger=logger)
    
    logs.task_pass(f"Release deployment completed for {compose.name}")
    return results

def local_dev_reset(compose: DockerCompose, logger: Optional[logging.Logger] = None, dry_run: bool = False) -> None:
    logger = logger or _MODULE_LOGGER
    logs.task_start(f"Resetting local development environment: {compose.name}")
    
    if dry_run:
        logger.info(f"Dry-run: Would reset local dev environment for {compose.name}")
        return
    
    try:
        # Stop and remove containers
        compose_down(compose, remove_volumes=True, remove_images='local', logger=logger)
        
        # Prune system
        prune_orphans(dry_run=False, logger=logger)
        
        # Build fresh images
        compose_build(compose, nocache=True, logger=logger)
        
        # Start services
        compose_up(compose, build=False, pull=False, logger=logger)
        
        logs.task_pass(f"Local development environment reset for {compose.name}")
    except Exception as e:
        logs.task_fail(f"Failed to reset local dev environment: {e}")
        raise

def scheduled_image_retention_job(compose: DockerCompose, keep_per_image: int = 5, dry_run: bool = False, logger: Optional[logging.Logger] = None) -> Dict:
    logger = logger or _MODULE_LOGGER
    
    result = {
        'compose': compose.name,
        'keep_per_image': keep_per_image,
        'dry_run': dry_run,
        'cleanup_results': {}
    }
    
    try:
        cleanup_result = cleanup_old_images(compose, keep_count=keep_per_image, dry_run=dry_run, logger=logger)
        result['cleanup_results'] = cleanup_result
    except Exception as e:
        result['error'] = str(e)
        logger.error(f"Scheduled image retention job failed: {e}")
    
    return result

# L. High-Level Management
# L. High-Level Management
@dataclass
class DeploymentResult:
    """Enhanced result object with detailed deployment information"""
    success: bool
    duration: float
    updated_keys: List[str] = field(default_factory=list)
    services_healthy: int = 0
    services_total: int = 0
    backup_path: Optional[str] = None
    error: Optional[str] = None
    rollback_performed: bool = False
    deployment_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

def deploy(
    # Path configuration
    compose_file: str = 'docker-compose.yml',
    compose_dir: Optional[str] = None,
    env_new: str = '.env.new', 
    env_file: str = '.env', 
    backup_dir: str = 'deploy_backups', 
    log_file: str = 'logs/deploy.log',
    
    # Operation control
    pull: Optional[bool] = None,      # None=auto, True/False=force
    up: Optional[bool] = None,        # None=auto, True/False=force  
    health: Optional[bool] = None,    # None=auto, True/False=force
    dry_run: bool = False,
    verbose: bool = False,
    
    # Environment strategy
    env_update_keys: Optional[List[str]] = None,  # None=all keys, []=no keys
    env_merge_strategy: str = 'smart',  # 'smart', 'update', 'replace', 'preserve', 'safe'
    
    # Backup & cleanup
    backup_images: bool = True,
    backup_compress: bool = True,
    cleanup_backups: bool = True, 
    cleanup_images: bool = True,
    keep: int = 3,
    
    # Health & retry
    retry_count: int = 12,
    retry_sleep: int = 10,
    health_timeout: Optional[int] = None,
    fail_fast: bool = True,
    
    # Rollback
    rollback_strategy: str = 'smart',  # 'smart', 'auto', 'manual', 'none'
    max_rollback_attempts: int = 3,
    
    # Backward compatibility (deprecated but supported)
    no_pull: bool = False,
    no_up: bool = False,
    skip_health: bool = False,
    
    # Logging
    logger: Optional[logging.Logger] = None
) -> DeploymentResult:
    """
    Enhanced flexible deployment workflow with rollback capabilities.
    
    Steps:
    1. Validate inputs and resolve paths
    2. Create backup of current state
    3. Update environment file (flexible strategies)
    4. Pull new images (if not disabled)
    5. Bring up services (if not disabled)
    6. Health checks (if not disabled)
    7. Rollback on failure (flexible strategies)
    8. Clean up old backups/images
    
    Returns: DeploymentResult with detailed outcome information
    """
    import uuid
    start_time = dt_ops.current_datetime()
    logger = logger or _MODULE_LOGGER
    
    # Initialize result object
    result = DeploymentResult(
        success=False, 
        duration=0.0, 
        updated_keys=[],
        services_healthy=0,
        services_total=0
    )
    
    # Resolve all paths relative to compose_dir
    base_dir = Path(compose_dir) if compose_dir else Path.cwd()
    compose_file_path = base_dir / compose_file
    env_new_path = base_dir / env_new
    env_file_path = base_dir / env_file
    backup_dir_path = base_dir / backup_dir
    log_file_path = base_dir / log_file
    
    # Convert legacy flags to new flags
    if pull is None:
        pull = not no_pull
    if up is None:
        up = not no_up
    if health is None:
        health = not skip_health
    
    # Smart defaults
    if env_update_keys is None:
        env_update_keys = []  # Empty list means "all keys"
    
    if env_merge_strategy == 'smart':
        env_merge_strategy = 'update' if env_update_keys else 'replace'
    
    if rollback_strategy == 'smart':
        rollback_strategy = 'manual' if dry_run else 'auto'
    
    if health_timeout is None:
        health_timeout = retry_count * retry_sleep
    
    # Track deployment state for rollback
    deployment_state = {
        'backup_created': False,
        'env_updated': False,
        'images_pulled': False,
        'services_started': False,
        'backup_path': None,
        'compose_revision': None,
        'compose_file': str(compose_file_path),
        'env_file': str(env_file_path),
        'env_backup_path': None,
        'env_original_content': None,
        'env_updated_keys': [],
        'rollback_attempted': False
    }
    
    # Progress tracking
    steps = ["validate", "backup", "environment", "pull", "up", "health", "cleanup"]
    current_step = 0
    
    def _log_progress(step_name: str):
        nonlocal current_step
        current_step += 1
        logger.info(f"📦 [{current_step}/{len(steps)}] {step_name.title()}...")
    
    def _perform_rollback_with_retry(deployment_state: Dict[str, Any], max_attempts: int = 3) -> bool:
        """Perform rollback with retry logic"""
        deployment_state['rollback_attempted'] = True
        
        if rollback_strategy == 'none':
            logger.warning("Rollback disabled by configuration")
            return False
            
        for attempt in range(1, max_attempts + 1):
            try:
                logger.info(f"Rollback attempt {attempt}/{max_attempts}...")
                success = _perform_rollback(deployment_state)
                if success:
                    logger.info("Rollback completed successfully")
                    return True
                else:
                    logger.warning(f"Rollback attempt {attempt} failed")
                    if attempt < max_attempts:
                        dt_ops.sleep(5)  # Wait before retry
            except Exception as e:
                logger.error(f"Rollback attempt {attempt} failed with error: {e}")
                if attempt < max_attempts:
                    dt_ops.sleep(5)
        
        logger.error(f"All {max_attempts} rollback attempts failed")
        return False
    
    def _perform_rollback(deployment_state: Dict[str, Any]) -> bool:
        """Perform rollback to previous state"""
        try:
            rollback_actions = []
            
            # Rollback services if they were started
            if deployment_state.get('services_started') and rollback_strategy == 'auto':
                logger.info("Rolling back services...")
                try:
                    compose = read_compose(deployment_state['compose_file'], logger=logger)
                    compose_down(compose, logger=logger)
                    if deployment_state.get('compose_revision'):
                        rollback_compose(compose, deployment_state['compose_revision'], logger=logger)
                    rollback_actions.append("services")
                except Exception as e:
                    logger.error(f"Service rollback failed: {e}")
            
            # Rollback environment if it was updated
            if deployment_state.get('env_updated'):
                if deployment_state.get('env_backup_path'):
                    files.copy_file(deployment_state['env_backup_path'], deployment_state['env_file'])
                    rollback_actions.append("environment from backup")
                elif deployment_state.get('env_original_content') is not None:
                    files.write_file(deployment_state['env_file'], deployment_state['env_original_content'])
                    rollback_actions.append("environment from memory")
                else:
                    logger.warning("No environment backup available for rollback")
            
            # Restore from full backup if available
            if (deployment_state.get('backup_created') and 
                deployment_state.get('backup_path') and 
                rollback_strategy == 'auto'):
                try:
                    restored_compose = restore_compose(
                        deployment_state['backup_path'],
                        restore_dir=Path(deployment_state['compose_file']).parent,
                        load_images=True,
                        logger=logger
                    )
                    rollback_actions.append("full backup")
                except Exception as restore_error:
                    logger.error(f"Backup restoration failed: {restore_error}")
            
            logger.info(f"Rollback completed for: {rollback_actions}")
            return len(rollback_actions) > 0
            
        except Exception as rollback_error:
            logger.error(f"Rollback procedure failed: {rollback_error}")
            return False
    
    def _update_environment_file(env_new_path: Path, env_file_path: Path, strategy: str, keys: List[str]) -> Tuple[bool, List[str]]:
        """Update environment file and return (success, updated_keys)"""
        if not files.file_exists(env_new_path):
            logger.warning(f"New environment file not found: {env_new_path}")
            return False, []
        
        new_env = envs.load_env_file(env_new_path, as_dict=True)
        updated_keys = []
        
        if strategy == 'replace':
            if dry_run:
                logger.info(f"Dry-run: Would replace {env_file_path} with {env_new_path}")
                return True, list(new_env.keys())
            files.copy_file(env_new_path, env_file_path, backup=True)
            return True, list(new_env.keys())
            
        elif strategy == 'update':
            return _update_env_selective(env_file_path, new_env, keys, dry_run, logger)
            
        elif strategy == 'preserve':
            return _update_env_preserve(env_file_path, new_env, dry_run, logger)
            
        elif strategy == 'safe':
            return _update_env_safe(env_file_path, new_env, keys, dry_run, logger)
            
        elif strategy == 'smart':
            if not keys:
                return _update_env_replace(env_new_path, env_file_path, dry_run, logger)
            else:
                return _update_env_selective(env_file_path, new_env, keys, dry_run, logger)
            
        else:
            logger.error(f"Unknown environment strategy: {strategy}")
            return False, []
    
    def _update_env_replace(env_new_path: Path, env_file_path: Path, dry_run: bool, logger) -> Tuple[bool, List[str]]:
        """Replace entire environment file"""
        if dry_run:
            new_env = envs.load_env_file(env_new_path, as_dict=True)
            logger.info(f"Dry-run: Would replace {env_file_path} with {env_new_path}")
            return True, list(new_env.keys())
        files.copy_file(env_new_path, env_file_path, backup=True)
        new_env = envs.load_env_file(env_new_path, as_dict=True)
        return True, list(new_env.keys())
    
    def _update_env_selective(env_file_path: Path, new_env: Dict, keys: List[str], dry_run: bool, logger) -> Tuple[bool, List[str]]:
        """Update only specified keys"""
        if not files.file_exists(env_file_path):
            logger.warning(f"Environment file not found: {env_file_path}, creating new one")
            if dry_run:
                selected_keys = keys if keys else list(new_env.keys())
                logger.info(f"Dry-run: Would create {env_file_path} with keys: {selected_keys}")
                return True, selected_keys
            selected_env = {k: new_env[k] for k in (keys if keys else new_env.keys()) if k in new_env}
            envs.write_env_file(env_file_path, selected_env)
            return True, list(selected_env.keys())
        
        if dry_run:
            logger.info(f"Dry-run: Would update keys {keys if keys else 'all'} in {env_file_path}")
            return True, keys if keys else list(new_env.keys())
            
        current_env = envs.load_env_file(env_file_path, as_dict=True)
        updated_keys = []
        keys_to_update = keys if keys else new_env.keys()
        
        for key in keys_to_update:
            if key in new_env:
                if current_env.get(key) != new_env[key]:
                    current_env[key] = new_env[key]
                    updated_keys.append(key)
                    logger.debug(f"Updated {key} in environment")
            else:
                logger.warning(f"Key {key} not found in {env_new_path}")
        
        if updated_keys:
            envs.write_env_file(env_file_path, current_env)
        
        return bool(updated_keys), updated_keys
    
    def _update_env_preserve(env_file_path: Path, new_env: Dict, dry_run: bool, logger) -> Tuple[bool, List[str]]:
        """Merge, preserving existing values"""
        if dry_run:
            logger.info(f"Dry-run: Would merge new environment into {env_file_path}")
            return True, list(new_env.keys())
            
        if files.file_exists(env_file_path):
            current_env = envs.load_env_file(env_file_path, as_dict=True)
        else:
            current_env = {}
            
        updated_keys = [k for k in new_env.keys() if current_env.get(k) != new_env[k]]
        current_env.update(new_env)
        envs.write_env_file(env_file_path, current_env)
        
        return True, updated_keys
    
    def _update_env_safe(env_file_path: Path, new_env: Dict, keys: List[str], dry_run: bool, logger) -> Tuple[bool, List[str]]:
        """Only update keys that exist in both current and new environment"""
        if not files.file_exists(env_file_path):
            logger.warning(f"Environment file not found: {env_file_path}")
            return False, []
            
        current_env = envs.load_env_file(env_file_path, as_dict=True)
        updated_keys = []
        keys_to_update = keys if keys else [k for k in new_env.keys() if k in current_env]
        
        for key in keys_to_update:
            if key in current_env and key in new_env:
                if current_env[key] != new_env[key]:
                    if dry_run:
                        updated_keys.append(key)
                        logger.debug(f"Dry-run: Would update {key} (safe mode)")
                    else:
                        current_env[key] = new_env[key]
                        updated_keys.append(key)
                        logger.debug(f"Updated {key} (safe mode)")
            elif key not in current_env:
                logger.warning(f"Key {key} not in current environment, skipping (safe mode)")
            else:
                logger.warning(f"Key {key} not in new environment, skipping (safe mode)")
        
        if updated_keys and not dry_run:
            envs.write_env_file(env_file_path, current_env)
        
        return bool(updated_keys), updated_keys

    # Start deployment
    deployment_id = result.deployment_id
    logger.info(f"🚀 Starting deployment {deployment_id}")
    logger.info(f"   Compose: {compose_file_path}")
    logger.info(f"   Environment: {env_file_path} ← {env_new_path} ({env_merge_strategy})")
    logger.info(f"   Strategy: rollback={rollback_strategy}, health={health}, dry_run={dry_run}")
    logger.info(f"   Cleanup: keep={keep} versions, backup={backup_images}")
    
    try:
        # 1. Validate inputs
        _log_progress("validating inputs")
        if not files.file_exists(compose_file_path):
            raise DockerOpsError(f"Compose file not found: {compose_file_path}")
        
        if env_merge_strategy == 'replace' and files.file_exists(env_new_path):
            env_validation = envs.validate_env_file(env_new_path)
            if not env_validation.get('valid', True):
                raise DockerOpsError(f"Invalid environment file: {env_validation.get('errors')}")
        
        # 2. Load current compose and create backup
        compose = read_compose(str(compose_file_path), logger=logger)
        result.services_total = len(compose.services)
        deployment_state['compose_revision'] = create_compose_revision(
            compose, 
            description=f"Pre-deployment backup {deployment_id}",
            logger=logger
        )
        
        # 3. Create backup
        _log_progress("creating backup")
        if backup_images or backup_compress:
            backup_path = backup_compose(
                compose, 
                backup_dir=str(backup_dir_path),
                include_images=backup_images,
                compress=backup_compress,
                dry_run=dry_run,
                logger=logger
            )
            deployment_state['backup_created'] = True
            deployment_state['backup_path'] = backup_path
            result.backup_path = backup_path
        
        # 4. Update environment
        _log_progress("updating environment")
        if env_new_path.exists():
            # Backup current environment for rollback
            if env_file_path.exists():
                deployment_state['env_original_content'] = files.read_file(env_file_path)
                deployment_state['env_backup_path'] = files.backup_file(env_file_path)
            
            # Perform environment update
            env_updated, updated_keys = _update_environment_file(
                env_new_path, 
                env_file_path, 
                env_merge_strategy, 
                env_update_keys
            )
            
            if env_updated:
                deployment_state['env_updated'] = True
                deployment_state['env_updated_keys'] = updated_keys
                result.updated_keys = updated_keys
                envs.load_env_file(env_file_path)  # Reload environment
                
                if dry_run:
                    logger.info(f"Dry-run: Environment update completed (strategy: {env_merge_strategy}, keys: {updated_keys})")
                else:
                    logger.info(f"Environment update completed (strategy: {env_merge_strategy}, updated {len(updated_keys)} keys)")
        
        # 5. Pull images
        if pull and not dry_run:
            _log_progress("pulling images")
            logger.info("Pulling new images...")
            pull_results = compose_pull(
                compose, 
                parallel=DEFAULT_CONCURRENCY_LIMIT,
                logger=logger
            )
            deployment_state['images_pulled'] = True
            
            failed_pulls = [svc for svc, img in pull_results.items() if not img]
            if failed_pulls:
                logger.warning(f"Failed to pull images for services: {failed_pulls}")
        
        # 6. Start services
        if up:
            _log_progress("starting services")
            logger.info("Starting services...")
            up_result = compose_up(
                compose,
                build=False,
                pull=False,
                detach=True,
                dry_run=dry_run,
                logger=logger
            )
            deployment_state['services_started'] = True
            
            if dry_run:
                logger.info("Dry-run: Deployment would proceed")
                result.success = True
                result.duration = (dt_ops.current_datetime() - start_time).total_seconds()
                return result
        
        # 7. Health checks
        if health and not dry_run:
            _log_progress("checking health")
            logger.info("Performing health checks...")
            healthy = wait_compose_healthy(
                compose,
                timeout=health_timeout,
                logger=logger
            )
            
            if not healthy:
                raise HealthCheckFailed(f"Services failed health checks after {health_timeout}s")
            
            result.services_healthy = result.services_total
        
        # 8. Cleanup
        _log_progress("cleaning up")
        if not dry_run:
            if cleanup_backups:
                _cleanup_old_backups(str(backup_dir_path), keep=keep, logger=logger)
            
            if cleanup_images:
                cleanup_old_images(compose, keep_count=keep, dry_run=dry_run, logger=logger)
        
        # Success
        result.success = True
        result.duration = (dt_ops.current_datetime() - start_time).total_seconds()
        
        # Success summary
        logger.info(f"🎉 Deployment {deployment_id} completed successfully in {result.duration:.1f}s")
        logger.info(f"   Updated: {len(result.updated_keys)} environment keys")
        logger.info(f"   Services: {result.services_healthy}/{result.services_total} services healthy")
        if result.backup_path:
            logger.info(f"   Backup: {Path(result.backup_path).name}")
        
        logs.task_pass(f"Deployment {deployment_id} completed")
        return result
        
    except Exception as e:
        # Failure handling
        result.success = False
        result.duration = (dt_ops.current_datetime() - start_time).total_seconds()
        result.error = str(e)
        
        logs.task_fail(f"Deployment {deployment_id} failed at step {current_step+1}/{len(steps)}: {steps[current_step]}")
        logger.error(f"💥 Deployment {deployment_id} failed: {e}")
        
        # Enhanced error reporting
        if verbose:
            logger.error(f"Error details: {type(e).__name__}: {e}")
            import traceback
            logger.debug(f"Traceback: {traceback.format_exc()}")
        
        # Categorized error messages
        if isinstance(e, DockerOpsError):
            logger.error("Docker operation failed - check Docker daemon and permissions")
        elif isinstance(e, HealthCheckFailed):
            logger.error("Services failed health checks - check service logs")
        elif isinstance(e, FileNotFoundError):
            logger.error("Required file not found - verify paths and permissions")
        else:
            logger.error("Unexpected error occurred")
        
        # Rollback
        if not dry_run and rollback_strategy != 'none':
            logger.info("Initiating rollback...")
            rollback_success = _perform_rollback_with_retry(
                deployment_state, 
                max_attempts=max_rollback_attempts
            )
            result.rollback_performed = rollback_success
            
            if not rollback_success:
                logger.error("💥 Rollback failed! Manual intervention required!")
        
        return result

def _cleanup_old_backups(backup_dir: str, keep: int, logger: logging.Logger):
    """Cleanup old backup files, keeping only the most recent ones"""
    try:
        import glob
        backup_files = sorted(glob.glob(f"{backup_dir}/*.tar*"), key=os.path.getmtime, reverse=True)
        for old_backup in backup_files[keep:]:
            os.remove(old_backup)
            logger.info(f"Removed old backup: {Path(old_backup).name}")
    except Exception as e:
        logger.warning(f"Failed to cleanup old backups: {e}")

def _cleanup_old_backups(backup_dir: str, keep: int, logger: logging.Logger):
    """Cleanup old backup files, keeping only the most recent ones"""
    try:
        import glob
        backup_files = sorted(glob.glob(f"{backup_dir}/*.tar*"), key=os.path.getmtime, reverse=True)
        for old_backup in backup_files[keep:]:
            os.remove(old_backup)
            logger.info(f"Removed old backup: {Path(old_backup).name}")
    except Exception as e:
        logger.warning(f"Failed to cleanup old backups: {e}")

# Low-level image operations
@retry(stop=stop_after_attempt(DEFAULT_PULL_RETRIES), wait=wait_exponential(multiplier=1, min=4, max=10))
def pull_image(name: str, tag: str = 'latest', auth: Optional[Dict] = None, retries: int = 3, dry_run: bool = False, logger: Optional[logging.Logger] = None) -> DockerImage:
    logger = logger or _MODULE_LOGGER
    full_name = _normalize_image_name(name, tag)
    
    if dry_run:
        logger.info(f"Dry-run: Would pull image {full_name}")
        return DockerImage(name=name, tag=tag)
    
    client = _get_docker_client(logger=logger)
    if client:
        try:
            image = client.images.pull(full_name, auth_config=auth)
            return DockerImage(
                name=name,
                tag=tag,
                digest=image.id,
                size=image.attrs['Size'],
                created=dt_ops.timestamp_to_datetime(image.attrs['Created']),
                labels=image.labels
            )
        except DockerException as e:
            logger.error(f"SDK pull failed: {e}")
    
    # Fallback to CLI
    cmd = ["docker", "pull", full_name]
    _run_cli(cmd, logger=logger)
    
    # Inspect to get image details
    inspect_data = _inspect_image(full_name, logger=logger)
    return DockerImage(
        name=name,
        tag=tag,
        digest=inspect_data.get('Id', ''),
        size=inspect_data.get('Size', 0),
        created=dt_ops.timestamp_to_datetime(inspect_data.get('Created', 0)),
        labels=inspect_data.get('Config', {}).get('Labels', {})
    )

@retry(stop=stop_after_attempt(DEFAULT_PULL_RETRIES), wait=wait_exponential(multiplier=1, min=4, max=10))
def push_image(name: str, tag: str = 'latest', auth: Optional[Dict] = None, retries: int = 3, dry_run: bool = False, logger: Optional[logging.Logger] = None) -> None:
    logger = logger or _MODULE_LOGGER
    full_name = _normalize_image_name(name, tag)
    
    if dry_run:
        logger.info(f"Dry-run: Would push image {full_name}")
        return
    
    client = _get_docker_client(logger=logger)
    if client:
        try:
            client.images.push(full_name, auth_config=auth)
            return
        except DockerException as e:
            logger.error(f"SDK push failed: {e}")
    
    # Fallback to CLI
    cmd = ["docker", "push", full_name]
    _run_cli(cmd, logger=logger)

def save_image(name: str, tag: str = 'latest', path: str = None, compress: bool = True, logger: Optional[logging.Logger] = None) -> str:
    logger = logger or _MODULE_LOGGER
    full_name = _normalize_image_name(name, tag)
    
    if not path:
        path = f"./{name.replace('/', '_')}_{tag}.tar"
        if compress:
            path += ".gz"
    
    client = _get_docker_client(logger=logger)
    if client:
        try:
            image = client.images.get(full_name)
            with open(path, 'wb') as f:
                for chunk in image.save(named=True):
                    f.write(chunk)
            return path
        except DockerException as e:
            logger.error(f"SDK save failed: {e}")
    
    # Fallback to CLI
    cmd = ["docker", "save", "-o", path, full_name]
    _run_cli(cmd, logger=logger)
    return path

def load_image(path: str, logger: Optional[logging.Logger] = None, dry_run: bool = False) -> DockerImage:
    logger = logger or _MODULE_LOGGER
    
    if dry_run:
        logger.info(f"Dry-run: Would load image from {path}")
        return DockerImage(name="loaded", tag="image")
    
    if not files.file_exists(path):
        raise DockerOpsError(f"Image file not found: {path}")
    
    client = _get_docker_client(logger=logger)
    if client:
        try:
            with open(path, 'rb') as f:
                image = client.images.load(f)
            if image:
                img = image[0]
                tags = img.tags[0] if img.tags else 'loaded:latest'
                name, tag = tags.split(':') if ':' in tags else (tags, 'latest')
                return DockerImage(
                    name=name,
                    tag=tag,
                    digest=img.id,
                    size=img.attrs['Size'],
                    created=dt_ops.timestamp_to_datetime(img.attrs['Created']),
                    labels=img.labels
                )
        except DockerException as e:
            logger.error(f"SDK load failed: {e}")
    
    # Fallback to CLI
    cmd = ["docker", "load", "-i", path]
    result = _run_cli(cmd, logger=logger)
    
    # Parse output to get loaded image name
    # This is a simplified parsing - you might need to adjust based on your docker version
    lines = result.stdout.splitlines()
    for line in lines:
        if 'Loaded image:' in line:
            loaded_image = line.split('Loaded image:')[-1].strip()
            name, tag = loaded_image.split(':') if ':' in loaded_image else (loaded_image, 'latest')
            return DockerImage(name=name, tag=tag)
    
    return DockerImage(name="unknown", tag="loaded")

def tag_image(name: str, tag: str = 'latest', new_tag: str = None, force: bool = False, logger: Optional[logging.Logger] = None) -> DockerImage:
    logger = logger or _MODULE_LOGGER
    
    if not new_tag:
        raise DockerOpsError("new_tag is required")
    
    source_name = _normalize_image_name(name, tag)
    target_name = _normalize_image_name(name, new_tag)
    
    client = _get_docker_client(logger=logger)
    if client:
        try:
            image = client.images.get(source_name)
            image.tag(target_name, force=force)
            return DockerImage(name=name, tag=new_tag, digest=image.id)
        except DockerException as e:
            logger.error(f"SDK tag failed: {e}")
    
    # Fallback to CLI
    cmd = ["docker", "tag", source_name, target_name]
    _run_cli(cmd, logger=logger)
    
    return DockerImage(name=name, tag=new_tag)

def remove_image(name: str, tag: str = 'latest', force: bool = False, logger: Optional[logging.Logger] = None) -> None:
    logger = logger or _MODULE_LOGGER
    full_name = _normalize_image_name(name, tag)
    
    client = _get_docker_client(logger=logger)
    if client:
        try:
            client.images.remove(full_name, force=force)
            return
        except DockerException as e:
            logger.error(f"SDK remove failed: {e}")
    
    # Fallback to CLI
    cmd = ["docker", "rmi", full_name]
    if force:
        cmd.append("-f")
    _run_cli(cmd, logger=logger)

def build_image(context: str, dockerfile: str = 'Dockerfile', tag: str = None, nocache: bool = False, pull: bool = False, build_args: Optional[Dict] = None, timeout: int = 3600, logger: Optional[logging.Logger] = None) -> DockerImage:
    logger = logger or _MODULE_LOGGER
    
    if not tag:
        tag = f"{Path(context).name}:latest"
    
    client = _get_docker_client(logger=logger)
    if client:
        try:
            image, logs = client.images.build(
                path=context,
                dockerfile=dockerfile,
                tag=tag,
                nocache=nocache,
                pull=pull,
                buildargs=build_args,
                timeout=timeout
            )
            
            return DockerImage(
                name=tag.split(':')[0],
                tag=tag.split(':')[1] if ':' in tag else 'latest',
                digest=image.id,
                size=image.attrs['Size'],
                created=dt_ops.timestamp_to_datetime(image.attrs['Created']),
                labels=image.labels
            )
        except DockerException as e:
            logger.error(f"SDK build failed: {e}")
    
    # Fallback to CLI
    cmd = ["docker", "build", "-t", tag, "-f", dockerfile, context]
    if nocache:
        cmd.append("--no-cache")
    if pull:
        cmd.append("--pull")
    if build_args:
        for key, value in build_args.items():
            cmd.extend(["--build-arg", f"{key}={value}"])
    
    _run_cli(cmd, timeout=timeout, logger=logger)
    
    # Inspect to get image details
    inspect_data = _inspect_image(tag, logger=logger)
    return DockerImage(
        name=tag.split(':')[0],
        tag=tag.split(':')[1] if ':' in tag else 'latest',
        digest=inspect_data.get('Id', ''),
        size=inspect_data.get('Size', 0),
        created=dt_ops.timestamp_to_datetime(inspect_data.get('Created', 0)),
        labels=inspect_data.get('Config', {}).get('Labels', {})
    )

def run_container(image: str, name: Optional[str] = None, detach: bool = True, ports: Optional[Dict] = None, volumes: Optional[List] = None, env: Optional[Dict] = None, logger: Optional[logging.Logger] = None) -> DockerContainer:
    logger = logger or _MODULE_LOGGER
    
    client = _get_docker_client(logger=logger)
    if client:
        try:
            container = client.containers.run(
                image,
                name=name,
                detach=detach,
                ports=ports,
                volumes=volumes,
                environment=env
            )
            
            return DockerContainer(
                id=container.id,
                name=container.name,
                image=image,
                status=container.status
            )
        except DockerException as e:
            logger.error(f"SDK run failed: {e}")
    
    # Fallback to CLI
    cmd = ["docker", "run"]
    if detach:
        cmd.append("-d")
    if name:
        cmd.extend(["--name", name])
    if ports:
        for host_port, container_port in ports.items():
            cmd.extend(["-p", f"{host_port}:{container_port}"])
    if volumes:
        for volume in volumes:
            cmd.extend(["-v", volume])
    if env:
        for key, value in env.items():
            cmd.extend(["-e", f"{key}={value}"])
    cmd.append(image)
    
    result = _run_cli(cmd, logger=logger)
    
    # Get container ID from output
    container_id = result.stdout.strip()
    
    # Inspect to get container details
    inspect_data = _inspect_container(container_id, logger=logger)
    return DockerContainer(
        id=container_id,
        name=inspect_data.get('Name', '').lstrip('/'),
        image=image,
        status=inspect_data.get('State', {}).get('Status', ''),
        started_at=inspect_data.get('State', {}).get('StartedAt', ''),
        ports=inspect_data.get('NetworkSettings', {}).get('Ports', {}),
        inspect=inspect_data
    )

def start_container(container_id: str, logger: Optional[logging.Logger] = None) -> None:
    logger = logger or _MODULE_LOGGER
    
    client = _get_docker_client(logger=logger)
    if client:
        try:
            container = client.containers.get(container_id)
            container.start()
            return
        except DockerException as e:
            logger.error(f"SDK start failed: {e}")
    
    # Fallback to CLI
    cmd = ["docker", "start", container_id]
    _run_cli(cmd, logger=logger)

def stop_container(container_id: str, timeout: int = 10, logger: Optional[logging.Logger] = None) -> None:
    logger = logger or _MODULE_LOGGER
    
    client = _get_docker_client(logger=logger)
    if client:
        try:
            container = client.containers.get(container_id)
            container.stop(timeout=timeout)
            return
        except DockerException as e:
            logger.error(f"SDK stop failed: {e}")
    
    # Fallback to CLI
    cmd = ["docker", "stop", "-t", str(timeout), container_id]
    _run_cli(cmd, logger=logger)

def restart_container(container_id: str, timeout: int = 10, logger: Optional[logging.Logger] = None) -> None:
    logger = logger or _MODULE_LOGGER
    
    client = _get_docker_client(logger=logger)
    if client:
        try:
            container = client.containers.get(container_id)
            container.restart(timeout=timeout)
            return
        except DockerException as e:
            logger.error(f"SDK restart failed: {e}")
    
    # Fallback to CLI
    cmd = ["docker", "restart", "-t", str(timeout), container_id]
    _run_cli(cmd, logger=logger)

def kill_container(container_id: str, signal: str = 'SIGKILL', logger: Optional[logging.Logger] = None) -> None:
    logger = logger or _MODULE_LOGGER
    
    client = _get_docker_client(logger=logger)
    if client:
        try:
            container = client.containers.get(container_id)
            container.kill(signal=signal)
            return
        except DockerException as e:
            logger.error(f"SDK kill failed: {e}")
    
    # Fallback to CLI
    cmd = ["docker", "kill", "-s", signal, container_id]
    _run_cli(cmd, logger=logger)

def container_logs(container_id: str, follow: bool = False, tail: Optional[Union[str, int]] = 'all', since: Optional[int] = None, logger: Optional[logging.Logger] = None) -> Iterator[LogLine]:
    logger = logger or _MODULE_LOGGER
    
    client = _get_docker_client(logger=logger)
    if client:
        try:
            container = client.containers.get(container_id)
            logs = container.logs(
                follow=follow,
                tail=tail,
                since=since,
                stream=follow,
                timestamps=True
            )
            
            if follow:
                for line in logs:
                    yield _parse_container_log_line(line.decode('utf-8'))
            else:
                for line in logs.decode('utf-8').splitlines():
                    yield _parse_container_log_line(line)
            return
        except DockerException as e:
            logger.error(f"SDK logs failed: {e}")
    
    # Fallback to CLI
    cmd = ["docker", "logs"]
    if follow:
        cmd.append("-f")
    if tail:
        cmd.extend(["--tail", str(tail)])
    if since:
        cmd.extend(["--since", str(since)])
    cmd.append(container_id)
    
    result = _run_cli(cmd, capture=not follow, logger=logger)
    
    if not follow:
        for line in result.stdout.splitlines():
            yield _parse_container_log_line(line)
    else:
        # For follow mode with CLI, we'd need proper streaming
        logger.warning("Follow mode for container logs with CLI is not fully implemented")

def _parse_container_log_line(line: str) -> LogLine:
    """Parse a container log line into LogLine object"""
    # Docker log format: timestamp stream message
    # Example: "2023-01-01T12:00:00.000000000Z stdout message content"
    parts = line.split(' ', 2)
    if len(parts) >= 3:
        timestamp = parts[0]
        stream = parts[1]
        message = parts[2]
        return LogLine(timestamp=timestamp, message=f"[{stream}] {message}")
    else:
        return LogLine(message=line)

def exec_command(container_id: str, cmd: List[str], user: Optional[str] = None, stream: bool = False, tty: bool = False, logger: Optional[logging.Logger] = None) -> ExecResult:
    logger = logger or _MODULE_LOGGER
    
    client = _get_docker_client(logger=logger)
    if client:
        try:
            container = client.containers.get(container_id)
            result = container.exec_run(
                cmd,
                user=user,
                stream=stream,
                tty=tty
            )
            
            if stream:
                # For stream=True, we'd need to handle the generator
                stdout = ""
                for output in result.output:
                    stdout += output.decode('utf-8') if isinstance(output, bytes) else str(output)
                return ExecResult(rc=result.exit_code, stdout=stdout, stderr="")
            else:
                output = result.output
                if isinstance(output, bytes):
                    output = output.decode('utf-8')
                return ExecResult(rc=result.exit_code, stdout=output, stderr="")
        except DockerException as e:
            logger.error(f"SDK exec failed: {e}")
    
    # Fallback to CLI
    full_cmd = ["docker", "exec"]
    if user:
        full_cmd.extend(["-u", user])
    if tty:
        full_cmd.append("-t")
    full_cmd.append(container_id)
    full_cmd.extend(cmd)
    
    try:
        result = _run_cli(full_cmd, logger=logger)
        return ExecResult(rc=result.returncode, stdout=result.stdout, stderr=result.stderr)
    except DockerOpsError as e:
        # _run_cli raises exception on non-zero return code, but we want to capture it
        if hasattr(e, '__cause__') and hasattr(e.__cause__, 'returncode'):
            proc = e.__cause__
            return ExecResult(rc=proc.returncode, stdout=proc.stdout, stderr=proc.stderr)
        else:
            return ExecResult(rc=1, stdout="", stderr=str(e))

def commit_container(container_id: str, tag: str, message: Optional[str] = None, logger: Optional[logging.Logger] = None) -> DockerImage:
    logger = logger or _MODULE_LOGGER
    
    client = _get_docker_client(logger=logger)
    if client:
        try:
            container = client.containers.get(container_id)
            image = container.commit(repository=tag, message=message)
            return DockerImage(
                name=tag.split(':')[0],
                tag=tag.split(':')[1] if ':' in tag else 'latest',
                digest=image.id,
                labels=image.labels
            )
        except DockerException as e:
            logger.error(f"SDK commit failed: {e}")
    
    # Fallback to CLI
    cmd = ["docker", "commit"]
    if message:
        cmd.extend(["-m", message])
    cmd.extend([container_id, tag])
    
    _run_cli(cmd, logger=logger)
    
    # Inspect to get image details
    inspect_data = _inspect_image(tag, logger=logger)
    return DockerImage(
        name=tag.split(':')[0],
        tag=tag.split(':')[1] if ':' in tag else 'latest',
        digest=inspect_data.get('Id', ''),
        labels=inspect_data.get('Config', {}).get('Labels', {})
    )

def attach_container(container_id: str, logs: bool = False, stream: bool = True, logger: Optional[logging.Logger] = None) -> None:
    logger = logger or _MODULE_LOGGER
    
    client = _get_docker_client(logger=logger)
    if client:
        try:
            container = client.containers.get(container_id)
            # Note: attach is complex and might block
            # This is a simplified implementation
            for line in container.attach(logs=logs, stream=stream):
                print(line.decode('utf-8') if isinstance(line, bytes) else line)
            return
        except DockerException as e:
            logger.error(f"SDK attach failed: {e}")
    
    # Fallback to CLI
    cmd = ["docker", "attach"]
    if logs:
        cmd.append("--no-stdin")
    cmd.append(container_id)
    
    # Note: This will block and attach to the container
    _run_cli(cmd, capture=False, logger=logger)

def remove_container(container_id: str, force: bool = False, remove_volumes: bool = False, logger: Optional[logging.Logger] = None) -> None:
    logger = logger or _MODULE_LOGGER
    
    client = _get_docker_client(logger=logger)
    if client:
        try:
            container = client.containers.get(container_id)
            container.remove(force=force, v=remove_volumes)
            return
        except DockerException as e:
            logger.error(f"SDK remove failed: {e}")
    
    # Fallback to CLI
    cmd = ["docker", "rm"]
    if force:
        cmd.append("-f")
    if remove_volumes:
        cmd.append("-v")
    cmd.append(container_id)
    
    _run_cli(cmd, logger=logger)

# CLI wrapper (optional)
try:
    import typer
except ImportError:
    typer = None

if typer:
    app = typer.Typer(name="docker_ops")

    @app.command()
    def compose_up(file: str):
        compose = read_compose(file)
        compose.up()

    # Add other commands

if __name__ == "__main__":
    if typer:
        app()
    else:
        print("Typer not available for CLI")

# __all__ and help()
__all__ = [
    "DockerOpsError", "ComposeConflictError", "HealthCheckFailed", "RollbackFailed", "ImageRetentionError",
    "BuildSpec", "PortBinding", "VolumeMount", "HealthCheckSpec", "NetworkSpec", "VolumeSpec",
    "ServiceRevision", "DockerComposeRevision", "ExecResult", "LogLine", "DockerImage", "DockerContainer",
    "ComposeService", "DockerCompose", "read_compose", "write_compose", "sync_compose", "compose_preview_changes",
    "backup_compose", "restore_compose", "add_service", "add_services", "read_service", "read_services",
    "remove_service", "remove_services", "update_service", "update_services", "docker_compose_down_conflict",
    "find_conflicting_containers_for_compose", "compose_up", "compose_down", "compose_restart", "compose_ps",
    "compose_logs", "compose_config", "compose_pull", "compose_build", "service_up", "service_down",
    "service_restart", "service_logs", "service_pull", "service_push", "service_build", "service_exec",
    "service_commit", "service_attach", "service_kill", "service_inspect", "service_is_running",
    "service_health_check", "wait_service_healthy", "compose_health_check", "wait_compose_healthy",
    "wait_for_log_pattern", "create_service_revision", "rollback_service", "create_compose_revision",
    "rollback_compose", "auto_rollback_on_health_failure", "keep_image_versions", "keep_image_versions_by_name",
    "cleanup_old_images", "prune_orphans", "prune_images", "prune_volumes", "prune_networks",
    "bulk_services_up", "bulk_services_down", "bulk_services_restart", "update_multiple_services",
    "validate_compose", "validate_service", "compare_services", "service_to_dict", "dict_to_service",
    "get_service_images", "pull_service_images", "push_service_images", "save_service_image",
    "load_service_image", "tag_service_image", "retag_rotate_image", "deploy_compose_release",
    "local_dev_reset", "scheduled_image_retention_job", "deploy", "pull_image", "push_image",
    "save_image", "load_image", "tag_image", "remove_image", "build_image", "run_container",
    "start_container", "stop_container", "restart_container", "kill_container", "container_logs",
    "exec_command", "commit_container", "attach_container", "remove_container", "help"
]

def help() -> None:
    """
    docker_ops — High-Level Docker Compose Helpers

    Overview:
    This module provides utilities for managing Docker and Docker Compose in DevOps scripts.
    It uses dataclasses for Compose structures, low-level SDK/CLI wrappers, and middle-level functions for common ops.
    Dependencies: docker-py (optional for SDK), ruamel-yaml (for YAML preservation), tenacity (for retries).
    Falls back to CLI if SDK unavailable. Integrates with utils_devops.core (logs, files, etc.).

    Usage Tips:
    - Start by loading a compose: compose = read_compose('docker-compose.yml')
    - Modify: add_service(compose, ComposeService(name='web', image='nginx'))
    - Apply: sync_compose(compose) or compose.up()
    - Health/Rollback: Use health checks and revisions for safe deploys.
    - Parallel: Many functions support concurrency for bulk ops.
    - Dry-run: Most functions have dry_run param to preview actions.
    - Logging: Pass logger or use module's; integrates with logs module.
    - Errors: Catch DockerOpsError and subclasses.

    For complete function documentation, see the individual function docstrings.
    """
    print(help.__doc__)