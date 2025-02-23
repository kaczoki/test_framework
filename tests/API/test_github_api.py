import os
import requests
import allure

@allure.epic("GitHub API Operations")
@allure.feature("Basic API Functionality")
@allure.story("User Information")
@allure.title("Test GitHub API basic user information retrieval")
def test_github_api():
    """Test basic GitHub API functionality by retrieving user information."""
    
    with allure.step("Prepare and send request"):
        api_key = os.getenv("GITHUB_API_KEY")
        username = os.getenv("GITHUB_USERNAME")
        base_url = os.getenv("BASE_URL")
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        response = requests.get(f"{base_url}/users/{username}", headers=headers)
        allure.attach(
            str(response.status_code),
            name="Response Status Code",
            attachment_type=allure.attachment_type.TEXT
        )
        allure.attach(
            response.text,
            name="Response Body",
            attachment_type=allure.attachment_type.JSON
        )
        
    with allure.step("Verify response"):
        response_json = response.json()
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
        assert "login" in response_json, "Response should contain 'login' field"
        assert response_json["login"] == username, f"Expected username {username}, got {response_json['login']}"

