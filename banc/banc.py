"""Test 6 : banc propre. Mesure si le skill `locale` de locale-fr est appelé, selon la charge en skills et le hook.

Isolement (un premier banc, lancé dans un dépôt de travail, chargeait ses instructions et sa mémoire) :
- dossier de travail vierge hors de tout dépôt (~/.cache/locale-fr-banc/projet) ;
- --restricted --strict-mcp-config : ni CLAUDE.md utilisateur, ni MCP, ni réglages utilisateur ;
  CLAUDE_CODE_DISABLE_AUTO_MEMORY=1 : pas de mémoire ;
- outils réduits à Skill et Read, lecture limitée au dossier de travail et aux dossiers des plugins ;
- copies des plugins hors dépôt, régénérées à chaque lancement depuis ../locale-fr ;
- chaque essai ne compte que si son en-tête `init` est conforme (verifier_entete) ;
- une sonde vérifie avant chaque lot qu'aucun CLAUDE.md n'est chargé (l'en-tête ne le montre pas).

usage : python3 -I banc.py preparer | sonde | lancer [lot1|haiku] | bilan
"""
import collections, concurrent.futures as cf, json, os, pathlib, shutil, subprocess, sys

ICI = pathlib.Path(__file__).resolve().parent
BASE = pathlib.Path.home() / ".cache" / "locale-fr-banc"
KWP = BASE / "kwp"
KWP_REV = "e91a134"
PLUGINS = BASE / "plugins"
PROJET = BASE / "projet"
SORTIES = ICI / "sorties"  # sorties brutes : chemins du poste, jamais publiées telles quelles
OFFICIELS = ["marketing", "sales", "customer-support", "finance", "human-resources", "legal",
             "design", "data", "operations", "product-management", "engineering", "small-business"]
CHARGES = {"un": ["legal"], "douze": OFFICIELS}
VARIANTES = ("sanshook", "hook")
ESSAIS = 3
ENV = {**os.environ, "CLAUDE_CODE_DISABLE_AUTO_MEMORY": "1"}
COMMUN = ["--restricted", "--strict-mcp-config", "--setting-sources", "project",
          "--add-dir", str(PLUGINS), "--add-dir", str(KWP), "--tools", "Skill,Read", "--allowedTools", "Skill", "Read"]
# skills intégrés à Claude Code (sans préfixe de plugin) : liste relevée par `preparer`, propre à la version
INTEGRES = ICI / "skills-integres.txt"


def demandes():
    for f in sorted(ICI.glob("demandes-*.tsv")):
        for n, l in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            c = l.split("\t")
            if len(c) >= 4 and c[1] in ("piege", "neutre", "hors"):
                yield f"{f.stem[9:]}-{c[0].replace('/', '_')}-{c[1]}-{n}", c[0], c[1], c[2], c[3]


def lots(lot):
    """(nom, charge, variante, modèle, type, demande)."""
    for ident, _, typ, dem, _ in demandes():
        if lot == "lot1":
            cases = [("un", "sanshook"), ("douze", "sanshook"), ("douze", "hook")] if typ == "piege" else \
                    [("douze", "hook")]
            modele = "sonnet"
        elif lot == "haiku":
            cases = [("douze", "sanshook"), ("douze", "hook")] if typ == "piege" else []
            modele = "haiku"
        else:
            raise SystemExit(f"lot inconnu : {lot}")
        for charge, var in cases:
            for k in range(1, (1 if typ == "hors" else ESSAIS) + 1):
                yield f"{charge}-{var}__{modele}__{ident}__{k}", charge, var, modele, typ, dem


