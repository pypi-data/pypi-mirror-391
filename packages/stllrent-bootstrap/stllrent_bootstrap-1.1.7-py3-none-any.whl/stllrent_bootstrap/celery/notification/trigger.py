from stllrent_bootstrap.celery.notification.email import send_mail
from celery.exceptions import Retry
from config.celery_settings import celery_settings
from config.base_settings import settings
from smtplib import SMTPSenderRefused

import logging

log = logging.getLogger(__name__)

def on_retry(task, exc: Retry):

    if not celery_settings.NOTIFICATION_EMAIL_RELAY or not celery_settings.NOTIFICATION_EMAIL_FROM:
        log.warning("Ignoring E-mail notification. Setup [NOTIFICATION_EMAIL_RELAY, NOTIFICATION_EMAIL_FROM] variables to activate this functionality.")
        return

    # O atributo 'when' da exceção Retry contém o delay em segundos (se 'countdown' foi usado) ou um datetime (se 'eta' foi usado).
    retry_delay = exc.when
    # O número de tentativas já executadas.
    current_retries = task.request.retries
    # O número máximo de tentativas configurado na task.
    max_retries = task.max_retries

    msg_body = f"""
    Uma falha ocorreu ao processar a tarefa: {task.name}
    
    Detalhes: {exc!r}

    - Task ID: {task.request.id}
    - Tentativa de reprocessamento: {current_retries + 1} de {max_retries}.
    - A próxima tentativa (se permitida) ocorrerá em aproximadamente {retry_delay} segundos.
    - Ambiente: {settings.APP_ENVIRONMENT}

    """

    msg_to = task.notify_on_retry
    msg_from = celery_settings.NOTIFICATION_EMAIL_FROM
    msg_subject = "Falha ao processar tarefa"
    try:
        log.debug(f"Sending E-mail notification for retry task {task.request.id}")
        send_mail(body=msg_body, subject=msg_subject, mail_to=msg_to, mail_from=msg_from)
        log.debug(f"E-mail sent to {msg_to}")
    except SMTPSenderRefused as smtp_e:
        log.error(f"[BOOTSTRAP_CELERY_NOTIFICATION_ERROR] {smtp_e!r}")
        raise
    except Exception as e:
        log.error(f"[BOOTSTRAP_CELERY_NOTIFICATION_UNEXPECTED_ERROR] {e!r}")
        raise
