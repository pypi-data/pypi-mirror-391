from http import HTTPStatus
from logging import getLogger

from asgikit._constants import (
    IS_FINISHED,
    IS_STARTED,
    RESPONSE,
    SCOPE_ASGIKIT,
    STATUS,
)

from asgikit.cookies import Cookies
from asgikit.exceptions import (
    ResponseAlreadyEndedError,
    ResponseAlreadyStartedError,
    ResponseNotStartedError,
)
from asgikit.headers import encode_headers

__all__ = ("Response",)

logger = getLogger(__name__)


class Response:
    """Response object used to interact with the client"""

    __slots__ = ("_scope", "_receive", "_send")

    def __init__(self, scope, receive, send):
        scope.setdefault(SCOPE_ASGIKIT, {})
        scope[SCOPE_ASGIKIT].setdefault(RESPONSE, {})
        scope[SCOPE_ASGIKIT][RESPONSE].setdefault(IS_STARTED, False)
        scope[SCOPE_ASGIKIT][RESPONSE].setdefault(IS_FINISHED, False)

        self._scope = scope
        self._receive = receive
        self._send = send

    @property
    def is_started(self) -> bool:
        """Tells whether the response is started or not"""

        return self._scope[SCOPE_ASGIKIT][RESPONSE][IS_STARTED]

    def __set_started(self):
        self._scope[SCOPE_ASGIKIT][RESPONSE][IS_STARTED] = True

    @property
    def is_finished(self) -> bool:
        """Tells whether the response is started or not"""

        return self._scope[SCOPE_ASGIKIT][RESPONSE][IS_FINISHED]

    def __set_finished(self):
        self._scope[SCOPE_ASGIKIT][RESPONSE][IS_FINISHED] = True

    @staticmethod
    def _encode_headers(
        status: HTTPStatus,
        media_type: str | None,
        content_length: int | None,
        headers: dict[str, str],
        cookies: Cookies | None,
    ) -> list[tuple[bytes, bytes]]:
        headers = headers or {}

        if media_type:
            headers["content-type"] = media_type

        if (
            content_length is not None
            and not (
                status < HTTPStatus.OK
                or status in (HTTPStatus.NO_CONTENT, HTTPStatus.NOT_MODIFIED)
            )
            and "content-length" not in headers
        ):
            headers["content-length"] = str(content_length)

        encoded_headers = encode_headers(headers)

        if cookies:
            encoded_headers.extend(cookies.encode())

        return encoded_headers

    # pylint: disable=too-many-arguments
    async def start(
        self,
        status: HTTPStatus,
        *,
        media_type: str = None,
        content_length: int = None,
        headers: dict[str, str] = None,
        cookies: Cookies = None,
    ):
        """Start the response

        Must be called before calling ``write()`` or ``end()``

        :raise ResponseAlreadyStartedError: If the response is already started
        :raise ResponseAlreadyEndedError: If the response is finished
        """

        if self.is_finished:
            raise ResponseAlreadyEndedError()

        if self.is_started:
            raise ResponseAlreadyStartedError()

        self.__set_started()

        encoded_headers = self._encode_headers(
            status, media_type, content_length, headers, cookies
        )

        self._scope[SCOPE_ASGIKIT][RESPONSE][STATUS] = status

        await self._send(
            {
                "type": "http.response.start",
                "status": status,
                "headers": encoded_headers,
            }
        )

    async def write(self, body: bytes | str, *, more_body=False):
        """Write data to the response

        :raise ResponseNotStartedError: If the response is not started
        """

        assert isinstance(body, bytes)

        if self.is_finished:
            raise ResponseAlreadyEndedError()

        if not self.is_started:
            raise ResponseNotStartedError()

        await self._send(
            {
                "type": "http.response.body",
                "body": body,
                "more_body": more_body,
            }
        )

        if not more_body:
            self.__set_finished()

    async def end(self):
        """Finish the response

        Must be called when no more data will be written to the response

        :raise ResponseNotStartedError: If the response is not started
        :raise ResponseAlreadyEndedError: If the response is already finished
        """

        if self.is_finished:
            raise ResponseAlreadyEndedError

        if not self.is_started:
            raise ResponseNotStartedError()

        await self.write(b"", more_body=False)
