import arrow


class _datetime:
    @staticmethod
    def now(fmt: str = "YYYY-MM-DD HH:mm:ss") -> str:
        return arrow.now().format(fmt)

    @staticmethod
    def delta(start_datetime_str: str, end_datetime_str: str) -> int:
        start_datetime = arrow.get(start_datetime_str).datetime
        end_datetime = arrow.get(end_datetime_str).datetime
        seconds = (end_datetime - start_datetime).total_seconds()
        return int(seconds)


__all__ = [
    "_datetime"
]
