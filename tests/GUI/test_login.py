import os
import pytest
import allure
from playwright.sync_api import Page
from tests.GUI.pages.login_page import LoginPage

USERNAME = os.getenv("GITHUB_USERNAME")
PASSWORD = os.getenv("GITHUB_PASSWORD")

@allure.epic("GitHub GUI Operations")
@allure.feature("Authentication")
@allure.story("Login")
@allure.title("Test GitHub login functionality")
def test_smoke_login(page: Page):
    """
    Smoke test verifying basic GitHub login functionality.

    Args:
        page (Page): Playwright page object
    """
    with allure.step("Perform login"):
        login_page = LoginPage(page)
        login_page.login(USERNAME, PASSWORD)
