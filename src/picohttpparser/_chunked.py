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

from picohttpparser._picohttpparser import lib, ffi


class InvalidChunk(Exception):
    """
    Raised when the data we've been given isn't a valid chunk for some reason.
    """


# A singleton that is returned as the # of bytes left over when we finished
# parsing a section of data whenever we haven't fully parsed the data.
PartialChunked = type("PartialChunked", (object,), {})()


class ChunkedParser(object):

    def __init__(self, *args, **kwargs):
        super(ChunkedParser, self).__init__(*args, **kwargs)

        self._decoder = ffi.new("struct phr_chunked_decoder *", [0])

    def feed_data(self, data):
        # We need to allocate this ourselves instead of allowing CFFI to do it
        # for us, because picohttpparser will simply set a pointer back to this
        # data and it's possible that the copy that CFFI made will have already
        # been cleaned up if we don't.
        # TODO: This is going to incur a copy to send the data into C land,
        #       it would be great if we could figure out a way to make that
        #       copy not required. I'm not sure how to do that though, will
        #       need some thought put behind it.
        buf_len = ffi.new("size_t *", len(data))
        buf = ffi.new("char[{}]".format(buf_len[0]))
        buf[0:buf_len[0]] = data

        # Actually parse the bytes given to us
        ret = lib.phr_decode_chunked(self._decoder, buf, buf_len)

        # Check to see if we failed parsing the data for any reason, if we have
        # then we'll bail out now and raise an InvalidChunk exception.
        if ret == -1:
            raise InvalidChunk

        # phr_decode_chunked will have modified our buffer in place and set the
        # buf_len to whatever the new end of the buffer is, so we can simply
        # read the buffer up to the length set to by buf_len and that will be
        # all of our decoded data.
        decoded = ffi.buffer(buf)[:buf_len[0]]

        # Now that we've gotten our decoded data, we can simply return the
        # decoded data, as well as the number of bytes left in the given data
        # that were not part of this chunked request. Any trailing headers will
        # be included in the unparsed data, it is up to the caller to parse
        # those. If we're still expecting more data then we'll return a None.
        return decoded, PartialChunked if ret == -2 else ret


class ChunkedIncomplete(ValueError):
    """
    Raised when we've gotten an incomplete chunked body and more data is
    required.

    Note: This is only used by the "one shot" api, parse_chunked
    """


def parse_chunked(data):
    """
    Unlike the ChunkedParser(), this method is one shot and done, it must be
    given the entire body or else it will raise an error, however it can give
    additional data beyond the end of the chunk.
    """
    decoded, left_over = ChunkedParser().feed_data(data)
    if left_over is PartialChunked:
        raise ChunkedIncomplete
    return decoded, left_over
