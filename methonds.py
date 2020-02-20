import os
import re
import glob
import time
import shutil
import autoit
import keyboard
import pyperclip
import beautifultable
import cx_Oracle
from sql import sql
from colorama import init
from datetime import datetime
from colorama import Fore, Style
from read_settings import read_settings
from information_reports import message
import logging

init()
logging.basicConfig(filename='ProgramLog.txt', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

clear = lambda: os.system('cls')

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

# ===========================================WORK WITH FOLDERS===================================================


# Проверка папки источника
def check_source_folder(path_to_folder_regex):
    print(message['INFO_ABOUT_PATH'])
    path_to_folder_regex = re.compile(path_to_folder_regex, re.IGNORECASE)
    while True:
        print(YELLOW + 'УКАЖИ ПУТЬ К КАТАЛОГУ:' + RESET)
        path = path_to_folder_regex.search(input(''))
        if path:
            path = path.group()
            if os.path.exists(path):
                if len(os.listdir(path)) > 0:
                    clear()
                    return path
        print(RED + 'КАТАЛОГ НЕ СУЩЕСТВУЕТ, ЛИБО ПУСТ"' + RESET)


# Получение номера и имени разработчика в указанной папке
def split_folder_name(path):
    folder_property = re.search(r'(\d{2,3})_([a-zA-Z]+)', os.path.basename(path))
    if folder_property:  # Если имя каталога содержит нужные составляеющие то разбиваем имя папки на части
        folder_num = folder_property.group(1)
        dev_name = folder_property.group(2)
        return [folder_num, dev_name]


def show_folder_contents(path, newfolder=None):
    # Create table
    table = beautifultable.BeautifulTable()
    table.max_table_width = 120
    table.set_style(beautifultable.STYLE_RST)
    table.left_border_char = '║'
    table.right_border_char = '║'
    table.intersect_header_right = '╣'
    table.intersect_header_left = '╠'
    table.intersect_bottom_left = '╚'
    table.intersect_bottom_right = '╝'
    table.intersect_top_left = '╔'
    table.intersect_top_right = '╗'

    # Fill table
    if newfolder is not None:
        table.column_headers = [f'{YELLOW}В КАТАЛОГЕ {path} СОЗДАН:{RESET}']
        for item in os.listdir(path)[:-1]:
            table.append_row([item.ljust(116)])
        table.append_row([newfolder.ljust(116)])
        print(table)
    else:
        table.column_headers = [f'{YELLOW}СОДЕРЖИМОЕ КАТАЛОГА {path}:{RESET}']
        for item in os.listdir(path):
            table.append_row([item.ljust(116)])
        print(table)
    links_to_folder_content = glob.glob(path + r'\*')
    return links_to_folder_content


def create_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)
        return path


def create_destination_folder(path, sfolder):
    dfolder = path + '\\' + TODAY
    while True:
        if os.path.isdir(dfolder):
            files = show_folder_contents(dfolder)  # Считываем содержимое каталога
            devname = split_folder_name(sfolder)[1]
            if len(files) == 0:
                dfolder = dfolder + r'\01_' + devname
                create_folder(dfolder)
                show_folder_contents(path + '\\' + TODAY, YELLOW + '01_' + devname + RESET)
                return dfolder
            else:
                num_folders = sorted([int(split_folder_name(file)[0]) for file in files])
                next_catalog_num = f'{(num_folders[-1] + 1):02d}'
                dfolder = dfolder + '\\' + next_catalog_num + '_' + devname
                create_folder(dfolder)
                show_folder_contents(path + '\\' + TODAY, YELLOW + next_catalog_num + '_' + devname + RESET)
                return dfolder
        else:
            os.makedirs(dfolder)


# ================================================WORK WITH FILES=======================================================


# Выборочное копирование файлов из одной папки в другую в соответствием с регулярным выражением
def copy_files(sfolder, dfolder, check_regex='.*', include_directory=False):
    if include_directory:
        dfolder = os.path.join(dfolder, os.path.basename(sfolder))
    os.makedirs(dfolder, exist_ok=True)
    for file in os.listdir(sfolder):  # Генерим пути к файлам и папкам в конечном каталоге
        srcfile = os.path.join(sfolder, file)
        dstfile = os.path.join(dfolder, file)
        if re.search(check_regex, dstfile):  # Проверяем файлы на соответствие regexp
            if os.path.isdir(srcfile):  # Если это папка то используем функцию для копирования папок
                copy_files(srcfile, dstfile, check_regex)
                logging.debug(f'Копируем {file}')
            else:  # Если это файл используем функцию для копирования файлов
                shutil.copyfile(srcfile, dstfile)
                logging.debug(f'Копируем {file}')


