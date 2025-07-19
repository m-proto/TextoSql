"""
Application Streamlit standalone - Tout-en-un sécurisé
Version simplifiée sans FastAPI pour Streamlit Cloud
"""

import streamlit as st
import pandas as pd
import time
from datetime import datetime
import os
from typing import Optional, Dict, Any

# Configuration de la page
st.set_page_config(
    page_title="TextToSQL - Générateur SQL IA",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import conditionnel des modules (seulement si disponibles)
@st.cache_resource
def init_services():
    """Initialise les services de manière sécurisée"""
    try:
        # Import des modules infrastructure
        from infrastructure.settings import settings
        from infrastructure.llm import LLMManager
        from infrastructure.cache import CacheManager
        from infrastructure.monitoring import MetricsCollector
        from infrastructure.logging import logger
        from domain.sql.service import generate_sql_query_only
        
        # Vérification des credentials
        if not settings.google_api_key or settings.google_api_key == "test_key":
            st.error("🔑 Veuillez configurer GOOGLE_API_KEY dans les secrets Streamlit")
            st.stop()
        
        # Initialisation des services
        llm_manager = LLMManager()
        cache_manager = CacheManager()
        metrics = MetricsCollector()
        
        logger.info("Services initialisés avec succès")
        
        return {
            "llm": llm_manager,
            "cache": cache_manager, 
            "metrics": metrics,
            "settings": settings,
            "logger": logger
        }
        
    except Exception as e:
        st.error(f"❌ Erreur d'initialisation : {e}")
        st.info("🔧 Vérifiez la configuration des secrets Streamlit")
        st.stop()

class StreamlitTextToSQL:
    """Application TextToSQL standalone pour Streamlit"""
    
    def __init__(self):
        self.services = init_services()
        self.initialize_session_state()
    
    def initialize_session_state(self):
        """Initialise l'état de session Streamlit"""
        if 'history' not in st.session_state:
            st.session_state.history = []
        if 'total_queries' not in st.session_state:
            st.session_state.total_queries = 0
        if 'cache_hits' not in st.session_state:
            st.session_state.cache_hits = 0
    
    def generate_sql_safe(self, question: str, use_cache: bool = True) -> Dict[str, Any]:
        """Génère du SQL de manière sécurisée"""
        start_time = time.time()
        
        try:
            # Validation de l'entrée
            if not question or len(question.strip()) < 3:
                return {"error": "Question trop courte (minimum 3 caractères)"}
            
            if len(question) > 500:
                return {"error": "Question trop longue (maximum 500 caractères)"}
            
            # Vérification du cache
            cached_result = None
            if use_cache:
                cached_result = self.services["cache"].get_cached_sql_result(question)
                
            if cached_result:
                st.session_state.cache_hits += 1
                self.services["metrics"].record_cache_hit()
                
                return {
                    "sql": cached_result["sql"],
                    "execution_time": time.time() - start_time,
                    "cached": True,
                    "success": True
                }
            
            # Génération SQL avec LLM
            self.services["metrics"].record_cache_miss()
            self.services["metrics"].record_sql_generation()
            
            # Simulation du schéma (remplace la vraie DB)
            mock_schema = """
            Tables disponibles:
            - users (id, name, email, created_at)
            - orders (id, user_id, amount, order_date) 
            - products (id, name, price, category)
            """
            
            sql_query = self.services["llm"].generate_sql(question, mock_schema)
            
            if not sql_query:
                return {"error": "Impossible de générer la requête SQL"}
            
            # Mise en cache
            response_data = {
                "sql": sql_query,
                "execution_time": time.time() - start_time,
                "cached": False,
                "success": True
            }
            
            if use_cache:
                self.services["cache"].cache_sql_result(question, response_data)
            
            self.services["metrics"].record_request(time.time() - start_time, success=True)
            st.session_state.total_queries += 1
            
            return response_data
            
        except Exception as e:
            self.services["logger"].error("Erreur génération SQL", error=str(e))
            self.services["metrics"].record_request(time.time() - start_time, success=False)
            
            return {
                "error": f"Erreur lors de la génération : {str(e)}",
                "success": False
            }
    
    def render_sidebar(self):
        """Affiche la barre latérale"""
        with st.sidebar:
            st.header("⚙️ Configuration")
            
            # Statut des services
            st.subheader("🔧 Statut")
            if self.services["llm"].is_available():
                st.success("✅ LLM connecté")
            else:
                st.error("❌ LLM non disponible")
            
            st.success("✅ Cache actif")
            
            # Statistiques
            st.subheader("📊 Statistiques")
            st.metric("Requêtes totales", st.session_state.total_queries)
            
            cache_rate = 0
            if st.session_state.total_queries > 0:
                cache_rate = (st.session_state.cache_hits / st.session_state.total_queries) * 100
            
            st.metric("Taux de cache", f"{cache_rate:.1f}%")
            
            # Options
            st.subheader("🎛️ Options")
            use_cache = st.checkbox("Utiliser le cache", value=True)
            
            # Exemples
            st.subheader("💡 Exemples")
            examples = [
                "Combien d'utilisateurs avons-nous ?",
                "Quelles sont les commandes de cette semaine ?",
                "Top 5 des produits les plus vendus",
                "Revenus totaux par mois",
                "Utilisateurs créés aujourd'hui"
            ]
            
            selected_example = st.selectbox(
                "Choisir un exemple :",
                [""] + examples,
                key="example_selector"
            )
            
            return use_cache, selected_example
    
    def render_main_interface(self, use_cache: bool, selected_example: str):
        """Affiche l'interface principale"""
        # Header
        st.title("🔍 TextToSQL - Générateur SQL avec IA")
        st.markdown("### Posez votre question en français, obtenez du SQL professionnel !")
        
        # Zone de saisie
        question = st.text_area(
            "🗣️ Votre question :",
            value=selected_example if selected_example else "",
            height=100,
            placeholder="Ex: Montrez-moi les ventes par région pour cette année",
            help="Posez une question sur vos données en langage naturel"
        )
        
        # Boutons d'action
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            generate_btn = st.button("🚀 Générer SQL", type="primary", use_container_width=True)
        
        with col2:
            clear_btn = st.button("🗑️ Effacer", use_container_width=True)
        
        with col3:
            history_btn = st.button("📜 Historique", use_container_width=True)
        
        if clear_btn:
            st.rerun()
        
        # Génération SQL
        if generate_btn and question.strip():
            with st.spinner("🤖 Génération SQL en cours..."):
                result = self.generate_sql_safe(question.strip(), use_cache)
                
                if result.get("success"):
                    # Ajout à l'historique
                    st.session_state.history.insert(0, {
                        "timestamp": datetime.now(),
                        "question": question,
                        "sql": result["sql"],
                        "cached": result["cached"],
                        "execution_time": result["execution_time"]
                    })
                    
                    # Limiter l'historique à 50 entrées
                    if len(st.session_state.history) > 50:
                        st.session_state.history = st.session_state.history[:50]
                    
                    # Affichage des résultats
                    self.display_results(result, question)
                    
                else:
                    st.error(f"❌ {result.get('error', 'Erreur inconnue')}")
        
        elif generate_btn:
            st.warning("⚠️ Veuillez saisir une question")
        
        # Affichage de l'historique
        if history_btn:
            self.display_history()
    
    def display_results(self, result: Dict[str, Any], question: str):
        """Affiche les résultats de génération SQL"""
        st.success("✅ SQL généré avec succès !")
        
        # Métadonnées
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("⏱️ Temps", f"{result['execution_time']:.3f}s")
        with col2:
            st.metric("📂 Cache", "Oui" if result['cached'] else "Non")
        with col3:
            st.metric("🕒 Heure", datetime.now().strftime("%H:%M:%S"))
        
        # SQL généré
        st.subheader("📝 Requête SQL générée")
        st.code(result['sql'], language='sql')
        
        # Actions sur le SQL
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                "💾 Télécharger SQL",
                result['sql'],
                f"query_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql",
                "text/plain"
            )
        
        with col2:
            if st.button("📋 Copier dans le presse-papiers"):
                st.code(result['sql'])  # Fallback pour copie manuelle
        
        # Note sur l'exécution
        st.info("💡 **Note :** Cette version ne se connecte pas à une vraie base de données. Le SQL généré peut être testé dans votre environnement de base de données.")
    
    def display_history(self):
        """Affiche l'historique des requêtes"""
        if not st.session_state.history:
            st.info("📜 Aucun historique disponible")
            return
        
        st.subheader("📜 Historique des requêtes")
        
        for i, entry in enumerate(st.session_state.history[:10]):  # 10 dernières
            with st.expander(f"🔍 {entry['question'][:50]}... ({entry['timestamp'].strftime('%H:%M:%S')})"):
                st.write(f"**Question :** {entry['question']}")
                st.code(entry['sql'], language='sql')
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"⏱️ {entry['execution_time']:.3f}s")
                with col2:
                    st.write(f"📂 {'Cache' if entry['cached'] else 'Nouveau'}")
    
    def run(self):
        """Lance l'application"""
        try:
            # Rendu de l'interface
            use_cache, selected_example = self.render_sidebar()
            self.render_main_interface(use_cache, selected_example)
            
            # Footer
            st.markdown("---")
            st.markdown("🚀 **TextToSQL** - Généré avec IA • Made with Streamlit")
            
        except Exception as e:
            st.error(f"❌ Erreur application : {e}")
            st.info("🔄 Rafraîchissez la page pour réessayer")

# Point d'entrée de l'application
if __name__ == "__main__":
    app = StreamlitTextToSQL()
    app.run()
