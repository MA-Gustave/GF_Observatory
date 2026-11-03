"""Quick probe safety checks; no fake compiler is treated as GF evidence."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools import wordbench_quick_probe as probe


def test_probe_rejects_source_outside_rgl(tmp_path):
    rgl = tmp_path / 'rgl'
    rgl.mkdir()
    src = tmp_path / 'external.gf'
    src.write_text('abstract External = {} ;')
    assert probe.execute(src, rgl, tmp_path / 'out', None) == 6
    assert not (tmp_path/'out').exists()


def test_probe_detects_missing_gf_executable(tmp_path):
    rgl = tmp_path / 'rgl'
    rgl.mkdir()
    src = rgl / 'SyntaxEng.gf'
    src.write_text('abstract SyntaxEng = {} ;')
    assert probe.execute(src, rgl, tmp_path / 'out', tmp_path / 'missing-gf.exe') == 4
    assert not (tmp_path/'out').exists()


def test_quick_probe_includes_rgl_abstract_for_grammar_eng(tmp_path):
    """Regression: GF error `File Grammar.gf does not exist`."""
    rgl = tmp_path / 'gf-rgl'
    eng = rgl / 'src/english'
    abstract = rgl / 'src/abstract'
    common = rgl / 'src/common'
    for directory in (eng, abstract, common):
        directory.mkdir(parents=True)
    grammar = eng / 'GrammarEng.gf'
    grammar.write_text('concrete GrammarEng of Grammar = {} ;', encoding='utf-8')
    (abstract / 'Grammar.gf').write_text('abstract Grammar = {} ;', encoding='utf-8')
    paths = probe.rgl_search_paths(grammar, rgl)
    assert paths[0] == eng.resolve()
    assert abstract.resolve() in paths
    assert common.resolve() in paths
    assert paths.index(abstract.resolve()) < paths.index(common.resolve())
    assert len(paths) == len(set(paths))


def test_quick_probe_does_not_include_nonexistent_shared_paths(tmp_path):
    rgl = tmp_path / 'gf-rgl'
    eng = rgl / 'src/english'
    eng.mkdir(parents=True)
    grammar = eng / 'GrammarEng.gf'
    grammar.touch()
    paths = probe.rgl_search_paths(grammar, rgl)
    assert all(p.is_dir() for p in paths)
    assert (rgl / 'src/abstract').resolve() not in paths
