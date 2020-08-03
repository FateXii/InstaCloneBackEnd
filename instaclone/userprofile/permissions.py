from rest_framework import permissions
from django.core import exceptions
from .models import Profile
from django.shortcuts import get_object_or_404


class IsAuthenticatedCurrentUserObj(permissions.IsAuthenticated):
    """
    Check if request user is user being accessed
    """

    def has_object_permission(self, request, view, obj):
        return super().has_permission(request, view) and\
            request.user.profile.id == obj.id


class IsAuthenticatedCurrentUserView(permissions.IsAuthenticated):
    """
    Check if request user is user being accessed
    """

    def has_permission(self, request, view):
        obj = get_object_or_404(Profile, pk_uuid=view.kwargs['pk_uuid'])
        return super().has_permission(request, view) and\
            request.user.profile.id == obj.id


class IsAuthenticatedAndFollowingPrivateProfile(permissions.BasePermission):
    """
    Check if user is authenticated and following a profile
    """

    def has_permission(self, request, view):
        obj = get_object_or_404(Profile, pk_uuid=view.kwargs['pk_uuid'])
        if obj.is_private:
            if not request.user.is_authenticated:
                return False
            return obj in request.user.profile.following.all()
        return True
