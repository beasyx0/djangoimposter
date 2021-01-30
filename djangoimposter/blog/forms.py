from django import forms
from tinymce import TinyMCE

from djangoimposter.blog.models import Post, Tag, Contact, NewsletterSignup


class TinyMCEWidget(TinyMCE):
    def use_required_attribute(self, *args):
        return False


class NewsletterSignupForm(forms.ModelForm):
    class Meta:
        model = NewsletterSignup
        fields = ('email',)


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ('name', 'email', 'phone', 'message',)


class PostForm(forms.ModelForm):
    content = forms.CharField(
        widget=TinyMCEWidget(
            attrs={'required': False, 'cols': 30, 'rows': 10}
        )
    )

    tag_str = forms.CharField(widget=forms.TextInput(
                attrs={'placeholder': 'comma seperated tag names'}), 
                label='Tags', required=False)

    class Meta:
        model = Post
        fields = ('title', 'author', 'overview', 'content', 'tag_str', 
                'previous_post', 'next_post', 'post_image', 'featured',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if instance:
            self.fields['tag_str'].initial=', '.join(x.name for x in instance.tags.all())

    def save(self, commit=True, *args, **kwargs):
        instance = super().save(commit=False, *args, **kwargs)
        tag_str = self.cleaned_data.get('tag_str')
        if commit:
            tag_qs = Tag.items.comma_to_qs(tag_str)
            if not instance.id:
                instance.save()
            instance.tags.clear()
            instance.tags.add(*tag_qs)
            instance.save()
        return instance