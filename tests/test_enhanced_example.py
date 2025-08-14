import importlib.util
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "python"

def load_by_filename(module_name: str, filename: str):
    path = SRC / filename
    assert path.exists(), f"Expected {path} to exist"
    spec = importlib.util.spec_from_file_location(module_name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod

def test_import_enhanced_v2_example():
    mod = load_by_filename("enhanced_v2_example", "enhanced_v2_example.py")
    assert hasattr(mod, "__file__")
