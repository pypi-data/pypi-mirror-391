"""
agents/image_analyst_agent.py
-----------------------------
Multimodal ImageAnalystAgent that reads microscopy images and
designs a workflow based on both user goals and literature context.

Now uses SmartRetriever to automatically search ALL user collections.
"""

import numpy as np
from PIL import Image
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory
from core.smart_retriever import get_smart_retriever
from core.llm_client import get_llm, get_vision_llm  # <-- use vision-capable LLM here
from config.settings import CHROMA_DIR
from .base_agent import BaseAgent
from core.debug_utils import debug_stage
from config.prompts.imageanalyst_prompt import IMANALYST_PROMPT
from core.memory_manager import GLOBAL_MEMORY

class ImageAnalystAgent(BaseAgent):
    """Analyzes raw microscopy images and suggests a workflow."""
    def __init__(self, temperature: float = 0.3, debug: bool = False):
        super().__init__()
        self.text_llm = get_llm(temperature=temperature)
        self.vision_llm, self.call_with_image = get_vision_llm(temperature=temperature)
        
        # Use SmartRetriever to search ALL collections
        self.smart_retriever = get_smart_retriever()
        # Get retriever functions for papers and code docs
        self.bio_retriever = self.smart_retriever.get_retriever("papers", k=3)
        self.fiji_retriever = self.smart_retriever.get_retriever("code", k=3)

        # Define multimodal prompt
        self.prompt = ChatPromptTemplate.from_template(IMANALYST_PROMPT)
        self.debug = debug
        def maybe_debug(label):
            return debug_stage(label) if self.debug else RunnablePassthrough()
        self.rag_chain = (
            RunnablePassthrough()
            | maybe_debug("Assembling Inputs")
            | self._assemble_inputs
            | maybe_debug("Pre-Prompt Assembly")
            | self.prompt
            | maybe_debug("Prompt to LLM")
            | self.text_llm
            | maybe_debug("LLM Output")
            | StrOutputParser()
            | maybe_debug("Parsed Output")
        )


        self.session_store = {}
        self.chat_chain = RunnableWithMessageHistory(
            self.rag_chain,
            self._get_session_history,
            input_messages_key="user_goal",
            history_messages_key="history",
        )

    def _retrieve_context(self, query: str):
        """Retrieve relevant text context from scientific and code documentation."""
        # SmartRetriever returns list of documents
        sci_docs = self.bio_retriever(query)
        fiji_docs = self.fiji_retriever(query)

        sci_context = "\n\n".join([d.page_content for d in sci_docs])
        fiji_context = "\n\n".join([d.page_content for d in fiji_docs])

        return {"scientific_context": sci_context, "fiji_context": fiji_context}
        
    def _assemble_inputs(self, inputs):
        """
        Combine user_goal, retrieved contexts, and history into one dict
        compatible with the prompt template.
        """
        query = inputs["user_goal"]
        context_dict = self._retrieve_context(query)
        history_text = self._format_history(inputs.get("history", []))
        # 👀 Extract remembered image context from history if present
        image_context = ""
        for msg in reversed(inputs.get("history", [])):
            if "[Image context remembered:" in msg.content:
                image_context = msg.content
                break
        if image_context:
            context_dict["scientific_context"] += f"\n\n🧠 Previous Image Context:\n{image_context}"

        return {
            "user_goal": query,
            "scientific_context": context_dict["scientific_context"],
            "fiji_context": context_dict["fiji_context"],
            "history": self._format_history(inputs.get("history", [])),
        }

    def _format_history(self, msgs):
        """Convert previous turns into readable text."""
        if not msgs:
            return ""
        lines = []
        for m in msgs:
            role = "User" if m.type == "human" else "AI"
            lines.append(f"{role}: {m.content}")
        return "\n".join(lines)
    
    def _get_session_history(self, session_id: str):
        """Retrieve or create chat memory per session."""
        # if session_id not in self.session_store:
        #     self.session_store[session_id] = InMemoryChatMessageHistory()
        # return self.session_store[session_id]
        return GLOBAL_MEMORY.get_session(session_id)
    
    def _build_prompt_text(self, user_goal: str):
        """Helper to compose final prompt text."""
        ctx = self._retrieve_context(user_goal)
        prompt_text = self.prompt.format(
            user_goal=user_goal,
            scientific_context=ctx["scientific_context"],
            fiji_context=ctx["fiji_context"],
        )
        return prompt_text
    
    def _update_memory_with_image_context(self, session_id: str, image_path: str, summary_text: str):
        """
        Store the image description or analysis summary in memory so that
        later text-only queries can recall what image was discussed.
        """
        history = self._get_session_history(session_id)
        image_note = f"[Image context remembered: {image_path}]\nSummary: {summary_text[:500]}"
        history.add_ai_message(image_note)

    def run(self, user_goal: str, image_path: str = None, session_id: str = "default") -> str:
        """
        Run the agent:
        - If image_path provided → vision model
        - Else → text-only model
        """
        prompt_text = self._build_prompt_text(user_goal)
        history = self._get_session_history(session_id)
        if image_path:
            print(f"🖼️ Using vision model for image: {image_path}")
            history.add_user_message(f"[Image Input: {image_path}]\n{user_goal}")
            response = self.call_with_image(prompt_text, image_path)
            response_text = response.content if hasattr(response, "content") else str(response)
            # Record AI response
            history.add_ai_message(response_text)
            # 🧠 Store a textual memory of this image for later turns
            self._update_memory_with_image_context(session_id, image_path, response_text)
            return response_text
        else:
            print("💬 Using text-only model (no image provided)")
            response = self.chat_chain.invoke(
                {"user_goal": user_goal},
                config={"configurable": {"session_id": session_id}},
            )

        return response.content if hasattr(response, "content") else response
    
    def stream(self, user_goal: str, image_path: str = None, session_id: str = "default"):
        """
        Stream model output, maintaining memory consistency for both text and image paths.
        """
        prompt_text = self._build_prompt_text(user_goal)
        history = self._get_session_history(session_id)
        if image_path:
            print(f"Streaming vision model for image: {image_path}")
            history.add_user_message(f"[Image Input: {image_path}]\n{user_goal}")
            response = self.call_with_image(prompt_text, image_path)
            response_text = response.content if hasattr(response, "content") else str(response)
            # Manually record the AI message to memory
            history.add_ai_message(response_text)
            yield response_text
        else:
            print("💬 Streaming text-only model")
            partial = ""
            for chunk in self.chat_chain.stream(
                {"user_goal": user_goal},
                config={"configurable": {"session_id": session_id}},
            ):
                # Each chunk from LangChain may be a small delta string
                delta = getattr(chunk, "content", None) or str(chunk)
                partial += delta
                yield delta

            # After streaming completes, record the whole message
            history.add_ai_message(partial)
            # 🧠 Store a textual memory of this image for later turns
            self._update_memory_with_image_context(session_id, image_path, response_text)
    
if __name__ == "__main__":
    agent = ImageAnalystAgent(debug=False)
    while True:
        goal = input("🧠 Describe your analysis goal (or 'exit'): ")
        if goal.lower() in ["exit", "quit"]:
            break
        image = input("🖼️ Enter path to image (or press Enter to skip): ").strip() or None

        response = agent.run(user_goal=goal, image_path=image)
        print(f"\n📋 Workflow Suggestion:\n{response}\n")






   