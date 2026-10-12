import os

# Import-level smoke test that does not require a live database.
os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("DATABASE_URL", "postgresql+psycopg://pageturners:pageturners@localhost:5432/pageturners")

from app.main import app


def test_app_metadata():
    assert app.title == "PageTurners API"
    assert any(route.path == "/health" for route in app.routes)
