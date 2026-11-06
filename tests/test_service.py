import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from gf_observatory.config import Config
from gf_observatory.service import Observatory
from gf_observatory.errors import ObservatoryError
from gf_observatory.static_export import export_static
from gf_observatory.policy import CORE_14
from factory import fake_archive

class ServiceTests(unittest.TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.path=fake_archive(self.root/'source.zip')
        self.app=Observatory(Config(self.root/'state'/'db.sqlite3'))
        self.addCleanup(self.app.close)
    def test_zero_evidence(self):self.assertEqual(self.app.status()["status"],"NO_EVIDENCE")
    def test_import_persists_14_languages(self):
        result=self.app.import_pilot(self.path)
        self.assertEqual(result["candidate_total_in_scope"],210)
        self.assertEqual(result["canonical_readiness"],"R0")
        self.assertEqual(len(self.app.languages()),14)
        self.assertEqual(len(self.app.scenarios()),210)
        self.assertEqual(len(self.app.matrix('Fre')["signals"]),14)
        self.assertIsNone(self.app.matrix('Fre')["maturity"])
        self.assertFalse(self.app.status()["linguistically_certified"])
    def test_replay_idempotent(self):
        self.assertTrue(self.app.import_pilot(self.path)["imported"])
        self.assertFalse(self.app.import_pilot(self.path)["imported"])
        self.assertEqual(len(self.app.batches()),1)
        self.assertEqual(len(self.app.store.attempts()),2)
    def test_source_not_modified(self):
        before=self.path.read_bytes();self.app.import_pilot(self.path)
        self.assertEqual(self.path.read_bytes(),before)
    def test_stored_after_source_removed(self):
        self.app.import_pilot(self.path);self.path.unlink()
        self.assertEqual(self.app.status()["candidate_for_review"],210)
    def test_core14_only(self):
        self.app.import_pilot(self.path)
        with self.assertRaises(ObservatoryError) as cm:self.app.scenarios('Sqi')
        self.assertEqual(cm.exception.code,'OBS_LANGUAGE_OUT_OF_SCOPE')
    def test_attempt_rejected(self):
        self.path.write_bytes(b'broken')
        with self.assertRaises(ObservatoryError):self.app.import_pilot(self.path)
        self.assertEqual(self.app.store.attempts()[0]['result'],'REJECTED')
        self.assertEqual(len(self.app.batches()),0)
    def test_trend_no_baseline(self):
        self.app.import_pilot(self.path)
        self.assertEqual(self.app.trends('Fre')['status'],'NO_COMPARABLE_BASELINE')
    def test_backup_outside_state_dir(self):
        self.app.import_pilot(self.path)
        dest=self.root/'backup'/'data.sqlite3'
        result=self.app.store.backup(dest)
        self.assertTrue(dest.is_file())
        other=Observatory(Config(dest))
        try:self.assertEqual(len(other.batches()),1)
        finally:other.close()
    def test_export_require_approval(self):
        self.app.import_pilot(self.path)
        with self.assertRaises(ObservatoryError):export_static(self.app,self.root/'static')
    def test_static_redaction_four_files(self):
        self.app.import_pilot(self.path)
        output=self.root/'static'
        res=export_static(self.app,output,acknowledged=True)
        self.assertEqual(len(list(output.iterdir())),4)
        self.assertFalse(res['external_publication_performed'])
        data=json.loads((output/'status.json').read_text())
        self.assertEqual(len(data['languages']),14)
        self.assertFalse(data['linguistically_certified'])
        self.assertNotIn(str(self.root),json.dumps(data))
    def test_static_preserves_unrelated_folder(self):
        self.app.import_pilot(self.path)
        output=self.root/'static';output.mkdir();(output/'secret.txt').write_text('private')
        with self.assertRaises(ObservatoryError):export_static(self.app,output,acknowledged=True)
        self.assertEqual((output/'secret.txt').read_text(),'private')
    def test_static_not_over_db(self):
        self.app.import_pilot(self.path)
        with self.assertRaises(ObservatoryError):export_static(self.app,self.root/'state'/'site',acknowledged=True)
    def test_scope_subset(self):
        self.app.import_pilot(self.path,['Eng','Fre'])
        self.assertEqual(self.app.status()['languages_in_scope'],2)
        self.assertEqual(self.app.status()['scenarios_in_scope'],30)
        self.assertEqual(self.app.status()['source_full_batch_totals']['candidate_for_review'],210)
