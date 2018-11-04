# -*- mode: python -*-
import sys
sys.setrecursionlimit(5000)

block_cipher = None

a = Analysis(['simcav_main.py'],
             pathex=[],
             binaries=[],
             datas=[('Icons/', 'Icons/')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=['_gtkagg', 'PyQt4', 'PyQt5', 'PySide', 'pandas', 'sqlalchemy', 'sqlite3'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='SimCav',
          debug=False,
          strip=False,
          upx=True,
          icon='Icons/logo-tg3.ico',
          console=False )