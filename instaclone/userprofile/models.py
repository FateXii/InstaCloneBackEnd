from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django_countries.fields import CountryField
import uuid


class Profile(models.Model):
    pk_uuid = models.UUIDField(default=uuid.uuid4, null=False,
                               editable=False, unique=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    country = CountryField(blank=True, null=True)
    bio = models.CharField(max_length=255, blank=True, null=True)
    is_private = models.BooleanField(default=False)
    profiles_followed = models.ForeignKey(
        'self', to_field='pk_uuid', on_delete=models.DO_NOTHING,
        blank=True, null=True, related_name='following')


class FollowRequests(models.Model):
    pk_uuid = models.UUIDField(default=uuid.uuid4, null=False,
                               editable=False, unique=True)
    request_from = models.ForeignKey(
        Profile, to_field='pk_uuid',
        on_delete=models.CASCADE,
        related_name='requests_sent')
    request_to = models.ForeignKey(
        Profile, to_field='pk_uuid',
        on_delete=models.CASCADE,
        related_name='requests_received')
    created = models.DateTimeField(auto_now_add=True)
    accepted = models.DateTimeField(blank=True, null=True)
    rejected = models.DateTimeField(blank=True, null=True)
