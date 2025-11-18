from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory

from core.smart_retriever import get_smart_retriever
from core.llm_client import get_llm
from .base_agent import BaseAgent
from config.prompts.scientist_prompt import SCIENTIST_PROMPT

from core.debug_utils import debug_stage
from core.memory_manager import GLOBAL_MEMORY

class AIScientistAgent(BaseAgent):
    """
    AI Scientist Agent
    ------------------
    This agent performs retrieval-augmented generation (RAG)
    for scientific reasoning and literature question answering.

    Now uses SmartRetriever to automatically search ALL user collections.

    Responsibilities:
    - Defines its own prompt
    - Initializes RAG pipeline (retriever + LLM)
    - Exposes a simple `.run(query)` interface
    """
    def __init__(self, temperature: float = 0.2, debug: bool = False):
        super().__init__()
        # 1️⃣ Use SmartRetriever to search ALL collections
        self.smart_retriever = get_smart_retriever()
        # Get retriever function that searches all collections
        self.retriever = self.smart_retriever.get_retriever("all", k=3)
        # 2️⃣ Load LLM client
        self.llm = get_llm(temperature=temperature)
        # 3️⃣ Load predefined prompt from config/prompts
        self.prompt = ChatPromptTemplate.from_template(SCIENTIST_PROMPT)
        # Use the new in-memory chat history
        self.session_store = {}
        self.debug = debug
        # 4️⃣ Build retrieval-augmented pipeline
        def maybe_debug(label):
            return debug_stage(label) if self.debug else RunnablePassthrough()
        
        self.rag_chain = (
            {
                "context": (lambda x: x["question"]) 
                    | maybe_debug("Retriever Input")
                    | self.retriever 
                    | maybe_debug("Retriever Output (Documents)")
                    | self._combine_docs 
                    | maybe_debug("Combined Context Text"),
                "question": (lambda x: x["question"]) | maybe_debug("User Question"),
                "history": (lambda x: self._format_history(x.get("history", []))),
            }
            | maybe_debug("Pre-Prompt Assembly")
            | self.prompt
            | maybe_debug("Prompt to LLM")
            | self.llm
            | maybe_debug("LLM Raw Output")
            | StrOutputParser()
            | maybe_debug("Final Parsed Output")
        )
        # Wrap the chain with session-based chat history
        self.chat_chain = RunnableWithMessageHistory(
            self.rag_chain,
            self._get_session_history,
            input_messages_key="question",
            history_messages_key="history",
        )

    def _combine_docs(self, docs):
        """Merge retrieved documents into a single context string."""
        return "\n\n".join([d.page_content for d in docs])
    
    def _format_history(self, msgs):
        """Convert list of chat messages into a readable text block."""
        if not msgs:
            return ""
        lines = []
        for m in msgs:
            role = "User" if m.type == "human" else "AI"
            lines.append(f"{role}: {m.content}")
        return "\n".join(lines)
    
    def _get_session_history(self, session_id: str):
        """Retrieve or create a per-session message history."""
        #print("session id is ", session_id)
        # if session_id not in self.session_store:
        #     self.session_store[session_id] = InMemoryChatMessageHistory()
        # return self.session_store[session_id]
        return GLOBAL_MEMORY.get_session(session_id)
    
    def run(self, query: str, session_id: str = "default") -> str:
        """Run RAG pipeline for a given query."""
        return self.chat_chain.invoke(
            {"question": query},
            config={"configurable": {"session_id": session_id}},
        )
    
    def stream(self, query: str, session_id: str = "default"):
        for chunk in self.chat_chain.stream(
            {"question": query},
            config={"configurable": {"session_id": session_id}},
        ):
            yield chunk
        
if __name__ == "__main__":
    agent = AIScientistAgent()
    while True:
        query = input("🧠 Enter your scientific question (or 'exit'): ")
        if query.lower() in ["exit", "quit"]:
            break
        response = agent.run(query)
        print(f"\n🧩 Answer:\n{response}\n")















    






