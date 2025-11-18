from abc import ABC, abstractmethod

class BaseAgent(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def run(self, query: str):
        pass