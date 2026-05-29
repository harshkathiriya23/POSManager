from accounts.models import User


def application_users():
    """App-managed users only (excludes Django /admin/ superuser accounts)."""
    return User.objects.filter(is_superuser=False)
