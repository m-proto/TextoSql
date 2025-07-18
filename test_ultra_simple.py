"""
Test ultra-simple avec votre ancien code
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Utilisons votre ancien code simple
from infrastructure.settings import settings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.utilities import SQLDatabase
from sqlalchemy.engine import create_engine
from sqlalchemy import inspect

def test_ultra_simple():
    """Test avec votre ancien code qui marchait"""
    print("🔧 Test connexion Redshift...")
    
    try:
        # Votre ancien code qui marchait
        dsn = settings.redshift_dsn
        engine = create_engine(dsn)
        
        # Test de connexion
        with engine.connect() as conn:
            result = conn.execute("SELECT 1").fetchone()
            print(f"✅ Connexion OK: {result}")
        
        # Tables
        inspector = inspect(engine)
        tables = inspector.get_table_names(schema=settings.redshift_schema)
        print(f"📋 Tables trouvées: {len(tables)}")
        
        # SQLDatabase
        db = SQLDatabase(engine, schema=settings.redshift_schema, include_tables=tables)
        print("✅ SQLDatabase créé")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    
    print("\n🤖 Test LLM...")
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0,
            google_api_key=settings.google_api_key
        )
        print("✅ LLM OK")
    except Exception as e:
        print(f"❌ Erreur LLM: {e}")
        return False
    
    print("\n🎉 Votre système de base fonctionne parfaitement !")
    return True

if __name__ == "__main__":
    test_ultra_simple()
