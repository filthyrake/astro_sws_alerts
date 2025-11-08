#!/usr/bin/env python3
"""
Test suite for mount_scraper.py
Tests that the module can be imported without environment variables set.
"""

import os
import unittest
from unittest.mock import patch, MagicMock
import smtplib

# Ensure environment variables are not set for these tests
for var in ["PHONE_NUMBER", "EMAIL", "PASSWORD", "SWS_URL"]:
    if var in os.environ:
        del os.environ[var]

import mount_scraper


class TestModuleImport(unittest.TestCase):
    """Test that the module can be imported without environment variables."""
    
    def test_module_imports_without_env_vars(self):
        """Test that mount_scraper can be imported without environment variables set."""
        self.assertIsNotNone(mount_scraper)
        self.assertEqual(type(mount_scraper).__name__, "module")
    
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
    
    def test_send_message_validates_inputs(self):
        """Test that send_message validates required parameters."""
        # Test with missing phone_number
        with self.assertRaises(ValueError) as context:
            mount_scraper.send_message(None, "test message")
        self.assertIn("phone_number is required", str(context.exception))
        
        # Test with missing EMAIL/PASSWORD (they should be None from cleared env vars)
        with self.assertRaises(ValueError) as context:
            mount_scraper.send_message("5551234567", "test message")
        self.assertIn("EMAIL and PASSWORD environment variables must be set", str(context.exception))


class TestSMTPErrorHandling(unittest.TestCase):
    """Test SMTP error handling in send_message function."""
    
    def setUp(self):
        """Set up test environment with mock credentials."""
        os.environ["EMAIL"] = "test@example.com"
        os.environ["PASSWORD"] = "test_password"
        # Reload module to pick up new environment variables
        import importlib
        importlib.reload(mount_scraper)
    
    def tearDown(self):
        """Clean up environment variables after tests."""
        for var in ["EMAIL", "PASSWORD"]:
            if var in os.environ:
                del os.environ[var]
    
    @patch('smtplib.SMTP')
    def test_smtp_authentication_error_exits(self, mock_smtp):
        """Test that SMTPAuthenticationError causes script to exit with error message."""
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        mock_server.login.side_effect = smtplib.SMTPAuthenticationError(535, b'Authentication failed')
        
        with self.assertRaises(SystemExit) as context:
            mount_scraper.send_message("5551234567", "test message")
        
        self.assertEqual(context.exception.code, 1)
        mock_server.quit.assert_called_once()
    
    @patch('smtplib.SMTP')
    def test_smtp_general_exception_exits(self, mock_smtp):
        """Test that general SMTPException causes script to exit with error message."""
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        mock_server.sendmail.side_effect = smtplib.SMTPException("Connection lost")
        
        with self.assertRaises(SystemExit) as context:
            mount_scraper.send_message("5551234567", "test message")
        
        self.assertEqual(context.exception.code, 1)
        mock_server.quit.assert_called_once()
    
    @patch('smtplib.SMTP')
    def test_smtp_connect_error_exits(self, mock_smtp):
        """Test that SMTPConnectError causes script to exit with error message."""
        mock_smtp.side_effect = smtplib.SMTPConnectError(421, b'Cannot connect')
        
        with self.assertRaises(SystemExit) as context:
            mount_scraper.send_message("5551234567", "test message")
        
        self.assertEqual(context.exception.code, 1)
    
    @patch('smtplib.SMTP')
    def test_successful_send_calls_quit(self, mock_smtp):
        """Test that successful send properly cleans up connection."""
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        mount_scraper.send_message("5551234567", "test message")
        
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with("test@example.com", "test_password")
        mock_server.sendmail.assert_called_once()
        mock_server.quit.assert_called_once()
    
    @patch('smtplib.SMTP')
    def test_quit_error_ignored_after_auth_failure(self, mock_smtp):
        """Test that errors during quit() are gracefully ignored."""
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        mock_server.login.side_effect = smtplib.SMTPAuthenticationError(535, b'Auth failed')
        mock_server.quit.side_effect = Exception("Connection already closed")
        
        with self.assertRaises(SystemExit):
            mount_scraper.send_message("5551234567", "test message")
        
        # Should still try to quit despite the error
        mock_server.quit.assert_called_once()


class TestHTMLElementValidation(unittest.TestCase):
    """Test HTML element validation for driver status elements."""
    
    def setUp(self):
        """Set up test environment with mock credentials."""
        os.environ["EMAIL"] = "test@example.com"
        os.environ["PASSWORD"] = "test_password"
        # Reload module to pick up new environment variables
        import importlib
        importlib.reload(mount_scraper)
    
    def tearDown(self):
        """Clean up environment variables after tests."""
        for var in ["EMAIL", "PASSWORD"]:
            if var in os.environ:
                del os.environ[var]
        # Reload module to clear environment variables
        import importlib
        importlib.reload(mount_scraper)
    
    @patch('mount_scraper.send_message')
    @patch('mount_scraper.requests.get')
    def test_both_driver_elements_found(self, mock_get, mock_send):
        """Test that script continues when both driver elements are found."""
        # Create mock response with both driver elements present
        mock_response = MagicMock()
        mock_response.content = b'''
        <html>
            <div id="dvr_stat0">Standstill</div>
            <div id="dvr_stat1">Done</div>
        </html>
        '''
        mock_get.return_value = mock_response
        
        # Should not raise SystemExit since both elements exist with valid statuses
        try:
            mount_scraper.check_driver_status("http://example.com/test.html", "5551234567")
        except SystemExit:
            self.fail("Script should not exit when both driver elements are found with valid statuses")
    
    @patch('mount_scraper.send_message')
    @patch('mount_scraper.requests.get')
    def test_driver1_element_missing(self, mock_get, mock_send):
        """Test that script exits with error when driver1 element is missing."""
        # Create mock response with driver1 element missing
        mock_response = MagicMock()
        mock_response.content = b'''
        <html>
            <div id="dvr_stat1">Done</div>
        </html>
        '''
        mock_get.return_value = mock_response
        
        # Script should exit with error when driver1 element is missing
        with self.assertRaises(SystemExit) as context:
            mount_scraper.check_driver_status("http://example.com/test.html", "5551234567")
        
        self.assertEqual(context.exception.code, 1)
    
    @patch('mount_scraper.send_message')
    @patch('mount_scraper.requests.get')
    def test_driver2_element_missing(self, mock_get, mock_send):
        """Test that script exits with error when driver2 element is missing."""
        # Create mock response with driver2 element missing
        mock_response = MagicMock()
        mock_response.content = b'''
        <html>
            <div id="dvr_stat0">Standstill</div>
        </html>
        '''
        mock_get.return_value = mock_response
        
        # Script should exit with error when driver2 element is missing
        with self.assertRaises(SystemExit) as context:
            mount_scraper.check_driver_status("http://example.com/test.html", "5551234567")
        
        self.assertEqual(context.exception.code, 1)
    
    @patch('mount_scraper.send_message')
    @patch('mount_scraper.requests.get')
    def test_both_driver_elements_missing(self, mock_get, mock_send):
        """Test that script exits with error when both driver elements are missing."""
        # Create mock response with both driver elements missing
        mock_response = MagicMock()
        mock_response.content = b'''
        <html>
            <div id="some_other_element">Other content</div>
        </html>
        '''
        mock_get.return_value = mock_response
        
        # Script should exit with error when both driver elements are missing
        with self.assertRaises(SystemExit) as context:
            mount_scraper.check_driver_status("http://example.com/test.html", "5551234567")
        
        self.assertEqual(context.exception.code, 1)


if __name__ == '__main__':
    unittest.main()
