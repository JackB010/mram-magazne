from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from django.views.generic.base import RedirectView
from django.contrib.sitemaps.views import sitemap
from posts.sitemaps import PostSitemap


sitemaps = {'posts': PostSitemap,}
urlpatterns = i18n_patterns(
    path('admin/', admin.site.urls),
    path('profile/', include('profiles.urls')),
    path('', RedirectView.as_view(url='/ar/posts/')),
    path('posts/', include('posts.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap') 
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
