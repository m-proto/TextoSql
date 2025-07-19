"""
🤖 Classe principale du ChatBot
Orchestre tous les composants de l'application
"""

import streamlit as st
import sys
import os
from datetime import datetime
from typing import Dict, Any, Optional

# Ajout du chemin pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .config.settings import AppConfig
from .translations.languages import language_manager
from .ui.sidebar import SidebarManager
from .ui.chat_interface import ChatInterface
from .ui.footer import FooterManager
from .services.sql_service import SQLService


class TextToSQLChatBot:
    """
    Classe principale du ChatBot TextToSQL
    Intègre tous les composants pour une interface unifiée
    """
    
    def __init__(self):
        """Initialise le ChatBot avec tous ses composants"""
        self.config = AppConfig()
        self.language_manager = language_manager
        self.services = None
        
        # Initialiser les services
        self._init_services()
        
        # Initialiser les composants UI
        self.sidebar_manager = SidebarManager(self.services)
        self.chat_interface = ChatInterface(self.services)
        self.footer_manager = FooterManager()
        
        # Initialiser l'état de session
        self._init_session_state()
    
    def _init_services(self):
        """Initialise les services de l'application"""
        try:
            # Configuration de l'environnement
            self.config.init_environment()
            
            # Import des services existants
            from infrastructure.settings import settings
            from infrastructure.llm import LLMManager
            from infrastructure.cache import CacheManager
            from infrastructure.monitoring import MetricsCollector
            from infrastructure.logging import logger
            from domain.sql.service import SQLGenerationService
            
            # Initialisation des services
            llm_manager = LLMManager()
            cache_manager = CacheManager()
            metrics = MetricsCollector()
            # SQLGenerationService n'a pas de constructeur - c'est une classe statique
            sql_generation_service = SQLGenerationService()
            
            self.services = {
                "llm": llm_manager,
                "cache": cache_manager,
                "metrics": metrics,
                "sql_service": sql_generation_service,
                "logger": logger,
                "settings": settings
            }
            
            # Service SQL modulaire
            self.sql_service = SQLService(self.services)
            
        except Exception as e:
            st.error(f"Erreur d'initialisation des services : {str(e)}")
            self.services = None
            self.sql_service = SQLService()  # Service de base sans dépendances
    
    def _init_session_state(self):
        """Initialise l'état de session Streamlit"""
        # Langue par défaut
        if 'language' not in st.session_state:
            st.session_state.language = 'fr'
        
        # Messages de chat
        if 'messages' not in st.session_state:
            welcome_text = self.language_manager.get_welcome_with_examples(
                st.session_state.language
            )
            st.session_state.messages = [{
                "role": "assistant", 
                "content": welcome_text,
                "timestamp": datetime.now()
            }]
        
        # Statistiques de chat
        if 'chat_stats' not in st.session_state:
            st.session_state.chat_stats = {
                "total_questions": 0,
                "sql_generated": 0,
                "cache_hits": 0,
                "session_start": datetime.now()
            }
        
        # Tables utilisées
        if 'used_tables' not in st.session_state:
            st.session_state.used_tables = []
    
    def run(self):
        """
        Lance l'application ChatBot
        Point d'entrée principal
        """
        # Configuration de la page
        app_settings = self.config.get_app_settings()
        st.set_page_config(
            page_title=app_settings['page_title'],
            page_icon=app_settings['page_icon'],
            layout=app_settings['layout'],
            initial_sidebar_state=app_settings['initial_sidebar_state']
        )
        
        # Styles CSS
        self._apply_styles()
        
        # Interface utilisateur
        self._render_ui()
    
    def _apply_styles(self):
        """Applique les styles CSS personnalisés"""
        try:
            from .config.styles import get_custom_css
            st.markdown(get_custom_css(), unsafe_allow_html=True)
        except ImportError:
            # CSS de base si les styles ne peuvent pas être importés
            st.markdown("""
            <style>
            .main-header {
                background: linear-gradient(90deg, #2E86AB, #A23B72);
                padding: 1rem;
                border-radius: 10px;
                color: white;
                text-align: center;
                margin-bottom: 2rem;
            }
            </style>
            """, unsafe_allow_html=True)
    
    def _render_ui(self):
        """Affiche l'interface utilisateur complète"""
        # Sidebar
        self.sidebar_manager.render()
        
        # Interface de chat principale
        with st.container():
            self.chat_interface.render()
        
        # Footer
        self.footer_manager.render()
    
    def generate_sql_response(self, question: str) -> str:
        """
        Génère une réponse SQL pour une question
        Interface simplifiée pour l'intégration
        """
        if not self.sql_service:
            return "❌ Service SQL non disponible"
        
        try:
            # Générer la réponse
            response_data = self.sql_service.generate_sql_response(question)
            
            # Formater pour l'affichage
            current_lang = st.session_state.get('language', 'fr')
            formatted_response = self.sql_service.format_sql_response(
                response_data, 
                current_lang
            )
            
            # Mettre à jour les statistiques
            self._update_stats(response_data)
            
            return formatted_response
            
        except Exception as e:
            return f"❌ Erreur lors de la génération : {str(e)}"
    
    def _update_stats(self, response_data: Dict[str, Any]):
        """Met à jour les statistiques de session"""
        if 'chat_stats' not in st.session_state:
            return
        
        stats = st.session_state.chat_stats
        
        if response_data.get("success", False):
            stats["sql_generated"] += 1
            
            if response_data.get("cached", False):
                stats["cache_hits"] += 1
        
        stats["total_questions"] += 1
    
    def get_text(self, key: str) -> str:
        """
        Récupère un texte traduit (compatibilité avec code existant)
        """
        current_lang = st.session_state.get('language', 'fr')
        return self.language_manager.get_text(key, current_lang)
    
    def update_welcome_message(self):
        """
        Met à jour le message d'accueil (compatibilité avec code existant)
        """
        if 'messages' in st.session_state and st.session_state.messages:
            current_lang = st.session_state.get('language', 'fr')
            welcome_text = self.language_manager.get_welcome_with_examples(current_lang)
            
            st.session_state.messages[0] = {
                "role": "assistant",
                "content": welcome_text,
                "timestamp": datetime.now()
            }
