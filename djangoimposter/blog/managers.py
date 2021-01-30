from django.db import models
from django.db.models import Count, F
from django.contrib.postgres.aggregates import StringAgg
from django.contrib.postgres.search import (
    SearchQuery, SearchRank, SearchVector, TrigramSimilarity,
)
# from djangoimposter.blog.blog_utils import create_or_new_tag


class PostQuerySet(models.QuerySet):

    def search(self, search_text):
        search_vectors = (
            SearchVector('title', weight='A', config='english') +
            SearchVector('overview', weight='B', config='english') +
            SearchVector(StringAgg('content', delimiter=' '), 
                                weight='C', config='english',)
        )
        search_query = SearchQuery(
            search_text, config='english'
        )
        search_rank = SearchRank(search_vectors, search_query)
        trigram_similarity = TrigramSimilarity('title', search_text)
        return self.filter(search_vector=search_query)\
                    .prefetch_related('tags')\
                    .prefetch_related('bookmarked')\
                    .annotate(rank=search_rank + trigram_similarity)\
                    .order_by('-rank')

    def featured(self):
        return self.filter(featured=True)

    def most_viewed(self):
        return self.annotate(views=Count(F('post_views'))).order_by('-views')

    def most_bookmarked(self):
        return self.annotate(num_bookmarks=Count(F('bookmarked'))).order_by('-num_bookmarks')



class PostManager(models.Manager):

    def get_queryset(self):
        return PostQuerySet(self.model, using=self._db)

    def search(self, search_text):
        return self.get_queryset().search(search_text)

    def featured(self):
        return self.get_queryset().featured()

    def most_viewed(self):
        return self.get_queryset().most_viewed()

    def most_bookmarked(self):
        return self.get_queryset().most_bookmarked()


class TagManager(models.Manager):

    def create_or_new(self, name):
        name = name.strip()
        qs = self.get_queryset().filter(name__iexact=name)
        if qs.exists():
            return qs.first(), False
        return self.get_queryset().create(name=name), True


    def comma_to_qs(self, tag_str):
        final_ids = []
        for tag in tag_str.split(','):
            obj, created = self.create_or_new(tag)
            final_ids.append(obj.id)
        qs = self.get_queryset().filter(id__in=final_ids).distinct()
        return qs