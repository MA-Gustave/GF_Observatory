"""Single application boundary. CLI, dashboard and desktop import call this service."""
from pathlib import Path
from .analysis import matrix, overview, trend
from .config import Config
from .errors import ObservatoryError, require
from .pilot_reader import inspect_archive
from .policy import CORE_14, scope
from .store import Store

class Observatory:
    def __init__(self,config:Config):
        self.config=config
        self.store=Store(config.database)
    def close(self):self.store.close()
    def import_pilot(self,path,selected=None):
        # All validation and reading happens before any state is persisted.
        source=Path(path).expanduser()
        try:
            result=inspect_archive(source,scope(selected))
            identity,created=self.store.save(result)
            batch=self.store.batch(identity)
            return {"import_id":identity,"imported":created,"replayed":not created,
                "source_batch_id":batch["source_batch_id"],"archive_sha256":batch["archive_sha256"],
                "languages":list(result.selected),"scenarios":15*len(result.selected),
                "source_archive_languages":len(result.source_languages),
                "source_manifest":"NONE_IN_PILOT_ZIP","review_status":"NOT_REVIEWED",
                "linguistically_certified":False,"canonical_readiness":"R0",
                "candidate_total_in_scope":sum(x["candidate_count"] for x in result.languages),
                "warnings":result.warnings}
        except ObservatoryError as e:
            self.store.attempt(source.name,"REJECTED",e.code)
            raise

    def batch(self,import_id=None):return self.store.batch(import_id)
    def batches(self):return self.store.batches()
    def languages(self,import_id=None):
        batch=self.batch(import_id)
        return self.store.languages(batch["import_id"])
    def scenarios(self,language=None,import_id=None):
        batch=self.batch(import_id)
        if language is not None:
            require(language in batch["selected"],"OBS_LANGUAGE_OUT_OF_SCOPE","Language not in selected scope",404)
        return self.store.scenarios(batch["import_id"],language)
    def matrix(self,language,import_id=None):
        batch=self.batch(import_id)
        require(language in batch["selected"],"OBS_LANGUAGE_OUT_OF_SCOPE","Language out of scope",404)
        return matrix(batch,language)
    def status(self,import_id=None):
        try:batch=self.batch(import_id)
        except ObservatoryError as e:
            if import_id is None and e.code=="OBS_BATCH_NOT_FOUND":
                return {"status":"NO_EVIDENCE","languages_in_scope":0,"scenarios_in_scope":0,
                    "human_reviews_completed":0,"linguistically_certified":False,"canonical_readiness":"R0"}
            raise
        return overview(batch,self.store.languages(batch["import_id"]),self.store.scenarios(batch["import_id"]))
    def trends(self,language):
        require(language in CORE_14,"OBS_LANGUAGE_OUT_OF_SCOPE","Language outside core-14 policy",404)
        return trend(self.store.distinct_batches(),language,self.store.languages)
    def report(self,import_id=None):
        batch=self.batch(import_id)
        langs=self.store.languages(batch["import_id"])
        scenarios=self.store.scenarios(batch["import_id"])
        return {"metadata":batch,"overview":overview(batch,langs,scenarios),
                "languages":langs,"scenarios":scenarios,
                "matrices":{code:matrix(batch,code) for code in batch["selected"]}}
