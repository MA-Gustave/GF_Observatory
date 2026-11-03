"""Regression tests: WordBench/GF background processes do not flash CMD."""
from __future__ import annotations

from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
from pathlib import Path
from threading import Event
from unittest.mock import patch
import subprocess

from tools import wordbench_runner as wb
from tools.windows_process import background_process_options

ROOT = Path(__file__).resolve().parents[1]
SPEC = spec_from_loader("obs_hidden_ui", SourceFileLoader("obs_hidden_ui", str(ROOT / "GF_Observatory_Diagnostic.pyw")))
UI = module_from_spec(SPEC)
SPEC.loader.exec_module(UI)


class FakeProc:
    def __init__(self):
        self.returncode = 0
        self.pid = 1234
    def communicate(self, timeout=None):
        return "sortie capturée", None
    def poll(self):
        return self.returncode


def test_windows_background_has_no_window_flag():
    opts = background_process_options(windows=True)
    assert opts["creationflags"] & 0x08000000
    assert not (opts["creationflags"] & 0x00000200)


def test_windows_process_group_still_hidden():
    opts = background_process_options(windows=True, new_process_group=True)
    assert opts["creationflags"] & 0x08000000
    assert opts["creationflags"] & 0x00000200


def test_posix_launch_unaffected():
    assert background_process_options(windows=False) == {}
    assert background_process_options(windows=False, new_process_group=True) == {"start_new_session": True}


def test_wordbench_runner_uses_hidden_policy_for_child_process():
    with patch.object(wb, "background_process_options", return_value={"creationflags": 0x08000200}) as options, \
         patch.object(wb.subprocess, "Popen", return_value=FakeProc()) as popen:
        state, code, message = wb._execute(["python.exe", "-V"], {}, 10, Event())
    options.assert_called_once_with(new_process_group=True)
    assert popen.call_args.kwargs["creationflags"] == 0x08000200
    assert state == "ok" and code == 0 and "capturée" in message


def test_gui_embedded_runner_uses_hidden_policy_for_child_process():
    with patch.object(UI, "background_process_options", return_value={"creationflags": 0x08000200}) as options, \
         patch.object(UI.subprocess, "Popen", return_value=FakeProc()) as popen:
        state, code, message = UI._execute(["python.exe", "-V"], {}, 10, Event())
    options.assert_called_once_with(new_process_group=True)
    assert popen.call_args.kwargs["creationflags"] == 0x08000200
    assert state == "ok" and code == 0 and "capturée" in message


def test_taskkill_hidden_in_wordbench_runner():
    class Running:
        pid = 2345
        def poll(self): return None
        def kill(self): raise AssertionError("should not need kill")
    with patch.object(wb.os, "name", "nt"), \
         patch.object(wb, "background_process_options", return_value={"creationflags": 0x08000000}), \
         patch.object(wb.subprocess, "run") as run:
        wb._stop_process(Running())
    assert run.call_args.kwargs["creationflags"] == 0x08000000
    assert run.call_args.args[0][0] == "taskkill"


def test_taskkill_hidden_in_gui_embedded_runner():
    class Running:
        pid = 2345
        def poll(self): return None
        def kill(self): raise AssertionError("should not need kill")
    with patch.object(UI.os, "name", "nt"), \
         patch.object(UI, "background_process_options", return_value={"creationflags": 0x08000000}), \
         patch.object(UI.subprocess, "run") as run:
        UI._stop_process(Running())
    assert run.call_args.kwargs["creationflags"] == 0x08000000
    assert run.call_args.args[0][0] == "taskkill"


def test_gf_child_process_uses_hidden_policy(tmp_path):
    """The second-level GF compiler must not open a console either."""
    from types import ModuleType, SimpleNamespace
    import sys
    from tools import wordbench_quick_probe as probe

    rgl = tmp_path / 'rgl'
    source = rgl / 'src/english/GrammarEng.gf'
    source.parent.mkdir(parents=True)
    source.write_text('concrete GrammarEng of Grammar = {} ;', encoding='utf-8')
    gf = tmp_path / 'gf.exe'
    gf.write_text('dummy executable not actually run')
    output = tmp_path / 'out'

    fake_commands = ModuleType('gf_wordbench.validation.compilation.commands')
    fake_commands.GfCommandProfile = lambda **kwargs: object()
    fake_commands.ValueOptionStyle = SimpleNamespace(EQUALS='equals')
    fake_commands.build_module_compile_command = lambda **kwargs: SimpleNamespace(
        executable=gf, arguments=('--quiet',), working_directory=source.parent)
    modules = {name: ModuleType(name) for name in (
        'gf_wordbench', 'gf_wordbench.validation', 'gf_wordbench.validation.compilation')}
    modules['gf_wordbench.validation.compilation.commands'] = fake_commands

    def fake_gf_run(*args, **kwargs):
        expected = output / 'gfo/GrammarEng.gfo'
        expected.write_bytes(b'compiled')
        return SimpleNamespace(returncode=0, stdout='Compiled successfully')

    with patch.dict(sys.modules, modules), \
         patch.object(probe, 'background_process_options', return_value={'creationflags': 0x08000000}) as opts, \
         patch.object(probe.subprocess, 'run', side_effect=fake_gf_run) as gf_run:
        assert probe.execute(source, rgl, output, gf) == 0
    opts.assert_called_once_with()
    assert gf_run.call_args.kwargs['creationflags'] == 0x08000000
    assert (output / 'quick_probe_result.json').is_file()
