from pathlib import Path


def test_adapter_source_is_present_and_uses_onebot11():
    source = (Path(__file__).parents[1] / "napcat" / "adapter.py").read_text(encoding="utf-8")
    assert "OneBot 11" in source
    assert "class NapCatAdapter" in source
    assert "ws_port" in source
