"""
🧪 TextToSQL - Test entre collègues
Application simple et directe
"""

import streamlit as st
import sys
import os

# Configuration du chemin pour les imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

def main():
    """Application simple pour test entre collègues"""
    try:
        # Import et configuration simple
        from streamlit_app.config.settings import AppConfig
        AppConfig.init_environment()
        
        # Import de la classe principale
        from streamlit_app.chatbot import TextToSQLChatBot
        
        # Création et lancement de l'application
        chatbot = TextToSQLChatBot()
        chatbot.run()
        
    except Exception as e:
        st.error(f"❌ Erreur: {str(e)}")
        st.info("� Vérifiez votre configuration dans .env")


if __name__ == "__main__":
    main()
