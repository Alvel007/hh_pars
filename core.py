from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import requests
import os


bot_token = '' # токен вашего тг-бота
chat_id = '' # ID вашего чата с тг-ботом
# Ниже указан url который мы будем чекать (заменить на ваше значение)
link_to_hh = 'https://hh.ru/search/vacancy?resume=386e905fff0cff8f8f0039ed1f51523756565a&from=resumelist&hhtmFrom=resume_list&schedule=remote&schedule=fullDay&schedule=flexible&search_field=name&search_field=company_name&search_field=description&enable_snippets=false&forceFiltersSaving=true'
login_time = 1 # Время на первичную авторизацию (в мин.)
check_time = 5 # Время между обновлениями линка чекером (в мин.)
raise_view = True # Автоподъем резюме на hh

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


time_raise_view = (240/check_time)  + 1
driver = webdriver.Firefox()
driver.get('https://hh.ru/account/login?backurl=%2F&hhtmFrom=main')
create_empty_json_file('hh.json')
time.sleep(login_time*60)
count=0
while True:
    driver.get(link_to_hh)
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
    count += 1
    if (count ==1 or count%time_raise_view==0) and raise_view:
        try:
            driver.get('https://hh.ru/')
            wait = WebDriverWait(driver, 10)
            up_button = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@data-qa='applicant-index-nba-action_update-resumes']")))
            up_button.click()
            print('Резюме up')
        except:
            print('Резюме не up')
    print(f'Проведена проверка №{count}')
    time.sleep(check_time * 60)
