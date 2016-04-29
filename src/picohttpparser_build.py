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

import os.path

from cffi import FFI


INCLUDE_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "libpicohttpparser",
)


ffi = FFI()
ffi.set_source(
    "_picohttpparser",
    " #include <picohttpparser.h> ",
    include_dirs=[INCLUDE_DIR],
    libraries=["libpicohttpparser"],
)
ffi.cdef("""

    struct phr_header {
        const char *name;
        size_t name_len;
        const char *value;
        size_t value_len;
    };

    int phr_parse_request(
        const char *buf,
        size_t len,
        const char **method,
        size_t *method_len,
        const char **path,
        size_t *path_len,
        int *minor_version,
        struct phr_header *headers,
        size_t *num_headers,
        size_t last_len
    );

    int phr_parse_response(
        const char *_buf,
        size_t len,
        int *minor_version,
        int *status,
        const char **msg,
        size_t *msg_len,
        struct phr_header *headers,
        size_t *num_headers,
        size_t last_len
    );

    int phr_parse_headers(
        const char *buf,
        size_t len,
        struct phr_header *headers,
        size_t *num_headers,
        size_t last_len
    );

    struct phr_chunked_decoder {
        size_t bytes_left_in_chunk;
        char consume_trailer;
        char _hex_count;
        char _state;
    };

    ssize_t phr_decode_chunked(
        struct phr_chunked_decoder *decoder,
        char *buf,
        size_t *bufsz
    );

""")
