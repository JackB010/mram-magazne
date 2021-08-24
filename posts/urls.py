from django.urls import path
from .feeds import LatestArticlesFeed
from .views import (PostsList,
                    post,
                    create_post,
                    update_post,
                    search,
                    post_by_tag,
                    top_posts,
                    top_tags_api,
                    # api
                    delete_post_api,
                    like_api,
                    is_liked_api,
                    delete_comment_api,
                    comment_api,
                    save_api,
                    is_saved_api,
                    super_profile_api,
                    is_super_profile_api
                    )


urlpatterns = [

     path('', PostsList.as_view(), name='posts'),
     path('<uuid:id>/<str:status>/', post, name='post'),
     path('search/', search, name='search'),
     path('create/', create_post, name='create_post'),
     path('update/<uuid:id>/<str:status>/', update_post, name='update_post'),
     path('tag/<str:tag>/', post_by_tag, name='tags'),
     path('top/', top_posts, name='top_posts'),
     path('feed/', LatestArticlesFeed(), name='post_feed'), 
#     path('top/tags/', top_tags, name='top_tags'),


    # api
    path('api/like/<uuid:id>/', like_api, name='like_api'),
    path('api/is_liked/', is_liked_api, name='is_liked_api'),
    path('api/comment/delete/', delete_comment_api, name='delete_comment_api'),
    path('api/comment/', comment_api, name='comment_api'),
    path('api/save/', save_api, name='save_api'),
    path('api/is_saved/', is_saved_api, name='is_saved_api'),
    path('api/delete/post/',
         delete_post_api, name='delete_post_api'),
    path('api/super/profile/',
         super_profile_api, name='super_profile_api'),
    path('api/is_super/profile/',
         is_super_profile_api, name='is_super_profile_api'),
     path('api/top/tags/', top_tags_api, name='top_tags_api'),



]
