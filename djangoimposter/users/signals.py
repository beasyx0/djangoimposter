from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver


@receiver(user_logged_in)
def post_login(sender, user, request, **kwargs):
    print(f'user {user.username} logged in')


@receiver(user_logged_out)
def post_logout(sender, user, request, **kwargs):
	print(f'User: {user} logged out')


@receiver(user_login_failed)
def login_failed(sender, credentials, request, **kwargs):
    print(f'Credentials: {credentials}')