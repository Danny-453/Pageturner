# PageTurners API

FastAPI service for PageTurners. The API uses PostgreSQL, SQLAlchemy, Alembic migrations, and bearer-token authentication.

## Requirements

- Python 3.12+
- PostgreSQL, either Neon or the provided Docker Compose service

## Local setup (PowerShell)

Run the following from the `Backend` directory:

```powershell
Copy-Item .env.example .env
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Edit `.env` and configure `DATABASE_URL` for your PostgreSQL provider:

- **Neon:** copy the connection string from the Neon console. Use the direct endpoint while applying migrations; append `sslmode=require` if it is not already present, and use the SQLAlchemy/Psycopg scheme `postgresql+psycopg://`. For example:

  ```text
  postgresql+psycopg://USER:PASSWORD@HOST/DBNAME?sslmode=require
  ```

  Replace the placeholders with the values from Neon. The Neon pooled endpoint (host containing `-pooler`) can be used for the running API when you need connection pooling; use the direct endpoint for `alembic upgrade head`. If the password contains URL-reserved characters, percent-encode it before putting it in the URL.

- **Local Docker PostgreSQL:** keep the example value `postgresql+psycopg://pageturners:pageturners@localhost:5432/pageturners` and start the included database with `docker compose up -d postgres`.

- `SECRET_KEY` to a long, random value (at least 32 characters)
- `SEED_ADMIN_EMAIL` and `SEED_STUDENT_EMAIL` to the login email addresses you want for the optional seeded accounts. The defaults use valid email domains.
- `SEED_ADMIN_PASSWORD` and `SEED_STUDENT_PASSWORD` to create the seeded admin and student accounts (both must be set; student registration works without them)
- `CORS_ORIGINS` to include the Vite frontend origin (the example includes `http://localhost:5173` and `http://127.0.0.1:5173`)
- `FRONTEND_URL` to the frontend origin used in password reset links
- `SMTP_HOST`, `SMTP_PORT`, and `SMTP_SENDER_EMAIL` to enable password reset emails; set `SMTP_USERNAME` and `SMTP_PASSWORD` if your SMTP provider requires authentication. Use `SMTP_USE_SSL=true` for implicit TLS (typically port 465); otherwise the server uses STARTTLS (typically port 587).

Then initialize the database and start the API. Run migrations against the direct Neon endpoint, and use the same `DATABASE_URL` for seeding:

```powershell
python -m alembic upgrade head
python seed.py
python -m uvicorn app.main:app --reload
```

The API is available at `http://localhost:8000`; interactive docs are at `http://localhost:8000/docs`. When both seed passwords are configured, the seed creates the accounts using `SEED_ADMIN_EMAIL` and `SEED_STUDENT_EMAIL`. Existing legacy accounts ending in `@pageturners.local` are updated to those configured addresses when you rerun `python seed.py`; their existing passwords are unchanged. To enable content management in the frontend, sign in using `SEED_ADMIN_EMAIL` and `SEED_ADMIN_PASSWORD`. Without the passwords, the seed still installs reference and course data so students can register normally, but it does not create demo accounts.

Password reset requires an SMTP provider. Configure its SMTP settings above, set `FRONTEND_URL` to the deployed site origin, and run `python -m alembic upgrade head` to create the reset-token table. Reset links expire after 30 minutes and can only be used once. Keep SMTP credentials in `.env` and never commit them.

## Tests

From the `Backend` directory, with the Python environment activated:

```powershell
python -m pytest -q
```
