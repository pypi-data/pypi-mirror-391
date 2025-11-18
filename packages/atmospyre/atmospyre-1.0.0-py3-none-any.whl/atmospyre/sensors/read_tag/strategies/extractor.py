from abc import ABC, abstractmethod
from typing import Any, Dict

from ..metadata import ReadTagMetadata


class ExtractorStrategy(ABC):
    """Strategy for extracting/serializing metadata to different formats.

    Extracts ALL metadata fields and converts to format (JSON, XML, YAML, etc).
    """

    @abstractmethod
    def extract(self, metadata: ReadTagMetadata) -> str:
        """Serialize metadata to string format.

        Args:
            metadata: TagMetadata object to serialize

        Returns:
            Serialized string (JSON, XML, YAML, etc.)
        """
        pass

    @abstractmethod
    def load(self, data: str) -> Dict[str, Any]:
        """Deserialize metadata from string format.

        Args:
            data: Serialized metadata string

        Returns:
            Dictionary of metadata fields
        """
        pass
