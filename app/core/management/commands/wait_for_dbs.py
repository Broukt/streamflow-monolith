"""Django command to wait for the configured databases to be available."""

import time
from psycopg import OperationalError as PsycopgOperationalError
from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError
from pymongo.errors import PyMongoError


DATABASE_ALIASES = ["auth", "users", "videos", "billing"]


class Command(BaseCommand):
    """Django command to wait for the database to be available."""

    def handle(self, *args, **options):
        """Entrypoint for command.

        Args:
            *args: Variable length argument list.
            **options: Arbitrary keyword arguments.
        """
        self.stdout.write("Waiting for database...")
        for alias in DATABASE_ALIASES:
            db_ready = False
            while not db_ready:
                try:
                    connections[alias].ensure_connection()
                    db_ready = True
                except (PsycopgOperationalError,
                        OperationalError,
                        PyMongoError):
                    self.stdout.write(
                        f"Database {alias} unavailable, waiting 1 second..."
                    )
                    time.sleep(1)
            self.stdout.write(self.style.SUCCESS(
                f"Database {alias} available!"
                ))
