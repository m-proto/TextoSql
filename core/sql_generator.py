import datetime
from langchain.chains import create_sql_query_chain
from core.settings import settings
from core.logging import logger

def generate_sql_query_only(question: str, llm, db):
    print(f"\n--- Generating SQL for: '{question}' ---")
    try:
        chain = create_sql_query_chain(llm, db)
        sql = chain.invoke({"question": question})

        print("\n--- Generated SQL ---")
        print(sql)
        print("----------------------\n")

        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_FILE_PATH, "a", encoding="utf-8") as f:
            f.write("=" * 50 + "\n")
            f.write(f"Timestamp: {current_time}\n")
            f.write(f"Natural Language Query:\n{question}\n\n")
            f.write(f"Generated SQL Query:\n{sql}\n")
            f.write("=" * 50 + "\n\n")

        print(f"✅ Saved to '{LOG_FILE_PATH}'")
        return sql

    except Exception as e:
        print(f"❌ Error during SQL generation: {e}")
        return None
