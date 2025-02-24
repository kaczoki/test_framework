import os
import pytest
import logging
import allure
from playwright.sync_api import Page
from tests.GUI.pages.login_page import LoginPage
from tests.GUI.pages.repository_page import RepositoryPage
from tests.GUI.pages.pull_request_page import PullRequestPage
from tests.GUI.pages.merge_page import MergePage
from tests.api_helpers.github_helpers import (
    delete_repository,
    verify_repository_not_exists
)

USERNAME = os.getenv("GITHUB_USERNAME")
PASSWORD = os.getenv("GITHUB_PASSWORD")
BASE_URL_GUI = os.getenv("BASE_URL_GUI")
REPO_NAME = "test-repo-playwright"
TOKEN = os.getenv("GITHUB_API_KEY")

@pytest.fixture(autouse=True)
def login(page: Page):
    login_page = LoginPage(page)
    login_page.login(USERNAME, PASSWORD)

@pytest.fixture(scope="session", autouse=True)
def setup_and_cleanup(worker_id):
    """
    Setup and cleanup fixture for repository management.
    Handles parallel test execution with unique repository names.
    """
    headers = {"Authorization": f"token {TOKEN}"}
    
    if TOKEN is None:
        pytest.skip("GITHUB_TOKEN is not set")
    
    # Add unique identifier for parallel runs
    parallel_repo_name = f"{REPO_NAME}-{worker_id}" if worker_id != "master" else REPO_NAME
        
    def cleanup_repository():
        try:
            if not verify_repository_not_exists(headers, USERNAME, parallel_repo_name):
                delete_repository(headers, USERNAME, parallel_repo_name)
                assert verify_repository_not_exists(headers, USERNAME, parallel_repo_name), "Failed to delete repository"
        except Exception as e:
            pytest.fail(f"Error during repository cleanup: {str(e)}")
    
    # Run cleanup at the start
    cleanup_repository()
    
    yield parallel_repo_name  # Pass the repo name to tests
    
    # Run cleanup after tests
    cleanup_repository()

@pytest.fixture(autouse=True)
def update_repo_name(setup_and_cleanup):
    """Update global REPO_NAME for each test."""
    global REPO_NAME
    REPO_NAME = setup_and_cleanup

@allure.epic("GitHub GUI Operations")
@allure.feature("Repository Management")
class TestGitHubOperations:
    
    @allure.story("Repository Creation")
    @allure.title("Test repository creation via GUI")
    def test_create_repository(self, page: Page):
        """Test repository creation functionality."""
        with allure.step("Create new repository"):
            repo_page = RepositoryPage(page)
            repo_page.create_repository(
                name=REPO_NAME,
                description="Test repository created by Playwright"
            )

    @allure.story("Pull Request Creation")
    @allure.title("Test pull request creation via GUI")
    def test_create_pull_request(self, page: Page):
        """Test pull request creation functionality."""
        with allure.step("Create new pull request"):
            pr_page = PullRequestPage(page)
            pr_page.create_pull_request(
                username=USERNAME,
                repo_name=REPO_NAME, 
                content="TestAutomationCode",
                pr_description="TestAutomationDescription"
            )

    @allure.story("Pull Request Merge")
    @allure.title("Test pull request merge via GUI")
    def test_merge_pull_request(self, page: Page):
        """Test pull request merge functionality."""
        with allure.step("Merge pull request"):
            merge_page = MergePage(page)
            merge_page.validate_and_merge_pr(
                username=USERNAME,
                repo_name=REPO_NAME,
                content="TestAutomationCode",
                pr_description="TestAutomationDescription"
            ) 