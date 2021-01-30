from django.db.models import signals
from django.dispatch import receiver
from django.db import transaction
from django.contrib.postgres.search import SearchVector

from djangoimposter.blog.models import Post, Contact, NewsletterSignup
from djangoimposter.blog.tasks import new_contact_notification, new_newslettersignup_welcome_email

# config = english on vectors?
@receiver(signals.post_save, sender=Post)
def update_search_vectors(sender, instance, created, **kwargs):
	search_vectors = SearchVector('title', weight='A') + SearchVector('overview', weight='B') + SearchVector('content', weight='C')
	if created:
		instance.search_vector = search_vectors
		instance.save()


# probably don't need transaction on commit, its a post save signal so its already saved duh
@receiver(signals.post_save, sender=Contact)
def new_contact(sender, instance, created, **kwargs):
	if created:
		transaction.on_commit(lambda: new_contact_notification.delay(instance.id))


@receiver(signals.post_save, sender=NewsletterSignup)
def new_newslettersignup(sender, instance, created, **kwargs):
	if created:
		transaction.on_commit(lambda: new_newslettersignup_welcome_email.delay(instance.id))
