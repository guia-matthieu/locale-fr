"""Lire un article d'un texte de l'UE par le Cellar (Office des publications), sans compte ni identifiant.

usage : python3 -I eurlex.py [--json] [--origine] CELEX:article [...]
  ex. : 32016R0679:33   32024R1689:50   32019L0882:4
Par défaut, prend la dernière version consolidée (CELEX 0…) si elle existe, sinon le texte publié au JO.
--origine : force le texte publié au JO. --json : une ligne JSON par demande.
"""
import html, json, pathlib, re, sys, urllib.parse, urllib.request

SPARQL = "https://publications.europa.eu/webapi/rdf/sparql"
CELLAR = "https://publications.europa.eu/resource/celex/"
CACHE = pathlib.Path.home() / ".cache" / "eurlex"
UA = {"User-Agent": "locale-fr-verif/1.0"}


def consolidee(celex):
    """CELEX et date de la dernière version consolidée, ou (None, None)."""
    base = "0" + celex[1:]
    q = f"""PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
SELECT ?celex ?date WHERE {{ ?act cdm:resource_legal_id_celex "{celex}"^^<http://www.w3.org/2001/XMLSchema#string> .
 ?cons cdm:act_consolidated_consolidates_resource_legal ?act . ?cons cdm:resource_legal_id_celex ?celex .
 OPTIONAL {{ ?cons cdm:act_consolidated_date ?date }} FILTER(STRSTARTS(STR(?celex), "{base}")) }} ORDER BY DESC(?celex) LIMIT 1"""
    req = urllib.request.Request(SPARQL, data=urllib.parse.urlencode({"query": q}).encode(),
                                 headers={**UA, "Accept": "application/sparql-results+json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        b = json.load(r)["results"]["bindings"]
    return (b[0]["celex"]["value"], b[0].get("date", {}).get("value")) if b else (None, None)


def texte_complet(celex):
    f = CACHE / f"{celex}.txt"
    if f.exists():
        return f.read_text()
    req = urllib.request.Request(CELLAR + celex, headers={**UA, "Accept": "application/xhtml+xml, text/html;q=0.9",
                                                          "Accept-Language": "fra"})
    with urllib.request.urlopen(req, timeout=120) as r:
        brut = r.read().decode("utf-8", "ignore")
    brut = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", brut)
    brut = re.sub(r"(?i)<(br|/p|/div|/tr|/h\d|/li|/table)[^>]*>", "\n", brut)
    t = html.unescape(re.sub(r"<[^>]+>", " ", brut))
    t = "\n".join(" ".join(l.split()) for l in t.splitlines())
    t = re.sub(r"\n{2,}", "\n", t)
    CACHE.mkdir(parents=True, exist_ok=True)
    f.write_text(t)
    return t


def article(t, num):
    """Texte de l'article num : de la ligne « Article num » à la ligne « Article suivant »."""
    lignes = t.splitlines()
    tete = re.compile(rf"^Article {re.escape(num)}$")
    debuts = [i for i, l in enumerate(lignes) if tete.match(l.strip())]
    if not debuts:
        return ""
    i = debuts[0]  # première occurrence : le corps du texte (les suivantes sont des annexes ou tableaux)
    fin = next((j for j in range(i + 1, len(lignes)) if re.match(r"^(Article \d+[a-z]*( bis| ter)?|(▼\w+ )?(CHAPITRE|SECTION|TITRE|ANNEXE)\b.*|▼\w+)$", lignes[j].strip())
                and not re.match(r"^▼\w+$", lignes[j].strip()) or re.match(r"^(▼\w+ )?(CHAPITRE|SECTION|TITRE|ANNEXE) ", lignes[j].strip())), len(lignes))
    return " ".join(lignes[i:fin])


if __name__ == "__main__":
    origine, sortie_json = "--origine" in sys.argv, "--json" in sys.argv
    for d in [x for x in sys.argv[1:] if not x.startswith("--")]:
        celex, _, num = d.partition(":")
        version, date, note = celex, None, ""
        try:
            if not origine:
                c, date = consolidee(celex)
                if c:
                    version = c
            txt = article(texte_complet(version), num)
            if not txt:
                note = "ARTICLE INTROUVABLE (numéro, ou découpage du texte à revoir)"
        except Exception as e:
            txt, note = "", f"ERREUR {type(e).__name__}: {e}"
        if sortie_json:
            print(json.dumps({"demande": d, "version": version, "consolidee_au": date, "note": note, "texte": txt},
                             ensure_ascii=False))
        else:
            print(f"## {d} — version {version}" + (f" (consolidée au {date})" if date else "") + (f" — {note}" if note else ""))
            print(txt)
            print()
