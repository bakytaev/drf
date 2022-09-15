from django.db import IntegrityError
from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, get_object_or_404
from rest_framework.authentication import SessionAuthentication, TokenAuthentication

from .permissions import IsAuthorPermission, CommentPermission


from .models import Tweet, Comment, LikeTweet, DisLikeTweet, LikeDislikeTweet, TweetStatus, LikeDislikeComment, CommentStatus
from .serializers import TweetSerializer, CommentSerializer
from .paginations import StandardPagination


class TweetViewSet(ModelViewSet):
    serializer_class = TweetSerializer
    queryset = Tweet.objects.all()
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthorPermission, ]
    pagination_class = StandardPagination

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        queryset = self.queryset
        user = self.request.query_params.get('user')
        if user:
            queryset = queryset.filter(user__username=user)
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(text__icontains=search)
        return queryset


# class CommentViewSet(ModelViewSet):
#     serializer_class = CommentSerializer
#     queryset = Comment.objects.all()
#     authentication_classes = [SessionAuthentication, TokenAuthentication]
#     permission_classes = [CommentPermission, ]
#
#     def perform_create(self, serializer):
#         serializer.save(user=self.request.user)

class CommentListCreateAPIView(ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthorPermission, ]

    # def get_queryset(self):
    #     return self.queryset.filter(tweet=Tweet.objects.get(id=tweet_id))

    def get_queryset(self):
        print(self.kwargs)
        return self.queryset.filter(tweet_id=self.kwargs['tweet_id'])

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            tweet=get_object_or_404(Tweet, id=self.kwargs['tweet_id'])
        )


class CommentRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthorPermission, ]


class PostTweetLike(APIView):
    def get(self, request, tweet_id, status_slug):
        tweet = get_object_or_404(Tweet, id=tweet_id)
        tweet_status = get_object_or_404(TweetStatus, slug=status_slug)
        try:
            like_dislike = LikeDislikeTweet.objects.create(tweet=tweet, user=request.user)
        except IntegrityError:
            like_dislike = LikeDislikeTweet.objects.get(tweet=tweet, user=request.user)
            like_dislike.status = tweet_status
            like_dislike.save()
            data = {"error": f"tweet {tweet_id} has changed status by {request.user.username}"}
            return Response(data, status=status.HTTP_200_OK)
        else:
            data = {"message": f"tweet {tweet_id} got status from {request.user.username}"}
            return Response(data, status=status.HTTP_201_CREATED)


# class PostTweetDisLike(APIView):
#     def get(self, request, tweet_id):
#         tweet = get_object_or_404(Tweet, id=tweet_id)
#         try:
#             dislike = DisLikeTweet.objects.create(tweet=tweet, user=request.user)
#         except IntegrityError:
#             dislike = DisLikeTweet.objects.get(tweet=tweet, user=request.user)
#             dislike.delete()
#             data = {"error": f"tweet {tweet_id} already got dislike from {request.user.username}"}
#             return Response(data, status=status.HTTP_204_NO_CONTENT)
#         else:
#             data = {"message": f"tweet {tweet_id} got dislike from {request.user.username}"}
#             return Response(data, status=status.HTTP_201_CREATED)


class PostCommentLike(APIView):
    def get(self, request, comment_id, status_slug):
        comment = get_object_or_404(Comment, id=comment_id)
        comment_status = get_object_or_404(CommentStatus, slug=status_slug)
        try:
            like_dislike = LikeDislikeComment.objects.create(comment=comment, user=request.user)
        except IntegrityError:
            like_dislike = LikeDislikeComment.objects.get(comment=comment, user=request.user)
            like_dislike.status = comment_status
            like_dislike.save()
            data = {"error": f"comment {comment_id} has changed status by {request.user.username}"}
            return Response(data, status=status.HTTP_200_OK)
        else:
            data = {"message": f"comment {tweet_id} got status from {request.user.username}"}
            return Response(data, status=status.HTTP_201_CREATED)
