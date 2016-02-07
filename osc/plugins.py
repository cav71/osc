# Copyright (C) 2016 CCLimited Ltd.  All rights reserved.
# This program is free software; it may be used, copied, modified
# and distributed under the terms of the GNU General Public Licence,
# either version 2, or version 3 (at your option).

from __future__ import print_function

import os
import imp
import inspect


def is_compiled(py_filename):
    with open(py_filename, 'rb') as fp:
        return fp.read(len(imp.get_magic())) == imp.get_magic()


def load_from_source(py_filename, modname=None, inject=None, include_modules=True):
    root, ext = os.path.splitext(py_filename)
    modname = modname or os.path.basename(root)

    if is_compiled(py_filename):
        mod = imp.load_compiled(modname, py_filename)
    else:
        mod = imp.load_source(modname, py_filename)

    if inject:
        mod.__dict__.update(inject)   

    result = {}
    for name in dir(mod):
        data = getattr(mod, name)
        include = False
        if include_modules and inspect.ismodule(data):
            include = True
        if inspect.isfunction(data) and inspect.getmodule(data) == mod:
            include = True
        if include:
            result[name] = data

    return result
