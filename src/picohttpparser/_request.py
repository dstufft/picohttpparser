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

import collections

from picohttpparser._picohttpparser import lib, ffi


Request = collections.namedtuple(
    "Request",
    ["method", "path", "http_version", "headers"],
)


Header = collections.namedtuple("Header", ["name", "value"])


class InvalidRequest(ValueError):
    """
    Raised when the request we've gotten is invalid in some way.
    """


class PartialRequest(Exception):
    """
    Raised when we've gotten a partial request and more data is required.
    """


class RequestParser(object):

    MAX_HEADERS = 100

    def __init__(self, *args, **kwargs):
        super(RequestParser, self).__init__(*args, **kwargs)

        self._method = ffi.new("const char **")
        self._method_len = ffi.new("size_t *")
        self._path = ffi.new("const char **")
        self._path_len = ffi.new("size_t *")
        self._minor_version = ffi.new("int *")
        self._headers = ffi.new(
            "struct phr_header[{}]".format(self.MAX_HEADERS)
        )
        self._num_headers = ffi.new(
            "size_t *",
            ffi.sizeof(self._headers) // ffi.sizeof(self._headers[0])
        )
        self._data_read = 0

    def parse(self, data):
        # TODO: Figure out how to support zero_buffer.

        # We need to allocate this ourselves instead of allowing CFFI to do it
        # for us, because picohttpparser will simply set a pointer back to this
        # data and it's possible that the copy that CFFI made will have already
        # been cleaned up if we don't.
        buf = ffi.new("const char[]", data)
        buf_len = len(data)

        ret = lib.phr_parse_request(
            buf,
            buf_len,
            self._method,
            self._method_len,
            self._path,
            self._path_len,
            self._minor_version,
            self._headers,
            self._num_headers,
            self._data_read,
        )

        # Do some basic error handling, ensuring that we've successfully parsed
        # the request, raising if we've gotten an invalid request, or if we
        # need more data.
        if ret == -1:
            raise InvalidRequest
        elif ret == -2:
            # If we've gotten a partial request, then we'll record how much
            # data we've actually read so that we can read starting from the
            # last length next time.
            self._data_read = buf_len

            # Raise a PartialRequest to let the caller know that we need more
            # data before we can parse this request.
            raise PartialRequest

        # At this point, the only value that *should* be coming in the return
        # value from phr_parse_request is an integer >= 0 telling us how many
        # bytes it has read from the data.
        assert ret >= 0

        # If we've gotten here, then we can reset the amount of data that we've
        # read back to 0, because we're done parsing the current request.
        self._data_read = 0

        # Turn all of our data that we got from parsing the request into our
        # little Request object, which is really just a small named tuple that
        # provides some nicer ways to access the data.
        req = Request(
            method=bytes(ffi.buffer(self._method[0], self._method_len[0])),
            path=bytes(ffi.buffer(self._path[0], self._path_len[0])),
            http_version=(1, self._minor_version[0]),
            headers=[
                Header(
                    name=bytes(ffi.buffer(h.name, h.name_len)),
                    value=bytes(ffi.buffer(h.value, h.value_len)),
                )
                for h in ffi.unpack(self._headers, self._num_headers[0])
            ]
        )

        # Now that we've gotten all of the data we need, we'll go ahead and
        # return our Request object, as well as the number of bytes we've read
        # from the passed in data.
        return req, ret


def parse_request(data):
    return RequestParser().parse(data)
