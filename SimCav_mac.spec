# -*- mode: python -*-

block_cipher = None


a = Analysis(['simcav4_7_GUI.py'],
             pathex=['/home/julio/Projects/simcav'],
             binaries=[],
             datas=[('Icons/', 'Icons/')],
             hiddenimports=[],
             hookspath=['pyinstaller-hooks'],
             runtime_hooks=['pyinstaller-hooks/pyi_rth__tkinter.py'],
             excludes=[],
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
app = BUNDLE(exe,
         name='SimCav.app',
         icon='Icons/logo-tg3.ico',
         bundle_identifier=None)
