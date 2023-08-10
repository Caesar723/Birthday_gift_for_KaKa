# -*- mode: python ; coding: utf-8 -*-


block_cipher = None

import os
import sys

if sys.platform.startswith('win'):
    separate="\\"
else:
    separate="/"

your_path=os.path.abspath(os.getcwd())

folders=["img","music","stl"]

datas=[]

for folder in folders:
    file_list = os.listdir(f"{your_path}{separate}{folder}")
    for file in file_list:
        datas.append((f"{your_path}{separate}{folder}{separate}{file}",f".{separate}{folder}"))


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch='arm64',
    codesign_identity=None,
    entitlements_file=None,
    icon='leo.icns',
)
app = BUNDLE(
    exe,
    name='Gift_for_KaKa❤️.app',
    icon='img.icns',
    bundle_identifier=None,
)
