---
juridiction: FR
domaine: typographie
base: EU
complete:
  - design:ux-copy
  - design:design-system
  - design:design-handoff
  - marketing:*
  - data:create-viz
  - data:build-dashboard
  - small-business:canva-creator
  - small-business:social-content-engine
verifie_le: non vérifié (brouillon du 2026-11-15 ; section espaces réécrite le 2026-11-16)
revoir_avant: 2027-05-15
sources: Lexique des règles typographiques en usage à l'Imprimerie nationale ; CLDR (locale fr-FR) ; Académie française ; brouillon rédigé de mémoire, à relire par un humain
---

# Paquet FR : typographie et formats fr-FR

**Application silencieuse.** Tout texte en français destiné à la France suit ces règles. Aucun commentaire, aucune section, aucune note ou parenthèse sur la typographie appliquée (espaces, formats, dates) : le texte sort déjà bien composé. Ce paquet n'a pas de tableau de contrôle.

**Exception.** Code, CSV, JSON, noms de champs, URL : garder les formats machine (point décimal, ISO 8601 `2026-11-15`). Seul l'affichage passe en fr-FR (`Intl.NumberFormat('fr-FR')`, `toLocaleDateString('fr-FR')`, locale d3 `fr-FR`).

## Espaces avant la ponctuation haute et dans les nombres

**Constat du 16/11/2026** : la sortie texte de Claude ne contient jamais d'espace insécable (U+00A0, U+202F), même quand on lui demande de recopier un texte qui en contient. Ne pas promettre d'insécables dans la prose, ne pas en parler.

- **Prose** : une espace simple avant `;` `!` `?` `:` `»` `€` `%`, après `«`, entre les milliers (1 234,50 €), dans `14 h 30`, `n° 5`, `M. Martin`. Jamais de ponctuation collée (`Bonjour!`, `12,50€`).
- **Code, HTML, gabarits** : écrire les insécables en échappement ASCII, qui survit : `&#8239;` ou `\u202F` (fine) avant `;` `!` `?`, après `«`, avant `»`, entre les milliers ; `&nbsp;` ou `\u00A0` avant `:` `€` `%`, unités, `14&nbsp;h&nbsp;30`. Nombres et dates affichés : `Intl.NumberFormat('fr-FR')`, `toLocaleDateString('fr-FR')`, locale d3 `fr-FR` (insèrent eux-mêmes la fine U+202F).
- Rien avant `.` `,` `)`.

## Guillemets

- Premier niveau `« »`, fines insécables à l'intérieur.
- Second niveau, dans une citation : `“ ”` sans espace. Jamais `"` droits dans un texte rédigé.
- Apostrophe typographique `’` (U+2019) dans la prose ; `'` reste dans le code.

## Nombres, monnaie, pourcentages

- Milliers séparés par une espace insécable, virgule décimale : 1 234,56. Séparer dès 1 000 (l'IN tolère 1234 en tableau, à vérifier).
- Années, numéros de page, codes : jamais séparés (2026, 75002).
- Monnaie après le montant : 12,50 € ; 1 250,00 €. Jamais `€12.50` ni `12.50€`.
- Montants ronds : 15 € ou 15,00 € (cohérent dans un même document).
- Grands nombres en abrégé : 1,2 k€, 3,4 M€, 2 Md€. **Billion américain = milliard.** `$1.2B` devient 1,2 Md$.
- Pourcentage : 12,5 %.
- Axes et infobulles de graphique : mêmes règles.

## Dates et heures

- Toutes lettres : 15 novembre 2026. Jour et mois en minuscule : lundi 15 novembre 2026. Premier du mois : 1er décembre.
- Chiffres : 15/11/2026 (jour/mois/année). Jamais `11/15/2026`.
- Heures : 14 h 30, 9 h, 18 h 05. Tableaux et interfaces serrées : 14:30 toléré. Pas d'AM/PM.
- Intervalle : du 3 au 7 mars ; de 9 h à 12 h. Siècle : XXIe siècle (petites capitales romaines).

## Téléphone et adresse

- National : 01 23 45 67 89 (cinq paires, espaces insécables).
- International : +33 1 23 45 67 89 (le 0 initial disparaît).
- Adresse : numéro, type de voie en minuscule, nom ; ligne suivante code postal à cinq chiffres **avant** la ville.
  `12 rue des Lilas` / `75011 Paris`. Sur une enveloppe, ville en capitales : `75011 PARIS` (à vérifier, norme postale). Pas d'État, pas de ZIP après la ville.

## Majuscules

- Titres, boutons, menus, intertitres : majuscule au **premier mot seulement** et aux noms propres. `Créer un compte`, pas `Créer Un Compte`. Supprimer tout Title Case.
- Majuscules accentuées : État, À propos, Écrire (l'Académie française recommande l'accent).
- Jours, mois, langues, gentilés adjectifs en minuscule : en français, le marché breton. Gentilé nom : les Bretons.
- Pas de texte entier en capitales pour insister ; le gras suffit.

## Abréviations

- M. (pas Mr), Mme, MM., Mmes, Dr, Me. Éviter Mlle.
- n° 12 (ou no avec o en exposant), p. 4, etc. (jamais `etc...`), c.-à-d., p. ex.
- Ordinaux : 1er, 1re, 2e, 3e (pas 2ème, 2nd hors second). Exposant si possible.
- Points de suspension : un seul caractère `…` ou trois points, jamais quatre.
- Tiret d'incise : tiret demi-cadratin `–` entouré d'espaces. Liste : tiret ou puce, ponctuation homogène.

## Unités

- Système international, espace insécable entre nombre et symbole : 5 km, 250 g, 20 °C, 3 m², 1,5 l ou 1,5 L.
- Symboles invariables, sans point : 10 kg, jamais « 10 kgs ».
- Convertir : miles → km, °F → °C, pieds → m, livres → kg, onces → g ou ml.

## Écriture inclusive

Ne pas l'imposer, ne pas la retirer d'office. Suivre la graphie du texte fourni. Si rien n'est fixé, préférer les formes neutres ou les doublets (« les clientes et les clients », « l'équipe »), sans point médian. Graphies mélangées : harmoniser sur la plus fréquente, le dire en une ligne après le texte. Textes rédigés pour l'État (actes administratifs, Journal officiel) : la circulaire du Premier ministre du 21 novembre 2017 invite à ne pas employer l'écriture dite inclusive ; elle ne vise pas les textes d'entreprise. Point médian dans un tel texte : le signaler en une ligne.
