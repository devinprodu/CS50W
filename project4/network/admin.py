from pdb import post_mortem
from django.contrib import admin

from .models import Post, Followee, Follower, Like

# Register your models here.

admin.site.register(Post)
admin.site.register(Followee)
admin.site.register(Follower)
admin.site.register(Like)