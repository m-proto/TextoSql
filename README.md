# TextToSQL API

API de conversion de langage naturel vers SQL avec FastAPI et intégration Redshift.

## 🚀 Installation

```bash
# Cloner le repo
git clone https://github.com/m-proto/TextoSql.git
cd TextoSql

# Installer les dépendances
pip install -r requirements.txt

# Configurer l'environnement
cp .env.example .env
# Puis éditer .env avec vos vraies credentials
```

## ⚙️ Configuration

Configurer le fichier `.env` avec vos credentials :

```bash
# Base de données Redshift
REDSHIFT_USER=your_username
REDSHIFT_PASSWORD=your_password
REDSHIFT_HOST=your_cluster.region.redshift.amazonaws.com
REDSHIFT_PORT=5439
REDSHIFT_DB=your_database
REDSHIFT_SCHEMA=your_schema

# API Google Gemini
GOOGLE_API_KEY=your_google_api_key

# Configuration
DEBUG=false
LOG_LEVEL=INFO
```

## 🎯 Utilisation

```bash
# Démarrer l'API
python main.py

# L'API sera disponible sur :
# - API : http://localhost:8000
# - Documentation : http://localhost:8000/docs
# - Health check : http://localhost:8000/health
```

## 📁 Structure du projet

```
TextoSql/
├── app/                    # Application FastAPI
│   ├── main.py            # Point d'entrée FastAPI
│   ├── dependencies.py    # Dépendances (rate limiting)
│   ├── routers/           # Routeurs API
│   │   ├── sql.py         # Endpoints SQL
│   │   └── health.py      # Health checks
│   └── schemas/           # Schémas Pydantic
│       └── sql.py         # Schémas SQL
├── domain/                # Logique métier
│   └── sql/
│       └── service.py     # Service de génération SQL
├── infrastructure/        # Services techniques
│   ├── settings.py        # Configuration
│   ├── database.py        # Gestion Redshift
│   ├── llm.py            # Intégration Gemini
│   ├── cache.py          # Cache en mémoire
│   └── logging.py        # Logging structuré
├── tests/                 # Tests
├── main.py               # Point d'entrée principal
└── requirements.txt      # Dépendances
```

## 🔗 Endpoints

- `GET /` - Informations de base
- `GET /health` - Health check
- `POST /sql/generate` - Génération SQL
- `GET /sql/tables` - Liste des tables
- `GET /sql/cache/stats` - Statistiques cache
- `DELETE /sql/cache/clear` - Vider le cache

## 📊 Features

- ✅ **FastAPI** avec documentation automatique
- ✅ **Rate limiting** (60 req/min par IP)
- ✅ **Cache en mémoire** pour optimiser les performances
- ✅ **Logging structuré** avec timestamping
- ✅ **Gestion d'erreurs** robuste
- ✅ **Health checks** pour monitoring
- ✅ **Architecture hexagonale** propre
- ✅ **Validation Pydantic** des données

## 🛠️ Développement

```bash
# Mode développement avec rechargement automatique
python main.py

# Tests
python -m pytest tests/

# Linting
flake8 .
```

## 📝 Exemple d'utilisation

```python
import requests

# Générer une requête SQL
response = requests.post("http://localhost:8000/sql/generate", json={
    "question": "Combien d'utilisateurs ont été créés ce mois ?",
    "execute_query": false,
    "use_cache": true
})

print(response.json())
# {
#   "sql": "SELECT COUNT(*) FROM users WHERE created_at >= DATE_TRUNC('month', CURRENT_DATE)",
#   "execution_time": 0.245,
#   "cached": false
# }
```

## 🔒 Production

- Configurer des vraies credentials Redshift
- Définir `DEBUG=false` en production
- Utiliser un reverse proxy (nginx)
- Configurer le monitoring et alerting
- Utiliser Redis pour le cache en production
