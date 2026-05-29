from django.urls import include, path

from application.views import (
    CompleteProfileView,
    DashboardView,
    LoginView,
    LogoutView,
    SettingsView,
    UserDetailView,
    UserListView,
)

urlpatterns = [
    path("", LoginView.as_view(), name="home"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("complete-profile/", CompleteProfileView.as_view(), name="complete_profile"),
    path("settings/", SettingsView.as_view(), name="settings"),
    path("users/", UserListView.as_view(), name="user_list"),
    path("users/<int:pk>/", UserDetailView.as_view(), name="user_detail"),
    path("products/", include("products.urls")),
]
