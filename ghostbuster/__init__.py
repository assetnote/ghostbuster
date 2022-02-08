#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Eliminate dangling elastic IPs by performing analysis on your resources within all your AWS accounts.

.. currentmodule:: ghostbuster
.. moduleauthor:: shubham_shah <sshah@assetnote.io>
"""

from .version import __version__, __release__  # noqa
import click


class Info(object):
    """An information object to pass data between CLI functions."""

    def __init__(self):  # Note: This object must have an empty constructor.
        """Create a new instance."""
        self.verbose: int = 0
        self.apikey: str = ""
        self.instance: str = ""


# pass_info is a decorator for functions that pass 'Info' objects.
#: pylint: disable=invalid-name
pass_info = click.make_pass_decorator(Info, ensure=True)
