# Math Learning Calculators

Учебные математические калькуляторы: алгебра, уравнения, симплекс-метод, транспортная задача и системы линейных уравнений.

## Структура

- `frontend` - React/Vite приложение.
- `backend` - FastAPI API.

## Локальный запуск

Backend:

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

## Переменные окружения

Frontend:

```text
VITE_API_URL=http://127.0.0.1:8000
```

Backend:

```text
FRONTEND_ORIGIN=http://localhost:5173
```

Для публикации `FRONTEND_ORIGIN` должен быть адресом сайта на Vercel.
