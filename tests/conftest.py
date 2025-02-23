import pytest
from pathlib import Path
import os 

import sys
sys.path.append("./helpers/")

import allure
from playwright.sync_api import Page

# Configure parallel test execution using the number of available CPU cores
def pytest_configure(config):
    config.option.numprocesses = os.cpu_count() or 1

# Fixture providing path to test data directory that persists for entire test session
@pytest.fixture(scope="session") 
def test_data_dir():
    return Path(__file__).parent / "test_data"

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """
    Browser context configuration for Playwright
    """
    return {
        **browser_context_args,
        "viewport": {
            "width": 1920,
            "height": 1080,
        },
        "record_video_dir": "test-results/videos" if os.getenv("RECORD_VIDEO") else None,
    }

@pytest.fixture(scope="session")
def browser_context(playwright):
    browser = playwright.chromium.launch()
    context = browser.new_context(
        animations_disabled=True  # Wyłącza wszystkie animacje CSS
    )
    page = context.new_page()
    return context, page

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Adds screenshots to Allure reports when a test fails.
    """
    outcome = yield
    report = outcome.get_result()
    
    if report.when == "call" and report.failed:
        if "page" in item.funcargs:
            page: Page = item.funcargs["page"]
            allure.attach(
                page.screenshot(full_page=True),
                name="screenshot",
                attachment_type=allure.attachment_type.PNG
            )
            allure.attach(
                page.content(),
                name="html",
                attachment_type=allure.attachment_type.HTML
            )

@pytest.fixture(autouse=True)
def allure_attach_env():
    """
    Adds environment information to Allure report.
    """
    allure.attach.file(
        "requirements.txt",
        name="Dependencies",
        attachment_type=allure.attachment_type.TEXT
    )