# API Documentation - Ассоциация Ветеранов

## Базовый URL
```
http://172.16.79.233:5000
```

## Аутентификация
Для доступа к защищенным endpoint-ам необходимо включать JWT токен в заголовок:
```
Authorization: Bearer <your-jwt-token>
```

---

## 1. Аутентификация

### 1.1 Вход в систему
```http
POST /api/auth/login
```

**Описание:** Аутентификация пользователя и получение JWT токена

**Параметры (body):**
```json
{
  "username": "string",  // required - имя пользователя
  "password": "string"   // required - пароль
}
```

**Пример запроса:**
```json
{
  "username": "admin",
  "password": "admin"
}
```

**Ответы:**
- **200 OK** - Успешная аутентификация
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "username": "admin",
    "role": "admin"
  }
}
```

- **401 Unauthorized** - Неверные учетные данные
```json
{
  "error": "Invalid credentials",
  "message": "Username or password is incorrect"
}
```

### 1.2 Выход из системы
```http
POST /api/auth/logout
```

**Описание:** Деактивация текущего JWT токена

**Заголовки:**
```
Authorization: Bearer <token>
```

**Ответы:**
- **204 No Content** - Успешный выход
- **401 Unauthorized** - Токен недействителен

### 1.3 Проверка токена
```http
GET /api/auth/verify
```

**Описание:** Проверка действительности JWT токена

**Заголовки:**
```
Authorization: Bearer <token>
```

**Ответы:**
- **200 OK** - Токен действителен
```json
{
  "valid": true,
  "user": {
    "id": 1,
    "username": "admin",
    "role": "admin"
  }
}
```

- **401 Unauthorized** - Токен недействителен или отсутствует

---

## 2. Законодательство (Laws)

### 2.1 Получить все законы
```http
GET /api/laws
```

**Описание:** Получение списка всех законов

**Параметры (query) - опциональные:**
- `category` (string) - фильтр по категории
- `search` (string) - поиск по названию или описанию
- `limit` (number) - количество записей (по умолчанию 50)
- `offset` (number) - смещение для пагинации (по умолчанию 0)

**Пример запроса:**
```
GET /api/laws?category=федеральный&limit=20&offset=0
```

**Ответ 200 OK:**
```json
{
  "laws": [
    {
      "id": 1,
      "title": {
        "ru": "Закон о ветеранах",
        "uz": "Veteranlar haqidagi qonun",
        "en": "Veterans Law"
      },
      "description": {
        "ru": "Федеральный закон о ветеранах",
        "uz": "Veteranlar haqidagi federal qonun",
        "en": "Federal Veterans Law"
      },
      "category": {
        "ru": "Федеральный закон",
        "uz": "Federal qonun",
        "en": "Federal Law"
      },
      "date": "2023-01-15",
      "pdfUrl": "https://example.com/files/law1.pdf",
      "createdAt": "2023-01-15T10:30:00Z",
      "updatedAt": "2023-01-15T10:30:00Z"
    }
  ],
  "total": 25,
  "limit": 20,
  "offset": 0
}
```

### 2.2 Получить закон по ID
```http
GET /api/laws/{id}
```

**Описание:** Получение конкретного закона по его ID

**Параметры (path):**
- `id` (number, required) - ID закона

**Ответы:**
- **200 OK** - Закон найден (структура как в списке)
- **404 Not Found** - Закон не найден

### 2.3 Создать новый закон
```http
POST /api/laws
```

**Описание:** Создание нового закона

**Заголовки:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Параметры (body):**
```json
{
  "title": {
    "ru": "string",  // required
    "uz": "string",  // required  
    "en": "string"   // required
  },
  "description": {
    "ru": "string",  // required
    "uz": "string",  // required
    "en": "string"   // required
  },
  "category": {
    "ru": "string",  // required
    "uz": "string",  // required
    "en": "string"   // required
  },
  "date": "string",     // required, format: YYYY-MM-DD
  "pdfUrl": "string"    // optional, URL к PDF файлу
}
```

**Пример запроса:**
```json
{
  "title": {
    "ru": "Новый закон о льготах",
    "uz": "Imtiyozlar haqidagi yangi qonun",
    "en": "New Benefits Law"
  },
  "description": {
    "ru": "Закон о социальных льготах для ветеранов",
    "uz": "Veteranlar uchun ijtimoiy imtiyozlar qonuni",
    "en": "Social benefits law for veterans"
  },
  "category": {
    "ru": "Социальные льготы",
    "uz": "Ijtimoiy imtiyozlar",
    "en": "Social Benefits"
  },
  "date": "2024-01-01",
  "pdfUrl": "https://example.com/files/new-law.pdf"
}
```

**Ответы:**
- **201 Created** - Закон успешно создан
```json
{
  "id": 26,
  "title": { /* ... */ },
  "description": { /* ... */ },
  "category": { /* ... */ },
  "date": "2024-01-01",
  "pdfUrl": "https://example.com/files/new-law.pdf",
  "createdAt": "2024-01-01T12:00:00Z",
  "updatedAt": "2024-01-01T12:00:00Z"
}
```

- **400 Bad Request** - Ошибка валидации
- **401 Unauthorized** - Не авторизован

### 2.4 Обновить закон
```http
PUT /api/laws/{id}
```

**Описание:** Обновление существующего закона

**Заголовки:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Параметры (path):**
- `id` (number, required) - ID закона

**Параметры (body):** те же что и в POST запросе

**Ответы:**
- **200 OK** - Закон успешно обновлен
- **400 Bad Request** - Ошибка валидации
- **401 Unauthorized** - Не авторизован
- **404 Not Found** - Закон не найден

### 2.5 Удалить закон
```http
DELETE /api/laws/{id}
```

**Описание:** Удаление закона

**Заголовки:**
```
Authorization: Bearer <token>
```

**Параметры (path):**
- `id` (number, required) - ID закона

**Ответы:**
- **204 No Content** - Закон успешно удален
- **401 Unauthorized** - Не авторизован
- **404 Not Found** - Закон не найден

---

## 3. Новости (News)

### 3.1 Получить все новости
```http
GET /api/news
```

**Описание:** Получение списка всех новостей

**Параметры (query) - опциональные:**
- `search` (string) - поиск по заголовку или содержанию
- `dateFrom` (string) - фильтр от даты (YYYY-MM-DD)
- `dateTo` (string) - фильтр до даты (YYYY-MM-DD)
- `limit` (number) - количество записей (по умолчанию 20)
- `offset` (number) - смещение для пагинации (по умолчанию 0)
- `sortBy` (string) - сортировка: 'date' | 'title' (по умолчанию 'date')
- `sortOrder` (string) - порядок: 'asc' | 'desc' (по умолчанию 'desc')

**Пример запроса:**
```
GET /api/news?limit=10&dateFrom=2024-01-01&sortBy=date&sortOrder=desc
```

**Ответ 200 OK:**
```json
{
  "news": [
    {
      "id": 1,
      "title": {
        "ru": "Важная новость",
        "uz": "Muhim yangilik",
        "en": "Important News"
      },
      "content": {
        "ru": "Полный текст новости...",
        "uz": "Yangilik to'liq matni...",
        "en": "Full news text..."
      },
      "summary": {
        "ru": "Краткое описание",
        "uz": "Qisqacha tavsif",
        "en": "Brief description"
      },
      "date": "2024-01-15",
      "imageUrl": "https://example.com/images/news1.jpg",
      "createdAt": "2024-01-15T10:30:00Z",
      "updatedAt": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 15,
  "limit": 10,
  "offset": 0
}
```

### 3.2 Получить новость по ID
```http
GET /api/news/{id}
```

**Описание:** Получение конкретной новости по её ID

**Параметры (path):**
- `id` (number, required) - ID новости

**Ответы:**
- **200 OK** - Новость найдена (структура как в списке)
- **404 Not Found** - Новость не найдена

### 3.3 Создать новую новость
```http
POST /api/news
```

**Описание:** Создание новой новости

**Заголовки:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Параметры (body):**
```json
{
  "title": {
    "ru": "string",  // required
    "uz": "string",  // required
    "en": "string"   // required
  },
  "content": {
    "ru": "string",  // required
    "uz": "string",  // required
    "en": "string"   // required
  },
  "summary": {
    "ru": "string",  // required
    "uz": "string",  // required
    "en": "string"   // required
  },
  "date": "string",     // required, format: YYYY-MM-DD
  "imageUrl": "string"  // optional, URL к изображению
}
```

**Ответы:**
- **201 Created** - Новость успешно создана
- **400 Bad Request** - Ошибка валидации
- **401 Unauthorized** - Не авторизован

### 3.4 Обновить новость
```http
PUT /api/news/{id}
```

**Описание:** Обновление существующей новости

**Заголовки:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Параметры (path):**
- `id` (number, required) - ID новости

**Параметры (body):** те же что и в POST запросе

**Ответы:**
- **200 OK** - Новость успешно обновлена
- **400 Bad Request** - Ошибка валидации
- **401 Unauthorized** - Не авторизован
- **404 Not Found** - Новость не найдена

### 3.5 Удалить новость
```http
DELETE /api/news/{id}
```

**Описание:** Удаление новости

**Заголовки:**
```
Authorization: Bearer <token>
```

**Параметры (path):**
- `id` (number, required) - ID новости

**Ответы:**
- **204 No Content** - Новость успешно удалена
- **401 Unauthorized** - Не авторизован
- **404 Not Found** - Новость не найдена

---

## 4. Поиск сослуживцев (Comrades)

### 4.1 Поиск сослуживцев
```http
GET /api/comrades
```

**Описание:** Поиск сослуживцев по различным параметрам

**Параметры (query) - все опциональные:**
- `name` (string) - имя или фамилия
- `unit` (string) - воинская часть
- `region` (string) - регион службы
- `yearFrom` (number) - год службы от
- `yearTo` (number) - год службы до
- `rank` (string) - воинское звание
- `limit` (number) - количество результатов (по умолчанию 50)
- `offset` (number) - смещение для пагинации (по умолчанию 0)

**Пример запроса:**
```
GET /api/comrades?name=Иванов&unit=123&region=Ташкент&yearFrom=1990&yearTo=1995
```

**Ответ 200 OK:**
```json
{
  "comrades": [
    {
      "id": 1,
      "firstName": "Иван",
      "lastName": "Иванов",
      "middleName": "Петрович",
      "unit": "Воинская часть 12345",
      "region": "Ташкентская область",
      "yearOfServiceFrom": 1990,
      "yearOfServiceTo": 1992,
      "rank": "Сержант",
      "photoUrl": "https://example.com/photos/person1.jpg",
      "contactInfo": {
        "phone": "+998901234567",
        "email": "ivanov@example.com",
        "address": "г. Ташкент, ул. Примерная 123"
      },
      "additionalInfo": "Дополнительная информация о службе",
      "isVerified": true,
      "createdAt": "2023-01-15T10:30:00Z",
      "updatedAt": "2023-06-20T14:45:00Z"
    }
  ],
  "total": 5,
  "limit": 50,
  "offset": 0
}
```

### 4.2 Добавить информацию о сослуживце
```http
POST /api/comrades
```

**Описание:** Добавление информации о сослуживце

**Заголовки:**
```
Content-Type: application/json
```

**Параметры (body):**
```json
{
  "firstName": "string",           // required
  "lastName": "string",            // required
  "middleName": "string",          // optional
  "unit": "string",                // required
  "region": "string",              // required
  "yearOfServiceFrom": "number",   // required
  "yearOfServiceTo": "number",     // optional
  "rank": "string",                // optional
  "photoUrl": "string",            // optional
  "contactInfo": {                 // optional
    "phone": "string",
    "email": "string",
    "address": "string"
  },
  "additionalInfo": "string"       // optional
}
```

**Пример запроса:**
```json
{
  "firstName": "Александр",
  "lastName": "Петров",
  "middleName": "Сергеевич",
  "unit": "Воинская часть 54321",
  "region": "Самаркандская область",
  "yearOfServiceFrom": 1985,
  "yearOfServiceTo": 1987,
  "rank": "Старший лейтенант",
  "photoUrl": "https://example.com/photos/petrov.jpg",
  "contactInfo": {
    "phone": "+998901111111",
    "email": "petrov@example.com",
    "address": "г. Самарканд, ул. Мирзо Улугбека 45"
  },
  "additionalInfo": "Служил в танковых войсках"
}
```

**Ответы:**
- **201 Created** - Информация успешно добавлена
- **400 Bad Request** - Ошибка валидации

### 4.3 Получить информацию о сослуживце по ID
```http
GET /api/comrades/{id}
```

**Описание:** Получение детальной информации о конкретном сослуживце

**Параметры (path):**
- `id` (number, required) - ID записи

**Ответы:**
- **200 OK** - Информация найдена
- **404 Not Found** - Запись не найдена

### 4.4 Обновить информацию о сослуживце
```http
PUT /api/comrades/{id}
```

**Описание:** Обновление информации о сослуживце

**Заголовки:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Параметры (path):**
- `id` (number, required) - ID записи

**Параметры (body):** те же что и в POST запросе

**Ответы:**
- **200 OK** - Информация успешно обновлена
- **400 Bad Request** - Ошибка валидации
- **401 Unauthorized** - Не авторизован
- **404 Not Found** - Запись не найдена

### 4.5 Удалить информацию о сослуживце
```http
DELETE /api/comrades/{id}
```

**Описание:** Удаление информации о сослуживце

**Заголовки:**
```
Authorization: Bearer <token>
```

**Параметры (path):**
- `id` (number, required) - ID записи

**Ответы:**
- **204 No Content** - Информация успешно удалена
- **401 Unauthorized** - Не авторизован
- **404 Not Found** - Запись не найдена

### 4.6 Массовый импорт сослуживцев из Excel
```http
POST /api/comrades/bulk-import
```

**Описание:** Импорт нескольких сослуживцев из Excel файла

**Заголовки:**
```
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Параметры (form-data):**
- `file` (file, required) - Excel файл (.xlsx или .xls)

**Формат Excel файла:**
| Колонка | Обязательна | Описание |
|---------|-------------|----------|
| Фамилия | ✅ | Фамилия сослуживца |
| Имя | ✅ | Имя сослуживца |
| Отчество | ❌ | Отчество сослуживца |
| Воинская часть | ✅ | Номер части или соединение |
| Регион | ✅ | Регион службы |
| Год службы с | ✅ | Год начала службы |
| Год службы по | ❌ | Год окончания службы |
| Звание | ❌ | Воинское звание |
| Телефон | ❌ | Контактный телефон |
| Email | ❌ | Электронная почта |
| Адрес | ❌ | Почтовый адрес |
| Дополнительная информация | ❌ | Дополнительные сведения |

**Пример запроса:**
```bash
curl -X POST http://localhost:5000/api/comrades/bulk-import \
  -H "Authorization: Bearer <your-jwt-token>" \
  -F "file=@comrades.xlsx"
```

**Ответы:**
- **200 OK** - Импорт выполнен (возможны предупреждения)
```json
{
  "success": true,
  "message": "Импорт завершен. Импортировано: 15, пропущено: 2",
  "statistics": {
    "imported": 15,
    "skipped": 2,
    "total_processed": 17
  },
  "warnings": ["Строка 3: Пропущен год службы по"],
  "import_errors": ["Строка 5: Сослуживец уже существует"]
}
```
- **400 Bad Request** - Ошибка валидации файла
- **401 Unauthorized** - Не авторизован

### 4.7 Скачать образец Excel файла
```http
GET /api/comrades/bulk-import/sample
```

**Описание:** Получить образец Excel файла для импорта

**Заголовки:**
```
Authorization: Bearer <token>
```

**Ответы:**
- **200 OK** - Образец файла создан
```json
{
  "message": "Sample file created successfully",
  "file_path": "/tmp/sample_comrades_import_20231220_143000.xlsx",
  "columns": {
    "required": ["Фамилия", "Имя", "Воинская часть", "Регион", "Год службы с"],
    "optional": ["Отчество", "Год службы по", "Звание", "Телефон", "Email", "Адрес", "Дополнительная информация"]
  }
}
```
- **401 Unauthorized** - Не авторизован

---

## 5. Управление файлами (Files)

### 5.1 Загрузка файла
```http
POST /api/files/upload
```

**Описание:** Загрузка файла (PDF документы или изображения)

**Заголовки:**
```
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Параметры (form-data):**
- `file` (file, required) - файл для загрузки
- `type` (string, required) - тип файла: "pdf" | "image"
- `category` (string, optional) - категория: "law" | "news" | "photo" | "other"

**Ограничения:**
- PDF файлы: максимум 10MB
- Изображения: максимум 5MB, форматы: jpg, jpeg, png, gif, webp

**Пример запроса:**
```bash
curl -X POST \
  -H "Authorization: Bearer <token>" \
  -F "file=@document.pdf" \
  -F "type=pdf" \
  -F "category=law" \
  http://172.16.79.233:5000/api/files/upload
```

**Ответы:**
- **201 Created** - Файл успешно загружен
```json
{
  "id": "12345",
  "filename": "document_20240115_123456.pdf",
  "originalName": "document.pdf",
  "url": "https://example.com/files/document_20240115_123456.pdf",
  "type": "pdf",
  "category": "law",
  "size": 2048576,
  "uploadedAt": "2024-01-15T12:34:56Z"
}
```

- **400 Bad Request** - Неверный формат файла или размер превышен
- **401 Unauthorized** - Не авторизован

### 5.2 Получить информацию о файле
```http
GET /api/files/{id}
```

**Описание:** Получение метаданных файла

**Параметры (path):**
- `id` (string, required) - ID файла

**Ответы:**
- **200 OK** - Информация о файле
- **404 Not Found** - Файл не найден

### 5.3 Удалить файл
```http
DELETE /api/files/{id}
```

**Описание:** Удаление файла и его метаданных

**Заголовки:**
```
Authorization: Bearer <token>
```

**Параметры (path):**
- `id` (string, required) - ID файла

**Ответы:**
- **204 No Content** - Файл успешно удален
- **401 Unauthorized** - Не авторизован
- **404 Not Found** - Файл не найден

### 5.4 Получить список файлов
```http
GET /api/files
```

**Описание:** Получение списка загруженных файлов

**Заголовки:**
```
Authorization: Bearer <token>
```

**Параметры (query) - опциональные:**
- `type` (string) - фильтр по типу: "pdf" | "image"
- `category` (string) - фильтр по категории
- `limit` (number) - количество записей (по умолчанию 50)
- `offset` (number) - смещение для пагинации (по умолчанию 0)

**Ответ 200 OK:**
```json
{
  "files": [
    {
      "id": "12345",
      "filename": "document_20240115_123456.pdf",
      "originalName": "document.pdf",
      "url": "https://example.com/files/document_20240115_123456.pdf",
      "type": "pdf",
      "category": "law",
      "size": 2048576,
      "uploadedAt": "2024-01-15T12:34:56Z"
    }
  ],
  "total": 25,
  "limit": 50,
  "offset": 0
}
```

---

## 6. Коды ошибок

### Общие HTTP статусы:
- **200 OK** - Запрос выполнен успешно
- **201 Created** - Ресурс успешно создан
- **204 No Content** - Запрос выполнен успешно, данных для возврата нет
- **400 Bad Request** - Ошибка в параметрах запроса
- **401 Unauthorized** - Требуется аутентификация
- **403 Forbidden** - Доступ запрещен
- **404 Not Found** - Ресурс не найден
- **409 Conflict** - Конфликт данных (дублирование)
- **422 Unprocessable Entity** - Ошибка валидации данных
- **500 Internal Server Error** - Внутренняя ошибка сервера

### Формат ошибок:
```json
{
  "error": "Error Type",
  "message": "Detailed error description",
  "details": {
    "field": "error description"
  },
  "timestamp": "2024-01-15T12:34:56Z"
}
```

### Примеры ошибок валидации:
```json
{
  "error": "Validation Error",
  "message": "Request validation failed",
  "details": {
    "title.ru": "Title in Russian is required",
    "date": "Date must be in YYYY-MM-DD format"
  },
  "timestamp": "2024-01-15T12:34:56Z"
}
```

---

## 7. Примеры использования

### Полный цикл работы с новостью:

1. **Авторизация:**
```bash
curl -X POST http://172.16.79.233:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'
```

2. **Загрузка изображения:**
```bash
curl -X POST http://172.16.79.233:5000/api/files/upload \
  -H "Authorization: Bearer <token>" \
  -F "file=@news-image.jpg" \
  -F "type=image" \
  -F "category=news"
```

3. **Создание новости:**
```bash
curl -X POST http://172.16.79.233:5000/api/news \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"title":{"ru":"Новость","uz":"Yangilik","en":"News"},...}'
```

4. **Получение списка новостей:**
```bash
curl http://172.16.79.233:5000/api/news?limit=10
```

---

## 8. Рекомендации по безопасности

1. **HTTPS:** В продакшене обязательно использовать HTTPS
2. **CORS:** Настроить правильные CORS заголовки
3. **Rate Limiting:** Ограничить количество запросов на IP
4. **Валидация:** Тщательно валидировать все входящие данные
5. **Файлы:** Проверять типы и размеры загружаемых файлов
6. **JWT:** Использовать короткий срок жизни токенов + refresh токены
7. **Логирование:** Логировать все операции для аудита

---

## 9. Версионирование API

Текущая версия API: **v1**

При изменении API добавлять версию в URL:
```
/api/v1/news
/api/v2/news (будущая версия)
```
