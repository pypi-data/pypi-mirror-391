import re


class _string:
    @staticmethod
    def camel_to_snake(string: str) -> str:
        """
        >>> _string.camel_to_snake('CamelCaseString')
        'camel_case_string'

        Args:
            string:

        Returns:

        """
        string = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", string)
        string = re.sub("([a-z0-9])([A-Z])", r"\1_\2", string).lower()
        return string

    @staticmethod
    def snake_to_camel(string: str) -> str:
        """
        >>> _string.snake_to_camel('snake_case_string')
        'SnakeCaseString'

        Args:
            string:

        Returns:

        """
        return "".join(i.capitalize() for i in string.split("_"))


__all__ = [
    "_string"
]
