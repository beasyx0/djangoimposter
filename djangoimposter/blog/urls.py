from django.urls import path
from djangoimposter.blog.views import (
    home, search, create_post, update_post, delete_post_confirm, delete_post, post_detail,
    random_post, tag_detail, subscribed, newsletter_opt_in_out, newsletter_confirm, 
    contact, bookmarked)

app_name = "blog"
urlpatterns = [
    path("", home, name="home"),
    path("search/", search, name="search"),
    path("posts/create-post/", create_post, name="create-post"),
    path("posts/update-post/<slug>/", update_post, name="update-post"),
    path("posts/delete-post-confirm/<slug>/", delete_post_confirm, name="delete-post-confirm"),
    path("posts/delete-post/<slug>/", delete_post, name="delete-post"),
    path("posts/<slug>/", post_detail, name="post-detail"),
    path("random-post/", random_post, name="random-post"),
    path("tags/<name>/", tag_detail, name="tag-detail"),
    path("subscribed/", subscribed, name="subscribed"),
    path("newsletter/opt-in-out/<slug>/", newsletter_opt_in_out, name="newsletter-opt-in-out"),
    path("newsletter/confirm/<slug>/", newsletter_confirm),
    path("contact/", contact, name="contact"),
    path("bookmarked/", bookmarked, name="bookmarked"),
    # path("create-post-test/", create_post_test, name="create-post-test"),
]
