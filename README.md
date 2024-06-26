# MADSOFT-Test: Веб-приложение для работы с мемами

## Описание проекта

Этот проект представляет собой веб-приложение, разработанное с использованием FastAPI, которое предоставляет API для работы с коллекцией мемов. Приложение состоит из двух сервисов: сервис с публичным API для бизнес-логики и сервис для работы с медиа-файлами, используя S3-совместимое хранилище MinIO.

### Функциональность

- **GET /memes**: Получить список всех мемов (с пагинацией).
- **GET /memes/{id}**: Получить конкретный мем по его ID.
- **POST /memes**: Добавить новый мем (с картинкой и текстом).
- **PUT /memes/{id}**: Обновить существующий мем.
- **DELETE /memes/{id}**: Удалить мем.

### Требования

- Использование реляционной СУБД для хранения данных.
- Обработка ошибок и валидация входных данных.
- Использование Swagger/OpenAPI для документирования API.
- Написание нескольких unit-тестов для проверки основной функциональности.
- Написание README с описанием функциональности проекта и инструкцией по локальному запуску для разработки.
- Проект должен состоять минимум из: 1 сервис с публичным API, 1 сервис с приватным API для изображений, 1 сервис СУБД, 1 сервис S3-storage.
- Написание docker-compose.yml для запуска проекта.

## Инструкция по локальному запуску для разработки

### Предварительные требования

- Установленный Docker и Docker Compose.
- Python 3.12 или выше.

### Шаги для запуска

1. **Клонирование репозитория:**

   git clone https://github.com/Fastroer/MADSOFT-Test.git
   
   cd MADSOFT-Test

3. **Запуск Docker Compose:**

    В корневой директории проекта выполните команду:
   
    docker-compose up --build

    Это запустит все необходимые сервисы: базу данных PostgreSQL, MinIO, публичный и приватный API.


5. **Проверка работоспособности:**

    Откройте браузер и перейдите по следующим адресам для проверки API:
    - Публичное API: http://127.0.0.1:8000/api
    - Приватное API: http://127.0.0.1:8001/private-api

6. **Запуск тестов:**

   Тесты запускаются автоматически при помощи соответствующего сервиса.
