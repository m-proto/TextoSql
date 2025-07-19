"""
🦶 Composant Footer
Affiche les informations de bas de page
"""

import streamlit as st
from datetime import datetime


class FooterManager:
    """Gestionnaire du footer"""
    
    def render(self):
        """Affiche le footer de l'application"""
        st.markdown("---")
        
        # Footer avec informations
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### 🤖 TextToSQL ChatBot")
            st.markdown("*Intelligence artificielle pour vos données*")
        
        with col2:
            st.markdown("### 📊 Statistiques")
            if 'chat_stats' in st.session_state:
                stats = st.session_state.chat_stats
                session_duration = datetime.now() - stats["session_start"]
                st.markdown(f"⏰ Session : {session_duration.seconds // 60}min")
                st.markdown(f"💬 Questions : {stats['total_questions']}")
        
        with col3:
            st.markdown("### 🔗 Liens Utiles")
            st.markdown("📚 [Documentation](#)")
            st.markdown("💡 [Aide](#)")
        
        # Copyright
        st.markdown("""
        <div class="footer">
            <hr>
            <p style="text-align: center; color: #666;">
                © 2025 TextToSQL ChatBot | 
                Propulsé par Streamlit & Google Gemini | 
                Fait avec ❤️
            </p>
        </div>
        """, unsafe_allow_html=True)
