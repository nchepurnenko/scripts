import os
import csv
import requests
# import logging
# try:
#     import http.client as http_client
# except ImportError:
#     # Python 2
#     import httplib as http_client
# http_client.HTTPConnection.debuglevel = 1

# # logging.basicConfig(level=logging.DEBUG)
# logging.basicConfig()
# logging.getLogger().setLevel(logging.DEBUG)
# requests_log = logging.getLogger("requests.packages.urllib3")
# requests_log.setLevel(logging.DEBUG)
# requests_log.propagate = True

# https://pddimp.yandex.ru/api2/admin/get_token
TOKEN = os.environ.get('TOKEN')
DOMAIN = ''
csv_file = 'mailuser.csv'

def load_data_from_csv(filename):

    with open(filename, 'r', encoding='utf-8') as csvfile:
        rows = csv.DictReader(csvfile)
        yield from rows

def create_user(data):

    headers = {
        'PddToken': TOKEN,
    }

    create_user_params = {
        'domain': DOMAIN,
        'login': data['login'],
        'password': data['pass']
    }
    # Создать пользователя
    response = requests.post(
        'https://pddimp.yandex.ru/api2/admin/email/add',
        headers=headers,
        data=create_user_params,
        timeout=10,
    )
    response_data = response.json()

    if response_data['success'] == 'ok':
        # Редактировать созданного пользователя
        edit_user_params = {
            'domain': DOMAIN,
            'uid': response_data['uid'],
            'iname': data['iname'],
            'fname': data['fname']
        }

        response = requests.post(
            'https://pddimp.yandex.ru/api2/admin/email/edit',
            headers=headers,
            data=edit_user_params,
            timeout=10,
    )

    response_data = response.json()
    results = response_data
    return results

users = load_data_from_csv(csv_file)

for user in users:
    print(create_user(user))


    # пример get запроса
    # param = {
    #     'domain': 'sipuni.ru',
    # }
    # headers = {
    #     'PddToken': TOKEN,
    # }
    # response = requests.get(
    #     'https://pddimp.yandex.ru/api2/admin/email/list',
    #     headers=headers,
    #     params=param,
    #     timeout=10,
    # )
    # response.raise_for_status()
