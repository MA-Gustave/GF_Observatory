"""Regression guard for the visual refactor's non-GUI contracts."""
from pathlib import Path
from tools.ui_state import read_ui_preferences, write_ui_preferences, SCHEMA
from tools.ui_theme import PALETTE


def test_brand_contract_color_meaning():
    assert PALETTE['paper'] == '#F3EFE4'
    assert PALETTE['navy'] == '#24455B'
    assert PALETTE['vermilion'] == '#D95B38'
    assert PALETTE['sage'] == '#91A18C'


def test_preferences_round_trip_without_results(tmp_path):
    target = tmp_path / 'pref.json'
    write_ui_preferences(target, {'rgl_root': 'C:/rgl', 'gf_executable': 'C:/GF/gf.exe',
                                  'wb_mode': 'quick', 'wb_timeout': '300',
                                  'wordbench_results': 'secret', 'status': 'ready'})
    actual = read_ui_preferences(target)
    assert actual == {'rgl_root': 'C:/rgl', 'gf_executable': 'C:/GF/gf.exe',
                      'wb_mode': 'quick', 'wb_timeout': '300'}
    assert 'secret' not in target.read_text(encoding='utf-8')


def test_preferences_unknown_schema_ignored(tmp_path):
    p = tmp_path / 'other.json'
    p.write_text('{"schema": "other", "values":{"wb_mode":"quick"}}')
    assert read_ui_preferences(p) == {}
    p.write_text('broken json')
    assert read_ui_preferences(p) == {}


def test_preferences_bad_execution_flags_cannot_override_default(tmp_path):
    p = tmp_path / 'pref.json'
    p.write_text('{"schema":"' + SCHEMA + '", "values":{"wb_mode":"unknown","wb_timeout":"999999","rgl_root":"c:/rgl"}}')
    assert read_ui_preferences(p) == {'rgl_root': 'c:/rgl'}


def test_ui_source_preserves_existing_runners_and_new_workspace():
    file = Path(__file__).resolve().parents[1] / 'GF_Observatory_Diagnostic.pyw'
    text = file.read_text(encoding='utf-8')
    for identifier in ('_start_wordbench', '_stop_wordbench', '_open_batch_logs',
                       '_export_batch_logs', '_save_error', 'run_diagnostic',
                       '_toggle_settings', '_refresh_metrics', '_open_selected_log'):
        assert f'def {identifier}(' in text
