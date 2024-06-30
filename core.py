from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import json
import requests
import os


bot_token = '5120192268:AAEQIAlVnnrvxl7HC9G2TgzWtBJft61QkIA' # токен вашего тг-бота
chat_id = '346094457' # ID вашего чата с тг-ботом


def tg_alert(alarm):
    """Функция отправки сообщения в чат через бота telegram"""
    return requests.get(f'https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&parse_mode=html&text={alarm}')

def create_empty_json_file(file_name):
    """Функция проверки наличия файла json в директории скрипта"""
    file_path = os.path.join(os.path.dirname(__file__), file_name)
    if not os.path.isfile(file_path):
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write('{}')
        print(f'Файл {file_name} был создан.')
    else:
        print(f'Файл {file_name} уже существует.')

driver = webdriver.Firefox()

# Открываем авторизацию hh.ru
driver.get('https://samara.hh.ru/account/login?backurl=%2F&hhtmFrom=main')
create_empty_json_file('hh.json')
time.sleep(60) # за это время вы должны авторизоваться на hh
count=0
while True:
    # ниже указан линк на страницу с вакансиями. На hh все выставленные чекбоксы указаны в url
    driver.get('https://samara.hh.ru/search/vacancy?resume=386e905fff0cff8f8f0039ed1f51523756565a&from=resumelist&hhtmFrom=resume_list&schedule=remote&schedule=fullDay&schedule=flexible&search_field=name&search_field=company_name&search_field=description&enable_snippets=false&forceFiltersSaving=true')
    # чекаем все линки на вакансии на странице и их title
    vacancy_blocks = driver.find_elements(By.CLASS_NAME, 'vacancy-card--z_UXteNo7bRGzxWVcL7y')
    vacancies_dict = {}
    for block in vacancy_blocks:
        link = block.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
        title = block.find_element(By.CLASS_NAME, 'vacancy-name--c1Lay3KouCl7XasYakLk').text
        vacancies_dict[link] = title
    # считываем все, что уже было ранее записано в архив
    with open('hh.json', 'r', encoding='utf-8') as file:
        existing_data = json.load(file)
    # если в чеке есть то чего нет в архиве, собираем в словарь
    missing_keys = {}
    for key in vacancies_dict.keys():
        if key not in existing_data:
            missing_keys[key] = vacancies_dict[key]
    # если словарь не пустой, отправляем значения в чат
    if len(missing_keys)>0:
        missing_keys_str = '\n'.join([f'{value}: {key}' for key, value in missing_keys.items()])
        tg_alert(missing_keys_str)
        # полученный словарь дописываем в архив
        with open('hh.json', 'r', encoding='utf-8') as file:
            existing_data = json.load(file)
        existing_data.update(missing_keys)
        with open('hh.json', 'w', encoding='utf-8') as file:
            json.dump(existing_data, file, ensure_ascii=False, indent=4)
        print('Сообщение отправлено в чат')
    count = count+1
    print(f'Проведена проверкка №{count}')
    time.sleep(300) # время между чеками
