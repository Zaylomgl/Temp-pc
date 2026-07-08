# tempmon 🌡️

Logiciel léger pour **afficher les températures des composants** (CPU, GPU,
disques, carte mère) — en ligne de commande ou via un tableau de bord web
temps réel. **Aucune dépendance externe** : uniquement la bibliothèque
standard de Python 3.9+.

## Fonctionnalités

- Lecture des capteurs réels sous Linux via `/sys/class/hwmon`.
- Sous Windows, repli sur les zones thermiques ACPI (`MSAcpi_ThermalZoneTemperature`
  via WMI) — moins précis que `hwmon` et pas disponible sur toutes les
  machines (dépend du firmware).
- Repli automatique sur `psutil` (si installé) puis sur des données
  **simulées** — le logiciel tourne donc partout (conteneurs, CI, VM).
- Seuils **par catégorie** de composant (CPU ≠ disque) avec statut
  coloré : `normal` / `warning` / `critical`.
- Tableau de bord web avec jauges, rafraîchissement automatique, thème
  clair/sombre.
- API JSON (`/api/snapshot`) réutilisable par d'autres outils.

## Démarrage rapide (utilisateur non-technique) 🖱️

**Option A — le `.exe` (Windows, sans rien installer)**

1. Va dans l'onglet **Releases** du dépôt GitHub.
2. Télécharge **`tempmon.exe`**.
3. Double-clique dessus → le tableau de bord s'ouvre tout seul dans ton
   navigateur. C'est tout.

> Le `.exe` est construit automatiquement par GitHub Actions
> (`.github/workflows/build-exe.yml`). Pour en générer un : crée un tag
> `v1.0.0` (ou lance le workflow « Build tempmon.exe » à la main).

**Option B — le lanceur double-clic (Windows / Mac / Linux, avec Python)**

Double-clique sur le fichier correspondant à ton système :

| Système  | Fichier                  |
|----------|--------------------------|
| Windows  | `Lancer-tempmon.bat`     |
| macOS    | `Lancer-tempmon.command` |
| Linux    | `lancer-tempmon.sh`      |

Le navigateur s'ouvre automatiquement sur le tableau de bord. Si Python
n'est pas installé, le lanceur te l'indique et te donne le lien.

## Installation (développeur)

Rien à installer : clonez le dépôt, Python 3.9+ suffit.

## Utilisation

```bash
# Un seul relevé dans le terminal
python3 -m tempmon --once

# Rafraîchissement continu dans le terminal
python3 -m tempmon --watch --interval 2

# Tableau de bord web (http://127.0.0.1:8787)
python3 -m tempmon --serve

# Forcer une source de capteurs
python3 -m tempmon --once --source simulated
```

### Options principales

| Option        | Effet                                              |
|---------------|----------------------------------------------------|
| `--once`      | Un seul relevé puis quitte (défaut).               |
| `--watch`     | Rafraîchit en continu dans le terminal.            |
| `--serve`     | Lance le serveur du tableau de bord web.           |
| `--interval`  | Intervalle de rafraîchissement en secondes.        |
| `--host`/`--port` | Adresse d'écoute du serveur.                   |
| `--source`    | `hwmon`, `psutil`, `windows_wmi` ou `simulated`.   |
| `--no-color`  | Désactive les couleurs ANSI.                       |

## Architecture

```
tempmon/
├── model.py            # Reading / SensorGroup / Snapshot + logique de statut
├── config.py           # Seuils par type de composant
├── sensors/
│   ├── base.py         # Interface SensorProvider
│   ├── hwmon.py        # Lecteur Linux réel (/sys/class/hwmon)
│   ├── psutil_provider.py  # Repli multiplateforme (optionnel)
│   ├── windows_wmi.py  # Zones thermiques ACPI (Windows, optionnel)
│   ├── simulated.py    # Données simulées (démo / CI)
│   └── registry.py     # Auto-détection : hwmon → psutil → windows_wmi → simulé
├── server.py           # Serveur HTTP stdlib : API JSON + statique
├── cli.py              # Interface ligne de commande
└── web/                # Tableau de bord (HTML/CSS/JS)
```

Le flux : `registry` choisit la meilleure source disponible →
`provider.read()` renvoie un `Snapshot` → `model` applique les seuils →
affichage CLI ou API JSON servie au tableau de bord.

## Tests

```bash
python3 -m unittest discover -s tests -v
```

## Notes

- Sur une vraie machine Linux, le provider `hwmon` est utilisé
  automatiquement. Pour de meilleurs résultats, assurez-vous que les modules
  noyau (`coretemp`, `k10temp`, `drivetemp`, `nvme`...) sont chargés.
- Dans un conteneur sans capteurs (comme lors du développement), la source
  `simulated` prend le relais pour permettre la démonstration.
- Sous Windows, si le firmware n'expose aucune zone thermique ACPI (fréquent
  sur certaines machines), tempmon retombe aussi sur `simulated` — c'est une
  limite matérielle/firmware, pas un bug de l'application.
