import subprocess
from methonds import *
from colorama import init
from datetime import datetime
from colorama import Fore, Style
from read_settings import read_settings
from information_reports import message
import logging

init()
logging.basicConfig(filename='ProgramLog.txt', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

clear = lambda: os.system('cls')
# hwnd = win32gui.GetForegroundWindow()
# win32gui.MoveWindow(hwnd, 200, 200, 1010, 600, True)
# file = 'my_tuning.json'

settings = read_settings('my_tuning.json')

if settings['COLOR']['bright'] == '1':
    RED = Fore.LIGHTRED_EX
    GREEN = Fore.LIGHTGREEN_EX
    YELLOW = Fore.LIGHTYELLOW_EX
else:
    RED = Fore.RED
    GREEN = Fore.GREEN
    YELLOW = Fore.YELLOW
RESET = Style.RESET_ALL

TODAY = datetime.today().strftime('%Y_%m_%d')

# Init variables
far = settings['FAR']['path']
remote = settings['REMOTE']['remote']
password = settings['PASSWORD']['password']
task_regex = settings['TASK_NUM_REGEX']['regex']
check_path_regex = settings['CHECK_PATH_REGEX']['regex']

database = settings['DATABASE']['database']
destination_folder = settings['FOLDER_FOR_CHECK']['path']
destination_folder_distr = settings['FOLDER_FOR_DISTR']['path']
check_regex = re.compile('|'.join(list(settings['CHECK_CONTENT_REGEX'].values())[::2]), re.IGNORECASE | re.VERBOSE)

# TODO Основной цикл

while True:
    try:
        # Проверка пути на соответствие формату
        source_folder = check_source_folder(check_path_regex)
        # Автоматический режим выкладки
        if easy_check(message['CHECK1']) == 'AUTO':
            try:
                rp = get_task_num_from_pck(source_folder, task_regex)
                task, description, task_type = get_task_information(rp, database)
                print_description(description)
                print_task_table(task)
            except BaseException as err:
                logging.debug(RED + 'Не удалось получить информацию из базы данных' + RESET)
                logging.debug(RED + err + RESET)
            check_catalog(check_regex, source_folder)
            dst = create_destination_folder(destination_folder, source_folder)
            copy_files(source_folder, dst, check_regex)
            run_check(dst, remote, far, password)
            if waiting_checker_log(dst):
                dst_distr = create_destination_folder(destination_folder_distr, source_folder)
                copy_files(source_folder, dst_distr, check_regex)
                print(message['CONGRATULATION'])
                time.sleep(3)
                subprocess.Popen(f'explorer "{dst_distr}"')
            else:
                # Удаление ранее скопированной папки если чекалка не прошла
                autoit.win_activate(r"[REGEXPTITLE: Far]")
                pyperclip.copy(f'cd {destination_folder}\\{TODAY}')
                keyboard.press_and_release('ctrl+v')
                keyboard.press_and_release('enter')
                shutil.rmtree(dst, ignore_errors=True)
                logging.debug(RED + f'Папка {dst} удалена' + RESET)

                print(f'{RED}ПРОВЕРКА ЧЕКАЛКОЙ НЕ ПРОШЛА, ДАВАЙ ЗАНОВО!{RESET}')
        # Ручной режим выкладки
        else:
            clear()
            print(message['CHECK2'])
            check_catalog(check_regex, source_folder)
            easy_check(message['CHECK3'])
            try:
                rp = get_task_num_from_pck(source_folder, task_regex)
                task, description, task_type = get_task_information(rp, database)
                print_description(description)
                if task or description or task_type:
                    if 'Дефект' == task_type:
                        easy_check(message['CHECK4_defect'])
                        easy_check(message['CHECK5'])
                    elif 'Доработка' == task_type:
                        easy_check(message['CHECK4_rework'])
                    if re.search('Документирование', str(task)):
                        easy_check(message['CHECK6'])
                    print_task_table(task)
            except BaseException as err:
                print(RED + 'Не удалось получить информацию из базы данных' + RESET)
                print(RED + err + RESET)
                easy_check(message['CHECK4_rework'])
                easy_check(message['CHECK5'])
                easy_check(message['CHECK6'])
            easy_check(message['CHECK7'])
            easy_check(message['CHECK8'])

            # Формируем destination каталог
            dst = create_destination_folder(destination_folder, source_folder)
            print(message['CHECK9'])
            copy_all_or_not(source_folder, dst, check_regex, 1)

            # Копирование файлов и просмотр того что скопировали
            print(f'{GREEN}ФАЙЛЫ УСПЕШНО СКОПИРОВАНЫ!{RESET}')
            show_folder_contents(dst)

            # Запуск чекалки и ожидание ее лога
            run_check(dst, remote, far, password)
            waiting_checker_log(dst)

            # Проверка с возможностью скопировать каталог заново
            check_with_checker(message['CHECK10'], check_regex, source_folder, dst)
            clear()

            # Формируем destination каталог на дистре и копируем файлы
            dst_distr = create_destination_folder(destination_folder_distr, source_folder)
            copy_all_or_not(source_folder, dst_distr, check_regex, 0)
            print(f'{GREEN}ФАЙЛЫ УСПЕШНО СКОПИРОВАНЫ!{RESET}\n')

            # Все операции закончены открываем итоговый каталог
            print(message['CONGRATULATION'])
            time.sleep(3)
            subprocess.Popen(f'explorer "{dst_distr}"')
        print('ДЛЯ ВЫКЛАДКИ СДЕЛУЮЩЕГО КАТАЛОГА НАЖМИ ЛЮБУЮ КЛАВИШУ')
        print('ДЛЯ ВЫХОДА НАЖМИ "N"')

        if input('Y\\N:') in ['N', 'n', 'Т', 'т']:
            break
        else:
            clear()
    except BaseException as err:
        logging.debug(err)
