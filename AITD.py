import os
import re
import glob
import time
import shutil
import autoit
import win32gui
import keyboard
import pyperclip
import pyautogui
import subprocess
import beautifultable
import cx_Oracle
from colorama import init
from datetime import datetime
from colorama import Fore, Style
from read_settings import precondition
from InformationReports import report, InfoReports, Checks

init()

clear = lambda: os.system('cls')
hwnd = win32gui.GetForegroundWindow()
win32gui.MoveWindow(hwnd, 200, 200, 1010, 600, True)

settings = precondition()

if settings['COLOR'] == '1':
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
def check_source_folder():
    report(InfoReports.INFO_ABOUT_PATH, color=YELLOW)
    path_to_folder_regex = re.compile(settings['CHECK_SOURCE_FOLDER_PATH_REGEX'], re.IGNORECASE)
    while True:
        report(InfoReports.CHANGE_CATALOG, color=YELLOW)
        path_to_folder = input('')
        if path_to_folder_regex.search(path_to_folder):  # Если путь соответствует формату пересохраняем его
            path_to_folder = path_to_folder_regex.search(path_to_folder).group()
            try:  # Проверяем существование каталога и содержит каталог файлы и папки или нет
                if len(os.listdir(path_to_folder)) > 0:
                    break
                else:  # Выводим сообщение если каталог пуст и пробуем заново
                    report(InfoReports.NO_CONTENT_IN_FOLDER, path_to_folder, color=RED)
                    continue
            except FileNotFoundError:  # Выводим сообщение если каталога не существует и пробуем заново
                report(InfoReports.FOLDER_NOT_EXIST, path_to_folder, color=RED)
                continue
        else:  # Выводим сообщение если путь не существует формату и пробуем заново
            report(InfoReports.PATH_NOT_CORRECT, color=RED)
    return path_to_folder


# Получение номера и имени разработчика в указанной папке
def parsing_path_to_folder(path_to_folder):
    number_name_developer = re.search(r'(\d{2,3})_([a-zA-Z]+)', os.path.basename(path_to_folder))
    if number_name_developer:  # Если имя каталога содержит нужные составляеющие то разбиваем имя папки на части
        number_folder = number_name_developer.group(1)
        name_dev = number_name_developer.group(2)
        return number_folder, name_dev
    else:
        print(f'{RED}КАТАЛОГ {path_to_folder}\nНЕ СООТВЕТСТВУЕТ ФОРМАТУ NN_ФАМИЛИЯ РАЗРАБОТЧИКА!{RESET}')


# Отобразить содержимое каталога
def show_folder_contents(name_folder):
    report(InfoReports.FOLDER_CONTENT, name_folder, color=YELLOW)
    print('╔'+''.center(118, '=') + '╗')
    for item in os.listdir(name_folder):  # Просто просматриваем содержимое каталога
        print('║ ' + str(item).ljust(117, '.') + '║')
    print('╚'+ ''.center(118, '=') + '╝')
    links_to_folder_contents = glob.glob(f'{name_folder}\\*')
    return links_to_folder_contents


# Создать папку назначения
def create_destination_folder(destination_folder, source_folder):
    links = show_folder_contents(destination_folder)  # Считываем содержимое каталога
    if len(links) == 0:  # Если каталог пуст то создаем папку с номером 01_имя разработчика
        report(InfoReports.NO_CONTENT_IN_FOLDER, TODAY, color=YELLOW)
        num, dev = parsing_path_to_folder(source_folder)
        destination_folder = f'{destination_folder}\\01_{dev}'
        report(InfoReports.CREATE_FOLDER, f'01_{dev}', color=YELLOW)
        os.makedirs(destination_folder)
        report(InfoReports.FOLDER_CREATED, f'01_{dev}', color=GREEN)
    else:  # Если каталог содержит более одной папки
        num_folders = []
        for i in links:  # Считываем все номера папок
            try:
                num, dev = parsing_path_to_folder(i)
                num_folders += [int(num)]
            except TypeError:
                # Если у каталога имя папки без номера пропустить
                pass
        # Формируем порядковый номер следующего по счету каталога, для этого
        # к последнему в списке номеру добавляем единицу и приводим к формату двух знаков
        num_next_catalog = f'{(num_folders[-1] + 1):02d}'
        # Парсим путь источника
        num, dev = parsing_path_to_folder(source_folder)
        # Формируем имя следующего по счету каталога, где соединяем путь с новым порядковым номером и фамилией
        destination_folder = f'{destination_folder}\\{num_next_catalog}_{dev}'
        report(InfoReports.CREATE_FOLDER, f'{num_next_catalog}_{dev}', color=YELLOW)
        try:  # Создаем новый каталог с сгенерированным именем
            os.makedirs(destination_folder)
            report(InfoReports.FOLDER_CREATED, f'{num_next_catalog}_{dev}', color=GREEN)
        except FileExistsError:
            print('Такое случается если количество каталогов в папке перевалило за сотню')
            print('Дальше работать не будет')
    return destination_folder


