"""
🔧 Configuration simplifiée pour test entre collègues
"""

from typing import Dict, Any
from streamlit_app.config.settings import AppConfig as BaseAppConfig


class SimpleConfig(BaseAppConfig):
    """Configuration simple pour test"""
    
    @staticmethod
    def get_app_settings() -> Dict[str, Any]:
        """Configuration basique pour les tests"""
        base_settings = BaseAppConfig.get_app_settings()
        
        # Paramètres simples pour test entre collègues
        return {
            **base_settings,
            'page_title': '🧪 TextToSQL - Test',
            'page_icon': '🧪',
            'debug': True,  # Facilite le debug
            'initial_sidebar_state': 'expanded',
            'theme': {
                'primaryColor': '#FF6B6B',
                'backgroundColor': '#FFFFFF', 
                'secondaryBackgroundColor': '#F0F2F6',
                'textColor': '#262730'
            }
        }


# Instance simple
simple_config = SimpleConfig()
