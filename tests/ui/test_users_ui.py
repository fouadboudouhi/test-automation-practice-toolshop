import pytest
from playwright.sync_api import Page, expect

@pytest.mark.ui
def test_create_user_via_ui(page: Page, base_url: str):
    page.goto(f"{base_url}/")
    expect(page.get_by_test_id("page-title")).to_have_text("User Management")

    page.get_by_test_id("create-email").fill("ui@example.com")
    page.get_by_test_id("create-name").fill("UI User")
    page.get_by_test_id("create-submit").click()

    rows = page.get_by_test_id("user-row")
    expect(rows).to_have_count(1)
    expect(page.get_by_test_id("user-email")).to_have_text("ui@example.com")
    expect(page.get_by_test_id("user-name")).to_have_text("UI User")
