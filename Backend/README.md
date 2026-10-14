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
- `GEMINI_API_KEY` to enable the AI study tutor and optionally `GEMINI_MODELS` to set an ordered, comma-separated model list. The defaults try `gemini-flash-lite-latest` first and automatically fall back to `gemini-3.1-flash-lite` on temporary service failures. Create a key in [Google AI Studio](https://aistudio.google.com/api-keys) and keep it private. The tutor sends course lesson content and the current chat to Gemini for answers.

Then initialize the database and start the API. Run migrations against the direct Neon endpoint, and use the same `DATABASE_URL` for seeding:

```powershell
python -m alembic upgrade head
python seed.py
python -m uvicorn app.main:app --reload
```

The API is available at `http://localhost:8000`; interactive docs are at `http://localhost:8000/docs`. When both seed passwords are configured, the seed creates the accounts using `SEED_ADMIN_EMAIL` and `SEED_STUDENT_EMAIL`. Existing legacy accounts ending in `@pageturners.local` are updated to those configured addresses when you rerun `python seed.py`; their existing passwords are unchanged. To enable content management in the frontend, sign in using `SEED_ADMIN_EMAIL` and `SEED_ADMIN_PASSWORD`. Without the passwords, the seed still installs reference and course data so students can register normally, but it does not create demo accounts.

Password reset requires an SMTP provider. Configure its SMTP settings above, set `FRONTEND_URL` to the deployed site origin, and run `python -m alembic upgrade head` to create the reset-token table. Reset links expire after 30 minutes and can only be used once. Keep SMTP credentials in `.env` and never commit them.

Administrators can manage accounts from the admin page: deactivation blocks sign-in but preserves account data, reactivation restores access, and permanent deletion removes the account and its associated learning records. The API protects the current administrator and prevents removing the last active administrator.

The AI tutor is available to signed-in users from the **AI Tutor** navigation link. It answers questions using the selected published course’s description, topics, and lesson notes. Chat history is held in the browser only; each request sends at most the recent conversation to Gemini. Configure `GEMINI_API_KEY` in the backend environment to enable it. Gemini API free-tier access has model and request limits that can change; review Google's current [pricing and data-use terms](https://ai.google.dev/gemini-api/docs/pricing) before sending student information. Do not send personal or sensitive information to the free tier.

Administrators can attach an optional HTTPS video URL to each lesson. Run `python -m alembic upgrade head` to add the lesson video URL column before deploying the updated API. YouTube, Vimeo, and direct MP4, WebM, or OGG links are supported on the student lesson page.

## Deploy to Google Cloud Run with Neon

The backend includes a Dockerfile for Cloud Run. Keep the existing Neon database and use its pooled connection string for the running API. Use the direct Neon connection for applying database migrations.

1. In Google Cloud Console, create or select a project, enable billing, and enable **Cloud Run**, **Cloud Build**, and **Secret Manager** APIs. Install and authenticate the Google Cloud CLI, then select the project:

   ```powershell
   gcloud auth login
   gcloud config set project YOUR_GOOGLE_CLOUD_PROJECT_ID
   gcloud services enable run.googleapis.com cloudbuild.googleapis.com secretmanager.googleapis.com
   ```

2. Create secrets in **Google Cloud Console → Security → Secret Manager** for `DATABASE_URL`, `SECRET_KEY`, and `GEMINI_API_KEY`. Add `SMTP_PASSWORD` too if password-reset email uses authenticated SMTP. Use the Neon **pooled** `postgresql+psycopg://` URL for `DATABASE_URL`; keep the direct URL private for the migration step. Do not add `.env` to the image or repository.
3. Before deploying a release that includes new migrations, run `python -m alembic upgrade head` from this directory with the direct Neon URL configured in your local environment. Migrations are deliberately not run as part of every Cloud Run instance startup.
4. Deploy from the repository root. Replace the project ID, region, and mail values. Put the Google AI Studio key and secrets in Secret Manager; ordinary values such as SMTP host/port and frontend URL can be set as plain environment variables.

   ```powershell
   gcloud run deploy pageturners-api `
     --source . `
     --project YOUR_GOOGLE_CLOUD_PROJECT_ID `
     --region us-central1 `
     --allow-unauthenticated `
     --max 3 `
     --set-secrets "DATABASE_URL=DATABASE_URL:latest,SECRET_KEY=SECRET_KEY:latest,GEMINI_API_KEY=GEMINI_API_KEY:latest,SMTP_PASSWORD=SMTP_PASSWORD:latest" `
     --set-env-vars "^#^APP_ENV=production#DEBUG=false#FRONTEND_URL=https://YOUR-SITE.netlify.app#CORS_ORIGINS=https://YOUR-SITE.netlify.app#GEMINI_MODELS=gemini-flash-lite-latest,gemini-3.1-flash-lite#SMTP_HOST=YOUR_SMTP_HOST#SMTP_PORT=587#SMTP_USERNAME=YOUR_SMTP_USERNAME#SMTP_SENDER_EMAIL=YOUR_VERIFIED_SENDER#SMTP_USE_SSL=false"
   ```

   If SMTP is not configured, remove the SMTP values and `SMTP_PASSWORD` secret mapping. The first deployment may need additional permissions to let the Cloud Run runtime service account access each secret; grant it **Secret Manager Secret Accessor** on those secrets when prompted or in IAM.
5. Copy the deployed service URL printed by `gcloud run deploy` and verify `https://YOUR-SERVICE-URL/health` reports `"database":"ok"`.
6. In Netlify, set `VITE_API_BASE_URL` to `https://YOUR-SERVICE-URL/api/v1` and redeploy the frontend. Set `FRONTEND_URL` and `CORS_ORIGINS` in the Cloud Run service to the exact Netlify site origin (no trailing slash), then deploy a new backend revision.

Cloud Run requires a Google Cloud billing account even when the service stays within free allowances. Cloud Run usage, Neon usage, SMTP delivery, and Gemini's separate free-tier limits are governed by their providers' current plans and quotas. Set a Cloud Run maximum instance count and billing budget alerts; free-tier terms do not guarantee zero charges.

## Tests

From the `Backend` directory, with the Python environment activated:

```powershell
python -m pytest -q
```
