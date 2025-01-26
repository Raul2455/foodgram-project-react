# Используем официальный образ Node.js на основе Alpine Linux
FROM node:21.7.1-alpine as builder

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем package.json и package-lock.json
COPY package*.json ./

# Устанавливаем зависимости
RUN npm install

# Копируем все файлы проекта
COPY . .

# Собираем проект
RUN npm run build

# Используем легковесный образ Nginx для раздачи статики
FROM nginx:alpine

# Копируем собранные файлы из этапа сборки в папку Nginx
COPY --from=builder /app/build /usr/share/nginx/html

# Указываем порт, который будет слушать Nginx
EXPOSE 80

# Команда для запуска Nginx
CMD ["nginx", "-g", "daemon off;"]
