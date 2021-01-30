from django.contrib.auth import get_user_model
User = get_user_model()

from djangoimposter.blog.models import Post
from djangoimposter.blog.forms import NewsletterSignupForm, ContactForm, PostForm


def extra_blog_context(request):
	return {
		'canonical_path': request.build_absolute_uri(request.path),
		'post_form': PostForm(),
		'form_contact': ContactForm(),
		'form_newsletter': NewsletterSignupForm(),
		'featured': Post.objects.filter(featured=True)[:3],
	}