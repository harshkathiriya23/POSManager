from django.urls import path

from accounts.api.views import (
    CookieTokenRefreshView,
    LoginAPIView,
    LogoutAPIView,
    ProfileAPIView,
    UserDetailAPIView,
    UserListCreateAPIView,
)

urlpatterns = [
    path("auth/login/", LoginAPIView.as_view(), name="api_login"),
    path("auth/logout/", LogoutAPIView.as_view(), name="api_logout"),
    path("auth/token/refresh/", CookieTokenRefreshView.as_view(), name="api_token_refresh"),
    path("auth/profile/", ProfileAPIView.as_view(), name="api_profile"),
    path("users/", UserListCreateAPIView.as_view(), name="api_user_list"),
    path("users/<int:pk>/", UserDetailAPIView.as_view(), name="api_user_detail"),
]
