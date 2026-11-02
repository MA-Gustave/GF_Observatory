"""Test WordBench integration without running or impersonating a GF compiler."""
from pathlib import Path
import json
import threading
import sys
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools import wordbench_runner as wb
from tools.rgl_inventory import inventory


def sample(tmp_path):
    root = tmp_path / 'rgl'
    for item in ('src/english/SyntaxEng.gf', 'src/albanian/CatSqi.gf',
                 'src/api/abstract_to_api/AllEngAbs.gf', 'src/zulu/abstract_ext/CatExt.gf',
                 'src/TEMPLATE/AllTMP.gf', 'src/prelude/PredefCnc.gf'):
        file = root / item
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text('resource Dummy = {} ;', encoding='utf-8')
    project = tmp_path / 'GF_Wordbench'
    pkg = project / 'src/gf_wordbench'
    pkg.mkdir(parents=True)
    (pkg / '__init__.py').touch()
    return root, project


def test_phantom_codes_are_not_languages(tmp_path):
    rgl, _ = sample(tmp_path)
    result = inventory(rgl)
    assert {lang['code'] for lang in result['languages']} == {'Eng', 'Sqi'}


def test_selective_quick_uses_canonical_wordbench_not_full_suite(tmp_path):
    rgl, project = sample(tmp_path)
    inv = inventory(rgl)
    seen = []
    def fake_exec(cmd, env, timeout, stop):
        seen.append(cmd)
        return 'ok', 0, 'fake command exit 0, not a GF test\n'
    with patch.object(wb, '_execute', side_effect=fake_exec):
        batch = wb.run_batch(inventory=inv, rgl_root=rgl, wordbench_root=project,
                             output_dir=tmp_path/'out', codes=['Eng'], timeout=90)
    assert len(seen) == 1
    assert seen[0][1:6] == ['-m','gf_wordbench','validate','--mode','quick']
    assert '--target' in seen[0] and any('SyntaxEng.gf' in x for x in seen[0])
    assert batch['results'][0]['status'] == 'ok'
    assert batch['results'][0]['source_module'].endswith('SyntaxEng.gf')
    assert len(batch['results']) == 1
    assert json.loads((tmp_path/'out'/'wordbench_quick_results.json').read_text())['mode'] == 'quick'


def test_practical_needs_scenarios_and_never_approves_missing_gold(tmp_path):
    rgl, project = sample(tmp_path)
    (project / 'src/gf_wordbench/practical').mkdir()
    (project / 'src/gf_wordbench/practical/cli.py').touch()
    practical_profile = tmp_path / 'practical.json'
    practical_profile.write_text('{}')
    inv = inventory(rgl)
    with patch.object(wb, '_execute', side_effect=AssertionError('must not execute')):
        report = wb.run_batch(inventory=inv, rgl_root=rgl, wordbench_root=project,
                              output_dir=tmp_path/'out', codes=['Sqi'], mode='practical',
                              practical_profile=practical_profile)
    assert report['results'][0]['status'] == 'not_tested'
    assert 'profil' in report['results'][0]['reason'].lower()


def test_rejects_writing_inside_rgl(tmp_path):
    rgl, project = sample(tmp_path)
    try:
        wb.run_batch(inventory=inventory(rgl), rgl_root=rgl, wordbench_root=project,
                     output_dir=rgl/'results', codes=['Eng'])
        assert False, 'Expected safe output guard'
    except ValueError as exc:
        assert 'sortie' in str(exc)


def test_wordbench_resolves_nested_zip_layout(tmp_path):
    base = tmp_path / 'workspace'
    nested = base / 'GF_Wordbench' / 'GF_Wordbench'
    pkg = nested / 'src' / 'gf_wordbench'
    pkg.mkdir(parents=True)
    (pkg / '__init__.py').touch()
    assert wb.resolve_wordbench_root(base / 'GF_Wordbench', base) == nested.resolve()
    assert wb.resolve_wordbench_root(nested) == nested.resolve()
    assert wb.resolve_wordbench_root(pkg.parent) == nested.resolve()
    assert wb.resolve_wordbench_root(base / 'missing', base) == nested.resolve()
    assert wb.resolve_wordbench_root(base / 'none') is None


def test_batch_runs_on_detected_nested_wordbench(tmp_path):
    rgl, unused = sample(tmp_path)
    nested = tmp_path / 'workspace' / 'GF_Wordbench' / 'GF_Wordbench'
    pkg = nested / 'src/gf_wordbench'
    pkg.mkdir(parents=True)
    (pkg / '__init__.py').touch()
    with patch.object(wb, '_execute', return_value=('ok', 0, 'hello')) as executed:
        result = wb.run_batch(inventory=inventory(rgl), rgl_root=rgl,
                              wordbench_root=nested.parent, output_dir=tmp_path / 'reports',
                              codes=['Eng'], mode='quick')
    assert executed.call_count == 1
    assert result['wordbench_root'] == str(nested.resolve())
    assert result['results'][0]['status'] == 'ok'


def test_preflight_absent_wordbench_clear_message(tmp_path):
    rgl, unused = sample(tmp_path)
    import pytest
    with pytest.raises(ValueError, match='Détecter WordBench'):
        wb.run_batch(inventory=inventory(rgl), rgl_root=rgl,
                     wordbench_root=tmp_path / 'missing', output_dir=tmp_path / 'reports',
                     codes=['Eng'])
