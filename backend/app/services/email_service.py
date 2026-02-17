from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from html import escape
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
        safe_name = escape(project_name)
        safe_url = escape(project_url)
        subject = f"Has sido añadido al proyecto: {safe_name}"
        html_content = f"""
        <h2>Notificación de Asignación de Proyecto</h2>
        <p>Has sido añadido al proyecto: <strong>{safe_name}</strong></p>
        <p>Conéctate a la VPN y haz clic <a href="{safe_url}">aquí</a> para ver el proyecto.</p>
        """
        return EmailService.send_email([user_email], subject, html_content)

    @staticmethod
    def notify_task_assignment(user_email: str, task_name: str, project_name: str, task_url: str):
        """Send notification when task is assigned to user"""
        safe_task = escape(task_name)
        safe_project = escape(project_name)
        safe_url = escape(task_url)
        subject = f"Nueva tarea asignada: {safe_task}"
        html_content = f"""
        <h2>Notificación de Asignación de Tarea</h2>
        <p>Se te ha asignado una nueva tarea en el proyecto {safe_project}:</p>
        <p><strong>{safe_task}</strong></p>
        <p>Haz clic <a href="{safe_url}">aquí</a> para ver la tarea.</p>
        """
        return EmailService.send_email([user_email], subject, html_content)

    @staticmethod
    def notify_task_completed(user_emails: List[str], task_name: str, project_name: str, completed_by: str):
        """Send notification when task is marked as completed"""
        safe_task = escape(task_name)
        safe_project = escape(project_name)
        safe_completed_by = escape(completed_by)
        subject = f"Tarea completada: {safe_task}"
        html_content = f"""
        <h2>Notificación de Tarea Completada</h2>
        <p>Una tarea en el proyecto {safe_project} ha sido marcada como completada:</p>
        <p><strong>{safe_task}</strong></p>
        <p>Completada por: {safe_completed_by}</p>
        """
        return EmailService.send_email(user_emails, subject, html_content)

    @staticmethod
    def notify_project_completed(user_emails: List[str], project_name: str):
        """Send notification when project is marked as completed"""
        safe_name = escape(project_name)
        subject = f"Proyecto completado: {safe_name}"
        html_content = f"""
        <h2>Notificación de Proyecto Completado</h2>
        <p>El siguiente proyecto ha sido marcado como completado:</p>
        <p><strong>{safe_name}</strong></p>
        <p>¡Felicidades a todos los miembros del equipo!</p>
        """
        return EmailService.send_email(user_emails, subject, html_content)

    @staticmethod
    def send_new_user_credentials(username: str, password: str) -> bool:
        """Send welcome email to new user with their credentials"""
        safe_username = escape(username)
        safe_url = escape(config.SERVER_URL)
        subject = "Bienvenido al Gestor de Proyectos - Detalles de tu Cuenta"
        html_content = f"""
        <h2>Bienvenido al Gestor de Proyectos</h2>
        <p>Tu cuenta ha sido creada en el sistema de Gestión de Proyectos.</p>
        <p>Tus credenciales de acceso son:</p>
        <ul>
            <li><strong>Usuario:</strong> {safe_username}</li>
            <li><strong>Contraseña:</strong> (enviada de forma segura)</li>
        </ul>
        <p>Conéctate a la VPN y accede al sistema haciendo clic <a href="{safe_url}/login">aquí</a>.</p>
        <p>Por favor, cambia tu contraseña después de tu primer inicio de sesión.</p>
        <p>Saludos cordiales,<br>Equipo de Gestión de Proyectos</p>
        """
        return EmailService.send_email([username], subject, html_content)

    @staticmethod
    def notify_project_reopened(emails: List[str], project_name: str):
        safe_name = escape(project_name)
        subject = f"El proyecto {safe_name} ha sido reabierto"
        content = f"""
        <h2>Proyecto Reabierto</h2>
        <p>Se han añadido nuevas tareas y el proyecto <strong>{safe_name}</strong> ha sido reabierto.</p>
        <p>Por favor, revisa el estado del proyecto y las nuevas asignaciones.</p>
        """
        EmailService.send_email(emails, subject, content)
