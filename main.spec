# -*- mode: python ; coding: utf-8 -*-
SETUP_DIR = 'E:\\workspace\\SteelPriceVis\\'

block_cipher = None


a = Analysis(['main.py',
               SETUP_DIR+'creatWord.py',
               SETUP_DIR+'drawLine.py',
               SETUP_DIR+'fileProcessing.py',
               SETUP_DIR+'jsonTool.py',
               SETUP_DIR+'mySteelSpider.py',
               SETUP_DIR+'pricePredict.py',
               SETUP_DIR+'QtWindow.py',
               SETUP_DIR+'SmmSteelSpider.py',
               SETUP_DIR+'ZczxSteelSSpider.py',
            ],
             pathex=['E:\\workspace\\SteelPriceVis'],
             binaries=[],
             datas=[(SETUP_DIR+'files/*',SETUP_DIR+'files'),
                    (SETUP_DIR+'dataSet.json', '.'),
                    (SETUP_DIR+'setting.json', '.'),
                    (SETUP_DIR+'chromedriver.exe', '.'),
             ],
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts, 
          [],
          exclude_binaries=True,
          name='main',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas, 
               strip=False,
               upx=True,
               upx_exclude=[],
               name='main')
