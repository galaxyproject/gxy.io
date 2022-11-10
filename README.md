# gxy.io link shortening

This repository is for [Galaxy Project](https://galaxyproject.org/) members to create gxy.io short links that redirect
to other URLs, e.g. for publications, conference slides, etc.

## Usage

1. Add your link to `gxy_io_rewrites` in [group_vars/all.yaml](group_vars/all.yaml).

    The value of `src` is the path (after `gxy.io`) of the short link you would like to create. It should start with a
    `/` and supports regular expressions; the path component of a gxy.io request is checked with `re.match(src, path)`.

    The value of `dest` is the URL to redirect to.

    The `tests` key is optional unless the `src` is a regular expression. This should contain a list of paths to test
    that the rewrite function appropriately rewrites paths matching your `src` to your `dest`. If unset, it defaults to
    the value of `src`.

2. Make a Pull Request with your changes. A test will make sure your syntax passes. Once your PR is approved and merged, the changes are automatically deployed.

## Notes

Rewrites are performed via an AWS [Lambda@Edge](https://aws.amazon.com/lambda/edge/) function via CloudFront. [The
function](templates/lambda_function.py.j2) runs under the Python 3.9 runtime.

The initial gxy.io service (pre-automation) ran via nginx on an EC2 instance, so some work was done to support
automated deployment under nginx, which is preserved in the [nginx](nginx/) directory in case it would be useful in the
future.

Backreferences from `src` are not supported (there has been no need thus far), but could be implemented fairly easily in
the Lambda function, if someone wanted it.
