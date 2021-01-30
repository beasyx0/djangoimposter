from django.apps import AppConfig


class BlogConfig(AppConfig):
    name = 'djangoimposter.blog'
    def ready(self):
        import djangoimposter.blog.signals
