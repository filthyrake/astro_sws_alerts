#!/usr/bin/env python3
"""
Test suite for mount_scraper.py
Tests that the module can be imported without environment variables set.
"""

import sys
import os
import unittest

# Ensure environment variables are not set for these tests
for var in ["PHONE_NUMBER", "EMAIL", "PASSWORD", "SWS_URL"]:
    if var in os.environ:
        del os.environ[var]

import mount_scraper


class TestModuleImport(unittest.TestCase):
    """Test that the module can be imported without environment variables."""
    
    def test_module_imports_without_env_vars(self):
        """Test that mount_scraper can be imported without environment variables set."""
        # If we got here, the import succeeded
        self.assertTrue(True)
    
    def test_send_message_function_exists(self):
        """Test that send_message function is available after import."""
        self.assertTrue(hasattr(mount_scraper, 'send_message'))
        self.assertTrue(callable(mount_scraper.send_message))
    
    def test_global_vars_exist_but_are_none(self):
        """Test that global variables exist but are None when not set."""
        self.assertIsNone(mount_scraper.phone_number)
        self.assertIsNone(mount_scraper.EMAIL)
        self.assertIsNone(mount_scraper.PASSWORD)
        self.assertIsNone(mount_scraper.URL)


if __name__ == '__main__':
    unittest.main()
