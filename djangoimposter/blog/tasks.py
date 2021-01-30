import logging
logger = logging.getLogger(__name__)
from datetime import datetime, timedelta
import pytz

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

import celery
from config import celery_app
from config.celery_app import app, BaseTaskWithRetry
from celery.decorators import periodic_task

from djangoimposter.blog.models import Post, Contact, NewsletterSignup
from djangoimposter.blog.builder import make_all_data


@celery_app.task(bind=True, base=BaseTaskWithRetry)
def new_contact_notification(self, id):
    contact = get_object_or_404(Contact, id=id)
    plain_template = 'email-templates/new-contact-plain-template.txt'
    html_template = 'email-templates/new-contact-template.html'
    subject = settings.EMAIL_SUBJECT_PREFIX + ' New Contact'
    data = {'name': contact.name, 'email': contact.email,
            'phone': contact.phone, 'message': contact.message,}
    plain_message = render_to_string(plain_template, data)
    html_message = render_to_string(html_template, data)
    msg = EmailMultiAlternatives(subject, plain_message,
            settings.DEFAULT_FROM_EMAIL, [settings.ADMINS,])
    msg.attach_alternative(html_message, "text/html")
    try:
        msg.send(fail_silently=False)
        logger.info(f'New contact notification sent for {contact.email}')
    except Exception as e:
        logger.error(e)


@celery_app.task(bind=True, base=BaseTaskWithRetry)
def new_newslettersignup_welcome_email(self, id):
    newsletter = get_object_or_404(NewsletterSignup, id=id)
    plain_template = 'email-templates/new-newsletter-signup-plain-template.txt'
    html_template = 'email-templates/new-newsletter-signup-template.html'
    subject = settings.EMAIL_SUBJECT_PREFIX + ' Thank you for signing up for our newsletter!'
    data = {'email': newsletter.email, 
            'slug': newsletter.slug}
    plain_message = render_to_string(plain_template, data)
    html_message = render_to_string(html_template, data)
    msg = EmailMultiAlternatives(subject, plain_message,
            settings.DEFAULT_FROM_EMAIL, [newsletter.email,])
    msg.attach_alternative(html_message, "text/html")
    try:
        msg.send(fail_silently=False)
        logger.info(f'New newsletter signup welcome email sent {newsletter.email}')
    except Exception as e:
        logger.error(e)


@celery_app.task(bind=True, base=BaseTaskWithRetry)
def weekly_newsletter(self):
    now = datetime.now()
    timezone = pytz.timezone('America/New_York')
    now_aware = timezone.localize(now)
    past_week = now_aware - timedelta(days=7)
    posts = Post.objects.filter(date__gte=past_week)
    signups = NewsletterSignup.objects.filter(opted_in=True)
    for signup in signups:
            new_posts = []
            for post in posts:
                if post not in signup.posts.all():
                    new_posts.append(post)
                    post.newsletters.add(signup)
            if new_posts:
                plain_template = 'email-templates/weekly-newsletter-plain-template.txt'
                html_template = 'email-templates/weekly-newsletter-template.html'
                subject = settings.EMAIL_SUBJECT_PREFIX + ' Here\'s the latest posts from DjangoImposter!'
                plain_message = render_to_string(plain_template, {'posts': new_posts,})
                html_message = render_to_string(html_template, {'posts': new_posts,})
                msg = EmailMultiAlternatives(subject, plain_message,
                                            settings.DEFAULT_FROM_EMAIL, 
                                            [signup.email])
                msg.attach_alternative(html_message, "text/html")
                try:
                    msg.send(fail_silently=False)
                    logger.info(f'Newsletter email sent to {signup.email}')
                except Exception as e:
                    logger.error(e)


@celery_app.task(bind=True, base=BaseTaskWithRetry)
def admin_send_posts_to_newslettersignups(self, queryset):
    signups = NewsletterSignup.objects.filter(opted_in=True).prefetch_related('posts')
    plain_template = 'email-templates/admin-send-to-newslettersignups-plain-template.txt'
    html_template = 'email-templates/admin-send-to-newslettersignups-template.html'
    subject = settings.EMAIL_SUBJECT_PREFIX + ' Some choice posts from DjangoImposter'
    for signup in signups:
        posts = [post for post in queryset if post not in signup.posts.all()]
        if posts:
            plain_message = render_to_string(plain_template, {'posts': posts,})
            html_message = render_to_string(html_template, {'posts': posts,})
            msg = EmailMultiAlternatives(subject, plain_message, settings.DEFAULT_FROM_EMAIL, [signup.email])
            msg.attach_alternative(html_message, "text/html")
            try:
                msg.send(fail_silently=False)
                logger.info(f'Newsletter email sent to {signup.email}')
                for post in posts:
                    post.newsletters.add(signup)
            except Exception as e:
                logger.error(e)


# @celery_app.task(bind=True, base=BaseTaskWithRetry)
# def make_all_data_on_compose_up(self):
#     '''
#     Build data on bringing up the site, if data exists doesnt run.
#     Tries every minute
#     '''
#     if Post.objects.all().exists():
#         pass
#     else:
#         make_all_data()

# https://testdriven.io/blog/retrying-failed-celery-tasks/
# from celery import shared_task
# import random
# @shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=5, retry_jitter=True, retry_kwargs={'max_retries': 5})
# def task_process_notification(self):
#     if not random.choice([0, 1]):
#         # mimic random error
#         raise Exception()

#     requests.post('https://httpbin.org/delay/5')

# class BaseTaskWithRetry(celery.Task):
#     autoretry_for = (Exception, KeyError)
#     retry_kwargs = {'max_retries': 5}
#     retry_backoff = True


# @shared_task(bind=True, base=BaseTaskWithRetry)
# def task_process_notification(self):
#     raise Exception()

# https://coderbook.com/@marcus/how-to-automatically-retry-failed-tasks-with-celery/
# @app.task(name="foo.task", bind=True, max_retries=3)
# def foo_task(self):
#     try:
#         execute_something()
#     except Exception as ex:
#         logger.exception(ex)
#         self.retry(countdown=3**self.request.retries)