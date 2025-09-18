# Поиск Однополчан - API Документация

Данная документация описывает функциональность поиска и управления данными сослуживцев (однополчан) в системе Ассоциации Ветеранов.

## Обзор функциональности

Система предоставляет следующие возможности:
- **Поиск сослуживцев** по различным параметрам (имя, часть, регион, год службы)
- **Добавление сослуживцев** по одному через API
- **Массовый импорт** сослуживцев из Excel файла
- **Управление данными** сослуживцев (обновление, удаление)

## 🔍 Поиск Сослуживцев

### Базовый поиск

```http
GET /api/comrades
```

**Описание:** Поиск сослуживцев по различным параметрам с поддержкой пагинации.

**Query Parameters (все опциональные):**

| Параметр | Тип | Описание | Пример |
|----------|-----|----------|---------|
| `name` | string | Поиск по имени, фамилии или отчеству | `Иванов` |
| `unit` | string | Поиск по воинской части или соединению | `12345` |
| `region` | string | Поиск по региону службы | `Ташкент` |
| `yearFrom` | number | Год службы от | `1990` |
| `yearTo` | number | Год службы до | `1995` |
| `rank` | string | Воинское звание | `Сержант` |
| `limit` | number | Количество результатов (по умолчанию 50, максимум 100) | `20` |
| `offset` | number | Смещение для пагинации (по умолчанию 0) | `0` |

**Примеры запросов:**

```bash
# Поиск по имени
GET /api/comrades?name=Иванов

# Поиск по части
GET /api/comrades?unit=12345

# Поиск по региону
GET /api/comrades?region=Ташкент

# Поиск по году службы
GET /api/comrades?yearFrom=1990&yearTo=1995

# Комбинированный поиск
GET /api/comrades?name=Иванов&unit=123&region=Ташкент&yearFrom=1990&yearTo=1995

# Поиск с пагинацией
GET /api/comrades?limit=20&offset=40
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
  "total": 1,
  "limit": 50,
  "offset": 0
}
```

## ➕ Добавление Сослуживца

### Добавить одного сослуживца

```http
POST /api/comrades
```

**Описание:** Добавление информации об одном сослуживце.

**Request Body:**
```json
{
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
  "additionalInfo": "Дополнительная информация о службе"
}
```

**Обязательные поля:**
- `firstName` - имя
- `lastName` - фамилия
- `unit` - воинская часть
- `region` - регион службы
- `yearOfServiceFrom` - год начала службы

**Опциональные поля:**
- `middleName` - отчество
- `yearOfServiceTo` - год окончания службы
- `rank` - воинское звание
- `photoUrl` - ссылка на фотографию
- `contactInfo` - контактная информация
  - `phone` - телефон (формат: +[код страны][номер])
  - `email` - электронная почта
  - `address` - адрес
- `additionalInfo` - дополнительная информация

**Response 201:**
```json
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
  "isVerified": false,
  "createdAt": "2023-01-15T10:30:00Z",
  "updatedAt": "2023-01-15T10:30:00Z"
}
```

## 📊 Массовый Импорт из Excel

### Импорт сослуживцев из Excel файла

```http
POST /api/comrades/bulk-import
```

**Описание:** Массовый импорт сослуживцев из Excel файла.

**Требует авторизации:** ✅ Да

**Request:** Multipart form data с Excel файлом

**Parameters:**
- `file` - Excel файл (.xlsx или .xls)

**Формат Excel файла:**

| Колонка | Обязательна | Описание | Пример |
|---------|-------------|----------|---------|
| Фамилия | ✅ | Фамилия сослуживца | Иванов |
| Имя | ✅ | Имя сослуживца | Иван |
| Отчество | ❌ | Отчество сослуживца | Петрович |
| Воинская часть | ✅ | Номер части или соединение | Воинская часть 12345 |
| Регион | ✅ | Регион службы | Ташкентская область |
| Год службы с | ✅ | Год начала службы | 1990 |
| Год службы по | ❌ | Год окончания службы | 1992 |
| Звание | ❌ | Воинское звание | Сержант |
| Телефон | ❌ | Контактный телефон | +998901234567 |
| Email | ❌ | Электронная почта | ivanov@example.com |
| Адрес | ❌ | Почтовый адрес | г. Ташкент, ул. Примерная 123 |
| Дополнительная информация | ❌ | Дополнительные сведения | Служил в танковых войсках |

**Пример запроса:**
```bash
curl -X POST http://localhost:5000/api/comrades/bulk-import \
  -H "Authorization: Bearer <your-jwt-token>" \
  -F "file=@comrades.xlsx"
```

