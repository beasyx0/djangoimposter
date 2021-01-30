from django.db.models import Count, F
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, RedirectView, UpdateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
User = get_user_model()

from djangoimposter.blog.models import Post
from djangoimposter.blog.views import pag_posts
from djangoimposter.users.forms import UserUpdateForm


@login_required
def user_detail_view(request, email):
    user = request.user
    posts = Post.objects.prefetch_related('tags')\
                .prefetch_related('bookmarked')\
                .annotate(viewcount=Count(F('post_views')))\
                .filter(bookmarked=user)
    posts = pag_posts(request, posts)
    context = {
        'user': user,
        'posts': posts,
    }
    return render(request, 'users/user_detail.html', context)


@login_required
def user_update_view(request):
    user = request.user
    form = UserUpdateForm(request.POST or None, instance=user)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            email = user.email
            messages.success(request, 'User updated successfully')
            return redirect('users:redirect')
    context = {
        'user': user,
        'form': form,
    }
    return render(request, 'users/user_form.html', context)

# class UserUpdateView(LoginRequiredMixin, UpdateView):

#     model = User
#     fields = ["name"]

#     def get_success_url(self):
#         return reverse("users:detail", kwargs={"email": self.request.user.email})

#     def get_object(self):
#         return User.objects.get(email=self.request.user.email)

#     def form_valid(self, form):
#         messages.add_message(
#             self.request, messages.INFO, _("Infos successfully updated")
#         )
#         return super().form_valid(form)


# user_update_view = UserUpdateView.as_view()


class UserRedirectView(LoginRequiredMixin, RedirectView):

    permanent = False

    def get_redirect_url(self):
        return reverse("users:detail", kwargs={"email": self.request.user.email})


user_redirect_view = UserRedirectView.as_view()


from allauth.account.views import SignupView


class AccountSignupView(SignupView):
    template_name = "account/signup.html"

account_signup_view = AccountSignupView.as_view()
