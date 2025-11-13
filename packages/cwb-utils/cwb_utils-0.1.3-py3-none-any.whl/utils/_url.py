import hashlib
import os
import re
import sys
from typing import Any, Final
from urllib import parse

import httpx
import tldextract
from furl import furl
from tqdm import tqdm
from typing_extensions import Literal
from w3lib.url import canonicalize_url

from utils._headers import _headers


# noinspection PyShadowingNames
class _url:
    @staticmethod
    def get_furl_obj(url: str) -> furl:
        return furl(url)

    @staticmethod
    def get_parse_result(url: str) -> parse.ParseResult:
        parse_result = parse.urlparse(url)
        return parse_result

    @staticmethod
    def get_origin_path(url: str) -> str:
        """
        >>> _url.get_origin_path("https://github.com/search?q=owner%3Amathewgeola+cwb-utils&type=repositories")
        'https://github.com/search'

        Args:
            url:

        Returns:

        """
        furl_obj = _url.get_furl_obj(url)
        origin_path = str(furl_obj.origin) + str(furl_obj.path)
        return origin_path

    @staticmethod
    def is_valid(url: str) -> bool:
        """
        >>> _url.is_valid("https://www.baidu.com/")
        True

        Args:
            url:

        Returns:

        """
        try:
            parse_result = _url.get_parse_result(url)
            scheme, netloc = parse_result.scheme, parse_result.netloc
            if not scheme:
                return False
            if not netloc:
                return False
            if scheme not in ("http", "https"):
                return False
            return True
        except ValueError:
            return False

    @staticmethod
    def quote(
            url: str,
            safe: str | None = None,
            encoding: str = "utf-8",
            quote_type: Literal["encodeURI", "encodeURIComponent", "browser"] | None = "browser"
    ) -> str:
        """
        >>> _url.quote("https://www.baidu.com/s?wd=你好")
        'https://www.baidu.com/s?wd=%E4%BD%A0%E5%A5%BD'

        Args:
            url:
            safe:
            encoding:
            quote_type:

        Returns:

        """
        if quote_type == "encodeURI":
            safe = ";/?:@&=+$,-_.!~*'()#"
        elif quote_type == "encodeURIComponent":
            safe = "-_.~"
        elif quote_type == "browser":
            safe = ";/?:@&=+$,-_.!~*'()"
            parsed = parse.urlparse(url)
            path = parse.quote(parsed.path, safe=safe)
            query_pairs = parse.parse_qsl(parsed.query, keep_blank_values=True)
            encoded_query = "&".join(
                f"{k}={parse.quote(v, safe='-_.~', encoding=encoding)}"
                for k, v in query_pairs
            )
            fragment = parse.quote(parsed.fragment, safe='-_.~', encoding=encoding)
            return parse.urlunparse((
                parsed.scheme,
                parsed.netloc,
                path,
                parsed.params,
                encoded_query,
                fragment
            ))
        else:
            if safe is None:
                safe = "/"

        return parse.quote(url, safe=safe, encoding=encoding)

    @staticmethod
    def unquote(url: str, encoding: str = "utf-8") -> str:
        """
        >>> _url.unquote("https://www.baidu.com/s?wd=%E4%BD%A0%E5%A5%BD")
        'https://www.baidu.com/s?wd=你好'

        Args:
            url:
            encoding:

        Returns:

        """
        return parse.unquote(url, encoding=encoding)

    @staticmethod
    def encode(params: dict[str, Any]) -> str:
        """
        >>> _url.encode({"a": "1", "b": "2"})
        'a=1&b=2'

        Args:
            params:

        Returns:

        """
        return parse.urlencode(params)

    @staticmethod
    def decode(url: str) -> dict[str, str]:
        """
        >>> _url.decode("xxx?a=1&b=2")
        {'a': '1', 'b': '2'}

        Args:
            url:

        Returns:

        """
        params = dict()

        lst = url.split("?", maxsplit=1)[-1].split("&")
        for i in lst:
            key, value = i.split("=", maxsplit=1)
            params[key] = _url.unquote(value)

        return params

    @staticmethod
    def join_url(base_url: str, url: str) -> str:
        """
        >>> _url.join_url("https://www.baidu.com/", "/s?ie=UTF-8&wd=cwb-utils")
        'https://www.baidu.com/s?ie=UTF-8&wd=cwb-utils'

        Args:
            base_url:
            url:

        Returns:

        """
        return parse.urljoin(base_url, url)

    @staticmethod
    def join_params(url: str, params: dict[str, Any]) -> str:
        """
        >>> _url.join_params("https://www.baidu.com/s", {"wd": "你好"})
        'https://www.baidu.com/s?wd=%E4%BD%A0%E5%A5%BD'

        Args:
            url:
            params:

        Returns:

        """
        if not params:
            return url

        params = _url.encode(params)
        separator = "?" if "?" not in url else "&"
        return url + separator + params

    @staticmethod
    def get_params(url: str) -> dict[str, str]:
        """
        >>> _url.get_params("https://www.baidu.com/s?wd=cwb-utils")
        {'wd': 'cwb-utils'}

        Args:
            url:

        Returns:

        """
        furl_obj = _url.get_furl_obj(url)
        params = dict(furl_obj.query.params)
        return params

    @staticmethod
    def get_param(url: str, key: str, default: Any | None = None) -> Any:
        """
        >>> _url.get_param("https://www.baidu.com/s?wd=cwb-utils", "wd")
        'cwb-utils'

        Args:
            url:
            key:
            default:

        Returns:

        """
        params = _url.get_params(url)
        param = params.get(key, default)
        return param

    @staticmethod
    def get_url_params(url: str) -> tuple[str, dict[str, str]]:
        """
        >>> _url.get_url_params("https://www.baidu.com/s?wd=cwb-utils")
        ('https://www.baidu.com/s', {'wd': 'cwb-utils'})

        Args:
            url:

        Returns:

        """
        root_url = ""
        params = dict()

        if "?" in url:
            root_url = url.split("?", maxsplit=1)[0]
            params = _url.get_params(url)
        else:
            if re.search("[&=]", url) and not re.search("/", url):
                params = _url.get_params(url)
            else:
                root_url = url

        return root_url, params

    @staticmethod
    def get_domain(url: str) -> str:
        """
        >>> _url.get_domain("https://image.baidu.com/search/index?word=cwb-utils")
        'baidu'

        Args:
            url:

        Returns:

        """
        er = tldextract.extract(url)
        domain = er.domain
        return domain

    @staticmethod
    def get_subdomain(url: str) -> str:
        """
        >>> _url.get_subdomain("https://image.baidu.com/search/index?word=cwb-utils")
        'image'

        Args:
            url:

        Returns:

        """
        er = tldextract.extract(url)
        subdomain = er.subdomain
        return subdomain

    @staticmethod
    def canonicalize(url: str) -> str:
        """
        >>> _url.canonicalize("https://www.baidu.com/s?wd=cwb-utils")
        'https://www.baidu.com/s?wd=cwb-utils'

        Args:
            url:

        Returns:

        """
        return canonicalize_url(url)

    @staticmethod
    def _get_file_path(
            url: str,
            headers: dict[str, str] | None = None,
            file_path: str | None = None,
            dir_path: str | None = None,
            file_name: str | None = None,
            file_prefix: str | None = None,
            file_suffix: str | None = None
    ) -> str:
        """

        Args:
            url:
            headers: response.headers
            file_path:
            dir_path:
            file_name: file_prefix + file_suffix
            file_prefix:
            file_suffix:

        Returns:

        """
        # todo：Add more content_type.
        content_type_to_file_suffix: Final[dict[str, str]] = {
            "image/png": "png",
            "image/gif": "gif",
            "text/html;charset=utf-8": "html",
            "text/javascript; charset=utf-8": "js",
            "application/json; charset=utf-8": "json",
            "image/jpeg;charset=UTF-8": "jpeg",
        }

        if file_path is None:
            if dir_path is None:
                dir_path = os.path.dirname(os.path.abspath(sys.argv[0]))
            if file_name is None:
                if not (file_prefix is not None and file_suffix is not None):
                    _file_name: str | None = None

                    if _file_name is None:
                        if (content_disposition := headers.get("content-disposition")) is not None:
                            m = re.match(r'attachment;fileName="(.*?)"', content_disposition)
                            if m:
                                _file_name = m.group(1)
                                _file_name = _file_name.replace("/", "_")

                    if _file_name is None:
                        _file_prefix, _file_suffix = os.path.splitext(_url.get_furl_obj(url).path.segments[-1])
                        if not _file_suffix:
                            if (content_type := headers.get("content-type")) is not None:
                                _file_ext = content_type_to_file_suffix[content_type]
                                _file_suffix = os.path.extsep + _file_ext
                                _file_name = _file_prefix + _file_suffix
                        else:
                            _file_name = _file_prefix + _file_suffix

                    if _file_name is None:
                        _file_name = hashlib.sha256(url.encode()).hexdigest() + os.path.extsep + "bin"

                    if file_prefix is None:
                        file_prefix = os.path.splitext(_file_name)[0]

                    if file_suffix is None:
                        file_suffix = os.path.splitext(_file_name)[-1]

                file_name = file_prefix + file_suffix
            else:
                dir_path = os.path.abspath(dir_path)
            file_path = os.path.join(dir_path, file_name)
        else:
            file_path = os.path.abspath(file_path)

        dir_path = os.path.dirname(file_path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        return file_path

    @staticmethod
    def to_file_path(
            url: str,
            headers: dict[str, str] | None = None,
            file_path: str | None = None,
            dir_path: str | None = None,
            file_name: str | None = None,
            file_prefix: str | None = None,
            file_suffix: str | None = None,
            use_cache: bool = True,
            chunk_size: int = 64 * 1024,
            use_tqdm: bool = False
    ) -> str | None:
        if not _url.is_valid(url):
            return None

        if headers is None:
            headers = _headers.get_default()

        try:
            with httpx.Client(timeout=None, follow_redirects=True) as client:
                with client.stream("GET", url, headers=headers) as response:
                    response.raise_for_status()

                    file_path = _url._get_file_path(
                        url, response.headers,
                        file_path,
                        dir_path, file_name,
                        file_prefix, file_suffix
                    )

                    if use_cache:
                        if os.path.exists(file_path):
                            return file_path

                    total = int(response.headers.get("content-length", 0))
                    progress: tqdm | None = None

                    if use_tqdm:
                        progress = tqdm(
                            total=total,
                            unit="B",
                            unit_scale=True,
                            unit_divisor=1024,
                            desc=file_path.split("/")[-1],
                            bar_format="{l_bar}{bar} | {n_fmt}/{total_fmt} | {rate_fmt} | ETA {remaining}",
                        )

                    with open(file_path, "wb") as file:
                        for chunk in response.iter_bytes(chunk_size=chunk_size):
                            file.write(chunk)
                            if progress is not None:
                                progress.update(len(chunk))

                    if progress is not None:
                        progress.close()
        except Exception as e:  # noqa
            file_path = None

        return file_path


__all__ = [
    "_url"
]
