import git
import os
import logging
from typing import List, Optional

def clone_repository(
    username: str,
    repo_name: str,
    target_dir: str,
    token: str = None
) -> str:
    """
    Clones a GitHub repository to the specified directory.
    
    Args:
        username (str): GitHub username
        repo_name (str): Repository name
        target_dir (str): Target directory for the cloned repository
        token (str): GitHub access token (optional)
        
    Returns:
        str: Path to the cloned repository
    """
    # Prepare repository URL
    if token:
        clone_url = f"https://{token}@github.com/{username}/{repo_name}.git"
    else:
        clone_url = f"https://github.com/{username}/{repo_name}.git"
    
    # Create target directory if it doesn't exist
    repo_path = os.path.join(target_dir, repo_name)
    os.makedirs(target_dir, exist_ok=True)
    
    # Clone the repository
    logging.info(f"Cloning repository {repo_name} to {repo_path}")
    git.Repo.clone_from(clone_url, repo_path)
    
    return repo_path

def verify_repository_content(
    repo_path: str,
    expected_files: Optional[List[str]] = None
) -> bool:
    """
    Verifies the content of the cloned repository.
    
    Args:
        repo_path (str): Path to the cloned repository
        expected_files (list[str]): List of expected files (optional)
        
    Returns:
        bool: True if verification succeeded
    """
    # Check if directory exists
    if not os.path.exists(repo_path):
        logging.error(f"Repository directory {repo_path} does not exist")
        return False
        
    # Check if it's a git repository
    try:
        repo = git.Repo(repo_path)
    except git.InvalidGitRepositoryError:
        logging.error(f"{repo_path} is not a valid git repository")
        return False
    
    # Check for expected files
    if expected_files:
        for file_path in expected_files:
            full_path = os.path.join(repo_path, file_path)
            if not os.path.exists(full_path):
                logging.error(f"Expected file not found: {file_path}")
                return False
            logging.info(f"Found expected file: {file_path}")
    
    return True