# 🎯 Kazi Hunter

Pipeline d'automatisation de recherche d'emploi — 100% local, 0€, open-source.

## Stack technique

| Composant | Outil |
|---|---|
| Scraping | Playwright (Python) |
| LLM local | Ollama + Mistral 7B |
| Base de données | SQLite |
| Dashboard | Streamlit |
| Conteneurs | Docker + Compose |
| CI/CD | GitHub Actions |

## Prérequis

- Linux (Ubuntu 22.04/24.04)
- 8GB RAM minimum (16GB recommandé)
- Connexion internet pour le premier setup

## Installation en une commande

```bash
git clone https://github.com/Ciramor07/kazi-hunter-plateform.git
cd kazi-hunter-plateform
./install.sh
```

## Configuration

```bash
# Copie le template
cp .env.example .env

# Modifie tes mots-clés
nano .env
```

## Démarrage après redémarrage PC

```bash
./start.sh
```

## Structure du projet
kazi-hunter/
├── scraper/
│   ├── platforms/
│   │   ├── indeed.py      ← Scraper Indeed
│   │   ├── linkedin.py    ← Scraper LinkedIn
│   │   └── wttj.py        ← Scraper WTTJ
│   ├── utils/
│   │   └── db.py          ← Base de données SQLite
│   ├── scorer.py          ← Scoring IA avec Ollama
│   ├── main.py            ← Point d entrée
│   └── Dockerfile
├── dashboard/
│   ├── app.py             ← Interface Streamlit
│   └── Dockerfile
├── .github/
│   └── workflows/
│       ├── ci.yml         ← CI (lint + build)
│       └── daily-hunt.yml ← CD (scraping quotidien)
├── docker-compose.yml
├── .env.example
├── install.sh             ← Installation automatique
├── start.sh               ← Démarrage rapide
└── README.md

## ⚠️ Important

- Ne commite JAMAIS ton fichier `.env`
- La DB `kazi.db` contient tes données personnelles
- Les credentials → uniquement dans `.env` local

## Licence
