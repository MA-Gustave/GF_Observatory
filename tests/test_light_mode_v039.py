"""Low-cost Cat-only compilation must not be misreported as full readiness."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from tools import wordbench_runner as wb
from tools.rgl_inventory import inventory


def fixture(tmp_path: Path):
    rgl = tmp_path / 'gf-rgl'
    for relative in ('src/latvian/CatLav.gf', 'src/latvian/GrammarLav.gf',
                     'src/english/GrammarEng.gf'):
        path = rgl / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('resource Dummy = {} ;', encoding='utf-8')
    wordbench = tmp_path / 'GF_Wordbench'
    (wordbench / 'src/gf_wordbench').mkdir(parents=True)
    (wordbench / 'src/gf_wordbench/__init__.py').touch()
    gf = tmp_path / 'gf.exe'
    gf.touch()
    gf.chmod(0o755)
    return rgl, wordbench, gf


def test_light_uses_cat_not_grammar_and_keeps_quick_separate(tmp_path):
    rgl, wb_root, gf = fixture(tmp_path)
    calls = []
    def mock_execute(command, env, timeout, stop):
        calls.append(command)
        return 'ok', 0, 'mock execution only'
    with patch.object(wb, '_execute', side_effect=mock_execute):
        report = wb.run_batch(inventory=inventory(rgl), rgl_root=rgl,
                              wordbench_root=wb_root, output_dir=tmp_path/'out',
                              codes=['Lav', 'Eng'], mode='light', timeout=60,
                              gf_executable=gf)
    assert len(calls) == 1
    assert calls[0][calls[0].index('--source') + 1].endswith('CatLav.gf')
    assert report['results'][0]['code'] == 'Lav'
    assert report['results'][0]['status'] == 'ok'
    assert report['results'][0]['probe_scope'] == 'Cat module only'
    assert report['results'][0]['timeout_seconds'] == 60
    assert report['results'][1]['code'] == 'Eng'
    assert report['results'][1]['status'] == 'not_applicable'
    assert report['results'][1]['reason'] == 'light_cat_module_absent'
    assert (tmp_path/'out/wordbench_light_results.json').is_file()
    assert not (tmp_path/'out/wordbench_quick_results.json').exists()
    assert (tmp_path/'out/wordbench_logs/Lav_light.log').is_file()


def test_timeout_includes_budget_without_grammatical_failure(tmp_path):
    rgl, wb_root, gf = fixture(tmp_path)
    with patch.object(wb, '_execute', return_value=('timeout', None, 'GF started')):
        result = wb.run_batch(inventory=inventory(rgl), rgl_root=rgl,
                              wordbench_root=wb_root, output_dir=tmp_path/'out',
                              codes=['Lav'], mode='quick', timeout=300,
                              gf_executable=gf)
    r = result['results'][0]
    assert r['status'] == 'timeout'
    assert r['reason'] == 'wordbench_timeout'
    assert r['timeout_seconds'] == 300
    assert r['source_module'].endswith('GrammarLav.gf')
    log = (tmp_path/'out/wordbench_logs/Lav_quick.log').read_text(encoding='utf-8')
    assert '300 secondes' in log
    assert 'ne prouve pas une erreur grammaticale' in log
    assert json.loads((tmp_path/'out/wordbench_quick_results.json').read_text())['results'][0]['status'] == 'timeout'
