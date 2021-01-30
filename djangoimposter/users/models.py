from django.contrib.auth.models import AbstractUser
from django.db.models import CharField, ImageField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from djangoimposter.blog.blog_utils import make_thumbnail


class User(AbstractUser):
    """Default user for djangoImposter."""
    #: First and last name do not cover name patterns around the globe
    name = CharField(_("Full Name"), blank=True, max_length=255)

    def get_absolute_url(self):
        """Get url for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"email": self.email})

