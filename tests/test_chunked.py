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

import pytest

from picohttpparser import (
    ChunkedParser, PartialChunked, InvalidChunk, ChunkedIncomplete,
    parse_chunked,
)


@pytest.mark.parametrize(
    ("chunked", "decoded", "leftover"),
    [
        (b"b\r\nhello world\r\n0\r\n", b"hello world", 0),
        (b"6\r\nhello \r\n5\r\nworld\r\n0\r\n", b"hello world", 0),
        (b"6;comment=hi\r\nhello \r\n5\r\nworld\r\n0\r\n", b"hello world", 0),
        (
            b"6\r\nhello \r\n5\r\nworld\r\n0\r\na: b\r\nc: d\r\n\r\n",
            b"hello world",
            14,
        ),
        (b"b\r\nhello world\r\n0\r\n", b"hello world", 0),
    ],
)
def test_chunked_valid(chunked, decoded, leftover):
    # Single shot parsing
    result = parse_chunked(chunked)
    assert result[0] == decoded
    assert result[1] == leftover

    # Parsed by feeding a single byte per ChunkedParser().feed_data() call
    parser = ChunkedParser()
    result = b""
    for i in range(len(chunked)):
        data = chunked[i:i + 1]
        byte_result, remaining = parser.feed_data(data)
        result += byte_result
        if remaining is not PartialChunked:
            assert remaining == 0
            break
    assert result == decoded


@pytest.mark.parametrize(
    "chunked",
    [
        b"z\r\nabcdefg",
    ],
)
def test_chunked_invalid(chunked):
    # Single shot parsing
    with pytest.raises(InvalidChunk):
        parse_chunked(chunked)

    # Parsed by feeding a single byte per ChunkedParser().feed_data() call
    parser = ChunkedParser()
    with pytest.raises(InvalidChunk):
        for i in range(len(chunked)):
            data = chunked[i:i + 1]
            parser.feed_data(data)


@pytest.mark.parametrize("chunked", [b"b\r\nhello world\r\n"])
def test_chunked_singleshot_incomplete(chunked):
    with pytest.raises(ChunkedIncomplete):
        parse_chunked(chunked)


@pytest.mark.parametrize(
    ("chunked", "expected"),
    [
        (b"b\r\nhello world\r\n", b"hello world"),
    ],
)
def test_chunked_feed_data_incomplete(chunked, expected):
    parser = ChunkedParser()
    result = parser.feed_data(chunked)

    assert result[0] == expected
    assert result[1] is PartialChunked
