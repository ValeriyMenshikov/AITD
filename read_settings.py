import os
from colorama import init
from colorama import Fore, Style

init()

RED = Fore.LIGHTRED_EX
GREEN = Fore.LIGHTGREEN_EX
YELLOW = Fore.LIGHTYELLOW_EX
RESET = Style.RESET_ALL

file = 'my_tuning.txt'


# Чтение файла настроек
def read_settings():
    setting = {}
    with open(file, 'r', encoding='windows-1251') as read_settings:
        try:
            for line in read_settings:
                (key, value) = line.split('=')
                setting[key] = value.strip()
        except (ValueError, KeyError):
            print(f'''{RED}ПРЕДНАСТРОЙКА БЫЛА ВЫПОЛНЕНА НЕКОРРЕКТНО,
ВОЗМОЖНО БЫЛИ ЗАПОЛНЕНЫ НЕ ВСЕ ПОЛЯ, ПЕРЕЗАПУСТИ ПРОГРАММУ{RESET}''')
            open(file, 'w')  # Таким образом зачищаем содержимое файла настроек
    if setting == {}:
        raise FileNotFoundError
    return setting


# Опрос и формирование файла настроек
def precondition():
    try:  # Пытаемся считать настройки если они есть
        read_settings()
    except FileNotFoundError:  # Если настроек нет Формируем файл конфигурации
        print(f'''{YELLOW}СЕЙЧАС БУДЕМ ПРОВОДИТЬ ПРЕДВАРИТЕЛЬНУЮ НАСТРОЙКУ,
НАСТРОЙКИ ВСЕГДА МОЖНО ИЗМЕНИТЬ В ФАЙЛЕ MY_TUNING.TXT{RESET}\n''')
        os.system("pause")
        while True:
            print(f'{YELLOW}ЯРКОСТЬ ТЕМНЕЕ, ЯРЧЕ? 1-без изменений, 0-темнее: {RESET}')
            COLOR = str(input())
            if COLOR == '1' or COLOR == '0':
                break
        while True:
            print(f'{YELLOW}ЗАПУСКАЕШЬ FAR ЧЕРЕЗ ПЕРСЕЙ? 1-да, 0-нет: {RESET}')
            REMOTE = str(input())
            if REMOTE == '1' or REMOTE == '0':
                break
        while True:
            print(f'{YELLOW}УКАЖИ ПУТЬ К FAR: {RESET}')
            FAR = str(input())
            if FAR:
                break
        while True:
            print(f'{YELLOW}ПАРОЛЬ К УЧЕТНОЙ ЗАПИСИ: {RESET}')
            PASSWORD = str(input())
            if PASSWORD:
                break
        with open(file, 'w', encoding='windows-1251') as write_settings:
            write_settings.write(
                f'COLOR= {COLOR}\n'
                f'REMOTE= {REMOTE}\n'
                f'FAR= {FAR}\n'
                f'PASSWORD= {PASSWORD}\n'
                r'DESTINATION_FOLDER_FOR_CHECK= \\pumba\BFT\СХЕМЫ\DISTRIB\57_DEV_IBS\REPS\DISTRIB\57_DISTR_IBS'+'\n'
                r'DESTINATION_FOLDER_FOR_DISTR= \\pumba\BFT\СХЕМЫ\DISTRIB\57_DISTR_IBS'+'\n'
                r'PATH_REQUIREMENTS= \\PUMBA\BFT\СХЕМЫ\DISTRIB\57_DEV_IBS\REPS\ГГГГ_ММ_ММ\НОМЕР_ФАМИЛИЯ'+'\n'
                r'PATH_EXAMPLE= \\PUMBA\BFT\СХЕМЫ\DISTRIB\57_DEV_IBS\REPS\2019_08_14\01_ivanov'+'\n'
                'DATABASE= ibs/ibs@ATM_SBDEV\n'
                r'CHECK_CONTENT_REGEX= (ibsobj\d{0,2}?\.mdb)|'                    # ibsobj.mdb
                r'(ibsobj\d{0,2}?\.pck)|'                                         # ibsobj.pck
                r'(delete\d{0,2}?\.pck)|'                                         # delete.pck
                r'(Ин.*я\sпо\sу.*е\.txt)|'                                        # Инструкция по установке.txt
                r'(О.*е\sо.*й\sк.*и\.xls[x]?)|'                                   # Описание операций конвертации.xls
                r'(REPORT[S]?)|'                                                  # REPORTS
                r'(SCRIPT[S]?)|'                                                  # SCRIPTS
                r'(DATA)|'                                                        # DATA
                r'(dr\.bat)|'                                                     # dr.bat
                r'(.*r.*me\.txt)|'                                                # readme.txt 
                r'(.*н.*е\sво.*ти.*\.doc[x]?)|'                                   # Новые возможности.doc
                r'(.*н.*е\sра.*я.*\.xls[x]?)|'                                    # Новые расширения.xls
                r'(.*кл.*я\sсп.*в.*\.xls[x]?)|'                                   # Классификация справочников.xls
                r'([\'|\"]?del[_|\s]old[_|\s]reps[_|\s]\d{8}[\'|\"]?\.bat)'+'\n'  # del_old_reps_YYYYMMDD.bat
                r'NUMBER_REQUEST_REGEX= RP\d{7}'+'\n'                             # Номер заявки RP{7 цифр}
                r'CHECK_SOURCE_FOLDER_PATH_REGEX= \\\\pumba\\bft\\СХЕМЫ\\DISTRIB\\57_DEV_IBS\\REPS\\\d{4}_\d{2}_\d{2}\\\d{2}_[a-zA-Z]+'
                )
    return read_settings()