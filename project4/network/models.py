from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _



class User(AbstractUser):
    pass

class Post(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    content = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def serialize(self):
        return {
            "creator": self.creator,
            "content": self.content,
            "created_on": self.created_on,
            "updated_on": self.updated_on,
        }

    def __str__(self):
        return f"{self.creator}: {self.content}"

class Followee(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followeesu")
    followees = models.ManyToManyField(User, related_name="followeeT", blank=True)

    def __str__(self):
        return f"{self.user} Followees"

class Follower(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followersu")
    followers = models.ManyToManyField(User, blank=True, related_name="followedT")

    def __str__(self):
        return f"{self.user} Followers"

class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes", unique=True)
    user = models.ManyToManyField(User, blank=True, related_name="likes")
    def __str__(self):
        return f"{self.post} Likes"