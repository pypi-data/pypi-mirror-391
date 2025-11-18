from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory
from typing import Optional

from core.smart_retriever import get_smart_retriever
from core.llm_client import get_llm
from .base_agent import BaseAgent
from config.prompts.reviewer_prompt import REVIEWER_PROMPT
from data.utils_pdf import extract_text_images_tables

from core.debug_utils import debug_stage
from core.memory_manager import GLOBAL_MEMORY


class PaperReviewerAgent(BaseAgent):
    """
    Paper Reviewer Agent
    -------------------
    This agent specializes in paper review, literature analysis, 
    and scientific critique for bioimaging research.

    Responsibilities:
    - Review and critique scientific papers
    - Provide literature reviews and summaries
    - Analyze methodology and experimental design
    - Offer constructive feedback on research
    - Compare and synthesize findings across papers
    """
    def __init__(self, temperature: float = 0.3, debug: bool = False):
        super().__init__()
        
        # 1️⃣ Load SmartRetriever for automatic multi-collection search
        self.smart_retriever = get_smart_retriever()
        self.retriever = self.smart_retriever.get_retriever("papers", k=5)  # More context for reviews
        
        # 2️⃣ Load LLM client with slightly higher temperature for nuanced analysis
        self.llm = get_llm(temperature=temperature)
        
        # 3️⃣ Load reviewer-specific prompt
        self.prompt = ChatPromptTemplate.from_template(REVIEWER_PROMPT)
        
        # Session management
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
        return GLOBAL_MEMORY.get_session(session_id)
    
    def _extract_pdf_content(self, pdf_path: str) -> str:
        """Extract and format content from a PDF paper."""
        try:
            parsed = extract_text_images_tables(pdf_path)
            
            # Format the extracted content
            content_parts = []
            
            # Add main text
            if parsed.get("text"):
                content_parts.append("=== PAPER TEXT ===\n" + parsed["text"])
            
            # Add table summaries
            if parsed.get("tables"):
                content_parts.append(f"\n=== TABLES ({len(parsed['tables'])} found) ===")
                for i, table in enumerate(parsed["tables"], 1):
                    content_parts.append(f"\nTable {i}:\n{table.to_string()[:500]}")  # Limit table size
            
            # Add figure captions
            if parsed.get("figures"):
                content_parts.append(f"\n=== FIGURES ({len(parsed['figures'])} found) ===")
                for fig in parsed["figures"]:
                    content_parts.append(f"- {fig.get('caption', 'No caption')}")
            
            return "\n\n".join(content_parts)
        except Exception as e:
            return f"[Error extracting PDF: {str(e)}]"
    
    def _update_memory_with_pdf_context(self, session_id: str, pdf_path: str, content_summary: str):
        """Store PDF context in memory for later reference."""
        history = self._get_session_history(session_id)
        pdf_note = f"[PDF Paper uploaded: {pdf_path}]\nContent summary: {content_summary[:300]}..."
        history.add_ai_message(pdf_note)
    
    def run(self, query: str, pdf_path: Optional[str] = None, session_id: str = "default") -> str:
        """
        Run review pipeline for a given query.
        If pdf_path is provided, extract and analyze the paper content.
        """
        if pdf_path:
            print(f"📄 Extracting content from PDF: {pdf_path}")
            pdf_content = self._extract_pdf_content(pdf_path)
            
            # Enhance the query with PDF content
            enhanced_query = f"""I have uploaded a paper for review. Here is the extracted content:

{pdf_content}

User request: {query}

Please analyze this paper based on the request above."""
            
            # Store PDF context in memory
            history = self._get_session_history(session_id)
            history.add_user_message(f"[Uploaded PDF: {pdf_path}]")
            
            response = self.chat_chain.invoke(
                {"question": enhanced_query},
                config={"configurable": {"session_id": session_id}},
            )
            
            # Store a summary in memory
            self._update_memory_with_pdf_context(session_id, pdf_path, pdf_content)
            return response
        else:
            # Standard RAG query without PDF
            return self.chat_chain.invoke(
                {"question": query},
                config={"configurable": {"session_id": session_id}},
            )
    
    def stream(self, query: str, pdf_path: Optional[str] = None, session_id: str = "default"):
        """Stream review response for a given query."""
        if pdf_path:
            print(f"📄 Extracting content from PDF: {pdf_path}")
            pdf_content = self._extract_pdf_content(pdf_path)
            
            enhanced_query = f"""I have uploaded a paper for review. Here is the extracted content:

{pdf_content}

User request: {query}

Please analyze this paper based on the request above."""
            
            for chunk in self.chat_chain.stream(
                {"question": enhanced_query},
                config={"configurable": {"session_id": session_id}},
            ):
                yield chunk
        else:
            for chunk in self.chat_chain.stream(
                {"question": query},
                config={"configurable": {"session_id": session_id}},
            ):
                yield chunk

