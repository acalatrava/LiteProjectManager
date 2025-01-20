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
        subject = f"Has sido añadido al proyecto: {project_name}"
        html_content = f"""
        <h2>Notificación de Asignación de Proyecto</h2>
        <p>Has sido añadido al proyecto: <strong>{project_name}</strong></p>
        <p>Conéctate a la VPN y haz clic <a href="{project_url}">aquí</a> para ver el proyecto.</p>
        """
        return EmailService.send_email([user_email], subject, html_content)

    @staticmethod
    def notify_task_assignment(user_email: str, task_name: str, project_name: str, task_url: str):
        """Send notification when task is assigned to user"""
        subject = f"Nueva tarea asignada: {task_name}"
        html_content = f"""
        <h2>Notificación de Asignación de Tarea</h2>
        <p>Se te ha asignado una nueva tarea en el proyecto {project_name}:</p>
        <p><strong>{task_name}</strong></p>
        <p>Haz clic <a href="{task_url}">aquí</a> para ver la tarea.</p>
        """
        return EmailService.send_email([user_email], subject, html_content)

    @staticmethod
    def notify_task_completed(user_emails: List[str], task_name: str, project_name: str, completed_by: str):
        """Send notification when task is marked as completed"""
        subject = f"Tarea completada: {task_name}"
        html_content = f"""
        <h2>Notificación de Tarea Completada</h2>
        <p>Una tarea en el proyecto {project_name} ha sido marcada como completada:</p>
        <p><strong>{task_name}</strong></p>
        <p>Completada por: {completed_by}</p>
        """
        return EmailService.send_email(user_emails, subject, html_content)

    @staticmethod
    def notify_project_completed(user_emails: List[str], project_name: str):
        """Send notification when project is marked as completed"""
        subject = f"Proyecto completado: {project_name}"
        html_content = f"""
        <h2>Notificación de Proyecto Completado</h2>
        <p>El siguiente proyecto ha sido marcado como completado:</p>
        <p><strong>{project_name}</strong></p>
        <p>¡Felicidades a todos los miembros del equipo!</p>
        """
        return EmailService.send_email(user_emails, subject, html_content)

    @staticmethod
    def send_new_user_credentials(username: str, password: str) -> bool:
        """Send welcome email to new user with their credentials"""
        subject = "Bienvenido al Gestor de Proyectos - Detalles de tu Cuenta"
        html_content = f"""
        <h2>Bienvenido al Gestor de Proyectos</h2>
        <p>Tu cuenta ha sido creada en el sistema de Gestión de Proyectos.</p>
        <p>Tus credenciales de acceso son:</p>
        <ul>
            <li><strong>Usuario:</strong> {username}</li>
            <li><strong>Contraseña:</strong> {password}</li>
        </ul>
        <p>Conéctate a la VPN y accede al sistema haciendo clic <a href="{config.SERVER_URL}/login">aquí</a>.</p>
        <p>Por favor, cambia tu contraseña después de tu primer inicio de sesión.</p>
        <p>Saludos cordiales,<br>Equipo de Gestión de Proyectos</p>
        """
        return EmailService.send_email([username], subject, html_content)

    @staticmethod
    def notify_project_reopened(emails: List[str], project_name: str):
        subject = f"El proyecto {project_name} ha sido reabierto"
        content = f"""
            Se han añadido nuevas tareas y el proyecto {project_name} ha sido reabierto.
            Por favor, revisa el estado del proyecto y las nuevas asignaciones.
        """
        EmailService.send_email(emails, subject, content)
