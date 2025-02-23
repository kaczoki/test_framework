import os
import logging
import pytest
from tests.api_helpers.github_helpers import (
    create_new_repository,
    verify_repository_in_user_repos,
    create_new_branch,
    push_commit_to_branch,
    create_pull_request,
    verify_pull_request,
    delete_repository,
    verify_repository_not_exists,
    check_token_permissions
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

# Fixture to clean up repository after test
@pytest.fixture(autouse=True)
def cleanup_repository():
    # Check if repository exists before test
    if not verify_repository_not_exists(HEADERS, GITHUB_USERNAME, REPO_NAME):
        logging.info(f"Repository {REPO_NAME} exists, cleaning up before test")
        delete_repository(HEADERS, GITHUB_USERNAME, REPO_NAME)
        assert verify_repository_not_exists(HEADERS, GITHUB_USERNAME, REPO_NAME), \
            f"Repository {REPO_NAME} should not exist after cleanup"
    
    yield 
    # Cleanup after test -> if test fails delete existing repository anyway
    if not verify_repository_not_exists(HEADERS, GITHUB_USERNAME, REPO_NAME):
        logging.info(f"Cleaning up repository {REPO_NAME} after test")
        delete_repository(HEADERS, GITHUB_USERNAME, REPO_NAME)
        assert verify_repository_not_exists(HEADERS, GITHUB_USERNAME, REPO_NAME), \
            f"Repository {REPO_NAME} should not exist after cleanup"




def test_github_api():
    # Create new repository 
    create_new_repository(HEADERS, REPO_NAME)

    # Check if repository exists using helper method
    repository_data = verify_repository_in_user_repos(HEADERS, GITHUB_USERNAME, REPO_NAME)

    # Create new branch
    branch_data = create_new_branch(HEADERS,GITHUB_USERNAME,REPO_NAME,NEW_BRANCH_NAME)
    logging.info(f"New branch created: {NEW_BRANCH_NAME}")

    # Push a commit to the new branch
    file_content = "# Test Repository\nThis is a test repository created via API."
    commit_message = "Add README.md"
    file_path = "README.md"
    
    commit_data = push_commit_to_branch(
        HEADERS,
        GITHUB_USERNAME,
        REPO_NAME,
        NEW_BRANCH_NAME,
        file_content,
        commit_message,
        file_path
    )

    # Create a pull request
    pr_title = "Add README.md file"
    pr_body = "This PR adds a basic README.md file to the repository"
    pr_data = create_pull_request(
        HEADERS,
        GITHUB_USERNAME,
        REPO_NAME,
        NEW_BRANCH_NAME,
        title=pr_title,
        body=pr_body
    )
    
    # Verify pull request
    pr_number = pr_data['number']
    pr_info, pr_files = verify_pull_request(
        HEADERS,
        GITHUB_USERNAME,
        REPO_NAME,
        pr_number
    )
    
    # Assertions to verify PR metadata
    assert pr_info['title'] == pr_title, "PR title doesn't match"
    assert pr_info['body'] == pr_body, "PR description doesn't match"
    assert pr_info['state'] == 'open', "PR should be in open state"
    assert len(pr_files) > 0, "PR should contain file changes"
    assert any(file['filename'] == 'README.md' for file in pr_files), "README.md should be among changed files"

    # Clean up - delete repository and verify it's gone
    delete_repository(HEADERS, GITHUB_USERNAME, REPO_NAME)
    
    # Verify repository no longer exists
    assert verify_repository_not_exists(HEADERS, GITHUB_USERNAME, REPO_NAME), \
        f"Repository {REPO_NAME} should not exist after deletion"

    

    


