"""Read-only local WordBench batch log overview for GF Observatory.

No external paths are followed; the quick/light JSON outputs are the source of
truth and source directories remain untouched. These compile probes do not
establish semantic readiness.
"""
from __future__ import annotations

import json
from pathlib import Path

VALID_MODES = ('light', 'quick')
ERROR_STATUSES = {'error', 'timeout', 'interrupted'}


def _safe_log(output_dir: Path, path: object) -> Path | None:
    if not isinstance(path, str) or not path:
        return None
    root = (output_dir / 'wordbench_logs').resolve()
    target = Path(path).expanduser().resolve()
    if not target.is_relative_to(root) or target.is_symlink() or not target.is_file():
        return None
    return target


def load_batch_log_rows(output_dir: Path) -> list[dict]:
    """Load both modes (including prior batches), preserving each result code."""
    output_dir = Path(output_dir).expanduser().resolve()
    rows = []
    for mode in VALID_MODES:
        filename = output_dir / f'wordbench_{mode}_results.json'
        if not filename.is_file() or filename.is_symlink() or filename.stat().st_size > 12_000_000:
            continue
        try:
            document = json.loads(filename.read_text(encoding='utf-8'))
            if document.get('schema_id') != 'gf-observatory.wordbench-execution' or document.get('mode') != mode:
                continue
            if not isinstance(document.get('results'), list):
                continue
            for record in document['results']:
                if not isinstance(record, dict):
                    continue
                code = record.get('code')
                if not isinstance(code, str) or len(code) != 3 or not code.isalpha():
                    continue
                status = record.get('status', 'not_tested')
                reason = record.get('reason')
                # Upgrade the v0.3.9 result without altering the historical file.
                if mode == 'light' and reason == 'light_cat_module_absent' and status == 'not_tested':
                    status = 'not_applicable'
                original_log = record.get('log_path')
                valid_path = _safe_log(output_dir, original_log)
                rows.append(dict(code=code, mode=mode, status=status,
                                 duration_seconds=record.get('duration_seconds'),
                                 reason=reason, source_module=record.get('source_module'),
                                 log_path=str(valid_path) if valid_path else None))
        except (OSError, ValueError, TypeError, KeyError):
            continue
    return sorted(rows, key=lambda r: (r['code'], VALID_MODES.index(r['mode'])))


def summarize_batch(rows: list[dict]) -> str:
    ok = sum(r['status'] == 'ok' for r in rows)
    failed = sum(r['status'] in ERROR_STATUSES for r in rows)
    na = sum(r['status'] == 'not_applicable' for r in rows)
    rest = len(rows) - ok - failed - na
    return f'{len(rows)} tests | {ok} OK | {failed} erreurs/délais | {na} non applicables | {rest} autres'


def read_log(output_dir: Path, record: dict, limit: int = 120_000) -> str:
    path = _safe_log(Path(output_dir), record.get('log_path'))
    if path is None:
        if record.get('status') == 'not_applicable':
            return 'Test light non applicable : aucun module Cat de cette langue. Aucune compilation tentée.\n'
        return 'Aucun journal enregistré pour ce test.\n'
    # Guard against enormous or hostile log files; preserve useful tail.
    with path.open('rb') as file:
        file.seek(0, 2)
        length = file.tell()
        file.seek(max(0, length - limit))
        content = file.read(limit)
    text = content.decode('utf-8', errors='replace')
    return ('[Début du journal omis : contenu tronqué]\n' if length > limit else '') + text


def format_batch_report(output_dir: Path, rows: list[dict]) -> str:
    parts = ['GF Observatory — Journaux WordBench regroupés',
             summarize_batch(rows),
             'Quick/light = compilation structurelle ; aucune preuve de couverture génération pratique.',
             '']
    for record in rows:
        parts.append('=' * 75)
        parts.append(f"{record['code']} | {record['mode']} | {record['status']} | "
                     f"{record.get('duration_seconds')} s | {record.get('reason') or 'aucun'}")
        parts.append(f"Journal : {record.get('log_path') or 'aucun'}")
        parts.append(read_log(output_dir, record, limit=300_000))
        parts.append('')
    return '\n'.join(parts) + '\n'