**Response 200 (успешный импорт):**
```json
{
  "success": true,
  "message": "Импорт завершен. Импортировано: 15, пропущено: 2",
  "statistics": {
    "imported": 15,
    "skipped": 2,
    "total_processed": 17
  },
  "warnings": [
    "Строка 3: Пропущен год в поле 'Год службы по': не указан"
  ],
  "import_errors": [
    "Строка 5: Сослуживец уже существует (Петр Петров, Воинская часть 123)",
    "Строка 8: Неверный формат года в поле 'Год службы с': abc"
  ],
  "timestamp": "2023-06-20T14:45:00Z"
}
```

**Response 400 (ошибки валидации):**
```json
{
  "error": "Import validation failed",
  "message": "Найдены ошибки в файле",
  "details": {
    "errors": [
      "Отсутствуют обязательные колонки: Фамилия, Имя"
    ],
    "warnings": []
  },
  "timestamp": "2023-06-20T14:45:00Z"
}
```

### Скачать образец Excel файла

```http
GET /api/comrades/bulk-import/sample
```

**Описание:** Получить образец Excel файла для импорта.

**Требует авторизации:** ✅ Да

**Response 200:**
```json
{
  "message": "Sample file created successfully",
  "download_instructions": "Use the file path provided to download the sample Excel file",
  "file_path": "/tmp/sample_comrades_import_20231220_143000.xlsx",
  "columns": {
    "required": ["Фамилия", "Имя", "Воинская часть", "Регион", "Год службы с"],
    "optional": ["Отчество", "Год службы по", "Звание", "Телефон", "Email", "Адрес", "Дополнительная информация"]
  },
  "timestamp": "2023-06-20T14:45:00Z"
}
```

## 🔧 Управление Данными

### Получить данные сослуживца

```http
GET /api/comrades/{id}
```

**Response 200:**
```json
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
```

### Обновить данные сослуживца

```http
PUT /api/comrades/{id}
```

**Требует авторизации:** ✅ Да

**Request Body:** Аналогично POST запросу для создания

### Удалить сослуживца

```http
DELETE /api/comrades/{id}
```

**Требует авторизации:** ✅ Да

**Response 204:** Успешное удаление (без содержимого)

## 📝 Примеры Интеграции для Frontend

### JavaScript/TypeScript

#### Класс для работы с API сослуживцев

