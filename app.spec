# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files
a = Analysis(
    ['app.py'],
    pathex=[
        '.',                      # chính là project/project4
        '../../env_project4/Lib/site-packages'  # để import usersustomsize
    ],
    binaries=[],
    datas=[
        ('prompt', 'prompt'),
        ('../../env_project4/Lib/site-packages/tkcode/schemes', 'tkcode/schemes')],
    hiddenimports=[],
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
    name='app',
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
