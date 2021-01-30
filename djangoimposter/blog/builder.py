# Python imports
import logging
logger = logging.getLogger(__name__)
import random
import uuid
# Django imports
from django.contrib.postgres.search import SearchVector
from django.utils import timezone
from django.template.defaultfilters import slugify
from django.contrib.auth import get_user_model
User = get_user_model()
# Third party imports
import lorem
# My imports
from djangoimposter.blog.models import Post, PostView, Tag


def make_users(usr_qty):
    logger.info('Making users')
    users = []
    for i in range(usr_qty):
        name = lorem.get_word(2)
        email = lorem.get_word(2)
        email = email.split(' ')
        email = '@'.join(email)
        email = email + '.com'
        pasw = str(uuid.uuid4())
        user = User(username=name, 
                    email=email, 
                    password=pasw)
        users.append(user)
    User.objects.bulk_create(users)
    logger.info('Making users complete')


def make_tags():
    '''
    Creates a limited # of tags. Roughly 50
    '''
    logger.info('Making tags')
    new_tags = []
    paragraph = lorem.get_paragraph()
    punctuation = '''!()-[]{};:'"\,<>./?@#$%^&*_~''' # punctuation to check against
    no_punctuation_paragraph = ""
    for char in paragraph:          # loop over every character and if not in punctuation string\
        if char not in punctuation: # then add it to no punctuation string, includes whitespace!
            no_punctuation_paragraph = \
                no_punctuation_paragraph + char
    words = no_punctuation_paragraph.split(' ') # split into list of words
    words = set(words) # make unique
    words = list(words) # convert back to list
    for i in words:
        new_tags.append(Tag(name=i))
    Tag.objects.bulk_create(new_tags) # profit
    logger.info('Making tags complete')


def make_posts(post_qty):
    '''
    post_qty: int
    returns: Created model instances
    https://docs.djangoproject.com/en/3.1/ref/models/querysets/#bulk-create
    Using bulk_create. Had to include slug, created and modified to make work.
    bulk_create doesn't call models save method or call pre and post save signals. Duh!
    '''
    logger.info('Making posts')
    new_posts = [] # container for new posts
    for i in range(post_qty):
        title = lorem.get_sentence(1)
        slug = slugify(title)
        num = str(uuid.uuid4().hex)
        unique_slug = f'{slug}-{num}'
        overview = lorem.get_sentence(3)
        created = timezone.now()
        modified = timezone.now()
        content = lorem.get_paragraph(10)
        author = lorem.get_word()
        featured = random.getrandbits(1)
        new_post = Post(title=title, 
                    slug=unique_slug,
                    overview=overview,
                    date=created,
                    modified=modified,
                    content=content, 
                    author=author,
                    featured=featured)
        new_posts.append(new_post) # add new posts to container
    Post.objects.bulk_create(new_posts) # profit
    search_vectors = SearchVector('title', weight='A') + \
                    SearchVector('overview', weight='B') + \
                    SearchVector('content', weight='C')
    Post.objects.update(search_vector=search_vectors)
    logger.info('Making posts complete')
    

def add_tags_to_posts():
    '''
    This can be improved
    '''
    logger.info('Adding tags to posts')
    posts = Post.objects.all()
    users = User.objects.all()
    tags = Tag.objects.all()
    for post in posts:
        post.tags.set(tags)
        post.previous_post = random.choice(posts)
        post.next_post = random.choice(posts)
        post.bookmarked.add(random.choice(users))
        post.save()
    logger.info('Adding tags to posts complete')


def make_postviews(post_view_qty):
    '''
    post_view_qty: int
    returns: Created model instances
    '''
    logger.info('Making postviews')
    posts = Post.objects.all()
    users = User.objects.all()
    post_views = []
    for post in posts:
        for i in range(post_view_qty):
            user = random.choice(users)
            post_views.append(
                PostView(user=user, 
                        post=post, 
                        date=timezone.now()))
    PostView.objects.bulk_create(post_views)
    logger.info('Making postviews complete')

    
def make_all_data(usr_qty=10, post_qty=20, post_view_qty=20):
    '''
    usr_qty: int
    post_qty: int
    post_view_qty: int
    returns: Created User, Tag, Post and PostView instances
    '''
    try:
        logger.info('Making all data')
        make_users(usr_qty)
        make_tags()
        make_posts(post_qty)
        add_tags_to_posts()
        make_postviews(post_view_qty)
        logger.info('Making all data complete')
    except Exception as e:
        logger.exception(e)