from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from app.core import config
from typing import List
import logging

logger = logging.getLogger(__name__)


class EmailService:
    @staticmethod
    def send_email(to_emails: List[str], subject: str, html_content: str) -> bool:
        """Send an email to one or more recipients"""
        if not config.EMAIL_ENABLED:
            logger.info(f"Email sending is disabled. Would have sent to {to_emails}: {subject}")
            return False

        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{config.EMAIL_FROM_NAME} <{config.EMAIL_FROM}>"
            msg['To'] = ", ".join(to_emails)

            msg.attach(MIMEText(html_content, 'html'))

            with smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT) as server:
                server.starttls()
                server.login(str(config.SMTP_USER), str(config.SMTP_PASSWORD))
                server.send_message(msg)

            return True

        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False

    @staticmethod
    def notify_project_assignment(user_email: str, project_name: str, project_url: str):
        """Send notification when user is assigned to a project"""
        subject = f"You've been added to project: {project_name}"
        html_content = f"""
        <h2>Project Assignment Notification</h2>
        <p>You have been added to the project: <strong>{project_name}</strong></p>
        <p>Click <a href="{project_url}">here</a> to view the project.</p>
        """
        return EmailService.send_email([user_email], subject, html_content)

    @staticmethod
    def notify_task_assignment(user_email: str, task_name: str, project_name: str, task_url: str):
        """Send notification when task is assigned to user"""
        subject = f"New task assigned: {task_name}"
        html_content = f"""
        <h2>Task Assignment Notification</h2>
        <p>You have been assigned a new task in project {project_name}:</p>
        <p><strong>{task_name}</strong></p>
        <p>Click <a href="{task_url}">here</a> to view the task.</p>
        """
        return EmailService.send_email([user_email], subject, html_content)

    @staticmethod
    def notify_task_completed(user_emails: List[str], task_name: str, project_name: str, completed_by: str):
        """Send notification when task is marked as completed"""
        subject = f"Task completed: {task_name}"
        html_content = f"""
        <h2>Task Completion Notification</h2>
        <p>A task in project {project_name} has been marked as completed:</p>
        <p><strong>{task_name}</strong></p>
        <p>Completed by: {completed_by}</p>
        """
        return EmailService.send_email(user_emails, subject, html_content)

    @staticmethod
    def notify_project_completed(user_emails: List[str], project_name: str):
        """Send notification when project is marked as completed"""
        subject = f"Project completed: {project_name}"
        html_content = f"""
        <h2>Project Completion Notification</h2>
        <p>The following project has been marked as completed:</p>
        <p><strong>{project_name}</strong></p>
        <p>Congratulations to all team members!</p>
        """
        return EmailService.send_email(user_emails, subject, html_content)
