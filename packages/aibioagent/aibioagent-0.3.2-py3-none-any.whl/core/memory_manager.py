"""
core/memory_manager.py
----------------------
Contextual query rewriting based on conversation history.
"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.chat_history import InMemoryChatMessageHistory
from core.llm_client import get_llm

class MemoryManager:
    """Uses the LLM to rewrite queries using previous conversation."""

    def __init__(self, temperature: float = 0.1):
        self.llm = get_llm(temperature=temperature)
        self._sessions = {}
        self.contextualizer_prompt = ChatPromptTemplate.from_template("""
        You are a helpful assistant that rewrites the latest user query
        so it makes sense without prior context.

        Conversation so far:
        {history}

        User's latest query:
        {query}

        Rewrite the user's query to be self-contained but preserve its intent.
        """)

        self.rewrite_chain = (
            {"history": RunnablePassthrough(), "query": RunnablePassthrough()}
            | self.contextualizer_prompt
            | self.llm
            | StrOutputParser()
        )
    # ------------------------------------------------------------------
    # 🔹 Shared memory methods
    # ------------------------------------------------------------------
    def get_session(self, session_id: str) -> InMemoryChatMessageHistory:
        """Return a shared chat memory object for the given session_id."""
        if session_id not in self._sessions:
            self._sessions[session_id] = InMemoryChatMessageHistory()
        return self._sessions[session_id]
    
    def add_user_message(self, session_id: str, message: str):
        """Append a user message to session memory."""
        self.get_session(session_id).add_user_message(message)

    def add_ai_message(self, session_id: str, message: str):
        """Append an AI message to session memory."""
        self.get_session(session_id).add_ai_message(message)

    def get_history_text(self, session_id: str) -> str:
        """Return the conversation history formatted as text."""
        hist = self.get_session(session_id)
        if not hist.messages:
            return ""
        lines = []
        for m in hist.messages:
            role = "User" if m.type == "human" else "AI"
            lines.append(f"{role}: {m.content}")
        return "\n".join(lines)
    
    def clear(self, session_id: str = None):
        """Clear one or all sessions."""
        if session_id:
            self._sessions.pop(session_id, None)
        else:
            self._sessions.clear()

    # ------------------------------------------------------------------
    # 🔹 Contextual query rewriting
    # ------------------------------------------------------------------
    def contextualize(self, query: str, session_id: str) -> str:
        """Rewrite user query using previous history."""
        history_text = self.get_history_text(session_id)
        if not history_text.strip():
            return query  # no prior context
        return self.rewrite_chain.invoke({"history": history_text, "query": query})
    
if __name__ == "__main__":

    memory = MemoryManager()

    session_id = "test_session"
    memory.add_user_message(session_id, "How many cups of water should an adult drink?")
    memory.add_ai_message(session_id, "An adult should drink about 8 cups of water daily.")
    memory.add_user_message(session_id, "What about a child?")

    rewritten = memory.contextualize("What about a child?", session_id)
    print("Rewritten query:", rewritten)

# ----------------------------------------------------------------------
# ✅ Global shared memory instance
# ----------------------------------------------------------------------
GLOBAL_MEMORY = MemoryManager()