# Создать папку с текущей датой
def create_today_folder(destination_folder, source_folder):
    destination_folder = f'{destination_folder}\\{TODAY}'
    if os.path.isdir(destination_folder):  # Проверяем наличие каталога с текущей датой и генерим конечный каталог
        report(InfoReports.FOLDER_EXIST, TODAY, color=GREEN)
        report(InfoReports.CHECK_FOLDER_CONTENT, TODAY, color=YELLOW)
        dst = create_destination_folder(destination_folder, source_folder)
    else:  # Если каталога с текущей датой нет, то создаем и генерим конечный каталог
        report(InfoReports.FOLDER_NOT_EXIST, TODAY, color=RED)
        report(InfoReports.CREATE_FOLDER, TODAY, color=YELLOW)
        os.makedirs(destination_folder)
        report(InfoReports.FOLDER_CREATED, TODAY, color=GREEN)
        dst = create_destination_folder(destination_folder, source_folder)
    return dst


# ================================================WORK WITH FILES=======================================================

check_regex = re.compile(settings['CHECK_CONTENT_REGEX'], re.IGNORECASE | re.VERBOSE)


# Выборочное копирование файлов из одной папки в другую в соответствием с регулярным выражением
def copy_files(source_folder, destination_folder, check_regex=re.compile('.*'), include_directory=False):
    if include_directory:
        destination_folder = os.path.join(destination_folder, os.path.basename(source_folder))
    os.makedirs(destination_folder, exist_ok=True)
    # tag each file to the source path to create the file path
    for file in os.listdir(source_folder):  # Генерим пути к файлам и папкам в конечном каталоге
        srcfile = os.path.join(source_folder, file)
        dstfile = os.path.join(destination_folder, file)
        if check_regex.search(dstfile):  # Проверяем файлы на соответствие regexp
            if os.path.isdir(srcfile):  # Если это папка то используем функцию для копирования папок
                copy_files(srcfile, dstfile, check_regex)
                print(f'Копируем {file}')
            else:  # Если это файл используем функцию для копирования файлов
                shutil.copyfile(srcfile, dstfile)
                print(f'Копируем {file}')
        else:  # Если не соответствует, пропускаем
            pass
            # print(f'Файл {file} не соответствует требованиям ОПД')


# Проверка содержимого каталога на соответсвие регулярному выражению
def check_catalog(check_regex, folder):
    print(f'{YELLOW}АВТОМАТИЧЕСКАЯ ПРОВЕРКА КАТАЛОГА {folder}!{RESET}')
    match_flag = True
    match = []
    dont_match = []
    for file in os.listdir(folder):  # Считываем содержимое папки
        dstfile = os.path.join(folder, file)
        if check_regex.search(dstfile):  # Если соответствует regexp то добавляем в массив соответствующих
            match.append(f'{GREEN}{file}{RESET}')
        else:  # Если нет то добавляем в массив не соответствующих
            dont_match.append(f'{RED}{file}{RESET}')
            match_flag = False
    print(f'{GREEN}СООТВЕТСТВУЮТ ДЛЯ ВЫКЛАДКИ:{RESET}')
    print('╔' + ''.center(118, '=') + '╗')
    for i in match:
        print('║ ' + i.ljust(126, '.') + '║')
    print('╚' + ''.center(118, '=') + '╝')
    print(f'\n{RED}НЕ СООТВЕТСТВУЮТ ДЛЯ ВЫКЛАДКИ:{RESET}')
    print('╔' + ''.center(118, '=') + '╗')
    for j in dont_match:
        print('║ ' + j.ljust(126, '.') + '║')
    print('╚' + ''.center(118, '=') + '╝')
    if match_flag:
        print(f'{GREEN}СОДЕРЖИМОЕ КАТАЛОГА СООТВЕТСТВУЕТ ТРЕБОВАНИЯМ ВЫКЛАДКИ')
        return True
    else:
        print(f'{YELLOW}НЕ СООТВЕТСТВУЮЩИЕ ФАЙЛЫ НЕ БУДУТ КОПИРОВАТЬСЯ!{RESET}')
        return False


