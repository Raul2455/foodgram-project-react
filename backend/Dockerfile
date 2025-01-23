# Этап 1: Сборка зависимостей
FROM python:3.8-slim as builder

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем переменные окружения для Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Копируем файл с зависимостями
COPY requirements.txt .

# Обновляем pip и устанавливаем зависимости в локальную папку
RUN pip install --upgrade pip && \
    pip install --user --no-warn-script-location -r requirements.txt

# Этап 2: Финальный образ
FROM python:3.8-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем установленные зависимости из первого этапа
COPY --from=builder /root/.local /root/.local

# Копируем исходный код проекта
COPY . .

# Указываем, что Python должен использовать установленные в /root/.local пакеты
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Открываем порт для приложения
EXPOSE 8000

# Команда для запуска приложения с использованием Gunicorn
CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0.0.0.0:8000"]