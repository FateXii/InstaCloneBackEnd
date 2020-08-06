from rest_framework import permissions


class IsUserWhoPosted(permissions.BasePermission):
    """
        Check if poster is current user
    """

    def has_object_permission(self, request, view, post):
        return request.user.profile == post.profile


class PosterIsNotPrivateOrUserIsFollowing(permissions.BasePermission):
    """
    Check if posted by private user
    """

    def has_object_permission(self, request, view, post):
        poster = post.profile
        current_profile = request.user.profile
        return not poster.is_private or\
            (poster.is_private and poster in current_profile.following)
