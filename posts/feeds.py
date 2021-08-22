from django.contrib.syndication.views import Feed
from django.urls import reverse_lazy
from django.template.defaultfilters import truncatewords
from django.db.models import Q
from .models import Article



class LatestArticlesFeed(Feed):

    title = 'My blog'    
    link = reverse_lazy('posts')    
    description = 'New posts of my blog.'

    def items(self):        
    	return Article.objects.filter(
        Q(status='PUB') & Q(active=True)).order_by('-created')[:20]

    def item_title(self, item):     
        return item.title

    def item_description(self, item):    
        return truncatewords(item.body, 500)

