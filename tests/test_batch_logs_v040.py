"""Batch overview must expose every language and not misclassify missing Cat."""
from __future__ import annotations
import json
from pathlib import Path
from unittest.mock import patch
from tools import wordbench_runner as wb
from tools.batch_logs import load_batch_log_rows, read_log, format_batch_report, summarize_batch
from tools.rgl_inventory import inventory


def sample(tmp_path: Path):
    root = tmp_path / 'gf-rgl'
    for name in ('src/latvian/CatLav.gf', 'src/greenlandic/ResKal.gf', 'src/greenlandic/GrammarKal.gf'):
        p = root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text('resource Foo = {} ;', encoding='utf-8')
    wb_root = tmp_path / 'GF_Wordbench'
    (wb_root / 'src/gf_wordbench').mkdir(parents=True)
    (wb_root / 'src/gf_wordbench/__init__.py').touch()
    gf = tmp_path / 'gf.exe'
    gf.touch()
    gf.chmod(0o755)
    return root, wb_root, gf


def test_missing_cat_is_not_applicable_and_quick_result_preserved(tmp_path):
    rgl, wb_root, gf = sample(tmp_path)
    output = tmp_path / 'out'
    with patch.object(wb, '_execute', return_value=('ok', 0, 'GF OK')):
        result = wb.run_batch(inventory=inventory(rgl), rgl_root=rgl, wordbench_root=wb_root,
                              output_dir=output, codes=['Kal','Lav'], mode='light',timeout=30, gf_executable=gf)
        assert result['results'][0]['status'] == 'not_applicable'
        assert result['results'][0]['reason'] == 'light_cat_module_absent'
        wb.run_batch(inventory=inventory(rgl),rgl_root=rgl,wordbench_root=wb_root,output_dir=output,
                     codes=['Kal'],mode='quick',timeout=30,gf_executable=gf)
    rows = load_batch_log_rows(output)
    assert len(rows) == 3
    kal_light = next(r for r in rows if r['code']=='Kal' and r['mode']=='light')
    kal_quick = next(r for r in rows if r['code']=='Kal' and r['mode']=='quick')
    assert kal_light['status'] == 'not_applicable' and kal_light['log_path'] is None
    assert kal_quick['status'] == 'ok'
    assert 'Aucune compilation tentée' in read_log(output,kal_light)
    report=format_batch_report(output,rows)
    assert 'Kal | light | not_applicable' in report and 'Kal | quick | ok' in report
    assert 'GF OK' in report
    assert '1 non applicables' in summarize_batch(rows)


def test_legacy_missing_cat_and_unsafe_logs(tmp_path):
    out = tmp_path / 'out'
    out.mkdir()
    outside = tmp_path / 'outside.log'
    outside.write_text('SENSITIVE DATA', encoding='utf-8')
    data={'schema_id':'gf-observatory.wordbench-execution','mode':'light','results':[
        {'code':'Kal','status':'not_tested','reason':'light_cat_module_absent','log_path':None},
        {'code':'Lav','status':'ok','log_path':str(outside)}]}
    (out/'wordbench_light_results.json').write_text(json.dumps(data),encoding='utf-8')
    rows=load_batch_log_rows(out)
    assert rows[0]['status']=='not_applicable'
    assert rows[1]['log_path'] is None
    assert 'SENSITIVE DATA' not in format_batch_report(out,rows)


def test_ui_has_batch_log_tab_and_summary(tmp_path):
    from importlib.machinery import SourceFileLoader
    from importlib.util import spec_from_loader, module_from_spec
    script = Path(__file__).resolve().parents[1] / 'GF_Observatory_Diagnostic.pyw'
    loader = SourceFileLoader('observatory_ui_v040', str(script))
    spec = spec_from_loader(loader.name, loader)
    module = module_from_spec(spec)
    loader.exec_module(module)
    assert hasattr(module.DiagnosticWindow,'_make_batch_logs_tab')
    assert hasattr(module.DiagnosticWindow,'_export_batch_logs')
    assert hasattr(module.DiagnosticWindow,'_open_batch_logs')
