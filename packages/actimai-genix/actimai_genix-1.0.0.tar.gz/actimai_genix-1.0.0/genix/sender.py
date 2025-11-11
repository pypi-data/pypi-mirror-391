import smtplib
from email.message import EmailMessage

class EmailSender:
    """
    A class to send emails via Gmail or Outlook using App Passwords.

    Example:
        sender = EmailSender("your_email@gmail.com", "app_password")
        sender.send_email(
            to="recipient@example.com",
            subject="Hello",
            body="This is a test email."
        )
    """

    SMTP_SERVERS = {
        "gmail": "smtp.gmail.com",
        "outlook": "smtp.office365.com"
    }

    SMTP_PORT = {
        "gmail": 465,   # SSL
        "outlook": 587  # TLS
    }

    def __init__(self, email: str, app_password: str, provider: str = "gmail"):
        self.email = email
        self.app_password = app_password
        self.provider = provider.lower()
        if self.provider not in self.SMTP_SERVERS:
            raise ValueError(f"Provider '{provider}' not supported. Choose 'gmail' or 'outlook'.")

    def send_email(self, to: str, subject: str, body: str = None, html: str = None):
        """
        Send an email, supporting plain text and HTML content.

        Args:
            to (str): Recipient email address
            subject (str): Email subject
            body (str, optional): Plain text content. Defaults to fallback if HTML is provided.
            html (str, optional): HTML content. Defaults to None.
        """
        msg = EmailMessage()
        msg['From'] = self.email
        msg['To'] = to
        msg['Subject'] = subject

        if html:
            # If HTML provided, use it, fallback plain text if body is None
            fallback_text = body if body else "This email contains HTML content."
            msg.set_content(fallback_text)
            msg.add_alternative(html, subtype='html')
        else:
            # Only plain text
            if not body:
                raise ValueError("Either 'body' or 'html' must be provided")
            msg.set_content(body)

        # Gmail uses SSL, Outlook uses STARTTLS
        if self.provider == "gmail":
            with smtplib.SMTP_SSL(self.SMTP_SERVERS[self.provider], self.SMTP_PORT[self.provider]) as server:
                server.login(self.email, self.app_password)
                server.send_message(msg)
        elif self.provider == "outlook":
            with smtplib.SMTP(self.SMTP_SERVERS[self.provider], self.SMTP_PORT[self.provider]) as server:
                server.starttls()
                server.login(self.email, self.app_password)
                server.send_message(msg)

        print(f"Email sent to {to} via {self.provider}!")
