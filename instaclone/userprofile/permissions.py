from rest_framework import permissions


class IsAuthenticatedCurrentUser(permissions.IsAuthenticated):
    """
    Check if request user is user being accessed
    """

    def has_object_permission(self, request, view, obj):
        return request.user.profile.id == obj.id and\
            super().has_permission(request, view)
