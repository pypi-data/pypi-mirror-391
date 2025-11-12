"""Test the exception_hook method of Forking."""

import friendly_traceback

from forking import Forking


def test_without_friendly():
    forking = Forking()
    with forking:
        print(1 / 0)
    assert b"ZeroDivision" in forking.stderr


def test_with_friendly():
    forking = Forking()
    forking.exception_hook = friendly_traceback.session.exception_hook
    with forking:
        print(1 / 0)
    assert b"You are dividing by zero." in forking.stderr


def test_with_friendly_subclassing():
    class MyForking(Forking):
        """A Forking class that use Friendly Traceback"""

        def exception_hook(self, exc_type, exc_value, tb):
            friendly_traceback.session.exception_hook(exc_type, exc_value, tb)

    forking = MyForking()
    with forking:
        print(1 / 0)
    assert b"You are dividing by zero." in forking.stderr
