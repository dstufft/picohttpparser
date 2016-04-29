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
