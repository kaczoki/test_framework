import os
import logging
from playwright.sync_api import Page, expect

BASE_URL = os.getenv("BASE_URL")
USERNAME = os.getenv("GITHUB_USERNAME")
PASSWORD = os.getenv("GITHUB_PASSWORD")


def test_github_operations(page: Page):
    """
    Test GitHub operations using Playwright
    """
    #1 SECTION
    # Navigate to main page
    page.goto("https://github.com/login")
    
    # Fill login form
    page.get_by_label("Username or email address").fill(USERNAME)
    page.get_by_label("Password").fill(PASSWORD.strip("'"))
    # Click Sign in button
    page.get_by_role("button", name="Sign in", exact=True).click()

    # Open user navigation menu
    page.wait_for_load_state("load", timeout=5000)
    expect(page.get_by_role("button", name="Open user navigation menu")).to_be_enabled()
    page.get_by_role("button", name="Open user navigation menu").click()

    # Verify username is visible in menu
    expect(page.get_by_text(USERNAME, exact=True)).to_be_visible()
  
    page.get_by_role("button", name="Close", exact=True).click()   

    #2 SECTION
    # Create new repository
    page.get_by_role("link", name="New", exact=True).click()
    # Fill repository details
    page.get_by_role("textbox", name="Repository name *").fill("test-repo-playwright")
    page.get_by_role("textbox", name="Description").fill("Test repository created by Playwright")
    
    # Select private repository
    page.get_by_role("radio", name="Private").check()
    page.get_by_role("checkbox", name="Add a README file").check()
    
    # Create repository
    create_repo_button = page.get_by_role("button", name="Create repository")
    expect(create_repo_button).to_be_enabled()
    expect(create_repo_button).to_be_visible()
    page.wait_for_selector('button:has-text("Create repository")', state='visible', timeout=5000)
    page.wait_for_timeout(1000)
    create_repo_button.click(force=True, timeout=5000)
    
    # Verify repository was created successfully

    expect(page.get_by_role("heading", name="test-repo-playwright", exact=True)).to_be_visible()

    #3 SECTION 
    # Navigate to specific repository
    page.goto("https://github.com/kaczoki/test-repo-playwright")
    page.wait_for_load_state("load")
    
    # Verify we're on the correct page
    expect(page.get_by_role("heading", name="test-repo-playwright", exact=True)).to_be_visible()

    #edit README.md with pull request
    page.get_by_role("button", name="Edit file").click()
    page.get_by_role("region", name="Editing README.md file").click()
    page.keyboard.press("Control+A")
    page.keyboard.type("TestAutomationCode")
    page.get_by_role("button", name="Commit changes...").click()
    page.wait_for_timeout(1000)
    expect(page.get_by_role("textbox", name="Add an optional extended")).to_be_visible()
    page.get_by_role("textbox", name="Add an optional extended").fill("TestAutomationDescription")
    page.get_by_role("radio", name="Create a new branch for this").check()  
    page.wait_for_timeout(1000)
    page.get_by_role("button", name="Propose changes").click()
    page.wait_for_timeout(1000)
    page.get_by_role("button", name="Create pull request").click()
    page.wait_for_timeout(1000)


    #4 SECTION

    # validate pull request
    page.goto("https://github.com/kaczoki/test-repo-playwright/pulls")
    page.wait_for_load_state("load")
    expect(page.get_by_role("link", name="Update README.md").first).to_be_visible()
    page.get_by_role("link", name="Update README.md").first.click()
    page.wait_for_timeout(1000)
    #assert that description is visible
    expect(page.get_by_text("TestAutomationDescription").first).to_be_visible()
    page.get_by_role("link", name="Files changed").first.click()
    page.wait_for_timeout(1000)
    expect(page.get_by_text("TestAutomationCode", exact=True).first).to_be_visible()
    page.get_by_role("link", name="Conversation").click()
    page.get_by_role("button", name="Merge pull request").click()
    page.wait_for_timeout(1000)
    page.get_by_role("button", name="Confirm merge").click()
    expect(page.get_by_text("Pull request successfully merged and closed")).to_be_visible()
    page.pause()

