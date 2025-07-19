"""
💬 Interface de Chat
Gère l'affichage et l'interaction des messages de chat
"""

import streamlit as st
from datetime import datetime
from typing import Dict, Any, List, Optional
from ..translations.languages import language_manager


class ChatInterface:
    """Gestionnaire de l'interface de chat"""
    
    def __init__(self, services=None):
        self.services = services
        self.language_manager = language_manager
    
    def render(self):
        """Affiche l'interface de chat complète"""
        self._render_header()
        self._render_messages()
        self._render_input()
    
    def _render_header(self):
        """En-tête de l'interface de chat"""
        current_lang = st.session_state.get('language', 'fr')
        
        st.markdown(f"""
        <div class="main-header">
            <h1>{self.language_manager.get_text('title', current_lang)}</h1>
            <p>{self.language_manager.get_text('subtitle', current_lang)}</p>
        </div>
        """, unsafe_allow_html=True)
    
    def _render_messages(self):
        """Affiche tous les messages de la conversation"""
        if 'messages' not in st.session_state:
            return
        
        for message in st.session_state.messages:
            self._render_single_message(message)
    
    def _render_single_message(self, message: Dict[str, Any]):
        """Affiche un message individuel"""
        role = message["role"]
        content = message["content"]
        timestamp = message.get("timestamp", datetime.now())
        
        if role == "user":
            self._render_user_message(content, timestamp)
        elif role == "assistant":
            self._render_assistant_message(content, timestamp)
    
    def _render_user_message(self, content: str, timestamp: datetime):
        """Affiche un message utilisateur"""
        with st.chat_message("user"):
            st.markdown(f"""
            <div class="user-message">
                <strong>🧑‍💻 Vous :</strong><br>
                {content}
                <div style="font-size: 0.8em; color: #666; margin-top: 0.5rem;">
                    ⏰ {timestamp.strftime('%H:%M:%S')}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    def _render_assistant_message(self, content: str, timestamp: datetime):
        """Affiche un message de l'assistant"""
        with st.chat_message("assistant"):
            if "```sql" in content:
                # Message contenant du SQL
                self._render_sql_response(content, timestamp)
            else:
                # Message texte normal
                st.markdown(f"""
                <div class="assistant-message">
                    {content}
                    <div style="font-size: 0.8em; color: #666; margin-top: 0.5rem;">
                        ⏰ {timestamp.strftime('%H:%M:%S')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    def _render_sql_response(self, content: str, timestamp: datetime):
        """Affiche une réponse contenant du SQL avec actions"""
        # Extraire le SQL du contenu
        sql_start = content.find("```sql")
        sql_end = content.find("```", sql_start + 6)
        
        if sql_start != -1 and sql_end != -1:
            # Partie avant le SQL
            before_sql = content[:sql_start].strip()
            # Code SQL
            sql_code = content[sql_start + 6:sql_end].strip()
            # Partie après le SQL
            after_sql = content[sql_end + 3:].strip()
            
            # Afficher le texte avant
            if before_sql:
                st.markdown(before_sql)
            
            # Afficher le SQL avec actions
            self._render_sql_block(sql_code)
            
            # Afficher le texte après
            if after_sql:
                st.markdown(after_sql)
        else:
            # Fallback si pas de SQL trouvé
            st.markdown(content)
        
        # Timestamp
        st.caption(f"⏰ {timestamp.strftime('%H:%M:%S')}")
    
    def _render_sql_block(self, sql_code: str):
        """Affiche un bloc SQL avec actions"""
        # Afficher le code SQL
        st.code(sql_code, language="sql")
        
        # Actions pour le SQL
        col1, col2, col3 = st.columns(3)
        
        current_lang = st.session_state.get('language', 'fr')
        
        with col1:
            if st.button(
                self.language_manager.get_text('copy_sql', current_lang),
                key=f"copy_{hash(sql_code)}"
            ):
                st.success("📋 SQL copié !")
        
        with col2:
            st.download_button(
                label=self.language_manager.get_text('download', current_lang),
                data=sql_code,
                file_name=f"query_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql",
                mime="text/sql"
            )
        
        with col3:
            if st.button(
                self.language_manager.get_text('explain', current_lang),
                key=f"explain_{hash(sql_code)}"
            ):
                self._explain_sql(sql_code)
    
    def _render_input(self):
        """Zone de saisie pour les nouvelles questions"""
        current_lang = st.session_state.get('language', 'fr')
        placeholder = self.language_manager.get_text('input_placeholder', current_lang)
        
        # Input utilisateur
        if user_input := st.chat_input(placeholder):
            self._handle_user_input(user_input)
    
    def _handle_user_input(self, user_input: str):
        """Traite une nouvelle question utilisateur"""
        # Ajouter le message utilisateur
        st.session_state.messages.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now()
        })
        
        # Générer la réponse
        if self.services:
            try:
                response = self._generate_response(user_input)
                
                # Ajouter la réponse de l'assistant
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response,
                    "timestamp": datetime.now()
                })
                
                # Mettre à jour les statistiques
                self._update_stats()
                
            except Exception as e:
                st.error(f"Erreur lors de la génération de la réponse : {str(e)}")
        
        st.rerun()
    
    def _generate_response(self, question: str) -> str:
        """Génère une réponse SQL pour la question"""
        # Cette méthode devrait être connectée au service SQL
        # Pour l'instant, on retourne une réponse simulée
        current_lang = st.session_state.get('language', 'fr')
        
        sql_title = self.language_manager.get_text('sql_query_title', current_lang)
        next_actions = self.language_manager.get_text('next_actions', current_lang)
        
        # SQL simulé
        sql_query = f"""
SELECT COUNT(*) as total_users
FROM users
WHERE status = 'active'
  AND created_at >= DATE_TRUNC('month', CURRENT_DATE);
"""
        
        return f"""
{sql_title}

```sql
{sql_query.strip()}
```

{next_actions}
"""
    
    def _explain_sql(self, sql_code: str):
        """Explique le code SQL"""
        current_lang = st.session_state.get('language', 'fr')
        
        explanations = {
            'fr': f"""
**🔍 Explication du SQL :**

Cette requête permet de :
- 📊 Compter le nombre total d'enregistrements
- 🔍 Filtrer selon des critères spécifiques
- 📅 Utiliser des fonctions de date si nécessaire

**Structure :**
- `SELECT` : Sélectionne les colonnes à afficher
- `FROM` : Indique la table source
- `WHERE` : Applique les filtres
""",
            'en': f"""
**🔍 SQL Explanation:**

This query allows you to:
- 📊 Count the total number of records
- 🔍 Filter according to specific criteria
- 📅 Use date functions if necessary

**Structure:**
- `SELECT`: Selects the columns to display
- `FROM`: Indicates the source table
- `WHERE`: Applies filters
""",
            'ja': f"""
**🔍 SQL説明：**

このクエリの機能：
- 📊 総レコード数をカウント
- 🔍 特定の条件でフィルタ
- 📅 必要に応じて日付関数を使用

**構造：**
- `SELECT`：表示する列を選択
- `FROM`：ソーステーブルを指定
- `WHERE`：フィルタを適用
"""
        }
        
        explanation = explanations.get(current_lang, explanations['fr'])
        st.markdown(explanation)
    
    def _update_stats(self):
        """Met à jour les statistiques de session"""
        if 'chat_stats' not in st.session_state:
            st.session_state.chat_stats = {
                "total_questions": 0,
                "sql_generated": 0,
                "cache_hits": 0,
                "session_start": datetime.now()
            }
        
        st.session_state.chat_stats["total_questions"] += 1
        st.session_state.chat_stats["sql_generated"] += 1
