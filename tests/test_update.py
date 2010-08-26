import osc.core
import osc.oscerr
import os
import sys
from common import GET, OscTestCase
from xml.etree import cElementTree as ET
FIXTURES_DIR = os.path.join(os.getcwd(), 'update_fixtures')

def suite():
    import unittest
    return unittest.makeSuite(TestUpdate)

class TestUpdate(OscTestCase):
    def _get_fixtures_dir(self):
        return FIXTURES_DIR

    @GET('http://localhost/source/osctest/simple?rev=latest', file='testUpdateNoChanges_files')
    @GET('http://localhost/source/osctest/simple/_meta', file='meta.xml')
    def testUpdateNoChanges(self):
        """update without any changes (the wc is the most recent version)"""
        self._change_to_pkg('simple')
        osc.core.Package('.').update()
        self.assertEqual(sys.stdout.getvalue(), 'At revision 1.\n')

    @GET('http://localhost/source/osctest/simple?rev=2', file='testUpdateNewFile_files')
    @GET('http://localhost/source/osctest/simple/upstream_added?rev=2', file='testUpdateNewFile_upstream_added')
    @GET('http://localhost/source/osctest/simple/_meta', file='meta.xml')
    def testUpdateNewFile(self):
        """a new file was added to the remote package"""
        self._change_to_pkg('simple')
        osc.core.Package('.').update(rev=2)
        exp = 'A    upstream_added\nAt revision 2.\n'
        self.assertEqual(sys.stdout.getvalue(), exp)
        self.__check_digests('testUpdateNewFile_files')

    @GET('http://localhost/source/osctest/simple?rev=2', file='testUpdateNewFileLocalExists_files')
    def testUpdateNewFileLocalExists(self):
        """
        a new file was added to the remote package but the same (unversioned)
        file exists locally
        """
        self._change_to_pkg('simple')
        self.assertRaises(osc.oscerr.PackageFileConflict, osc.core.Package('.').update, rev=2)

    @GET('http://localhost/source/osctest/simple?rev=2', file='testUpdateDeletedFile_files')
    @GET('http://localhost/source/osctest/simple/_meta', file='meta.xml')
    def testUpdateDeletedFile(self):
        """a file was deleted from the remote package"""
        self._change_to_pkg('simple')
        osc.core.Package('.').update(rev=2)
        exp = 'D    foo\nAt revision 2.\n'
        self.assertEqual(sys.stdout.getvalue(), exp)
        self.__check_digests('testUpdateDeletedFile_files')
        self.assertFalse(os.path.exists('foo'))
        self.assertFalse(os.path.exists(os.path.join('.osc', 'foo')))

    @GET('http://localhost/source/osctest/simple?rev=2', file='testUpdateUpstreamModifiedFile_files')
    @GET('http://localhost/source/osctest/simple/foo?rev=2', file='testUpdateUpstreamModifiedFile_foo')
    @GET('http://localhost/source/osctest/simple/_meta', file='meta.xml')
    def testUpdateUpstreamModifiedFile(self):
        """a file was modified in the remote package (local file isn't modified)"""
        
        self._change_to_pkg('simple')
        osc.core.Package('.').update(rev=2)
        exp = 'U    foo\nAt revision 2.\n'
        self.assertEqual(sys.stdout.getvalue(), exp)
        self.__check_digests('testUpdateUpstreamModifiedFile_files')

    @GET('http://localhost/source/osctest/conflict?rev=2', file='testUpdateConflict_files')
    @GET('http://localhost/source/osctest/conflict/merge?rev=2', file='testUpdateConflict_merge')
    @GET('http://localhost/source/osctest/conflict/_meta', file='meta.xml')
    def testUpdateConflict(self):
        """
        a file was modified in the remote package (local file is also modified 
        and a merge isn't possible)
        """
        self._change_to_pkg('conflict')
        osc.core.Package('.').update(rev=2)
        exp = 'C    merge\nAt revision 2.\n'
        self.__check_digests('testUpdateConflict_files')
        self.assertEqual(sys.stdout.getvalue(), exp)
        self._check_conflictlist('merge\n')

    @GET('http://localhost/source/osctest/already_in_conflict?rev=2', file='testUpdateAlreadyInConflict_files')
    @GET('http://localhost/source/osctest/already_in_conflict/merge?rev=2', file='testUpdateAlreadyInConflict_merge')
    @GET('http://localhost/source/osctest/already_in_conflict/_meta', file='meta.xml')
    def testUpdateAlreadyInConflict(self):
        """
        a file was modified in the remote package (the local file is already in conflict)
        """
        self._change_to_pkg('already_in_conflict')
        osc.core.Package('.').update(rev=2)
        exp = 'skipping \'merge\' (this is due to conflicts)\nAt revision 2.\n'
        self.assertEqual(sys.stdout.getvalue(), exp)
        self._check_conflictlist('merge\n')
        self.__check_digests('testUpdateAlreadyInConflict_files')

    @GET('http://localhost/source/osctest/deleted?rev=2', file='testUpdateLocalDeletions_files')
    @GET('http://localhost/source/osctest/deleted/foo?rev=2', file='testUpdateLocalDeletions_foo')
    @GET('http://localhost/source/osctest/deleted/merge?rev=2', file='testUpdateLocalDeletions_merge')
    @GET('http://localhost/source/osctest/deleted/_meta', file='meta.xml')
    def testUpdateLocalDeletions(self):
        """
        the files 'foo' and 'merge' were modified in the remote package
        and marked for deletion in the local wc. Additionally the file
        'merge' was modified in the wc before deletion so the local file
        still exists (and a merge with the remote file is not possible)
        """
        self._change_to_pkg('deleted')
        osc.core.Package('.').update(rev=2)
        exp = 'U    foo\nC    merge\nAt revision 2.\n'
        self.assertEqual(sys.stdout.getvalue(), exp)
        self._check_deletelist('foo\n')
        self._check_conflictlist('merge\n')
        self.assertEqual(open('foo', 'r').read(), open(os.path.join('.osc', 'foo'), 'r').read())
        self.__check_digests('testUpdateLocalDeletions_files')

    @GET('http://localhost/source/osctest/restore?rev=latest', file='testUpdateRestore_files')
    @GET('http://localhost/source/osctest/restore/foo?rev=1', file='testUpdateRestore_foo')
    @GET('http://localhost/source/osctest/restore/_meta', file='meta.xml')
    def testUpdateRestore(self):
        """local file 'foo' was deleted with a non osc command and will be restored"""
        self._change_to_pkg('restore')
        osc.core.Package('.').update()
        exp = 'Restored \'foo\'\nAt revision 1.\n'
        self.assertEqual(sys.stdout.getvalue(), exp)
        self.__check_digests('testUpdateRestore_files')

    @GET('http://localhost/source/osctest/limitsize?rev=latest', file='testUpdateLimitSizeNoChange_filesremote')
    @GET('http://localhost/source/osctest/limitsize/_meta', file='meta.xml')
    def testUpdateLimitSizeNoChange(self):
        """
        a new file was added to the remote package but isn't checked out because
        of the size constraint
        """
        self._change_to_pkg('limitsize')
        osc.core.Package('.').update(limit_size=50)
        exp = 'D    bigfile\nAt revision 2.\n'
        self.assertEqual(sys.stdout.getvalue(), exp)
        self.assertFalse(os.path.exists(os.path.join('.osc', 'bigfile')))
        self.assertFalse(os.path.exists('bigfile'))
        self.__check_digests('testUpdateLimitSizeNoChange_files', 'bigfile')

    @GET('http://localhost/source/osctest/limitsize?rev=latest', file='testUpdateLimitSizeAddDelete_filesremote')
    @GET('http://localhost/source/osctest/limitsize/exists?rev=2', file='testUpdateLimitSizeAddDelete_exists')
    @GET('http://localhost/source/osctest/limitsize/_meta', file='meta.xml')
    def testUpdateLimitSizeAddDelete(self):
        """
        a new file (exists) was added to the remote package with
        size < limit_size and one file (nochange) was deleted from the
        remote package (local file 'nochange' is modified). Additionally
        files which didn't change are removed the local wc due to the
        size constraint.
        """
        self._change_to_pkg('limitsize')
        osc.core.Package('.').update(limit_size=10)
        exp = 'A    exists\nD    bigfile\nD    foo\nD    merge\nD    nochange\nAt revision 2.\n'
        self.assertEqual(sys.stdout.getvalue(), exp)
        self.assertFalse(os.path.exists(os.path.join('.osc', 'bigfile')))
        self.assertFalse(os.path.exists('bigfile'))
        self.assertFalse(os.path.exists(os.path.join('.osc', 'foo')))
        self.assertFalse(os.path.exists('foo'))
        self.assertFalse(os.path.exists(os.path.join('.osc', 'merge')))
        self.assertFalse(os.path.exists('merge'))
        # exists because local version is modified
        self.assertTrue(os.path.exists('nochange'))

        self.__check_digests('testUpdateLimitSizeAddDelete_files', 'bigfile', 'foo', 'merge', 'nochange')

    @GET('http://localhost/source/osctest/services?rev=latest', file='testUpdateServiceFilesAddDelete_filesremote')
    @GET('http://localhost/source/osctest/services/bigfile?rev=2', file='testUpdateServiceFilesAddDelete_bigfile')
    @GET('http://localhost/source/osctest/services/_service%3Abar?rev=2', file='testUpdateServiceFilesAddDelete__service:bar')
    @GET('http://localhost/source/osctest/services/_service%3Afoo?rev=2', file='testUpdateServiceFilesAddDelete__service:foo')
    @GET('http://localhost/source/osctest/services/_meta', file='meta.xml')
    def testUpdateAddDeleteServiceFiles(self):
        """
        a new file was added to the remote package but isn't checked out because
        of the size constraint
        """
        self._change_to_pkg('services')
        osc.core.Package('.').update(service_files=True)
        exp = 'A    bigfile\nD    _service:exists\nA    _service:bar\nA    _service:foo\nAt revision 2.\n'
        self.assertEqual(sys.stdout.getvalue(), exp)
        self.assertFalse(os.path.exists(os.path.join('.osc', '_service:bar')))
        self.assertTrue(os.path.exists('_service:bar'))
        self.assertEqual(open('_service:bar').read(), 'another service\n')
        self.assertFalse(os.path.exists(os.path.join('.osc', '_service:foo')))
        self.assertTrue(os.path.exists('_service:foo'))
        self.assertEqual(open('_service:foo').read(), 'small\n')
        self.assertTrue(os.path.exists('_service:exists'))
        self.__check_digests('testUpdateServiceFilesAddDelete_files', '_service:foo', '_service:bar')

    # tests to recover from an aborted/broken update

    @GET('http://localhost/source/osctest/simple/foo?rev=2', file='testUpdateResume_foo')
    @GET('http://localhost/source/osctest/simple/merge?rev=2', file='testUpdateResume_merge')
    @GET('http://localhost/source/osctest/simple/_meta', file='meta.xml')
    @GET('http://localhost/source/osctest/simple?rev=2', file='testUpdateResume_files')
    @GET('http://localhost/source/osctest/simple/_meta', file='meta.xml')
    def testUpdateResume(self):
        """resume an aborted update"""
        self._change_to_pkg('resume')
        osc.core.Package('.').update(rev=2)
        exp = 'resuming broken update...\nU    foo\nU    merge\nAt revision 2.\nAt revision 2.\n'
        self.assertEqual(sys.stdout.getvalue(), exp)
        self.assertFalse(os.path.exists(os.path.join('.osc', '_in_update')))
        self.__check_digests('testUpdateResume_files')

    @GET('http://localhost/source/osctest/simple/added?rev=1', file='testUpdateResumeDeletedFile_foo')
    @GET('http://localhost/source/osctest/simple/foo?rev=1', file='testUpdateResumeDeletedFile_foo')
    @GET('http://localhost/source/osctest/simple/merge?rev=1', file='testUpdateResumeDeletedFile_merge')
    @GET('http://localhost/source/osctest/simple/_meta', file='meta.xml')
    @GET('http://localhost/source/osctest/simple?rev=1', file='testUpdateResumeDeletedFile_files')
    @GET('http://localhost/source/osctest/simple/_meta', file='meta.xml')
    def testUpdateResumeDeletedFile(self):
        """
        resume an aborted update (the file 'added' was already deleted in the first update
        run). It's marked as deleted again (this is due to an expected issue with the update
        code)
        """
        self._change_to_pkg('resume_deleted')
        osc.core.Package('.').update(rev=1)
        exp = 'resuming broken update...\nD    added\nU    foo\nU    merge\nAt revision 1.\nAt revision 1.\n'
        self.assertEqual(sys.stdout.getvalue(), exp)
        self.assertFalse(os.path.exists(os.path.join('.osc', '_in_update')))
        self.assertFalse(os.path.exists('added'))
        self.assertFalse(os.path.exists(os.path.join('.osc', 'added')))
        self.__check_digests('testUpdateResumeDeletedFile_files')

    def __check_digests(self, fname, *skipfiles):
        fname = os.path.join(self._get_fixtures_dir(), fname)
        self.assertEqual(open(os.path.join('.osc', '_files'), 'r').read(), open(fname, 'r').read())
        root = ET.parse(fname).getroot()
        for i in root.findall('entry'):
            if i.get('name') in skipfiles:
                continue
            self.assertTrue(os.path.exists(os.path.join('.osc', i.get('name'))))
            self.assertEqual(osc.core.dgst(os.path.join('.osc', i.get('name'))), i.get('md5'))

if __name__ == '__main__':
    import unittest
    unittest.main()