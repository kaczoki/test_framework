import os
import logging
import pytest
import allure
import requests
from tests.api_helpers.github_helpers import (
    create_new_repository,
    verify_repository_in_user_repos,
    create_new_branch,
    push_commit_to_branch,
    create_pull_request,
    verify_pull_request,
    delete_repository,
    verify_repository_not_exists
)

logging.basicConfig(level=logging.INFO)

GITHUB_TOKEN = os.getenv("GITHUB_API_KEY")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
BASE_URL = os.getenv("BASE_URL")
REPO_NAME = "TestRepository"
NEW_BRANCH_NAME = "feature/test-branch"
HEADERS = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }

@pytest.fixture(scope="class")
def setup_and_cleanup():
    """
    Class-level fixture that ensures clean test environment:
    - Removes test repository if it exists before all tests
    - Cleans up the test repository after all tests complete
    """
    with allure.step("Clean up environment before tests"):
        if not verify_repository_not_exists(HEADERS, GITHUB_USERNAME, REPO_NAME):
            logging.info(f"Repository {REPO_NAME} exists, cleaning up before tests")
            delete_repository(HEADERS, GITHUB_USERNAME, REPO_NAME)
            assert verify_repository_not_exists(
                HEADERS,
                GITHUB_USERNAME,
                REPO_NAME
            ), f"Repository {REPO_NAME} should not exist after cleanup"

    yield

    with allure.step("Clean up environment after tests"):
        if not verify_repository_not_exists(HEADERS, GITHUB_USERNAME, REPO_NAME):
            logging.info(f"Cleaning up repository {REPO_NAME} after tests")
            delete_repository(HEADERS, GITHUB_USERNAME, REPO_NAME)
            assert verify_repository_not_exists(
                HEADERS,
                GITHUB_USERNAME,
                REPO_NAME
            ), f"Repository {REPO_NAME} should not exist after cleanup"

@allure.epic("GitHub API Operations")
@allure.feature("Repository Management")
@pytest.mark.usefixtures("setup_and_cleanup")
class TestGithubOperations:
    """Test suite for GitHub repository operations."""

    @allure.story("Repository Creation")
    @allure.title("Test repository creation via API")
    def test_repository_creation(self):
        """
        Test verifies that a new repository can be created and is visible
        in user's repository list.
        """
        with allure.step("Create new repository"):
            create_new_repository(HEADERS, REPO_NAME)
        
        with allure.step("Verify repository exists"):
            repository_data = verify_repository_in_user_repos(
                HEADERS,
                GITHUB_USERNAME,
                REPO_NAME
            )
            assert repository_data is not None, "Repository should exist after creation"

    @allure.story("Branch Management")
    @allure.title("Test branch creation in repository")
    def test_branch_creation(self):
        """
        Test verifies that a new branch can be created in the repository
        """
        with allure.step(f"Create new branch: {NEW_BRANCH_NAME}"):
            branch_data = create_new_branch(
                HEADERS, 
                GITHUB_USERNAME, 
                REPO_NAME, 
                NEW_BRANCH_NAME
            )
            assert branch_data is not None, "Branch should be created successfully"
            logging.info(f"New branch created: {NEW_BRANCH_NAME}")

    @allure.story("Content Management")
    @allure.title("Test committing and pushing content")
    def test_commit_push(self):
        """
        Test verifies that content can be committed and pushed to a branch
        """
        file_content = "# Test Repository\nThis is a test repository created via API."
        commit_message = "Add README.md"
        file_path = "README.md"

        with allure.step("Push commit to branch"):
            commit_data = push_commit_to_branch(
                HEADERS,
                GITHUB_USERNAME,
                REPO_NAME,
                NEW_BRANCH_NAME,
                file_content,
                commit_message,
                file_path
            )
            assert commit_data is not None, "Commit should be created successfully"

    @allure.story("Pull Request Management")
    @allure.title("Test pull request creation and verification")
    def test_pull_request_creation(self):
        """
        Test verifies that a pull request can be created and contains
        expected changes.
        """
        pr_title = "Add README.md file"
        pr_body = "This PR adds a basic README.md file to the repository"

        with allure.step("Create pull request"):
            pr_data = create_pull_request(
                HEADERS,
                GITHUB_USERNAME,
                REPO_NAME,
                NEW_BRANCH_NAME,
                title=pr_title,
                body=pr_body
            )

        with allure.step("Verify pull request"):
            pr_number = pr_data['number']
            pr_info, pr_files = verify_pull_request(
                HEADERS,
                GITHUB_USERNAME,
                REPO_NAME,
                pr_number
            )

            with allure.step("Validate pull request data"):
                assert pr_info['title'] == pr_title, "PR title doesn't match"
                assert pr_info['body'] == pr_body, "PR description doesn't match"
                assert pr_info['state'] == 'open', "PR should be in open state"
                assert len(pr_files) > 0, "PR should contain file changes"
                assert any(
                    file['filename'] == 'README.md' for file in pr_files
                ), "README.md should be among changed files"

    

    


