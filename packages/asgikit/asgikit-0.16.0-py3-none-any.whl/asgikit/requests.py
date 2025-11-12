import asyncio
import contextlib
from collections.abc import AsyncIterable, Awaitable, Callable
from email.utils import formatdate
import hashlib
import json
import logging
import mimetypes
import os
import re
from http import HTTPMethod, HTTPStatus
from typing import Any, AsyncGenerator
from urllib.parse import parse_qsl

from anyio import to_thread

try:
    from asgikit import forms
except ImportError:
    forms = None

from asgikit._constants import (
    CHARSET,
    CONTENT_LENGTH,
    CONTENT_TYPE,
    DEFAULT_ENCODING,
    IS_CONSUMED,
    REQUEST,
    SCOPE_ASGIKIT,
)
from asgikit.cookies import Cookies
from asgikit.exceptions import (
    AsgiException,
    ClientDisconnectError,
    RequestAlreadyConsumedError,
)
from asgikit.files import async_file_stream
from asgikit.forms import UploadedFile, MultipartNotEnabledError
from asgikit.http_context import HttpContext
from asgikit.multi_value_dict import MultiValueDict
from asgikit.responses import Response

__all__ = ("Request",)

RE_CHARSET = re.compile(r"""charset="?([\w-]+)"?""")

FORM_URLENCODED_CONTENT_TYPE = "application/x-www-urlencoded"
FORM_MULTIPART_CONTENT_TYPE = "multipart/form-data"
FORM_CONTENT_TYPES = (FORM_URLENCODED_CONTENT_TYPE, FORM_MULTIPART_CONTENT_TYPE)

logger = logging.getLogger(__name__)