# Удаление файлов не соответствующих регулярному выражению
def delete_trash(check_regex, folder):
    for file in os.listdir(folder):   # Считываем содержимое
        dstfile = os.path.join(folder, file)
        if not check_regex.search(dstfile):  # Если не соответствует regexp удаляем
            if os.path.isdir(dstfile):
                shutil.rmtree(dstfile)
                print(f'{RED}Удалена папка: {file}')
            else:
                os.remove(dstfile)
                print(f'{RED}Удален файл: {file}')
        else:  # Иначе пропускаем
            pass

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
        print('Проверка наличия активной копии FAR')
        autoit.win_activate(r"[REGEXPTITLE: Far]")
        send_command_run()
    except autoit.autoit.AutoItError:
        try:  # если окно не найдено, ждем 20 сек пока оно запустится
            print('Ожидание FAR по заголовку')
            autoit.win_wait_active(r"[REGEXPTITLE: Far]", 30)
            autoit.win_activate(r"[REGEXPTITLE: Far]")  # активировать окно перед запуском чекалки
            send_command_run()
        except autoit.autoit.AutoItError:
            print('Активный FAR не найден')
            print(f'{RED}ЗАПУСТИТЬ ЧЕКАЛКУ НЕ УДАЛОСЬ, ЗАПУСТИ В РУЧНУЮ.{RESET}')
            print(f'{YELLOW}ПУТЬ К КАТАЛОГУ: {dst}')
            print(f'{YELLOW}ДОЖДИСЬ ОКОНЧАНИЯ ПРОВЕРКИ И НАЖМИ ЛЮБУЮ КЛАВИШУ.{RESET}')
            os.system("pause")


# Запуск чекалки
def run_check(dst):
    if settings['REMOTE'] == '1':
        try:  # проверяем есть ли запущенный фар и отправляем команду на чек
            autoit.win_activate(r"[REGEXPTITLE: Far]")
            search_far_and_start(dst)
        except autoit.autoit.AutoItError:  # если нет, запускаем фар, авторизуемся и отправляем команду на пуск чекалки
            os.popen(settings['FAR'])
            autoit.win_wait_active("Безопасность Windows", 30)
            time.sleep(1)
            keyboard.write(f"{settings['PASSWORD']}\n", delay=0)
            search_far_and_start(dst)
    else:  # Если комп не удаленный то блок с авторизацией отсутствует
        try:
            autoit.run(settings['FAR'])
            search_far_and_start(dst)
        except autoit.autoit.AutoItError:
            print('ПРОВЕРЬ НАСТРОЙКИ ВОЗМОЖНО НЕПРАВИЛЬНО УКАЗАН ПУТЬ К FAR')


# Ожидание формирования лога чекалки и его вывод
def waiting_checker_log(address_where_log):
    address_for_waiting_log = address_where_log + '\\ChkInfo.xml'
    address_where_log = address_where_log + '\\chkerr.log'
    log_not_ready = True
    timer = 0
    while log_not_ready:  # Таймер принудительного выхода из цикла если не дождались лога
        if timer >= 300:
            print(f'{RED}Лог проверки не сформирован проверьте работоспособность чекалки!{RESET}')
            break
        try:
            # Ожидаем пока сформируется файл, который появляется позже лога, пытаясь прочесть его каждую секунду
            with open(address_for_waiting_log) as f1:
                print(f'{YELLOW}РЕЗУЛЬТАТ ПРОВЕРКИ ЧЕКАЛКИ chkerr.log:{RESET}')
                print('╔' + ''.center(118, '=') + '╗')
            # Как только этот файл сформирован, так как он последний, то к тому времени лог уже готов. И мы его читаем.
            try:
                with open(address_where_log) as f2:  # Выводим содержимое лога на экран
                    for line in f2:
                        print('║ ' + line.strip().ljust(117) + '║')
                print('╚'+''.center(118, '=') + '╝')  # Чтобы визуально отделить лог в консоли
                log_not_ready = False
            except PermissionError:
                print(f'{RED}Нет доступа к логу, проверь, возможно он открыт в другой программе!{RESET}')
        except (FileNotFoundError, PermissionError):  # Если файл не удается открыть ждем секунду
            time.sleep(1)
            timer += 1
            continue

