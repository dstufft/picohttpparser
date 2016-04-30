# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import glob
import os.path

import pytest

from picohttpparser import (
    RequestParser, PartialRequest, InvalidRequest, parse_request,
)


def load_requests():
    location = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "requests",
    )

    for filename in glob.glob(os.path.join(location, "*")):
        data = {}
        with open(filename) as fp:
            exec(fp.read(), {}, data)
        yield (data["REQUEST"], data["PARSED"], data["READ"])


@pytest.mark.parametrize(
    ("http_request", "parsed_request", "parsed_data"),
    load_requests(),
)
def test_request_valid(http_request, parsed_request, parsed_data):
    parsed = parse_request(http_request)
    assert parsed[0] == parsed_request
    assert parsed[1] == parsed_data


@pytest.mark.parametrize(
    "http_request",
    [
        b"GET / HTTP/1.0\r\n\r",
        b"GET",
        b"GET ",
        b"GET /",
        b"GET / ",
        b"GET / H",
        b"GET / HTTP/1.",
        b"GET / HTTP/1.0",
        b"GET / HTTP/1.0\r",
    ]
)
def test_request_partial(http_request):
    with pytest.raises(PartialRequest):
        parse_request(http_request)


@pytest.mark.parametrize(
    "http_request",
    [
        b"GET / HTTP/1.0\r\n:a\r\n\r\n",   # Empty header name
        b"GET / HTTP/1.0\r\n :a\r\n\r\n",  # Space only header name
        b"G\tT / HTTP/1.0\r\n\r\n",        # Tab in method
    ],
)
def test_request_invalid(http_request):
    with pytest.raises(InvalidRequest):
        parse_request(http_request)


def test_slowloris():
    parser = RequestParser()

    with pytest.raises(PartialRequest):
        parser.parse(b"GET /hoge HTTP/1.0\r\n\r")
    parsed, read = parser.parse(b"GET /hoge HTTP/1.0\r\n\r\n")

    assert parsed == (b"GET", b"/hoge", (1, 0), [])
    assert read == 22
