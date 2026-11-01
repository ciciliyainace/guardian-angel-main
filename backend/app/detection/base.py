from abc import ABC, abstractmethod
from typing import Dict, Any, List


class BaseDetector(ABC):
    @abstractmethod
    def evaluate(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate an event or flow.
        Returns detection result dictionary containing:
        is_attack (bool), category (str), confidence (float), severity (str), evidence (dict).
        """
        pass
