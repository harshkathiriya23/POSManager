from django.core.management.base import BaseCommand

from accounts.models import User


class Command(BaseCommand):
    help = (
        "Create or reset the application SuperAdmin login (personID + password). "
        "Django /admin/ uses createsuperuser separately."
    )

    def add_arguments(self, parser):
        parser.add_argument("--personID", default="SA001")
        parser.add_argument("--password", default="Admin@123")
        parser.add_argument("--name", default="Super Admin")
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Reset password and re-activate user if personID already exists.",
        )

    def handle(self, *args, **options):
        person_id = options["personID"].strip()
        password = options["password"]
        name = options["name"]

        try:
            user = User.objects.get(personID=person_id)
            if not options["reset"]:
                self.stdout.write(
                    self.style.WARNING(
                        f"User {person_id} already exists. "
                        f"Active={user.is_active}. "
                        f"Run: python manage.py bootstrap_superadmin --reset"
                    )
                )
                return
            user.set_password(password)
            user.is_active = True
            user.is_staff = True
            user.role = "superadmin"
            if name:
                user.name = name
            user.save()
            self.stdout.write(
                self.style.SUCCESS(
                    f"SuperAdmin {person_id} reset: password updated, account activated."
                )
            )
            return
        except User.DoesNotExist:
            pass

        user = User(
            personID=person_id,
            username=person_id,
            name=name,
            role="superadmin",
            is_staff=True,
            is_superuser=False,
            is_active=True,
            is_profile_completed=False,
        )
        user.set_password(password)
        user.save()
        self.stdout.write(
            self.style.SUCCESS(
                f"SuperAdmin created: personID={person_id} / password={password} "
                f"(complete profile on first login)."
            )
        )
