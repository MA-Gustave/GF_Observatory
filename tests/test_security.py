import zipfile
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from gf_observatory.pilot_reader import inspect_archive, MAX_ARCHIVE
from gf_observatory.errors import ObservatoryError
from gf_observatory.config import load_config
from factory import fake_archive

class ArchiveSecurity(unittest.TestCase):
    def setUp(self):
        self.temp=TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.path=self.root/'s.zip'
    def assert_bad(self,code):
        with self.assertRaises(ObservatoryError) as e:inspect_archive(self.path)
        self.assertEqual(e.exception.code,code)
    def test_symlink_source_rejected(self):
        fake_archive(self.path)
        shortcut=self.root/'link.zip'
        try:shortcut.symlink_to(self.path)
        except (OSError,NotImplementedError):self.skipTest('Symlink creation unavailable')
        with self.assertRaises(ObservatoryError) as cm:inspect_archive(shortcut)
        self.assertEqual(cm.exception.code,'OBS_SOURCE_LINK')
    def test_symlink_member_rejected(self):
        fake_archive(self.path)
        zi=zipfile.ZipInfo('defluens-batch-full-symlink/short')
        zi.create_system=3
        zi.external_attr=(0o120777 << 16)
        with zipfile.ZipFile(self.path,'a') as z:z.writestr(zi,'../../outside')
        self.assert_bad('OBS_ZIP_LINK')
    def test_oversized_declared_member_rejected(self):
        fake_archive(self.path)
        with zipfile.ZipFile(self.path,'a') as z:
            z.writestr('defluens-batch-full-extra/zeros', b'0' * 500_000)
        self.assert_bad('OBS_ZIP_PATH')  # foreign root is still rejected
    def test_config_wildcard_binding_rejected(self):
        p=self.root/'unsafe.toml'
        p.write_text('[api]\nbind="0.0.0.0"\n')
        with self.assertRaises(ObservatoryError) as cm:load_config(p)
        self.assertEqual(cm.exception.code,'OBS_CONFIG_UNSAFE')
    def test_config_source_writes_rejected(self):
        p=self.root/'unsafe.toml'
        p.write_text('[security]\nsource_writes=true\n')
        with self.assertRaises(ObservatoryError) as cm:load_config(p)
        self.assertEqual(cm.exception.code,'OBS_CONFIG_UNSAFE')
