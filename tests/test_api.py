"""
Tests automatisés pour l'API TextToSQL
"""
import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from api import app
from core.settings import settings

@pytest.fixture
def client():
    """Client de test FastAPI"""
    return TestClient(app)

@pytest.fixture
def mock_db():
    """Mock de la base de données"""
    db = Mock()
    db.get_table_info.return_value = "Table: users\nColumns: id, name, email"
    db.run.return_value = [{"id": 1, "name": "John", "email": "john@example.com"}]
    return db

@pytest.fixture
def mock_llm():
    """Mock du LLM"""
    llm = Mock()
    return llm

class TestHealthEndpoint:
    """Tests pour l'endpoint de santé"""
    
    def test_health_check_success(self, client):
        """Test du health check en cas de succès"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "database_connected" in data

class TestSQLGeneration:
    """Tests pour la génération SQL"""
    
    @patch('api.generate_sql_query_only')
    def test_generate_sql_success(self, mock_generate, client):
        """Test de génération SQL réussie"""
        mock_generate.return_value = "SELECT * FROM users"
        
        response = client.post("/sql/generate", json={
            "question": "Show me all users",
            "execute_query": False
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["sql"] == "SELECT * FROM users"
        assert "execution_time" in data
        assert data["cached"] is False
    
    def test_generate_sql_empty_question(self, client):
        """Test avec question vide"""
        response = client.post("/sql/generate", json={
            "question": "",
            "execute_query": False
        })
        
        assert response.status_code == 422  # Validation error
    
    def test_generate_sql_long_question(self, client):
        """Test avec question trop longue"""
        long_question = "a" * 501
        response = client.post("/sql/generate", json={
            "question": long_question,
            "execute_query": False
        })
        
        assert response.status_code == 422  # Validation error

class TestRateLimiting:
    """Tests pour le rate limiting"""
    
    @patch('api.generate_sql_query_only')
    def test_rate_limit_exceeded(self, mock_generate, client):
        """Test de dépassement de limite de taux"""
        mock_generate.return_value = "SELECT 1"
        
        # Simule de nombreuses requêtes
        for i in range(settings.rate_limit_requests + 1):
            response = client.post("/sql/generate", json={
                "question": f"Test query {i}",
                "execute_query": False
            })
            
            if i < settings.rate_limit_requests:
                assert response.status_code == 200
            else:
                assert response.status_code == 429

class TestCaching:
    """Tests pour le cache"""
    
    @patch('api.cache_manager')
    @patch('api.generate_sql_query_only')
    def test_cache_hit(self, mock_generate, mock_cache, client):
        """Test de hit cache"""
        mock_cache.get_cached_sql_result.return_value = {
            "sql": "SELECT * FROM users",
            "result": [{"id": 1, "name": "John"}]
        }
        
        response = client.post("/sql/generate", json={
            "question": "Show me all users",
            "use_cache": True
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["cached"] is True
        assert data["sql"] == "SELECT * FROM users"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
