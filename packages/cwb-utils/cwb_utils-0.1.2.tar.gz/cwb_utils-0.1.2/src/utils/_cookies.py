from typing import Any


class _cookies:
    @staticmethod
    def list_dict_to_str(cookies_list_dict: list[dict[str, Any]]) -> str:
        return "; ".join([i["name"] + "=" + i["value"] for i in cookies_list_dict])

    @staticmethod
    def str_to_dict(cookies_str: str) -> dict[str, str]:
        return {i.split("=")[0].strip(): i.split("=")[-1].strip() for i in cookies_str.split(";") if "=" in i}

    @staticmethod
    def dict_to_str(cookies_dict: dict[str, str]) -> str:
        return "; ".join([k + "=" + v for k, v in cookies_dict.items()])


__all__ = [
    "_cookies"
]