# Проверка содержимого каталога на соответсвие регулярному выражению
def check_catalog(check_regex, folder):
    # Match table
    print(f'{YELLOW}АВТОМАТИЧЕСКАЯ ПРОВЕРКА КАТАЛОГА {folder}!{RESET}')
    table_match = beautifultable.BeautifulTable()
    table_match.column_headers = [f'{GREEN}СООТВЕТСТВУЮТ ДЛЯ ВЫКЛАДКИ:{RESET}']
    table_match.max_table_width = 120
    table_match.set_style(beautifultable.STYLE_RST)
    table_match.left_border_char = '║'
    table_match.right_border_char = '║'
    table_match.intersect_header_right = '╣'
    table_match.intersect_header_left = '╠'
    table_match.intersect_bottom_left = '╚'
    table_match.intersect_bottom_right = '╝'
    table_match.intersect_top_left = '╔'
    table_match.intersect_top_right = '╗'

    # Dont match table
    table_dont_match = beautifultable.BeautifulTable()
    table_dont_match.set_style(beautifultable.STYLE_RST)
    table_dont_match.column_headers = [f'{RED}НЕ СООТВЕТСТВУЮТ ДЛЯ ВЫКЛАДКИ:{RESET}']
    table_dont_match.max_table_width = 120
    table_dont_match.left_border_char = '║'
    table_dont_match.right_border_char = '║'
    table_dont_match.intersect_header_right = '╣'
    table_dont_match.intersect_header_left = '╠'
    table_dont_match.intersect_bottom_left = '╚'
    table_dont_match.intersect_bottom_right = '╝'
    table_dont_match.intersect_top_left = '╔'
    table_dont_match.intersect_top_right = '╗'

    # Write data to tables
    for file in os.listdir(folder):
        dstfile = os.path.join(folder, file)
        if check_regex.search(dstfile):
            table_match.append_row([f"{GREEN}{file.ljust(116, ' ')}{RESET}"])
        else:
            table_dont_match.append_row([f"{RED}{file.ljust(116, ' ')}{RESET}"])

    print(table_match)
    print(table_dont_match)


# Удаление файлов не соответствующих регулярному выражению
def delete_trash(check_regex, folder):
    for file in os.listdir(folder):
        dstfile = os.path.join(folder, file)
        if not check_regex.search(dstfile):  # Если не соответствует regexp удаляем
            if os.path.isdir(dstfile):
                shutil.rmtree(dstfile)
                logging.debug(f'Удалена папка: {file}')
            else:
                os.remove(dstfile)
                logging.debug(f'Удален файл: {file}')


# ==============================================WORK WITH FAR(CHECKER)==================================================


# Активация окна с фаром и отправка команды на запуск чекалки
def search_far_and_start(dst):
    def send_command_run():
        pyperclip.copy(f'cd {dst}')  # Копируем путь к каталогу с скопированным содержимым
        keyboard.press_and_release('ctrl+v')  # Вставляем в активное окно и переходим в каталог
        keyboard.press_and_release('enter')
        # time.sleep(0.5)
        autoit.win_activate(r"[REGEXPTITLE: Far]")
        pyperclip.copy('chk.exe')  # Копируем команду на пуск чекалки
        keyboard.press_and_release('ctrl+v')  # Вставляем и запускам
        keyboard.press_and_release('enter')

    try:  # пытаемся найти уже запущенный FAR по заголовку окна с текстом Far
        logging.debug('Проверка наличия активной копии FAR')
        autoit.win_activate(r"[REGEXPTITLE: Far]")
        send_command_run()
    except autoit.autoit.AutoItError:
        try:  # если окно не найдено, ждем 20 сек пока оно запустится
            logging.debug('Ожидание FAR по заголовку')
            autoit.win_wait_active(r"[REGEXPTITLE: Far]", 30)
            autoit.win_activate(r"[REGEXPTITLE: Far]")  # активировать окно перед запуском чекалки
            send_command_run()
        except autoit.autoit.AutoItError:
            logging.critical(f'''Активный FAR не найден
            ЗАПУСТИТЬ ЧЕКАЛКУ НЕ УДАЛОСЬ, ЗАПУСТИ В РУЧНУЮ.
            ПУТЬ К КАТАЛОГУ: {dst}
            ДОЖДИСЬ ОКОНЧАНИЯ ПРОВЕРКИ И НАЖМИ ЛЮБУЮ КЛАВИШУ.''')
            os.system("pause")


