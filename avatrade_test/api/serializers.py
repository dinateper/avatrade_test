from rest_framework import serializers
from .models import Post, Like
from django.contrib.auth.models import User
from .consts import CLEARBIT_KEY, HUNTER_KEY

import clearbit
import requests

clearbit.key = CLEARBIT_KEY


class PostSerializer(serializers.ModelSerializer):

    creator = serializers.ReadOnlyField(source='creator.username')
    likes = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ('post_id', 'creator', 'content', 'likes')
        read_only_fields = ('creator', 'likes')


class UserSerializer(serializers.ModelSerializer):

    posts = serializers.PrimaryKeyRelatedField(many=True, queryset=Post.objects.all())
    liked_posts = serializers.PrimaryKeyRelatedField(many=True, allow_empty=True, queryset=Like.objects.all())

    class Meta:
        model = User
        fields = ('id', 'username', 'posts', 'liked_posts')


class LikeSerializer(serializers.ModelSerializer):

    user_id = serializers.ReadOnlyField(source='user_id.username')

    class Meta:
        model = Like
        fields = ('id', 'user_id', 'post_id')

    def save(self, **kwargs):
        user_id = kwargs['user_id']
        post_id = self.validated_data['post_id']
        if Post.objects.get(post_id=getattr(post_id, 'post_id')).creator == user_id:
            raise serializers.ValidationError({'post_id': "user cannot like his own post"})
        like = Like(post_id=post_id, user_id=user_id)
        like.save()


class RegistrationSerializer(serializers.ModelSerializer):

    id = serializers.ReadOnlyField()
    confirm_password = serializers.CharField(max_length=128, style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'password', 'confirm_password')
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def save(self):
        password = self.validated_data['password']
        confirm_password = self.validated_data['confirm_password']
        if password != confirm_password:
            raise serializers.ValidationError({'password': "passwords do not match"})
        res = requests.get('https://api.hunter.io/v2/email-verifier?email={}&api_key={}'
                           .format(self.validated_data['email'], HUNTER_KEY))
        if '"status": "invalid"' in res.content:
            raise serializers.ValidationError({'email': "invalid email address"})
        enrichment = clearbit.Enrichment.find(email=self.validated_data['email'])
        first_name = ''
        last_name = ''
        if enrichment and enrichment.has_key('person'):
            first_name = enrichment['person']['name']['givenName'] or first_name
            last_name = enrichment['person']['name']['familyName'] or first_name
        user = User(
            email=self.validated_data['email'],
            username=self.validated_data['username'],
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        user.set_password(password)
        user.save()
        return user
