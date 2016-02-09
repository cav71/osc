# Copyright (C) 2016 CCLimited Ltd.  All rights reserved.
# This program is free software; it may be used, copied, modified
# and distributed under the terms of the GNU General Public Licence,
# either version 2, or version 3 (at your option).

from __future__ import print_function

import os
import sys
import path
import imp
import inspect
import contextlib
import zipimport
import zipfile


try:
    import jinja2
except ImportError:
    jinja2 = None


def is_compiled(py_filename):
    with open(py_filename, 'rb') as fp:
        return fp.read(len(imp.get_magic())) == imp.get_magic()


@contextlib.contextmanager
def setpath(wdir):
    osys = sys.path[:]
    sys.path.insert(0, wdir)        
    yield
    sys.path = osys


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


def load_from_dir(py_dir, modname=None, inject=None, include_modules=True, main='main.py'):
    modname = modname or os.path.basename(py_dir)
    py_filename = os.path.join(py_dir, main)
    inject = inject or {}

    # adds support for jinja templating in a plugin
    if jinja2 and not 'jenv' in inject:
        loader = jinja2.FileSystemLoader([ os.path.join(py_dir, 'templates'), ])
        # We can add more to the jinja env..
        inject['jenv'] = jinja2.Environment(loader=loader)

    with setpath(py_dir):
        return load_from_source(py_filename, modname=modname, 
                    inject=inject, include_modules=include_modules)


def load_from_zipfile(zip_filename, modname=None, inject=None, include_modules=True, main='main.py'):

    root, ext = os.path.splitext(zip_filename)
    modname = modname or os.path.basename(root)

    with setpath(zip_filename):
        zfp = zipimport.zipimporter(zip_filename)
        #with zipfile.ZipFile(zip_filename) as zfp:
        #    zfp.printdir()
        #    print(zfp.read('plugin.with.jinja/' + main))
        #print(zfp.get_code('main'))
    

    #py_filename = os.path.join(py_dir, main)
    #if jinja2:
    #    inject = inject or {}
    #return load_from_source(py_filename, modname=modname, inject=inject, include_modules=include_modules)


