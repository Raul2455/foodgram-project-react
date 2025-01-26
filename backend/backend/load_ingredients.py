import json
import psycopg2

# Подключение к базе данных
conn = psycopg2.connect(
    dbname="foodgram",
    user="postgres",
    password="ваш_пароль",  # Замените на ваш пароль
    host="localhost",
    port="5432"
)
cursor = conn.cursor()

# Чтение данных из JSON-файла
with open('D:/Dev/foodgram-project-react-master/data/ingredients.json', 'r', encoding='utf-8') as file:
    ingredients = json.load(file)

# Вставка данных в таблицу
for ingredient in ingredients:
    cursor.execute(
        "INSERT INTO ingredients (name, measurement_unit) VALUES (%s, %s)",
        (ingredient['name'], ingredient['measurement_unit'])
    )

# Сохранение изменений и закрытие соединения
conn.commit()
cursor.close()
conn.close()
print("Данные успешно загружены!")