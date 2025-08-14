import pytest

import importlib.util, pathlib

def load_module(path):
    spec = importlib.util.spec_from_file_location("genmod", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def test_requires_passes(tmp_path):
    mod = load_module(str(pathlib.Path("/mnt/data/enhanced_example.py")))
    def process(x):
        class Obj: pass
        o = Obj(); o.score = x
        return o
    mod.process = process
    def handle_error(msg): pass
    mod.handle_error = handle_error
    items = [1,2,3,4]
    limiter = 2
    fn = getattr(mod, "ProcessItems", getattr(mod, "process_items"))
    out = fn(items, limiter)
    assert all(getattr(o, "score", 0) >= limiter for o in out)

def test_requires_fails():
    mod = load_module(str(pathlib.Path("/mnt/data/enhanced_example.py")))
    fn = getattr(mod, "ProcessItems", getattr(mod, "process_items"))
    import pytest
    with pytest.raises(AssertionError):
        fn(None, 1)
