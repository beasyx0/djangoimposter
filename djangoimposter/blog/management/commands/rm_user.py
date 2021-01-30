from django.contrib.auth import get_user_model
User = get_user_model()
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Delete one or many users'

    def add_arguments(self, parser):
        parser.add_argument('user_id', nargs='+', type=int, help='Users IDs')
    def handle(self, *args, **kwargs):
        users_ids = kwargs['user_id']
        for user_id in users_ids:
            try:
                user = User.objects.get(pk=user_id)
                user.delete()
                self.stdout.write(f'User "{user.username} ({user_id})" deleted with success!')
            except User.DoesNotExist:
                self.stdout.write(f'User with id {user_id} does not exist.')

# usage:
# docker-compose -f local.yml run --rm django python manage.py delete_user 6