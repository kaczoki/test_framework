from playwright.sync_api import Page, expect
import os


class LoginPage:
    """Page object for GitHub login functionality."""

    def __init__(self, page: Page):
        """
        Initialize LoginPage with page elements.

        Args:
            page (Page): Playwright page object
        """
        self.page = page
        self.base_url = os.getenv("BASE_URL_GUI")
        self.username_input = page.get_by_label(
            "Username or email address"
        )
        self.password_input = page.get_by_label(
            "Password"
        )
        self.sign_in_button = page.get_by_role(
            "button",
            name="Sign in",
            exact=True
        )
        self.user_menu_button = page.get_by_role(
            "button",
            name="Open user navigation menu"
        )
        self.close_button = page.get_by_role(
            "button",
            name="Close",
            exact=True
        )

    def login(self, username: str, password: str):
        """
        Perform login operation with provided credentials.

        Args:
            username (str): GitHub username
            password (str): GitHub password
        """
        self.page.goto(f"{self.base_url}/login")
        self.username_input.fill(username)
        self.password_input.fill(password.strip("'"))
        self.sign_in_button.click()
        
        self.page.wait_for_load_state("load", timeout=5000)
        expect(self.user_menu_button).to_be_enabled()
        self.user_menu_button.click()
        
        expect(self.page.get_by_text(username, exact=True)).to_be_visible()
        self.close_button.click() 