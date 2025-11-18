"""
core/rag_pipeline.py
--------------------
Unified RAG pipeline that can work with any agent class.

Usage:
    rag = RAGPipeline(agent_cls=AIScientistAgent)
    rag.run("Explain adaptive optics in microscopy")

You can easily plug in new agents like:
    rag = RAGPipeline(agent_cls=PaperReviewerAgent)
"""

from agents.AI_scientist_agent import AIScientistAgent
from typing import Type

class RAGPipeline:
    def __init__(self, agent_cls: Type, **agent_kwargs):
        """
        Initialize RAG pipeline with a specific agent class.

        Parameters
        ----------
        agent_cls : class
            The agent class to instantiate (e.g., AIScientistAgent)
        agent_kwargs : dict
            Optional keyword arguments passed to the agent.
        """
        self.agent = agent_cls(**agent_kwargs)

    def run(self, query: str):
        """Execute RAG pipeline and return result."""
        print(f"\n[{self.agent.__class__.__name__}] Processing query: {query}\n")
        return self.agent.run(query)



if __name__ == "__main__":
    rag = RAGPipeline(AIScientistAgent)
    while True:
        query = input("🧠 Enter your scientific question (or 'exit'): ")
        if query.lower() in ["exit", "quit"]:
            break
        response = rag.run(query)
        print(f"\n🧩 Answer:\n{response}\n")
