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


if __name__ == '__main__':
    unittest.main()
