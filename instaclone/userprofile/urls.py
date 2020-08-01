from rest_framework import routers
from userprofile import views
from django.urls import path, include, re_path


router = routers.SimpleRouter()
router.register(r'profiles',  views.ProfileViewSet, 'profiles')

urlpatterns = [
    path('', include(router.urls)),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),

]
