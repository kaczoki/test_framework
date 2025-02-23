import pytest
from pathlib import Path
import os 

import sys
sys.path.append("./helpers/")


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