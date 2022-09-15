from django.contrib import admin
from .models import TweetStatus, LikeDislikeTweet, CommentStatus, LikeDislikeComment

admin.site.register(TweetStatus)
admin.site.register(LikeDislikeTweet)
admin.site.register(CommentStatus)
admin.site.register(LikeDislikeComment)
