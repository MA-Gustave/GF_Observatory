"""Loopback-only read-only HTTP surface; no source import or admin endpoints."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit, parse_qs
from importlib.resources import files
import json
import secrets
from .config import Config
from .errors import ObservatoryError, require
from .service import Observatory
from .jsonsafe import utcnow


def make_handler(config:Config):
    class Handler(BaseHTTPRequestHandler):
        server_version="GFObservatory/1.0"
        def log_message(self,*args):pass  # avoid printing private request strings
        def response(self, status, body:bytes, ct="application/json; charset=utf-8"):
            self.send_response(status)
            for k,v in {"Content-Type":ct,"Content-Length":str(len(body)),"Cache-Control":"no-store",
                         "X-Content-Type-Options":"nosniff","Referrer-Policy":"no-referrer",
                         "Content-Security-Policy":"default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self'; base-uri 'none'; frame-ancestors 'none'"}.items():
                self.send_header(k,v)
            self.end_headers()
            try:self.wfile.write(body)
            except (BrokenPipeError,ConnectionResetError):pass
        def json_response(self,code,obj):self.response(code,json.dumps(obj,ensure_ascii=False,allow_nan=False).encode("utf8"))
        def check_host(self):
            host=self.headers.get("Host", "")
            require(host==f"127.0.0.1:{self.server.server_address[1]}",
                    "OBS_HOST_DENIED","Requests must target the loopback host",403)
        def do_POST(self):self.json_response(405,{"error":{"code":"OBS_READ_ONLY_API","message":"Use local CLI or desktop to import","details":{}}})
        do_PUT=do_POST
        do_DELETE=do_POST
        do_PATCH=do_POST
        def do_GET(self):
            request_id="req_"+secrets.token_hex(6)
            try:
                self.check_host()
                parsed=urlsplit(self.path)
                path=parsed.path
                if path in ("/", "/index.html", "/app.js", "/style.css"):
                    filename="index.html" if path in ("/", "/index.html") else path.lstrip("/")
                    raw=files("gf_observatory").joinpath("web",filename).read_bytes()
                    ct="text/html; charset=utf-8" if filename.endswith(".html") else "text/javascript; charset=utf-8" if filename.endswith(".js") else "text/css; charset=utf-8"
                    self.response(200,raw,ct)
                    return
                query=parse_qs(parsed.query,keep_blank_values=True)
                require(set(query).issubset({"language","batch_id"}) and all(len(v)==1 and len(v[0])<=120 for v in query.values()),
                        "OBS_QUERY_INVALID","Unknown or repeated query parameter",400)
                lang=query.get("language",[None])[0]
                bid=query.get("batch_id",[None])[0]
                with_app=Observatory(config)
                try:
                    if path=="/api/v1/health/live":payload={"live":True}
                    elif path=="/api/v1/health/ready":payload={"ready":True,"source_writes":False}
                    elif path=="/api/v1/status":payload=with_app.status(bid)
                    elif path=="/api/v1/batches":payload=with_app.batches()
                    elif path=="/api/v1/languages":payload=with_app.languages(bid)
                    elif path=="/api/v1/scenarios":payload=with_app.scenarios(lang,bid)
                    elif path=="/api/v1/matrix":
                        require(lang is not None,"OBS_QUERY_INVALID","Language required",400)
                        payload=with_app.matrix(lang,bid)
                    elif path=="/api/v1/trends":
                        require(lang is not None,"OBS_QUERY_INVALID","Language required",400)
                        payload=with_app.trends(lang)
                    elif path=="/api/v1/report":payload=with_app.report(bid)
                    elif path=="/api/v1/diagnostics":payload=with_app.store.attempts()
                    else:raise ObservatoryError("OBS_ROUTE_UNKNOWN","Unknown route",404)
                finally:with_app.close()
                self.json_response(200,{"data":payload,"meta":{"request_id":request_id,"contract_version":"1.0",
                                                  "generated_at":utcnow()}})
            except ObservatoryError as e:
                self.json_response(e.status,{"error":{"code":e.code,"message":str(e),"request_id":request_id,"details":{}}})
            except Exception:
                self.json_response(500,{"error":{"code":"OBS_INTERNAL_ERROR","message":"Internal error","request_id":request_id,"details":{}}})
    return Handler


def new_server(config:Config):
    server=ThreadingHTTPServer((config.bind,config.port),make_handler(config))
    server.daemon_threads=True
    return server


def serve(config:Config):
    with new_server(config) as server:
        print(f"GF Observatory (read-only): http://127.0.0.1:{server.server_address[1]}/",flush=True)
        server.serve_forever(poll_interval=0.1)
