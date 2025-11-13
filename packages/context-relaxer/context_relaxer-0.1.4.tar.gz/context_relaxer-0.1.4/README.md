# SSL Context Relaxer

Relax the SSL verification strictness introduced in python 3.13

Monkey-patching structure inspired by [truststore](https://github.com/sethmlarson/truststore)

## Usage

Install the library

```
pip install context-relaxer
```

At the entry point of your project, inject the monkey-patch

```python
import context_relaxer

context_relaxer.inject_into_ssl()
```

## Rationale

Many corporates have systems that proxy internal traffic, and sometimes they produce broken certificates.

Yes, they should be fixed, No, probably won't be fixed soon, but that doesn't mean you should pass `verify=False`
or `ssl_verify=False` to every HTTPS session instance.

## Usage with truststore

You can use this concurrently with `truststore`, as we monkey-patch different properties of `ssl`, this library patches
the default context creation function and `truststore` patches the SSLContext class. 

Usage example (the order doesn't matter)

```python
import context_relaxer
import truststore

truststore.inject_into_ssl()
context_relaxer.inject_into_ssl()
```

## Tested usage

* `urllib` (builtin)
* `urllib3`
* `requests`
* `aiohttp`

## Requests 2.32.0 - 2.32.4

In version 2.32.0 `requests` introduced a preloaded context, which was reverted in 2.32.5

If you are using a version in this range, make sure to inject the monkey-patch before importing `requests` 
