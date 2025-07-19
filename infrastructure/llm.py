from langchain_google_genai import ChatGoogleGenerativeAI
from infrastructure.settings import settings
from infrastructure.logging import logger

class LLMManager:
    """Gestionnaire pour les interactions avec le modèle LLM"""
    
    def __init__(self):
        """Initialise le gestionnaire LLM"""
        self.llm = None
        self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialise le modèle LLM avec gestion d'erreur"""
        try:
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                temperature=0,
                google_api_key=settings.google_api_key
            )
            logger.info("LLM initialisé avec succès", model="gemini-1.5-flash")
        except Exception as e:
            logger.error("Erreur lors de l'initialisation du LLM", error=str(e))
            self.llm = None
    
    def generate_sql(self, question: str, schema_info: str = "") -> str:
        """Génère une requête SQL à partir d'une question en langage naturel"""
        if not self.llm:
            raise ValueError("LLM non initialisé")
        
        prompt = f"""
        Convertis cette question en requête SQL valide.
        
        Question: {question}
        
        Schéma de base de données: {schema_info}
        
        Réponds uniquement avec la requête SQL, sans explication.
        """
        
        try:
            response = self.llm.invoke(prompt)
            return response.content.strip()
        except Exception as e:
            logger.error("Erreur lors de la génération SQL", error=str(e), question=question)
            raise
    
    def is_available(self) -> bool:
        """Vérifie si le LLM est disponible"""
        return self.llm is not None

def init_llm():
    """Fonction legacy pour compatibilité"""
    return ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=0,
        google_api_key=settings.google_api_key
    )
