import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create the first CMS administrator from environment variables."

    def add_arguments(self, parser):
        parser.add_argument(
            "--if-configured",
            action="store_true",
            help="Skip cleanly when administrator variables are absent.",
        )

    def handle(self, *args, **options):
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
        if not username or not email or not password:
            if options["if_configured"]:
                self.stdout.write(
                    "Administrator variables are not fully configured; "
                    "administrator creation skipped."
                )
                return
            raise CommandError(
                "Set DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL and "
                "DJANGO_SUPERUSER_PASSWORD first."
            )
        user_model = get_user_model()
        if user_model.objects.filter(username=username).exists():
            self.stdout.write("Administrator already exists; no change made.")
            return
        user_model.objects.create_superuser(username, email, password)
        self.stdout.write(self.style.SUCCESS("Administrator created."))
