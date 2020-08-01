from rest_framework import permissions


class IsCurrentUser(permissions.BasePermission):
    """
    Check if request user is user being accessed
    """

    def has_object_permission(self, request, view, obj):
        return request.user.profile.id == obj.id
