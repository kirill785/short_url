# short_url

API-сервис сокращения ссылок

## Запуск сервера

```bash
python -m app.main
```

Запуск из docker контейнера:
```bash
# сборка образа
docker build -t url-shortener .

# запуск контейнера
docker run -p 8000:8000 --env-file .env url-shortener
```

База данных PostgreSQL при этом также должна быть развернута. В файле `.env` необходимо указать url базы данных, url приложения и secret key. Пример:
```bash
DATABASE_URL=postgresql://url_app:your-password@localhost/url_shortener
SECRET_KEY=your-secret-key
BASE_URL=http://localhost:8000
```

Создание пользователя url_app и базы данных url_shortener в PostgreSQL:
```bash
CREATE ROLE url_app WITH LOGIN PASSWORD 'your-password';
CREATE DATABASE url_shortener OWNER url_app;
```
