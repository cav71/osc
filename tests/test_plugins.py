import os
import osc.core
import osc.plugins


import unittest

FIXTURES_DIR = os.path.join(os.getcwd(), os.environ.get('FIXTURES_DIR', ''), 'plugins_fixtures')


def suite():
    return unittest.makeSuite(TestPackageStatus)


class TestModule(unittest.TestCase):
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
        found = osc.plugins.load_from_source(filename, modname='simple4', inject={ 'unittest' : unittest })
        self.assertEquals(sorted(found.keys()), 
            [ 'hello', 'os', 'path', 'unittest', ])


if __name__ == '__main__':
    import unittest
    unittest.main()
