import functools
import ssl
import sys

try:
    import urllib3.util.ssl_ as urllib3_ssl
    from urllib3 import __version__ as urllib3_version, connection

    original_create_urllib3_context = urllib3_ssl.create_urllib3_context
except ImportError:
    urllib3_ssl = None


    def original_create_urllib3_context(*args, **kwargs) -> ssl.SSLContext:
        raise NotImplementedError()

original_create_default_context = ssl.create_default_context


@functools.wraps(ssl.create_default_context)
def patched_create_default_context(*args, **kwargs):
    context = original_create_default_context(*args, **kwargs)
    # Remove the STRICT flag
    context.verify_flags &= ~ssl.VERIFY_X509_STRICT
    return context


@functools.wraps(original_create_urllib3_context)
def patched_create_urllib3_context(**kwargs) -> ssl.SSLContext:
    """
    In this function it is possible to pass flags, so we need to override in ingress
    """
    if urllib3_version >= "2.4.0":
        # Before version 2.4.0 urllib3 did not implement the python 3.13 ssl verify_flags compatibility
        if kwargs.get("verify_flags", None) is None and sys.version_info >= (3, 13):
            kwargs["verify_flags"] = ssl.VERIFY_X509_PARTIAL_CHAIN

    context = original_create_urllib3_context(**kwargs)
    return context


def inject_into_ssl() -> None:
    setattr(ssl, "create_default_context", patched_create_default_context)
    setattr(ssl, "_create_default_https_context", patched_create_default_context)
    if urllib3_ssl:
        setattr(urllib3_ssl, "create_urllib3_context", patched_create_urllib3_context)
        # The function is imported specifically in urllib3.connection
        setattr(connection, "create_urllib3_context", patched_create_urllib3_context)


def extract_from_ssl() -> None:
    setattr(ssl, "create_default_context", original_create_default_context)
    setattr(ssl, "_create_default_https_context", original_create_default_context)
    if urllib3_ssl:
        setattr(urllib3_ssl, "create_urllib3_context", original_create_urllib3_context)
        setattr(connection, "create_urllib3_context", original_create_urllib3_context)
