from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from .views import (signup,
                    login_view,
                    ChangeUserPasswordView,
                    profile_view,
                    update_info_profile,
                    update_info_user,
                    draft_profile_posts,
                    saved_posts,
                    reset_password,
                    confirm_code_reset,
                    change_password_reset
                    )
urlpatterns = [
    path('signup/', signup, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='profiles/logout.html'), name='logout'),

    path('update/user/', update_info_user, name='update_info_user'),
    path('update/profile/', update_info_profile, name='update_info_profile'),

    path('<uuid:id>/', profile_view, name='profile'),
    path('<uuid:id>/draft/', draft_profile_posts, name='draft_posts'),
    path('saved', saved_posts, name='saved'),
    # path('<uuid:id>/draft/<slug:slug>/', draft_post, name='draft_post'),

    path('change_password/', ChangeUserPasswordView.as_view(
        template_name='profiles/change_password.html'), name='change_password'),

    path('change_done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='profiles/change_done.html'), name='password_change_done'),
    path('reset_password/', reset_password, name='reset_password'),
    path('sended_reset_code/', TemplateView.as_view(
        template_name='profiles/sended_reset_code.html'), name='sended_reset_code'),
    path('confirm_code_reset/<uuid:id>/',
         confirm_code_reset, name='confirm_code_reset'),
    path('change_password_reset/<str:code>/',
         change_password_reset, name='change_password_reset')

]
