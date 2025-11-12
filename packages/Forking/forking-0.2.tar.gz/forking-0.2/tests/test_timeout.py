"""Tests for the forking's timeout."""

import time

from forking import Forking

forking = Forking(timeout=0.5)


def test_simple_timeout():
    before = time.perf_counter()
    with forking:
        time.sleep(10)
    after = time.perf_counter()
    assert (after - before) < 2
    assert forking.exit.signal == 9


def test_write_before_timeout():
    before = time.perf_counter()
    with forking:
        print("Coucou")
        time.sleep(10)
    after = time.perf_counter()
    assert (after - before) < 2
    assert forking.exit.signal == 9
    assert forking.stdout == b"Coucou\n"


def test_write_after_timeout():
    before = time.perf_counter()
    with forking:
        time.sleep(10)
        print("Coucou")
    after = time.perf_counter()
    assert (after - before) < 2
    assert forking.exit.signal == 9
    assert forking.stdout == b""
