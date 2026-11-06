from pathlib import Path
from tempfile import TemporaryDirectory
import contextlib
import io
import json
import unittest
from gf_observatory.cli import main
from factory import fake_archive

class CliTests(unittest.TestCase):
    def setUp(self):
        self.temp=TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.config=self.root/'observatory.toml'
        self.config.write_text('[api]\nbind="127.0.0.1"\nport=8765\n[state]\ndatabase="db/o.db"\n',encoding='utf-8')
        self.zip=fake_archive(self.root/'sample.zip')
    def run_cli(self,*args):
        out=io.StringIO();err=io.StringIO()
        with contextlib.redirect_stdout(out),contextlib.redirect_stderr(err):
            rc=main(['--config',str(self.config),*args])
        return rc,out.getvalue(),err.getvalue()
    def test_doctor(self):
        rc,text,_=self.run_cli('doctor');self.assertEqual(rc,0)
        self.assertEqual(json.loads(text)['core_languages'].__len__(),14)
    def test_verify_does_not_create_db(self):
        rc,text,_=self.run_cli('verify-pilot',str(self.zip))
        self.assertEqual(rc,0)
        self.assertEqual(json.loads(text)['status'],'ARCHIVE_VERIFIED_PILOT_ONLY')
        self.assertFalse((self.root/'db'/'o.db').exists())
    def test_import_and_reporting(self):
        rc,text,_=self.run_cli('import-pilot',str(self.zip))
        self.assertEqual(rc,0);self.assertTrue(json.loads(text)['imported'])
        rc,text,_=self.run_cli('report','--format','markdown')
        self.assertEqual(rc,0);self.assertIn('non approuvées',text)
    def test_cannot_add_out_of_scope_language(self):
        rc,text,err=self.run_cli('import-pilot',str(self.zip),'--languages','Sqi')
        self.assertEqual(rc,4)
        self.assertEqual(json.loads(err)['error']['code'],'OBS_SCOPE_INVALID')
    def test_no_duplicate_import(self):
        self.run_cli('import-pilot',str(self.zip))
        rc,text,_=self.run_cli('import-pilot',str(self.zip))
        self.assertEqual(rc,0);self.assertTrue(json.loads(text)['replayed'])
