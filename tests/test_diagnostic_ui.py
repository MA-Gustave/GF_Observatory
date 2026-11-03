"""Offline tests for the standalone graphical diagnostic's non-GUI core."""
from __future__ import annotations

import hashlib
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
LOADER = SourceFileLoader("gf_observatory_gui_under_test", str(ROOT / "GF_Observatory_Diagnostic.pyw"))
SPEC = spec_from_loader(LOADER.name, LOADER)
UI = module_from_spec(SPEC)
LOADER.exec_module(UI)


def dump(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False), encoding="utf-8")


def fixture_sources(tmp_path: Path):
    rgl = tmp_path / "gf-rgl"
    for relative in ("src/english/GrammarEng.gf", "src/english/SyntaxEng.gf",
                     "src/english/ParadigmsEng.gf", "src/english/LangEng.gf",
                     "src/albanian/ResSqi.gf", "src/albanian/CatSqi.gf"):
        path = rgl / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("resource Dummy = {} ;", encoding="utf-8")
    compiler = tmp_path / 'gf.exe'
    compiler.write_text('fake, never executed by these tests')
    compiler.chmod(0o755)
    return rgl


def test_inventory_sees_partial_albanian(tmp_path):
    rgl = fixture_sources(tmp_path)
    inv = UI.inventory(rgl)
    assert inv["language_count"] == 2
    sqi = next(item for item in inv["languages"] if item["code"] == "Sqi")
    assert sqi["structural_status"] == "partial_candidate"
    assert "Syntax" in sqi["structural_gaps"]
    assert "Res" in sqi["modules"]


def test_without_wordbench_never_claim_ready(tmp_path):
    rgl = fixture_sources(tmp_path)
    output = tmp_path / "output"
    result = UI.run_diagnostic(workspace=tmp_path, rgl_root=rgl, reports_root=None,
                               profile_path=ROOT / 'profiles/practical_generation_v1.json',
                               identity_map_path=None, output_dir=output)
    assert result["catalog"]["counts"] == {"ready": 0, "needs_work": 0, "unverified": 2}
    assert (output / 'diagnostic.json').is_file()
    assert (output / 'rgl_inventory.json').is_file()
    assert (output / 'practical_catalog.csv').is_file()
    assert len(next(x for x in result['catalog']['languages'] if x['code'] == 'Eng')['unverified']) == 15


def test_output_rejects_writing_to_rgl(tmp_path):
    rgl = fixture_sources(tmp_path)
    with pytest.raises(ValueError, match="sortie"):
        UI.run_diagnostic(workspace=tmp_path, rgl_root=rgl, reports_root=None,
                          profile_path=ROOT / 'profiles/practical_generation_v1.json',
                          identity_map_path=None, output_dir=rgl / 'unsafe')
    assert not (rgl / 'unsafe').exists()


def test_imports_verified_wordbench_without_retesting_every_language(tmp_path):
    rgl = fixture_sources(tmp_path)
    output = tmp_path / "out"
    reports = tmp_path / "reports"
    run = reports / "run_01"
    profile = json.loads((ROOT / "profiles/practical_generation_v1.json").read_text(encoding="utf-8"))
    summary = {"schema_id":"gf-wordbench.run-summary", "schema_version":"1.0",
               "metadata":{"project_id":"english", "run_id":"run_01", "no_compile":False},
               "totals":{"overall_status":"OK"},
               "scenario_results":[{"scenario_id":c['scenario_ids'][0], "status":"OK",
                                    "gold_match":True, "gold_path":"gold/"+c['id'],
                                    "normalized_output_path":"raw/"+c['id'], "exit_code":0}
                                   for c in profile['capabilities'] if c['required']]}
    dump(run / 'summary.json', summary)
    content = (run / 'summary.json').read_bytes()
    manifest = {"schema_id":"gf-wordbench.artifact-manifest", "schema_version":"1.0",
                "artifacts":[{"path":"summary.json", "role":"machine_summary",
                              "sha256":hashlib.sha256(content).hexdigest(), "size_bytes":len(content)}]}
    dump(run / 'manifest.json', manifest)
    report_caps = []
    for c in profile['capabilities']:
        report_caps.append({"id":c['id'], "required":c['required'], "domains":c['domains'],
                            "status":"passed" if c['required'] else "unverified"})
    dump(run / 'practical_coverage.json', {
        "schema_id":"gf-practical.coverage-result", "schema_version":"1.0",
        "language_key":"english", "wordbench_run_id":"run_01", "wordbench_run_status":"OK",
        "profile_id":profile['profile_id'], "profile_version":profile['profile_version'],
        "profile_sha256":hashlib.sha256((ROOT / 'profiles/practical_generation_v1.json').read_bytes()).hexdigest(),
        "status":"ready", "capabilities":report_caps,
        "domains":[{"domain":domain,"status":"ready"} for domain in profile['domains']]})
    aliases = tmp_path / "identity.json"
    dump(aliases, {'Eng': 'english'})
    result = UI.run_diagnostic(workspace=tmp_path, rgl_root=rgl, reports_root=reports,
                               profile_path=ROOT / 'profiles/practical_generation_v1.json',
                               identity_map_path=aliases, output_dir=output)
    assert result['catalog']['counts'] == {'ready': 1, 'needs_work': 0, 'unverified': 1}
    # Tampering with WordBench's finalized summary must revoke readiness.
    summary['metadata']['run_id'] = 'altered'
    dump(run / 'summary.json', summary)
    result = UI.run_diagnostic(workspace=tmp_path, rgl_root=rgl, reports_root=reports,
                               profile_path=ROOT / 'profiles/practical_generation_v1.json',
                               identity_map_path=aliases, output_dir=output)
    assert result['catalog']['counts']['ready'] == 0


