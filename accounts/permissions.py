from rest_framework.permissions import BasePermission


class SuperAdminManager(BasePermission):
    """Access for SuperAdmin role with method-based restrictions."""

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return user.role == "superadmin"
        if request.method in ("POST", "PUT", "PATCH", "DELETE"):
            return user.role == "superadmin"
        return False


class AdminManager(BasePermission):
    """Access for Admin and SuperAdmin roles."""

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return user.role in ("superadmin", "admin")
        if request.method in ("POST", "PUT", "PATCH", "DELETE"):
            return user.role in ("superadmin", "admin")
        return False


class SalesPersonManager(BasePermission):
    """Access for all authenticated staff roles."""

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return user.role in ("superadmin", "admin", "salesperson")
        if request.method in ("POST", "PUT", "PATCH", "DELETE"):
            return user.role in ("superadmin", "admin", "salesperson")
        return False
