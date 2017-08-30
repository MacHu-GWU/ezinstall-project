.. image:: https://travis-ci.org/MacHu-GWU/ezinstall-project.svg?branch=master

.. image:: https://img.shields.io/pypi/v/ezinstall.svg

.. image:: https://img.shields.io/pypi/l/ezinstall.svg

.. image:: https://img.shields.io/pypi/pyversions/ezinstall.svg


Welcome to ezinstall Documentation
===========================================
``ezinstall (Easy install)`` is a package allows you to instantly install
package to your python environment **without having** ``setup.py`` file.
It simply copy the source code to ``site-packages`` directory.
**It also works for virtualenv**. The behavior is exactly the same as
``pip install setup.py --ignore-installed``.

It doesn't install any dependencies from ``requirement.txt``.

**Note**: It ONLY works for **directory styled** package.

**Usage**:

Create a ``zzz_ezinstall.py`` file (or use any other filename you like), and
put it next to ``package_dir/__init__.py``, which is ``package_dir/zzz_ezinstall.py``.

.. code-block:: python

    #!/usr/bin/env python
    # -*- coding: utf-8 -*-

    if __name__ == "__main__":
        import os
        from ezinstall import install

        install(os.path.dirname(__file__))


**Quick Links**
---------------
- `GitHub Homepage <https://github.com/MacHu-GWU/ezinstall-project>`_
- `Online Documentation <http://www.wbh-doc.com.s3.amazonaws.com/ezinstall/index.html>`_
- `PyPI download <https://pypi.python.org/pypi/ezinstall>`_
- `Install <install_>`_
- `Issue submit and feature request <https://github.com/MacHu-GWU/ezinstall-project/issues>`_
- `API reference and source code <http://www.wbh-doc.com.s3.amazonaws.com/ezinstall/py-modindex.html>`_


.. _install:

Install
-------

``ezinstall`` is released on PyPI, so all you need is:

.. code-block:: console

	$ pip install ezinstall

To upgrade to latest version:

.. code-block:: console

	$ pip install --upgrade ezinstall