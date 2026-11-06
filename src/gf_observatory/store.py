"""Private SQLite-derived history; producer artifacts are never written."""
from __future__ import annotations
import json
from pathlib import Path
from contextlib import closing
import sqlite3
from .errors import ObservatoryError
from .jsonsafe import dumps, fingerprint, utcnow
from .pilot_reader import PilotImport

SCHEMA = 1

class Store:
    def __init__(self, path: Path):
        self.path = Path(path).expanduser().absolute()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.db=sqlite3.connect(self.path, timeout=15, check_same_thread=False)
        self.db.row_factory=sqlite3.Row
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA busy_timeout=15000")
        self.migrate()

    def migrate(self):
        existing=self.db.execute("PRAGMA user_version").fetchone()[0]
        if existing > SCHEMA:
            raise ObservatoryError("OBS_DB_VERSION", "Database was created by a newer release")
        with self.db:
            self.db.executescript("""
                CREATE TABLE IF NOT EXISTS batches (
                  import_id TEXT PRIMARY KEY, archive_sha256 TEXT NOT NULL,
                  source_batch_id TEXT NOT NULL, profile_id TEXT NOT NULL,
                  source_status TEXT NOT NULL, started_at TEXT NOT NULL,
                  finished_at TEXT NOT NULL, imported_at TEXT NOT NULL,
                  selected_json TEXT NOT NULL, source_totals_json TEXT NOT NULL,
                  source_languages_json TEXT NOT NULL, member_count INTEGER NOT NULL,
                  member_tree_sha256 TEXT NOT NULL, archive_bytes INTEGER NOT NULL,
                  warnings_json TEXT NOT NULL,
                  UNIQUE(archive_sha256,selected_json)
                );
                CREATE TABLE IF NOT EXISTS language_results (
                  import_id TEXT NOT NULL REFERENCES batches(import_id) ON DELETE RESTRICT,
                  code TEXT NOT NULL, candidate_count INTEGER NOT NULL,
                  failed_count INTEGER NOT NULL, timeout_count INTEGER NOT NULL,
                  unverified_count INTEGER NOT NULL, scenario_count INTEGER NOT NULL,
                  technical_status TEXT NOT NULL, human_review_status TEXT NOT NULL,
                  practical_generation_status TEXT NOT NULL, canonical_readiness TEXT NOT NULL,
                  source_report_sha256 TEXT NOT NULL,
                  PRIMARY KEY(import_id,code)
                );
                CREATE TABLE IF NOT EXISTS scenarios (
                  import_id TEXT NOT NULL, code TEXT NOT NULL,
                  scenario_id TEXT NOT NULL, status TEXT NOT NULL,
                  semantic_intent TEXT NOT NULL, meaning_en TEXT NOT NULL,
                  candidate TEXT, exit_code INTEGER, timed_out INTEGER NOT NULL,
                  reason TEXT NOT NULL, source_member TEXT NOT NULL,
                  source_member_sha256 TEXT NOT NULL, warnings_json TEXT NOT NULL,
                  review_approved INTEGER NOT NULL DEFAULT 0,
                  PRIMARY KEY(import_id,code,scenario_id),
                  FOREIGN KEY(import_id,code) REFERENCES language_results(import_id,code)
                );
                CREATE INDEX IF NOT EXISTS lang_code_idx ON language_results(code);
                CREATE INDEX IF NOT EXISTS scenario_status_idx ON scenarios(status);
                CREATE TABLE IF NOT EXISTS ingestion_attempts (
                  attempt_id TEXT PRIMARY KEY, at_utc TEXT NOT NULL,
                  source_file_basename TEXT NOT NULL, result TEXT NOT NULL,
                  reason_code TEXT NOT NULL, import_id TEXT
                );
            """)
            self.db.execute(f"PRAGMA user_version={SCHEMA}")

    def close(self):self.db.close()
    def __enter__(self):return self
    def __exit__(self,*_):self.close()

    def attempt(self, filename, result, reason, import_id=None):
        at=utcnow();eid="try_"+fingerprint([at,str(filename),result,reason,import_id])[:24]
        # Collision in the same second is acceptable for an audit append; add a row counter.
        import secrets
        eid+=secrets.token_hex(5)
        with self.db:
            self.db.execute("INSERT INTO ingestion_attempts VALUES (?,?,?,?,?,?)",
                           (eid,at,Path(filename).name[:200],result,reason,import_id))

    def save(self, bundle:PilotImport):
        selected_json=dumps(list(bundle.selected)).decode()
        import_id="imp_"+fingerprint({"sha":bundle.archive_sha256,"scope":list(bundle.selected)})[:32]
        row=self.db.execute("SELECT import_id FROM batches WHERE import_id=?",(import_id,)).fetchone()
        if row:
            self.attempt("pilot-archive.zip","REPLAY","ALREADY_IMPORTED",import_id)
            return import_id,False
        with self.db:
            self.db.execute("""INSERT INTO batches VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (import_id,bundle.archive_sha256,bundle.batch_id,"defluens-practical-15/core-14/1",
                bundle.source_status,bundle.started_at,bundle.finished_at,bundle.imported_at,
                selected_json,dumps(bundle.totals).decode(),dumps(list(bundle.source_languages)).decode(),
                bundle.member_count,bundle.recalculated_members_sha256,bundle.archive_bytes,
                dumps(bundle.warnings).decode()))
            self.db.executemany("""INSERT INTO language_results VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                [(import_id,x["language"],x["candidate_count"],x["failed_count"],x["timeout_count"],
                  x["unverified_count"],x["scenario_count"],x["technical_status"],x["human_review_status"],
                  x["practical_generation_status"],x["canonical_readiness"],x["source_report_sha256"])
                 for x in bundle.languages])
            self.db.executemany("""INSERT INTO scenarios VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                [(import_id,x["language"],x["scenario_id"],x["status"],x["semantic_intent"],
                  x["meaning_en"],x["candidate"],x["exit_code"],int(x["timed_out"]),x["reason"],
                  x["evidence_member"],x["evidence_sha256"],dumps(x["surface_warnings"]).decode(),0)
                 for x in bundle.scenarios])
        self.attempt("pilot-archive.zip","IMPORTED","PILOT_TECHNICAL_ONLY",import_id)
        return import_id,True

    def batches(self,limit=100):
        rows=self.db.execute("SELECT * FROM batches ORDER BY finished_at DESC,import_id DESC LIMIT ?",(limit,)).fetchall()
        return [self._batch_row(r) for r in rows]

    def _batch_row(self, r):
        obj={k:r[k] for k in r.keys()}
        for key in ("selected_json","source_totals_json","source_languages_json","warnings_json"):
            obj[key[:-5] if key.endswith('_json') else key]=json.loads(obj.pop(key))
        obj["evidence_class"]="WORD_BENCH_PRACTICAL_PILOT_CANDIDATES"
        obj["canonical_wordbench_manifest_verified"]=False
        obj["human_review_completed"]=False
        obj["linguistically_certified"]=False
        obj["published"]=False
        obj["activated"]=False
        return obj

    def batch(self, bid=None):
        if bid is None:
            row=self.db.execute("SELECT * FROM batches ORDER BY finished_at DESC,import_id DESC LIMIT 1").fetchone()
        else:
            row=self.db.execute("SELECT * FROM batches WHERE import_id=?",(bid,)).fetchone()
        if row is None:raise ObservatoryError("OBS_BATCH_NOT_FOUND","No matching imported batch",404)
        return self._batch_row(row)

    def languages(self,bid):
        rows=self.db.execute("SELECT * FROM language_results WHERE import_id=? ORDER BY code",(bid,)).fetchall()
        return [dict(r) for r in rows]

    def scenarios(self,bid,code=None):
        sql="SELECT * FROM scenarios WHERE import_id=?"
        params=[bid]
        if code is not None:sql+=" AND code=?";params.append(code)
        sql+=" ORDER BY code,scenario_id"
        rows=self.db.execute(sql,params).fetchall()
        out=[]
        for r in rows:
            d=dict(r);d["surface_warnings"]=json.loads(d.pop("warnings_json"))
            d["timed_out"]=bool(d["timed_out"]);d["review_approved"]=False
            out.append(d)
        return out

    def attempts(self,limit=100):
        return [dict(x) for x in self.db.execute("SELECT * FROM ingestion_attempts ORDER BY at_utc DESC LIMIT ?",(limit,))]

    def distinct_batches(self):
        return self.batches(limit=1000)

    def backup(self, destination:Path):
        to=Path(destination).expanduser().absolute()
        if to==self.path or to.is_relative_to(self.path.parent):
            raise ObservatoryError("OBS_BACKUP_LOCATION","Backup must be outside active DB directory")
        if to.exists():raise ObservatoryError("OBS_BACKUP_EXISTS","Refusing to overwrite backup")
        to.parent.mkdir(parents=True,exist_ok=True)
        # SQLite backup API ensures consistent copy even with WAL.
        with closing(sqlite3.connect(to)) as dest:
            self.db.backup(dest)
        return {"backup_path":str(to),"bytes":to.stat().st_size}
