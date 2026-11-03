# -*- coding: utf-8 -*-
"""Small, opt-in GUI preference persistence. Never contains GF results/proofs."""
from __future__ import annotations

import json
from pathlib import Path

FIELDS = (
    'workspace', 'rgl_root', 'reports_root', 'wordbench_root',
    'validation_profiles_root', 'gf_executable', 'profile_path',
    'identity_path', 'output_dir', 'wb_mode', 'wb_timeout',
)
SCHEMA = 'gf-observatory.ui-preferences-v1'


def read_ui_preferences(file: Path) -> dict[str, str]:
    try:
        data = json.loads(Path(file).read_text(encoding='utf-8'))
    except (OSError, ValueError, UnicodeError):
        return {}
    if not isinstance(data, dict) or data.get('schema') != SCHEMA:
        return {}
    values = data.get('values')
    if not isinstance(values, dict):
        return {}
    clean = {k: v for k, v in values.items()
             if k in FIELDS and isinstance(v, str) and len(v) <= 4096}
    if clean.get('wb_mode') not in ('light', 'quick', 'practical'):
        clean.pop('wb_mode', None)
    try:
        if not 5 <= int(clean.get('wb_timeout', '60')) <= 3600:
            clean.pop('wb_timeout', None)
    except (ValueError, TypeError):
        clean.pop('wb_timeout', None)
    return clean


def write_ui_preferences(file: Path, values: dict[str, str]) -> None:
    """Best effort atomic replacement in the user home, never in the RGL."""
    path = Path(file)
    permitted = {k: str(values[k]) for k in FIELDS if k in values}
    content = json.dumps({'schema': SCHEMA, 'values': permitted},
                         ensure_ascii=False, indent=2) + '\n'
    temporary = path.with_name(path.name + '.tmp')
    temporary.write_text(content, encoding='utf-8')
    temporary.replace(path)
