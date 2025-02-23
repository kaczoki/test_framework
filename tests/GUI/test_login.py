import os
import pytest
from playwright.sync_api import Page
from tests.GUI.pages.login_page import LoginPage

USERNAME = os.getenv("GITHUB_USERNAME")
PASSWORD = os.getenv("GITHUB_PASSWORD")

def test_smoke_login(page: Page):
    """
    Smoke test verifying basic GitHub login functionality.

    Args:
        page (Page): Playwright page object
    """
    login_page = LoginPage(page)
    login_page.login(USERNAME, PASSWORD)
