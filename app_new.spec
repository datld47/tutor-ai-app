# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['app.py'],
    pathex=['.'], # Thường chỉ cần thư mục gốc là đủ
    binaries=[],
    datas=[
        ('data', 'data'),
        ('img', 'img'),
        ('prompt', 'prompt'),
        ('compiler', 'compiler'),
        # Thêm các thư viện cần thiết khác nếu có
        ('venv/Lib/site-packages/tkcode/schemes', 'tkcode/schemes'),
    ],
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
    [], # binaries được quản lý trong COLLECT
    [], # datas được quản lý trong COLLECT
    name='TutorAI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False, # <-- Tương đương với --noconsole
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='tutorai.ico'
)

# THÊM KHỐI NÀY ĐỂ TẠO CẤU TRÚC THƯ MỤC (CHẾ ĐỘ ONE-DIR)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='TutorAI'
)