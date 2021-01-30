from io import BytesIO
from django.core.files import File
from PIL import Image


def make_thumbnail(image, size=(100, 100)):
    """Makes thumbnails of given size from given image"""
    im = Image.open(image)
    im = im.convert('RGB') # convert mode
    im.thumbnail(size) # resize image
    thumb_io = BytesIO() # create a BytesIO object
    im.save(thumb_io, 'JPEG', quality=85) # save image to BytesIO object
    resized_image = File(thumb_io, name=image.name) # create a django friendly File object
    return resized_image



from avatar.templatetags.avatar_tags import avatar_url
from django_comments_xtd.utils import get_user_avatar


def get_avatar_url(comment):
    ret = None
    if comment.user is not None:
        try:
            return avatar_url(comment.user)
        except Exception as exc:
            pass
    return get_user_avatar(comment)