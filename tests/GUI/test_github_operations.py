import pytest
import os
from playwright.sync_api import Page
from tests.GUI.pages.login_page import LoginPage
from tests.GUI.pages.repository_page import RepositoryPage

USERNAME = os.getenv("GITHUB_USERNAME")
PASSWORD = os.getenv("GITHUB_PASSWORD")

@pytest.fixture(autouse=True)
def login(page: Page):
    login_page = LoginPage(page)
    login_page.login(USERNAME, PASSWORD)

def test_create_repository(page: Page):
    repo_page = RepositoryPage(page)
    repo_page.create_repository(
        name="test-repo-playwright",
        description="Test repository created by Playwright"
    ) 