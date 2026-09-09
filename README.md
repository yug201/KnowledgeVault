# Personal Knowledge Vault

Personal Knowledge Vault is a full-stack web application for privately managing notes, links, images, PDFs, tags, and personal tasks. It provides a Streamlit dashboard for users and a FastAPI backend that stores application data in PostgreSQL and uploads files to ImageKit.

## Deployment status

The application is deployed on **Render**. Streamlit is the frontend/dashboard technology, while FastAPI runs the backend API. The deployed Streamlit service communicates with the deployed API through its Render URL.

> Add the public URLs here when sharing the project:
>
> - Frontend: `https://knowvault.streamlit.app/`
> - API: `https://knowledgevault-3bqk.onrender.com`
> - API documentation: `https://knowledgevault-3bqk.onrender.com/docs`

## Core capabilities

- Secure account registration and sign-in
- JWT-based access control for private user data
- Create, read, update, and delete knowledge entries
- Save text notes and external URLs
- Upload images and PDFs, with file hosting provided by ImageKit
- Add tags to knowledge entries
- Create, complete, edit, and delete todos
- Ensure each authenticated user can access only their own knowledge and tasks

## System architecture

```text
┌─────────────────────┐
│ User's web browser  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐       HTTPS / JSON        ┌─────────────────────┐
│ Streamlit frontend  │ ─────────────────────────► │ FastAPI backend    │
│ app.py              │ ◄───────────────────────── │ app/main.py        │
└─────────────────────┘        JSON response       └───────┬─────┬─────┘
                                                            │     │
                                      SQLAlchemy (async) ───┘     └── ImageKit SDK
                                                            │              │
                                                            ▼              ▼
                                                  ┌──────────────┐  ┌──────────┐
                                                  │ PostgreSQL   │  │ ImageKit │
                                                  └──────────────┘  └──────────┘
```

### Request lifecycle

For example, when a user creates a knowledge item:

1. The user submits the form in the Streamlit dashboard.
2. `app.py` sends a `POST /knowledge` request to the FastAPI API.
3. FastAPI checks the JWT token sent in the `Authorization` header.
4. The backend identifies the user and validates the payload with Pydantic.
5. The knowledge service saves the item and tag relations in PostgreSQL.
6. FastAPI returns the created item as JSON.
7. Streamlit reloads the vault list and shows the new item.

For an uploaded image or PDF, the backend first creates the knowledge item, uploads the file to ImageKit, then stores the resulting file URL and file metadata in PostgreSQL.

## Technology stack

| Layer | Technology | Purpose |
| --- | --- | --- |
| Frontend | Streamlit | Builds the interactive dashboard, forms, task list, and vault view. |
| HTTP client | Requests | Sends API requests from Streamlit to FastAPI. |
| Backend | FastAPI | Exposes REST API endpoints and manages request handling. |
| Validation | Pydantic | Validates request input and shapes API responses. |
| ORM | SQLAlchemy 2.0 (async) | Maps Python models to database tables and performs async queries. |
| Database driver | asyncpg | Async PostgreSQL driver used by SQLAlchemy. |
| Database | PostgreSQL | Persists users, knowledge items, tags, and todos. |
| Authentication | PyJWT + pwdlib | Creates/verifies JWTs and securely hashes passwords. |
| File storage | ImageKit | Stores uploaded images and PDFs outside the application server. |
| Deployment | Render | Hosts the deployed services and PostgreSQL database. |
| Application server | Uvicorn | Runs the FastAPI ASGI application in production. |

## Project structure

```text
.
├── app.py                    # Streamlit user interface
├── app/
│   ├── main.py               # FastAPI application, startup, router registration
│   ├── dependencies.py       # JWT verification and current-user dependency
│   ├── core/
│   │   ├── config.py         # Reads environment configuration
│   │   └── security.py       # Password hashing and JWT creation
│   ├── db/
│   │   ├── database.py       # Async SQLAlchemy engine and sessions
│   │   └── models.py         # User, KnowledgeItem, Todo, and Tag tables
│   ├── schemas/              # Pydantic request and response contracts
│   ├── routes/               # API URL handlers
│   └── services/             # Business logic and database operations
├── requirements.txt          # Pinned Python dependencies
├── .env                      # Local-only environment variables; never commit
└── README.md                 # Project documentation
```

