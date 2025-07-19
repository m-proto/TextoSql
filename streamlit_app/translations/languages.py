"""
🌐 Gestion multilingue centralisée
Contient toutes les traductions de l'interface
"""

from typing import Dict, Any


class LanguageManager:
    """Gestionnaire des traductions multilingues"""
    
    def __init__(self):
        self.translations = {
            'fr': {
                'title': '🤖 Assistant SQL Intelligent',
                'subtitle': 'Posez vos questions en français, obtenez du SQL professionnel !',
                'welcome': '👋 Bonjour ! Je suis votre assistant SQL. Posez-moi des questions sur vos données et je génèrerai les requêtes SQL correspondantes.',
                'examples_title': '💡 Exemples :',
                'service_status': '🔧 Statut des Services',
                'ai_connected': '✅ IA connectée',
                'ai_disconnected': '❌ IA non disponible',
                'cache_active': '✅ Cache actif',
                'session_stats': '📊 Statistiques de Session',
                'questions': 'Questions',
                'sql_generated': 'SQL générés',
                'cache_hits': 'Cache hits',
                'cache_rate': 'Taux cache',
                'session': 'Session',
                'tables_used': '📈 Tables utilisées',
                'last_question': 'Pour votre dernière question',
                'example_questions': '💡 Questions d\'Exemple',
                'actions': '🎛️ Actions',
                'new_conversation': '🗑️ Nouvelle conversation',
                'export_conversation': '📥 Exporter conversation',
                'language': '🌍 Langue',
                'input_placeholder': 'Posez votre question sur vos données...',
                'sql_query_title': '🎯 **Voici la requête SQL pour votre question :**',
                'from_cache': '📂 **(depuis le cache)**',
                'newly_generated': '🆕 **(nouvellement généré)**',
                'next_actions': '💡 **Que souhaitez-vous faire maintenant ?**',
                'copy_sql': '📋 Copier SQL',
                'download': '💾 Télécharger',
                'explain': '🔍 Expliquer'
            },
            'en': {
                'title': '🤖 Smart SQL Assistant',
                'subtitle': 'Ask questions in English, get professional SQL!',
                'welcome': '👋 Hello! I am your SQL assistant. Ask me questions about your data and I will generate the corresponding SQL queries.',
                'examples_title': '💡 Examples:',
                'service_status': '🔧 Service Status',
                'ai_connected': '✅ AI connected',
                'ai_disconnected': '❌ AI unavailable',
                'cache_active': '✅ Cache active',
                'session_stats': '📊 Session Statistics',
                'questions': 'Questions',
                'sql_generated': 'SQL generated',
                'cache_hits': 'Cache hits',
                'cache_rate': 'Cache rate',
                'session': 'Session',
                'tables_used': '📈 Tables used',
                'last_question': 'For your last question',
                'example_questions': '💡 Example Questions',
                'actions': '🎛️ Actions',
                'new_conversation': '🗑️ New conversation',
                'export_conversation': '📥 Export conversation',
                'language': '🌍 Language',
                'input_placeholder': 'Ask your question about the data...',
                'sql_query_title': '🎯 **Here\'s the SQL query for your question:**',
                'from_cache': '📂 **(from cache)**',
                'newly_generated': '🆕 **(newly generated)**',
                'next_actions': '💡 **What would you like to do next?**',
                'copy_sql': '📋 Copy SQL',
                'download': '💾 Download',
                'explain': '🔍 Explain'
            },
            'ja': {
                'title': '🤖 スマートSQL アシスタント',
                'subtitle': '日本語で質問して、プロ仕様のSQLを取得！',
                'welcome': '👋 こんにちは！私はあなたのSQLアシスタントです。データについて質問していただければ、対応するSQLクエリを生成します。',
                'examples_title': '💡 例：',
                'service_status': '🔧 サービス状態',
                'ai_connected': '✅ AI接続済み',
                'ai_disconnected': '❌ AI利用不可',
                'cache_active': '✅ キャッシュ有効',
                'session_stats': '📊 セッション統計',
                'questions': '質問数',
                'sql_generated': 'SQL生成数',
                'cache_hits': 'キャッシュヒット',
                'cache_rate': 'キャッシュ率',
                'session': 'セッション',
                'tables_used': '📈 使用テーブル',
                'last_question': '最後の質問で使用',
                'example_questions': '💡 質問例',
                'actions': '🎛️ アクション',
                'new_conversation': '🗑️ 新しい会話',
                'export_conversation': '📥 会話をエクスポート',
                'language': '🌍 言語',
                'input_placeholder': 'データについて質問してください...',
                'sql_query_title': '🎯 **あなたの質問に対するSQLクエリ：**',
                'from_cache': '📂 **(キャッシュから)**',
                'newly_generated': '🆕 **(新規生成)**',
                'next_actions': '💡 **次に何をしますか？**',
                'copy_sql': '📋 SQLをコピー',
                'download': '💾 ダウンロード',
                'explain': '🔍 説明'
            }
        }
        
        self.welcome_examples = {
            'fr': "\n\n💡 **Exemples :**\n- Combien d'utilisateurs avons-nous ?\n- Quelles sont les ventes du mois dernier ?\n- Top 10 des produits les plus vendus",
            'en': "\n\n💡 **Examples:**\n- How many users do we have?\n- What are last month's sales?\n- Top 10 best-selling products",
            'ja': "\n\n💡 **例：**\n- ユーザー数は？\n- 先月の売上は？\n- 売上トップ10の商品"
        }
    
    def get_text(self, key: str, language: str = 'fr') -> str:
        """
        Récupère un texte traduit
        
        Args:
            key: Clé de traduction
            language: Code de langue ('fr', 'en', 'ja')
            
        Returns:
            Texte traduit ou clé si non trouvé
        """
        return self.translations.get(language, self.translations['fr']).get(key, key)
    
    def get_welcome_with_examples(self, language: str = 'fr') -> str:
        """
        Récupère le message d'accueil avec exemples
        
        Args:
            language: Code de langue
            
        Returns:
            Message d'accueil complet avec exemples
        """
        welcome = self.get_text('welcome', language)
        examples = self.welcome_examples.get(language, self.welcome_examples['fr'])
        return welcome + examples
    
    def get_available_languages(self) -> Dict[str, str]:
        """Retourne les langues disponibles"""
        return {
            'fr': '🇫🇷 Français',
            'en': '🇺🇸 English', 
            'ja': '🇯🇵 日本語'
        }
    
    def is_valid_language(self, language: str) -> bool:
        """Vérifie si une langue est supportée"""
        return language in self.translations


# Instance globale pour faciliter l'utilisation
language_manager = LanguageManager()
