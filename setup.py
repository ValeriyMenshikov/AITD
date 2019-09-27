# coding: utf-8

from cx_Freeze import setup, Executable

import os.path
PYTHON_INSTALL_DIR = os.path.dirname(os.path.dirname(os.__file__))
os.environ['TCL_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tcl8.6')
os.environ['TK_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tk8.6')

options = {
    'build_exe': {
        'include_files':[
            os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'tk86t.dll'),
            os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'tcl86t.dll'),
         ],
    },
}


executables = [Executable('AITD.py')]

setup(name='AutoIncludeToDistribution',
      version='0.0.3',
      description='Внутренний сервис компании ЦФТ для проверки и '
                  'включения обновлений в дистрибутив. Разработчик: Меньшиков ВС',
      executables=executables)