#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
``ezinstall (Easy install)`` is a package allows you to instantly install
package to your python environment, by simply copy the source code to
``site-packages`` directory. **It install to virtual environment** when 
inside a virtual environment.

Compared to ``pip install setup.py``, its fast!
"""

__version__ = "0.0.1"
__short_description__ = "Instantly install your package to site-packages."
__license__ = "MIT"
__author__ = "Sanhe Hu"
__author_email__ = "husanhe@me.com"
__maintainer__ = "Sanhe Hu"
__maintainer_email__ = "husanhe@me.com"
__github_username__ = "MacHu-GWU"

from .ezinstall import install
