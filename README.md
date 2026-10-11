### README файл:

#### Title:
**Dialogue Service API**

#### Description:
FastAPI gateway for the dialogue service. This project is part of the "Programming Practice" course at National University of Science and Technology MISIS. It includes functionality for sending random jokes.

#### Содержание:
- [Описание](#описание)
- [Установка и запуск](#установка-и-запуск)
- [Использование](#использование)
- [Документация](#документация)


#### Описание
Этот репозиторий содержит реализацию шлюза FastAPI для сервиса диалогов, который включает функцию отправки случайных шуток. Проект демонстрирует использование FastAPI, Docker и интеграцию с внешними API.

#### Установка и запуск
Чтобы запустить полный набор сервисов локально, выполните следующие шаги:

1. Создайте актуальный файл `.env` на основе `.env.example`.
   ```sh
   cp .env.example .env
   ```
2. Создайте Docker-образ:
   ```sh
   docker build -t get-joke ./app/get_jokes
   ```
3. Выполните миграции базы данных:
   ```sh
   sudo docker-compose run --rm "dialog-api" make migrate
   ```
4. Запустите сервисы:
   ```sh
   sudo docker-compose up --build -d
   ```

#### Использование
После запуска сервисов, вы можете получить доступ к API следующим образом:

- **Quick access to the OpenAPI specification of the service:** [here](./openapi.yaml)
- **Visualize:** [here](https://editor.swagger.io)

#### Документация
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Documentation](https://docs.docker.com/)




## Смена пароля

`PUT /api/v1/users/set_password` принимает JSON-тело и требует Bearer-токен:

```http
PUT /api/v1/users/set_password
Authorization: Bearer <access-token>
Content-Type: application/json

{"password": "new-password", "password_confirm": "new-password"}
```

Передача паролей через query-параметры больше не поддерживается. Обновите
клиентские вызовы на JSON-тело. При ошибке валидации API возвращает описание
ошибок, но не копирует исходное тело запроса в ответ. Поля смены пароля
маскируются при отображении модели; правила длины и подтверждения остаются
в сервисе пользователей.

## Проверки API и фоновых задач

Текущий стек проекта рассчитан на Python 3.10. Для воспроизводимого тестового
окружения используйте совместимые версии тестового клиента и зависимостей:

```bash
python3.10 -m venv .venv
source .venv/bin/activate
python -m pip install pip==24.0
python -m pip install -r requirements-test.txt
python -m unittest discover -s tests/unit -v
```

Фиксация pip нужна для метаданных существующей версии Celery 4. Модульные
проверки используют тестовые настройки и подменяют DB-зависимости: им не нужны
PostgreSQL, Redis или рабочий Celery worker. Проверяются JSON-тело смены пароля,
авторизация, отсутствие пароля в ответах валидации и закрытие DB-сессии на всех
ветках фоновой задачи, включая возврат из кеша и ошибки.

GitHub Actions дополнительно запускает существующие API-тесты с отдельной
PostgreSQL-базой `dialogue_test`. Эти интеграционные тесты пересоздают таблицы:
запускайте их только с отдельной тестовой базой, никогда с рабочей.
