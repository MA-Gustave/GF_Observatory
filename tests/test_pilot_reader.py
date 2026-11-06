import json
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile, ZIP_DEFLATED
import unittest
from gf_observatory.errors import ObservatoryError
from gf_observatory.policy import CORE_14,SCENARIOS_15,scope
from gf_observatory.pilot_reader import inspect_archive
from gf_observatory.jsonsafe import sha256,loads,fingerprint
from factory import fake_archive, ROOT

class PilotReaderTests(unittest.TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/"defluens-batch-full-test.zip"
    def fails(self,code,**kwargs):
        fake_archive(self.path,**kwargs)
        with self.assertRaises(ObservatoryError) as cm:inspect_archive(self.path)
        self.assertEqual(cm.exception.code,code)
    def test_success_14_languages(self):
        fake_archive(self.path)
        a=inspect_archive(self.path)
        self.assertEqual(len(a.languages),14)
        self.assertEqual(len(a.scenarios),210)
        self.assertEqual(a.totals["candidate_for_review"],210)
        self.assertEqual(a.archive_sha256,sha256(self.path.read_bytes()))
        self.assertFalse(any(x["review_approved"] for x in a.scenarios))
        self.assertEqual(a.selected,CORE_14)
    def test_strict_fifteen_only(self):self.assertEqual(len(SCENARIOS_15),15)
    def test_fixed_languages(self):
        self.assertEqual(len(CORE_14),14)
        self.assertRaises(ObservatoryError,scope,["Sqi"])
    def test_failed_probe_is_still_evidence(self):
        fake_archive(self.path,fail_language="Eng")
        a=inspect_archive(self.path)
        self.assertEqual(a.totals["probe_failed"],15)
        self.assertEqual(next(x for x in a.languages if x["language"]=="Eng")["failed_count"],15)
    def test_subset_selection(self):
        fake_archive(self.path)
        a=inspect_archive(self.path,["Fre", "Eng"])
        self.assertEqual([x["language"] for x in a.languages],["Eng","Fre"])
        self.assertEqual(len(a.scenarios),30)
        self.assertEqual(a.totals["candidate_for_review"],210)
    def test_scenario_text_mismatch(self):self.fails("OBS_PILOT_INCONSISTENT",tamper_candidate=True)
    def test_counters_mismatch(self):self.fails("OBS_PILOT_INCONSISTENT",tamper_counters=True)
    def test_no_review_claim_without_provenance(self):self.fails("OBS_PILOT_REVIEW_UNTRUSTED",reviewed=True)
    def test_zip_slip(self):self.fails("OBS_ZIP_PATH",malicious="../../evil.txt")
    def test_second_root_refused(self):self.fails("OBS_ZIP_PATH",malicious="another-root/file.txt")
    def test_zip_duplicate_member(self):
        fake_archive(self.path)
        with ZipFile(self.path,"a",compression=ZIP_DEFLATED) as z:
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore",UserWarning)
                z.writestr(ROOT+"batch_summary.json",b"{}")
        with self.assertRaises(ObservatoryError) as cm:inspect_archive(self.path)
        self.assertEqual(cm.exception.code,"OBS_ZIP_COLLISION")
    def test_corrupt_zip(self):
        self.path.write_bytes(b"not a zip")
        with self.assertRaises(ObservatoryError) as cm:inspect_archive(self.path)
        self.assertEqual(cm.exception.code,"OBS_ZIP_INTEGRITY")
    def test_archive_integrity_hash_is_exact(self):
        fake_archive(self.path)
        with ZipFile(self.path) as z:
            self.assertEqual(sha256(self.path.read_bytes()),inspect_archive(self.path).archive_sha256)
    def test_nonfinite_and_duplicate_json(self):
        for payload in (b'{"a":1,"a":2}',b'{"x":NaN}',b'{"x":1e999}'):
            with self.subTest(payload=payload),self.assertRaises(ObservatoryError):loads(payload)
    def test_unicode_not_normalized(self):
        self.assertNotEqual(sha256("é".encode()),sha256("e\u0301".encode()))
    def test_fingerprint_key_order(self):
        self.assertEqual(fingerprint({"a":1,"b":2}),fingerprint({"b":2,"a":1}))
