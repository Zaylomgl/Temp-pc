# tempmon

## Quoi
Logiciel léger qui affiche les températures des composants (CPU, GPU, disques, carte mère) en ligne de commande ou dans un tableau de bord web.

## Pour qui / pourquoi
Utilisateurs non techniques qui veulent surveiller leur PC, sans rien installer (`.exe` Windows).

## Périmètre V1 (code existant au 2026-11-18, PR ouvertes comprises)
- Capteurs Linux (`/sys/class/hwmon`), repli Windows WMI ACPI, puis `psutil`, puis données simulées
- Seuils par catégorie, tableau de bord web, API JSON
- `.exe` construit par GitHub Actions et publié en release

## Hors périmètre
- Lecture précise des capteurs sous Windows (limitée aux zones ACPI)

## Stack / outils
Python 3.9+ sans dépendance, GitHub Actions (build `.exe`).

## Où ça vit
À la racine du dépôt, sur la branche `main` : `PROJECT.md`, `DECISIONS.md`, `PROGRESS.md`, `CLAUDE.md`.
