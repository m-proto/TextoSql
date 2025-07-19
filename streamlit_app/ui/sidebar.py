"""
🎨 Composant Sidebar
Gère la barre latérale avec statistiques, contrôles et navigation
"""

import streamlit as st
from datetime import datetime
from typing import Dict, Any, List
from ..translations.languages import language_manager


class SidebarManager:
    """Gestionnaire de la barre latérale"""
    
    def __init__(self, services=None):
        self.services = services
        self.language_manager = language_manager
    
    def render(self):
        """Affiche la barre latérale complète"""
        with st.sidebar:
            self._render_header()
            self._render_language_selector()
            st.divider()
            self._render_service_status()
            self._render_session_stats()
            st.divider()
            self._render_tables_used()
            self._render_example_questions()
            self._render_actions()
    
    def _render_header(self):
        """En-tête de la sidebar"""
        st.header("🤖 Assistant SQL")
    
    def _render_language_selector(self):
        """Sélecteur de langue"""
        st.subheader(self.language_manager.get_text('language', st.session_state.language))
        
        language_options = {
            'Français 🇫🇷': 'fr',
            'English 🇺🇸': 'en', 
            '日本語 🇯🇵': 'ja'
        }
        
        selected_lang = st.selectbox(
            "Select/選択/Sélectionner:",
            options=list(language_options.keys()),
            index=list(language_options.values()).index(st.session_state.language),
            key="language_selector"
        )
        
        if language_options[selected_lang] != st.session_state.language:
            st.session_state.language = language_options[selected_lang]
            self._update_welcome_message()
            st.rerun()
    
    def _render_service_status(self):
        """Statut des services"""
        st.subheader(self.language_manager.get_text('service_status', st.session_state.language))
        
        if self.services and self.services.get("llm") and self.services["llm"].is_available():
            st.success(self.language_manager.get_text('ai_connected', st.session_state.language))
        else:
            st.error(self.language_manager.get_text('ai_disconnected', st.session_state.language))
        
        st.success(self.language_manager.get_text('cache_active', st.session_state.language))
    
    def _render_session_stats(self):
        """Statistiques de session"""
        st.subheader(self.language_manager.get_text('session_stats', st.session_state.language))
        
        if 'chat_stats' not in st.session_state:
            return
        
        stats = st.session_state.chat_stats
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                self.language_manager.get_text('questions', st.session_state.language), 
                stats["total_questions"]
            )
            st.metric(
                self.language_manager.get_text('sql_generated', st.session_state.language), 
                stats["sql_generated"]
            )
        
        with col2:
            cache_rate = 0
            if stats["total_questions"] > 0:
                cache_rate = (stats["cache_hits"] / stats["total_questions"]) * 100
            st.metric(
                self.language_manager.get_text('cache_hits', st.session_state.language), 
                stats["cache_hits"]
            )
            st.metric(
                self.language_manager.get_text('cache_rate', st.session_state.language), 
                f"{cache_rate:.0f}%"
            )
        
        # Durée de session
        session_duration = datetime.now() - stats["session_start"]
        st.info(f"⏰ {self.language_manager.get_text('session', st.session_state.language)} : {session_duration.seconds // 60}min")
    
    def _render_tables_used(self):
        """Affiche les tables utilisées dans la dernière question"""
        if hasattr(st.session_state, 'used_tables') and st.session_state.used_tables:
            st.subheader(self.language_manager.get_text('tables_used', st.session_state.language))
            for table in st.session_state.used_tables:
                st.markdown(f"• **{table}**")
            st.caption(f"💡 {self.language_manager.get_text('last_question', st.session_state.language)}")
            st.divider()
    
    def _render_example_questions(self):
        """Exemples de questions selon la langue"""
        st.subheader(self.language_manager.get_text('example_questions', st.session_state.language))
        
        examples = {
            'fr': [
                "Combien d'utilisateurs avons-nous au total ?",
                "Quelles sont les ventes de cette semaine ?",
                "Top 5 des produits les plus vendus",
                "Revenus par mois cette année"
            ],
            'en': [
                "How many users do we have in total?",
                "What are this week's sales?",
                "Top 5 best-selling products",
                "Monthly revenue this year"
            ],
            'ja': [
                "ユーザー総数は？",
                "今週の売上は？",
                "売れ筋商品トップ5",
                "今年の月別収益"
            ]
        }
        
        current_examples = examples.get(st.session_state.language, examples['fr'])
        
        for i, example in enumerate(current_examples):
            if st.button(f"💡 {example}", key=f"example_{i}"):
                # Ajouter l'exemple au chat
                if 'messages' not in st.session_state:
                    st.session_state.messages = []
                
                st.session_state.messages.append({
                    "role": "user",
                    "content": example,
                    "timestamp": datetime.now()
                })
                st.rerun()
    
    def _render_actions(self):
        """Actions disponibles"""
        st.subheader(self.language_manager.get_text('actions', st.session_state.language))
        
        # Nouvelle conversation
        if st.button(
            self.language_manager.get_text('new_conversation', st.session_state.language),
            key="new_conversation"
        ):
            self._clear_conversation()
        
        # Exporter conversation
        if st.button(
            self.language_manager.get_text('export_conversation', st.session_state.language),
            key="export_conversation"
        ):
            self._export_conversation()
    
    def _update_welcome_message(self):
        """Met à jour le message d'accueil selon la langue"""
        if 'messages' in st.session_state and st.session_state.messages:
            # Remplacer le premier message d'accueil
            welcome_text = self.language_manager.get_welcome_with_examples(st.session_state.language)
            st.session_state.messages[0] = {
                "role": "assistant",
                "content": welcome_text,
                "timestamp": datetime.now()
            }
    
    def _clear_conversation(self):
        """Efface la conversation et démarre une nouvelle session"""
        st.session_state.messages = [{
            "role": "assistant", 
            "content": self.language_manager.get_welcome_with_examples(st.session_state.language),
            "timestamp": datetime.now()
        }]
        
        # Réinitialiser les statistiques
        st.session_state.chat_stats = {
            "total_questions": 0,
            "sql_generated": 0,
            "cache_hits": 0,
            "session_start": datetime.now()
        }
        
        # Effacer les tables utilisées
        if hasattr(st.session_state, 'used_tables'):
            st.session_state.used_tables = []
        
        st.rerun()
    
    def _export_conversation(self):
        """Exporte la conversation en JSON"""
        if 'messages' in st.session_state:
            import json
            
            conversation_data = {
                "timestamp": datetime.now().isoformat(),
                "language": st.session_state.language,
                "stats": st.session_state.get('chat_stats', {}),
                "messages": [
                    {
                        "role": msg["role"],
                        "content": msg["content"],
                        "timestamp": msg["timestamp"].isoformat() if isinstance(msg["timestamp"], datetime) else str(msg["timestamp"])
                    }
                    for msg in st.session_state.messages
                ]
            }
            
            json_string = json.dumps(conversation_data, indent=2, ensure_ascii=False)
            
            st.download_button(
                label="📥 JSON",
                data=json_string,
                file_name=f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