def preparer():
    if not (KWP / ".git").exists():
        subprocess.run(["git", "clone", "-q", "https://github.com/anthropics/knowledge-work-plugins.git", str(KWP)], check=True)
    subprocess.run(["git", "-C", str(KWP), "checkout", "-q", KWP_REV], check=True)
    for var in VARIANTES:
        dest = PLUGINS / var / "locale-fr"
        shutil.rmtree(dest, ignore_errors=True)
        shutil.copytree(ICI.parent / "locale-fr", dest, ignore=shutil.ignore_patterns(*(["hooks"] if var == "sanshook" else []), ".DS_Store"))
    PROJET.mkdir(parents=True, exist_ok=True)
    if subprocess.run(["git", "-C", str(PROJET), "rev-parse"], capture_output=True).returncode == 0:
        raise SystemExit(f"{PROJET} est dans un dépôt git : banc non propre")
    if any(PROJET.iterdir()):
        raise SystemExit(f"{PROJET} n'est pas vide")
    print("prêt :", KWP_REV, [str(p.relative_to(BASE)) for p in PLUGINS.glob("*/locale-fr")])


def commande(charge, var, modele, dem):
    dirs = sum((["--plugin-dir", str(KWP / p)] for p in CHARGES[charge]), [])
    return ["claude", "-p", dem, *dirs, "--plugin-dir", str(PLUGINS / var / "locale-fr"), *COMMUN,
            "--model", modele, "--output-format", "stream-json", "--verbose"]


def entete(p):
    for l in p.read_text(encoding="utf-8").splitlines():
        try:
            m = json.loads(l)
        except json.JSONDecodeError:
            continue
        if m.get("subtype") == "init":
            return m
    return None


def verifier_entete(m, charge):
    """Liste des écarts de l'en-tête init par rapport au banc propre (vide = conforme)."""
    if m is None:
        return ["pas d'en-tête init"]
    e = []
    if m.get("cwd") != str(PROJET):
        e.append(f"cwd {m.get('cwd')}")
    if m.get("mcp_servers"):
        e.append(f"{len(m['mcp_servers'])} serveurs MCP")
    if sorted(m.get("tools") or []) != ["Read", "Skill"]:
        e.append(f"{len(m.get('tools') or [])} outils au lieu de Read et Skill")
    attendus = set(CHARGES[charge]) | {"locale-fr"}
    hors = [p["name"] for p in m.get("plugins", []) if p["name"] not in attendus and not p.get("source", "").endswith("@builtin")]
    if hors:
        e.append(f"plugins en trop {hors}")
    integres = set(INTEGRES.read_text().split()) if INTEGRES.exists() else set()
    for s in m.get("skills", []):
        pref = s.split(":")[0] if ":" in s else None
        if (pref and pref not in attendus) or (not pref and s not in integres):
            e.append(f"skill inattendu {s}")
    if not any(s == "locale-fr:locale" for s in m.get("skills", [])):
        e.append("skill locale-fr:locale absent")
    if any(k for k in m if "memory" in k and m[k]):
        e.append("mémoire chargée")
    return e


def lire(nom):
    """(skills appelés, texte, écarts d'en-tête) ou None si l'essai est absent, en erreur ou coupé par la limite."""
    p = SORTIES / f"{nom}.jsonl"
    if not p.exists():
        return None
    skills, texte, erreur = [], "", False
    for l in p.read_text(encoding="utf-8").splitlines():
        try:
            m = json.loads(l)
        except json.JSONDecodeError:
            continue
        if m.get("type") == "assistant":
            for c in m["message"].get("content", []):
                if c.get("type") == "tool_use" and c["name"] == "Skill":
                    skills.append(c["input"].get("skill") or "")
        if m.get("type") == "result":
            texte, erreur = m.get("result") or "", bool(m.get("is_error"))
    if not texte or erreur or ("limit" in texte.lower()[:200] and len(texte) < 300):
        return None
    return skills, texte, verifier_entete(entete(p), nom.split("-")[0])


