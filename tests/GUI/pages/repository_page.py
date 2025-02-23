from playwright.sync_api import Page, expect


class RepositoryPage:
    """Page object for repository creation and management."""

    def __init__(self, page: Page):
        """
        Initialize RepositoryPage with page elements.

        Args:
            page (Page): Playwright page object
        """
        self.page = page
        self.new_repo_link = page.get_by_role(
            "link",
            name="New",
            exact=True
        )
        self.repo_name_input = page.get_by_role(
            "textbox",
            name="Repository name *"
        )
        self.repo_description_input = page.get_by_role(
            "textbox",
            name="Description"
        )
        self.private_radio = page.get_by_role(
            "radio",
            name="Private"
        )
        self.readme_checkbox = page.get_by_role(
            "checkbox",
            name="Add a README file"
        )
        self.create_repo_button = page.get_by_role(
            "button",
            name="Create repository"
        )

    def create_repository(self, name: str, description: str):
        """
        Create a new repository with specified parameters.

        Args:
            name (str): Repository name
            description (str): Repository description
        """
        self.new_repo_link.click()
        self.repo_name_input.fill(name)
        self.repo_description_input.fill(description)
        self.private_radio.check()
        self.readme_checkbox.check()
        
        expect(self.create_repo_button).to_be_enabled()
        expect(self.create_repo_button).to_be_visible()
        self.page.wait_for_selector(
            'button:has-text("Create repository")',
            state='visible',
            timeout=5000
        )
        self.page.wait_for_timeout(500)
        self.create_repo_button.click(force=True, timeout=5000)
        
        expect(
            self.page.get_by_role("heading", name=name, exact=True)
        ).to_be_visible() 