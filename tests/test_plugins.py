import os
import osc.core
import osc.plugins


import unittest

FIXTURES_DIR = os.path.join(os.getcwd(), os.environ.get('FIXTURES_DIR', ''), 'plugins_fixtures')


def suite():
    return unittest.makeSuite(TestPackageStatus)


class TestFromSource(unittest.TestCase):
    def test_load_from_source(self):
        filename = os.path.join(FIXTURES_DIR, 'simple.py')

# simple
        found = osc.plugins.load_from_source(filename)
        self.assertEquals(sorted(found.keys()), 
            [ 'hello', 'os', 'path', ])

# simple2
        found = osc.plugins.load_from_source(filename, modname='simple2', inject={ 'unittest' : unittest })
        self.assertEquals(sorted(found.keys()), 
            [ 'hello', 'os', 'path', 'unittest', ])
    
    def test_load_from_source_compiled(self):
        filename = os.path.join(FIXTURES_DIR, 'simple.compiled')

# simple3
        found = osc.plugins.load_from_source(filename, modname='simple3')
        self.assertEquals(sorted(found.keys()), 
            [ 'hello', 'os', 'path', ])

# simple4
        found = osc.plugins.load_from_source(filename, modname='simple4', 
                    inject={ 'unittest' : unittest })
        self.assertEquals(sorted(found.keys()), 
            [ 'hello', 'os', 'path', 'unittest', ])


class TestFromDir(unittest.TestCase):
    def test_load_fromdir(self):
        py_dir = os.path.join(FIXTURES_DIR, 'inadir')

# simple5
        found = osc.plugins.load_from_dir(py_dir, modname='simple5')
        self.assertEquals(sorted(found.keys()), 
            [ 'hello2', 'os', 'path', 'wow', ])
        
# simple6
        found = osc.plugins.load_from_dir(py_dir, modname='simple6', 
                inject={ 'unittest' : unittest })
        self.assertEquals(sorted(found.keys()), 
            [ 'hello2', 'os', 'path', 'unittest', 'wow', ])

    def test_load_fromdir_with_jinja(self):

        py_dir = os.path.join(FIXTURES_DIR, 'plugin.with.jinja')

# simple7
        found = osc.plugins.load_from_dir(py_dir, modname='simple7')
        self.assertEquals(sorted(found.keys()), 
            [ 'test0', 'test1', 'test2', ])
        self.assertMultiLineEqual(found['test0']('World'),'''
Hello from the base

Simple example, you passed name=World
''')

        self.assertMultiLineEqual(found['test1']('World'),'''
Hello from the base


This block from base

Simple example, you passed name=World
''')

        self.assertMultiLineEqual(found['test2']('World'),'''
Hello from the base


This block from base

This block from example where you gave the name=World
'''.lstrip())


class TestFromZip(unittest.TestCase):
    def test_from_zip(self):
        zip_filename = os.path.join(FIXTURES_DIR, 'plugin.with.jinja.zip')

# simple8
        found = osc.plugins.load_from_zipfile(zip_filename, modname='simple8')
        print found


if __name__ == '__main__':
    import unittest
    unittest.main()
