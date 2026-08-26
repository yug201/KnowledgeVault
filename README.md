# Personal Knowledge Vault

A full-stack personal knowledge manager. Users can create accounts, save notes and links, upload files, organize entries with tags, and manage a personal todo list.

## Features

- User registration and login with JWT authentication
- Personal knowledge entries: text notes, URLs, images, and PDFs
- Tags for organizing knowledge entries
- Image and PDF uploads stored through ImageKit
- Create, update, complete, and delete todos
- Data isolation: each user can access only their own entries and todos

## Tech stack

| Area | Technology |
| --- | --- |
| Dashboard | Streamlit |
| API | FastAPI |
| Database access | SQLAlchemy (async) |
| Database | PostgreSQL |
| Authentication | JWT + password hashing with `pwdlib` |
| File storage | ImageKit |

## Project structure

```text
.
├── app.py                 # Streamlit dashboard
├── app/
│   ├── main.py            # FastAPI application entry point
│   ├── core/              # Configuration and security helpers
│   ├── db/                # Database engine and SQLAlchemy models
│   ├── routes/            # API endpoint definitions
│   ├── schemas/           # Request/response validation models
│   └── services/          # Application and database logic
├── requirements.txt       # Python dependencies
└── .env                   # Local secrets (do not commit)
```

## How it works

```text
Browser
  ↓
Streamlit dashboard (app.py)
  ↓ HTTP requests
FastAPI API (app/main.py)
  ↓
PostgreSQL database + ImageKit file storage
```

The dashboard sends requests to the FastAPI API. The API validates the request, confirms the user is logged in, saves or retrieves data from PostgreSQL, and returns JSON to the dashboard.

## Local setup

### 1. Create and activate a virtual environment

On Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

> The current app also uses `streamlit`, `requests`, `PyJWT`, `imagekitio`, and `python-multipart`. Ensure they are present in `requirements.txt` before setting up on a new computer.

### 3. Create `.env`

Create a file named `.env` in the project root:

```env
DATABASE_URL=postgresql+asyncpg://USERNAME:PASSWORD@HOST:5432/DATABASE_NAME
JWT_SECRET_KEY=replace-with-a-long-random-secret
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
IMAGEKIT_PUBLIC_KEY=your-imagekit-public-key
IMAGEKIT_PRIVATE_KEY=your-imagekit-private-key
IMAGEKIT_URL_ENDPOINT=https://ik.imagekit.io/your_imagekit_id
```

Never commit this file to GitHub.

### 4. Start the FastAPI backend

Open a terminal in the project folder:

```powershell
uvicorn app.main:app --reload
```

The API runs at `http://localhost:8000`.

FastAPI also provides interactive documentation at:

```text
http://localhost:8000/docs
```

### 5. Start the Streamlit dashboard

Open a second terminal, activate the virtual environment, then run:

```powershell
streamlit run app.py
```

Streamlit opens the dashboard in your browser, normally at `http://localhost:8501`.

## API endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| POST | `/auth/register` | Create an account |
| POST | `/auth/login` | Log in and receive an access token |
| GET | `/auth/me` | Get the logged-in user |
| GET, POST | `/knowledge` | List or create knowledge entries |
| GET, PUT, DELETE | `/knowledge/{knowledge_id}` | Read, edit, or delete an entry |
| POST | `/knowledge/{knowledge_id}/file` | Upload an image, PDF, or supported file |
| GET, POST | `/todos` | List or create todos |
| GET, PUT, DELETE | `/todos/{todo_id}` | Read, edit, or delete a todo |

All endpoints except registration and login require this request header:

```text
Authorization: Bearer <access_token>
```

## Deploying on Render

Deploy three resources in Render:

1. A Render Postgres database
2. A FastAPI Web Service
3. A Streamlit Web Service

### FastAPI service

| Setting | Value |
| --- | --- |
| Build command | `pip install -r requirements.txt` |
| Start command | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |

Set the same environment variables as in `.env`. Use the Render database's internal URL, changing its prefix from `postgresql://` to `postgresql+asyncpg://`.

### Streamlit service

Update `app.py` so the API URL comes from an environment variable:

```python
import os

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
```

Then configure the service:

| Setting | Value |
| --- | --- |
| Build command | `pip install -r requirements.txt` |
| Start command | `streamlit run app.py --server.address 0.0.0.0 --server.port $PORT` |
| Environment variable | `BASE_URL=https://your-api-name.onrender.com` |

## Security notes

- Keep `.env`, database URLs, JWT secrets, and ImageKit keys private.
- Add `.env`, `venv/`, and `__pycache__/` to `.gitignore`.
- Use a long, random `JWT_SECRET_KEY` in production.
- The application currently creates database tables at API startup. For production schema changes, use database migrations such as Alembic.

## Future improvements

- Complete and pin `requirements.txt`
- Add automated tests
- Add search and filtering for knowledge entries
- Add file deletion from ImageKit when an entry is deleted
- Add pagination for large collections
- Add stronger input validation and user-friendly error messages
