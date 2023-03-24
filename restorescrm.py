#!/usr/bin/env python3

import os
import sys
from pymongo import MongoClient
from bson import json_util
import tarfile
import json

SCRM = "server"
SCRM6 = "server".
MONGO_LOCAL_SERVER = "127.0.0.1"
DB_RESTORE_DIR = "/opt/backup/restore"
DB_NAME = "scrm"
DB_COLLECTION = "registrations"
MONGO_USER="admin"
MONGO_PASSWORD="pass"
MONGO_AUTH_SOURCE="admin"
usage = """Использование:
            restorescrm идентификатор_клиента дата_архива сервер [действие]
            формат даты: ГГГГММДД
            доступные серверы: scrm
            доступные действия:
                - dump - сохранить данные по клиенту из архива в файл.
                - revert - откатить изменения"""

if len(sys.argv) == 4:
    client_id = sys.argv[1]
    backup_date = sys.argv[2]
    server = sys.argv[3]
    action = ""
elif len(sys.argv) == 5:
    client_id = sys.argv[1]
    backup_date = sys.argv[2]
    server = sys.argv[3]
    action = sys.argv[4]
else:
    print(usage)
    sys.exit(1)...

def mongo_connect(server,db,collection):
.....
    # На этих серверах не включена авторизация
    if server == MONGO_LOCAL_SERVER or server == SCRM6:
       conn = MongoClient(server)
    else:
        conn = MongoClient(server,
                        username=MONGO_USER,
						password=MONGO_PASSWORD,
                        authSource=MONGO_AUTH_SOURCE)
    database = conn[db]
    db_collection = database[collection]
    return conn, db_collection

def find_document(collection, elements):

    return collection.find_one(elements)

def update_document(collection, data, client_id):

    collection.update_one(
        {
            "pbx_user_id": client_id
        },
        {
            "$set": data
        },
        upsert=False
    )

def extract_arc(path):

    tar = tarfile.open(path, "r:bz2")..
    tar.extractall(DB_RESTORE_DIR)
    tar.close()

def delete_temp_files(db_connection):

    print("Удаление временных файлов...")
    # удалить файлы из распакованного архива
    os.system(f"rm -rf {DB_RESTORE_DIR}/*")
    # удалить локальную БД
    db_connection.drop_database('scrm')


if server == "scrm":
    mongo_prod_server = SCRM
elif server == "scrm6":
    mongo_prod_server = SCRM6
else:
    print(usage)

# директория с бэкапами
db_backup_dir = f"/opt/backup/db-{server}"

# revert.
if (action == "revert"):
    revert_file = f"restorescrm_dumps/{client_id}_bk.json"
    if os.path.isfile(revert_file):
        question = input(f"Восстановить данные интеграции клиента {client_id} из файла {revert_file}? y/n\n")
        if question == "y":
            print(f"Восстановление данных клиента {client_id} из файла...")
            os.system(f"mongoimport --host={mongo_prod_server} -u {MONGO_USER} -p {MONGO_PASSWORD} --authenticationDatabase {MONGO_AUTH_SOURCE}
            sys.exit(0)
        elif question == "n":
            sys.exit(0)
    else:
        print(f"Не существует файла резервной копии данных интеграции клиента {client_id}")
 # end revert...

print("Восстановление БД из архива...")
backup_arc_path = f"{db_backup_dir}/{backup_date}.tar.bz2"
if os.path.isfile(backup_arc_path):
    extract_arc(backup_arc_path)
    exit_code = os.system(f"mongorestore -d scrm {DB_RESTORE_DIR}/opt/backup/{backup_date}/scrm/ > /dev/null 2>&1")
    if exit_code > 0:
        print("ОШИБКА. Не удалось восстановить БД из архива")
        sys.exit(1)
else:
    print("Нет архива на эту дату")
    sys.exit(1)

print(f"Получение данных по клиенту {client_id} из восстановленной БД...")
local_conn, local_collection = mongo_connect(MONGO_LOCAL_SERVER, DB_NAME, DB_COLLECTION)
archive_data = find_document(local_collection, {"pbx_user_id" : client_id})
if not archive_data:
    print("ОШИБКА. Не удалось получить данные.")
    delete_temp_files(local_conn)
    sys.exit(1)
if (action == "dump"):
    dump_file = f"restorescrm_dumps/{client_id}_dump.json"
    print(f"Запись в файл {dump_file}...")
    with open(dump_file, "w") as file:
        file.write(json_util.dumps(archive_data))
    delete_temp_files(local_conn)
    print(f"Завершено")
    sys.exit(0)

question = input(f"Восстановить данные интеграции клиента {client_id} из резервной копии {backup_date}? y/n\n")
if question == "y":
    print(f"Получение данных по клиенту {client_id} из текущей базы...")
    prod_conn, prod_collection = mongo_connect(mongo_prod_server, DB_NAME, DB_COLLECTION)
    current_data = find_document(prod_collection, {"pbx_user_id" : client_id})
    if not current_data:
	    print("ОШИБКА. Не удалось получить данные.")
        delete_temp_files(local_conn)
        sys.exit(1)
    # выгрузить в файл на случай отката
    with open(f"restorescrm_dumps/{client_id}_bk.json", "w") as file:
        file.write(json_util.dumps(current_data))

    print("Обновление данных в текущей базе...")
    archive_data['_id'] = current_data['_id']
    archive_data['settings']['oauth_access_key'] = current_data['settings']['oauth_access_key']
    archive_data['settings']['oauth_refresh_key'] = current_data['settings']['oauth_refresh_key']
    update_document(prod_collection, archive_data, client_id)

    # если ключи отличаются после обновления, вернуть первоначальные значения
    print("Тестирование изменений...")
    test_data = find_document(prod_collection, {"pbx_user_id" : client_id})
    if current_data['settings']['oauth_access_key'] != test_data['settings']['oauth_access_key'] or \
    current_data['settings']['oauth_refresh_key'] != test_data['settings']['oauth_refresh_key'] or \
    current_data['_id'] != test_data['_id']:
        update_document(prod_collection, current_data, client_id)
        print("ОШИБКА. Изменения не будут применены.")
        delete_temp_files(local_conn)
        sys.exit(1)
    delete_temp_files(local_conn)
    print("Завершено успешно")

if question == "n":
    delete_temp_files(local_conn)
    sys.exit(0)