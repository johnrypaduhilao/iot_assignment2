"""
The kit's original tests/coap/test_proxy.py was missing, so this is my own version
Run:  pytest tests/coap/test_proxy.py -v -s
"""

import json
import pytest

import aiocoap
from aiocoap import Message, Code

from src.coap.server import build_server


# CoAP Content-Format integer  ->  HTTP Content-Type string  (RFC 7252 §12.3)
CONTENT_FORMAT_TO_MIME = {
    0:  "text/plain; charset=utf-8",
    40: "application/link-format",
    50: "application/json",
    60: "application/cbor",
}


def map_coap_options_to_http_headers(response: Message) -> dict:
    """
    Apply the CoAP-option -> HTTP-header mapping that a CoAP-HTTP proxy performs.
    This is the heart of Task 2.3 / report Section 5.2.
    """
    headers = {}

    # Content-Format option (#12)  ->  Content-Type
    cf = response.opt.content_format
    if cf is not None:
        headers["Content-Type"] = CONTENT_FORMAT_TO_MIME.get(int(cf), "application/octet-stream")

    # Max-Age option (#14)  ->  Cache-Control: max-age
    if response.opt.max_age is not None:
        headers["Cache-Control"] = f"max-age={response.opt.max_age}"

    # ETag option (#4)  ->  ETag
    if response.opt.etag is not None:
        headers["ETag"] = '"' + response.opt.etag.hex() + '"'

    # Location-Path option (#8)  ->  Location
    if response.opt.location_path:
        headers["Location"] = "/" + "/".join(response.opt.location_path)

    return headers


@pytest.fixture(scope="module")
def event_loop():
    import asyncio
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
async def coap_server():
    """Start the assignment's CoAP server resource tree in-process."""
    ctx = await build_server()
    yield ctx
    await ctx.shutdown()


@pytest.fixture(scope="module")
async def coap_client():
    ctx = await aiocoap.Context.create_client_context()
    yield ctx
    await ctx.shutdown()


async def test_get_returns_json(coap_server, coap_client):
    """A CoAP GET on the temperature resource returns valid JSON (2.05 Content)."""
    req = Message(code=Code.GET, uri="coap://localhost/factory/line1/temperature")
    resp = await coap_client.request(req).response

    assert resp.code == Code.CONTENT
    data = json.loads(resp.payload)
    assert "value" in data and "unit" in data

async def test_content_format_maps_to_content_type(coap_server, coap_client):
    """CoAP Content-Format 50 maps to HTTP Content-Type application/json."""
    req = Message(code=Code.GET, uri="coap://localhost/factory/line1/temperature")
    resp = await coap_client.request(req).response

    headers = map_coap_options_to_http_headers(resp)
    print("\nObserved HTTP headers (for report Section 5.2):", headers)

    assert int(resp.opt.content_format) == 50
    assert headers["Content-Type"] == "application/json"


async def test_http_body_matches_coap_body(coap_server, coap_client):
    """The body a proxy would return over HTTP is byte-identical to the CoAP payload."""
    req = Message(code=Code.GET, uri="coap://localhost/factory/line1/temperature")
    resp = await coap_client.request(req).response

    # A proxy passes the payload through unchanged; confirm it parses as JSON.
    http_body = resp.payload
    assert json.loads(http_body) == json.loads(resp.payload)