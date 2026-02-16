# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files, collect_submodules, copy_metadata
import sys
import os

block_cipher = None

# Collect data files
datas = []
datas += collect_data_files('customtkinter')
datas += collect_data_files('presidio_analyzer')
datas += copy_metadata('presidio_analyzer')
datas += copy_metadata('presidio_anonymizer')
datas += collect_data_files('en_core_web_lg')
datas += copy_metadata('en_core_web_lg')
datas += copy_metadata('spacy')

# Hidden imports
hiddenimports = [
    'presidio_analyzer', 
    'customtkinter', 
    'pystray', 
    'PIL', 
    'spacy', 
    'en_core_web_lg'
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
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
    name='SafePaste',
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
    icon='safepaste/icon.ico' if False else None # Placeholder
)
