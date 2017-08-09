#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
``ezinstall (Easy install)`` is a package allows you to instantly install
package to your python environment, by simply copy the source code to
``site-packages`` directory. **It install to virtual environment** when 
inside a virtual environment.

Compared to ``pip install setup.py``, its fast!

-------------------------------------------------------------------------------

Copyright (c) 2014-2017 Sanhe Hu

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from __future__ import print_function, unicode_literals
import os
from os.path import (
    isabs, join, abspath, dirname, basename, split, splitext,
    isfile, isdir, exists,
)
import shutil
import hashlib
import sys
import site
import platform


#--- Operation System ---
class OperationSystem(object):
    activate_script = None
    executable_python = None
    executable_pip = None
    venv_site_packages = None

    @classmethod
    def get_site_packages(cls):
        """
        Get system ``site-packages`` path.
        """
        raise NotImplementedError

    @classmethod
    def get_venv_site_packages(cls, venv_path):
        """
        Get virtual environment ``site-packages`` path.
        """
        return join(venv_path, cls.venv_site_packages)


class Windows(OperationSystem):
    script_dir = "Scripts"
    activate_script = r"%s\activate.bat" % script_dir
    executable_python = r"%s\python.exe" % script_dir
    executable_pip = r"%s\pip.exe" % script_dir
    venv_site_packages = r"Lib\site-packages"

    @classmethod
    def get_site_packages(cls):
        """
        Get system ``site-packages`` path.
        """
        try:
            return site.getsitepackages()[1]
        except AttributeError:
            return None


class MacOS(OperationSystem):
    script_dir = "bin"
    activate_script = "%s/activate" % script_dir
    executable_python = "%s/python" % script_dir
    executable_pip = "%s/pip" % script_dir
    venv_site_packages = "lib/python%s.%s/site-packages" % (
        sys.version_info.major, sys.version_info.minor,
    )

    @classmethod
    def get_site_packages(cls):
        """
        Get system ``site-packages`` path.
        """
        try:
            return site.getsitepackages()[0]
        except AttributeError:
            return None


class Linux(MacOS):
    pass


system = None
is_posix = None

system_name = platform.system()
if system_name == "Windows":
    system = Windows
    is_posix = False
elif system_name == "Darwin":
    system = MacOS
    is_posix = True
elif system_name == "Linux":
    system = Linux
    is_posix = True
else:
    raise Exception("Unknown Operation System!")


#--- Path ---
class Path(object):
    """Represent a path.
    """

    def __init__(self, path, *parts):
        path = str(path)
        parts = [str(part) for part in parts]
        self.abspath = join(path, *parts)

    def __repr__(self):
        return self.abspath

    def is_absolute(self):
        """
        Test if it's an absolute path.
        """
        return isabs(self.abspath)

    def absolute(self):
        """
        Return absolute version of this path.
        """
        if self.is_absolute():
            return self
        else:
            return self.__class__(abspath(self.abspath))

    def exists(self):
        return exists(self.abspath)

    @property
    def basename(self):
        """
        ``/usr/bin/test.txt`` -> ``test.txt``
        """
        return basename(self.abspath)

    @property
    def ext(self):
        """
        ``/usr/bin/test.txt`` -> ``.txt``
        """
        return splitext(self.basename)[1]

    @property
    def fname(self):
        """
        ``/usr/bin/test.txt`` -> ``test``
        """
        return splitext(self.basename)[0]

    @property
    def dirname(self):
        """
        ``/usr/bin/test.txt`` -> ``bin``
        """
        return basename(self.dirpath)

    @property
    def dirpath(self):
        """
        ``/usr/bin/test.txt`` -> ``/usr/bin``
        """
        return dirname(self.abspath)

    @property
    def parent(self):
        """
        Parent directory.
        """
        return self.__class__(self.dirpath)

    @property
    def parts(self):
        """
        - ``/usr/bin/test.txt`` -> ["/", "usr", "bin", "test.txt]
        - ``C:\\User\\admin\\test.txt`` -> ["C:\\", "User", "admin", "test.txt"]
        """
        if is_posix:
            l = [part for part in self.abspath.split("/") if part]
            if self.absolute():
                l = ["/", ] + l
        else:
            l = self.abspath.split("\\")
            if l[0].endswith(":"):
                l[0] = l[0] + "\\"
        return l

    def path_chain(self):
        """
        """
        path_list = [self, ]
        p = self
        for i in range(len(self.parts) - 1):
            p = p.parent
            path_list.append(p)
        return path_list

    def __eq__(self, other):
        return self.abspath == other.abspath


