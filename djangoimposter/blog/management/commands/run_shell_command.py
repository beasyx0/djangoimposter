from django.core.management.base import BaseCommand
import subprocess


class Command(BaseCommand):
    def handle(self, *args, **options):
        out = subprocess.Popen(['ls', '-l', '.'], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT)
        stdout,stderr = out.communicate()
        print(stdout)
        print(stderr)

# usage:
# docker-compose -f local.yml run --rm django python manage.py run_shell_command