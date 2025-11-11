from genix import EmailSender

# Gmail example
gmail_sender = EmailSender("your_gmail@gmail.com", "your_app_password", provider="gmail")
gmail_sender.send_email(
    to="recipient@example.com",
    subject="Test Gmail",
    body="Hello from Gmail App Password!"
)

# Outlook example
outlook_sender = EmailSender("your_outlook@example.com", "your_app_password", provider="outlook")
outlook_sender.send_email(
    to="recipient@example.com",
    subject="Test Outlook",
    body="Hello from Outlook App Password!"
)
