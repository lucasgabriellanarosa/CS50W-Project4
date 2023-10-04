
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new_post", views.new_post, name="new_post"),
    path("user_profile/<int:user_id>", views.user_profile, name="user_profile"),
    path("following_page", views.following_page, name="following_page"),
    

    # Api
    path("like_post/<int:post_id>", views.like_post, name="like_post"),
    path("follow_user/<int:profile_user_id>", views.follow_user, name="follow_user"),
    path("unfollow_user/<int:profile_user_id>", views.unfollow_user, name="unfollow_user"),
    path("get_following_count/<int:profile_user_id>", views.get_following_count, name="get_following_count"),
    path("save_edit/<int:post_id>", views.save_edit, name="save_edit"),
]
