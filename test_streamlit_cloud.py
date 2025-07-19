"""
🧪 Tests simples pour CI/CD Streamlit Cloud
Validation légère avant déploiement
"""

import sys
import os
from pathlib import Path

# Ajouter le projet au path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test que tous les modules principaux s'importent correctement"""
    try:
        print("🔍 Test des imports principaux...")
        
        # Test infrastructure
        from infrastructure.settings import settings
        from infrastructure.llm import LLMManager
        from infrastructure.cache import CacheManager
        print("✅ Infrastructure OK")
        
        # Test streamlit app
        from streamlit_app.config.settings import AppConfig
        from streamlit_app.chatbot import TextToSQLChatBot
        print("✅ Streamlit App OK")
        
        # Test services
        from streamlit_app.services.sql_service import SQLService
        print("✅ Services OK")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_configuration():
    """Test que la configuration fonctionne"""
    try:
        print("🔧 Test de configuration...")
        
        from streamlit_app.config.settings import AppConfig
        
        # Test récupération config
        config = AppConfig.get_app_settings()
        assert 'page_title' in config
        assert 'page_icon' in config
        print("✅ Configuration OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur config: {e}")
        return False

def test_requirements():
    """Test que requirements.txt est valide"""
    try:
        print("📋 Test requirements.txt...")
        
        req_file = Path("requirements.txt")
        if not req_file.exists():
            print("❌ requirements.txt manquant")
            return False
            
        # Lire et valider
        with open(req_file, 'r') as f:
            requirements = f.read()
            
        essential_packages = [
            'streamlit',
            'langchain',
            'pydantic'
        ]
        
        for package in essential_packages:
            if package not in requirements:
                print(f"❌ Package manquant: {package}")
                return False
                
        print("✅ Requirements OK")
        return True
        
    except Exception as e:
        print(f"❌ Erreur requirements: {e}")
        return False

def test_streamlit_entry():
    """Test que le point d'entrée Streamlit existe"""
    try:
        print("🚀 Test point d'entrée...")
        
        # Test que streamlit_main.py existe
        main_file = Path("streamlit_main.py")
        if not main_file.exists():
            print("❌ streamlit_main.py manquant")
            return False
            
        # Test que le contenu est valide
        with open(main_file, 'r') as f:
            content = f.read()
            
        if 'from streamlit_app.main import main' not in content:
            print("❌ Import incorrect dans streamlit_main.py")
            return False
            
        print("✅ Point d'entrée OK")
        return True
        
    except Exception as e:
        print(f"❌ Erreur point d'entrée: {e}")
        return False

def run_all_tests():
    """Lance tous les tests"""
    print("🧪 === TESTS CI/CD STREAMLIT CLOUD ===\n")
    
    tests = [
        test_requirements,
        test_streamlit_entry,
        test_imports,
        test_configuration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()  # Ligne vide
        except Exception as e:
            print(f"❌ Test échoué: {e}\n")
    
    # Résumé
    print("=" * 50)
    print(f"📊 RÉSUMÉ: {passed}/{total} tests passés")
    
    if passed == total:
        print("🎉 TOUS LES TESTS PASSENT - PRÊT POUR DÉPLOIEMENT!")
        return True
    else:
        print("⚠️  CERTAINS TESTS ÉCHOUENT - VÉRIFIER AVANT DÉPLOIEMENT")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
