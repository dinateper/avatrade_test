# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import viewsets, permissions
from .serializers import UserSerializer, PostSerializer, RegistrationSerializer, LikeSerializer
from .models import Post, Like
from .permissions import IsOwnerOrAuth
from django.contrib.auth.models import User


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class PostViewSet(viewsets.ModelViewSet):
    """
    allows posts to be created and edited
    """
    queryset = Post.objects.all().order_by('post_id')
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)


class LikeViewSet(viewsets.ModelViewSet):
    """
    allows tolike and unlike posts
    """
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    permission_classes = [IsOwnerOrAuth]

    def perform_create(self, serializer):
        serializer.save(user_id=self.request.user)


class RegistrationViewSet(viewsets.ModelViewSet):
    """
    allows new users to be created
    """
    serializer_class = RegistrationSerializer
    queryset = User.objects.none()