def is_virtualenv(dirpath):
    """
    Test if a directory is a virtual environment. By checking if all of these
    file exists::

        - dirpath/<path-to-activate-script>
        - dirpath/<path-to-executable-python>
        - dirpath/<path-to-executable-pip>
    """
    check_list = [
        system.activate_script,
        system.executable_python,
        system.executable_pip,
    ]

    for relpath in check_list:
        p = Path(dirpath, relpath)
        if not p.exists():
            return False

    return True


def is_in_virtualen(filepath):
    """
    Test if a file is in virtual environment. By test that any of its parent 
    directory is virtual environment.
    """
    dirpath = Path(filepath).absolute().parent

    dirpath_list = [dirpath, ]
    p = dirpath
    for i in range(len(dirpath.parts) - 1):
        p = p.parent
        dirpath_list.append(p)

    for dirpath in dirpath_list:
        if is_virtualenv(dirpath):
            return True, dirpath.abspath
    return False, None


def remove_pyc_file(package_dirpath):
    """
    Remove all ``__pycache__`` folder and ``.pyc`` file from a directory.
    """
    pyc_folder_list = list()
    pyc_file_list = list()

    for root, _, basename_list in os.walk(package_dirpath):
        if os.path.basename(root) == "__pycache__":
            pyc_folder_list.append(root)

        for basename in basename_list:
            if basename.endswith(".pyc"):
                abspath = os.path.join(root, basename)
                pyc_file_list.append(abspath)

    for folder in pyc_folder_list:
        try:
            shutil.rmtree(folder)
        except:
            pass

    for abspath in pyc_file_list:
        try:
            os.remove(abspath)
        except:
            pass


def md5_of_file(abspath):
    """
    Md5 value of a file.
    """
    chunk_size = 1024 * 1024
    m = hashlib.md5()
    with open(abspath, "rb") as f:
        while True:
            data = f.read(chunk_size)
            if not data:
                break
            m.update(data)
    return m.hexdigest()


def check_need_install(src, dst):
    """
    Check if installed package are exactly the same to this one.
    By checking md5 value of all files.
    """
    for root, _, basename_list in os.walk(src):
        if basename(root) != "__pycache__":
            for file_basename in basename_list:
                if not file_basename.endswith(".pyc"):
                    before = join(root, file_basename)
                    after = join(root.replace(src, dst), file_basename)
                    if exists(after):
                        if md5_of_file(before) != md5_of_file(after):
                            return True
                    else:
                        return True
    return False


class Printer(object):
    """
    Simple printer to support ``enable_verbose`` argument.
    """
    verbose = True

    @classmethod
    def log(cls, message):
        if cls.verbose:
            print(message)


def install(path, verbose=True):
    """Easy install main script.

    Create a ``zzz_ezinstall.py`` file, and put in your package folder (Next to
    the ``__init__.py`` file), and put following content::

        # content of zzz_ezinstall.py

        if __name__ == "__main__":
            from ezinstall import install

            install(__file__)

    """
    if verbose:
        Printer.verbose = True
    else:
        Printer.verbose = False

    # locate source directory
    p = Path(path).absolute().parent

    package_name = p.basename
    src = p.abspath

    # locate destination directory
    flag, venv_path = is_in_virtualen(path)
    if flag:
        site_packages_path = system.get_venv_site_packages(venv_path)
    else:
        site_packages_path = system.get_site_packages()
    dst = join(site_packages_path, package_name)

    # See if needs to install
    Printer.log("Compare to '%s' ..." % dst)
    need_install_flag = check_need_install(src, dst)
    if not need_install_flag:
        Printer.log("    package is up-to-date, no need to install.")
        return
    Printer.log("    Difference been found, start installing ...")

    # remove __pycache__ folder and *.pyc file
    Printer.log("Remove *.pyc file ...")
    try:
        remove_pyc_file(src)
        Printer.log("    Success! all *.pyc file has been removed.")
    except Exception as e:
        Printer.log("    Faield! %r" % e)

    Printer.log("Remove installed '%s' from '%s' ..." % (package_name, dst))
    if exists(dst):
        try:
            shutil.rmtree(dst)
            Printer.log("    Success!")
        except Exception as e:
            Printer.log("    Faield! %r" % e)

    # Copy source code to site-packages
    Printer.log("Install '%s' to '%s' ..." % (package_name, dst))
    try:
        shutil.copytree(src, dst)
        Printer.log("    Complete!")
    except Exception as e:
        Printer.log("    Failed! %r" % e)


if __name__ == "__main__":
    install(__file__)
