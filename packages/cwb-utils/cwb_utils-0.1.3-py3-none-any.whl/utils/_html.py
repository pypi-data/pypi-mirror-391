import html
from typing import Any

from htmlmin import minify


class _html:
    @staticmethod
    def compress(*args: Any, **kwargs: Any) -> str:
        return minify(*args, **kwargs)

    @staticmethod
    def escape(text: str) -> str:
        """
        >>> _html.escape("<")
        '&lt;'

        Args:
            text:

        Returns:

        """
        return html.escape(text)

    @staticmethod
    def unescape(text: str) -> str:
        """
        >>> _html.unescape("&lt;")
        '<'

        Args:
            text:

        Returns:

        """
        return html.unescape(text)


__all__ = [
    "_html"
]
