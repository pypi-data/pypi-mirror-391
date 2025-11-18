from pathlib import Path


class BaseLens:
    """Base class for content extraction lenses"""

    def extract(self, file_path: Path) -> dict:
        """Extract content from file

        Returns:
            dict with keys: success, data, error
        """
        raise NotImplementedError
