from langchain_google_genai import ChatGoogleGenerativeAI
from config.settings import settings

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=settings.GEMINI_API_KEY,
    temperature=0,
)


async def rewrite_query(query: str) -> str:
    """
    Rewrites the user query for better hybrid retrieval.
    Falls back to the original query on any LLM error so the graph never crashes.
    """
    prompt = (
        "Rewrite the following user query to be optimized for hybrid vector/sparse search. "
        "Extract key financial entities, terms, and intent. "
        "Output ONLY the rewritten query text, no explanation.\n"
        f"Query: {query}"
    )
    try:
        response = await llm.ainvoke(prompt)
        return response.content.strip()
    except Exception:
        # Graceful degradation: use the original query if rewrite fails
        return query
