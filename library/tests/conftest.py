"""
Configuration and helper utilities for Selenium tests.

This module provides common utilities and configuration for all Selenium tests.
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the Python path to allow imports
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Set up Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library.settings')

import django
django.setup()


class SeleniumTestConfig:
    """Configuration class for Selenium tests."""
    
    # Browser configuration
    BROWSER_TIMEOUT = 10  # seconds
    PAGE_LOAD_TIMEOUT = 10  # seconds
    
    # Chrome options
    HEADLESS = False  # Set to True to run in headless mode
    NO_SANDBOX = True
    DISABLE_DEV_SHM = True
    DISABLE_GPU = True
    WINDOW_SIZE = "1920,1080"
    
    # Test user credentials
    TEST_USER_EMAIL = "testuser@example.com"
    TEST_USER_PASSWORD = "TestPassword123!"
    TEST_USER_FIRST_NAME = "Test"
    TEST_USER_LAST_NAME = "User"
    TEST_USER_ROLE = 0  # 0 = visitor, 1 = librarian
    
    # Database
    TEST_DATABASE = None  # Uses Django's test database by default
    
    # Logging
    VERBOSE = True
    LOG_LEVEL = "INFO"
    
    @classmethod
    def get_chrome_options(cls):
        """Get configured Chrome options for WebDriver.
        
        Returns:
            Options: Configured Chrome options
        """
        from selenium.webdriver.chrome.options import Options
        
        options = Options()
        
        if cls.HEADLESS:
            options.add_argument("--headless")
        
        if cls.NO_SANDBOX:
            options.add_argument("--no-sandbox")
        
        if cls.DISABLE_DEV_SHM:
            options.add_argument("--disable-dev-shm-usage")
        
        if cls.DISABLE_GPU:
            options.add_argument("--disable-gpu")
        
        if cls.WINDOW_SIZE:
            options.add_argument(f"--window-size={cls.WINDOW_SIZE}")
        
        # Disable notifications
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        
        return options
    
    @classmethod
    def log(cls, message):
        """Log a message if verbose mode is enabled.
        
        Args:
            message (str): Message to log
        """
        if cls.VERBOSE:
            print(f"[Selenium Test] {message}")


# Export configuration
__all__ = ['SeleniumTestConfig']
