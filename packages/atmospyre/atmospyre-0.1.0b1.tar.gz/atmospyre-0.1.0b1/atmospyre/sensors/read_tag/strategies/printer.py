from abc import ABC, abstractmethod
from typing import Any

from ..metadata import ReadTagMetadata

class PrinterStrategy(ABC):
    """Strategy for formatting/printing values to different formats."""

    @abstractmethod
    def print(self, metadata: ReadTagMetadata) -> str:
        """Format value for display.

        Args:
            value: Raw value to format
            metadata: Metadata containing unit, precision, etc.

        Returns:
            Formatted string
        """
        pass
