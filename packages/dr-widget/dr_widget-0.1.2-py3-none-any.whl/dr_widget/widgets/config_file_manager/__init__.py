"""AnyWidget bindings for the config file manager widget."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import anywidget
import traitlets

__all__ = ["ConfigFileManager"]

_STATIC_DIR = Path(__file__).parent / "static"


def _normalize_version(value: Optional[str]) -> str:
    if value is None:
        return "default_v0"
    value = str(value).strip()
    return value or "default_v0"


def _default_config_name(version: str) -> str:
    safe = ''.join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in version)
    safe = safe or "default_v0"
    return f"{safe}.json"


def _serialize_user_state(data: Dict[str, Any]) -> str:
    """Return a JSON string for the user-facing state or an empty string."""

    if not data:
        return ""

    try:
        return json.dumps(data, sort_keys=True, separators=(",", ":"))
    except (TypeError, ValueError) as exc:  # pragma: no cover - defensive
        raise ValueError("Config state must be JSON serializable") from exc


def _ensure_mapping(value: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise TypeError("config_dict must be a mapping of keys to values")
    return value


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _normalize_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure the payload follows the new metadata/data contract."""

    normalized: Dict[str, Any] = dict(payload)
    data = normalized.get("data")

    if not isinstance(data, dict):
        user_data: Dict[str, Any] = {}

        selections = normalized.pop("selections", None)
        if isinstance(selections, dict):
            user_data.setdefault("selections", selections)

        for key in list(normalized.keys()):
            if key in {"version", "saved_at", "data"}:
                continue
            user_data[key] = normalized.pop(key)

        data = user_data

    normalized["data"] = data if isinstance(data, dict) else {}
    return normalized


def _load_config_from_file(path: Path) -> Dict[str, Any]:
    try:
        raw = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise
    except OSError as exc:  # pragma: no cover - filesystem specific
        raise IOError(f"Unable to read config file: {path}") from exc

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Config file must contain valid JSON: {path}") from exc

    if not isinstance(parsed, dict):
        raise ValueError("Config file root must be a JSON object")

    return _normalize_payload(parsed)


def _write_config_to_file(path: Path, *, data: Dict[str, Any], version: str) -> None:
    payload = {
        "version": version,
        "saved_at": _utc_timestamp(),
        "data": data,
    }

    serialized = json.dumps(payload, indent=2, sort_keys=True)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(serialized + "\n", encoding="utf-8")


def _file_binding_entry(path: Path) -> Dict[str, Any]:
    try:
        size = path.stat().st_size
    except OSError:
        size = 0

    return {
        "name": path.name,
        "size": size,
        "type": "application/json",
    }


class ConfigFileManager(anywidget.AnyWidget):
    """Config file manager widget for notebooks."""

    # AnyWidget expects module references pointing at the built assets on disk.
    _esm = _STATIC_DIR / "index.js"
    _css = _STATIC_DIR / "style.css"

    current_state = traitlets.Unicode("").tag(sync=True)
    baseline_state = traitlets.Unicode("").tag(sync=True)
    config_file = traitlets.Unicode("").tag(sync=True)
    version = traitlets.Unicode("default_v0").tag(sync=True)
    files = traitlets.Unicode("[]").tag(sync=True)
    file_count = traitlets.Int(0).tag(sync=True)
    error = traitlets.Unicode("").tag(sync=True)

    def __init__(
        self,
        config_file: str | Path | None = None,
        config_dict: Optional[Dict[str, Any]] = None,
        version: str = "default_v0",
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)

        normalized_version = _normalize_version(version)
        self.version = normalized_version
        self.current_state = ""
        self.baseline_state = ""
        self.config_file = ""

        if config_file is None and config_dict is None:
            return

        if config_file is None:
            user_data = _ensure_mapping(config_dict)
            self.current_state = _serialize_user_state(user_data)
            # No baseline until the data is persisted via the UI.
            self.baseline_state = ""
            self.config_file = _default_config_name(self.version)
            return

        path = Path(config_file).expanduser()

        if config_dict is not None:
            if path.exists():
                raise FileExistsError(
                    f"Config file already exists: {path}. Refusing to overwrite."
                )

            user_data = _ensure_mapping(config_dict)
            _write_config_to_file(path, data=user_data, version=self.version)
        elif not path.exists():
            raise FileNotFoundError(f"Config file does not exist: {path}")

        payload = _load_config_from_file(path)
        file_data = payload.get("data")
        user_state = file_data if isinstance(file_data, dict) else {}
        serialized_state = _serialize_user_state(user_state)

        payload_version = payload.get("version")
        if payload_version is not None:
            version_str = _normalize_version(str(payload_version))
            self.version = version_str

        self.config_file = str(path)
        self.current_state = serialized_state
        self.baseline_state = serialized_state

        file_entry = _file_binding_entry(path)
        self.files = json.dumps([file_entry])
        self.file_count = 1

    def _parse_state(self, value: str) -> Dict[str, Any]:
        if not value:
            return {}

        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return {}

        if isinstance(parsed, dict):
            return parsed

        return {}

    @property
    def current_data(self) -> Dict[str, Any]:
        """Return the parsed current_state JSON payload as a dict."""

        return self._parse_state(self.current_state)

    @property
    def baseline_data(self) -> Dict[str, Any]:
        """Return the parsed baseline_state JSON payload as a dict."""

        return self._parse_state(self.baseline_state)

    @property
    def is_dirty(self) -> bool:
        """True if the current state differs from the last saved baseline."""

        return self.current_data != self.baseline_data
