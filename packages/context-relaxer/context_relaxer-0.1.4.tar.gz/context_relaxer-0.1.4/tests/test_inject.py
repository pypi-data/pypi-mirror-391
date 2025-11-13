import ssl
import sys
from http.client import HTTPSConnection

import pytest
from aiohttp.connector import _make_ssl_context
from urllib3.util import ssl_ as urllib3_ssl

import context_relaxer


@pytest.fixture(scope="function")
def inject_relaxer():
    context_relaxer.inject_into_ssl()
    try:
        yield
    finally:
        context_relaxer.extract_from_ssl()


def test_inject_and_extract():
    assert ssl.create_default_context is not context_relaxer._api.patched_create_default_context
    try:
        original_create_default_context = ssl.create_default_context

        context_relaxer.inject_into_ssl()
        assert ssl.create_default_context is context_relaxer._api.patched_create_default_context

        ctx = ssl.create_default_context()
        assert ctx.verify_flags & ssl.VERIFY_X509_STRICT == 0

        context_relaxer.extract_from_ssl()
        assert ssl.create_default_context is original_create_default_context

        ctx = ssl.create_default_context()
        if sys.version_info >= (3, 13):
            assert ctx.verify_flags & ssl.VERIFY_X509_STRICT == ssl.VERIFY_X509_STRICT
        else:
            assert ctx.verify_flags & ssl.VERIFY_X509_STRICT == 0
    finally:
        context_relaxer.extract_from_ssl()


@pytest.mark.usefixtures("inject_relaxer")
def test_http_client():
    """
    This covers http.client for all relevant Python versions
    It also covers some of urllib.request implementations

    Here is the flow for context init depending on Python version (* notes init callable):
    Python <=3.11
        - urllib.request.urlopen -> ssl.create_default_context *
        - urllib.request.HTTPSHandler -> http.client.HTTPSConnection
        - http.client.HTTPSConnection -> ssl._create_default_https_context *
    Python ==3.12
        - urllib.request.urlopen -> ssl.create_default_context *
        - urllib.request.HTTPSHandler -> http.client._create_https_context
        - http.client.HTTPSConnection -> http.client._create_https_context
        - http.client._create_https_context -> ssl._create_default_https_context *
    Python >=3.13
        - urllib.request.urlopen -> urllib.request.HTTPSHandler
        - urllib.request.HTTPSHandler -> http.client._create_https_context
        - http.client.HTTPSConnection -> http.client._create_https_context
        - http.client._create_https_context -> ssl._create_default_https_context *
    """
    connection = HTTPSConnection("localhost")
    assert connection._context.verify_flags & ssl.VERIFY_X509_STRICT == 0


@pytest.mark.usefixtures("inject_relaxer")
def test_urllib3():
    """
    This also covers requests, it relies on urllib3's context builder
    urllib3 checks for python version to set flags
    if sys.version_info >= (3, 13)
    """
    ctx = context_relaxer._api.original_create_urllib3_context()
    if sys.version_info >= (3, 13) and context_relaxer._api.urllib3_version >= "2.4.0":
        assert ctx.verify_flags & ssl.VERIFY_X509_STRICT == ssl.VERIFY_X509_STRICT
    else:
        assert ctx.verify_flags & ssl.VERIFY_X509_STRICT == 0

    ctx = urllib3_ssl.create_urllib3_context()
    assert ctx.verify_flags & ssl.VERIFY_X509_STRICT == 0


@pytest.mark.usefixtures("inject_relaxer")
def test_aiohttp():
    """
    Verified context is using ssl.create_default_context
    """
    ctx = _make_ssl_context(verified=True)
    assert ctx.verify_flags & ssl.VERIFY_X509_STRICT == 0
