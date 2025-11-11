import pytest
from genix import EmailSender
from unittest.mock import patch

def test_send_email_ssl():
    with patch("smtplib.SMTP_SSL") as mock_smtp:
        sender = EmailSender("test@gmail.com", "app_pass", "gmail")
        sender.send_email("to@example.com", "Subject", "Body")

        mock_smtp.assert_called_once_with("smtp.gmail.com", 465)
        instance = mock_smtp.return_value.__enter__.return_value
        instance.login.assert_called_once_with("test@gmail.com", "app_pass")
        assert instance.send_message.called

def test_send_email_tls():
    with patch("smtplib.SMTP") as mock_smtp:
        sender = EmailSender("test@outlook.com", "app_pass", "outlook")
        sender.send_email("to@example.com", "Subject", "Body")

        mock_smtp.assert_called_once_with("smtp.office365.com", 587)
        instance = mock_smtp.return_value.__enter__.return_value
        instance.starttls.assert_called_once()
        instance.login.assert_called_once_with("test@outlook.com", "app_pass")
        assert instance.send_message.called
