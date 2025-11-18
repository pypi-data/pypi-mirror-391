class BaseAnalyzer:
    """Base class for content analyzers"""

    def analyze(self, content: str, mode: str = "assessment") -> dict:
        """Analyze content

        Args:
            content: The content to analyze
            mode: Analysis mode ('research' or 'assessment')

        Returns:
            dict with analysis results
        """
        raise NotImplementedError
