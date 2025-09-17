# API Documentation for Frontend Integration
# Ассоциация Ветеранов - API для интеграции фронтенда

Полная документация API для интеграции с фронтендом приложения Ассоциации Ветеранов.

## Базовая информация

**Base URL:** `http://172.16.79.233:5000/api`  
**Текущая версия:** v1  
**Формат данных:** JSON  
**Аутентификация:** JWT Bearer Token  

## Содержание

1. [Аутентификация](#аутентификация)
2. [Управление законами](#управление-законами)  
3. [Управление новостями](#управление-новостями)
4. [Поиск сослуживцев](#поиск-сослуживцев)
5. [Управление файлами](#управление-файлами)
6. [Коды ошибок и обработка](#коды-ошибок-и-обработка)
7. [Практические примеры интеграции](#практические-примеры-интеграции)

---

## Аутентификация

Все защищенные endpoint'ы требуют JWT токен в заголовке:
```
Authorization: Bearer <your-jwt-token>
```

### 🔐 Вход в систему

```http
POST /api/auth/login
```

**Описание:** Аутентификация пользователя и получение JWT токена

**Request Body:**
```json
{
  "username": "string",  // required - имя пользователя
  "password": "string"   // required - пароль
}
```

**Response 200 - Успешная аутентификация:**
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

**Response 400 - Ошибка валидации:**
```json
{
  "error": "Validation Error",
  "message": "Username and password are required"
}
```

**Response 401 - Неверные учетные данные:**
```json
{
  "error": "Invalid credentials", 
  "message": "Username or password is incorrect"
}
```

### 🚪 Выход из системы

```http
POST /api/auth/logout
```

**Описание:** Деактивация текущего JWT токена

**Headers:**
```
Authorization: Bearer <token>
```

**Response 204 - Успешный выход**  
**Response 401 - Токен недействителен**

### ✅ Проверка токена

```http
GET /api/auth/verify
```

**Описание:** Проверка действительности JWT токена

**Headers:**
```
Authorization: Bearer <token>
```

**Response 200 - Токен действителен:**
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

**Response 401 - Токен недействителен**

---

## Управление законами

### 📋 Получить все законы

```http
GET /api/laws
```

**Описание:** Получение списка всех законов с фильтрацией и пагинацией

**Query Parameters:**
- `category` (string, optional) - фильтр по категории
- `search` (string, optional) - поиск по названию или описанию
- `limit` (number, optional) - количество записей (по умолчанию 50, максимум 100)
- `offset` (number, optional) - смещение для пагинации (по умолчанию 0)

**Пример запроса:**
```
GET /api/laws?category=федеральный&limit=20&offset=0&search=ветераны
```

**Response 200:**
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

### 📄 Получить закон по ID

```http
GET /api/laws/{id}
```

**Описание:** Получение конкретного закона по его ID

**Path Parameters:**
- `id` (integer, required) - ID закона

**Response 200 - Закон найден (структура как в списке)**  
**Response 404 - Закон не найден**

### ➕ Создать новый закон

```http
POST /api/laws
```

**Описание:** Создание нового закона (требует аутентификации)

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
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
  "date": "YYYY-MM-DD",  // required, формат даты
  "pdfUrl": "string"     // optional, URL к PDF файлу
}
```

**Response 201 - Закон создан**  
**Response 400 - Ошибка валидации**  
**Response 401 - Не авторизован**

### ✏️ Обновить закон

```http
PUT /api/laws/{id}
```

**Описание:** Обновление существующего закона (требует аутентификации)

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Path Parameters:**
- `id` (integer, required) - ID закона

**Request Body:** те же поля что и в POST запросе

**Response 200 - Закон обновлен**  
**Response 400 - Ошибка валидации**  
**Response 401 - Не авторизован**  
**Response 404 - Закон не найден**

### 🗑️ Удалить закон

```http
DELETE /api/laws/{id}
```

**Описание:** Удаление закона (требует аутентификации)

**Headers:**
```
Authorization: Bearer <token>
```

**Path Parameters:**
- `id` (integer, required) - ID закона

**Response 204 - Закон удален**  
**Response 401 - Не авторизован**  
**Response 404 - Закон не найден**

---

## Управление новостями

### 📰 Получить все новости

```http
GET /api/news
```

**Описание:** Получение списка всех новостей с фильтрацией, сортировкой и пагинацией

**Query Parameters:**
- `search` (string, optional) - поиск по заголовку или содержанию
- `dateFrom` (string, optional) - фильтр от даты (YYYY-MM-DD)
- `dateTo` (string, optional) - фильтр до даты (YYYY-MM-DD)
- `limit` (number, optional) - количество записей (по умолчанию 20, максимум 100)
- `offset` (number, optional) - смещение для пагинации (по умолчанию 0)
- `sortBy` (string, optional) - сортировка: 'date' | 'title' (по умолчанию 'date')
- `sortOrder` (string, optional) - порядок: 'asc' | 'desc' (по умолчанию 'desc')

**Пример запроса:**
```
GET /api/news?limit=10&dateFrom=2024-01-01&sortBy=date&sortOrder=desc&search=важные
```

**Response 200:**
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

### 📰 Получить новость по ID

```http
GET /api/news/{id}
```

**Описание:** Получение конкретной новости по её ID

**Path Parameters:**
- `id` (integer, required) - ID новости

**Response 200 - Новость найдена (структура как в списке)**  
**Response 404 - Новость не найдена**

### ➕ Создать новую новость

```http
POST /api/news
```

**Описание:** Создание новой новости (требует аутентификации)

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
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
  "date": "YYYY-MM-DD",  // required, формат даты
  "imageUrl": "string"   // optional, URL к изображению
}
```

**Response 201 - Новость создана**  
**Response 400 - Ошибка валидации**  
**Response 401 - Не авторизован**

### ✏️ Обновить новость

```http
PUT /api/news/{id}
```

**Описание:** Обновление существующей новости (требует аутентификации)

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Path Parameters:**
- `id` (integer, required) - ID новости

**Request Body:** те же поля что и в POST запросе

**Response 200 - Новость обновлена**  
**Response 400 - Ошибка валидации**  
**Response 401 - Не авторизован**  
**Response 404 - Новость не найдена**

### 🗑️ Удалить новость

```http
DELETE /api/news/{id}
```

**Описание:** Удаление новости (требует аутентификации)

**Headers:**
```
Authorization: Bearer <token>
```

**Path Parameters:**
- `id` (integer, required) - ID новости

**Response 204 - Новость удалена**  
**Response 401 - Не авторизован**  
**Response 404 - Новость не найдена**

---

## Поиск сослуживцев

### 🔍 Поиск сослуживцев

```http
GET /api/comrades
```

**Описание:** Поиск сослуживцев по различным параметрам

**Query Parameters (все опциональные):**
- `name` (string) - имя или фамилия для поиска
- `unit` (string) - воинская часть
- `region` (string) - регион службы
- `yearFrom` (number) - год службы от
- `yearTo` (number) - год службы до
- `rank` (string) - воинское звание
- `limit` (number) - количество результатов (по умолчанию 50, максимум 100)
- `offset` (number) - смещение для пагинации (по умолчанию 0)

**Пример запроса:**
```
GET /api/comrades?name=Иванов&unit=123&region=Ташкент&yearFrom=1990&yearTo=1995
```

**Response 200:**
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

### 👤 Получить информацию о сослуживце по ID

```http
GET /api/comrades/{id}
```

**Описание:** Получение детальной информации о конкретном сослуживце

**Path Parameters:**
- `id` (integer, required) - ID записи

**Response 200 - Информация найдена**  
**Response 404 - Запись не найдена**

### ➕ Добавить информацию о сослуживце

```http
POST /api/comrades
```

**Описание:** Добавление информации о сослуживце (не требует аутентификации)

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "firstName": "string",        // required
  "lastName": "string",         // required  
  "middleName": "string",       // optional
  "unit": "string",             // required
  "region": "string",           // required
  "yearOfServiceFrom": number,  // required
  "yearOfServiceTo": number,    // optional
  "rank": "string",             // optional
  "photoUrl": "string",         // optional
  "contactInfo": {              // optional
    "phone": "string",
    "email": "string", 
    "address": "string"
  },
  "additionalInfo": "string"    // optional
}
```

**Validation Rules:**
- `yearOfServiceFrom` - должен быть между 1900 и текущим годом
- `yearOfServiceTo` - должен быть больше `yearOfServiceFrom` если указан
- `email` - должен быть валидным email адресом если указан
- `phone` - рекомендуется международный формат

**Response 201 - Информация добавлена**  
**Response 400 - Ошибка валидации**

### ✏️ Обновить информацию о сослуживце

```http
PUT /api/comrades/{id}
```

**Описание:** Обновление информации о сослуживце (требует аутентификации)

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Path Parameters:**
- `id` (integer, required) - ID записи

**Request Body:** те же поля что и в POST запросе

**Response 200 - Информация обновлена**  
**Response 400 - Ошибка валидации**  
**Response 401 - Не авторизован**  
**Response 404 - Запись не найдена**

### 🗑️ Удалить информацию о сослуживце

```http
DELETE /api/comrades/{id}
```

**Описание:** Удаление информации о сослуживце (требует аутентификации)

**Headers:**
```
Authorization: Bearer <token>
```

**Path Parameters:**
- `id` (integer, required) - ID записи

**Response 204 - Информация удалена**  
**Response 401 - Не авторизован**  
**Response 404 - Запись не найдена**

---

## Управление файлами

### 📤 Загрузка файла

```http
POST /api/files/upload
```

**Описание:** Загрузка файла (PDF документы или изображения)

**Headers:**
```
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Form Data Parameters:**
- `file` (file, required) - файл для загрузки
- `type` (string, required) - тип файла: "pdf" | "image"
- `category` (string, optional) - категория: "law" | "news" | "photo" | "other"

**Ограничения файлов:**
- **PDF файлы:** максимум 10MB, форматы: .pdf
- **Изображения:** максимум 5MB, форматы: .jpg, .jpeg, .png, .gif, .webp

**Пример запроса (curl):**
```bash
curl -X POST \
  -H "Authorization: Bearer <token>" \
  -F "file=@document.pdf" \
  -F "type=pdf" \
  -F "category=law" \
  http://172.16.79.233:5000/api/files/upload
```

**Response 201 - Файл загружен:**
```json
{
  "id": "12345-abcd-6789-efgh",
  "filename": "document_20240115_123456.pdf",
  "originalName": "document.pdf",
  "url": "http://172.16.79.233:5000/api/files/uploads/document_20240115_123456.pdf",
  "type": "pdf",
  "category": "law",
  "size": 2048576,
  "uploadedAt": "2024-01-15T12:34:56Z"
}
```

**Response 400 - Ошибка файла:**
```json
{
  "error": "Invalid file",
  "message": "File type not allowed or file too large"
}
```

**Response 401 - Не авторизован**

### 📂 Получить список файлов

```http
GET /api/files
```

**Описание:** Получение списка загруженных файлов (требует аутентификации)

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `type` (string, optional) - фильтр по типу: "pdf" | "image"
- `category` (string, optional) - фильтр по категории
- `limit` (number, optional) - количество записей (по умолчанию 50, максимум 100)
- `offset` (number, optional) - смещение для пагинации (по умолчанию 0)

**Пример запроса:**
```
GET /api/files?type=pdf&category=law&limit=20&offset=0
```

**Response 200:**
```json
{
  "files": [
    {
      "id": "12345-abcd-6789-efgh",
      "filename": "document_20240115_123456.pdf",
      "originalName": "document.pdf", 
      "url": "http://172.16.79.233:5000/api/files/uploads/document_20240115_123456.pdf",
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

**Response 401 - Не авторизован**

### 📄 Получить информацию о файле

```http
GET /api/files/{id}
```

**Описание:** Получение метаданных файла

**Path Parameters:**
- `id` (string, required) - ID файла

**Response 200 - Информация о файле (структура как в списке)**  
**Response 404 - Файл не найден**

### 🗑️ Удалить файл

```http
DELETE /api/files/{id}
```

**Описание:** Удаление файла и его метаданных (требует аутентификации)

**Headers:**
```
Authorization: Bearer <token>
```

**Path Parameters:**
- `id` (string, required) - ID файла

**Response 204 - Файл удален**  
**Response 401 - Не авторизован**  
**Response 404 - Файл не найден**

### 🔗 Получить файл

```http
GET /api/files/uploads/{filename}
```

**Описание:** Прямой доступ к загруженному файлу

**Path Parameters:**
- `filename` (string, required) - имя файла

**Response 200 - Файл**  
**Response 404 - Файл не найден**

---

## Коды ошибок и обработка

### HTTP статусы

| Код | Описание | Когда возникает |
|-----|----------|-----------------|
| 200 | OK | Запрос выполнен успешно |
| 201 | Created | Ресурс успешно создан |
| 204 | No Content | Запрос выполнен, данных для возврата нет |
| 400 | Bad Request | Ошибка в параметрах запроса |
| 401 | Unauthorized | Требуется аутентификация |
| 403 | Forbidden | Доступ запрещен |
| 404 | Not Found | Ресурс не найден |
| 405 | Method Not Allowed | HTTP метод не поддерживается |
| 409 | Conflict | Конфликт данных (дублирование) |
| 422 | Unprocessable Entity | Ошибка валидации данных |
| 500 | Internal Server Error | Внутренняя ошибка сервера |

### Формат ошибок

Все ошибки возвращаются в единообразном формате:

```json
{
  "error": "Error Type",
  "message": "Detailed error description",
  "details": {
    "field": "specific field error"
  },
  "timestamp": "2024-01-15T12:34:56Z"
}
```

### Примеры ошибок

**Ошибка валидации (400):**
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

**Ошибка аутентификации (401):**
```json
{
  "error": "Invalid credentials",
  "message": "Username or password is incorrect",
  "timestamp": "2024-01-15T12:34:56Z"
}
```

**Токен истек (401):**
```json
{
  "error": "Token expired",
  "message": "The token has expired",
  "timestamp": "2024-01-15T12:34:56Z"
}
```

### Обработка ошибок в JavaScript

```javascript
// Пример обработки ошибок
async function handleApiCall(url, options) {
  try {
    const response = await fetch(url, options);
    
    if (!response.ok) {
      const errorData = await response.json();
      
      switch (response.status) {
        case 401:
          // Перенаправить на страницу входа
          redirectToLogin();
          break;
        case 400:
          // Показать ошибки валидации
          showValidationErrors(errorData.details);
          break;
        case 404:
          // Показать сообщение "не найдено"
          showNotFoundMessage();
          break;
        default:
          // Показать общую ошибку
          showGenericError(errorData.message);
      }
      
      throw new Error(errorData.message);
    }
    
    return await response.json();
  } catch (error) {
    console.error('API call failed:', error);
    throw error;
  }
}
```

---

## Практические примеры интеграции

### Аутентификация и управление токенами

```javascript
class AuthService {
  constructor() {
    this.baseUrl = 'http://172.16.79.233:5000/api';
    this.token = localStorage.getItem('authToken');
  }

  async login(username, password) {
    const response = await fetch(`${this.baseUrl}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, password }),
    });

    if (response.ok) {
      const data = await response.json();
      this.token = data.token;
      localStorage.setItem('authToken', this.token);
      return data;
    } else {
      const error = await response.json();
      throw new Error(error.message);
    }
  }

  async logout() {
    if (this.token) {
      await fetch(`${this.baseUrl}/auth/logout`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.token}`,
        },
      });
    }
    
    this.token = null;
    localStorage.removeItem('authToken');
  }

  getAuthHeaders() {
    return this.token ? { 'Authorization': `Bearer ${this.token}` } : {};
  }

  isAuthenticated() {
    return !!this.token;
  }
}
```

### Работа с законами

```javascript
class LawsService {
  constructor(authService) {
    this.authService = authService;
    this.baseUrl = 'http://172.16.79.233:5000/api/laws';
  }

  async getLaws(filters = {}) {
    const params = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== '') {
        params.append(key, value);
      }
    });

    const response = await fetch(`${this.baseUrl}?${params}`);
    
    if (response.ok) {
      return await response.json();
    } else {
      throw new Error('Failed to fetch laws');
    }
  }

  async getLaw(id) {
    const response = await fetch(`${this.baseUrl}/${id}`);
    
    if (response.ok) {
      return await response.json();
    } else if (response.status === 404) {
      throw new Error('Law not found');
    } else {
      throw new Error('Failed to fetch law');
    }
  }

  async createLaw(lawData) {
    const response = await fetch(this.baseUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...this.authService.getAuthHeaders(),
      },
      body: JSON.stringify(lawData),
    });

    if (response.ok) {
      return await response.json();
    } else {
      const error = await response.json();
      throw new Error(error.message);
    }
  }

  async updateLaw(id, lawData) {
    const response = await fetch(`${this.baseUrl}/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        ...this.authService.getAuthHeaders(),
      },
      body: JSON.stringify(lawData),
    });

    if (response.ok) {
      return await response.json();
    } else {
      const error = await response.json();
      throw new Error(error.message);
    }
  }

  async deleteLaw(id) {
    const response = await fetch(`${this.baseUrl}/${id}`, {
      method: 'DELETE',
      headers: this.authService.getAuthHeaders(),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message);
    }
  }
}
```

### Работа с новостями

```javascript
class NewsService {
  constructor(authService) {
    this.authService = authService;
    this.baseUrl = 'http://172.16.79.233:5000/api/news';
  }

  async getNews(filters = {}) {
    const params = new URLSearchParams();
    
    // Установить значения по умолчанию
    const defaultFilters = {
      limit: 20,
      offset: 0,
      sortBy: 'date',
      sortOrder: 'desc',
      ...filters
    };

    Object.entries(defaultFilters).forEach(([key, value]) => {
      if (value !== undefined && value !== '') {
        params.append(key, value);
      }
    });

    const response = await fetch(`${this.baseUrl}?${params}`);
    
    if (response.ok) {
      return await response.json();
    } else {
      throw new Error('Failed to fetch news');
    }
  }

  async getNewsItem(id) {
    const response = await fetch(`${this.baseUrl}/${id}`);
    
    if (response.ok) {
      return await response.json();
    } else if (response.status === 404) {
      throw new Error('News not found');
    } else {
      throw new Error('Failed to fetch news');
    }
  }

  async createNews(newsData) {
    const response = await fetch(this.baseUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...this.authService.getAuthHeaders(),
      },
      body: JSON.stringify(newsData),
    });

    if (response.ok) {
      return await response.json();
    } else {
      const error = await response.json();
      throw new Error(error.message);
    }
  }
}
```

### Поиск сослуживцев

```javascript
class ComradesService {
  constructor(authService) {
    this.authService = authService;
    this.baseUrl = 'http://172.16.79.233:5000/api/comrades';
  }

  async searchComrades(searchCriteria = {}) {
    const params = new URLSearchParams();
    
    // Фильтрация пустых значений
    Object.entries(searchCriteria).forEach(([key, value]) => {
      if (value !== undefined && value !== '') {
        params.append(key, value);
      }
    });

    const response = await fetch(`${this.baseUrl}?${params}`);
    
    if (response.ok) {
      return await response.json();
    } else {
      throw new Error('Failed to search comrades');
    }
  }

  async addComrade(comradeData) {
    // Валидация обязательных полей
    const requiredFields = ['firstName', 'lastName', 'unit', 'region', 'yearOfServiceFrom'];
    const missingFields = requiredFields.filter(field => !comradeData[field]);
    
    if (missingFields.length > 0) {
      throw new Error(`Missing required fields: ${missingFields.join(', ')}`);
    }

    const response = await fetch(this.baseUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(comradeData),
    });

    if (response.ok) {
      return await response.json();
    } else {
      const error = await response.json();
      throw new Error(error.message);
    }
  }

  async getComrade(id) {
    const response = await fetch(`${this.baseUrl}/${id}`);
    
    if (response.ok) {
      return await response.json();
    } else if (response.status === 404) {
      throw new Error('Comrade not found');
    } else {
      throw new Error('Failed to fetch comrade');
    }
  }
}
```

### Управление файлами

```javascript
class FilesService {
  constructor(authService) {
    this.authService = authService;
    this.baseUrl = 'http://172.16.79.233:5000/api/files';
  }

  async uploadFile(file, type, category = 'other') {
    // Валидация файла
    const maxSizes = {
      pdf: 10 * 1024 * 1024,  // 10MB
      image: 5 * 1024 * 1024  // 5MB
    };

    if (file.size > maxSizes[type]) {
      throw new Error(`File too large. Maximum size for ${type} is ${maxSizes[type] / 1024 / 1024}MB`);
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('type', type);
    formData.append('category', category);

    const response = await fetch(`${this.baseUrl}/upload`, {
      method: 'POST',
      headers: this.authService.getAuthHeaders(),
      body: formData,
    });

    if (response.ok) {
      return await response.json();
    } else {
      const error = await response.json();
      throw new Error(error.message);
    }
  }

  async getFiles(filters = {}) {
    const params = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== '') {
        params.append(key, value);
      }
    });

    const response = await fetch(`${this.baseUrl}?${params}`, {
      headers: this.authService.getAuthHeaders(),
    });

    if (response.ok) {
      return await response.json();
    } else {
      throw new Error('Failed to fetch files');
    }
  }

  async deleteFile(id) {
    const response = await fetch(`${this.baseUrl}/${id}`, {
      method: 'DELETE',
      headers: this.authService.getAuthHeaders(),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message);
    }
  }

  getFileUrl(filename) {
    return `${this.baseUrl}/uploads/${filename}`;
  }
}
```

### Пример полного React Hook

```javascript
import { useState, useEffect } from 'react';

// Custom hook для работы с API
function useVeteranAPI() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const authService = new AuthService();
  const lawsService = new LawsService(authService);
  const newsService = new NewsService(authService);
  const comradesService = new ComradesService(authService);
  const filesService = new FilesService(authService);

  useEffect(() => {
    // Проверить токен при загрузке
    if (authService.isAuthenticated()) {
      setIsAuthenticated(true);
      // Можно добавить верификацию токена
    }
  }, []);

  const login = async (username, password) => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await authService.login(username, password);
      setIsAuthenticated(true);
      setUser(data.user);
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    setLoading(true);
    
    try {
      await authService.logout();
      setIsAuthenticated(false);
      setUser(null);
    } catch (err) {
      console.error('Logout error:', err);
    } finally {
      setLoading(false);
    }
  };

  return {
    // State
    isAuthenticated,
    user,
    loading,
    error,
    
    // Auth methods
    login,
    logout,
    
    // Services
    lawsService,
    newsService,
    comradesService,
    filesService,
    
    // Utility
    clearError: () => setError(null),
  };
}

export default useVeteranAPI;
```

### Пример компонента для загрузки файлов

```javascript
import React, { useState } from 'react';

function FileUploader({ filesService, onUploadComplete }) {
  const [file, setFile] = useState(null);
  const [type, setType] = useState('pdf');
  const [category, setCategory] = useState('other');
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!file) {
      setError('Please select a file');
      return;
    }

    setUploading(true);
    setError(null);

    try {
      const result = await filesService.uploadFile(file, type, category);
      onUploadComplete(result);
      setFile(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label>
          File:
          <input
            type="file"
            onChange={(e) => setFile(e.target.files[0])}
            accept={type === 'pdf' ? '.pdf' : 'image/*'}
          />
        </label>
      </div>
      
      <div>
        <label>
          Type:
          <select value={type} onChange={(e) => setType(e.target.value)}>
            <option value="pdf">PDF</option>
            <option value="image">Image</option>
          </select>
        </label>
      </div>
      
      <div>
        <label>
          Category:
          <select value={category} onChange={(e) => setCategory(e.target.value)}>
            <option value="law">Law</option>
            <option value="news">News</option>
            <option value="photo">Photo</option>
            <option value="other">Other</option>
          </select>
        </label>
      </div>

      {error && <div style={{ color: 'red' }}>{error}</div>}
      
      <button type="submit" disabled={uploading || !file}>
        {uploading ? 'Uploading...' : 'Upload'}
      </button>
    </form>
  );
}
```

---

## Заключение

Данная документация предоставляет полное описание всех API endpoints для интеграции фронтенда с backend приложения Ассоциации Ветеранов. 

### Ключевые моменты:

1. **Аутентификация обязательна** для всех операций создания, обновления и удаления
2. **Многоязычная поддержка** - все тексты должны быть на трех языках (ru, uz, en)
3. **Валидация данных** - серверная валидация для всех входящих данных
4. **Пагинация** - все списковые endpoints поддерживают пагинацию
5. **Фильтрация и поиск** - расширенные возможности поиска и фильтрации
6. **Обработка ошибок** - единообразный формат ошибок с детальными сообщениями

### Рекомендации для разработки:

Для получения дополнительной информации обращайтесь к OpenAPI спецификации по адресу `/api/swagger.json`.