# Запуск чекалки
def run_check(dst, remote, far, password):
    if remote == '1':
        try:  # проверяем есть ли запущенный фар и отправляем команду на чек
            autoit.win_activate(r"[REGEXPTITLE: Far]")
            search_far_and_start(dst)
        except autoit.autoit.AutoItError:  # если нет, запускаем фар, авторизуемся и отправляем команду на пуск чекалки
            os.popen(far)
            try:
                autoit.win_wait_active("Безопасность Windows", 30)
                time.sleep(1)
                keyboard.write(f"{password}\n", delay=0)
            except autoit.autoit.AutoItError:  # Если запущено еще одно приложение и уже не нужна авторизация
                pass
            search_far_and_start(dst)
    else:  # Если комп не удаленный то блок с авторизацией отсутствует
        try:
            autoit.run(far)
            search_far_and_start(dst)
        except autoit.autoit.AutoItError:
            logging.critical('ПРОВЕРЬ НАСТРОЙКИ ВОЗМОЖНО НЕПРАВИЛЬНО УКАЗАН ПУТЬ К FAR')


# Ожидание формирования лога чекалки и его вывод
def waiting_checker_log(address_where_log):
    address_for_waiting_log = address_where_log + '\\ChkInfo.xml'
    address_where_log = address_where_log + '\\chkerr.log'

    # Create log table
    table = beautifultable.BeautifulTable()
    table.set_style(beautifultable.STYLE_RST)
    table.column_headers = [f'{YELLOW}РЕЗУЛЬТАТ ПРОВЕРКИ ЧЕКАЛКИ chkerr.log:{RESET}']
    table.column_alignments[f'{YELLOW}РЕЗУЛЬТАТ ПРОВЕРКИ ЧЕКАЛКИ chkerr.log:{RESET}'] = beautifultable.ALIGN_LEFT
    table.max_table_width = 120
    table.left_border_char = '║'
    table.right_border_char = '║'
    table.intersect_header_right = '╣'
    table.intersect_header_left = '╠'
    table.intersect_bottom_left = '╚'
    table.intersect_bottom_right = '╝'
    table.intersect_top_left = '╔'
    table.intersect_top_right = '╗'

    timer = 0
    while True:  # Таймер принудительного выхода из цикла если не дождались лога

        if timer >= 300:
            print(f'{RED}Лог проверки не сформирован проверьте работоспособность чекалки!{RESET}')
            break
        if os.path.isfile(address_for_waiting_log):
            # Ожидаем пока сформируется файл, который появляется позже лога
            # Как только этот файл сформирован, так как он последний, то к тому времени лог уже готов. И мы его читаем.
            if os.path.isfile(address_where_log):
                time.sleep(2)
                with open(address_where_log) as log:  # Выводим содержимое лога на экран
                    num_rows = []
                    for line in log:
                        table.append_row([line.ljust(116, ' ')])
                        num_rows += line
                        if re.search(r'.*\.pck\sЗапрос\sна\sизменение.*не\sзакрыта\s.*\)', line) and len(num_rows) <= 1:
                            autocheck = True
                        else:
                            autocheck = False
                    print(table)
                    return autocheck
        else:
            time.sleep(1)
            timer += 1
            continue


# =====================================================CHECKS======================================================

# Простая проверка в зависимости от сообщения
def easy_check(msg):
    while True:
        print(msg)
        check = input('Y\\N: ')
        if check in ['N', 'n', 'Т', 'т']:
            print(RED + 'ИСПРАВЬ ЗАМЕЧАНИЯ И ПОПРОБУЙ СНОВА!'.center(120, ' ') + RESET)
            continue
        elif check in ['auto', 'AUTO', '!']:
            print(RED + 'ВЫБРАН АВТОМАТИЧЕСКИЙ РЕЖИМ'.center(120, ' ') + RESET)
            print(
                RED + '!!!!!!!!!ВНИМАНИЕ ВСЕ ПРОВЕРКИ ЗА ИСКЛЮЧЕНИЕМ ЧЕКАЛКИ БУДУТ СЧИТАТЬСЯ ПРОЙДЕННЫМИ!!!!!!!!!'.center(
                    120, ' ') + RESET)
            return 'AUTO'
        else:
            break


