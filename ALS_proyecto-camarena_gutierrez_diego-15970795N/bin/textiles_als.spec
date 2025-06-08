# PyInstaller spec file para compilar Sistema de Gestión Textiles ALS
# Este archivo define cómo PyInstaller debe crear el ejecutable

# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Definir datos adicionales que incluir
added_files = [
    ('../src/app/templates', 'app/templates'),
    ('../src/app/static', 'app/static'),
]

# Módulos ocultos que PyInstaller no detecta automáticamente
hidden_imports = [
    'app',
    'app.models',
    'app.routes', 
    'app.forms',
    'app.services',
    'app.utils',
    'app.models.usuario',
    'app.models.cliente', 
    'app.models.producto',
    'app.models.pedido',
    'app.models.proceso',
    'app.services.storage_service',
    'flask',
    'flask_login',
    'flask_wtf',
    'flask_wtf.csrf',
    'wtforms',
    'wtforms.fields',
    'wtforms.validators',
    'sirope',
    'redis',
    'werkzeug',
    'jinja2',
    'email_validator',
    'dnspython',
    'uuid',
    'datetime',
    'json',
    'os',
    'sys',
    'pathlib',
    'threading',
    'webbrowser',
    'time',
]

a = Analysis(
    ['textiles_als_standalone.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyi_splash = Splash(
    'splash_image.png',  # Opcional: imagen de splash
    binaries=a.binaries,
    datas=a.datas,
    text_pos=None,
    text_size=12,
    minify_script=True,
    always_on_top=True,
)

pyi = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyi,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    pyi_splash.binaries,
    [],
    name='TextilesALS',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Comprimir el ejecutable
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Cambiar a False para ocultar consola
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',  # Opcional: icono del ejecutable
)
