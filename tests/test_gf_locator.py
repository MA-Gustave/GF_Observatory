"""GF compiler presence and bounded auto-discovery; no real GF is required."""
from pathlib import Path
import sys
from unittest.mock import patch
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools.gf_locator import resolve_gf_executable, missing_gf_message
from tools.wordbench_runner import run_batch
from tools.rgl_inventory import inventory


def fake_gf(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('fake test executable, not used to claim a GF pass')
    path.chmod(0o755)
    return path


def test_find_workspace_root_executable(tmp_path):
    gf=fake_gf(tmp_path/'gf.exe')
    with patch('tools.gf_locator.shutil.which', return_value=None):
        assert resolve_gf_executable(None, tmp_path)==gf.resolve()


def test_find_compiler_in_nested_build_tree(tmp_path):
    gf=fake_gf(tmp_path/'gf-core'/'dist-newstyle'/'build'/'test'/'x'/'gf'/'build'/'gf'/'gf.exe')
    with patch('tools.gf_locator.shutil.which', return_value=None):
        assert resolve_gf_executable(None, tmp_path)==gf.resolve()


def test_explicit_invalid_path_must_not_silently_use_another(tmp_path):
    fake_gf(tmp_path/'gf.exe')
    assert resolve_gf_executable(tmp_path/'missing'/'gf.exe',tmp_path) is None


def test_not_a_compiler_if_only_sources_exist(tmp_path):
    (tmp_path/'gf-core').mkdir()
    (tmp_path/'gf-rgl').mkdir()
    with patch('tools.gf_locator.shutil.which',return_value=None):
        assert resolve_gf_executable(None,tmp_path) is None
    assert 'gf.exe' in missing_gf_message(tmp_path)


def test_batch_preflight_prevents_67_failing_subprocesses(tmp_path):
    rgl = tmp_path/'gf-rgl'
    file=rgl/'src/english/SyntaxEng.gf'
    file.parent.mkdir(parents=True)
    file.write_text('concrete SyntaxEng of Syntax = {} ;')
    wb=tmp_path/'GF_Wordbench'
    pkg=wb/'src/gf_wordbench'
    pkg.mkdir(parents=True)
    (pkg/'__init__.py').touch()
    with patch('tools.gf_locator.shutil.which',return_value=None), \
         patch('tools.wordbench_runner._execute',side_effect=AssertionError('no subprocess')):
        with pytest.raises(ValueError, match='Compilateur Grammatical Framework introuvable'):
            run_batch(inventory=inventory(rgl), rgl_root=rgl, wordbench_root=wb,
                      output_dir=tmp_path/'results',codes=['Eng'],mode='quick')
    assert not (tmp_path/'results'/'wordbench_quick_results.json').exists()


def test_batch_passes_detected_gf_executable_to_probe(tmp_path):
    gf=fake_gf(tmp_path/'gf.exe')
    rgl=tmp_path/'gf-rgl'
    file=rgl/'src/english/SyntaxEng.gf'
    file.parent.mkdir(parents=True)
    file.write_text('concrete SyntaxEng of Syntax = {} ;')
    wb=tmp_path/'GF_Wordbench'
    pkg=wb/'src/gf_wordbench'
    pkg.mkdir(parents=True)
    (pkg/'__init__.py').touch()
    with patch('tools.wordbench_runner._execute',return_value=('error',4,'GF not really executed here')) as call:
        batch=run_batch(inventory=inventory(rgl),rgl_root=rgl,wordbench_root=wb,
                        output_dir=tmp_path/'results',codes=['Eng'],mode='quick')
    assert '--gf-exe' in call.call_args.args[0]
    assert str(gf.resolve()) in call.call_args.args[0]
    assert batch['results'][0]['status']=='error'


def test_find_gf_312_windows_bundle_without_path(tmp_path):
    from tools.gf_locator import default_gf_executable
    gf = fake_gf(tmp_path / 'gf-3.12-windows' / 'gf.exe')
    with patch('tools.gf_locator.shutil.which', return_value=None):
        assert resolve_gf_executable(None, tmp_path) == gf.resolve()
        assert default_gf_executable(tmp_path) == gf.resolve()


def test_default_prefers_verified_local_gf_over_path(tmp_path):
    from tools.gf_locator import default_gf_executable
    local = fake_gf(tmp_path / 'gf-3.12-windows' / 'gf.exe')
    other = fake_gf(tmp_path / 'other' / 'gf.exe')
    with patch('tools.gf_locator.shutil.which', return_value=str(other)):
        assert default_gf_executable(tmp_path) == local.resolve()


def test_default_falls_back_if_local_bundle_missing(tmp_path):
    from tools.gf_locator import default_gf_executable
    other = fake_gf(tmp_path / 'gf.exe')
    with patch('tools.gf_locator.shutil.which', return_value=None):
        assert default_gf_executable(tmp_path) == other.resolve()