# =====================================================CHECKS======================================================


# Первая проверка
def first_check(msg1, msg2):
    while True:
        print(msg1)
        check = input('Y\\N: ')
        if check in ['N', 'n', 'Т', 'т']:
            print(RED + 'ИСПРАВЬ ЗАМЕЧАНИЯ И ПОПРОБУЙ СНОВА!'.center(120, ' ') + RESET)
            continue
        else:
            # print(GREEN + 'ПРОЙДЕНО!'.center(120, ' ') + RESET)
            print(msg2)
            # show_folder_contents(source_folder)
            break


# Простая проверка в зависимости от сообщения
def easy_check(msg):
    while True:
        print(msg)
        check = input('Y\\N: ')
        if check in ['N', 'n', 'Т', 'т']:
            print(RED + 'ИСПРАВЬ ЗАМЕЧАНИЯ И ПОПРОБУЙ СНОВА!'.center(120, ' ') + RESET)
            continue
        else:
            # print(GREEN + 'ПРОЙДЕНО!'.center(120, ' ') + RESET)
            break


# Проверка с копированием и повторным запуском чекалки
def check_with_checker(msg, check_regex, source_folder, destination_folder):
    while True:
        print(msg)
        check = input('Y\\N: ')
        if check in ['N', 'n', 'Т', 'т']:
            print(f'{YELLOW}СКОПИРОВАТЬ КАТАЛОГ ПОВТОРНО?{RESET}')
            yesno = input('Y\\N: ')
            if yesno in ['N', 'n', 'Т', 'т']:
                continue
            else:
                delete_trash(check_regex, destination_folder)  # Удаляем старый лог и лишние файлы
                report(InfoReports.COPY_FOLDER, source_folder, color=YELLOW)
                copy_all_or_not(source_folder, destination_folder, check_regex, 1)
                # copy_files(source_folder, destination_folder, check_regex)  # Копируем файлы заново
                print(f'{GREEN}ФАЙЛЫ УСПЕШНО СКОПИРОВАНЫ!{RESET}')
                show_folder_contents(dst)  # Просматриваем содержимое
                search_far_and_start(dst)  # Запускаем чекалку в уже запущенном FAR
                waiting_checker_log(dst)   # Ждем появления лога
        else:
            # print(GREEN + 'ПРОЙДЕНО!'.center(120, ' ') + RESET)
            break


# Копируем все содержимое или в соответсвтвии с регулярным выражением
def copy_all_or_not(source_folder, destination_folder, check_regex, print_report=0):
    print(Checks.CHECK9)
    all_not = str(input('Y\\N: '))
    if print_report == 1:
        report(InfoReports.DONT_TOUCH, color=RED)
        report(InfoReports.COPY_FOLDER, source_folder, color=YELLOW)
    else:
        pass
    if all_not in ['N', 'n', 'Т', 'т']:
        print('Копируем все файлы: ')
        copy_files(source_folder, destination_folder)
    else:
        print('Копируем файлы по результатам авто проверки: ')
        copy_files(source_folder, destination_folder, check_regex)


# =============================================WORK WITH DATABASE======================================================


