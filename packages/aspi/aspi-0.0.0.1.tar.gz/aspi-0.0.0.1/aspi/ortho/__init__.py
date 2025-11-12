#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:copyright:
    Yangkang Chen (chenyk2016@gmail.com), 2021-2022   
"""
# import collections
import logging

class PyorthoError(Exception):
    """
    Base class for all Pyortho exceptions. Will probably be used for all
    exceptions to not overcomplicate things as the whole package is pretty
    small.
    """
    pass


class PyorthoWarning(UserWarning):
    """
    Base class for all Pyortho warnings.
    """
    pass


# Setup the logger.
logger = logging.getLogger("Pyortho")
logger.setLevel(logging.WARNING)
# Prevent propagating to higher loggers.
logger.propagate = 0
# Console log handler.
ch = logging.StreamHandler()
# Add formatter
FORMAT = "[%(asctime)s] - %(name)s - %(levelname)s: %(message)s"
formatter = logging.Formatter(FORMAT)
ch.setFormatter(formatter)
logger.addHandler(ch)

from .localortho import localortho
from .localortho import localorthoc
from .localsimi import localsimi
from .localsimi import localsimic
from .focus import focus
from .divne import divne
from .drr3d import drr3d













