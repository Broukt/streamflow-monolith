"""Test custom Django management commands."""

from unittest.mock import MagicMock, patch
from psycopg import OperationalError as PsycopgOperationalError
from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import SimpleTestCase

from core.management.commands.wait_for_dbs import DATABASE_ALIASES


class CommandTests(SimpleTestCase):
    """Tests for the wait_for_dbs management command."""

    def _setup_connection_mocks(self, patched_connections):
        """Create per-alias connection mocks backed by the patched handler."""

        connection_mocks = {
            alias: MagicMock(name=f"{alias}_connection") for alias in DATABASE_ALIASES
        }
        patched_connections.__getitem__.side_effect = connection_mocks.__getitem__
        return connection_mocks

    @patch("core.management.commands.wait_for_dbs.connections")
    def test_wait_for_dbs_ready(self, patched_connections):
        """Command exits once each database connection succeeds."""

        connection_mocks = self._setup_connection_mocks(patched_connections)
        call_command("wait_for_dbs")

        for connection in connection_mocks.values():
            connection.ensure_connection.assert_called_once_with()

    @patch("time.sleep", return_value=None)
    @patch("core.management.commands.wait_for_dbs.connections")
    def test_wait_for_dbs_delay(self, patched_connections, patched_sleep):
        """Command retries until the database becomes available."""

        connection_mocks = self._setup_connection_mocks(patched_connections)
        connection_mocks["auth"].ensure_connection.side_effect = [
            PsycopgOperationalError("pg down"),
            PsycopgOperationalError("pg still down"),
            OperationalError("db starting"),
            OperationalError("db starting 2"),
            OperationalError("db starting 3"),
            None,
        ]

        call_command("wait_for_dbs")

        self.assertEqual(connection_mocks["auth"].ensure_connection.call_count, 6)
        for alias in [alias for alias in DATABASE_ALIASES if alias != "auth"]:
            connection_mocks[alias].ensure_connection.assert_called_once_with()

        self.assertEqual(patched_sleep.call_count, 5)
