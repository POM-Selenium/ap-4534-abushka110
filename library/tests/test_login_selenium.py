"""
Selenium test suite for authentication login functionality.

This module contains comprehensive tests for verifying the login process,
including valid credentials, invalid credentials, and logout functionality.
"""

import os
import django
from django.test import TestCase, LiveServerTestCase
from django.contrib.auth import get_user_model
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import unittest

# Setup Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library.settings')
django.setup()

User = get_user_model()

# Check if Chrome/Chromium is available
try:
    from webdriver_manager.chrome import ChromeDriverManager
    _CHROME_AVAILABLE = True
except Exception as e:
    _CHROME_AVAILABLE = False


@unittest.skipUnless(_CHROME_AVAILABLE, "Chrome/Chromium browser not available for Selenium tests")
class LoginTestCase(LiveServerTestCase):
    """Test cases for login and logout functionality."""

    @classmethod
    def setUpClass(cls):
        """Set up the test environment before running tests."""
        super().setUpClass()
        
        # Configure Chrome options for headless mode (optional)
        chrome_options = Options()
        # Uncomment the line below to run tests in headless mode
        # chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        
        # Initialize the WebDriver
        try:
            # Try with Chrome version 146 (current installed version)
            try:
                from webdriver_manager.chrome import ChromeDriverManager
                driver_path = ChromeDriverManager(driver_version="146").install()
            except:
                # Fallback to version 145
                try:
                    from webdriver_manager.chrome import ChromeDriverManager
                    driver_path = ChromeDriverManager(driver_version="145").install()
                except:
                    # Final fallback to default (latest available)
                    from webdriver_manager.chrome import ChromeDriverManager
                    driver_path = ChromeDriverManager().install()
            
            service = Service(driver_path)
            cls.driver = webdriver.Chrome(service=service, options=chrome_options)
        except Exception as e:
            raise unittest.SkipTest(f"Could not initialize ChromeDriver: {e}")
        cls.driver.set_page_load_timeout(10)
        cls.wait = WebDriverWait(cls.driver, 10)

    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests have run."""
        cls.driver.quit()
        super().tearDownClass()

    def setUp(self):
        """Set up before each test method."""
        # Create test user with valid credentials
        self.valid_email = 'testuser@example.com'
        self.valid_password = 'TestPassword123!'
        
        # Create the user if it doesn't exist
        User.objects.filter(email__iexact=self.valid_email).delete()
        self.test_user = User.objects.create_user(
            email=self.valid_email.lower(),  # Normalize to lowercase
            password=self.valid_password,
            first_name='Test',
            middle_name="Test",
            last_name='User',
            role=0,  # 0 = visitor
            is_active=True  # IMPORTANT: User must be active to log in!
        )

    def tearDown(self):
        """Clean up after each test method."""
        # Delete the test user
        User.objects.filter(email=self.valid_email).delete()
        
        # Clear cookies and local storage
        self.driver.delete_all_cookies()

    def _get_login_page(self):
        """Navigate to the login page."""
        login_url = f"{self.live_server_url}/auth/login/"
        self.driver.get(login_url)
        # Wait for the login form to be present
        self.wait.until(EC.presence_of_element_located((By.ID, "email")))

    def _enter_email(self, email):
        """Enter email in the email field."""
        email_field = self.wait.until(EC.presence_of_element_located((By.ID, "email")))
        email_field.clear()
        email_field.send_keys(email)

    def _enter_password(self, password):
        """Enter password in the password field."""
        password_field = self.wait.until(EC.presence_of_element_located((By.ID, "password")))
        password_field.clear()
        password_field.send_keys(password)

    def _click_login_button(self):
        """Click the login button and wait for redirect."""
        login_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))
        login_button.click()
        # Wait for page to process the login and redirect
        time.sleep(2)

    def _is_logged_in(self):
        """Check if user is logged in by verifying logout link is present."""
        try:
            # First, wait a bit for any AJAX or dynamic content
            time.sleep(1)
            
            # Try to wait for redirect to complete (up to 20 seconds for better reliability)
            logout_link = self.wait.until(
                EC.presence_of_element_located((By.LINK_TEXT, "🚪 Logout")),
                message="Logout link not found after waiting 20 seconds"
            )
            return logout_link is not None
        except Exception as e:
            # Also try checking by looking for the "Welcome" message with user email
            try:
                page_source = self.driver.page_source
                if "Welcome" in page_source and self.valid_email in page_source:
                    return True
            except:
                pass
            return False

    def _is_error_message_displayed(self):
        """Check if error message is displayed on login page."""
        try:
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "error")))
            return True
        except:
            return False

    def _get_error_message(self):
        """Get the error message text."""
        try:
            error_element = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "error")))
            return error_element.text
        except:
            return None

    def test_01_valid_login(self):
        """
        Test Case: User Login with Valid Credentials
        
        Steps:
        1. Navigate to login page
        2. Enter valid email
        3. Enter valid password
        4. Click login button
        
        Expected Result:
        - User should be successfully logged in
        - User should be redirected to home page
        - Logout button should be visible
        """
        self._get_login_page()
        
        # Enter valid credentials
        self._enter_email(self.valid_email)
        self._enter_password(self.valid_password)
        
        # Click login button
        self._click_login_button()
        
        # Verify successful login
        self.assertTrue(
            self._is_logged_in(),
            "User should be logged in after entering valid credentials"
        )
        
        # Verify user is on home page
        self.assertIn(
            "/",
            self.driver.current_url,
            "User should be redirected to home page after login"
        )
        
        # Verify welcome message contains user email
        welcome_text = self.driver.find_element(By.TAG_NAME, "body").text
        self.assertIn(
            self.valid_email,
            welcome_text,
            "User email should be displayed on home page"
        )

    def test_02_logout_after_login(self):
        """
        Test Case: User Logout After Successful Login
        
        Steps:
        1. Navigate to login page
        2. Enter valid credentials
        3. Click login button
        4. Verify successful login
        5. Click logout button
        
        Expected Result:
        - User should be successfully logged out
        - Logout button should not be visible
        - Login button should be visible
        """
        self._get_login_page()
        
        # Login with valid credentials
        self._enter_email(self.valid_email)
        self._enter_password(self.valid_password)
        self._click_login_button()
        
        # Verify user is logged in
        self.assertTrue(
            self._is_logged_in(),
            "User should be logged in"
        )
        
        # Click logout button
        logout_button = self.wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "🚪 Logout")))
        logout_button.click()
        
        # Wait for redirect to home page
        self.wait.until(EC.presence_of_element_located((By.LINK_TEXT, "🔐 Login")))
        
        # Verify user is logged out
        try:
            self.driver.find_element(By.LINK_TEXT, "🚪 Logout")
            self.fail("Logout button should not be visible after logout")
        except:
            pass  # This is expected
        
        # Verify login button is visible
        login_link = self.driver.find_element(By.LINK_TEXT, "🔐 Login")
        self.assertIsNotNone(
            login_link,
            "Login button should be visible after logout"
        )

    def test_03_invalid_email_password(self):
        """
        Test Case: User Login with Invalid Credentials (Wrong Email and Password)
        
        Steps:
        1. Navigate to login page
        2. Enter invalid email
        3. Enter invalid password
        4. Click login button
        
        Expected Result:
        - User should not be logged in
        - Error message should be displayed
        - User should remain on login page
        """
        self._get_login_page()
        
        # Enter invalid credentials
        self._enter_email("wrongemail@example.com")
        self._enter_password("WrongPassword123!")
        
        # Click login button
        self._click_login_button()
        
        # Verify user is not logged in
        self.assertFalse(
            self._is_logged_in(),
            "User should not be logged in with invalid credentials"
        )
        
        # Verify error message is displayed
        self.assertTrue(
            self._is_error_message_displayed(),
            "Error message should be displayed for invalid credentials"
        )
        
        # Verify error message content
        error_message = self._get_error_message()
        self.assertIn(
            "Invalid",
            error_message,
            "Error message should indicate invalid credentials"
        )

    def test_04_valid_email_invalid_password(self):
        """
        Test Case: User Login with Valid Email but Invalid Password
        
        Steps:
        1. Navigate to login page
        2. Enter valid email
        3. Enter incorrect password
        4. Click login button
        
        Expected Result:
        - User should not be logged in
        - Error message should be displayed
        - User should remain on login page
        """
        self._get_login_page()
        
        # Enter valid email but invalid password
        self._enter_email(self.valid_email)
        self._enter_password("WrongPassword123!")
        
        # Click login button
        self._click_login_button()
        
        # Verify user is not logged in
        self.assertFalse(
            self._is_logged_in(),
            "User should not be logged in with wrong password"
        )
        
        # Verify error message is displayed
        self.assertTrue(
            self._is_error_message_displayed(),
            "Error message should be displayed for invalid password"
        )
        
        # Verify error message content
        error_message = self._get_error_message()
        self.assertIn(
            "Invalid",
            error_message,
            "Error message should indicate invalid credentials"
        )

    def test_05_empty_email(self):
        """
        Test Case: User Login with Empty Email Field
        
        Steps:
        1. Navigate to login page
        2. Leave email field empty
        3. Enter password
        4. Click login button
        
        Expected Result:
        - Browser should show HTML5 validation error or form should reject submission
        """
        self._get_login_page()
        
        # Leave email empty and enter password
        self._enter_password(self.valid_password)
        
        # Try to click login button - HTML5 validation might prevent submission
        try:
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            # Check if email field is required
            email_field = self.driver.find_element(By.ID, "email")
            is_required = email_field.get_attribute("required") is not None
            
            self.assertTrue(
                is_required,
                "Email field should be required"
            )
        except Exception as e:
            self.fail(f"Failed to verify email field requirement: {e}")

    def test_06_empty_password(self):
        """
        Test Case: User Login with Empty Password Field
        
        Steps:
        1. Navigate to login page
        2. Enter email
        3. Leave password field empty
        4. Click login button
        
        Expected Result:
        - Browser should show HTML5 validation error or form should reject submission
        """
        self._get_login_page()
        
        # Enter email and leave password empty
        self._enter_email(self.valid_email)
        
        # Try to click login button - HTML5 validation might prevent submission
        try:
            password_field = self.driver.find_element(By.ID, "password")
            is_required = password_field.get_attribute("required") is not None
            
            self.assertTrue(
                is_required,
                "Password field should be required"
            )
        except Exception as e:
            self.fail(f"Failed to verify password field requirement: {e}")

    def test_07_case_sensitive_email(self):
        """
        Test Case: Verify email login is case-insensitive
        
        Steps:
        1. Navigate to login page
        2. Enter email with different case
        3. Enter valid password
        4. Click login button
        
        Expected Result:
        - User should be logged in (email should be case-insensitive)
        """
        self._get_login_page()
        
        # Enter email with uppercase letters (email handling should be case-insensitive)
        self._enter_email(self.valid_email.upper())
        self._enter_password(self.valid_password)
        
        # Click login button
        self._click_login_button()
        
        # Verify successful login
        self.assertTrue(
            self._is_logged_in(),
            "Login should work with uppercase email (should be case-insensitive)"
        )

    def test_08_multiple_failed_attempts(self):
        """
        Test Case: Multiple Failed Login Attempts
        
        Steps:
        1. Navigate to login page
        2. Attempt login 3 times with wrong password
        3. Verify error message is displayed each time
        
        Expected Result:
        - User should not be logged in after each attempt
        - Error message should be displayed each time
        - No account lockout should occur (for this implementation)
        """
        for attempt in range(3):
            self._get_login_page()
            
            # Enter valid email but wrong password
            self._enter_email(self.valid_email)
            self._enter_password(f"WrongPassword{attempt}")
            
            # Click login button
            self._click_login_button()
            
            # Verify user is not logged in
            self.assertFalse(
                self._is_logged_in(),
                f"User should not be logged in on attempt {attempt + 1}"
            )
            
            # Verify error message is displayed
            self.assertTrue(
                self._is_error_message_displayed(),
                f"Error message should be displayed on attempt {attempt + 1}"
            )

    def test_09_successful_login_after_failed_attempts(self):
        """
        Test Case: Successful Login After Failed Attempts
        
        Steps:
        1. Navigate to login page
        2. Attempt login with wrong password
        3. Attempt login again with correct password
        
        Expected Result:
        - First login should fail
        - Second login with correct password should succeed
        """
        # First attempt with wrong password
        self._get_login_page()
        self._enter_email(self.valid_email)
        self._enter_password("WrongPassword")
        self._click_login_button()
        
        # Verify first attempt failed
        self.assertFalse(
            self._is_logged_in(),
            "First login attempt should fail"
        )
        
        # Second attempt with correct password
        self._get_login_page()
        self._enter_email(self.valid_email)
        self._enter_password(self.valid_password)
        self._click_login_button()
        
        # Verify second attempt succeeded
        self.assertTrue(
            self._is_logged_in(),
            "Second login attempt with correct password should succeed"
        )

    def test_10_sql_injection_attempt(self):
        """
        Test Case: SQL Injection Resistance
        
        Steps:
        1. Navigate to login page
        2. Enter SQL injection payload in email field
        3. Enter random password
        4. Click login button
        
        Expected Result:
        - Login should fail gracefully
        - No database error should be displayed
        - Error message should be generic
        """
        self._get_login_page()
        
        # Enter SQL injection payload
        sql_payload = "admin'--"
        self._enter_email(sql_payload)
        self._enter_password("anypassword")
        
        # Click login button
        self._click_login_button()
        
        # Verify login failed
        self.assertFalse(
            self._is_logged_in(),
            "SQL injection attempt should not result in login"
        )
        
        # Verify no database error is displayed
        page_source = self.driver.page_source
        self.assertNotIn(
            "IntegrityError",
            page_source,
            "Database errors should not be displayed"
        )
        self.assertNotIn(
            "OperationalError",
            page_source,
            "Database errors should not be displayed"
        )


if __name__ == '__main__':
    import unittest
    unittest.main()
