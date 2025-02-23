import os
import pytest
import logging
from tests.api_helpers.git_helpers import clone_repository, verify_repository_content
from tests.api_helpers.github_helpers import (
    create_new_repository,
    push_commit_to_branch,
    delete_repository,
    create_pull_request
)
from tests.GUI.pages.login_page import LoginPage

# Environment variables
GITHUB_API_KEY = os.getenv("GITHUB_API_KEY")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
GITHUB_PASSWORD = os.getenv("GITHUB_PASSWORD")
BASE_URL = os.getenv("BASE_URL", "https://github.com")

# Test constants
TEST_REPO_NAME = "test-git-operations"
TEST_FILE_CONTENT = "print('HelloGit')"
TEST_FILE_PATH = "test_script.py"
TEST_README_CONTENT = "# Test Repository\n\nThis is a test repository."
TEST_BRANCH_NAME = "feature/update-readme"
TEST_PR_TITLE = "Update README.md"
TEST_PR_BODY = "Automated PR for testing"

@pytest.fixture(scope="class")
def test_repo_setup():
    """Fixture to create and cleanup test repository"""
    repo_name = TEST_REPO_NAME
    
    # Delete repository if it exists
    try:
        delete_repository(
            {"Authorization": f"token {GITHUB_API_KEY}"}, 
            GITHUB_USERNAME, 
            repo_name
        )
    except Exception as e:
        logging.info(f"Repository doesn't exist or couldn't be deleted: {e}")
    
    # Create repository
    create_new_repository(
        headers={"Authorization": f"token {GITHUB_API_KEY}"},
        repo_name=repo_name,
        description="Test repository for git operations"
    )
    
    # Add sample file
    push_commit_to_branch(
        headers={"Authorization": f"token {GITHUB_API_KEY}"},
        username=GITHUB_USERNAME,
        repo_name=repo_name,
        branch_name="main",
        file_content=TEST_FILE_CONTENT,
        commit_message="Added sample Python file",
        file_path=TEST_FILE_PATH
    )
    
    yield repo_name
    
    # Cleanup after test
    # delete_repository(
    #     {"Authorization": f"token {GITHUB_API_KEY}"}, 
    #     GITHUB_USERNAME, 
    #     repo_name
    # )

@pytest.mark.usefixtures("test_repo_setup")
class TestGitOperations:
    def test_clone_and_verify_repository(self, test_repo_setup, tmp_path):
        """
        Test repository cloning and content verification.
        
        1. Clones the created repository
        2. Verifies its structure
        3. Checks for presence of added files
        """
        repo_name = test_repo_setup
        
        # Clone repository
        repo_path = clone_repository(
            username=GITHUB_USERNAME,
            repo_name=repo_name,
            target_dir=str(tmp_path),
            token=GITHUB_API_KEY
        )
        
        # Verify content
        expected_files = [
            "README.md",  # Created automatically by auto_init
            TEST_FILE_PATH  # Added by us
        ]
        
        logging.info(f"Repository path: {repo_path}")
        assert verify_repository_content(repo_path, expected_files), \
            "Repository content verification failed"
        
        # Check test_script.py content
        with open(os.path.join(repo_path, TEST_FILE_PATH), "r") as f:
            content = f.read()
        
        assert content == TEST_FILE_CONTENT, \
            f"{TEST_FILE_PATH} content does not match expected"

    def test_push_changes(self, test_repo_setup, tmp_path):
        """
        Test creating a branch, pushing changes, and merging via UI.
        
        1. Creates a local branch
        2. Modifies a file
        3. Commits and pushes changes
        4. Creates PR and merges it using GitHub UI
        """
        from tests.GUI.pages.merge_page import MergePage
        from tests.api_helpers.github_helpers import create_pull_request
        import git
        
        repo_name = test_repo_setup
        
        # Clone repository
        repo_path = clone_repository(
            username=GITHUB_USERNAME,
            repo_name=repo_name,
            target_dir=str(tmp_path),
            token=GITHUB_API_KEY
        )
        
        # Initialize git repo object
        repo = git.Repo(repo_path)
        
        # Create and checkout new branch
        new_branch = "feature/update-readme"
        repo.git.checkout('-b', new_branch)
        
        # Modify README.md
        readme_path = os.path.join(repo_path, "README.md")
        with open(readme_path, 'w') as f:
            f.write(TEST_README_CONTENT)
            
        # Stage, commit and push changes
        repo.index.add(['README.md'])
        repo.index.commit("Update README.md")
        repo.git.push('--set-upstream', 'origin', TEST_BRANCH_NAME)
        
        # Create Pull Request
        create_pull_request(
            headers={"Authorization": f"token {GITHUB_API_KEY}"},
            username=GITHUB_USERNAME,
            repo_name=repo_name,
            head_branch=TEST_BRANCH_NAME,
            base_branch="main",
            title=TEST_PR_TITLE,
            body=TEST_PR_BODY
        )

    def test_merge_pr(self, test_repo_setup):
        """
        Test merging pull request via UI.
        
        1. Gets the repository name from fixture
        2. Uses MergePage to validate and merge PR
        """
        from playwright.sync_api import Page, sync_playwright
        from tests.GUI.pages.merge_page import MergePage
        
        repo_name = test_repo_setup
        
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            page = browser.new_page()
            
            try:
                login_page = LoginPage(page)
                login_page.login(GITHUB_USERNAME, GITHUB_PASSWORD)
                merge_page = MergePage(page)
                merge_page.validate_and_merge_pr(
                    username=GITHUB_USERNAME,
                    repo_name=repo_name,
                    content=TEST_PR_BODY,
                    pr_description=TEST_PR_TITLE
                )
            finally:
                browser.close()

        
        