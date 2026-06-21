import re


class ClauseProcessor:
    """Split feedback text into clauses for independent analysis."""

    _CONNECTORS = r"but|however|although|while|yet|though"
    _LEADING_CONNECTOR = re.compile(
        rf"^\s*(?:{_CONNECTORS})\b\s*",
        flags=re.IGNORECASE
    )
    _BOUNDARY = re.compile(
        rf"\s*(?:[;]+|(?<=[.!?])\s+|,?\s*\b(?:{_CONNECTORS})\b\s*,?)\s*",
        flags=re.IGNORECASE
    )

    def split_clauses(self, text: str) -> list[str]:
        """Return non-empty clauses split at contrast and sentence boundaries."""
        if not text or not text.strip():
            return []

        normalized_text = self._LEADING_CONNECTOR.sub("", text.strip())

        # A leading subordinate clause commonly ends at the first comma.
        if normalized_text != text.strip() and "," in normalized_text:
            first_clause, remainder = normalized_text.split(",", maxsplit=1)
            normalized_text = f"{first_clause};{remainder}"

        return [
            clause.strip()
            for clause in self._BOUNDARY.split(normalized_text)
            if clause.strip()
        ]
