from importlib import import_module


def test_streamlit_app_imports() -> None:
    module = import_module("etf150.streamlit_app")
    assert hasattr(module, "main")
