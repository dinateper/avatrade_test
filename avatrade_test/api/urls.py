from django.conf.urls import url, include
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token
from . import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet, basename='users')
router.register(r'posts', views.PostViewSet)
router.register(r'register', views.RegistrationViewSet)
router.register(r'like', views.LikeViewSet)

urlpatterns = [
    url('', include(router.urls)),
    url('api-auth/', include('rest_framework.urls')),
    url('api-token-auth/', obtain_auth_token)
]

