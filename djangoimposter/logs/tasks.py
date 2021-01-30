import logging
logger = logging.getLogger(__name__)
from datetime import datetime, timedelta

from django.conf import settings
from django.core.mail import EmailMessage

from config import celery_app
from config.celery_app import app, BaseTaskWithRetry


@celery_app.task(bind=True, base=BaseTaskWithRetry)
def send_logs(self):
    logger.info('Sending logs.')
    try:
        subject = settings.EMAIL_SUBJECT_PREFIX + 'Daily Logs'
        content = "Attached is the logs for DjangoImposter"
        email = EmailMessage(subject, content,
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.ADMINS])
        email.attach_file('djangoimposter/logs/debug.log')
        email.send()
        logger.info(f'Daily logs sent')
    except Exception as e:
        logger.exception(e)