## Frontend: Streamlit dashboard

`app.py` is the frontend entry point. It controls the visual application and uses `st.session_state` to retain the JWT access token while the user is logged in.

### User interface features

- Sign-in and registration tabs
- Knowledge-entry form for TEXT, URL, IMAGE, and PDF entries
- Upload control for supported files
- Two-column vault card grid
- Entry editing and deletion controls
- Todo sidebar with completion checkboxes and deletion controls
- Logout action that clears the token from Streamlit session state

### API configuration

The frontend reads the backend URL from `BASE_URL`:

```python
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
```

Local development uses `http://localhost:8000`. On Render, set `BASE_URL` to the public URL of the deployed FastAPI service.

## Backend: FastAPI API

`app/main.py` creates the FastAPI application and includes four routers:

| Router | Prefix | Responsibility |
| --- | --- | --- |
| `auth` | `/auth` | Registration, login, and current-user lookup |
| `knowledge` | `/knowledge` | Knowledge item CRUD operations |
| `todos` | `/todos` | Todo CRUD operations |
| `files` | `/knowledge` | File upload for a knowledge item |

At startup, the backend runs `Base.metadata.create_all`, which creates missing database tables. This is useful for a small project; production schema changes should eventually use Alembic migrations.

## Database design

### Main tables

| Table | Important fields | Description |
| --- | --- | --- |
| `users` | `id`, `email`, `password_hash`, `created_at` | Registered user accounts. |
| `knowledge_items` | `id`, `user_id`, `type`, `title`, `content`, `file_url` | Notes, URLs, and uploaded-file metadata. |
| `todos` | `id`, `user_id`, `title`, `completed` | A user's task list. |
| `tags` | `id`, `name` | Reusable tag names. |
| `knowledge_item_tags` | `knowledge_item_id`, `tag_id` | Many-to-many relationship between knowledge entries and tags. |

### Data relationships

```text
User 1 ──────── * KnowledgeItem
User 1 ──────── * Todo
KnowledgeItem * ──────── * Tag
```

All primary IDs are UUID strings. Every knowledge-item and todo query includes the authenticated user's ID, preventing users from reading or changing another user's records.

## Authentication and authorization

1. A user registers with an email and password.
2. The password is hashed with `pwdlib` before it is stored.
3. At login, the submitted password is verified against the stored hash.
4. The backend creates a signed JWT containing the user ID in the `sub` claim.
5. Streamlit saves that JWT in its session state.
6. Requests to protected endpoints include:

```text
Authorization: Bearer <access_token>
```

7. `get_current_user` decodes the token, retrieves the user from PostgreSQL, and injects that user into protected route handlers.

The token expiry is controlled by `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`, which defaults to 30 minutes.

## API reference

### Authentication

| Method | Endpoint | Authentication | Description |
| --- | --- | --- | --- |
| POST | `/auth/register` | No | Creates a user account. |
| POST | `/auth/login` | No | Validates credentials and returns a JWT. |
| GET | `/auth/me` | Yes | Returns the authenticated user. |

### Knowledge

| Method | Endpoint | Description |
| --- | --- | --- |
| POST | `/knowledge` | Create a knowledge entry. |
| GET | `/knowledge` | List the current user's knowledge entries, newest first. |
| GET | `/knowledge/{knowledge_id}` | Get one knowledge entry. |
| PUT | `/knowledge/{knowledge_id}` | Update title, description, content, or tags. |
| DELETE | `/knowledge/{knowledge_id}` | Delete a knowledge entry. |
| POST | `/knowledge/{knowledge_id}/file` | Upload a file for an existing entry. |

### Todos