def sonde():
    """Échoue si un CLAUDE.md (ou un autre contexte utilisateur) atteint le modèle dans la config du banc."""
    q = ("Test technique. As-tu reçu, dans ce contexte, des instructions issues d'un fichier CLAUDE.md ou d'une "
         "mémoire ? Réponds par un seul mot en première ligne : AUCUNE ou OUI ; si OUI, cite la première ligne.")
    out = subprocess.run(["claude", "-p", q, *COMMUN[:-5], "--tools", "", "--model", "haiku"], cwd=PROJET, env=ENV,
                         stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=300).stdout.strip()
    ok = out.upper().startswith("AUCUNE")
    print("sonde :", "OK" if ok else "ÉCHEC", "|", out[:200].replace("\n", " "))
    return ok


def lancer(lot="lot1"):
    preparer_si_besoin()
    if not sonde():
        raise SystemExit("contexte utilisateur détecté : rien n'est lancé")
    SORTIES.mkdir(exist_ok=True)
    plan = list(lots(lot))
    echecs = 0

    def un(e):
        nom, charge, var, modele, _, dem = e
        if lire(nom) is not None:
            return nom, "déjà fait"
        with open(SORTIES / f"{nom}.jsonl", "w", encoding="utf-8") as fh:
            subprocess.run(commande(charge, var, modele, dem), cwd=PROJET, env=ENV, stdin=subprocess.DEVNULL,
                           stdout=fh, stderr=subprocess.STDOUT, timeout=900)
        r = lire(nom)
        return nom, "ÉCHEC" if r is None else ("EN-TÊTE NON CONFORME " + "; ".join(r[2]) if r[2] else "ok")

    with cf.ThreadPoolExecutor(6) as ex:
        for nom, st in ex.map(un, plan):
            print(st, nom, flush=True)
            echecs = echecs + 1 if st == "ÉCHEC" else 0
            if echecs >= 6:  # probablement la limite d'usage : on arrête, relancer reprend où on en est
                print("6 échecs de suite : arrêt (limite d'usage ?). Relancer plus tard reprend les essais manquants.")
                ex.shutdown(wait=False, cancel_futures=True)
                break


def preparer_si_besoin():
    if not (KWP / ".git").exists() or not all((PLUGINS / v / "locale-fr").exists() for v in VARIANTES):
        preparer()


def bilan(_=None):
    appel = collections.defaultdict(lambda: [0, 0])
    officiel = collections.defaultdict(lambda: [0, 0])
    manquants, non_conformes = 0, 0
    for lot in ("lot1", "haiku"):
        for nom, charge, var, modele, typ, _ in lots(lot):
            r = lire(nom)
            if r is None:
                manquants += 1
                continue
            s, _, ecarts = r
            if ecarts:
                non_conformes += 1
                continue
            k = (f"{charge}-{var}", modele, typ)
            appel[k][1] += 1; officiel[k][1] += 1
            appel[k][0] += any(x.endswith(":locale") for x in s)
            officiel[k][0] += any(x and not x.endswith(":locale") for x in s)

    def f(c):
        return f"{c[0]}/{c[1]}" if c[1] else "—"

    out = ["# Bilan test 6 (banc propre)", "", f"Essais manquants ou en erreur : {manquants}",
           f"Essais écartés (en-tête non conforme) : {non_conformes}", "",
           "## Appel du skill `locale` (au moins une fois dans l'essai)", "",
           "| Série | Pièges Sonnet | Pièges Haiku | Neutres Sonnet | Hors UE Sonnet | Skill officiel appelé (pièges Sonnet) |",
           "|---|---|---|---|---|---|"]
    for s in ("un-sanshook", "douze-sanshook", "douze-hook"):
        out.append(f"| {s} | {f(appel[(s,'sonnet','piege')])} | {f(appel[(s,'haiku','piege')])} | "
                   f"{f(appel[(s,'sonnet','neutre')])} | {f(appel[(s,'sonnet','hors')])} | {f(officiel[(s,'sonnet','piege')])} |")
    (ICI / "BILAN.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print("\n".join(out))


if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "bilan"
    {"preparer": lambda: preparer(), "sonde": lambda: sonde(), "bilan": lambda: bilan(),
     "lancer": lambda: lancer(sys.argv[2] if len(sys.argv) > 2 else "lot1")}[action]()