def test_standalone_filters_technical_codes_but_preserves_partial_sqi(tmp_path):
    rgl = fixture_sources(tmp_path)
    for relative in ("src/api/abstract_to_api/AllEngAbs.gf", "src/prelude/CatCnc.gf",
                     "src/zulu/abstract_ext/CatExt.gf", "src/TEMPLATE/AllTMP.gf"):
        f = rgl / relative
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text("resource Dummy = {} ;", encoding="utf-8")
    result = UI.inventory(rgl)
    assert {item['code'] for item in result['languages']} == {'Eng', 'Sqi'}


def test_auto_imports_generated_wordbench_reports(tmp_path):
    rgl = fixture_sources(tmp_path)
    output = tmp_path / 'out'
    (output / 'wb_artifacts').mkdir(parents=True)
    result = UI.run_diagnostic(workspace=tmp_path, rgl_root=rgl, reports_root=None,
                               profile_path=ROOT / 'profiles/practical_generation_v1.json',
                               identity_map_path=None, output_dir=output)
    assert result['diagnostic']['wordbench_reports_imported']
    assert result['diagnostic']['reports_root'] == str(output / 'wb_artifacts')
    assert result['catalog']['counts']['unverified'] == 2


def test_ui_auto_detect_nested_wordbench(tmp_path):
    nested = tmp_path / 'GF_Wordbench' / 'GF_Wordbench'
    package = nested / 'src/gf_wordbench'
    package.mkdir(parents=True)
    (package / '__init__.py').touch()
    assert UI.resolve_wordbench_root(tmp_path / 'GF_Wordbench', tmp_path) == nested.resolve()
    assert 'src\\gf_wordbench' in UI.wordbench_missing_message(tmp_path / 'missing')


def test_error_saved_to_output_without_tk_thread_calls(tmp_path):
    try:
        raise RuntimeError('trace ciblée pour WordBench')
    except RuntimeError as exc:
        data = UI.DiagnosticWindow._save_error('WordBench quick', exc,
            output_dir=tmp_path / 'out', protected_paths=[tmp_path / 'src'])
    assert data['phase'] == 'WordBench quick'
    assert 'trace ciblée' in data['traceback']
    assert Path(data['log_path']).is_file()
    assert 'RuntimeError' in Path(data['log_path']).read_text(encoding='utf-8')


def test_error_log_refuses_source_tree(tmp_path):
    rgl = fixture_sources(tmp_path)
    try:
        raise RuntimeError('conflit')
    except RuntimeError as exc:
        data = UI.DiagnosticWindow._save_error('inventaire', exc,
            output_dir=rgl / 'src' / 'unsafe', protected_paths=[rgl])
    assert data['log_path'] == ''
    assert not (rgl / 'src' / 'unsafe').exists()


def test_wordbench_nonzero_is_visible_but_not_grammar_failure(tmp_path, monkeypatch):
    rgl = fixture_sources(tmp_path)
    wordbench = tmp_path / 'GF_Wordbench'
    pkg = wordbench / 'src' / 'gf_wordbench'
    pkg.mkdir(parents=True)
    (pkg / '__init__.py').touch()
    out = tmp_path / 'out'
    diag = UI.run_diagnostic(workspace=tmp_path, rgl_root=rgl, reports_root=None,
          profile_path=ROOT / 'profiles/practical_generation_v1.json',
          identity_map_path=None, output_dir=out)
    monkeypatch.setattr(UI, '_execute', lambda *args: (
       'error', 2, 'Error [CONFIGURATION]: The validation application requires a resolved RunConfig.'))
    batch = UI.run_batch(inventory=diag['inventory'],rgl_root=rgl,wordbench_root=wordbench,
                output_dir=out,codes=['Eng'],mode='quick')
    assert batch['results'][0]['reason'] == 'wordbench_runconfig_unresolved'
    diag2 = UI.run_diagnostic(workspace=tmp_path, rgl_root=rgl, reports_root=None,
          profile_path=out / 'practical_generation_profile.json',
          identity_map_path=None, output_dir=out)
    eng = next(x for x in diag2['catalog']['languages'] if x['code'] == 'Eng')
    assert eng['wordbench_quick'] == 'error'
    assert eng['wordbench_quick_reason'] == 'wordbench_runconfig_unresolved'
    assert eng['wordbench_quick_exit_code'] == 2
    assert eng['status'] == 'unverified'
    assert diag2['catalog']['counts']['needs_work'] == 0


def test_gui_preserves_failed_language_as_selection(tmp_path):
    import os
    if os.name != 'nt' and not os.environ.get('DISPLAY'):
        pytest.skip('Test graphique nécessite un serveur X')
    try:
        window = UI.DiagnosticWindow()
    except Exception:  # GUI unsupported in the current environment
        pytest.skip('Tkinter non disponible')
    try:
        window.withdraw()
        result = {
          'inventory': {'languages': []}, 'output_dir': str(tmp_path),
          'diagnostic': {'rgl_root': 'rgl', 'reports_root': None,
                         'tools': {}, 'repositories': {}},
          'catalog': {'counts': {'ready': 0, 'needs_work': 0, 'unverified': 2},
                      'languages': [
                          {'code':'Afr','status':'unverified','source_dirs':[],'structural_status':'candidate','unverified':[],'missing':[]},
                          {'code':'Eng','status':'unverified','source_dirs':[],'structural_status':'candidate','unverified':[],
                           'missing':[],'wordbench_quick':'error','wordbench_quick_reason':'gf_compilation_failed_or_wordbench_error'}]}
        }
        window._show_result(result, preferred_code='Eng')
        assert window.tree.selection() == ('Eng',)
        assert window._last_failed_code == 'Eng'
        window._render_rows()
        assert window.tree.selection() == ('Eng',)
    finally:
        window.destroy()
