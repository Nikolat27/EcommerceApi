from rest_framework.permissions import BasePermission


class IsAuthenticatedOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        # Allow GET requests (for listing products) for all users
        if request.method == "GET":
            return True

        # For all other methods, check if the user is authenticated
        return request.user and request.user.is_authenticated