# Проверка с копированием и повторным запуском чекалки
def check_with_checker(msg, check_regex, source_folder, destination_folder):
    while True:
        print(msg)
        if input('Y\\N: ') in ['N', 'n', 'Т', 'т']:
            print(f'{YELLOW}СКОПИРОВАТЬ КАТАЛОГ ПОВТОРНО?{RESET}')
            if input('Y\\N: ') in ['N', 'n', 'Т', 'т']:
                continue
            else:
                delete_trash(check_regex, destination_folder)  # Удаляем старый лог и лишние файлы
                copy_all_or_not(source_folder, destination_folder, check_regex, 1)
                print(f'{GREEN}ФАЙЛЫ УСПЕШНО СКОПИРОВАНЫ!{RESET}')
                show_folder_contents(destination_folder)  # Просматриваем содержимое
                search_far_and_start(destination_folder)  # Запускаем чекалку в уже запущенном FAR
                waiting_checker_log(destination_folder)  # Ждем появления лога
        else:
            break


# Копируем все содержимое или в соответсвтвии с регулярным выражением
def copy_all_or_not(source_folder, destination_folder, check_regex, print_report=0):
    all_not = str(input('Y\\N: '))
    if print_report == 1:
        print(RED + "НИЧЕГО НЕ ТРОГАЙ ДО ТЕХ ПОР ПОКА НЕ ЗАПУСТИТСЯ ЧЕКАЛКА!" + RESET)
    if all_not in ['N', 'n', 'Т', 'т']:
        print('Копируем все файлы: ')
        copy_files(source_folder, destination_folder)
    else:
        print('Копируем файлы по результатам авто проверки: ')
        copy_files(source_folder, destination_folder, check_regex)


# =============================================WORK WITH DATABASE======================================================

# Поиск в файле pck номера заявки
def get_task_num_from_pck(source_folder, task_regex):
    regex = re.compile(r'ibsobj\d{0,2}?\.pck')
    if regex.search(str(os.listdir(source_folder))):
        with open(os.path.join(source_folder, regex.search(str(os.listdir(source_folder))).group())) as pck:
            rp = re.search(task_regex, pck.read())
            if rp is not None:
                return rp.group()
            else:
                print(RED + 'В ФАЙЛЕ .PCK ОТСУТСТВУЕТ НОМЕР ЗАЯВКИ ЛИБО УКАЗАН НЕПРАВИЛЬНО' + RESET)
    else:
        print(RED + 'НЕ НАЙДЕН ФАЙЛ .PCK' + RESET)


def get_task_information(RP, database):
    if RP:
        tasks = sql['TASKS'] + f"'{RP}'" + '\norder by t.c_priority'
        problem_description = sql['PROBLEM_DESCRIPTION'] + f"'{RP}'"
        task_type = sql['TASK_TYPE'] + f"'{RP}'"
        try:
            with cx_Oracle.connect(database) as connection:
                tasks = connection.cursor().execute(tasks).fetchall()
                description = connection.cursor().execute(problem_description).fetchall()
                task_type = connection.cursor().execute(task_type).fetchall()[0][0]
            return tasks, description, task_type
        except cx_Oracle.DatabaseError as err:
            logging.debug(RED + 'Ошибка при работе с базой данных!' + RESET)
            logging.debug(RED + err + RESET)
            return False
    else:
        logging.debug(RED + 'Так как не был найден номер заявки, подключаться к базе не будем' + RESET)


# Вывод задач по заявке в соответствии с запросом полученным в sql_query()
def print_task_table(tasks):
    if len(tasks) > 0:
        table = beautifultable.BeautifulTable()
        table.max_table_width = 120
        table.column_headers = ['Приоритет', 'Задача', 'Название', 'Исполнитель', 'Статус']
        table.column_alignments['Название'] = beautifultable.ALIGN_LEFT
        table.column_alignments['Исполнитель'] = beautifultable.ALIGN_LEFT
        table.column_alignments['Статус'] = beautifultable.ALIGN_LEFT
        table.width_exceed_policy = beautifultable.WEP_ELLIPSIS
        table.set_style(beautifultable.STYLE_BOX_DOUBLED)

        for i in tasks:
            table.append_row(i)
        print(table)
    else:
        logging.debug(RED + 'Не удалось получить информацию по заявке' + RESET)


# Вывод public info по заявке в соответствии с запросом полученным
def print_description(task):
    try:
        table = beautifultable.BeautifulTable()
        table.column_headers = [f'{RED}ОПИСАНИЕ ПРОБЛЕМЫ:{Style.RESET_ALL}', f'{GREEN}РЕАЛИЗАЦИЯ:{Style.RESET_ALL}']
        for i in task:
            table.append_row(i)
        table.max_table_width = 120
        table.set_style(beautifultable.STYLE_BOX_DOUBLED)
        print(table)
    except IndexError:
        logging.debug(RED + 'Не удалось получить информацию по заявке' + RESET)
