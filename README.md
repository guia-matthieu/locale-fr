# locale-fr : adapter les plugins Claude à la France

Les [plugins officiels d'Anthropic](https://github.com/anthropics/knowledge-work-plugins) (ventes, finance, RH, juridique…) écrivent avec des usages américains : facture « Net 30 + late fee », contrat « at-will », formats de date et de montant, typographie anglaise. Pour une entreprise française, ces sorties sont fausses, et parfois illégales.

`locale-fr` est un plugin Claude Code qui s'installe à côté des plugins officiels et corrige ces réflexes :
- un **skill** `locale`, appelé avant tout texte, document ou calcul destiné à la France ou à l'UE ;
- un **hook** de démarrage qui ajoute une ligne de routage au contexte, pour rendre l'appel du skill systématique ;
- un **paquet typographie** (`packs/FR/typographie.md`) : espaces, guillemets, nombres, dates, montants, majuscules.

## État de cette version (0.3.0)

Les **paquets juridiques** (publicité, prospection, RGPD, vente, facturation, comptabilité, paie, recrutement, travail, contrats, accessibilité, socle UE) existent. Ils ont été vérifiés le 16/11/2026, affirmation par affirmation, contre le texte en vigueur (API Légifrance et Cellar d'EUR-Lex, outils dans `outils/`). Ils sont **en relecture par un professionnel** et seront publiés ensuite. En attendant, le skill signale les usages américains qui ne valent pas en France et liste les points à faire vérifier, sans inventer de règle.

Ce plugin n'est pas un conseil juridique.

## Installer

Dans Claude Code :

```
/plugin marketplace add guia-matthieu/locale-fr
/plugin install locale-fr@guia
```

ou, depuis un clone : `claude --plugin-dir ./locale-fr`.

## Mesure : le skill est-il appelé ?

`banc/` mesure combien de fois le skill est appelé, sur 52 demandes (26 « pièges » qui cachent un point de droit français, 13 neutres, 13 hors UE), 3 essais par demande, avec 1 ou 12 plugins officiels chargés (knowledge-work-plugins @ e91a134), avec et sans le hook.

Résultats du 17/11/2026 (Claude Sonnet, Claude Code 2.1.325) :

| Configuration | Pièges | Neutres | Hors UE | Skill officiel appelé (pièges) |
|---|---|---|---|---|
| 1 plugin officiel (`legal`) + locale-fr sans hook | 75/78 | — | — | 3/78 |
| 12 plugins officiels + locale-fr sans hook | 75/78 | — | — | 3/78 |
| 12 plugins officiels + locale-fr avec hook | 78/78 | 39/39 | 0/13 | 3/78 |

Avec Claude Haiku, sur les pièges et 12 plugins : 69/78 sans hook, 78/78 avec.

La description seule suffit presque toujours, que 1 ou 12 plugins soient chargés : pas d'effet de charge mesurable. Le hook comble les derniers manques (davantage avec Haiku) et ne se déclenche pas hors UE ; il s'applique aussi aux demandes neutres, puisque la typographie vaut pour tout texte en français.

Le banc tourne dans un dossier vierge, avec `--restricted --strict-mcp-config` et sans mémoire ; chaque essai n'est compté que si son en-tête (`init`) ne charge que les plugins prévus, et une sonde vérifie qu'aucun `CLAUDE.md` n'atteint le modèle. Un premier banc, lancé dans un dépôt de travail, chargeait les instructions et la mémoire de son auteur : ses chiffres ont été jetés. Les mesures ont été faites avec les paquets juridiques présents ; la description du skill et le hook sont ceux de cette version, à une phrase près.

```
python3 -I banc/banc.py preparer && python3 -I banc/banc.py lancer lot1 && python3 -I banc/banc.py bilan
```

## Outils de vérification

- `outils/legifrance.py` lit un article en vigueur sur l'API Légifrance (compte PISTE gratuit, identifiants hors dépôt) : `python3 -I outils/legifrance.py travail:L3141-3 "cgi:293 B"`.
- `outils/eurlex.py` lit un article de la dernière version consolidée d'un texte de l'UE par le Cellar, sans compte : `python3 -I outils/eurlex.py 32016R0679:33`.

## Licence et contact

MIT. Par [Guia](https://guia.fr) (Matthieu Crédou). Remarques et corrections : issues de ce dépôt.
