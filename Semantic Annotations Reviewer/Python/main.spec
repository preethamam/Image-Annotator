# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['D:\\OneDrive\\Education Materials\\Applications\\Toolboxes\\Python\\My Functions\\Image Annotator\\Semantic Annotations Reviewer\\Python\\main.py'],
    pathex=[],
    binaries=[],
    datas=[('D:\\OneDrive\\Education Materials\\Applications\\Toolboxes\\Python\\My Functions\\Image Annotator\\Semantic Annotations Reviewer\\Python\\pictures.kv', '.'), ('D:\\OneDrive\\Education Materials\\Applications\\Toolboxes\\Python\\My Functions\\Image Annotator\\Semantic Annotations Reviewer\\Python\\app.ico', '.'), ('D:\\OneDrive\\Education Materials\\Applications\\Toolboxes\\Python\\My Functions\\Image Annotator\\Semantic Annotations Reviewer\\Python\\icon.png', '.')],
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
    [],
    exclude_binaries=True,
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['D:\\OneDrive\\Education Materials\\Applications\\Toolboxes\\Python\\My Functions\\Image Annotator\\Semantic Annotations Reviewer\\Python\\app.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='main',
)
