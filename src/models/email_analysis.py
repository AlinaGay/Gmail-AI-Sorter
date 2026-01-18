from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class EmailAnalysis:
    """Result of email analysing."""
    categories: List[Dict]
    error: Optional[str] = None

    @property
    def success(self) -> bool:
        return self.error is None

    def to_dict(self) -> Dict:
        return {
            'categories':self.categories,
            'error': self.error
        }
