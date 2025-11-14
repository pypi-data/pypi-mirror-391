"""Client and persistence helpers for Trainy Auth integration."""

from __future__ import annotations

import base64
import binascii
import copy
import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

import requests
import yaml

from konduktor import config as konduktor_config
from konduktor import logging

logger = logging.get_logger(__name__)

DEFAULT_ENDPOINT = 'https://dex.trainy.ai:5555'
DEFAULT_SESSION_FILE = Path.home() / '.konduktor' / 'auth' / 'session.json'
DEFAULT_KUBECONFIG = Path.home() / '.kube' / 'config'


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_datetime(raw: Optional[str]) -> Optional[datetime]:
    if not raw:
        return None
    try:
        cleaned = raw.replace('Z', '+00:00')
        return datetime.fromisoformat(cleaned)
    except ValueError:
        logger.debug('Failed to parse timestamp %s', raw)
        return None


def _normalize_endpoint(value: str) -> str:
    trimmed = value.strip()
    if not trimmed:
        raise ValueError('Empty Trainy Auth endpoint')
    if '://' not in trimmed:
        trimmed = f'https://{trimmed}'
    return trimmed.rstrip('/')


def _load_endpoint(explicit: Optional[str]) -> str:
    if explicit:
        return _normalize_endpoint(explicit)

    env_value = os.getenv('TRAINY_AUTH_ENDPOINT')
    if env_value:
        return _normalize_endpoint(env_value)

    config_value = konduktor_config.get_nested(('auth', 'endpoint'), None)
    if config_value:
        return _normalize_endpoint(str(config_value))

    return DEFAULT_ENDPOINT


def _load_verify(explicit: Optional[bool | str]) -> bool | str:
    if explicit is not None:
        return explicit

    env_bundle = os.getenv('TRAINY_AUTH_CA_BUNDLE')
    if env_bundle:
        return os.path.expanduser(env_bundle)

    env_verify = os.getenv('TRAINY_AUTH_VERIFY_SSL')
    if env_verify is not None:
        return env_verify.strip().lower() not in {'0', 'false', 'no'}

    config_bundle = konduktor_config.get_nested(('auth', 'ca_bundle'), None)
    if config_bundle:
        return os.path.expanduser(str(config_bundle))

    config_verify = konduktor_config.get_nested(('auth', 'verify_ssl'), None)
    if config_verify is not None:
        if isinstance(config_verify, bool):
            return config_verify
        return str(config_verify).strip().lower() not in {'0', 'false', 'no'}

    return True


def _resolve_session_file(explicit: Optional[Path | str]) -> Path:
    if explicit:
        return Path(explicit).expanduser()
    env_value = os.getenv('KONDUKTOR_AUTH_SESSION_FILE')
    if env_value:
        return Path(env_value).expanduser()
    config_value = konduktor_config.get_nested(('auth', 'session_file'), None)
    if config_value:
        return Path(str(config_value)).expanduser()
    return DEFAULT_SESSION_FILE


class AuthServiceError(RuntimeError):
    """Raised for errors while talking to the Trainy Auth service."""


@dataclass(frozen=True)
class AuthUser:
    subject: str
    email: Optional[str] = None
    name: Optional[str] = None


@dataclass(frozen=True)
class DeviceStart:
    session_id: str
    user_code: str
    verification_uri: str
    verification_uri_complete: Optional[str]
    expires_in: int
    interval: int


@dataclass(frozen=True)
class DevicePollStatus:
    status: str
    session_token: Optional[str]
    detail: Optional[str]
    user: Optional[AuthUser]
    expires_at: Optional[datetime]


@dataclass(frozen=True)
class AuthState:
    token: str
    user: AuthUser
    expires_at: datetime

    def is_expired(self) -> bool:
        return _now() >= self.expires_at


@dataclass(frozen=True)
class ClusterInfo:
    name: str
    teleport_cluster: str
    description: Optional[str] = None


@dataclass(frozen=True)
class ClusterCredential:
    kubeconfig: str
    filename: str
    expires_at: datetime


