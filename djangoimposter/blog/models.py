import uuid
from PIL import Image

from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import slugify
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.search import SearchVector
from django.contrib.postgres.indexes import GinIndex
from django.contrib.auth import get_user_model
User = get_user_model()

from tinymce import HTMLField
from phone_field import PhoneField

from djangoimposter.blog.managers import PostManager, TagManager
from djangoimposter.blog.blog_utils import make_thumbnail


class TimeStamped(models.Model):
    date = models.DateTimeField(editable=False, null=True)
    modified = models.DateTimeField(editable=False, null=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.id:
            self.date = timezone.now()
        self.modified = timezone.now()
        return super(TimeStamped, self).save(*args, **kwargs)


class Tag(models.Model):
    name = models.CharField(max_length=25, unique=True)

    objects = models.Manager()
    items = TagManager()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Tags'

    def get_absolute_url(self):
        return reverse('blog:tag-detail', kwargs={
            'name': self.name
        })


class PostView(TimeStamped):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_post_views')
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='post_views')

    def __str__(self):
        return self.user.username

    class Meta:
        ordering = ['-date']
        verbose_name_plural = 'Post Views'


class Post(TimeStamped):
    title = models.CharField(max_length=255)
    slug = models.SlugField(editable=False, max_length=255, unique=True)
    overview = models.CharField(max_length=500, default=" ")
    content = HTMLField()
    author = models.CharField(max_length=255)
    post_image = models.ImageField(upload_to='post_pics', default='default-img.jpg')
    tags = models.ManyToManyField(Tag, related_name='posts', blank=True)
    featured = models.BooleanField(default=False)
    bookmarked = models.ManyToManyField(User, related_name='bookmarked_posts', blank=True)
    previous_post = models.ForeignKey(
        'self', related_name='previous', on_delete=models.SET_NULL, blank=True, null=True)
    next_post = models.ForeignKey(
        'self', related_name='next', on_delete=models.SET_NULL, blank=True, null=True)
    newsletters = models.ManyToManyField(
        'NewsletterSignup', related_name='posts', blank=True)
    search_vector = SearchVectorField(null=True, editable=False)
    
    objects = models.Manager()
    items = PostManager()

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-date']
        verbose_name_plural = 'Posts'
        indexes = [GinIndex(fields=['search_vector'])]

    def get_absolute_url(self):
        return reverse('blog:post-detail', kwargs={
            'slug': self.slug
        })

    @property
    def view_count(self):
        return PostView.objects.filter(post=self).count()

    @property
    def get_estimated_reading_time(self):
        string=self.content.strip()
        count=1
        for i in string:
            if i==" ":
                count+=1
        count = int(count / 300)
        if count < 1:
            return 1
        else:
            return count

    def _get_unique_slug(self):
        slug = slugify(self.title)
        num = str(uuid.uuid4().hex)
        unique_slug = f'{slug}-{num}'
        qs_exists = Post.objects.filter(slug=unique_slug)
        if qs_exists:
            _get_unique_slug(self)
        return unique_slug

    def bookmark(self, id):
        user = get_object_or_404(User, id=id)
        if user in self.bookmarked.all():
            self.bookmarked.remove(user)
            return False
        else:
            self.bookmarked.add(user)
            return True

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = self._get_unique_slug()
            self.post_image = make_thumbnail(self.post_image, size=(500, 500))
        return super(Post, self).save(*args, **kwargs)


from django_comments_xtd.moderation import moderator, XtdCommentModerator
class PostCommentModerator(XtdCommentModerator):
    removal_suggestion_notification = True

moderator.register(Post, PostCommentModerator)


class Contact(TimeStamped):
    name = models.CharField(max_length=55)
    email = models.EmailField()
    phone = PhoneField(blank=True)
    message = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-date']
        verbose_name_plural = 'Contacts'


class NewsletterSignup(TimeStamped):
    email = models.EmailField(unique=True)
    opted_in = models.BooleanField(default=False, editable=False)
    slug = models.SlugField(unique=True, editable=False, null=True, blank=True)

    def __str__(self):
        return self.email

    class Meta:
        ordering = ['-date']
        verbose_name_plural = 'Newsletter Signups'

    def opt_in_out(self):
        if self.opted_in is True:
            self.opted_in = False
        else:
            self.opted_in = True

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = uuid.uuid4().hex
        return super(NewsletterSignup, self).save(*args, **kwargs)
