import smtplib
from email.mime.text import MIMEText
from dataclasses import dataclass
from typing import List

from src.utils.logger import ConsoleLogger


@dataclass
class SMTPConfig:
    smtp_server: str
    smtp_port: int
    smtp_username: str
    smtp_password: str
    sender: str
    recipients: List[str]


def send_email(config: SMTPConfig, subject: str, body: str):
    logger = ConsoleLogger()
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = config.sender
    msg['To'] = ', '.join(config.recipients)

    try:
        with smtplib.SMTP_SSL(config.smtp_server, config.smtp_port) as server:
            server.login(config.smtp_username, config.smtp_password)
            server.sendmail(config.sender, config.recipients, msg.as_string())
            logger.info(f"Email [{subject}] sent successfully!")
    except Exception as e:
        logger.info(f"Failed to send email. Error: {str(e)}")
