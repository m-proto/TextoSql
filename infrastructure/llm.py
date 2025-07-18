from langchain_google_genai import ChatGoogleGenerativeAI
from core.settings import settings

def init_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=0,
        google_api_key=settings.google_api_key
    )
