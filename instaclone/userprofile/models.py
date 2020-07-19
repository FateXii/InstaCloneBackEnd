from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


class PhoneNumber(models.Model):
    country_code = models.CharField(max_length=10)
    number = models.CharField(max_length=30)


class Profile(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile')
    phone_number = models.OneToOneField(
        PhoneNumber, on_delete=models.CASCADE,
        null=True, blank=True)

    bio = models.CharField(max_length=255)
    is_private = models.BooleanField(default=False)

    profiles_followed = models.ForeignKey(
        'self', on_delete=models.DO_NOTHING,
        blank=True, null=True, related_name='following')

    follow_requests = models.ForeignKey(
        'self', on_delete=models.DO_NOTHING,
        blank=True, null=True, related_name='follow_requests_received')


# @receiver(post_save, sender=settings.AUTH_USER_MODEL)
# def create_auth_token(sender, instance=None, created=False, **kwargs):
#     """Create auth token on user/profile creation"""
#     if created:
#         Token.objects.create(user=instance)