class Request(HttpContext):
    """Represents the incoming request"""

    def __init__(self, scope, receive, send):
        assert scope["type"] == "http"

        super().__init__(scope, receive, send)

        self.asgi_scope[SCOPE_ASGIKIT][REQUEST].setdefault(IS_CONSUMED, False)
        self.response = Response(scope, receive, send)

    @property
    def method(self) -> HTTPMethod:
        """HTTP method of the request"""

        # pylint: disable=no-value-for-parameter
        return HTTPMethod(self.asgi_scope["method"])

    @property
    def content_type(self) -> str | None:
        """Content type of the request body"""

        if CONTENT_TYPE not in self.asgi_scope[SCOPE_ASGIKIT][REQUEST]:
            if content_type := self.headers.get_first("content-type"):
                content_type = content_type.split(";")[0]
            else:
                content_type = None
            self.asgi_scope[SCOPE_ASGIKIT][REQUEST][CONTENT_TYPE] = content_type
        return self.asgi_scope[SCOPE_ASGIKIT][REQUEST][CONTENT_TYPE]

    @property
    def content_length(self) -> int | None:
        """Content length of the request body"""

        if CONTENT_LENGTH not in self.asgi_scope[SCOPE_ASGIKIT][REQUEST]:
            if content_length := self.headers.get_first("content-length"):
                content_length = int(content_length)
            else:
                content_length = None
            self.asgi_scope[SCOPE_ASGIKIT][REQUEST][CONTENT_LENGTH] = content_length
        return self.asgi_scope[SCOPE_ASGIKIT][REQUEST].get(CONTENT_LENGTH)

    @property
    def charset(self) -> str | None:
        """Charset of the request"""

        if CHARSET not in self.asgi_scope[SCOPE_ASGIKIT][REQUEST]:
            if content_type := self.headers.get_first("content-type"):
                values = RE_CHARSET.findall(content_type)
                charset = values[0] if values else DEFAULT_ENCODING
            else:
                charset = DEFAULT_ENCODING
            self.asgi_scope[SCOPE_ASGIKIT][REQUEST][CHARSET] = charset
        return self.asgi_scope[SCOPE_ASGIKIT][REQUEST][CHARSET]

    @property
    def is_consumed(self) -> bool:
        """Verifies whether the request body is consumed or not"""
        return self.asgi_scope[SCOPE_ASGIKIT][REQUEST][IS_CONSUMED]

    def __set_consumed(self):
        self.asgi_scope[SCOPE_ASGIKIT][REQUEST][IS_CONSUMED] = True

    async def stream(self) -> AsyncIterable[bytes]:
        """Iterate over the bytes of the request body

        :raise RequestBodyAlreadyConsumedError: If the request body is already consumed
        :raise ClientDisconnectError: If the client is disconnected while reading the request body
        """

        if self.is_consumed:
            raise RequestAlreadyConsumedError()

        while True:
            message = await asyncio.wait_for(self.asgi_receive(), 1)

            if message["type"] == "http.request":
                data = message["body"]

                if not message["more_body"]:
                    self.__set_consumed()

                yield data

                if self.is_consumed:
                    break
            elif message["type"] == "http.disconnect":
                raise ClientDisconnectError()
            else:
                raise AsgiException(f"invalid message type: '{message['type']}'")

    async def read_bytes(self) -> bytes:
        """Read the full request body"""

        data = bytearray()

        async for chunk in self.stream():
            data.extend(chunk)

        return bytes(data)

    async def read_text(self, encoding: str = None) -> str:
        """Read the full request body as str"""

        data = await self.read_bytes()
        return data.decode(encoding or self.charset)

    async def read_json(self) -> Any:
        """Read the full request body and parse it as json"""

        if data := await self.read_bytes():
            return json.loads(data)

        return None

    @staticmethod
    def _is_form_multipart(content_type: str) -> bool:
        return content_type.startswith(FORM_MULTIPART_CONTENT_TYPE)

    async def read_form(
        self,
    ) -> MultiValueDict[str | UploadedFile]:
        """Read the full request body and parse it as form encoded"""

        if self._is_form_multipart(self.content_type):
            if not forms:
                raise MultipartNotEnabledError()

            return await forms.process_multipart(
                self.stream(), self.headers.get_first("content-type"), self.charset
            )

        if data := await self.read_text():
            return MultiValueDict(parse_qsl(data, keep_blank_values=True))

        return MultiValueDict()

    # pylint: disable=too-many-arguments
    async def respond_bytes(
        self,
        content: bytes,
        *,
        status=HTTPStatus.OK,
        media_type: str = None,
        headers: dict[str, str] = None,
        cookies: Cookies = None,
    ):
        """Respond with the given content and finish the response"""

        content_length = len(content)

        await self.response.start(
            status,
            media_type=media_type,
            content_length=content_length,
            headers=headers,
            cookies=cookies,
        )
        await self.response.write(content, more_body=False)

    # pylint: disable=too-many-arguments
    async def respond_text(
        self,
        content: str,
        *,
        status=HTTPStatus.OK,
        media_type: str = "text/plain",
        charset: str = DEFAULT_ENCODING,
        headers: dict[str, str] = None,
        cookies: Cookies = None,
    ):
        """Respond with the given content and finish the response"""

        if media_type.startswith("text/") and "charset=" not in media_type:
            media_type += f"; charset={charset}"

        data = content.encode(charset)
        await self.respond_bytes(
            data, status=status, media_type=media_type, headers=headers, cookies=cookies
        )

    # pylint: disable=too-many-arguments
    async def respond_json(
        self,
        content: Any,
        *,
        status=HTTPStatus.OK,
        media_type: str = "application/json",
        charset: str = DEFAULT_ENCODING,
        headers: dict[str, str] = None,
        cookies: Cookies = None,
    ):
        """Respond with the given content serialized as JSON"""

        data = json.dumps(
            content,
            allow_nan=False,
            indent=None,
            ensure_ascii=False,
            separators=(",", ":"),
        )

        await self.respond_text(
            data,
            status=status,
            media_type=media_type,
            charset=charset,
            headers=headers,
            cookies=cookies,
        )

    async def respond_status(
        self,
        status: HTTPStatus = HTTPStatus.NO_CONTENT,
        *,
        header: dict[str, str] = None,
        cookies: Cookies = None,
    ):
        """Respond an empty response with the given status"""

        await self.response.start(status, headers=header, cookies=cookies)
        await self.response.end()

    async def redirect(
        self,
        location: str,
        *,
        permanent: bool = False,
        headers: dict[str, str] = None,
        cookies: Cookies = None,
    ):
        """Respond with a redirect

        :param location: Location to redirect to
        :param permanent: If true, send permanent redirect (HTTP 308),
            otherwise send a temporary redirect (HTTP 307).
        """

        headers = headers or {}

        status = (
            HTTPStatus.TEMPORARY_REDIRECT
            if not permanent
            else HTTPStatus.PERMANENT_REDIRECT
        )

        headers["location"] = location
        await self.respond_status(status, header=headers, cookies=cookies)

    async def redirect_post_get(
        self,
        location: str,
        headers: dict[str, str] = None,
        cookies: Cookies = None,
    ):
        """Response with HTTP status 303

        Used to send a redirect to a GET endpoint after a POST request, known as post/redirect/get
        https://en.wikipedia.org/wiki/Post/Redirect/Get

        :param location: Location to redirect to
        """

        headers = headers or {}
        headers["location"] = location
        await self.respond_status(HTTPStatus.SEE_OTHER, header=headers, cookies=cookies)

    async def __listen_for_disconnect(self):
        while True:
            try:
                message = await self.asgi_receive()
            except Exception:
                logger.exception("error while listening for client disconnect")
                break

            if message["type"] == "http.disconnect":
                break

    # pylint: disable=too-many-arguments
    @contextlib.asynccontextmanager
    async def response_writer(
        self,
        status=HTTPStatus.OK,
        *,
        media_type: str = None,
        content_length: int = None,
        headers: dict[str, str] = None,
        cookies: Cookies = None,
    ) -> AsyncGenerator[Callable[[bytes], Awaitable], None]:
        """Context manager for streaming data to the response

        :raise ClientDisconnectError: If the client disconnects while sending data
        """

        await self.response.start(
            status,
            media_type=media_type,
            content_length=content_length,
            headers=headers,
            cookies=cookies,
        )

        client_disconnect = asyncio.create_task(self.__listen_for_disconnect())

        async def write(data: bytes | str):
            if client_disconnect.done():
                raise ClientDisconnectError()

            if isinstance(data, str):
                data = data.encode(DEFAULT_ENCODING)

            await self.response.write(data, more_body=True)

        try:
            yield write
        finally:
            await self.response.end()
            client_disconnect.cancel()

    # pylint: disable=too-many-arguments
    async def respond_stream(
        self,
        stream: AsyncIterable[bytes],
        *,
        status=HTTPStatus.OK,
        media_type: str = None,
        content_length: int = None,
        headers: dict[str, str] = None,
        cookies: Cookies = None,
    ):
        """Respond with the given stream of data

        :raise ClientDisconnectError: If the client disconnects while sending data
        """

        async with self.response_writer(
            status,
            media_type=media_type,
            content_length=content_length,
            headers=headers,
            cookies=cookies,
        ) as write:
            async for chunk in stream:
                await write(chunk)

    # pylint: disable=too-many-arguments
    async def respond_file(
        self,
        path: str | os.PathLike,
        *,
        status=HTTPStatus.OK,
        media_type: str = None,
        content_length: int = None,
        headers: dict[str, str] = None,
        cookies: Cookies = None,
        stat_result: os.stat_result = None,
    ):
        """Send the given file to the response"""

        headers = headers or {}

        if not media_type:
            media_type, _ = mimetypes.guess_type(path, strict=False)

        headers["content-type"] = media_type

        if not stat_result:
            stat_result = await to_thread.run_sync(os.stat, path)

        if not content_length:
            content_length = stat_result.st_size

        last_modified = formatdate(stat_result.st_mtime, usegmt=True)
        etag_base = str(stat_result.st_mtime) + "-" + str(stat_result.st_size)
        etag = f'"{hashlib.md5(etag_base.encode(), usedforsecurity=False).hexdigest()}"'
        headers["last-modified"] = last_modified
        headers["etag"] = etag

        if "http.response.pathsend" in self.asgi_scope.get("extensions", {}):
            await self.response.start(
                status,
                media_type=media_type,
                content_length=content_length,
                headers=headers,
                cookies=cookies,
            )
            await self.asgi_send(
                {
                    "type": "http.response.pathsend",
                    "path": str(path),
                }
            )
            return

        try:
            async with async_file_stream(path) as stream:
                await self.respond_stream(
                    stream,
                    status=status,
                    media_type=media_type,
                    content_length=content_length,
                    headers=headers,
                    cookies=cookies,
                )
        except ClientDisconnectError:
            pass
