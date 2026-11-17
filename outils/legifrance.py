"""Lire un article sur l'API Légifrance (DILA, via PISTE).

Identifiants lus, jamais dans le dépôt, dans ~/.config/piste/legifrance.env ou legifrance-sandbox.env :
    CLIENT_ID=... / CLIENT_SECRET=...        (production)
    SB_OAUTH_ID=... / SB_ID_KEY=...          (--sandbox)
ou à défaut dans le trousseau macOS : service « piste-legifrance-prod » (production)
ou « piste-legifrance » (--sandbox), comptes « client_id » et « client_secret » :
    security add-generic-password -s piste-legifrance-prod -a client_id -w
    security add-generic-password -s piste-legifrance-prod -a client_secret -w

usage : python3 -I legifrance.py [--sandbox] [--json] LEGIARTI000051828335 travail:L3141-3 cgi:"293 B" [...]
  code:numéro = article en vigueur de ce code (codes : voir CODES ci-dessous) ; --json = une ligne JSON par article
Affiche, pour chaque article : numéro, état, dates de début et de fin de la version, texte brut.
"""
import json, subprocess, sys, urllib.parse, urllib.request
import html, pathlib, re

SANDBOX = "--sandbox" in sys.argv
OAUTH = f"https://{'sandbox-' if SANDBOX else ''}oauth.piste.gouv.fr/api/oauth/token"
SERVICE = "piste-legifrance" if SANDBOX else "piste-legifrance-prod"
API = f"https://{'sandbox-' if SANDBOX else ''}api.piste.gouv.fr/dila/legifrance/lf-engine-app"


ENVS = [pathlib.Path.home() / ".config" / "piste" / n for n in ("legifrance.env", "legifrance-sandbox.env")]
# noms acceptés dans les fichiers .env (hors dépôt), production puis sandbox
NOMS = {False: {"client_id": ["CLIENT_ID"], "client_secret": ["CLIENT_SECRET"]},
        True: {"client_id": ["SB_OAUTH_ID", "SB_CLIENT_ID"], "client_secret": ["SB_ID_KEY", "SB_CLIENT_SECRET"]}}


CODES = {"travail": "LEGITEXT000006072050", "consommation": "LEGITEXT000006069565", "commerce": "LEGITEXT000005634379",
         "cgi": "LEGITEXT000006069577", "cgi-ann2": "LEGITEXT000006069569", "cgi-ann3": "LEGITEXT000006069574",
         "cgi-ann4": "LEGITEXT000006069576", "civil": "LEGITEXT000006070721", "cpce": "LEGITEXT000006070987",
         "secu": "LEGITEXT000006073189", "cpi": "LEGITEXT000006069414", "cmf": "LEGITEXT000006072026",
         "penal": "LEGITEXT000006070719", "cpc": "LEGITEXT000006070716", "cpce-exec": "LEGITEXT000025024948",
         "assurances": "LEGITEXT000006073984", "cch": "LEGITEXT000006074096", "environnement": "LEGITEXT000006074220", "csp": "LEGITEXT000006072665", "education": "LEGITEXT000006071191", "cibs": "LEGITEXT000044595989"}


CACHE = pathlib.Path.home() / ".cache" / "legifrance"


def index_code(tok, code):
    """numéro d'article -> identifiant de la version en vigueur, depuis la table des matières du code (cache du jour)."""
    import datetime
    jour = datetime.date.today().isoformat()
    f = CACHE / f"{code}-{jour}{'-sandbox' if SANDBOX else ''}.json"
    if f.exists():
        return json.loads(f.read_text())
    r = appel(tok, "/consult/legi/tableMatieres", {"textId": CODES[code], "date": jour, "nature": "CODE"})
    idx = {}

    def parcours(n):
        for a in n.get("articles") or []:
            num = " ".join((a.get("num") or "").split())
            if num and (a.get("etat") == "VIGUEUR" or num not in idx):
                idx[num] = a.get("id")
        for s in n.get("sections") or []:
            parcours(s)
    parcours(r)
    CACHE.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(idx))
    return idx