| Method | Endpoint | Description |
| --- | --- | --- |
| POST | `/todos` | Create a todo. |
| GET | `/todos` | List the current user's todos, newest first. |
| GET | `/todos/{todo_id}` | Get one todo. |
| PUT | `/todos/{todo_id}` | Update title, description, or completion state. |
| DELETE | `/todos/{todo_id}` | Delete a todo. |

FastAPI's live, interactive endpoint documentation is available at `/docs`.

## File uploads

Allowed MIME types are:

```text
image/jpeg
image/png
image/webp
application/pdf
video/mp4
```

The maximum upload size is **10 MB**. The API sends valid file bytes to ImageKit, then saves the file URL, original filename, and MIME type against its knowledge item.

## Environment variables

Create a local `.env` file. Do not commit it to source control.

```env
# PostgreSQL connection, using SQLAlchemy's asyncpg dialect
DATABASE_URL=postgresql+asyncpg://USERNAME:PASSWORD@HOST:5432/DATABASE_NAME

# JWT settings
JWT_SECRET_KEY=replace-with-a-long-random-secret
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# ImageKit file storage
IMAGEKIT_PUBLIC_KEY=your-imagekit-public-key
IMAGEKIT_PRIVATE_KEY=your-imagekit-private-key
IMAGEKIT_URL_ENDPOINT=https://ik.imagekit.io/your_imagekit_id

# Frontend-to-backend address
BASE_URL=http://localhost:8000
```

## Run locally

### Prerequisites

- Python 3.12 or compatible version
- A PostgreSQL database
- An ImageKit account and credentials

### Setup

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Add the environment values above to `.env`.

### Start the backend

```powershell
uvicorn app.main:app --reload
```

The API is available at `http://localhost:8000`, and its Swagger documentation is at `http://localhost:8000/docs`.

### Start the frontend

In another terminal:

```powershell
.\venv\Scripts\Activate.ps1
streamlit run app.py
```

The dashboard normally opens at `http://localhost:8501`.

## Render deployment configuration

### 1. Render Postgres

Create a Render Postgres database in the same region as the API. Copy its **internal connection URL** and use it for `DATABASE_URL`. Because this project uses SQLAlchemy asyncpg, use this prefix:

```text
postgresql+asyncpg://
```

instead of the standard `postgresql://` prefix.

### 2. FastAPI web service

| Setting | Value |
| --- | --- |
| Runtime | Python 3 |
| Build command | `pip install -r requirements.txt` |
| Start command | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Health-check path | `/` |

Configure `DATABASE_URL`, all `JWT_*` variables, and all `IMAGEKIT_*` variables in the Render dashboard's Environment section.

### 3. Streamlit web service

| Setting | Value |
| --- | --- |
| Runtime | Python 3 |
| Build command | `pip install -r requirements.txt` |
| Start command | `streamlit run app.py --server.address 0.0.0.0 --server.port $PORT` |
| Environment variable | `BASE_URL=https://<your-api-service>.onrender.com` |

Once both services deploy, open the Streamlit service URL. The dashboard sends all application requests to the FastAPI URL configured in `BASE_URL`.

## Security considerations

- Never expose `.env`, database credentials, ImageKit keys, or JWT secrets.
- Use a long random value for `JWT_SECRET_KEY` in production.
- Keep `.env`, `venv/`, and `__pycache__/` in `.gitignore`.
- Use HTTPS Render URLs for deployed services.
- Passwords are never stored as plain text; only password hashes are stored.
- Protected queries are filtered by the current user's ID.

## Current limitations and recommended next steps

- Add automated unit and API tests.
- Use Alembic for safe database migrations.
- Delete files from ImageKit when the corresponding knowledge item is deleted.
- Add search, filters, pagination, and tag management.
- Add rate limiting and login-attempt protections.
- Validate URL content and enforce stronger password requirements.
- Add centralized logging and error monitoring for production.

## License

Add a license file, such as MIT, before publishing this repository publicly.
