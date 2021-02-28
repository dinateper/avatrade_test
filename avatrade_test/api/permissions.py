from rest_framework import permissions


class IsOwnerOrAuth(permissions.IsAuthenticated):
    """
    allows all user to read, only crator can delete
    """

    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_authenticated:
            if request.method in permissions.SAFE_METHODS:
                return True
            return obj.user_id == request.user
        return False