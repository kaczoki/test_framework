import os
import requests

def test_github_api():
    # Getting environment variables directly from pytest.ini
    api_key = os.getenv("GITHUB_API_KEY")
    username = os.getenv("GITHUB_USERNAME")
    base_url = os.getenv("BASE_URL")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    response = requests.get(f"{base_url}/users/{username}", headers=headers)
    assert response.status_code == 200 

    # Check if the response contains the expected user information
    assert "login" in response.json()
    assert response.json()["login"] == username

