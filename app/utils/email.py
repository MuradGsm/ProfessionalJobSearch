import smtplib
import secrets
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from datetime import datetime, timedelta
import logging
from app.config.setting import settings

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.username = settings.SMTP_USERNAME
        self.password = settings.SMTP_PASSWORD

    async def send_email(self, to_email: str, subject: str, body: str, is_html: bool = False) -> bool:
        """Send email via SMTP"""
        if not all([self.smtp_server, self.username, self.password]):
            logger.warning("SMTP not configured, skipping email send")
            return False

        try:
            message = MIMEMultipart()
            message["From"] = self.username
            message["To"] = to_email
            message["Subject"] = subject

            message.attach(MIMEText(body, 'html' if is_html else 'plain'))

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(message)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False

    async def send_verification_email(self, to_email: str, token: str) -> bool:
        """Send email verification email"""
        subject = "Verify your email address"
        body = f"""
        <h2>Email Verification</h2>
        <p>Please click the link below to verify your email address:</p>
        <a href="http://localhost:8000/auth/verify-email?token={token}">Verify Email</a>
        <p>If you didn't create an account, please ignore this email.</p>
        <p>This link will expire in 24 hours.</p>
        """
        return await self.send_email(to_email, subject, body, is_html=True)

    async def send_password_reset_email(self, to_email: str, token: str) -> bool:
        """Send password reset email"""
        subject = "Password Reset Request"
        body = f"""
        <h2>Password Reset</h2>
        <p>You requested a password reset. Click the link below to reset your password:</p>
        <a href="http://localhost:8000/auth/verify-email?token={token}">Reset Password</a>
        <p>If you didn't request this, please ignore this email.</p>
        <p>This link will expire in 1 hour.</p>
        """
        return await self.send_email(to_email, subject, body, is_html=True)

    async def send_welcome_email(self, to_email: str, name: str) -> bool:
        """Send welcome email to new user"""
        subject = "Welcome to Job Platform!"
        body = f"""
        <h2>Welcome {name}!</h2>
        <p>Thank you for joining our job platform.</p>
        <p>You can now start exploring job opportunities or posting jobs.</p>
        <p>Best regards,<br>The Job Platform Team</p>
        """
        return await self.send_email(to_email, subject, body, is_html=True)

email_service = EmailService()