# Поиск в файле pck номера заявки, и запросы к БД в соответсвии с номером заявки
def about_request(source_folder, database):
    RP = ''
    regex = re.compile(r'ibsobj\d{0,2}?\.pck')
    for file in os.listdir(source_folder):
        if regex.search(file):
            src = os.path.join(source_folder, file)
            break
    try:
        with open(src) as pck:
            for line in pck:
                try:
                    RP = re.compile(settings['NUMBER_REQUEST_REGEX']).search(line).group()
                    break
                except AttributeError:
                    pass
    except UnboundLocalError:
        print(f'{RED}ФАЙЛ PCK НЕ НАЙДЕН{RESET}')

    def sql_query():
        SQL1 = f"""select t.c_priority ПРИОРИТЕТ,
                       t.c_code НОМЕР,
                       t.c_name НАИМЕНОВАНИЕ,
                       pp.c_lastname || ' ' || pp.c_name Ответственный,
                       (select case
                                 when A4_1.c_name = 'Новая' and
                                      (select 1
                                         from Z#TASK_PROPERTYS t
                                        where t.collection_id = A1_2.C_ADD_PROP_ARR
                                          and t.c_name = 'ГОТОВА_К_РАБОТЕ') = 1 then
                                  'Готова к работе'
                                 when A4_1.c_name = 'В работе' and
                                      (select 1
                                         from Z#TASK_PROPERTYS t
                                        where t.collection_id = A1_2.C_ADD_PROP_ARR
                                          and t.c_name = 'Готова к продолжению работы') = 1 then
                                  'Готова к продолжению работы'
                                 else
                                  A4_1.c_name
                               end C_10
                          FROM Z#TASK A1_2, Z#CM_CHECKPOINT A3_1, Z#CM_POINT A4_1
                         WHERE A1_2.C_CHECKPOINT = A3_1.ID(+)
                           AND A3_1.C_POINT = A4_1.ID(+)
                           and A1_2.id = t.id
                           and rownum < 2) Статус
                  from z#task t
                  left join z#REQUEST r
                    on t.c_request = r.id
                  left join z#PHYS_PERSON pp
                    on t.c_performer = pp.id
                 where r.c_code = '{RP}'
                 order by t.c_priority
                """
        SQL = f"""select distinct r.c_problem_descr, r.c_recommendation 
                            from z#task t, z#REQUEST r
                            where r.id = t.c_request
                            and r.c_code = '{RP}'"""

        SQL2 = f"""select st.c_name
                    from Z#SUPPORT_TYPE st, z#REQUEST r
                   where r.c_s_type = st.id
                     and r.c_code = '{RP}'"""
        try:
            connection = cx_Oracle.connect(database)
            cursor1 = connection.cursor()
            cursor2 = connection.cursor()
            cursor3 = connection.cursor()
            cursor1.execute(SQL1)
            cursor2.execute(SQL)
            cursor3.execute(SQL2)
            tasks = cursor1.fetchall()
            about_task = cursor2.fetchall()
            defect_or_not = cursor3.fetchall()
            cursor1.close()
            cursor2.close()
            cursor3.close()
            return tasks, about_task, defect_or_not
        except:
            print('НЕ УДАЛОСЬ ПОДКЛЮЧИТЬСЯ К БАЗЕ ДАННЫХ')
    return sql_query()


# Вывод задач по заявке в соответствии с запросом полученным в sql_query()
def print_task_table(tasks):
    print(f'{YELLOW}ВНИМАНИЕ, СПИСОК ЗАДАЧ ВЫГРУЖЕН ЗА ВЧЕРАШНИЙ ДЕНЬ!{RESET}')
    if len(tasks) > 0:
        table = beautifultable.BeautifulTable()
        table.column_headers = ['Приоритет', 'Задача', 'Название', 'Исполнитель', 'Статус']
        for i in tasks:
            table.append_row(i)
        table.column_alignments['Название'] = beautifultable.ALIGN_LEFT
        table.column_alignments['Исполнитель'] = beautifultable.ALIGN_LEFT
        table.column_alignments['Статус'] = beautifultable.ALIGN_LEFT
        table.width_exceed_policy = beautifultable.WEP_ELLIPSIS
        table.max_table_width = 120
        table.set_style(beautifultable.STYLE_BOX_DOUBLED)
        print(table)
    else:
        print(f"{RED}НЕ УДАЛОСЬ ПОЛУЧИТЬ ИНФОРМАЦИЮ ПО ЗАЯВКЕ{RESET}")


