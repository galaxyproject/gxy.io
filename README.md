# gxy.io link shortening

This repository is for [Galaxy Project](https://galaxyproject.org/) members to create gxy.io short links that redirect
to other URLs, e.g. for publications, conference slides, etc.

## Usage

1. Add your link to `gxy_io_rewrites` in [group_vars/all.yaml](group_vars/all.yaml).

   See the **Rewrite entry syntax** section below for details.

2. Make a Pull Request with your changes. A test will make sure your syntax passes. Once your PR is approved and merged, the changes are automatically deployed.

## Rewrite entry syntax

`gxy_io_rewrites` is a list of dictionaries with required keys `src` and `dest` and the optional key `tests`.

The value of `src` is the path (after `gxy.io`) of the short link you would like to create. It should start with a `/`
and supports regular expressions; the path component of a gxy.io request is checked with `re.match(src, path)`. Any
trailing `/` is automatically stripped and `/?` appended, meaning that `/example` and `/example/` are equivalent.

The value of `dest` is the URL to redirect to. It can contain regex backreferences.

The optional `tests` key can contain a list of paths to test as inputs to the rewrite function, to ensure they all
rewrite to the value of `dest`. The default if `tests` is unset is to use the `src` as the test input value, so defining
your own `tests` is required if `src` is a regular expression.

Alternatively, `tests` can be a list of dicts with `src` and `dest` keys, which is necessary if the rewrite `dest`
contains a regex backreference.

A few examples are shown below, but all currently supported possibilities are represented in the [current set of
rewrites](group_vars/all.yaml).

## Examples

A simple example that does not use regex, rewrites `http://gxy.io/example` (with or without trailing slash) to
`http://example.org`. The implied test ensures that the `src` value rewrites to `dest`:

```yaml
- src: /example
  dest: http://example.org
```

Using regex to allow for some common variations in the `src` - all of `/test-example`, `test_example`, and
`/testexample` will rewrite to `http://example.org`. At least one test definition is required since `src` contains a
regex:

```yaml
- src: /test[-_]?example
  dest: http://example.org
  tests:
    - /test-example
    - /testexample
```

Using backreferences in `dest` to rewrite any path after `/example/` to another domain with the path intact, requires
`src` and `dest` keys in `tests`:

```yaml
- src: "/example/(.*)"
  dest: "http://example.org/\\1"
  tests:
    - src: /example/foo
      dest: http://example.org/foo
    - src: /example/foo/bar?baz=quux
      dest: http://example.org/foo/bar?baz=quux
```

## Notes

Rewrites are performed via an AWS [Lambda@Edge](https://aws.amazon.com/lambda/edge/) function via CloudFront. [The
function](templates/lambda_function.py.j2) runs under the Python 3.9 runtime.

The initial gxy.io service (pre-automation) ran via nginx on an EC2 instance, so some work was done to support
automated deployment under nginx, which is preserved in the [nginx](nginx/) directory in case it would be useful in the
future.
