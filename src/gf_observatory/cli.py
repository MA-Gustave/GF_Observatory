"""Thin CLI over the single Observatory use-case service."""
import argparse
import json
import sys
from pathlib import Path
from .config import load_config
from .errors import ObservatoryError
from .jsonsafe import dumps
from .service import Observatory
from .policy import CORE_14


def parser():
    p=argparse.ArgumentParser(prog="gf-observatory",description="Read-only GF WordBench evidence observatory")
    p.add_argument("--config",help="Path to observatory.toml; defaults to current directory")
    sub=p.add_subparsers(dest="command",required=True)
    sub.add_parser("doctor")
    imp=sub.add_parser("import-pilot",help="Import a real technical pilot ZIP without certifying it")
    imp.add_argument("zip",type=Path)
    imp.add_argument("--languages",nargs="+",help="Subset of documented core 14; default all 14")
    verify=sub.add_parser("verify-pilot",help="Read and verify pilot ZIP without writing SQLite")
    verify.add_argument("zip",type=Path)
    verify.add_argument("--languages",nargs="+",help="Explicit subset of the core fourteen")
    sub.add_parser("batches")
    s=sub.add_parser("status");s.add_argument("--batch-id")
    ls=sub.add_parser("languages");ls.add_argument("--batch-id")
    sc=sub.add_parser("scenarios");sc.add_argument("--batch-id");sc.add_argument("--language")
    m=sub.add_parser("matrix");m.add_argument("language");m.add_argument("--batch-id")
    t=sub.add_parser("trends");t.add_argument("language")
    r=sub.add_parser("report");r.add_argument("--batch-id");r.add_argument("--format",choices=("json","markdown"),default="json");r.add_argument("--output",type=Path)
    b=sub.add_parser("backup");b.add_argument("output",type=Path)
    ex=sub.add_parser("export-static");ex.add_argument("output",type=Path);ex.add_argument("--batch-id")
    ex.add_argument("--acknowledge-candidate-publication",action="store_true")
    sub.add_parser("serve")
    sub.add_parser("gui")
    return p


def markdown_report(report):
    r=report["overview"];lines=["# GF Observatory — rapport de preuves pilotes", "",
     "**Avertissement : candidates techniques, non approuvées linguistiquement.**", "",
     f"- Lot source : `{r['source_batch_id']}`",
     f"- Empreinte de l'archive : `{r['source_archive_sha256']}`",
     f"- Langues du périmètre : {r['languages_in_scope']}",
     f"- Scénarios : {r['scenarios_in_scope']}",
     f"- Candidats techniques : {r['candidate_for_review']}",
     f"- Échecs : {r['probe_failed']}",
     "- Certification linguistique : **non vérifiée**", "- Readiness canonique : **R0** (manifeste canonique absent)", "",
     "| Langue | Candidats / 15 | Échecs | Revue humaine |", "|---|---:|---:|---|" ]
    for lang in report["languages"]:
        lines.append(f"| {lang['code']} | {lang['candidate_count']} | {lang['failed_count']} | Non effectuée |")
    lines.append("\nAucun RuntimeSet n'a été publié ni activé.\n")
    return "\n".join(lines)


def main(argv=None):
    args=parser().parse_args(argv)
    try:
        cfg=load_config(args.config)
        if args.command=="doctor":
            result={"application":"GF Observatory","status":"LOCAL_CONFIG_OK",
                "python":sys.version.split()[0],"api_bind":cfg.bind,"api_port":cfg.port,
                "db_location":str(cfg.database),"source_writes":False,
                "core_languages":list(CORE_14),"real_pilot_reader":"defluens.pilot-batch/1.0",
                "canonical_wordbench_reader":"NOT_QUALIFIED_WITH_REAL_SAMPLE"}
        elif args.command=="verify-pilot":
            from .pilot_reader import inspect_archive
            b=inspect_archive(args.zip,args.languages)
            result={"status":"ARCHIVE_VERIFIED_PILOT_ONLY","archive_sha256":b.archive_sha256,
                "source_batch_id":b.batch_id,"source_languages":len(b.source_languages),
                "selected_languages":list(b.selected),"scenarios_selected":len(b.scenarios),
                "candidates_selected":sum(x["candidate_count"] for x in b.languages),
                "source_totals":b.totals,"surface_warnings":b.warnings,
                "producer_manifest_verified":False,"human_review_completed":False,
                "linguistically_certified":False}
        elif args.command=="serve":
            from .api import serve
            serve(cfg);return 0
        elif args.command=="gui":
            from .desktop import launch
            launch(cfg);return 0
        else:
            app=Observatory(cfg)
            try:
                if args.command=="import-pilot": result=app.import_pilot(args.zip,args.languages)
                elif args.command=="batches": result=app.batches()
                elif args.command=="status": result=app.status(args.batch_id)
                elif args.command=="languages":result=app.languages(args.batch_id)
                elif args.command=="scenarios":result=app.scenarios(args.language,args.batch_id)
                elif args.command=="matrix":result=app.matrix(args.language,args.batch_id)
                elif args.command=="trends":result=app.trends(args.language)
                elif args.command=="report":
                    result=app.report(args.batch_id)
                    if args.format=="markdown":
                        text=markdown_report(result)
                        if args.output:
                            args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(text,encoding="utf8")
                            print(json.dumps({"report_path":str(args.output),"format":"markdown"},ensure_ascii=False));return 0
                        print(text);return 0
                    if args.output:
                        args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_bytes(dumps(result)+b"\n")
                        print(json.dumps({"report_path":str(args.output),"format":"json"},ensure_ascii=False));return 0
                elif args.command=="backup":result=app.store.backup(args.output)
                elif args.command=="export-static":
                    from .static_export import export_static
                    result=export_static(app,args.output,args.batch_id,args.acknowledge_candidate_publication)
                else:raise ObservatoryError("OBS_COMMAND_UNKNOWN","Unsupported command",404)
            finally:app.close()
        print(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False))
        return 0
    except ObservatoryError as exc:
        print(json.dumps({"error":{"code":exc.code,"message":str(exc)}},ensure_ascii=False),file=sys.stderr)
        return 4
    except (OSError, ValueError) as exc:
        print(json.dumps({"error":{"code":"OBS_IO_ERROR","message":str(exc)}},ensure_ascii=False),file=sys.stderr)
        return 5

if __name__=="__main__":raise SystemExit(main())
