#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. currentmodule:: test_example
.. moduleauthor:: shubham_shah <sshah@assetnote.io>

This is a sample test module.
"""

import pytest

"""
This is just an example test suite.  It will check the current project version
numbers against the original version numbers and will start failing as soon as
the current version numbers change.
"""


def test_import_getVersions_originalVersions():
    """
    Arrange: Load the primary module.
    Act: Retrieve the versions.
    Assert: Versions match the version numbers at the time of project creation.
    """
    assert (
        # fmt: off
        # '0.0.1' == ghostbuster.__version__,
        # fmt: on
        "This test is expected to fail when the version increments. "
        "It is here only as an example and you can remove it."
    )

    """
    This is just an example test suite that demonstrates the very useful
    `parameterized` module.  It contains a test in which the squares of the
    first two parameters are added together and passes if that sum equals the
    third parameter.
    """


@pytest.mark.parametrize("a,b,c", [(1, 2, 5), (3, 4, 25)])
def test_ab_addSquares_equalsC(a, b, c):
    """
    Arrange: Acquire the first two parameters (a and b).
    Act: Add the squares of the first two parameters (a and b).
    Assert: The sum of the squares equals the third parameter (c).

    :param a: the first parameter
    :param b: the second parameter
    :param c: the result of adding the squares of a and b
    """
    assert (
        a * a + b * b == c,
        "'c' should be the sum of the squares of 'a' and 'b'. "
        "This is an example test and can be removed.",
    )
