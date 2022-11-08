from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.forms import ModelForm
from django.core.paginator import Paginator


import json



from .models import User, Post, Followee, Follower, Like



class PostForm(ModelForm):
     class Meta:
         model = Post
         fields = ['creator', 'content']

def index(request, page=1):
    # Get all posts from the DB
    posts = Post.objects.all().order_by('-created_on')
    paginated_posts= Paginator(posts, 10)
    page_as_int = int(page)
    prev = page_as_int - 1
    return render(request, "network/index.html", {
        'posts': paginated_posts.page(page),
        'pages': range(1, paginated_posts.num_pages + 1),
        'prev': lambda: prev if prev>=1 else False,
        'next': lambda: page_as_int+1 if page_as_int+1<=paginated_posts.num_pages else False
    })


def profile(request, username, page=1):
    # TODO Check how it displays for logged out users
    user = User.objects.get(username=username)
    followbool = request.user.followeesu.filter(followees=user)
    selfprofile = user == request.user
    posts = Post.objects.filter(creator=user).order_by('-created_on')
    paginated_posts= Paginator(posts, 10)
    page_as_int = int(page)
    prev = page_as_int - 1

    return render(request, "network/profile.html", {
        'userdata': user,
        'posts': posts,
        'following': followbool,
        'self': selfprofile,
        'pages': range(1, paginated_posts.num_pages + 1),
        'prev': lambda: prev if prev>=1 else False,
        'next': lambda: page_as_int+1 if page_as_int+1<=paginated_posts.num_pages else False
    })


@login_required
def following(request):
    try:
        posts = Post.objects.filter(creator__in=request.user.followeesu.first().followees.all()).order_by('-created_on')
    except:
        return render(request, "network/index.html", {
        'message': "You are not following anyone yet"
    })
        
    print(request.user.followeesu.first().followees.all())
    return render(request, "network/index.html", {
        'posts': posts
    })

@login_required
def follow(request):
    # Require method be post
    if request.method != "POST":
        return redirect("network/index.html")

    # Check if the user is trying to follow themselves.
    # Tried to add this check in the db model but failed miserably, it's not trivial to implement with MtM relationships.
    if request.user.username == request.POST['followee']:
         return render(request, "network/index.html", {
                "message": "You can't follow yourself."
            })

    followee = User.objects.get(username=request.POST['followee'])

    # Check if user is already following the followee
    try:
        followship = request.user.followeesu.get(followees=followee)
        print(followship)
        # If true, delete the relationships
        followship.followees.remove(followee)
        followee.followersu.first().followers.remove(request.user)
    except:
        # Relationship doesnt exist, add it
        # Add the current user to the followee followers list
        if request.user.followeesu.all().count() == 0:
            # Create Followee if it doesn't exist
            followee_list = Followee.objects.create(user=request.user)

        # Add followee to list
        request.user.followeesu.first().followees.add(followee)

        # Add the followed user to the follower's followee list
        if followee.followersu.all().count() == 0:
            # Create Follower if it doesn't exist
            follower_list = Follower.objects.create(user=followee)
        # Add followee to list
        followee.followersu.first().followers.add(request.user)

    return redirect("index") # TODO Update the redirect
    
    
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
def post(request):
    # New posts must be created via POST
    if request.method != "POST":
        # TODO review
        return render(request, "network/index.html", {
                "message": "Posts should be submitted via POST"
            })
    
    # Load data into dict.
    try:
        formcontent = {}
        formcontent['creator'] = request.user
        formcontent['content'] = request.POST['newpost']
    except:
        return render(request, "network/index.html", {
                "message": "There was a problem creating your post, please check if you are logged in \
                    and if your post content was valid."
            })

    # Populate form
    postform = PostForm(formcontent)
    
    if postform.is_valid():
        posted = postform.save()
        return index(request)
        
    return render(request, "network/index.html", {
                    "message": "The submited post was not valid.",
                    "error": postform.errors
                })

@login_required
def edit(request):
    # Only accept PUT requests
    if request.method != "PUT":
        return JsonResponse({"error": "PUT request required."}, status=400)

    # Read data from request
    data = json.loads(request.body)
    # Lookup post
    try:
        post = Post.objects.get(id=data['id'])
    except Post.DoesNotExist:
        return JsonResponse({"error": "Please enter a valid id"}, status=404)

    # Check whether the request was submitted by the original poster
    if request.user != post.creator:
        return JsonResponse({"error": "You can't edit posts submitted by other users"}, status=401)
    # User is OP, continue
    # In production I would actually truncate data content to ensure a char limit and sanitize it just in case.
    post.content = data['content']
    post.save()

    return JsonResponse({"message": "Post was updated successfully"}, status=200)

@login_required
def like(request):
    # Only accept PUT requests
    if request.method != "PUT":
        return JsonResponse({"error": "PUT request required."}, status=400)
    
    # Read data from request
    data = json.loads(request.body)

    # Check if the post exists
    try: 
        post = Post.objects.get(id=data['id'])
    except Post.DoesNotExist:
        return JsonResponse({"error": "Please enter a valid post id"}, status=404)
    # Check if the like model exists for this post
    try:
        liked = Like.objects.get(post=data['id'])
        # Check if user previously liked this post
        if request.user in liked.user.all():
            # User liked the post, remove it
            print("got to user liked")
            liked.user.remove(request.user)
            return JsonResponse({"success": "Like removed"}, status=200)
        # User hasn't liked the post before, like it
        print("got to user hasnt liked")
        liked.user.add(request.user)
        return JsonResponse({"success": "Like added"}, status=200)
    except Like.DoesNotExist:
        print("got to like doesnNOtExist")
        # This is the first like on this post, create the object
        liked = Like(post=post)
        liked.save()
        liked.user.add(request.user)
        return JsonResponse({"success": "Like added"}, status=404)