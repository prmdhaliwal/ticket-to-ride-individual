# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files


REPO_ROOT = Path(SPECPATH).parent
SOURCE_DIR = REPO_ROOT / "Sprint 2"

datas = [
    (str(SOURCE_DIR / "assets"), "assets"),
]
datas += collect_data_files("sv_ttk")


a = Analysis(
    [str(SOURCE_DIR / "main.py")],
    pathex=[str(SOURCE_DIR)],
    binaries=[],
    datas=datas,
    hiddenimports=["sv_ttk"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="TicketToRideLondon",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
