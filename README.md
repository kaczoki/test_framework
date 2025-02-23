# Mend Test Framework

A comprehensive test automation framework for testing GitHub functionality through API, GUI, and Git operations.

## Prerequisites

- Python 3.8 or higher
- Git
- GitHub account
- Allure command line tool (for reporting)

## Installation

1. Clone the repository:
```
git clone https://github.com/kaczoki/test_framework.git
cd test_framework
```

2. Create and activate virtual environment:
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```
pip install -r requirements.txt
```

4. Install Playwright browsers:
```
playwright install
```

5. Create pytest.ini file in the root directory with the following environment variables:
```
[pytest]
env =
    GITHUB_USERNAME=your_github_username
    GITHUB_PASSWORD=your_github_password
    GITHUB_API_KEY=your_github_api_token
    BASE_URL=https://api.github.com
    BASE_URL_GUI=https://github.com
```

## Running Tests

### API Tests
Run GitHub API tests:
```
pytest tests/API/ -v
```

### GUI Tests
Run GitHub GUI tests (supports parallel execution):
```
pytest tests/GUI/ -v          # Run tests using headless browser
```

### Git Tests
Run Git operation tests:
```
pytest tests/GIT/ -v
```

### Run All Tests
Execute all test suites:
```
pytest tests/ -v
```

## Parallel Test Execution

The GUI tests are configured for parallel execution using pytest-xdist. Each test instance creates a unique repository name to prevent conflicts during parallel runs. The number of parallel processes can be configured using the -n parameter.

## Generating Reports

### Allure Reports

1. Run tests with Allure:
```
pytest --alluredir=./reports
```

2. Generate and open the report:
```
allure serve ./reports
```

### HTML Report
Generate a simple HTML report:
```
pytest --html=report.html
```

## Project Structure

- tests/API/ - API test suites
- tests/GUI/ - GUI test suites using Playwright
- tests/GIT/ - Git operation test suites
- tests/GUI/pages/ - Page Object Models
- tests/api_helpers/ - Helper functions for API testing
- reports/ - Test execution reports available after running tests

## Notes

- The framework uses Playwright for GUI testing
- Tests are configured with Allure for detailed reporting
- Environment variables must be set in pytest.ini before running tests
- GUI tests support parallel execution with unique repository names
- All tests include detailed logging and error reporting

