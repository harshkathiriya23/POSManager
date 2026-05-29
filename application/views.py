from django.contrib import messages
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import ListView, TemplateView

from accounts.jwt_utils import clear_jwt_cookies, get_tokens_for_user, set_jwt_cookies
from accounts.models import User
from accounts.querysets import application_users
from accounts.serializers import (
    ProfileCompleteSerializer,
    SelfProfileUpdateSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
)
from application.mixins import JWTLoginRequiredMixin, SuperAdminRequiredMixin


class LoginView(View):
    template_name = "auth/login.html"

    def get(self, request):
        if request.user.is_authenticated:
            if not request.user.is_profile_completed:
                return redirect("complete_profile")
            return redirect("dashboard")
        return render(request, self.template_name)

    def post(self, request):
        person_id = request.POST.get("personID", "").strip()
        password = request.POST.get("password", "")

        try:
            candidate = User.objects.get(personID__iexact=person_id)
            if not candidate.is_active:
                messages.error(
                    request,
                    "This account is deactivated. Contact your SuperAdmin or use Django admin to activate it.",
                )
                return render(request, self.template_name)
            if not candidate.check_password(password):
                messages.error(request, "Invalid Person ID or password.")
                return render(request, self.template_name)
        except User.DoesNotExist:
            pass

        user = authenticate(request, personID=person_id, password=password)
        if user is None:
            messages.error(request, "Invalid Person ID or password.")
            return render(request, self.template_name)
        tokens = get_tokens_for_user(user)
        response = redirect(
            "complete_profile" if not user.is_profile_completed else "dashboard"
        )
        return set_jwt_cookies(response, tokens)


class LogoutView(JWTLoginRequiredMixin, View):
    def get(self, request):
        response = redirect("login")
        return clear_jwt_cookies(response)


class DashboardView(JWTLoginRequiredMixin, TemplateView):
    template_name = "dashboard/index.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = "Dashboard"
        ctx["role_label"] = self.request.user.get_role_display()
        return ctx


class CompleteProfileView(JWTLoginRequiredMixin, View):
    template_name = "profile/complete.html"

    def get(self, request):
        if request.user.is_profile_completed:
            return redirect("dashboard")
        return render(request, self.template_name, {"user": request.user})

    def post(self, request):
        if request.user.is_profile_completed:
            return redirect("dashboard")
        serializer = ProfileCompleteSerializer(
            request.user,
            data=request.POST,
            partial=True,
        )
        if serializer.is_valid():
            user = serializer.save()
            if "profile_picture" in request.FILES:
                user.profile_picture = request.FILES["profile_picture"]
                user.save(update_fields=["profile_picture"])
            messages.success(request, "Profile completed successfully.")
            return redirect("dashboard")
        return render(
            request,
            self.template_name,
            {"user": request.user, "errors": serializer.errors},
        )


class SettingsView(JWTLoginRequiredMixin, View):
    template_name = "settings/index.html"

    def get(self, request):
        return render(
            request,
            self.template_name,
            {"page_title": "Profile", "form_errors": {}},
        )

    def post(self, request):
        serializer = SelfProfileUpdateSerializer(
            request.user,
            data=request.POST,
            partial=True,
            context={"request": request},
        )
        if serializer.is_valid():
            user = serializer.save()
            if "profile_picture" in request.FILES:
                user.profile_picture = request.FILES["profile_picture"]
                user.save(update_fields=["profile_picture"])
            messages.success(request, "Profile updated successfully.")
            return redirect("settings")
        return render(
            request,
            self.template_name,
            {"page_title": "Profile", "form_errors": serializer.errors},
        )


class UserListView(SuperAdminRequiredMixin, ListView):
    model = User
    template_name = "users/list.html"
    context_object_name = "users"

    def get_queryset(self):
        return application_users().order_by("personID")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        qs = self.get_queryset()
        ctx["page_title"] = "User Management"
        ctx["superadmin_users"] = qs.filter(role="superadmin")
        ctx["admin_users"] = qs.filter(role="admin")
        ctx["salesperson_users"] = qs.filter(role="salesperson")
        ctx["role_choices"] = User.ROLE_CHOICES
        ctx.setdefault("show_add_modal", False)
        ctx.setdefault("form_errors", {})
        ctx.setdefault("form_data", {})
        return ctx

    def post(self, request, *args, **kwargs):
        serializer = UserCreateSerializer(data=request.POST)
        if serializer.is_valid():
            serializer.save()
            messages.success(request, "User created successfully.")
            return redirect("user_list")

        self.object_list = self.get_queryset()
        context = self.get_context_data(
            show_add_modal=True,
            form_errors=serializer.errors,
            form_data=request.POST,
        )
        return self.render_to_response(context)


class UserDetailView(SuperAdminRequiredMixin, View):
    template_name = "users/detail.html"

    def get_user(self, pk):
        return get_object_or_404(application_users(), pk=pk)

    def get_context(self, profile_user, form_errors=None):
        return {
            "profile_user": profile_user,
            "page_title": "Edit User",
            "role_choices": User.ROLE_CHOICES,
            "form_errors": form_errors or {},
            "is_self": profile_user.pk == self.request.user.pk,
        }

    def get(self, request, pk):
        return render(request, self.template_name, self.get_context(self.get_user(pk)))

    def post(self, request, pk):
        profile_user = self.get_user(pk)
        data = request.POST.copy()
        data["is_active"] = request.POST.get("is_active") == "true"

        serializer = UserUpdateSerializer(
            profile_user,
            data=data,
            partial=True,
            context={"request": request},
        )
        if serializer.is_valid():
            user = serializer.save()
            if "profile_picture" in request.FILES:
                user.profile_picture = request.FILES["profile_picture"]
                user.save(update_fields=["profile_picture"])
            status_msg = (
                "User updated and deactivated successfully."
                if not user.is_active
                else "User updated successfully."
            )
            messages.success(request, status_msg)
            return redirect("user_detail", pk=pk)

        return render(
            request,
            self.template_name,
            self.get_context(profile_user, form_errors=serializer.errors),
        )
