from django.contrib.auth.backends import ModelBackend

from .models import User


class PersonIDBackend(ModelBackend):
    """Authenticate application users with personID and password."""

    def authenticate(self, request, personID=None, password=None, **kwargs):
        if personID is None or password is None:
            return None
        person_id = str(personID).strip()
        if not person_id:
            return None
        try:
            user = User.objects.get(personID__iexact=person_id)
        except User.DoesNotExist:
            return None
        if not user.check_password(password):
            return None
        if not self.user_can_authenticate(user):
            return None
        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
