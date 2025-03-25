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

## Описание API
```
POST /links/shorten – создает короткую ссылку (в custom_alias можно передать кастомную ссылку, в expires_at время жизни ссылки)
GET /links/{short_code} – перенаправляет на оригинальный URL
DELETE /links/{short_code} – удаляет связь (доступно только после регистрации)
PUT /links/{short_code} – обновляет URL (доступно только после регистрации)
GET /links/{short_code}/stats - получение статистики ссылки
GET /links/search?original_url={url} - поиск ссылки по оригинальному URL
POST /auth/register - регистрация пользователя
POST /auth/token - получение токена
```

## Примеры некоторых запросов

### Создание короткой ссылки
```bash
curl -X POST "http://localhost:8000/links/shorten" \
     -H "Content-Type: application/json" \
     -d '{"original_url":"https://google.com", "custom_alias":"test_url1"}'
```

### Переход по короткой ссылке
```bash
curl -L "http://localhost:8000/test_url1"
```

### Получение статистики
```bash
curl "http://localhost:8000/links/test_url1/stats"
```
