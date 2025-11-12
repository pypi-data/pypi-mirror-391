import asyncio
from http import HTTPStatus

import pytest

from asgikit.cookies import Cookies
from asgikit.exceptions import (
    ResponseAlreadyStartedError,
    ResponseAlreadyEndedError,
    ResponseNotStartedError,
)
from asgikit.requests import Request
from tests.utils.asgi import HttpSendInspector


async def test_respond_plain_text():
    inspector = HttpSendInspector()
    scope = {"type": "http", "headers": []}
    request = Request(scope, None, inspector)

    await request.respond_text("Hello, World!")

    assert inspector.body == "Hello, World!"


async def test_stream():
    async def stream_data():
        yield "Hello, "
        yield "World!"

    inspector = HttpSendInspector()
    scope = {"type": "http", "http_version": "1.1", "headers": []}
    request = Request(scope, None, inspector)
    await request.respond_stream(stream_data())

    assert inspector.body == "Hello, World!"


async def test_stream_context_manager():
    inspector = HttpSendInspector()
    scope = {"type": "http", "http_version": "1.1", "headers": []}
    request = Request(scope, None, inspector)

    async with request.response_writer() as write:
        await write("Hello, ")
        await write("World!")

    assert inspector.body == "Hello, World!"


async def test_respond_file(tmp_path):
    tmp_file = tmp_path / "tmp_file.txt"
    tmp_file.write_text("Hello, World!")

    inspector = HttpSendInspector()
    scope = {"type": "http", "http_version": "1.1", "headers": []}

    async def sleep_receive():
        while True:
            await asyncio.sleep(1000)

    request = Request(scope, sleep_receive, inspector)
    await request.respond_file(tmp_file)

    assert inspector.body == "Hello, World!"


async def test_respond_file_pathsend(tmp_path):
    tmp_file = tmp_path / "tmp_file.txt"
    tmp_file.write_text("Hello, World!")

    scope = {
        "type": "http",
        "http_version": "1.1",
        "headers": [],
        "extensions": {
            "http.response.pathsend": {}
        }
    }

    async def sleep_receive():
        while True:
            await asyncio.sleep(1000)

    result = None
    async def send(event):
        nonlocal result
        result = event

    request = Request(scope, sleep_receive, send)
    await request.respond_file(tmp_file)

    assert result == {
        "type": "http.response.pathsend",
        "path": str(tmp_file),
    }


async def test_respond_status():
    inspector = HttpSendInspector()
    scope = {"type": "http", "headers": []}
    request = Request(scope, None, inspector)
    await request.respond_status(HTTPStatus.IM_A_TEAPOT)

    assert inspector.status == HTTPStatus.IM_A_TEAPOT
    assert inspector.body == ""


async def test_respond_empty():
    inspector = HttpSendInspector()
    scope = {"type": "http", "headers": []}
    request = Request(scope, None, inspector)

    await request.respond_status(HTTPStatus.OK)
    assert inspector.status == HTTPStatus.OK
    assert inspector.body == ""


async def test_respond_plain_text_with_encoding():
    inspector = HttpSendInspector()
    scope = {"type": "http", "headers": []}
    request = Request(scope, None, inspector)
    await request.respond_text("زيت", charset="iso-8859-6")
    assert inspector.raw_body.decode("iso-8859-6") == "زيت"


async def test_respond_temporary_redirect():
    inspector = HttpSendInspector()
    scope = {"type": "http", "headers": []}
    request = Request(scope, None, inspector)
    await request.redirect("/redirect")

    assert inspector.status == HTTPStatus.TEMPORARY_REDIRECT
    assert (b"location", b"/redirect") in inspector.headers


async def test_respond_permanent_redirect():
    inspector = HttpSendInspector()
    scope = {"type": "http", "headers": []}
    request = Request(scope, None, inspector)
    await request.redirect("/redirect", permanent=True)

    assert inspector.status == HTTPStatus.PERMANENT_REDIRECT
    assert (b"location", b"/redirect") in inspector.headers


async def test_respond_post_get_redirect():
    inspector = HttpSendInspector()
    scope = {"type": "http", "headers": []}
    request = Request(scope, None, inspector)
    await request.redirect_post_get("/redirect")

    assert inspector.status == HTTPStatus.SEE_OTHER
    assert (b"location", b"/redirect") in inspector.headers


async def test_respond_header():
    inspector = HttpSendInspector()
    scope = {"type": "http", "headers": []}
    request = Request(scope, None, inspector)
    await request.respond_status(HTTPStatus.OK, header={"name": "value"})

    assert inspector.status == HTTPStatus.OK
    assert (b"name", b"value") in inspector.headers


async def test_respond_cookie():
    inspector = HttpSendInspector()
    scope = {"type": "http", "headers": []}
    request = Request(scope, None, inspector)
    cookies = Cookies()
    cookies.set("name", "value")
    await request.respond_status(HTTPStatus.OK, cookies=cookies)

    assert inspector.status == HTTPStatus.OK
    assert (b"Set-Cookie", b"name=value; HttpOnly; SameSite=lax") in inspector.headers


async def test_call_start_twice_should_fail():
    async def send(_event):
        pass

    request = Request({"type": "http", "headers": []}, None, send)
    await request.response.start(HTTPStatus.OK)

    with pytest.raises(ResponseAlreadyStartedError):
        await request.response.start(HTTPStatus.OK)


async def test_call_start_on_finished_response_should_fail():
    async def send(_event):
        pass

    request = Request({"type": "http", "headers": []}, None, send)
    await request.response.start(HTTPStatus.OK)
    await request.response.end()

    with pytest.raises(ResponseAlreadyEndedError):
        await request.response.start(HTTPStatus.OK)


async def test_call_write_on_without_start_should_fail():
    async def send(_event):
        pass

    request = Request({"type": "http", "headers": []}, None, send)

    with pytest.raises(ResponseNotStartedError):
        await request.response.write(b"")


async def test_call_write_on_finished_response_should_fail():
    async def send(_event):
        pass

    request = Request({"type": "http", "headers": []}, None, send)
    await request.response.start(HTTPStatus.OK)
    await request.response.end()

    with pytest.raises(ResponseAlreadyEndedError):
        await request.response.write(b"")


async def test_call_end_without_start_should_fail():
    async def send(_event):
        pass

    request = Request({"type": "http", "headers": []}, None, send)

    with pytest.raises(ResponseNotStartedError):
        await request.response.end()


async def test_call_end_on_finished_response_should_fail():
    async def send(_event):
        pass

    request = Request({"type": "http", "headers": []}, None, send)
    await request.response.start(HTTPStatus.OK)
    await request.response.end()

    with pytest.raises(ResponseAlreadyEndedError):
        await request.response.end()
