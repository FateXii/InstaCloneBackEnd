from rest_framework import permissions


class ProfilePermissions(permissions.BasePermission):
    message = 'Adding customers not allowed.'

    def has_permission(self, request, view):
        pass