```javascript
class ComradesService {
  constructor(apiBaseUrl, authService) {
    this.baseUrl = `${apiBaseUrl}/comrades`;
    this.authService = authService;
  }

  // Поиск сослуживцев
  async searchComrades(filters = {}) {
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
      const error = await response.json();
      throw new Error(error.message);
    }
  }

  // Добавить сослуживца
  async addComrade(comradeData) {
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

  // Массовый импорт из Excel
  async bulkImport(file) {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${this.baseUrl}/bulk-import`, {
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

  // Получить образец Excel файла
  async getSampleExcel() {
    const response = await fetch(`${this.baseUrl}/bulk-import/sample`, {
      headers: this.authService.getAuthHeaders(),
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

#### React компонент для поиска

```jsx
import React, { useState, useEffect } from 'react';

function ComradesSearch({ comradesService }) {
  const [filters, setFilters] = useState({
    name: '',
    unit: '',
    region: '',
    yearFrom: '',
    yearTo: '',
    rank: ''
  });
  
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [pagination, setPagination] = useState({ offset: 0, limit: 20 });

  const handleSearch = async () => {
    setLoading(true);
    try {
      const response = await comradesService.searchComrades({
        ...filters,
        ...pagination
      });
      setResults(response.comrades);
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (field, value) => {
    setFilters(prev => ({ ...prev, [field]: value }));
  };

  return (
    <div className="comrades-search">
      <div className="search-form">
        <input
          type="text"
          placeholder="Имя, фамилия, отчество"
          value={filters.name}
          onChange={(e) => handleFilterChange('name', e.target.value)}
        />
        
        <input
          type="text"
          placeholder="Воинская часть"
          value={filters.unit}
          onChange={(e) => handleFilterChange('unit', e.target.value)}
        />
        
        <input
          type="text"
          placeholder="Регион"
          value={filters.region}
          onChange={(e) => handleFilterChange('region', e.target.value)}
        />
        
        <input
          type="number"
          placeholder="Год службы с"
          value={filters.yearFrom}
          onChange={(e) => handleFilterChange('yearFrom', e.target.value)}
        />
        
        <input
          type="number"
          placeholder="Год службы по"
          value={filters.yearTo}
          onChange={(e) => handleFilterChange('yearTo', e.target.value)}
        />
        
        <button onClick={handleSearch} disabled={loading}>
          {loading ? 'Поиск...' : 'Найти'}
        </button>
      </div>

      <div className="search-results">
        {results.map(comrade => (
          <div key={comrade.id} className="comrade-card">
            <h3>{comrade.lastName} {comrade.firstName} {comrade.middleName}</h3>
            <p><strong>Часть:</strong> {comrade.unit}</p>
            <p><strong>Регион:</strong> {comrade.region}</p>
            <p><strong>Годы службы:</strong> {comrade.yearOfServiceFrom} - {comrade.yearOfServiceTo || 'н.в.'}</p>
            {comrade.rank && <p><strong>Звание:</strong> {comrade.rank}</p>}
            {comrade.contactInfo?.phone && <p><strong>Телефон:</strong> {comrade.contactInfo.phone}</p>}
            {comrade.contactInfo?.email && <p><strong>Email:</strong> {comrade.contactInfo.email}</p>}
          </div>
        ))}
      </div>
    </div>
  );
}
```

#### React компонент для импорта Excel

```jsx
import React, { useState } from 'react';

function ExcelImporter({ comradesService, onImportComplete }) {
  const [file, setFile] = useState(null);
  const [importing, setImporting] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setError(null);
    setResult(null);
  };

  const handleImport = async () => {
    if (!file) {
      setError('Пожалуйста, выберите файл');
      return;
    }

    setImporting(true);
    setError(null);

    try {
      const result = await comradesService.bulkImport(file);
      setResult(result);
      onImportComplete?.(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setImporting(false);
    }
  };

  const downloadSample = async () => {
    try {
      await comradesService.getSampleExcel();
      // В реальном приложении здесь должно быть скачивание файла
      alert('Образец файла создан. Обратитесь к администратору для получения файла.');
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="excel-importer">
      <h3>Импорт из Excel</h3>
      
      <div className="file-input">
        <input
          type="file"
          accept=".xlsx,.xls"
          onChange={handleFileChange}
        />
        <button onClick={downloadSample}>Скачать образец</button>
      </div>

      <button 
        onClick={handleImport} 
        disabled={!file || importing}
      >
        {importing ? 'Импорт...' : 'Импортировать'}
      </button>

      {error && (
        <div className="error">
          <p style={{color: 'red'}}>{error}</p>
        </div>
      )}

      {result && (
        <div className="import-result">
          <h4>Результат импорта:</h4>
          <p>✅ Импортировано: {result.statistics.imported}</p>
          <p>⚠️ Пропущено: {result.statistics.skipped}</p>
          
          {result.warnings?.length > 0 && (
            <div>
              <h5>Предупреждения:</h5>
              <ul>
                {result.warnings.map((warning, i) => (
                  <li key={i} style={{color: 'orange'}}>{warning}</li>
                ))}
              </ul>
            </div>
          )}
          
          {result.import_errors?.length > 0 && (
            <div>
              <h5>Ошибки:</h5>
              <ul>
                {result.import_errors.map((error, i) => (
                  <li key={i} style={{color: 'red'}}>{error}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
```

## 🚨 Обработка Ошибок

### Стандартные коды ошибок

| Код | Описание | Пример ответа |
|-----|----------|---------------|
| 400 | Ошибка валидации | `{"error": "Validation Error", "message": "Request validation failed"}` |
| 401 | Неавторизован | `{"error": "Unauthorized", "message": "Token required"}` |
| 404 | Не найден | `{"error": "Not Found", "message": "Comrade not found"}` |
| 500 | Внутренняя ошибка сервера | `{"error": "Internal Server Error", "message": "Database error"}` |

### Валидация данных

#### Обязательные поля при создании:
- `firstName` - должно быть не пустым
- `lastName` - должно быть не пустым  
- `unit` - должно быть не пустым
- `region` - должно быть не пустым
- `yearOfServiceFrom` - должно быть числом в диапазоне 1900-текущий год

#### Правила валидации:
- Год службы должен быть в диапазоне 1900 - текущий год
- Год окончания службы не может быть раньше года начала службы
- Телефон должен начинаться с '+' и содержать минимум 10 символов
- Email должен содержать '@' и '.'

## 🔐 Авторизация

Некоторые операции требуют авторизации:
- ✅ Поиск сослуживцев - **без авторизации**
- ✅ Просмотр данных сослуживца - **без авторизации**
- ✅ Добавление сослуживца - **без авторизации**
- 🔒 Обновление данных - **требует авторизации**
- 🔒 Удаление - **требует авторизации**
- 🔒 Массовый импорт - **требует авторизации**
- 🔒 Скачивание образца - **требует авторизации**

Для авторизованных запросов необходимо передавать JWT токен в заголовке:
```
Authorization: Bearer <your-jwt-token>
```

## 📞 Поддержка

При возникновении вопросов или проблем:
1. Проверьте формат данных согласно документации
2. Убедитесь в корректности авторизации для защищенных операций
3. Обратитесь к разработчикам API за поддержкой

---

*Документация обновлена: 2024-01-01*