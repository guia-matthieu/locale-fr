---
name: locale
description: Use before writing, reviewing or computing anything for a recipient, business or employee in France or the EU (ad, post, e-mail, prospecting, form, terms of sale, customer reply, quote, invoice, bookkeeping, tax, payroll, job ad, hiring, HR review, contract, NDA, accessibility audit, UI copy, chart labels). À utiliser avant tout texte, document ou calcul destiné à la France ou à l'UE : publicité, prospection, RGPD, CGV, facture, comptabilité, paie, recrutement, droit du travail, contrat, accessibilité, typographie. Applies French formats and typography instead of US defaults; flags French legal points to check.
---

# Adaptateur local : France et Union européenne

**Juridiction = celle du destinataire** (client, prospect, salarié, candidat, lecteur) ou de l'entreprise pour la compta, la paie et le droit du travail.

| Juridiction | Quoi faire |
|---|---|
| France | lis `${CLAUDE_SKILL_DIR}/packs/FR/typographie.md` pour tout texte en français, et applique la règle « sujets juridiques » ci-dessous |
| Autre pays de l'UE | applique la règle « sujets juridiques » ; dis que les règles nationales de ce pays ne sont pas couvertes |
| Hors UE | rien : ne lis aucun paquet, ne mentionne pas ce skill |

**Sujets juridiques** (publicité, prospection, données personnelles, vente, facture, comptabilité, paie, recrutement, droit du travail, contrat, accessibilité) : les paquets de règles de cette version sont en relecture et ne sont pas publiés. N'applique pas par défaut les usages américains (Net 30, late fee, at-will, opt-out, formats US) : quand la demande en contient, dis en une ligne qu'ils ne valent pas tels quels en France et ajoute une section « À faire vérifier » qui liste les points, sans inventer d'article ni de chiffre.

Fais ce qui est demandé ; applique les substitutions de format et de typographie sans commentaire.
