"""
core/router.py
---------------
Hybrid router for multi-agent orchestration.
Decides which agent should handle a query based on:
- Query intent keywords (takes priority)
- Uploaded files (images → ImageAnalystAgent, PDFs → PaperReviewerAgent)
- Optional LLM-based classification
- Default fallback to AIScientistAgent

Routes to:
- PaperReviewerAgent: paper review, critique, literature analysis
- ImageAnalystAgent: image analysis, segmentation workflows
- AIScientistAgent: general scientific Q&A, microscopy concepts
"""

from typing import Dict, Optional
from core.llm_client import get_llm
import re
import time
# import available agents
from agents.AI_scientist_agent import AIScientistAgent
from agents.Image_analyst_agent import ImageAnalystAgent
from agents.paper_reviewer_agent import PaperReviewerAgent
from config.prompts.router_prompt import ROUTER_PROMPT
from core.memory_manager import GLOBAL_MEMORY
from core.analytics import ANALYTICS

class Router:
    """
    Simple intelligent router for the multi-agent system.
    Routes queries to the most appropriate agent.
    """
    def __init__(self, agent_map: Optional[Dict[str, object]] = None, use_llm: bool = True):
        """
        agent_map: dictionary of agent_name → agent_class
        e.g. {"scientist": AIScientistAgent, "reviewer": PaperReviewerAgent}
        """
        self.agent_map = agent_map or {
        "scientist": AIScientistAgent,
        "analyst": ImageAnalystAgent,
        "reviewer": PaperReviewerAgent,
        }
        self.use_llm = use_llm
        self._instances = {}  # cache of active agents
        self.llm = get_llm(temperature=0.3)
    
    def _rule_based_route(self, query: str, image_path: Optional[str] = None, pdf_path: Optional[str] = None) -> str:
        q = query.lower().strip()

        # Priority 1: Check query intent first (keywords take precedence)
        # Paper review keywords → reviewer
        if any(k in q for k in ["paper", "review", "citation", "summarize", "literature", "criticize", "critique", "methodology"]):
            return "reviewer"
        
        # Image analysis keywords or image provided → analyst
        if image_path or any(k in q for k in ["segmentation", "segment", "detection", "threshold", "watershed", "pixel", "mask", "analyze image", "analyze data", "radiomics"]):
            return "analyst"
        
        # Scientific questions → scientist
        elif any(k in q for k in ["microscopy", "imaging", "neuron", "astrocyte", "adaptive optics", "optics"]):
            return "scientist"
        else:
            # Default fallback
            return "scientist"
        

    def _llm_based_route(self, query: str, image_path: Optional[str] = None, pdf_path: Optional[str] = None) -> str:
        """Ask an LLM to classify which agent should handle the task."""
        # Let the LLM decide based on query intent, even if files are uploaded
        routing_prompt = ROUTER_PROMPT.format(query=query)
        try:
            response = self.llm.invoke(routing_prompt)
            label = response.content.strip().lower()
            if label not in self.agent_map:
                label = self._rule_based_route(query, image_path, pdf_path)
            return label
        except Exception:
            return self._rule_based_route(query, image_path, pdf_path)
    
    # ------------------------------------------------------------------
    # Shared logic for getting or creating an agent
    # ------------------------------------------------------------------
    def _get_agent_instance(self, label: str):
        if label not in self._instances:
            self._instances[label] = self.agent_map[label]()
        return self._instances[label]

    # ------------------------------------------------------------------
    # Main dispatch
    # ------------------------------------------------------------------
    def route_query(self, query: str, session_id: str = "default", image_path: Optional[str] = None, pdf_path: Optional[str] = None, use_llm: Optional[bool] = None):
        """
        Handle query routing:
        1. Contextualize query using conversation history
        2. Select appropriate agent
        3. Run the query and store memory
        4. Log analytics for research metrics
        """
        use_llm = self.use_llm if use_llm is None else use_llm
        start_time = time.time()

        # Step 1. Contextualize the query using shared memory
        #rewritten_query = GLOBAL_MEMORY.contextualize(query, session_id)
        #print(f"Rewritten Query:\n{rewritten_query}\n")

        # Step 2. Choose agent
        #label = self._llm_based_route(rewritten_query, image_path, pdf_path) if use_llm else self._rule_based_route(rewritten_query, image_path, pdf_path)
        label = self._llm_based_route(query, image_path, pdf_path) if use_llm else self._rule_based_route(query, image_path, pdf_path)

        agent = self._get_agent_instance(label)

        # Step 3. Add user query to memory
        GLOBAL_MEMORY.add_user_message(session_id, query)

        # Step 4. Execute agent
        if label == "analyst" and image_path:
            response = agent.run(user_goal=query, image_path=image_path, session_id=session_id)
        elif label == "reviewer" and pdf_path:
            response = agent.run(query=query, pdf_path=pdf_path, session_id=session_id)
        else:
            response = agent.run(query, session_id=session_id)

        # Step 5. Store AI response
        GLOBAL_MEMORY.add_ai_message(session_id, response)

        # Step 6. Log analytics
        response_time = time.time() - start_time
        ANALYTICS.log_query(
            query=query,
            agent_used=label,
            session_id=session_id,
            response_time=response_time,
            has_image=bool(image_path),
            has_pdf=bool(pdf_path)
        )

        return response, label


if __name__ == "__main__":
    router = Router()
    while True:
        q = input("🧠 Enter query: ").strip()
        if q.lower() in ["exit", "quit"]:
            break
        img = input("🖼️ Image path (optional): ").strip() or None
        pdf = input("📄 PDF path (optional): ").strip() or None

        try:
            response, label = router.route_query(
                query=q,
                image_path=img,
                pdf_path=pdf,
            )
            print(f"\n➡ Routed to [{label.upper()}]\n")
            print(f"💬 Response:\n{response}\n")
        except Exception as e:
            print(f"⚠️ Error: {e}\n")

