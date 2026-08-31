"""Install the native NapCat adapter into an existing Hermes checkout.

Usage:
    python install.py --hermes-dir C:/path/to/hermes-agent

This installer is intentionally conservative: it refuses to overwrite an
existing adapter and creates backups before changing existing Hermes files.
"""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

REQUIRED = ["gateway/config.py", "gateway/run.py", "gateway/authz_mixin.py"]


def backup(path: Path) -> None:
    target = path.with_suffix(path.suffix + ".napcat-backup")
    if not target.exists():
        shutil.copy2(path, target)


def patch_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new in text:
        return
    if old not in text:
        raise RuntimeError(f"Could not find patch anchor in {path}")
    backup(path)
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def install(hermes_dir: Path) -> None:
    if not all((hermes_dir / p).is_file() for p in REQUIRED):
        raise RuntimeError("Not a Hermes Agent source checkout: missing required files")
    root = Path(__file__).resolve().parent
    target = hermes_dir / "gateway/platforms"
    target.mkdir(parents=True, exist_ok=True)
    for name in ("adapter.py", "api.py"):
        dest = target / f"napcat_{name}"
        if dest.exists():
            raise RuntimeError(f"Refusing to overwrite {dest}; remove it or uninstall manually")
        shutil.copy2(root / "napcat" / name, dest)

    config = hermes_dir / "gateway/config.py"
    text = config.read_text(encoding="utf-8")
    anchor = '    QQBOT = "qqbot"\n'
    patch_once(config, anchor, anchor + '    NAPCAT = "napcat"\n')

    run = hermes_dir / "gateway/run.py"
    anchor = '''        elif platform == Platform.YUANBAO:\n'''
    addition = '''        elif platform == Platform.NAPCAT:\n            from gateway.platforms.napcat_adapter import NapCatAdapter, check_napcat_requirements\n            if not check_napcat_requirements():\n                return None\n            return NapCatAdapter(config)\n\n'''
    patch_once(run, anchor, addition + anchor)

    authz = hermes_dir / "gateway/authz_mixin.py"
    anchor = '''                    if adapter_group_allowed:\n                        allowed = _coerce_allow_set(adapter_group_allowed)\n                        if "*" in allowed or source.chat_id in allowed:\n                            return True\n'''
    addition = anchor + '''                    napcat_allowed = getattr(adapter, "_group_allow_from", None)\n                    if napcat_allowed:\n                        allowed = _coerce_allow_set(napcat_allowed)\n                        if "*" in allowed or str(source.chat_id) in allowed:\n                            return True\n'''
    patch_once(authz, anchor, addition)
    print("NapCat adapter installed.")
    print("Configure platforms.napcat in Hermes config.yaml, then restart the gateway.")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--hermes-dir", type=Path, required=True)
    args = parser.parse_args()
    install(args.hermes_dir.expanduser().resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
