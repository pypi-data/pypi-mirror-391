import base64
import json
import requests
from typing import Dict, Any
from .config import get_cfg

# Global shared state
_CONFIG: Dict[str, Any] = {
    "enabled": False,
    "endpoint": None,
    "headers": None,
    "timeout": 10,
}

def init_langfuse():
    global _CONFIG

    cfg = get_cfg()

    public_key = cfg["langfuse_public"]
    secret_key = cfg["langfuse_secret"]
    endpoint   = cfg["langfuse_endpoint"]

    if not public_key or not secret_key or not endpoint:
        raise ValueError("Langfuse credentials missing in .env")

    auth = base64.b64encode(f"{public_key}:{secret_key}".encode()).decode()

    _CONFIG.update({
        "enabled": True,
        "endpoint": endpoint.rstrip("/"),
        "headers": {
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/json",
        },
        "timeout": 10,
    })

def is_enabled() -> bool:
    return _CONFIG["enabled"]

def send_bundle(bundle: Dict[str, Any]) -> bool:
    if not _CONFIG["enabled"]:
        return False

    try:
        resp = requests.post(
            _CONFIG["endpoint"],
            json=bundle,
            headers=_CONFIG["headers"],
            timeout=_CONFIG["timeout"]
        )
        return resp.status_code < 300
    except Exception:
        return False