class AuthStore:
    """Persists the opaque session token issued by the Trainy Auth service."""

    def __init__(self, path: Optional[Path | str] = None) -> None:
        self._path = _resolve_session_file(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> Optional[AuthState]:
        try:
            contents = self._path.read_text(encoding='utf-8')
        except FileNotFoundError:
            return None
        except OSError as exc:
            logger.warning('Failed to read auth session: %s', exc)
            return None
        try:
            payload = json.loads(contents)
        except json.JSONDecodeError:
            logger.warning('Auth session file %s is corrupt; ignoring', self._path)
            return None
        expires_at = _parse_datetime(payload.get('expires_at'))
        if not expires_at:
            return None
        user_payload = payload.get('user') or {}
        try:
            user = AuthUser(
                subject=user_payload['subject'],
                email=user_payload.get('email'),
                name=user_payload.get('name'),
            )
        except KeyError:
            return None
        state = AuthState(
            token=payload.get('token', ''),
            user=user,
            expires_at=expires_at,
        )
        if not state.token or state.is_expired():
            return None
        return state

    def save(self, state: AuthState) -> None:
        payload = {
            'token': state.token,
            'expires_at': state.expires_at.isoformat(),
            'user': asdict(state.user),
        }
        tmp_path = self._path.with_suffix('.tmp')
        tmp_path.write_text(json.dumps(payload, indent=2), encoding='utf-8')
        os.replace(tmp_path, self._path)

    def clear(self) -> None:
        try:
            self._path.unlink()
        except FileNotFoundError:
            return
        except OSError as exc:
            logger.debug('Unable to remove auth session file: %s', exc)


class AuthService:
    """Thin HTTP client for the Trainy Auth FastAPI service."""

    def __init__(
        self,
        *,
        base_url: Optional[str] = None,
        verify_ssl: Optional[bool | str] = None,
        timeout: float = 15.0,
        session: Optional[requests.Session] = None,
    ) -> None:
        self._base_url = _load_endpoint(base_url)
        self._verify = _load_verify(verify_ssl)
        self._timeout = timeout
        self._session = session or requests.Session()

    @property
    def base_url(self) -> str:
        return self._base_url

    def start_device_authorization(self) -> DeviceStart:
        response = self._request('POST', '/v1/device/start')
        payload = response.json()
        return DeviceStart(
            session_id=payload['session_id'],
            user_code=payload['user_code'],
            verification_uri=payload['verification_uri'],
            verification_uri_complete=payload.get('verification_uri_complete'),
            expires_in=int(payload['expires_in']),
            interval=int(payload['interval']),
        )

    def poll_device_session(self, session_id: str) -> DevicePollStatus:
        response = self._request('POST', '/v1/device/poll', json={'session_id': session_id})
        payload = response.json()
        user_payload = payload.get('user')
        user = None
        if user_payload:
            user = AuthUser(
                subject=user_payload.get('subject', ''),
                email=user_payload.get('email'),
                name=user_payload.get('name'),
            )
        expires_at = _parse_datetime(payload.get('expires_at'))
        return DevicePollStatus(
            status=payload['status'],
            session_token=payload.get('session_token'),
            detail=payload.get('detail'),
            user=user,
            expires_at=expires_at,
        )

    def list_clusters(self, token: str) -> List[ClusterInfo]:
        response = self._request(
            'GET',
            '/v1/clusters',
            headers=self._auth_header(token),
        )
        payload = response.json()
        clusters: List[ClusterInfo] = []
        for entry in payload:
            clusters.append(
                ClusterInfo(
                    name=entry['name'],
                    teleport_cluster=entry.get('teleport_cluster', entry['name']),
                    description=entry.get('description'),
                )
            )
        return clusters

    def issue_kubeconfig(
        self,
        token: str,
        cluster_name: str,
        *,
        ttl: Optional[str] = None,
    ) -> ClusterCredential:
        kwargs: Dict[str, Any] = {'headers': self._auth_header(token)}
        if ttl:
            kwargs['json'] = {'ttl': ttl}
        response = self._request(
            'POST',
            f'/v1/clusters/{cluster_name}/credential',
            **kwargs,
        )
        payload = response.json()
        encoded = payload['kubeconfig']
        try:
            decoded = base64.b64decode(encoded).decode('utf-8')
        except (binascii.Error, UnicodeDecodeError) as exc:
            raise AuthServiceError('Received invalid kubeconfig payload from server') from exc
        expires_at = _parse_datetime(payload.get('expires_at')) or _now()
        return ClusterCredential(
            kubeconfig=decoded,
            filename=payload.get('filename', f'{cluster_name}-kubeconfig.yaml'),
            expires_at=expires_at,
        )

    def _auth_header(self, token: str) -> Dict[str, str]:
        return {'Authorization': f'Bearer {token}'}

    def _request(self, method: str, path: str, **kwargs: Any) -> requests.Response:
        url = f'{self._base_url}{path}'
        try:
            response = self._session.request(
                method,
                url,
                timeout=self._timeout,
                verify=self._verify,
                **kwargs,
            )
        except requests.RequestException as exc:
            raise AuthServiceError(f'Failed to reach Trainy Auth at {url}: {exc}') from exc

        if response.status_code >= 400:
            detail = _extract_error_detail(response)
            raise AuthServiceError(
                f'{method} {path} failed with HTTP {response.status_code}: {detail}'
            )
        return response


def _extract_error_detail(response: requests.Response) -> str:
    try:
        payload = response.json()
        detail = payload.get('detail')
        if isinstance(detail, str):
            return detail
    except ValueError:
        pass
    return response.text.strip() or response.reason


def build_default_auth_store() -> AuthStore:
    return AuthStore()


def build_default_auth_service() -> AuthService:
    return AuthService()


def merge_kubeconfig(
    kubeconfig_text: str,
    *,
    destination: Optional[Path | str] = None,
    set_current_context: bool = True,
) -> Path:
    """Merge a kubeconfig snippet into ~/.kube/config (or a custom path)."""
    if not kubeconfig_text.strip():
        raise AuthServiceError('Empty kubeconfig payload received')

    destination_path = Path(destination).expanduser() if destination else DEFAULT_KUBECONFIG
    destination_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        incoming = yaml.safe_load(kubeconfig_text) or {}
    except yaml.YAMLError as exc:
        raise AuthServiceError(f'Invalid kubeconfig yaml: {exc}') from exc

    try:
        existing = (
            yaml.safe_load(destination_path.read_text(encoding='utf-8'))
            if destination_path.exists()
            else {}
        ) or {}
    except yaml.YAMLError as exc:
        logger.warning('Existing kubeconfig is invalid, overwriting: %s', exc)
        existing = {}

    merged = _merge_kubeconfig_dicts(existing, incoming, set_current_context=set_current_context)
    serialized = yaml.safe_dump(
        merged,
        default_flow_style=False,
        sort_keys=False,
    )
    destination_path.write_text(serialized, encoding='utf-8')
    return destination_path


def _merge_kubeconfig_dicts(
    existing: Dict[str, Any],
    incoming: Dict[str, Any],
    *,
    set_current_context: bool,
) -> Dict[str, Any]:
    merged = copy.deepcopy(existing) if existing else {}

    for key in ('clusters', 'users', 'contexts'):
        existing_section = existing.get(key) or []
        incoming_section = incoming.get(key) or []
        merged[key] = _merge_named_sections(existing_section, incoming_section)

    if set_current_context:
        if incoming.get('current-context'):
            merged['current-context'] = incoming['current-context']
    else:
        merged.setdefault('current-context', incoming.get('current-context'))

    for key, value in incoming.items():
        if key in {'clusters', 'users', 'contexts', 'current-context'}:
            continue
        merged[key] = value

    return merged


def _merge_named_sections(
    existing: Sequence[Dict[str, Any]],
    incoming: Sequence[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    merged: List[Dict[str, Any]] = [copy.deepcopy(entry) for entry in existing]
    index: Dict[str, int] = {}
    for idx, entry in enumerate(merged):
        name = entry.get('name')
        if isinstance(name, str):
            index[name] = idx

    for entry in incoming:
        name = entry.get('name')
        if not isinstance(name, str):
            continue
        data = copy.deepcopy(entry)
        if name in index:
            merged[index[name]] = data
        else:
            index[name] = len(merged)
            merged.append(data)
    return merged
