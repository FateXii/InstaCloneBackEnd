from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django_countries.fields import CountryField
# from django.contrib.postgres.functions import RandomUUID
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
    bio = models.CharField(max_length=255)
    is_private = models.BooleanField(default=False)
    profiles_followed = models.ForeignKey(
        'self', to_field='pk_uuid', on_delete=models.DO_NOTHING,
        blank=True, null=True, related_name='following')


class FollowRequests(models.Model):
    pk_uuid = models.UUIDField(default=uuid.uuid4, null=False,
                               editable=False, unique=True)
    request_by = models.ForeignKey(
        Profile, to_field='pk_uuid',
        on_delete=models.CASCADE,
        related_name='sent_by')
    # request_to_follow = models.ForeignKey(
    #     Profile, to_field='id',
    #     on_delete=models.CASCADE,
    #     related_name='sent_to')
    created = models.DateTimeField(auto_now_add=True)
    accepted = models.DateTimeField(blank=True, null=True)
