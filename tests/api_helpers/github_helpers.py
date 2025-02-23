import requests
import json
import logging
import os

# Get base URL from environment variables
BASE_URL = "https://api.github.com"

def create_new_repository(headers, repo_name="TestRepository", description="Test repository description"):
    """
    Creates a new GitHub repository
    
    Args:
        headers (dict): Headers containing GitHub authorization token
        repo_name (str): Name of the repository to create
        description (str): Repository description
        
    Returns:
        repo_name (str): Name of the created repository
    """
    create_repo_data = {
        "name": repo_name,
        "description": description,
        "homepage": "https://github.com",
        "private": False,
        "auto_init": True  # This will initialize the repository with README.md

    }
    
    create_response = requests.post(
        f"{BASE_URL}/user/repos",
        headers=headers,
        json=create_repo_data
    )
    logging.debug(f"Create Repository Response: \n{json.dumps(create_response.json(), indent=2)}")
    assert create_response.status_code == 201
    repo_name = create_response.json()['name']
    logging.info(f"Created repository name: {repo_name}")
    return repo_name


def verify_repository_in_user_repos(headers, username, repo_name):
    """
    Lists all user repositories and verifies if specific repository exists
    
    Args:
        headers (dict): Headers containing GitHub authorization token
        username (str): GitHub username
        repo_name (str): Name of the repository
        
    Returns:
        dict: Repository data
    """
    response = requests.get(f"{BASE_URL}/users/{username}/repos", headers=headers)
    assert response.status_code == 200, f"Failed to fetch repositories for user {username}"
    
    repositories = response.json()
    logging.info(f"Found {len(repositories)} repositories for user {username}")
    logging.debug(f"All repositories:\n{json.dumps(repositories, indent=2)}")
    matching_repo = next((repo for repo in repositories if repo['name'] == repo_name), None)
    assert matching_repo is not None, f"Repository {repo_name} was not found in user's repositories"
    
    logging.debug(f"Found matching repository:\n{json.dumps(matching_repo, indent=2)}")
    return matching_repo


def create_new_branch(headers, username, repo_name, branch_name, base_branch="main"):
    """
    Creates a new branch in the specified repository
    
    Args:
        headers (dict): Headers containing GitHub authorization token
        username (str): GitHub username
        repo_name (str): Name of the repository
        branch_name (str): Name of the new branch
        base_branch (str): Name of the base branch (default: main)
        
    Returns:
        dict: Branch creation response data
    """
    # Get the SHA of the base branch
    base_branch_response = requests.get(
        f"{BASE_URL}/repos/{username}/{repo_name}/git/refs/heads/{base_branch}",
        headers=headers
    )
    assert base_branch_response.status_code == 200, f"Failed to get {base_branch} branch reference"
    
    sha = base_branch_response.json()['object']['sha']
    
    # Create new branch
    create_branch_data = {
        "ref": f"refs/heads/{branch_name}",
        "sha": sha
    }
    
    create_branch_response = requests.post(
        f"{BASE_URL}/repos/{username}/{repo_name}/git/refs",
        headers=headers,
        json=create_branch_data
    )
    
    assert create_branch_response.status_code == 201, f"Failed to create branch {branch_name}"
    logging.info(f"Created new branch: {branch_name}")
    logging.debug(f"Branch creation response:\n{json.dumps(create_branch_response.json(), indent=2)}")
    
    return create_branch_response.json()


def push_commit_to_branch(headers, username, repo_name, branch_name, file_content, commit_message, file_path):
    """
    Pushes a commit to the specified branch
    
    Args:
        headers (dict): Headers containing GitHub authorization token
        username (str): GitHub username
        repo_name (str): Name of the repository
        branch_name (str): Name of the branch
        file_content (str): Content to commit
        commit_message (str): Commit message
        file_path (str): Path to the file in repository
        
    Returns:
        dict: Commit response data
    """
    # Get the reference of the branch
    ref_response = requests.get(
        f"{BASE_URL}/repos/{username}/{repo_name}/git/refs/heads/{branch_name}",
        headers=headers
    )
    assert ref_response.status_code == 200, f"Failed to get branch reference"
    branch_sha = ref_response.json()['object']['sha']

    # Get the current commit tree
    tree_response = requests.get(
        f"{BASE_URL}/repos/{username}/{repo_name}/git/commits/{branch_sha}",
        headers=headers
    )
    assert tree_response.status_code == 200, f"Failed to get commit tree"
    base_tree_sha = tree_response.json()['tree']['sha']

    # Create a blob for the file
    blob_data = {
        "content": file_content,
        "encoding": "utf-8"
    }
    blob_response = requests.post(
        f"{BASE_URL}/repos/{username}/{repo_name}/git/blobs",
        headers=headers,
        json=blob_data
    )
    assert blob_response.status_code == 201, "Failed to create blob"
    blob_sha = blob_response.json()['sha']

    # Create a new tree
    tree_data = {
        "base_tree": base_tree_sha,
        "tree": [{
            "path": file_path,
            "mode": "100644",
            "type": "blob",
            "sha": blob_sha
        }]
    }
    create_tree_response = requests.post(
        f"{BASE_URL}/repos/{username}/{repo_name}/git/trees",
        headers=headers,
        json=tree_data
    )
    assert create_tree_response.status_code == 201, "Failed to create tree"
    new_tree_sha = create_tree_response.json()['sha']

    # Create a commit
    commit_data = {
        "message": commit_message,
        "tree": new_tree_sha,
        "parents": [branch_sha]
    }
    commit_response = requests.post(
        f"{BASE_URL}/repos/{username}/{repo_name}/git/commits",
        headers=headers,
        json=commit_data
    )
    assert commit_response.status_code == 201, "Failed to create commit"
    new_commit_sha = commit_response.json()['sha']

    # Update the reference
    ref_data = {
        "sha": new_commit_sha,
        "force": False
    }
    update_ref_response = requests.patch(
        f"{BASE_URL}/repos/{username}/{repo_name}/git/refs/heads/{branch_name}",
        headers=headers,
        json=ref_data
    )
    assert update_ref_response.status_code == 200, "Failed to update reference"
    
    logging.info(f"Successfully pushed commit to branch {branch_name}")
    logging.debug(f"Commit response:\n{json.dumps(commit_response.json(), indent=2)}")
    
    return commit_response.json()

