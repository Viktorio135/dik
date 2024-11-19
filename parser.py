import pandas as pd
import os, re
import requests

from  database.db_commands import create_furniture


import transliterate

# Путь к файлу Excel
file_path = 'excel3.xls'

# Загрузка Excel файла с использованием xlrd
df = pd.read_excel(file_path, engine='xlrd', header=0)
# Определение столбцов для извлечения
columns_to_extract = ['Название', 'Розничная цена', 'Детальное описание', 'Детальная картинка', 'Длина столешницы (см)', 'Ширина столешницы (см)', 'Форма столешницы', 'Материал столешницы', 'Материал опор',
                      'Цвет опор',  'Высота (см)', 'Механизм раскладки', 'Цвет столешницы', 'Упаковки', 'Вес в упаковке, кг', 'Количество упаковок']

# Создание папки для сохранения изображений
def parse_price(price_str):
    # Используем регулярное выражение, чтобы убрать все символы, кроме цифр и точки
    cleaned_price = re.sub(r'[^\d.,]', '', price_str)
    
    # Заменяем запятую на точку, если она есть
    cleaned_price = cleaned_price.replace(',', '.')

    # Преобразуем в float
    if cleaned_price.endswith('.'):
        cleaned_price = cleaned_price[:-1]  # Удаляем последнюю точку
    try:
        return float(cleaned_price)
    except ValueError:
        return None  # Возвращаем None, если преобразование не удалось


# Функция для скачивания изображений
def download_image(url, name):
        try:
            response = requests.get(url, stream=True)
            with open(f'static/{name}', 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):  # Читаем данные по частям
                    f.write(chunk)  # Записываем часть данных в файл
            return 1
        except:
            return 0
       
        

count = 0
for _, row in df[columns_to_extract].iterrows():
    title = row['Название']
    price = row['Розничная цена']
    description = row['Детальное описание']
    image_url = row['Детальная картинка']
    dlina_stol = row['Длина столешницы (см)']
    shirina = row['Ширина столешницы (см)']
    forma = row['Форма столешницы']
    mat_stol = row['Материал столешницы']
    mat_opor = row['Материал опор']
    cvet_opor = row['Цвет опор']
    visota = row['Высота (см)']
    mex=row['Механизм раскладки']
    cvet_stol = row['Цвет столешницы']
    upakovki=row['Упаковки']
    ves_up=row['Вес в упаковке, кг']
    kolvo=row['Количество упаковок']
    

    caracteristic = f'Длина столешницы (см): {dlina_stol}, Ширина столешницы (см): {shirina}, Форма столешницы: {forma}, Материал столешницы: {mat_stol}, Материал опор: {mat_opor}, Цвет опор: {cvet_opor}, Высота (см): {visota}, Механизм раскладки: {mex}, Цвет столешницы: {cvet_stol}, Упаковки: {upakovki}, Вес в упаковке, кг: {ves_up}, Количество упаковок: {ves_up}'



    transliterated_text = transliterate.translit(title, 'ru', reversed=True)
    words = transliterated_text.split()
    snake_case_text = '_'.join(words) + '.jpg'
    if '/' in snake_case_text:
         snake_case_text = snake_case_text.replace(' ', '_').replace(',', '_').replace('/', '_')

    s = download_image(image_url, snake_case_text)
    if not s:
        snake_case_text = 'zaglushka.jpg'

    create_furniture(title, snake_case_text, description, caracteristic,  parse_price(price), 'Столы', forma)
    count += 1
    print(count)
    

