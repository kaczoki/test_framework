from playwright.sync_api import Page, expect
import os

class PullRequestPage:
    def __init__(self, page: Page):
        self.page = page
        self.base_url = os.getenv("BASE_URL_GUI")
        self.edit_file_button = page.get_by_role("button", name="Edit file")
        self.readme_editor = page.get_by_role("region", name="Editing README.md file")
        self.commit_changes_button = page.get_by_role("button", name="Commit changes...")
        self.description_input = page.get_by_role("textbox", name="Add an optional extended")
        self.new_branch_radio = page.get_by_role("radio", name="Create a new branch for this")
        self.propose_changes_button = page.get_by_role("button", name="Propose changes")
        self.create_pr_button = page.get_by_role("button", name="Create pull request")

    def create_pull_request(self, username: str, repo_name: str, content: str, branch_name: str, pr_description: str):
        # Navigate to repository
        self.page.goto(f"{self.base_url}/{username}/{repo_name}")
        self.page.wait_for_load_state("load")
        # Verify we're on the correct page
        expect(self.page.get_by_role("heading", name=repo_name, exact=True)).to_be_visible()

        # Edit README.md
        self.edit_file_button.click()
        self.readme_editor.click()
        self.page.keyboard.press("Control+A")
        self.page.keyboard.type(content)
        
        # Commit changes
        self.commit_changes_button.click()
        self.page.wait_for_timeout(1000)
        
        # Fill PR details
        expect(self.description_input).to_be_visible()
        self.description_input.fill(pr_description)
        self.new_branch_radio.check()
        
        # Create PR
        self.page.wait_for_timeout(1000)
        self.propose_changes_button.click()
        self.page.wait_for_timeout(1000)
        self.create_pr_button.click()
        self.page.wait_for_timeout(1000) 