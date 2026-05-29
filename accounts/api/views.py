from django.contrib.auth import authenticate
from django.conf import settings
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.views import TokenRefreshView

from accounts.jwt_utils import clear_jwt_cookies, get_tokens_for_user, set_jwt_cookies
from accounts.models import User
from accounts.querysets import application_users
from accounts.permissions import SuperAdminManager
from accounts.serializers import (
    LoginSerializer,
    ProfileCompleteSerializer,
    SelfProfileUpdateSerializer,
    UserCreateSerializer,
    UserSerializer,
    UserUpdateSerializer,
)


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        person_id = serializer.validated_data["personID"]
        password = serializer.validated_data["password"]
        from accounts.models import User as AppUser

        person_id = person_id.strip()
        try:
            candidate = AppUser.objects.get(personID__iexact=person_id)
            if not candidate.is_active:
                return Response(
                    {"detail": "This account is deactivated."},
                    status=status.HTTP_403_FORBIDDEN,
                )
        except AppUser.DoesNotExist:
            pass

        user = authenticate(
            request,
            personID=person_id,
            password=password,
        )
        if user is None:
            return Response(
                {"detail": "Invalid person ID or password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        tokens = get_tokens_for_user(user)
        response = Response(
            {
                "user": UserSerializer(user, context={"request": request}).data,
                "redirect": "/complete-profile/"
                if not user.is_profile_completed
                else "/dashboard/",
            },
            status=status.HTTP_200_OK,
        )
        return set_jwt_cookies(response, tokens)


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        response = Response({"detail": "Logged out successfully."})
        return clear_jwt_cookies(response)


class CookieTokenRefreshView(TokenRefreshView):
    """Refresh access token using refresh token from httpOnly cookie."""

    def post(self, request, *args, **kwargs):
        refresh = request.data.get("refresh") or request.COOKIES.get(
            settings.JWT_REFRESH_COOKIE
        )
        if not refresh:
            return Response(
                {"detail": "Refresh token not provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = TokenRefreshSerializer(data={"refresh": refresh})
        serializer.is_valid(raise_exception=True)
        access = serializer.validated_data["access"]
        response = Response({"access": access})
        return set_jwt_cookies(
            response,
            {"access": access, "refresh": refresh},
        )


class ProfileAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            if self.request.user.is_profile_completed:
                return SelfProfileUpdateSerializer
            return ProfileCompleteSerializer
        return UserSerializer

    def retrieve(self, request, *args, **kwargs):
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(serializer.data)


class UserListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [SuperAdminManager]

    def get_queryset(self):
        return application_users()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return UserCreateSerializer
        return UserSerializer


class UserDetailAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = [SuperAdminManager]
    queryset = application_users()
    lookup_field = "pk"

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return UserUpdateSerializer
        return UserSerializer
