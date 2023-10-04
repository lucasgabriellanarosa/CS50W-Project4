from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import *
import json
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator

# Paginator Function 
def paginator(request, posts):
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    posts_of_the_page = paginator.get_page(page_number)
    return posts_of_the_page


# Views
def index(request):
    allPosts = Post.objects.all().order_by('timestamp').reverse()
    current_user = request.user 

    posts_of_the_page = paginator(request, allPosts)
    
    postsCurrentUserLiked = []

    try:
        for like in Like.objects.all():
            if like.user.id == current_user.id:
                postsCurrentUserLiked.append(like.post.id)
    except:
        postsCurrentUserLiked = []

    return render(request, "network/index.html", {
        'posts_of_the_page': posts_of_the_page,
        'current_user': current_user,
        'postsCurrentUserLiked': postsCurrentUserLiked,
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


@login_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


@login_required
def new_post(request):
    if request.method == 'POST':
        current_user = request.user
        new_post_textarea = request.POST['new_post_textarea']

        newPost = Post(
            user=current_user,
            text=new_post_textarea
        )
        newPost.save()
        return HttpResponseRedirect(reverse('index'))


def user_profile(request, user_id):
    post_owner = User.objects.get(id=user_id)
    allOwnerPosts = Post.objects.filter(user=post_owner).order_by("timestamp").reverse()
    current_user = request.user

    posts_of_the_page = paginator(request, allOwnerPosts)

    postsCurrentUserLiked = []

    try:
        for like in Like.objects.all():
            if like.user.id == current_user.id:
                postsCurrentUserLiked.append(like.post.id)
    except:
        postsCurrentUserLiked = []

    if current_user != post_owner:
        try:
            if Following.objects.get(user_following=current_user, user_followed=post_owner):
                current_user_follows_post_owner = True
            else:
                current_user_follows_post_owner = False
        except:
            current_user_follows_post_owner = False
    else:
        current_user_follows_post_owner = False

    return render(request, 'network/user_profile.html', {
        'profile_user': post_owner,
        'posts_of_the_page': posts_of_the_page,
        'current_user': current_user,
        'postsCurrentUserLiked': postsCurrentUserLiked,
        'current_user_follows_post_owner': current_user_follows_post_owner,
    })


def following_page(request):
    current_user = request.user
    allFollowing = Following.objects.filter(user_following=current_user) 
    allPosts = Post.objects.all().order_by('timestamp').reverse()

    currentUserFollowingPosts = []

    for post in allPosts:
        for following in allFollowing:
            if following.user_followed == post.user:
                currentUserFollowingPosts.append(post)

    posts_of_the_page = paginator(request, currentUserFollowingPosts)


    postsCurrentUserLiked = []

    try:
        for like in Like.objects.all():
            if like.user.id == current_user.id:
                postsCurrentUserLiked.append(like.post.id)
    except:
        postsCurrentUserLiked = []

    return render(request, 'network/following_page.html', {
        'posts_of_the_page': posts_of_the_page,
        'current_user': current_user,
        'postsCurrentUserLiked': postsCurrentUserLiked,
    })


# Api

@login_required
def like_post(request, post_id):
    current_user = request.user
    postsCurrentUserLiked = []

    try:
        for like in Like.objects.all():
            if like.user.id == current_user.id:
                postsCurrentUserLiked.append(like.post.id)
    except:
        postsCurrentUserLiked = []

    post_liked = Post.objects.get(id=post_id)

    if post_id in postsCurrentUserLiked:
        like = Like.objects.get(user=current_user, post=post_liked)
        like.delete()
        liked = False
    else:
        newLike = Like(user=current_user, post=post_liked)
        newLike.save()
        liked = True

    post_likes_count = post_liked.post_likes.count()
    return JsonResponse({"post_id": post_id, "post_likes_count": post_likes_count, "liked": liked})


@login_required
def follow_user(request, profile_user_id):
    newFollowing = Following(
        user_following=request.user,
        user_followed=User.objects.get(pk=profile_user_id)
    )
    newFollowing.save()
    return JsonResponse({"message": "Following user"})


@login_required
def unfollow_user(request, profile_user_id):
    following = Following.objects.get(user_following=request.user, user_followed=User.objects.get(pk=profile_user_id))
    following.delete()

    return JsonResponse({"message": "Unfollowing user"})


def get_following_count(request, profile_user_id):
    profile_user = User.objects.get(pk=profile_user_id)
    # Users being followed by profile_user
    following_count = Following.objects.filter(user_following=profile_user).count()

    # Users following profile_user
    followers_count = Following.objects.filter(user_followed=profile_user).count()

    return JsonResponse({"followers_count": followers_count, "following_count": following_count})


@csrf_exempt
@login_required
def save_edit(request, post_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        edited_post = Post.objects.get(pk=post_id)
        edited_post.text = data["newText"]
        edited_post.save()
        return JsonResponse({"newText": data["newText"] })
    