from django.contrib import admin
from .models import TweetStatus, LikeDislikeTweet

admin.site.register(TweetStatus)
admin.site.register(LikeDislikeTweet)
