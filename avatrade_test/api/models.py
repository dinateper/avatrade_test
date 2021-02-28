# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class Post(models.Model):

    post_id = models.AutoField(primary_key=True)
    creator = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()


class Like(models.Model):

    post_id = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='likes')
    user_id = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='liked_posts')