def secret(compte):
    # 1) fichiers ~/.config/piste/*.env : CLE=valeur
    vals = {}
    for f in ENVS:
        if f.exists():
            for ligne in f.read_text().splitlines():
                cle, _, val = ligne.partition("=")
                val = val.strip().strip('"').strip("'")
                if val:
                    vals.setdefault(cle.strip().upper(), val)
    for nom in NOMS[SANDBOX][compte]:
        if vals.get(nom):
            return vals[nom]
    # 2) sinon, trousseau macOS
    return subprocess.run(["security", "find-generic-password", "-s", SERVICE, "-a", compte, "-w"],
                          capture_output=True, text=True, check=True).stdout.strip()


def jeton():
    data = urllib.parse.urlencode({"grant_type": "client_credentials", "client_id": secret("client_id"),
                                   "client_secret": secret("client_secret"), "scope": "openid"}).encode()
    with urllib.request.urlopen(urllib.request.Request(OAUTH, data=data), timeout=30) as r:
        return json.load(r)["access_token"]


def appel(tok, chemin, corps):
    req = urllib.request.Request(API + chemin, data=json.dumps(corps).encode(), method="POST",
                                 headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json",
                                          "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def date(ms):
    import datetime
    return datetime.datetime.fromtimestamp(ms / 1000, datetime.timezone.utc).date().isoformat() if ms else "?"


def texte(a):
    brut = a.get("texteHtml") or a.get("texte") or ""
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", brut)).split())


if __name__ == "__main__":
    ids = [x for x in sys.argv[1:] if not x.startswith("--")]
    tok = jeton()
    sortie_json = "--json" in sys.argv
    for i in ids:
        try:
            if ":" in i:
                code, num = i.split(":", 1)
                ident = index_code(tok, code).get(" ".join(num.split()))
                a = (appel(tok, "/consult/getArticle", {"id": ident}).get("article") or {}) if ident else {}
            else:
                a = appel(tok, "/consult/getArticle", {"id": i}).get("article") or {}
            note = ""
            if a.get("etat") not in ("VIGUEUR", "ABROGE_DIFF"):  # ABROGE_DIFF = en vigueur, remplacé à une date future
                v = [x for x in a.get("articleVersions") or [] if x.get("etat") == "VIGUEUR"]
                if v:
                    note = f"{i} est la version {a.get('etat')} du {date(a.get('dateDebut'))}"
                    a = appel(tok, "/consult/getArticle", {"id": v[0]["id"]}).get("article") or a
            if not a.get("id"):
                note = "INTROUVABLE (numéro ou code à corriger)"
        except Exception as e:  # article introuvable, code inconnu, erreur réseau
            a, note = {}, f"ERREUR {type(e).__name__}: {e}"
        futures = [f"{x.get('etat')} le {date(x.get('dateDebut'))} ({x.get('id')})"
                   for x in a.get("articleVersions") or [] if x.get("etat") in ("VIGUEUR_DIFF", "ABROGE_DIFF")
                   and x.get("id") != a.get("id")]
        if a.get("etat") == "ABROGE_DIFF":
            futures.insert(0, f"version actuelle remplacée le {date(a.get('dateFin'))}")
        if sortie_json:
            print(json.dumps({"demande": i, "id": a.get("id"), "num": a.get("num"), "etat": a.get("etat"),
                              "debut": date(a.get("dateDebut")), "fin": date(a.get("dateFin")),
                              "note": note, "a_venir": futures, "texte": texte(a)}, ensure_ascii=False))
        else:
            if note:
                print(f"(note : {note})")
            print(f"## {a.get('num', '?')} ({a.get('id') or i}) — {a.get('etat', '?')}, du {date(a.get('dateDebut'))} au {date(a.get('dateFin'))}")
            for f in futures:
                print(f"  ⚠ à venir : {f}")
            print(texte(a) or "(texte vide)")
            print()
