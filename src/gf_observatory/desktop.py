"""Optional Tkinter desktop: same import service as the CLI, web UI stays read-only."""
from __future__ import annotations
from pathlib import Path
import queue
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import webbrowser
from .config import Config
from .service import Observatory
from .api import new_server
from .errors import ObservatoryError

class Desktop:
    def __init__(self,config:Config):
        self.config=config
        self.window=tk.Tk()
        self.window.title("GF Observatory — Atelier de preuves")
        self.window.geometry("880x650")
        self.window.minsize(700,550)
        self.queue=queue.Queue()
        self.worker=None
        self.server=None
        self.server_thread=None
        style=ttk.Style(self.window)
        if "clam" in style.theme_names():style.theme_use("clam")
        base=ttk.Frame(self.window,padding=22);base.pack(fill="both",expand=True)
        head=tk.Frame(base,bg="#152e46",padx=18,pady=16);head.pack(fill="x")
        tk.Label(head,text="GF Observatory",bg="#152e46",fg="white",font=("Segoe UI",20,"bold")).pack(anchor="w")
        tk.Label(head,text="14 langues · 15 capacités utiles · lecture seule des preuves WordBench",bg="#152e46",fg="#c8dae5").pack(anchor="w")
        notice=tk.Label(base,text="Les résultats GF sont des candidats à la revue humaine, pas une qualification linguistique.\n"
          "L'application ne lance pas GF et ne modifie jamais WordBench.",bg="#fff0d1",fg="#725323",justify="left",padx=13,pady=11)
        notice.pack(fill="x",pady=(17,13))
        controls=ttk.Frame(base);controls.pack(fill="x")
        self.import_button=ttk.Button(controls,text="Importer un ZIP pilote WordBench…",command=self.choose_import)
        self.import_button.pack(side="left",padx=(0,7))
        ttk.Button(controls,text="Ouvrir le tableau de bord",command=self.open_dashboard).pack(side="left",padx=7)
        ttk.Button(controls,text="Actualiser",command=self.refresh).pack(side="left",padx=7)
        self.state=tk.StringVar(value="Prêt — ZIP techniques complets uniquement")
        ttk.Label(base,textvariable=self.state).pack(anchor="w",pady=12)
        self.prog=ttk.Progressbar(base,mode="indeterminate")
        self.prog.pack(fill="x",pady=(0,13))
        panel=ttk.LabelFrame(base,text=" État des preuves persistées ",padding=12);panel.pack(fill="both",expand=True)
        self.display=tk.Text(panel,wrap="word",font=("Consolas",10),background="#f8fafc",height=18)
        self.display.pack(fill="both",expand=True)
        self.display.configure(state="disabled")
        self.window.protocol("WM_DELETE_WINDOW",self.close)
        self.window.after(120,self.poll)
        self.refresh()

    def set_text(self,text):
        self.display.configure(state="normal");self.display.delete("1.0","end")
        self.display.insert("1.0",text);self.display.configure(state="disabled")

    def refresh(self):
        app=Observatory(self.config)
        try:
            s=app.status();rows=app.languages() if s.get("batch_id") else []
        finally:app.close()
        if not rows:self.set_text("Aucune campagne importée. Sélectionne une archive defluens-batch-full-*.zip.")
        else:
            lines=[f"Lot : {s['source_batch_id']}",f"Archive SHA-256 : {s['source_archive_sha256']}",
             f"Langues retenues : {s['languages_in_scope']}",f"Scénarios : {s['scenarios_in_scope']}",
             f"Candidats GF : {s['candidate_for_review']} — Revues humaines : 0",
             "Readiness canonique : R0 (non qualifiée)","", "LANGUES / CANDIDATS / ALERTES", ""]
            for l in rows:lines.append(f"{l['code']:4}  {l['candidate_count']:2}/15  {l['technical_status']}")
            self.set_text("\n".join(lines))

    def choose_import(self):
        if self.worker and self.worker.is_alive():return
        filename=filedialog.askopenfilename(title="Archive pilote WordBench (full)",
            filetypes=[("Archive WordBench", "*.zip"),("Tous les fichiers","*.*")])
        if not filename:return
        self.state.set("Vérification intégrale des preuves ZIP…")
        self.import_button.configure(state="disabled");self.prog.start(8)
        def work():
            app=Observatory(self.config)
            try:self.queue.put(("ok",app.import_pilot(filename)))
            except Exception as e:self.queue.put(("error",str(e)))
            finally:app.close()
        self.worker=threading.Thread(target=work,daemon=True);self.worker.start()

    def poll(self):
        try:
            while True:
                state,value=self.queue.get_nowait()
                self.prog.stop();self.import_button.configure(state="normal")
                if state=="ok":
                    self.state.set("Lot importé — 210 candidats techniques, revue humaine non effectuée")
                    self.refresh()
                else:
                    self.state.set("Import refusé (aucun verdict inventé)")
                    messagebox.showerror("Import refusé",value)
        except queue.Empty:pass
        self.window.after(120,self.poll)

    def open_dashboard(self):
        if self.server is None:
            try:
                self.server=new_server(self.config)
            except OSError as e:
                messagebox.showerror("Serveur indisponible",str(e));return
            self.server_thread=threading.Thread(target=self.server.serve_forever,kwargs={"poll_interval":0.1},daemon=True)
            self.server_thread.start()
        webbrowser.open(f"http://127.0.0.1:{self.config.port}/",new=2)

    def close(self):
        if self.worker and self.worker.is_alive():
            if not messagebox.askyesno("Import en cours","Fermer et abandonner la fenêtre ? La vérification se terminera sans publication."):
                return
        if self.server is not None:
            self.server.shutdown();self.server.server_close()
        self.window.destroy()
    def run(self):self.window.mainloop()


def launch(config:Config):
    Desktop(config).run()