def create_pull_request(headers, username, repo_name, head_branch, base_branch="main", title=None, body=None):
    """
    Creates a new pull request
    
    Args:
        headers (dict): Headers containing GitHub authorization token
        username (str): GitHub username
        repo_name (str): Name of the repository
        head_branch (str): Name of the branch containing changes
        base_branch (str): Name of the target branch (default: main)
        title (str): Title of the pull request
        body (str): Description of the pull request
        
    Returns:
        dict: Pull request data
    """
    if title is None:
        title = f"Pull request from {head_branch}"
    if body is None:
        body = f"Automated pull request created from {head_branch} to {base_branch}"

    pr_data = {
        "title": title,
        "body": body,
        "head": head_branch,
        "base": base_branch
    }

    create_pr_response = requests.post(
        f"{BASE_URL}/repos/{username}/{repo_name}/pulls",
        headers=headers,
        json=pr_data
    )
    
    assert create_pr_response.status_code == 201, "Failed to create pull request"
    logging.info(f"Created pull request: {title}")
    return create_pr_response.json()

def verify_pull_request(headers, username, repo_name, pr_number):
    """
    Verifies pull request metadata and changes
    
    Args:
        headers (dict): Headers containing GitHub authorization token
        username (str): GitHub username
        repo_name (str): Name of the repository
        pr_number (int): Pull request number
        
    Returns:
        tuple: (pr_data, pr_files)
    """
    # Get PR metadata
    pr_response = requests.get(
        f"{BASE_URL}/repos/{username}/{repo_name}/pulls/{pr_number}",
        headers=headers
    )
    assert pr_response.status_code == 200, f"Failed to get PR #{pr_number}"
    pr_data = pr_response.json()
    
    # Get PR changes
    files_response = requests.get(
        f"{BASE_URL}/repos/{username}/{repo_name}/pulls/{pr_number}/files",
        headers=headers
    )
    assert files_response.status_code == 200, f"Failed to get PR #{pr_number} files"
    pr_files = files_response.json()
    
    logging.info(f"Pull Request #{pr_number} metadata:")
    logging.info(f"Title: {pr_data['title']}")
    logging.info(f"State: {pr_data['state']}")
    logging.info(f"Changed files: {len(pr_files)}")
    
    return pr_data, pr_files

def delete_repository(headers, username, repo_name):
    """
    Deletes a repository
    
    Args:
        headers (dict): Headers containing GitHub authorization token
        username (str): GitHub username
        repo_name (str): Name of the repository to delete
    """
    delete_response = requests.delete(
        f"{BASE_URL}/repos/{username}/{repo_name}",
        headers=headers
    )
    
    if delete_response.status_code != 204:
        error_message = f"""
        Failed to delete repository {repo_name}.
        Status code: {delete_response.status_code}
        Response: {delete_response.text}
        URL: {BASE_URL}/repos/{username}/{repo_name}
        Headers: {headers}
        """
        logging.error(error_message)
        raise AssertionError(error_message)
    
    logging.info(f"Successfully deleted repository: {repo_name}")

def verify_repository_not_exists(headers, username, repo_name):
    """
    Verifies that a repository does not exist
    
    Args:
        headers (dict): Headers containing GitHub authorization token
        username (str): GitHub username
        repo_name (str): Name of the repository to check
        
    Returns:
        bool: True if repository does not exist
    """
    response = requests.get(f"{BASE_URL}/repos/{username}/{repo_name}", headers=headers)
    if response.status_code == 404:
        logging.info(f"Confirmed repository {repo_name} does not exist")
        return True
    elif response.status_code == 200:
        logging.info(f"Repository {repo_name} still exists when it should have been deleted")
        return False
    else:
        raise AssertionError(f"Unexpected status code {response.status_code} when checking repository existence")
