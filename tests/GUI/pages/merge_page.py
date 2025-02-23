from playwright.sync_api import Page, expect
import os

class MergePage:
    def __init__(self, page: Page):
        self.page = page
        self.base_url = os.getenv("BASE_URL_GUI")
        self.pr_link = page.get_by_role("link", name="Update README.md").first
        self.files_changed_tab = page.get_by_role("link", name="Files changed").first
        self.conversation_tab = page.get_by_role("link", name="Conversation")
        self.merge_button = page.get_by_role("button", name="Merge pull request")
        self.confirm_merge_button = page.get_by_role("button", name="Confirm merge")
        self.delete_branch_button = page.get_by_role("button", name="Delete branch")
        self.merged_badge = page.get_by_text("Merged")
        self.success_message = page.get_by_text("Pull request successfully merged and closed")

    def validate_and_merge_pr(self, username: str, repo_name: str):
        # Navigate to pull requests page
        self.page.goto(f"{self.base_url}/{username}/{repo_name}/pulls")
        self.page.wait_for_load_state("load")
        
        # Open the PR
        expect(self.pr_link).to_be_visible()
        self.pr_link.click()
        self.page.wait_for_timeout(1000)

        # Validate changes
        expect(self.page.get_by_text("TestAutomationDescription").first).to_be_visible()
        self.files_changed_tab.click()
        self.page.wait_for_timeout(1000)
        expect(self.page.get_by_text("TestAutomationCode", exact=True).first).to_be_visible()
        
        # Merge PR
        self.conversation_tab.click()
        expect(self.merge_button).to_be_enabled()
        self.merge_button.click()
        self.page.wait_for_timeout(1000)
        
        expect(self.confirm_merge_button).to_be_enabled()
        self.confirm_merge_button.click()
        
        # Verify merge success
        expect(self.success_message).to_be_visible()
        
        # Verify PR was merged
        expect(self.merged_badge).to_be_visible()
        
        # Delete branch
        expect(self.delete_branch_button).to_be_enabled()
        self.delete_branch_button.click() 