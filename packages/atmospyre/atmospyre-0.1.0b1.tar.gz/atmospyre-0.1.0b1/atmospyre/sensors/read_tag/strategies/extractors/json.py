import json
from typing import Dict, Any

from ..extractor import ExtractorStrategy
from ...metadata import ReadTagMetadata


class JSONExtractor(ExtractorStrategy):
    """Extract metadata as JSON format."""

    def __init__(self, indent: int = 2):
        self.indent = indent

    def extract(self, metadata: ReadTagMetadata) -> str:
        """Serialize metadata to JSON.

        Returns:
            JSON string with all metadata fields
        """
        # Convert dataclass to dict, excluding strategy objects
        data = {
            'unit': metadata.unit,
            'source': metadata.source,
            'min_interval': metadata.min_interval,
            'description': metadata.description,
            'precision': metadata.precision,
            'valid_range': metadata.valid_range,
        }

        # Remove None values for cleaner output
        data = {k: v for k, v in data.items() if v is not None}

        return json.dumps(data, indent=self.indent)

    def load(self, data: str) -> Dict[str, Any]:
        """Deserialize metadata from JSON.

        Args:
            data: JSON string

        Returns:
            Dictionary of metadata fields
        """
        return json.loads(data)
