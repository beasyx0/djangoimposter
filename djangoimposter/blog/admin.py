from django.contrib import admin
from django.db.models import Count, F
from django.utils.html import format_html

from djangoimposter.blog.models import Tag, PostView, Post, Contact, NewsletterSignup


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ('name',)
    search_fields = ['name',]


@admin.register(PostView)
class PostViewAdmin(admin.ModelAdmin):
    date_hierarchy = 'date'
    list_display = ('user', 'post', 'date',)
    list_filter = ('user', 'date',)
    search_fields = ['post',]


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    class Media:
        css = {
            "all": ("css/my-css.css",)
        }
    date_hierarchy = 'date'
    list_display = ('date', 'modified', 'title', 'author', \
                            'display_view_count', 'featured',)
    list_filter = ('date', 'author', 'tags', 'featured',)
    list_display_links = ('date',)
    list_editable = ('title', 'author', 'featured',)
    list_per_page = 50
    list_select_related = True
    search_fields = ['title', 'overview', 'author',]
    fieldsets = (
            (None, {
                'fields': ('date', 'modified', 'display_slug', 'display_view_count',\
                 'display_reading_time', 'title', 'overview', 'author', 'post_image', \
                 'content', 'previous_post', 'next_post', 'tags', 'featured',),
                # 'classes': ('wide', 'extrapretty'),
            }),
        )
    filter_horizontal = ['bookmarked', 'tags']
    autocomplete_fields = ['tags']
    readonly_fields = ('date', 'modified', 'display_slug', 'display_view_count',\
                         'display_reading_time',)
    actions = ['send_posts_to_newslettersignups']

    # def export_selected_objects(modeladmin, request, queryset):
    #     from django.contrib.contenttypes.models import ContentType
    #     from django.http import HttpResponseRedirect
    #     selected = queryset.values_list('pk', flat=True)
    #     ct = ContentType.objects.get_for_model(queryset.model)
    #     return HttpResponseRedirect('/export/?ct=%s&ids=%s' % (
    #         ct.pk,
    #         ','.join(str(pk) for pk in selected),
    #     ))

    def get_queryset(self, request):
        qs = super(PostAdmin, self).get_queryset(request)
        qs = qs.defer('content', 'overview',).prefetch_related('tags')\
                            .annotate(viewcount=Count(F('post_views')))
        return qs

    def changelist_view(self, request, extra_context=None):
        response = super(PostAdmin, self).changelist_view(request, extra_context)
        extra_context = {
            'tags': Tag.objects.values('name')
        }
        try:
            response.context_data.update(extra_context)
        except Exception as e:
            pass
        return response

    def display_slug(self, instance):
        return format_html(
            '<a href="https://www.djangoimposter.com/{}/">{}/</a>', \
                                            instance.slug, instance.slug)
    display_slug.short_description = "Slug"

    def display_view_count(self, instance):
        return str(instance.viewcount) + ' views'
    display_view_count.short_description = "View Count"

    def display_reading_time(self, instance):
        return str(instance.get_estimated_reading_time) + ' min'
    display_reading_time.short_description = "Reading Time"

    def send_posts_to_newslettersignups(self, request, queryset):
        from djangoimposter.blog.tasks import admin_send_posts_to_newslettersignups
        admin_send_posts_to_newslettersignups(queryset)
        self.message_user(request, 'Posts sent')


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    date_hierarchy = 'date'
    list_display = ('date', 'name', 'email', 'phone', 'message')
    list_filter = ('date',)
    search_fields = ['date', 'name', 'email', 'phone', 'messsage']


@admin.register(NewsletterSignup)
class NewsletterSignupAdmin(admin.ModelAdmin):
    date_hierarchy = 'date'
    list_display = ('date', 'email', 'opted_in')
    list_filter = ('date',)
    search_fields = ['email',]


admin.site.site_title = "DjangoImposter Admin"
admin.site.site_header = "DjangoImposter Admin"
admin.site.index_title = ""
admin.site.enable_nav_sidebar = False