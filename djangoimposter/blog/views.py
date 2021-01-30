import logging
logger = logging.getLogger(__name__)
import random
import json

from django.shortcuts import render, reverse, redirect, get_object_or_404
from django.db.models import Q, Count, F
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.contrib.auth import get_user_model
User = get_user_model()

from djangoimposter.blog.decorators import superuser_only, ajax_required
from djangoimposter.blog.models import Tag, PostView, Post, Contact, NewsletterSignup
from djangoimposter.blog.forms import ContactForm, NewsletterSignupForm, PostForm


def pag_posts(request, posts):
    page = request.GET.get('page', 1)
    paginator = Paginator(posts, 6)
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return posts


def search(request):
    title = 'Search Results'
    query = request.GET.get('q')
    logger.info(f'Someone searched for {query}')
    posts = Post.items.search(query)
    posts = pag_posts(request, posts)
    context = {
        'title': title,
        'posts': posts,
        'query': query,
    }
    return render(request, 'pages/search-results.html', context)


def home(request):
    title = 'Home'
    posts = Post.objects.prefetch_related('tags')\
        .prefetch_related('bookmarked')\
        .annotate(viewcount=Count(F('post_views')))
    posts = pag_posts(request, posts)
    context = {
        'title': title,
        'posts': posts,
    }
    return render(request, 'pages/home.html', context)


@superuser_only
def create_post(request):
    title = 'Create Post'
    if request.method == 'POST':
        post_form = PostForm(request.POST, request.FILES)
        if post_form.is_valid():
            new_post = post_form.save()
            return redirect(new_post.get_absolute_url())
    context = {
        'title': title,
    }
    return render(request, 'pages/create-post.html', context)


# def create_post_test(request):
#     if request.method == 'POST' and request.is_ajax():
#         title = request.POST.get('title')
#         author = request.POST.get('author')
#         overview = request.POST.get('overview')
#         content = request.POST.get('content')
#         tags = request.POST.get('tags')
#         previous_post_id = request.POST.get('previous_post_id')
#         previous_post = get_object_or_404(Post, id=previous_post_id)
#         next_post_id = request.POST.get('next_post_id')
#         next_post = get_object_or_404(Post, id=next_post_id)
#         is_image = request.FILES.get('image')
#         if is_image is not None:
#             image = is_image
#         else:
#             image = 'default-img.jpg'
#         is_featured = request.POST.get('featured')
#         if is_featured == 'on':
#             featured = True
#         else:
#             featured = False
#         logger.info(featured)
#         post = Post.objects.create(
#                 title=title,
#                 author=author,
#                 overview=overview,
#                 content=content,
#                 previous_post=previous_post,
#                 next_post=next_post,
#                 post_image=image,
#                 featured=featured,
#                 )
#         tag_qs = Tag.items.comma_to_qs(tags)
#         post.tags.clear()
#         post.tags.add(*tag_qs)
#         post.save()
#         return JsonResponse({'post_slug': post.slug,}, status=200)
@superuser_only
def update_post(request, slug):
    title = 'Update Post'
    if request.user.is_staff:
        post = get_object_or_404(Post, slug=slug)
        post_form = PostForm(instance=post)
        if request.method == 'POST':
            post_form = PostForm(request.POST, request.FILES, instance=post)
            if post_form.is_valid():
                post_form.save()
                return redirect(post.get_absolute_url())
        context = {
            'title': title,
            'post_form': post_form,
        }
        return render(request, 'pages/update-post.html', context)
    else:
        messages.error(request, 'You can\'t do that')
        return redirect('blog:home')


@superuser_only
def delete_post_confirm(request, slug):
    title = 'Delete Post Confirm'
    post = get_object_or_404(Post, slug=slug)
    context = {
        'title': title,
        'post': post,
    }
    return render(request, 'pages/delete-post-confirm.html', context)


