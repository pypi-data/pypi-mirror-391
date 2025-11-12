from ..printer import PrinterStrategy
from ...metadata import ReadTagMetadata

class DefaultPrinterStrategy(PrinterStrategy):
    """Print metadata in human-readable format."""

    def print(self, metadata: ReadTagMetadata) -> str:
        """Format metadata for human reading."""
        lines = []

        if metadata.description:
            lines.append(f"Description: {metadata.description}")

        if metadata.unit:
            lines.append(f"Unit: {metadata.unit}")

        if metadata.precision is not None:
            lines.append(f"Precision: {metadata.precision} decimal places")

        if metadata.valid_range:
            lines.append(f"Valid Range: {metadata.valid_range[0]} to {metadata.valid_range[1]}")

        if metadata.min_interval:
            lines.append(f"Min Interval: {metadata.min_interval} seconds")

        if metadata.source:
            lines.append(f"Source: {metadata.source}")

        return "\n".join(lines)