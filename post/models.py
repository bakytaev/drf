from django.db import models
from django.db.models.signals import pre_save, post_save
from django.db.models import Count

from account.models import User


def like_dislike_save(sender, instance, **kwargs):
    if sender == LikeTweet:
        model = DisLikeTweet
    else:
        model = LikeTweet
    try:
        like_dislike = model.objects.get(tweet=instance.tweet, user=instance.user)
    except model.DoesNotExist:
        pass
    else:
        like_dislike.delete()


class Post(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.__class__.__name__} from {self.user.username} at {self.updated}'

    @property
    def post_username(self):
        return self.user.username


class Tweet(Post):
    text = models.CharField(max_length=140)

    # def get_likes(self):
    #     likes = LikeTweet.objects.filter(tweet=self)
    #     return likes.count()
    #
    # def get_dislikes(self):
    #     dislikes = DisLikeTweet.objects.filter(tweet=self)
    #     return dislikes.count()

    def get_status(self):
        like_dislike = LikeDislikeTweet.objects.filter(tweet=self)\
            .values('status__status_name').annotate(count=Count('status'))
        statuses = {}
        for i in like_dislike:
            statuses[i['status__status_name']] = i['count']

        return statuses


class Comment(Post):
    text = models.CharField(max_length=255)
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE)


class LikeTweet(models.Model):
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'tweet')

    # def save(self, *args, **kwargs):
    #     try:
    #         dislike = DisLikeTweet.objects.get(tweet=self.tweet, user=self.user)
    #     except DisLikeTweet.DoesNotExist:
    #         pass
    #     else:
    #         dislike.delete()
    #     super().save(*args, **kwargs)


class DisLikeTweet(models.Model):
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'tweet')

    # def save(self, *args, **kwargs):
    #     try:
    #         like = LikeTweet.objects.get(tweet=self.tweet, user=self.user)
    #     except LikeTweet.DoesNotExist:
    #         pass
    #     else:
    #         like.delete()
    #     super().save(*args, **kwargs)


class TweetStatus(models.Model):
    slug = models.CharField(max_length=32, unique=True)
    status_name = models.CharField(max_length=64)

    def __str__(self):
        return self.status_name


class LikeDislikeTweet(models.Model):
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.ForeignKey(TweetStatus, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'tweet')

    def __str__(self):
        return f'{self.tweet} - {self.user.username} - {self.status.status_name}'


post_save.connect(like_dislike_save, LikeTweet)
post_save.connect(like_dislike_save, DisLikeTweet)