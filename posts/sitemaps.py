from django.contrib.sitemaps import Sitemap
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Article




class PostSitemap(Sitemap):
    changefreq = 'weekly'
    # priority = 0.9

    def items(self):
        return Article.objects.filter(
        Q(status='PUB') & Q(active=True)).order_by('-created')

    def lastmod(self, obj):
        return obj.updated 