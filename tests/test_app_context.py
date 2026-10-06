"""Application initialization behavior."""
from unittest import TestCase
from flask import has_app_context
from service import app


class TestApplicationContext(TestCase):
    """The service must not retain a process-wide request database session."""

    def test_database_initialization_does_not_leak_an_app_context(self):
        """Flask creates and tears down a context for each request."""
        self.assertIsNotNone(app)
        self.assertFalse(has_app_context())
