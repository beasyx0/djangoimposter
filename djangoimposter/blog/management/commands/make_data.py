import logging
logger = logging.getLogger(__name__)
from django.core.management.base import BaseCommand, CommandError

from djangoimposter.blog.builder import *


class Command(BaseCommand):

	help = "Command to create data"

	def add_arguments(self, parser):
		parser.add_argument('command', type=str, help='What type of command to run')
		parser.add_argument('total', type=int, help='Amount of objects to create')

	def handle(self, *args, **options):

		command = options['command']
		total = options['total']

		if command == 'make_users':
			make_users()
		if command == 'make_tags':
			make_tags()
		if command == 'make_posts':
			make_posts(total)
		if command == 'add_tags_to_posts':
			add_tags_to_posts()
		if command == 'make_postviews':
			make_postviews(total)
		if command == 'make_all_data':
			make_all_data(total)

		self.stdout.write(f'{command} complete, created {total} objects')


# usage
# docker-compose -f local.yml run --rm django python manage.py make_data make_posts 10