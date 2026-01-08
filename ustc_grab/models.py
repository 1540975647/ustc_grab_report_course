from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class Report:
    """Represents a report object from search results."""
    id: str  # BGBM
    name: str  # BGTMZW
    time: str  # BGSJ
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Report":
        return cls(
            id=data.get("BGBM", ""),
            name=data.get("BGTMZW", ""),
            time=data.get("BGSJ", "")
        )

@dataclass
class Course:
    """Represents a course object."""
    id: str
    name: str
    # Add other fields as necessary based on observation
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Course":
        return cls(
            id=data.get("id", ""),
            name=data.get("name", "")
        )