# Вывод public info по заявке в соответствии с запросом полученным в sql_query()
def print_description(about_task):
    print(f'{YELLOW}ВНИМАНИЕ, ОПИСАНИЕ ЗАЯВКИ ДАТИРОВАНО ВЧЕРАШНИМ ДНЕМ!{RESET}')
    try:
        table = beautifultable.BeautifulTable()
        table.column_headers = [f'{RED}ОПИСАНИЕ ПРОБЛЕМЫ:{Style.RESET_ALL}', f'{GREEN}РЕАЛИЗАЦИЯ:{Style.RESET_ALL}']
        for i in about_task:
            table.append_row(i)
        table.max_table_width = 120
        table.set_style(beautifultable.STYLE_BOX_DOUBLED)
        print(table)
    except IndexError:
        print(f'{RED}НЕ УДАЛОСЬ ПОЛУЧИТЬ ИНФОРМАЦИЮ ПО ЗАЯВКЕ!{RESET}')


# Проверка есть ли в заявке задача документрирование
def check_doc(task):
    doc = False
    for i in task:
        if 'Документирование' in i:
            doc = True
            break
    if not doc:
        print(f'{YELLOW}В ЗАЯВКЕ НЕ ОБНАРУЖЕНА ЗАДАЧА "ДОКУМЕНТИРОВАНИЕ"!{RESET}')
        print(f'{YELLOW}ЗНАЧИТ ИЗМЕНЕНИЙ В ДОКУМЕНТАЦИИ НЕ БЫЛО!\n{RESET}')
    return doc

# =====================================================================================================================


database = settings['DATABASE']
destination_folder = settings['DESTINATION_FOLDER_FOR_CHECK']
destination_folder_distr = settings['DESTINATION_FOLDER_FOR_DISTR']

# TODO Основной цикл

while True:
    # Предварительная настройка
    precondition()
    report(InfoReports.ABOUT, color=YELLOW)

    # Проверка пути на соответствие формату
    source_folder = check_source_folder()
    clear()

    # Блок проверок
    # easy_check(Checks.CHECK0)
    clear()
    easy_check(Checks.CHECK1)
    clear()
    print(Checks.CHECK2)
    check_catalog(check_regex, source_folder)
    easy_check(Checks.CHECK3)
    try:  # Если доступ к базе есть выводим проверки в зависимости от данных из БД
        task, about_task, defect_or_not = about_request(source_folder, database)
        clear()
        print_description(about_task)
        if 'Дефект' in defect_or_not[0][0]:
            easy_check(Checks.CHECK4_defect)
            clear()
            easy_check(Checks.CHECK5)
        else:
            easy_check(Checks.CHECK4_rework)
        if check_doc(task):
            clear()
            easy_check(Checks.CHECK6)
        clear()
        print_task_table(task)
    except TypeError:  # Если доступа к базе нет, то выводим все проверки без данных из БД
        easy_check(Checks.CHECK4_rework)
        clear()
        easy_check(Checks.CHECK5)
        clear()
        easy_check(Checks.CHECK6)
    easy_check(Checks.CHECK7)
    clear()
    easy_check(Checks.CHECK8)
    clear()

    # Формируем destination каталог
    dst = create_today_folder(destination_folder, source_folder)
    copy_all_or_not(source_folder, dst, check_regex, 1)

    # Копирование файлов и просмотр того что скопировали
    print(f'{GREEN}ФАЙЛЫ УСПЕШНО СКОПИРОВАНЫ!{RESET}')
    show_folder_contents(dst)

    # Запуск чекалки и ожидание ее лога
    run_check(dst)
    waiting_checker_log(dst)

    # Проверка с возможностью скопировать каталог заново
    check_with_checker(Checks.CHECK10, check_regex, source_folder, dst)
    clear()

    # Формируем destination каталог на дистре и копируем файлы
    dst_distr = create_today_folder(destination_folder_distr, source_folder)
    copy_all_or_not(source_folder, dst_distr, check_regex, 0)
    print(f'{GREEN}ФАЙЛЫ УСПЕШНО СКОПИРОВАНЫ!{RESET}\n')

    # Все операции закончены открываем итоговый каталог
    print(Checks.CONGRATULATION)
    time.sleep(3)
    subprocess.Popen(f'explorer "{dst_distr}"')
    print('ДЛЯ ВЫКЛАДКИ СДЕЛУЮЩЕГО КАТАЛОГА НАЖМИ ЛЮБУЮ КЛАВИШУ')
    print('ДЛЯ ВЫХОДА НАЖМИ "N"')
    next = input('Y\\N:')
    if next in ['N', 'n', 'Т', 'т']:
        break
    else:
        clear()
