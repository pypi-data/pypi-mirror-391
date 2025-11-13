from typing import Any

import sqlparse


class _sql:
    @staticmethod
    def format(sql: str, **kwargs: Any) -> str:
        if not kwargs:
            kwargs = dict(
                reindent=True,
                keyword_case="upper",
                identifier_case="lower",
                strip_comments=True
            )
        sql = sqlparse.format(sql, **kwargs)
        return sql


__all__ = [
    "_sql"
]
