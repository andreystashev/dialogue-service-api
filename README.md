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



