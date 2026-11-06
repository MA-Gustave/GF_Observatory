"""Exact-byte evidence hashing, bounded JSON and stable local fingerprints.

The local canonical JSON scheme is *not* RFC 8785 and does not replace producer hash rules.
"""
import hashlib
import json
import math
from datetime import datetime, timezone
from .errors import ObservatoryError, require

FINGERPRINT_PROFILE = "gf-observatory.sorted-json-utf8/1"

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def dumps(value) -> bytes:
    return json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")

def fingerprint(value) -> str:
    return sha256(dumps({"fingerprint_profile": FINGERPRINT_PROFILE, "value": value}))

def loads(raw: bytes, max_size: int = 8*1024*1024):
    require(len(raw) <= max_size, "OBS_JSON_TOO_LARGE", "JSON exceeds configured size bound")
    def pairs(items):
        out = {}
        for k, v in items:
            if k in out:
                raise ValueError("Duplicate JSON key")
            out[k] = v
        return out
    def reject_constant(x):
        raise ValueError("Nonfinite JSON number")
    try:
        obj = json.loads(raw.decode("utf-8"), object_pairs_hook=pairs, parse_constant=reject_constant)
        def walk(node, depth=0):
            if depth > 64:
                raise ValueError("JSON nesting >64")
            if isinstance(node, float) and not math.isfinite(node):
                raise ValueError("Nonfinite JSON float")
            if isinstance(node, dict):
                for value in node.values(): walk(value, depth+1)
            elif isinstance(node, list):
                for value in node: walk(value, depth+1)
        walk(obj)
    except (UnicodeError, ValueError, RecursionError) as exc:
        raise ObservatoryError("OBS_JSON_INVALID", f"Invalid JSON: {exc}") from exc
    return obj

def utcnow():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def parse_time(v: str):
    require(isinstance(v, str), "OBS_TIME_INVALID", "Expected timestamp string")
    try:
        t = datetime.fromisoformat(v.replace("Z", "+00:00"))
        require(t.tzinfo is not None, "OBS_TIME_INVALID", "Timestamp must include timezone")
        return t.astimezone(timezone.utc)
    except ValueError as exc:
        raise ObservatoryError("OBS_TIME_INVALID", "Bad timestamp") from exc
