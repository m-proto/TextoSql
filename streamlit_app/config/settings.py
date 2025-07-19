"""
🔧 Configuration centralisée de l'application
Gère les secrets et paramètres de manière sécurisée
"""

import streamlit as st
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class DatabaseConfig:
    """Configuration de la base de données"""
    host: str
    port: str
    user: str
    password: str
    database: str
    schema: str = "public"


class AppConfig:
    """Configuration centralisée de l'application"""
    
    @staticmethod
    def get_google_api_key() -> str:
        """
        Récupère la clé API Google depuis secrets.toml ou variables d'environnement
        Priorité: secrets.toml > env variables > défaut test
        """
        try:
            # Priorité 1: Streamlit secrets
            if hasattr(st, 'secrets') and 'GOOGLE_API_KEY' in st.secrets:
                return st.secrets['GOOGLE_API_KEY']
        except Exception:
            pass
        
        # Priorité 2: Variables d'environnement
        api_key = os.getenv('GOOGLE_API_KEY', '')
        if api_key:
            return api_key
            
        # Priorité 3: Valeur par défaut pour les tests
        return "test_key"
    
    @staticmethod
    def get_redshift_config() -> DatabaseConfig:
        """
        Configuration Redshift depuis secrets.toml ou variables d'environnement
        """
        try:
            # Priorité 1: Streamlit secrets
            if hasattr(st, 'secrets'):
                return DatabaseConfig(
                    host=st.secrets.get('REDSHIFT_HOST', ''),
                    port=st.secrets.get('REDSHIFT_PORT', '5439'),
                    user=st.secrets.get('REDSHIFT_USER', ''),
                    password=st.secrets.get('REDSHIFT_PASSWORD', ''),
                    database=st.secrets.get('REDSHIFT_DATABASE', '')
                )
        except Exception:
            pass
        
        # Priorité 2: Variables d'environnement
        return DatabaseConfig(
            host=os.getenv('REDSHIFT_HOST', 'test_host'),
            port=os.getenv('REDSHIFT_PORT', '5432'),
            user=os.getenv('REDSHIFT_USER', 'test_user'),
            password=os.getenv('REDSHIFT_PASSWORD', 'test_password'),
            database=os.getenv('REDSHIFT_DATABASE', 'test_db')
        )
    
    @staticmethod
    def get_app_settings() -> Dict[str, Any]:
        """Paramètres généraux de l'application"""
        return {
            'page_title': '🤖 TextToSQL ChatBot',
            'page_icon': '🔍',
            'layout': 'wide',
            'initial_sidebar_state': 'expanded',
            'debug': os.getenv('DEBUG', 'true').lower() == 'true'
        }
    
    @staticmethod
    def init_environment():
        """
        Initialise les variables d'environnement pour compatibilité
        avec le code existant (infrastructure/settings.py)
        """
        config = AppConfig.get_redshift_config()
        
        # Configuration pour l'infrastructure existante
        os.environ.setdefault("REDSHIFT_HOST", config.host)
        os.environ.setdefault("REDSHIFT_PORT", config.port)
        os.environ.setdefault("REDSHIFT_USER", config.user)
        os.environ.setdefault("REDSHIFT_PASSWORD", config.password)
        os.environ.setdefault("REDSHIFT_DATABASE", config.database)
        os.environ.setdefault("GOOGLE_API_KEY", AppConfig.get_google_api_key())
        os.environ.setdefault("DEBUG", "true")


# Instance globale pour faciliter l'utilisation
app_config = AppConfig()
