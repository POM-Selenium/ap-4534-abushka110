# Selenium Login Tests

## Overview

This directory contains comprehensive Selenium tests for the authentication/login functionality of the Library Management System. The tests verify various scenarios including:

- ✅ Valid login with correct credentials
- ✅ Logout functionality
- ✅ Invalid login attempts (wrong email/password)
- ✅ Empty field validation
- ✅ Case-insensitive email handling
- ✅ Multiple failed login attempts
- ✅ Security testing (SQL injection resistance)

## Test File

**File:** `test_login_selenium.py`

## Prerequisites

1. **Install Dependencies:**
   ```bash
   pip install -r ../requirements.txt
   ```

2. **Google Chrome/Chromium:** Must be installed on your system. The tests use ChromeDriver which is automatically managed by `webdriver-manager`.

3. **Django Project:** The project must be properly configured and migrations applied.

## Test Cases

### 1. test_01_valid_login
**Description:** Verifies successful login with valid credentials
- Navigates to login page
- Enters valid email and password
- Clicks login button
- Verifies user is logged in and redirected to home page

**Expected Result:** ✅ Login succeeds, user sees personalized welcome message

---

### 2. test_02_logout_after_login
**Description:** Verifies logout functionality after successful login
- Logs in with valid credentials
- Clicks logout button
- Verifies logout link disappears
- Verifies login link reappears

**Expected Result:** ✅ User is successfully logged out

---

### 3. test_03_invalid_email_password
**Description:** Verifies login fails with completely invalid credentials
- Enters non-existent email
- Enters wrong password
- Clicks login button
- Verifies error message is displayed

**Expected Result:** ❌ Login fails with error message

---

### 4. test_04_valid_email_invalid_password
**Description:** Verifies login fails with valid email but wrong password
- Enters valid email
- Enters incorrect password
- Clicks login button
- Verifies error message is displayed

**Expected Result:** ❌ Login fails with error message

---

### 5. test_05_empty_email
**Description:** Verifies email field validation (HTML5 required attribute)
- Leaves email field empty
- Enters password
- Verifies email field has required attribute

**Expected Result:** ✅ Email field is validated as required

---

### 6. test_06_empty_password
**Description:** Verifies password field validation (HTML5 required attribute)
- Enters email
- Leaves password field empty
- Verifies password field has required attribute

**Expected Result:** ✅ Password field is validated as required

---

### 7. test_07_case_sensitive_email
**Description:** Verifies email comparison is case-insensitive
- Enters email with uppercase letters
- Enters valid password
- Clicks login button
- Verifies login succeeds

**Expected Result:** ✅ Login succeeds (email handling is case-insensitive)

---

### 8. test_08_multiple_failed_attempts
**Description:** Verifies system handles multiple failed login attempts
- Attempts login 3 times with wrong passwords
- Verifies error message appears each time
- Verifies no account lockout occurs

**Expected Result:** ✅ System remains functional after failed attempts

---

### 9. test_09_successful_login_after_failed_attempts
**Description:** Verifies successful login is possible after previous failures
- Attempts login with wrong password
- Attempts login again with correct password
- Verifies correct login succeeds

**Expected Result:** ✅ Second login with correct credentials succeeds

---

### 10. test_10_sql_injection_attempt
**Description:** Verifies SQL injection resistance
- Enters SQL injection payload in email field
- Clicks login button
- Verifies no database errors are displayed
- Verifies login fails gracefully

**Expected Result:** ✅ System handles malicious input safely

---

## How to Run Tests

### Run All Tests
```bash
python manage.py test tests.test_login_selenium
```

### Run Specific Test Class
```bash
python manage.py test tests.test_login_selenium.LoginTestCase
```

### Run Specific Test Method
```bash
python manage.py test tests.test_login_selenium.LoginTestCase.test_01_valid_login
```

### Run Tests with Verbose Output
```bash
python manage.py test tests.test_login_selenium -v 2
```

### Run Tests in Headless Mode
Edit the `test_login_selenium.py` file and uncomment this line in the `setUpClass` method:
```python
chrome_options.add_argument("--headless")
```

### Run Tests in Interactive Mode
By default, the tests run with the browser window visible. This allows you to watch the tests execute in real-time.

## Important Notes

1. **LiveServerTestCase:** The tests use Django's `LiveServerTestCase` which automatically starts a test server on a random port during test execution.

2. **Test Database:** The tests use an isolated test database that is created before tests run and destroyed after.

3. **Test User:** A test user with the following credentials is created for each test:
   - **Email:** `testuser@example.com`
   - **Password:** `TestPassword123!`
   - **Role:** Guest (0)

4. **Chrome Driver:** ChromeDriver is automatically downloaded by `webdriver-manager`. No manual installation required.

5. **Wait Times:** All element interactions use explicit waits (10 seconds timeout) to handle slow page loads.

## Troubleshooting

### Chrome/Chromium Not Found
Ensure Google Chrome or Chromium is installed on your system:
- **macOS:** `brew install google-chrome`
- **Ubuntu:** `sudo apt-get install google-chrome-stable`
- **Windows:** Download from https://www.google.com/chrome

### Port Already in Use
If you get a "port already in use" error, try:
```bash
python manage.py test tests.test_login_selenium --keepdb
```

### Import Errors
Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
pip install selenium webdriver-manager
```

### Timeout Errors
If tests fail with timeout errors:
1. Increase the timeout in the test: `WebDriverWait(cls.driver, 20)` (change 10 to 20)
2. Check your system performance
3. Run in headless mode for potentially faster execution

## Test Coverage

The test suite covers:
- ✅ Happy path (valid login)
- ✅ Sad path (invalid credentials)
- ✅ Edge cases (empty fields, case sensitivity)
- ✅ Security (SQL injection attempts)
- ✅ User workflow (login → logout → login)
- ✅ Error handling (multiple failed attempts)

## Best Practices

1. **Isolate Tests:** Each test is independent and sets up its own test user
2. **Clean Setup/Teardown:** Resources are properly cleaned up after each test
3. **Wait Strategies:** Uses explicit waits instead of sleep() for reliability
4. **Descriptive Names:** Test method names clearly describe what is being tested
5. **Comprehensive Documentation:** Each test includes docstring explaining its purpose

## Continuous Integration

These tests can be integrated into CI/CD pipelines. Example for GitHub Actions:

```yaml
- name: Run Selenium Tests
  run: |
    python manage.py test tests.test_login_selenium -v 2
```

## Contributing

When adding new tests:
1. Follow the naming convention: `test_XX_description_of_test`
2. Include docstring explaining the test scenario
3. Use the helper methods (`_enter_email`, `_click_login_button`, etc.)
4. Add corresponding documentation to this README

## License

These tests are part of the Library Management System project.
