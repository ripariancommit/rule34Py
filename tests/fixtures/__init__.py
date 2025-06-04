"""A package of test fixtures that might be shared between unit, integration, and system tests.
"""
import pytest

from rule34Py import rule34Py

from .mock34 import mock34


@pytest.fixture(scope="module")
def rule34(mock34):
    """A rule34Py client instance.
    """
    r34 = rule34Py()
    yield r34
