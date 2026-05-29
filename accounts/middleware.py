from django.conf import settings
from django.shortcuts import redirect
from django.urls import resolve, reverse
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken

from accounts.models import User


class JWTAuthMiddleware:
    """
    Attach user from JWT access cookie for template-based views.
    Runs after Django's AuthenticationMiddleware.
    """

    EXEMPT_PREFIXES = (
        "/admin/",
        "/static/",
        "/media/",
        "/api/auth/login/",
        "/login/",
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            token = request.COOKIES.get(settings.JWT_AUTH_COOKIE)
            if token:
                try:
                    validated = AccessToken(token)
                    user_id = validated.get("user_id")
                    request.user = User.objects.get(pk=user_id, is_active=True)
                except (InvalidToken, TokenError, User.DoesNotExist, TypeError):
                    pass
        return self.get_response(request)

    @classmethod
    def is_exempt(cls, path):
        return any(path.startswith(prefix) for prefix in cls.EXEMPT_PREFIXES)


class ProfileCompletionMiddleware:
    """Redirect users with incomplete profiles to the complete-profile page."""

    EXEMPT_NAMES = {
        "login",
        "logout",
        "complete_profile",
        "api_login",
        "api_logout",
        "api_token_refresh",
    }

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if JWTAuthMiddleware.is_exempt(request.path) or request.path.startswith("/admin/"):
            return self.get_response(request)

        user = getattr(request, "user", None)
        if user and user.is_authenticated and not user.is_profile_completed:
            try:
                match = resolve(request.path)
                if match.url_name in self.EXEMPT_NAMES:
                    return self.get_response(request)
            except Exception:
                pass
            complete_url = reverse("complete_profile")
            if request.path != complete_url:
                return redirect(complete_url)

        return self.get_response(request)
