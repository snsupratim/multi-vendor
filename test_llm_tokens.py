import asyncio
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from core.config import settings

async def test_llm():
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=settings.GEMINI_API_KEY,
    )
    res = await llm.ainvoke([HumanMessage(content="Hello")])
    
    print(f"response_metadata: {res.response_metadata}")
    print(f"usage_metadata: {getattr(res, 'usage_metadata', None)}")

if __name__ == "__main__":
    asyncio.run(test_llm())
