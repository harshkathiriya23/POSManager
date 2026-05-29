from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


def set_jwt_cookies(response, tokens):
    access_max_age = int(settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds())
    refresh_max_age = int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds())
    cookie_kwargs = {
        "httponly": True,
        "samesite": settings.JWT_COOKIE_SAMESITE,
        "secure": settings.JWT_COOKIE_SECURE,
        "path": "/",
    }
    response.set_cookie(
        settings.JWT_AUTH_COOKIE,
        tokens["access"],
        max_age=access_max_age,
        **cookie_kwargs,
    )
    response.set_cookie(
        settings.JWT_REFRESH_COOKIE,
        tokens["refresh"],
        max_age=refresh_max_age,
        **cookie_kwargs,
    )
    return response


def clear_jwt_cookies(response):
    response.delete_cookie(settings.JWT_AUTH_COOKIE, path="/")
    response.delete_cookie(settings.JWT_REFRESH_COOKIE, path="/")
    return response
