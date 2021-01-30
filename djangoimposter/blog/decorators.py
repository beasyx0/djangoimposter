import logging
logger = logging.getLogger(__name__)
import functools

from django.shortcuts import reverse
from django.utils.html import format_html
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseBadRequest


def admin_change_url(obj):
    app_label = obj._meta.app_label
    model_name = obj._meta.model.__name__.lower()
    return reverse('admin:{}_{}_change'.format(
            app_label, model_name
            ), args=(obj.pk,))


def admin_link(attr, short_description, empty_description="-"):
    """Decorator used for rendering a link to a related model in
    the admin detail page.

    attr (str):
        Name of the related field.
    short_description (str):
        Name if the field.
    empty_description (str):
        Value to display if the related field is None.

    The wrapped method receives the related object and should
    return the link text.

    Usage:
        @admin_link('credit_card', _('Credit Card'))
        def credit_card_link(self, credit_card):
            return credit_card.name
    """
    def wrap(func):
        def field_func(self, obj):
            related_obj = getattr(obj, attr)
            if related_obj is None:
                return empty_description
            url = admin_change_url(related_obj)
            return format_html('<a href="{}">{}</a>', url, func(self, related_obj))
        field_func.short_description = short_description
        field_func.allow_tags = True
        return field_func
    return wrap
# PostAdmin
# @admin_link('next_post', _('next post'))
    # def next_link(self, next_post):
    #     return next_post


def admin_changelist_url(model):
    app_label = model._meta.app_label
    model_name = model.__name__.lower()
    return reverse('admin:{}_{}_changelist'.format(app_label, model_name))

def admin_changelist_link(
    attr,
    short_description,
    empty_description='-',
    query_string=None
):
    """Decorator used for rendering a link to the list display of
    a related model in the admin detail page.

    attr (str):
        Name of the related field.
    short_description (str):
        Field display name.
    empty_description (str):
        Value to display if the related field is None.
    query_string (function):
        Optional callback for adding a query string to the link.
        Receives the object and should return a query string.

    The wrapped method receives the related object and
    should return the link text.

    Usage:

        @admin_changelist_link('credit_card', _('Credit Card'))
        def credit_card_link(self, credit_card):
            return credit_card.name
    """
    def wrap(func):
        def field_func(self, obj):
            related_obj = getattr(obj, attr)
            if related_obj is None:
                return empty_description
            url = admin_changelist_url(related_obj.model)
            if query_string:
                url += '?' + query_string(obj)
            return format_html('<a href="{}">{}</a>', url, func(self, related_obj))
        field_func.short_description = short_description
        field_func.allow_tags = True
        return field_func
    return wrap


def superuser_only(function):
    """Limit view to superusers only."""
    @functools.wraps(function)
    def _inner(request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied       
        return function(request, *args, **kwargs)
    return _inner


def ajax_required(function):
   """
   AJAX request required decorator
   use it in your views:

   @ajax_required
   def my_view(request):
       ....
   """   
   @functools.wraps(function)
   def wrap(request, *args, **kwargs):
       if not request.is_ajax():
           return HttpResponseBadRequest('Something went wrong')
       return function(request, *args, **kwargs)

   return wrap