"""Optional authenticated source-archive regression fixture (never shipped with code)."""
import os
from pathlib import Path
import unittest
from gf_observatory.pilot_reader import inspect_archive

class RealArchiveAcceptance(unittest.TestCase):
    def test_provided_full_batch_when_explicitly_available(self):
        path=os.environ.get('GF_OBSERVATORY_REAL_BATCH')
        if not path or not Path(path).is_file():
            self.skipTest('Set GF_OBSERVATORY_REAL_BATCH to an operator-owned complete WordBench pilot ZIP')
        value=inspect_archive(Path(path))
        self.assertEqual(value.archive_sha256,'d6b10174d490a4f7a1f5f9b61fcf70de3140a3d6e50e3c3c52c913cfd56bdcfd')
        self.assertEqual(len(value.source_languages),20)
        self.assertEqual(len(value.languages),14)
        self.assertEqual(len(value.scenarios),210)
        self.assertEqual(value.totals['candidate_for_review'],223)
        self.assertEqual(value.totals['probe_failed'],77)
        self.assertEqual(len(value.warnings),4)
