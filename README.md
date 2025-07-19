# 🤖 TextToSQL ChatBot

[![Streamlit Cloud CI/CD](https://github.com/m-proto/TextoSql/actions/workflows/streamlit-cloud.yml/badge.svg)](https://github.com/m-proto/TextoSql/actions/workflows/streamlit-cloud.yml)

## 🚀 Test entre collègues

Application simple qui convertit vos questions en requêtes SQL.

### 🌐 Déployé sur Streamlit Cloud

**Point d'entrée** : `streamlit_main.py`

### 🛠️ Configuration requise

Les secrets suivants doivent être configurés dans Streamlit Cloud :

```toml
# Dans Streamlit Cloud > Settings > Secrets
GOOGLE_API_KEY = "votre_clé_api_google"
REDSHIFT_HOST = "votre_host_redshift"
REDSHIFT_PORT = "5439"
REDSHIFT_USER = "votre_user"
REDSHIFT_PASSWORD = "votre_password"
REDSHIFT_DATABASE = "votre_database"
```

### 🏃‍♂️ Lancement local

```bash
streamlit run streamlit_main.py
```

### 📋 Fonctionnalités

- ✅ Interface en français/anglais/japonais
- ✅ Génération SQL avec Google Gemini
- ✅ Cache intelligent
- ✅ Interface moderne et responsive

### 🔧 Déploiement Streamlit Cloud

1. **Connectez votre repo GitHub**
2. **Point d'entrée** : `streamlit_main.py`
3. **Configurez les secrets** dans l'interface Streamlit Cloud
4. **Déploiement automatique** à chaque push !
