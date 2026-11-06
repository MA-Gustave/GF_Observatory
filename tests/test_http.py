from pathlib import Path
from tempfile import TemporaryDirectory
import threading
import unittest
import urllib.request
import urllib.error
import json
from gf_observatory.config import Config
from gf_observatory.service import Observatory
from gf_observatory.api import new_server
from factory import fake_archive

class HttpTests(unittest.TestCase):
    def setUp(self):
        self.temp=TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        root=Path(self.temp.name)
        self.config=Config(root/'state'/'o.db',port=0)
        with_app=Observatory(self.config)
        self.addCleanup(with_app.close)
        with_app.import_pilot(fake_archive(root/'archive.zip'))
        self.server=new_server(self.config)
        self.port=self.server.server_address[1]
        self.base=f'http://127.0.0.1:{self.port}'
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True)
        self.thread.start()
        self.addCleanup(self.stop)
    def stop(self):
        self.server.shutdown();self.server.server_close();self.thread.join(timeout=5)
    def req(self, url, method='GET', host=None):
        headers={'Host':host} if host else {}
        request=urllib.request.Request(self.base+url,method=method,headers=headers)
        try:
            with urllib.request.urlopen(request,timeout=5) as r:
                return r.status,r.read(),dict(r.headers)
        except urllib.error.HTTPError as e:
            return e.code,e.read(),dict(e.headers)
    def test_health(self):
        s,b,_=self.req('/api/v1/health/live')
        self.assertEqual(s,200);self.assertTrue(json.loads(b)['data']['live'])
    def test_dashboard_assets(self):
        for route in ('/','/app.js','/style.css'):
            with self.subTest(route=route):
                s,b,h=self.req(route);self.assertEqual(s,200)
                self.assertGreater(len(b),100)
                self.assertIn('Content-Security-Policy',h)
    def test_status(self):
        s,b,_=self.req('/api/v1/status')
        obj=json.loads(b)['data']
        self.assertEqual(s,200);self.assertEqual(obj['candidate_for_review'],210)
        self.assertFalse(obj['linguistically_certified'])
    def test_languages_and_scenarios(self):
        s,b,_=self.req('/api/v1/languages')
        self.assertEqual(len(json.loads(b)['data']),14)
        s,b,_=self.req('/api/v1/scenarios?language=Fre')
        self.assertEqual(len(json.loads(b)['data']),15)
    def test_matrix_does_not_promote(self):
        s,b,_=self.req('/api/v1/matrix?language=Fre')
        mat=json.loads(b)['data']
        self.assertIsNone(mat['maturity']);self.assertEqual(mat['readiness'],'R0')
    def test_noncore_language_refused(self):
        s,b,_=self.req('/api/v1/scenarios?language=Sqi')
        self.assertEqual(s,404);self.assertEqual(json.loads(b)['error']['code'],'OBS_LANGUAGE_OUT_OF_SCOPE')
    def test_api_rejects_bad_host(self):
        s,b,_=self.req('/api/v1/status',host='malicious.example')
        self.assertEqual(s,403)
    def test_http_api_is_read_only(self):
        s,b,_=self.req('/api/v1/status',method='POST')
        self.assertEqual(s,405);self.assertIn(b'OBS_READ_ONLY_API',b)
    def test_unknown_param_rejected(self):
        s,b,_=self.req('/api/v1/status?sql=select')
        self.assertEqual(s,400)
    def test_endpoint_does_not_include_raw_windows_path(self):
        s,b,_=self.req('/api/v1/report')
        self.assertEqual(s,200)
        self.assertNotIn(b'C:\\Users\\',b)
