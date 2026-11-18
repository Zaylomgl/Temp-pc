# tempmon — consignes pour Claude

Lire d'abord `PROJECT.md`, puis `DECISIONS.md` et `PROGRESS.md`.

## Fichiers de suivi du projet (convention project-kickoff)

Trois fichiers de suivi vivent à la racine de ce dépôt : `PROJECT.md`, `DECISIONS.md`, `PROGRESS.md`.
Les tenir à jour automatiquement dans chaque conversation :

- `DECISIONS.md` — à chaque décision explicite, ajouter une entrée EN HAUT
  (date + titre court + justification en 1 à 3 phrases). Une décision = changement de périmètre,
  changement de direction, changement esthétique, idée écartée. Pas de détails techniques mineurs.
  Si une décision renverse une direction ou une hypothèse déjà notée, utiliser le format détaillé
  (Ce qu'on pensait / Pourquoi on a changé / Ce qui a changé).
- `PROGRESS.md` — quand une unité importante (composant, fonctionnalité, écran) est terminée,
  ajouter une entrée EN HAUT. Pas les petits ajustements ni les corrections de bugs.
- `PROJECT.md` — le mettre à jour quand le périmètre ou la direction change nettement
  (et noter ce changement dans `DECISIONS.md` aussi).

Après chaque ajout, le signaler en une phrase (« Noté dans DECISIONS.md : ... »).
Ne demander que en cas de doute (réfléchir à voix haute ≠ décider).
