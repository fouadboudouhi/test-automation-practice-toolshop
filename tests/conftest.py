import os
import pytest
import psycopg
import allure
import pytest

from utils.wait import wait_for_http

APP_BASE_URL = os.getenv("APP_BASE_URL", "http://app:8000")

DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = os.getenv("DB_NAME", "appdb")
DB_USER = os.getenv("DB_USER", "app")
DB_PASSWORD = os.getenv("DB_PASSWORD", "app")
DB_PORT = int(os.getenv("DB_PORT", "5432"))

@pytest.fixture(scope="session")
def base_url():
    return APP_BASE_URL

@pytest.fixture(scope="session", autouse=True)
def _wait_for_app(base_url):
    wait_for_http(f"{base_url}/api/health", timeout_s=60)

def _truncate_users():
    conn_str = f"host={DB_HOST} port={DB_PORT} dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD}"
    with psycopg.connect(conn_str) as conn:
        with conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE users RESTART IDENTITY;")
        conn.commit()

@pytest.fixture(autouse=True)
def clean_db():
    _truncate_users()
    yield

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()

    if rep.when == "call" and rep.failed and "page" in item.fixturenames:
        page = item.funcargs["page"]
        allure.attach(
            page.screenshot(),
            name="screenshot",
            attachment_type=allure.attachment_type.PNG,
        )