@superuser_only
def delete_post(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Successfully deleted post')
        return redirect('blog:home')
    else:
        return redirect('blog:home')


def post_detail(request, slug):
    title = 'Post Detail'
    post = get_object_or_404(\
        Post.objects.prefetch_related('tags')\
        .prefetch_related('bookmarked')\
        .annotate(viewcount=Count(F('post_views'))), slug=slug)
    if request.user.is_authenticated:
        PostView.objects.create(user=request.user, post=post)
    else:
        user = get_object_or_404(User, id=1)
        PostView.objects.create(user=user, post=post)
    context = {
        'title': title,
        'post': post,
    }
    return render(request, 'pages/post-detail.html', context)


def random_post(request):
    logger.info('Someone wanted a random post')
    title = 'Random Post'
    posts = Post.objects.all()
    if posts:
        rando = random.randint(0, (len(posts) - 1))
        post = posts[rando]
        logger.info(f'Displaying random post: {post.title}')
        context = {
            'title': title,
            'post': post,
        }
        return render(request, 'pages/post-detail.html', context)
    else:
        return render(request, 'pages/post-detail.html', context)
        # return render(request, 'pages/random-post.html')


def tag_detail(request, name):
    title = 'Tag Detail'
    tag = get_object_or_404(Tag, name=name)
    posts = Post.objects.filter(tags=tag)\
        .prefetch_related('tags')\
        .prefetch_related('bookmarked')\
        .annotate(viewcount=Count(F('post_views')))
    posts = pag_posts(request, posts)
    context = {
        'title': title,
        'tag': tag,
        'posts': posts,
    }
    return render(request, 'pages/tag-detail.html', context)


@ajax_required
def subscribed(request):
    data = None
    status = 400
    if request.method == 'POST' and request.is_ajax():
        honey = request.POST.get('phone', None)
        if honey != '':
            data = 'ohnohoney'
            status = 200
        else:
            form = NewsletterSignupForm(request.POST)
            if form.is_valid():
                form.save()
                status = 200
    return JsonResponse({"data": data}, status=status)


def newsletter_confirm(request, slug):
    title = 'Confirm Newsletter'
    newsletter = get_object_or_404(NewsletterSignup, slug=slug)
    opted_in = newsletter.opted_in
    context = {
        'title': title,
        'newsletter': newsletter,
        'opted_in': opted_in,
    }
    return render(request, 'pages/newsletter-confirm.html', context)


def newsletter_opt_in_out(request, slug):
    newsletter = get_object_or_404(NewsletterSignup, slug=slug)
    if request.method == 'POST':
        if newsletter.opted_in:
            newsletter.opt_in_out()
            newsletter.save()
            logger.info(f'{newsletter.email} successfully opted out of the newsletter')
            messages.success(request, f'{newsletter.email} has successfully unsubscribed from the newsletter.')
        else:
            newsletter.opt_in_out()
            newsletter.save()
            logger.info(f'{newsletter.email} successfully opted into the newsletter')
            messages.success(request, f'{newsletter.email} has successfully subscribed to the newsletter.')
        return redirect('blog:home')
    else:
        return redirect('blog:home')


def contact(request):
    if request.method == 'POST':
        form_contact = ContactForm(request.POST or None)
        if form_contact.is_valid():
            name = form_contact.instance.name
            form_contact.save()
            logger.info(f'{name} successfully contacted you')
            # form_newsletter = NewsletterSignupForm()
            # form_contact = ContactForm()
            messages.success(request, f'Message sent, thank you {name}!')
            context = {
                # 'form_newsletter': form_newsletter,
                # 'form_contact': form_contact,

            }
            return render(request, 'pages/contact-successful.html', context)
    else:
        return redirect('blog:home')


@ajax_required
def bookmarked(request):
    bookmarked = None
    post_id = None
    status = 400
    if request.method == 'POST' and request.is_ajax():
        user = request.user
        post_id = request.POST.get('post_id', None)
        post = get_object_or_404(Post, slug=post_id)
        if user.is_authenticated:
            bookmarked = post.bookmark(user.id)
            status = 200
    return JsonResponse({"bookmarked": bookmarked, "post_id": post_id}, status=status)
