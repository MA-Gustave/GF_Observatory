"""The product rename must not make existing Windows workspaces disappear."""
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
LOADER=SourceFileLoader('gf_obs_defluens_identity_test', str(ROOT/'GF_Observatory_Diagnostic.pyw'))
SPEC=spec_from_loader(LOADER.name,LOADER)
UI=module_from_spec(SPEC)
LOADER.exec_module(UI)


def test_prefers_new_defluens_slug_when_present(tmp_path):
    (tmp_path/'ars-magna-defluens').mkdir()
    (tmp_path/'ars-magna-lulli').mkdir()
    env=UI.collect_environment(tmp_path,tmp_path)
    repo=env['repositories']['ars-magna-defluens']
    assert repo['exists'] is True
    assert Path(repo['path']).name=='ars-magna-defluens'


def test_accepts_legacy_lulli_folder(tmp_path):
    (tmp_path/'ars-magna-lulli').mkdir()
    env=UI.collect_environment(tmp_path,tmp_path)
    repo=env['repositories']['ars-magna-defluens']
    assert repo['exists'] is True
    assert Path(repo['path']).name=='ars-magna-lulli'


def test_unknown_defluens_repo_is_not_claimed_present(tmp_path):
    env=UI.collect_environment(tmp_path,tmp_path)
    repo=env['repositories']['ars-magna-defluens']
    assert repo['exists'] is False
