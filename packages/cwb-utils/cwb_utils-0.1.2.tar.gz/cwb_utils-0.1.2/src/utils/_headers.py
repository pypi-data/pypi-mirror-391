from http.cookies import SimpleCookie
from typing import Any

import httpx
import requests.structures
import scrapy
from fake_useragent import UserAgent

from utils._cookies import _cookies


# noinspection PyShadowingNames
class _headers:
    @staticmethod
    def get_default(**kwargs: Any) -> dict[str, str]:
        if not kwargs:
            kwargs = dict(platforms=["desktop"])
        user_agent = UserAgent(**kwargs)

        headers = {
            "User-Agent": user_agent.random
        }
        return headers

    @staticmethod
    def get_updated(
            headers: dict[str, str] | None = None,
            default_headers: dict[str, str] | None = None
    ) -> dict[str, str]:
        """
        >>> _headers.get_updated({"a": "1"}, {"a": "2", "b": "1", "c": "3"})
        {'a': '1', 'b': '1', 'c': '3'}

        Args:
            headers:
            default_headers:

        Returns:

        """
        if headers is None:
            headers = {}
        if default_headers is None:
            default_headers = _headers.get_default()

        for k, v in default_headers.items():
            if k not in headers:
                headers[k] = v

        return headers

    @staticmethod
    def response_headers_to_cookies_dict(
            response_headers: scrapy.http.headers.Headers | requests.structures.CaseInsensitiveDict | httpx.Headers
    ) -> dict[str, str] | None:
        if isinstance(response_headers, scrapy.http.headers.Headers):
            cookies = {}
            for header in response_headers.getlist("Set-Cookie"):
                simple_cookie = SimpleCookie()
                simple_cookie.load(header.decode())
                for key, morsel in simple_cookie.items():
                    cookies[key] = morsel.value
        elif isinstance(response_headers, requests.structures.CaseInsensitiveDict):
            cookies = _cookies.str_to_dict(response_headers.get("Set-Cookie"))
        elif isinstance(response_headers, httpx.Headers):
            cookies = _cookies.str_to_dict(response_headers.get("Set-Cookie"))
        else:
            cookies = None
        return cookies


__all__ = [
    "_headers"
]
