from django.contrib.auth.models import AnonymousUser
from django.shortcuts import redirect
from django.urls import reverse

class JWTLoginRequiredMixin:
    """Require authenticated user via JWT cookie or session."""

    login_url = "login"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or isinstance(request.user, AnonymousUser):
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)


class RoleRequiredMixin(JWTLoginRequiredMixin):
    """Restrict view access to specified roles."""

    allowed_roles = ()

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(self.login_url)
        if self.allowed_roles and request.user.role not in self.allowed_roles:
            return redirect("dashboard")
        return super(JWTLoginRequiredMixin, self).dispatch(request, *args, **kwargs)


class SuperAdminRequiredMixin(RoleRequiredMixin):
    allowed_roles = ("superadmin",)


class AdminOrSuperAdminRequiredMixin(RoleRequiredMixin):
    allowed_roles = ("superadmin", "admin")
