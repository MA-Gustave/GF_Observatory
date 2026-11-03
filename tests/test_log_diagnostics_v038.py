"""Regressions for observed RGL batch diagnostics. No real GF executable invoked."""
from __future__ import annotations

from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools import wordbench_runner as runner, wordbench_quick_probe as probe

spec = spec_from_loader('observatory_v038_gui', SourceFileLoader('observatory_v038_gui', str(ROOT / 'GF_Observatory_Diagnostic.pyw')))
ui = module_from_spec(spec)
spec.loader.exec_module(ui)


def test_detect_windows_interruption_not_grammar_failure():
    for func in (runner.classify_quick_result, ui.classify_quick_result):
        assert func('error', 3221225786, '') == ('interrupted', 'windows_control_c_exit')
        assert func('error', -1073741510, '') == ('interrupted', 'windows_control_c_exit')
        assert func('error', 23, 'Processus GF interrompu (0xC000013A)') == ('interrupted', 'windows_control_c_exit')
        assert func('timeout', None, '') == ('timeout', 'wordbench_timeout')
        assert func('ok', 0, 'OK') == ('ok', None)


def test_distinct_compilation_diagnostics():
    func = runner.classify_quick_result
    assert func('error', 2, 'File CatBantu.gf does not exist.')[1] == 'gf_dependency_missing'
    assert func('error', 2, 'gf.exe: Internal error in Compute.Concrete:')[1] == 'gf_compiler_internal_error'
    assert func('error', 2, 'constant not found: IdetQuant')[1] == 'gf_api_symbol_missing'
    assert func('error', 2, 'unknown label hasDot in {s : Str}')[1] == 'gf_typecheck_error'


def test_shared_bantu_scots_zulu_paths(tmp_path):
    root=tmp_path / 'gf-rgl'
    src=root/'src'
    for relative in ['abstract', 'bantu', 'english', 'scots', 'zulu', 'zulu/abstract_ext', 'swahili']:
        (src/relative).mkdir(parents=True,exist_ok=True)
    (src/'bantu/CatBantu.gf').touch()
    (src/'english/NounEng.gf').touch()
    (src/'zulu/abstract_ext/CatExt.gf').touch()
    for code, rel, required in [('Swa','swahili','bantu'),('Sco','scots','english'),('Zul','zulu','zulu/abstract_ext')]:
        grammar=src/rel/f'Grammar{code}.gf'
        grammar.touch()
        paths=probe.rgl_search_paths(grammar,root)
        assert (src/required).resolve() in paths
        assert paths[0]==grammar.parent.resolve()
        assert len(paths)==len(set(paths))
    paths=probe.rgl_search_paths(src/'swahili/GrammarSwa.gf',root)
    assert (src/'zulu/abstract_ext').resolve() not in paths


def test_quick_batch_results_are_separate_from_history(tmp_path,monkeypatch):
    root=tmp_path/'gf-rgl'; source=root/'src/english/GrammarEng.gf'; source.parent.mkdir(parents=True)
    source.write_text('concrete GrammarEng of Grammar = {} ;')
    wb=tmp_path/'GF_Wordbench'; pkg=wb/'src/gf_wordbench';pkg.mkdir(parents=True);(pkg/'__init__.py').touch()
    gf=tmp_path/'gf.exe';gf.touch()
    inv={'languages':[{'code':'Eng','modules':{'Grammar':['src/english/GrammarEng.gf']}}]}
    out=tmp_path/'out';out.mkdir()
    prev={'schema_id':'gf-observatory.wordbench-execution','rgl_root':str(root.resolve()),'results':[{'code':'Fre','status':'ok','exit_code':0}]}
    import json
    (out/'wordbench_quick_results.json').write_text(json.dumps(prev))
    monkeypatch.setattr(runner,'resolve_gf_executable',lambda *a,**k:gf)
    monkeypatch.setattr(runner,'_execute',lambda *a:('error',3221225786,''))
    result=runner.run_batch(inventory=inv,rgl_root=root,wordbench_root=wb,output_dir=out,codes=['Eng'],gf_executable=gf)
    assert result['completed']==1
    assert len(result['batch_results'])==1
    assert result['batch_results'][0]['status']=='interrupted'
    assert {r['code'] for r in result['results']}=={'Eng','Fre'}


def test_existing_generic_results_read_only_local_log_for_classification(tmp_path):
    import json
    rgl=tmp_path/'gf-rgl';(rgl/'src/english').mkdir(parents=True)
    (rgl/'src/english/GrammarEng.gf').touch()
    out=tmp_path/'reports'; logs=out/'wordbench_logs';logs.mkdir(parents=True)
    log=logs/'Eng_quick.log';log.write_text('File CatBantu.gf does not exist.',encoding='utf-8')
    profile=ROOT/'profiles/practical_generation_v1.json'
    old={'schema_id':'gf-observatory.wordbench-execution','mode':'quick','rgl_root':str(rgl.resolve()),
         'results':[{'code':'Eng','status':'error','exit_code':2,'reason':'wordbench_exit_nonzero','log_path':str(log)}]}
    (out/'wordbench_quick_results.json').write_text(json.dumps(old),encoding='utf-8')
    report=ui.run_diagnostic(workspace=tmp_path,rgl_root=rgl,reports_root=None,profile_path=profile,identity_map_path=None,output_dir=out)
    row=next(r for r in report['catalog']['languages'] if r['code']=='Eng')
    assert row['wordbench_quick_reason']=='gf_dependency_missing'
    assert row['status']=='unverified'
