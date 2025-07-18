import datetime
from langchain.chains import create_sql_query_chain
from infrastructure.settings import settings
from infrastructure.logging import logger

def generate_sql_query_only(question: str, llm, db):
    """Génère une requête SQL à partir d'une question en langage naturel"""
    logger.info("Starting SQL generation", question=question)
    
    try:
        chain = create_sql_query_chain(llm, db)
        sql = chain.invoke({"question": question})
        
        logger.info("SQL generation successful", sql=sql)
        return sql

    except Exception as e:
        logger.error("SQL generation failed", error=str(e), question=question)
        return None
