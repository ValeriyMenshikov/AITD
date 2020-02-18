import os
from colorama import init
from colorama import Fore, Style
import json

init()

RED = Fore.LIGHTRED_EX
GREEN = Fore.LIGHTGREEN_EX
YELLOW = Fore.LIGHTYELLOW_EX
RESET = Style.RESET_ALL


def read_settings(file):
    while True:
        if os.path.isfile(file):
            with open(file) as set:
                return json.load(set)
        else:
            print(f'''{YELLOW}СЕЙЧАС БУДЕМ ПРОВОДИТЬ ПРЕДВАРИТЕЛЬНУЮ НАСТРОЙКУ,
            НАСТРОЙКИ ВСЕГДА МОЖНО ИЗМЕНИТЬ В ФАЙЛЕ MY_TUNING.JSON{RESET}\n''')
            os.system("pause")
            while True:
                print(f'{YELLOW}ЯРКОСТЬ 1-без изменений, 0-темнее: {RESET}')
                color = str(input())
                if color == '1' or color == '0':
                    break
                else:
                    print(f'{RED}Значение должно быть равно 0 или 1!{RESET}')
            while True:
                print(f'{YELLOW}ЗАПУСКАЕШЬ far ЧЕРЕЗ ПЕРСЕЙ? 1-да, 0-нет: {RESET}')
                remote = str(input())
                if remote == '1' or remote == '0':
                    break
                else:
                    print(f'{RED}Значение должно быть равно 0 или 1!{RESET}')
            while True:
                print(f'{YELLOW}ПАРОЛЬ К УЧЕТНОЙ ЗАПИСИ: {RESET}')
                password = str(input())
                if password:
                    break
                else:
                    print(f'{RED}Пароль к учетной записи не указан!{RESET}')
            while True:
                print(f'{YELLOW}УКАЖИ ПУТЬ К far: {RESET}')
                far = str(input())
                if far is not None:
                    break
                else:
                    print(f'{RED}Путь к фар не был указан!{RESET}')

            with open(file, 'w', encoding='windows-1251') as f:
                tunings = {
                    'COLOR': {
                        'bright': f'{color}', 'info': 'Яркость меню, 1 ярче, 0 темнее'
                    },
                    'REMOTE': {
                        'remote': f'{remote}', 'info': 'Локально установлена чекалка или через персей'
                    },
                    'PASSWORD': {
                        'password': f'{password}', 'info': 'Локально установлена чекалка или через персей'
                    },
                    'FAR': {
                        'path': f'{far}',
                        'info': 'Сдесь необходимо указать путь к FAR'
                    },
                    'FOLDER_FOR_CHECK': {
                        'path': r'\\pumba\BFT\СХЕМЫ\DISTRIB\57_DEV_IBS\REPS\DISTRIB\57_DISTR_IBS',
                        'info': 'Путь куда будет копироваться каталог для проверки чекалкой'
                    },
                    'FOLDER_FOR_DISTR': {
                        'path': r'\\pumba\BFT\СХЕМЫ\DISTRIB\57_DISTR_IBS',
                        'info': 'Путь к папке с дистрибутивом'
                    },
                    'PATH_REQUIREMENTS': {
                        'path': r'\\PUMBA\BFT\СХЕМЫ\DISTRIB\57_DEV_IBS\REPS\ГГГГ_ММ_ММ\НОМЕР_ФАМИЛИЯ',
                        'info': 'Как должен выглядеть путь к выкладываемому каталогу, эта надпись выводится на экран'
                    },
                    'PATH_EXAMPLE': {
                        'path': r'\\PUMBA\BFT\СХЕМЫ\DISTRIB\57_DEV_IBS\REPS\2019_08_14\01_ivanov',
                        'info': 'Образец как должен выглядеть путь к выкладываемому каталогу, надпись выводится на экран'
                    },
                    'DATABASE': {
                        'database': 'ibs/ibs@57_DEV',
                        'info': 'Указывается схема АТМ откуда будет тянуться описание заявки'
                    },
                    'CHECK_CONTENT_REGEX': {
                        'ibsobj.mdb': r'(ibsobj\d{0,2}?\.mdb)',
                        'info1': 'Регулярка для ibsobj.mdb',

                        'ibsobj.pck': r'(ibsobj\d{0,2}?\.pck)',
                        'info2': 'Регулярка для ibsobj.pck',

                        'delete.pck': r'(delete\d{0,2}?\.pck)',
                        'info3': 'Регулярка для delete.pck',

                        'conv_instruction': r'(Ин.*я\sпо\sу.*е\.txt)',
                        'info4': 'Регулярка для Инструкция по установке.txt',

                        'conv_description': r'(О.*е\sо.*й\sк.*и\.xls[x]?)',
                        'info5': 'Регулярка для Описание операций конвертации.xls',

                        'reports_folder': r'(REPORT[S]?)',
                        'info6': 'Регулярка для REPORTS',

                        'scripts_folder': r'(SCRIPT[S]?)',
                        'info7': 'Регулярка для SCRIPTS',

                        'data_folder': r'(DATA)',
                        'info8': 'Регулярка для DATA',

                        'bat_file': r'(dr\.bat)',
                        'info9': 'Регулярка для dr.bat',

                        'readme': r'(.*r.*me\.txt)',
                        'info10': 'Регулярка для readme.txt',

                        'new_opportunities': r'(.*н.*е\sво.*ти.*\.doc[x]?)',
                        'info11': 'Регулярка для Новые возможности.doc',

                        'new_extensions': r'(.*н.*е\sра.*я.*\.xls[x]?)',
                        'info12': 'Регулярка для Новые расширения.xls',

                        'classification': r'(.*кл.*я\sсп.*в.*\.xls[x]?)',
                        'info13': 'Регулярка для Классификация справочников.xls',

                        'bat': r'([\'|\"]?del[_|\s]old[_|\s]reps[_|\s]\d{8}[\'|\"]?\.bat)',
                        'info14': 'Регулярка для del_old_reps_YYYYMMDD.bat',
                    },
                    'TASK_NUM_REGEX': {
                        'regex': r'RP\d{7}',
                        'info': 'Регулярка для поиска номера заявки',
                    },
                    'CHECK_PATH_REGEX': {
                        'regex': r'\\\\pumba\\bft\\СХЕМЫ\\DISTRIB\\57_DEV_IBS\\REPS\\\d{4}_\d{2}_\d{2}\\\d{2}_[a-zA-Z]+',
                        'info': 'Регулярка для проверки пути к каталогу',
                    }
                }
                f.write(json.dumps(tunings, indent=2, ensure_ascii=False))
