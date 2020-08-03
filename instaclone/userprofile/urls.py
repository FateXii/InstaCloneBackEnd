from rest_framework import routers
from userprofile import views
from django.urls import path, include, re_path


router = routers.SimpleRouter()
router.register(r'profiles',  views.ProfileViewSet, 'profiles')

urlpatterns = [
    path('', include(router.urls)),
    path('profiles/<uuid:pk_uuid>/requests_sent',
         views.requests_sent_view, name='requests-sent'),
    path('profiles/<uuid:pk_uuid>/requests_received',
         views.requests_received_view, name='requests-received'),
    path('profiles/<uuid:pk_uuid>/requests/<uuid:request_uuid>/',
         views.requests_detail_view, name='requests-detail'),
    path('profiles/<uuid:pk_uuid>/requests/<uuid:request_uuid>/accept',
         views.requests_accept_view, name='requests-accept'),
    path('profiles/<uuid:pk_uuid>/requests/<uuid:request_uuid>/reject',
         views.requests_reject_view, name='requests-reject'),

    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
]
