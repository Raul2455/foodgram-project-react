Foodgram - Продуктовый помощник

Foodgram — это веб-приложение, которое позволяет пользователям публиковать рецепты, добавлять их в избранное, подписываться на других пользователей и формировать список покупок для выбранных рецептов. Проект реализован с использованием Django (бэкенд) и React (фронтенд).
Основные возможности
Рецепты:

    Публикация рецептов с изображениями, описанием и списком ингредиентов.

    Фильтрация рецептов по тегам, автору и избранному.

    Возможность добавления рецептов в избранное.

    Формирование списка покупок на основе выбранных рецептов.

Пользователи:

    Регистрация и аутентификация пользователей.

    Подписка на других пользователей.

    Просмотр рецептов других пользователей.

API:

    Полноценное REST API для взаимодействия с бэкендом.

    Документация API доступна по адресу: http://158.160.65.180/api/docs/ или http://foodgramraul245.strangled.net/api/docs/.

Технологии
Бэкенд:

    Python 3.9

    Django 4.2.18

    Django REST Framework

    PostgreSQL

    Gunicorn

    Nginx

Фронтенд:

    React

    Webpack

Инфраструктура:

    Docker

    Docker Compose

Установка и запуск проекта
1. Клонирование репозитория

Склонируйте репозиторий на ваш компьютер:
bash
Copy

git clone https://github.com/ваш-username/foodgram-project-react.git
cd foodgram-project-react/infra

2. Настройка переменных окружения

Создайте файл .env в папке infra и добавьте в него следующие переменные:
bash
Copy

# Настройки Django
SECRET_KEY=ваш-секретный-ключ
DEBUG=True

# Настройки базы данных
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

3. Запуск контейнеров

Перейдите в папку infra и выполните команду для запуска контейнеров:
bash
Copy

docker-compose up

После выполнения команды:

    Контейнер frontend подготовит файлы для работы фронтенд-приложения и завершит свою работу.

    Бэкенд и база данных будут запущены в соответствующих контейнерах.

4. Применение миграций

После запуска контейнеров выполните миграции для настройки базы данных:
bash
Copy

docker-compose exec backend python manage.py migrate

5. Создание суперпользователя

Создайте суперпользователя для доступа к административной панели Django:
bash
Copy

docker-compose exec backend python manage.py createsuperuser

6. Загрузка тестовых данных (опционально)

Для загрузки тестовых данных выполните команду:
bash
Copy

docker-compose exec backend python manage.py loaddata fixtures.json

Доступ к приложению

    Фронтенд: http://158.160.65.180 или http://foodgramraul245.strangled.net

    Админка: http://158.160.65.180/admin или http://foodgramraul245.strangled.net/admin

    API: http://158.160.65.180/api/docs/ или http://foodgramraul245.strangled.net/api/docs/

Автор

    Кирилл Мендрин

    GitHub: github.com/Raul2455

    Email: kirillmendrin245@gmail.com
