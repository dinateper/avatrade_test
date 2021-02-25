# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.core import validators


class User(models.Model):

    user_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()


class Post(models.Model):

    post_id = models.AutoField(primary_key=True)
    creator_user_id = models.ForeignKey('User', on_delete=models.CASCADE)
    content = models.TextField()
    likes = models.CharField(max_length=300, validators=[validators.validate_comma_separated_integer_list], blank=True)

