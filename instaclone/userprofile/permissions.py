from rest_framework import permissions


class IsCurrentUser(permissions.BasePermission):
    """
    Global permission check for blacklisted IPs.
    """

    def has_object_permission(self, request, view, obj):
        return request.user.profile == obj


class CanView(permissions.BasePermission):
    """
    Global permission check for blacklisted IPs.
    """

    def has_object_permission(self, request, view, obj):
        return True
        # return (obj.id in request.user.profile.following or
        # not obj.is_private)
