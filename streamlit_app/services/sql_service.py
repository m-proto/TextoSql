"""
🤖 Service de génération SQL
Gère la communication avec l'IA et la génération de requêtes
"""

import streamlit as st
import time
from typing import Dict, Any, Optional, List
import re


class SQLService:
    """Service de génération de requêtes SQL"""
    
    def __init__(self, services=None):
        self.services = services
        self.cache = services.get("cache") if services else None
        self.llm = services.get("llm") if services else None
        self.metrics = services.get("metrics") if services else None
    
    def generate_sql_response(self, question: str) -> Dict[str, Any]:
        """
        Génère une réponse SQL complète pour une question
        
        Args:
            question: Question en langage naturel
            
        Returns:
            Dictionnaire avec la réponse générée
        """
        start_time = time.time()
        
        try:
            # Vérifier le cache d'abord
            if self.cache:
                cached_result = self.cache.get(question)
                if cached_result:
                    if self.metrics:
                        self.metrics.record_cache_hit()
                    
                    return {
                        "success": True,
                        "sql": cached_result["sql"],
                        "execution_time": time.time() - start_time,
                        "cached": True,
                        "result": cached_result.get("result"),
                        "response_type": "sql_cached"
                    }
            
            # Génération SQL avec LLM
            if self.metrics:
                self.metrics.record_cache_miss()
                self.metrics.record_sql_generation()
            
            # Schéma de base de données
            schema = self._get_database_schema()
            
            # Générer le SQL
            sql_query = self._generate_sql_with_llm(question, schema)
            
            if not sql_query:
                return {
                    "success": False,
                    "error": "Impossible de générer la requête SQL pour cette question",
                    "response_type": "error"
                }
            
            # Analyser les tables utilisées
            used_tables = self._extract_tables_from_sql(sql_query)
            if used_tables:
                st.session_state.used_tables = used_tables
            
            # Préparer la réponse
            response_data = {
                "success": True,
                "sql": sql_query,
                "execution_time": time.time() - start_time,
                "cached": False,
                "response_type": "sql_generated",
                "tables_used": used_tables
            }
            
            # Mettre en cache
            if self.cache:
                self.cache.set(question, {
                    "sql": sql_query,
                    "timestamp": time.time(),
                    "tables_used": used_tables
                })
            
            return response_data
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Erreur lors de la génération SQL : {str(e)}",
                "response_type": "error",
                "execution_time": time.time() - start_time
            }
    
    def _get_database_schema(self) -> str:
        """Retourne le schéma de la base de données"""
        return """
        Tables disponibles dans votre base de données :
        
        🏢 **UTILISATEURS**
        - users (id, name, email, created_at, last_login, status)
        
        🛒 **COMMANDES** 
        - orders (id, user_id, amount, order_date, status, payment_method)
        - order_items (id, order_id, product_id, quantity, price)
        
        📦 **PRODUITS**
        - products (id, name, price, category, stock_quantity, created_at)
        - categories (id, name, description)
        
        💰 **FINANCES**
        - payments (id, order_id, amount, payment_date, method, status)
        """
    
    def _generate_sql_with_llm(self, question: str, schema: str) -> Optional[str]:
        """Génère le SQL avec le LLM"""
        if not self.llm or not self.llm.is_available():
            # Fallback avec SQL simulé
            return self._generate_mock_sql(question)
        
        try:
            return self.llm.generate_sql(question, schema)
        except Exception as e:
            st.error(f"Erreur LLM : {str(e)}")
            return self._generate_mock_sql(question)
    
    def _generate_mock_sql(self, question: str) -> str:
        """Génère du SQL simulé pour les tests"""
        question_lower = question.lower()
        
        # Détection de mots-clés simples
        if any(word in question_lower for word in ['utilisateur', 'user', 'ユーザー']):
            return """SELECT COUNT(*) as total_users
FROM users
WHERE status = 'active';"""
        
        elif any(word in question_lower for word in ['vente', 'sale', 'commande', 'order', '売上', '注文']):
            return """SELECT 
    DATE_TRUNC('month', order_date) as month,
    SUM(amount) as total_sales
FROM orders
WHERE order_date >= DATE_SUB(CURRENT_DATE, INTERVAL 12 MONTH)
GROUP BY month
ORDER BY month DESC;"""
        
        elif any(word in question_lower for word in ['produit', 'product', '商品']):
            return """SELECT 
    p.name,
    SUM(oi.quantity) as total_sold
FROM products p
JOIN order_items oi ON p.id = oi.product_id
GROUP BY p.id, p.name
ORDER BY total_sold DESC
LIMIT 10;"""
        
        else:
            # SQL générique
            return """SELECT COUNT(*) as total_records
FROM users
WHERE created_at >= DATE_SUB(CURRENT_DATE, INTERVAL 30 DAY);"""
    
    def _extract_tables_from_sql(self, sql: str) -> List[str]:
        """Extrait les noms de tables d'une requête SQL"""
        tables = []
        
        # Pattern pour FROM et JOIN
        patterns = [
            r'FROM\s+([a-zA-Z_][a-zA-Z0-9_]*)',
            r'JOIN\s+([a-zA-Z_][a-zA-Z0-9_]*)',
            r'INNER\s+JOIN\s+([a-zA-Z_][a-zA-Z0-9_]*)',
            r'LEFT\s+JOIN\s+([a-zA-Z_][a-zA-Z0-9_]*)',
            r'RIGHT\s+JOIN\s+([a-zA-Z_][a-zA-Z0-9_]*)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, sql, re.IGNORECASE)
            tables.extend(matches)
        
        # Supprimer les doublons et nettoyer
        unique_tables = list(set(tables))
        return [table.strip() for table in unique_tables if table.strip()]
    
    def format_sql_response(self, response_data: Dict[str, Any], language: str = 'fr') -> str:
        """Formate la réponse SQL pour l'affichage"""
        if not response_data.get("success", False):
            error_messages = {
                'fr': f"❌ **Erreur :** {response_data.get('error', 'Erreur inconnue')}",
                'en': f"❌ **Error:** {response_data.get('error', 'Unknown error')}",
                'ja': f"❌ **エラー:** {response_data.get('error', '不明なエラー')}"
            }
            return error_messages.get(language, error_messages['fr'])
        
        sql = response_data["sql"]
        cached = response_data.get("cached", False)
        execution_time = response_data.get("execution_time", 0)
        
        # Titre selon la langue et statut cache
        titles = {
            'fr': {
                True: "🎯 **Voici la requête SQL pour votre question :** 📂 **(depuis le cache)**",
                False: "🎯 **Voici la requête SQL pour votre question :** 🆕 **(nouvellement généré)**"
            },
            'en': {
                True: "🎯 **Here's the SQL query for your question:** 📂 **(from cache)**",
                False: "🎯 **Here's the SQL query for your question:** 🆕 **(newly generated)**"
            },
            'ja': {
                True: "🎯 **あなたの質問に対するSQLクエリ：** 📂 **(キャッシュから)**",
                False: "🎯 **あなたの質問に対するSQLクエリ：** 🆕 **(新規生成)**"
            }
        }
        
        title = titles.get(language, titles['fr'])[cached]
        
        # Actions suivantes
        next_actions = {
            'fr': "💡 **Que souhaitez-vous faire maintenant ?**",
            'en': "💡 **What would you like to do next?**",
            'ja': "💡 **次に何をしますか？**"
        }
        
        return f"""{title}

```sql
{sql}
```

⚡ *Généré en {execution_time:.2f}s*

{next_actions.get(language, next_actions['fr'])}
"""
