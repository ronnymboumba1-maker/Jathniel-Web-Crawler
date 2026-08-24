README.md pour JATHNIEL-WEB-CRAWLER

```markdown
# 🕷️ JATHNIEL-WEB-CRAWLER-PRO

## Crawler web professionnel avec extraction de fichiers sensibles

### 📌 Description

JATHNIEL-WEB-CRAWLER-PRO est un crawler web professionnel conçu pour explorer et télécharger intégralement des sites web. Il permet d'extraire automatiquement les fichiers sensibles, les assets, et de générer des rapports complets.

### ✨ Fonctionnalités

- ✅ **Crawl complet** : Exploration récursive avec profondeur configurable
- ✅ **Extraction de fichiers sensibles** : Détection et téléchargement automatique
- ✅ **Téléchargement d'assets** : CSS, JS, images, polices, etc.
- ✅ **Détection de technologies** : WordPress, Laravel, Django, etc.
- ✅ **Recherche de pages admin** : Détection automatique
- ✅ **Extraction d'emails** : Collecte des adresses email
- ✅ **Multi-threading** : Exploration rapide et efficace
- ✅ **Export de rapports** : JSON, HTML, CSV
- ✅ **Classification des fichiers sensibles** : Organisation par type

### 🚀 Installation

```bash
# 1. Cloner le dépôt
git clone https://github.com/votre-compte/jathniel-web-crawler.git
cd jathniel-web-crawler

# 2. Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/WSL
# ou
venv\Scripts\activate     # Windows

# 3. Installer les dépendances
pip install -r requirements.txt
```

🎯 Utilisation

```bash
# Lancer le crawler
python3 web_crawler.py

# Menu interactif
1. Lancer un crawl complet
2. Crawl avec extraction de fichiers sensibles
3. Télécharger un fichier spécifique
4. Voir les résultats du crawl
5. Voir les fichiers sensibles trouvés
6. Exporter les résultats (JSON/HTML)
7. Configuration
8. Statistiques du crawl
9. Aide / Documentation
0. Quitter
```

📊 Exemple de crawl

```bash
🔍 Debut du crawl de: https://example.com
================================================================================
📁 Dossier de sortie: ./crawled_sites/example.com
📊 Max pages: 500
📊 Max depth: 3
🔍 Recherche de fichiers sensibles: OUI
================================================================================
  📄 https://example.com/ (12580 octets)
    🔴 FICHIER SENSIBLE TELECHARGE: .env
        📍 https://example.com/.env
        📦 245 octets
  📄 https://example.com/about (8432 octets)
    📦 Asset téléchargé: style.css
  📄 https://example.com/contact (6571 octets)
    🔐 Page admin trouvee: https://example.com/admin

🔍 Analyse complémentaire...
    📧 Emails trouves: 3
        - admin@example.com
        - contact@example.com

✅ Crawl termine!
📄 Pages: 47
📁 Fichiers sensibles: 5
📦 Assets: 156
📊 Duree: 45.23 secondes
```

📁 Structure de sortie

```
crawled_sites/example.com/
├── pages/
│   ├── index.html
│   ├── about.html
│   └── contact.html
├── assets/
│   ├── images/
│   ├── scripts/
│   ├── styles/
│   ├── fonts/
│   └── icons/
├── sensitive/
│   ├── .env
│   ├── wp-config.php
│   ├── config.php
│   └── backup.sql
└── reports/
    └── crawl_report_20240815_143000.html
```