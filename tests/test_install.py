from pathlib import Path
import importlib.util


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("installer", ROOT / "install.py")
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


def test_install_patches_minimal_hermes_checkout(tmp_path):
    hermes = tmp_path / "hermes-agent"
    (hermes / "gateway").mkdir(parents=True)
    (hermes / "gateway/platforms").mkdir()
    (hermes / "gateway/config.py").write_text('    QQBOT = "qqbot"\n', encoding="utf-8")
    (hermes / "gateway/run.py").write_text(
        '        elif platform == Platform.YUANBAO:\n', encoding="utf-8"
    )
    (hermes / "gateway/authz_mixin.py").write_text(
        '                    if adapter_group_allowed:\n'
        '                        allowed = _coerce_allow_set(adapter_group_allowed)\n'
        '                        if "*" in allowed or source.chat_id in allowed:\n'
        '                            return True\n', encoding="utf-8"
    )
    installer.install(hermes)
    assert (hermes / "gateway/platforms/napcat_adapter.py").is_file()
    assert "NAPCAT = \"napcat\"" in (hermes / "gateway/config.py").read_text()
    assert (hermes / "gateway/run.py.napcat-backup").is_file()
