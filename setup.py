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

import setuptools


long_description = ""

with open("README.rst") as fp:
    long_description += fp.read()


setuptools.setup(
    name="picohttpparser",
    version="16.0.dev0",

    description="Python binding to the picohttpparser library",
    long_description=long_description,
    url="https://github.com/dstufft/picohttpparser",

    author="Donald Stufft",
    author_email="donald@stufft.io",

    setup_requires=[
        "cffi>=1.0.0",
    ],
    install_requires=[
        "cffi>=1.0.0",
    ],

    cffi_modules=["src/picohttpparser_build.py:ffi"],

    packages=setuptools.find_packages("src"),
    package_dir={"": "src"},

    ext_package="picohttpparser",

    libraries=[
        ("libpicohttpparser", {
            "sources": [
                "src/libpicohttpparser/picohttpparser.c",
            ]
        }),
    ],

    zip_safe=False,

    classifiers=[
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
    ]
)
