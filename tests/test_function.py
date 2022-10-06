#!/usr/bin/env python3
import json
import sys

from lambda_function import lambda_handler


EVENT = {
  "Records": [
    {
      "cf": {
        "config": {
          "distributionDomainName": "d3ujh5oi9ugd23.cloudfront.net",
          "distributionId": "E2D6EUJ5L1POFJE",
          "eventType": "viewer-request",
          "requestId": "4TyzHTaYWb1GX1qTfsHhEqV6HUDd_BzoBZnwfnvQc_1oF26ClkoUSEQ=="
        },
        "request": {
          "clientIp": "10.1.1.1",
          "headers": {
            "host": [
              {
                "key": "Host",
                "value": "d3ujh5oi9ugd23.cloudfront.net"
              }
            ],
            "user-agent": [
              {
                "key": "User-Agent",
                "value": "curl/7.66.0"
              }
            ],
            "accept": [
              {
                "key": "accept",
                "value": "*/*"
              }
            ]
          },
          "method": "GET",
          "querystring": "",
          "uri": "/"
        }
      }
    }
  ]
}


class TestCollector:
    path = "test-results.tap"

    def __init__(self, test_count):
        self.test_count = test_count
        self.current_test = 0
        self.ok = True

    def __enter__(self):
        self.fh = open(self.path, "w")
        self.fh.write(f"1..{self.test_count}\n")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.fh.close()

    def add_results(self, ok, name):
        self.current_test += 1
        if ok:
            status = "ok"
        else:
            status = "not ok"
            self.ok = False
        self.fh.write(f"{status} {self.current_test} - {name}\n")


def get_test_count(rewrites):
    tests = 0
    for rewrite in rewrites:
        tests += len(rewrite.get("tests", ["foo"]))
    return tests


def event_for_uri(uri):
    EVENT["Records"][0]["cf"]["request"]["uri"] = uri
    return EVENT


def test_rewrite(rewrite, test_collector):
    for test_uri in rewrite.get("tests", [rewrite["src"]]):
        event = event_for_uri(test_uri)
        location = lambda_handler(event, None)["headers"]["location"][0]["value"]
        test_name = f"{test_uri}: {location} -> {rewrite['dest']}"
        test_collector.add_results(location == rewrite["dest"], test_name)


def main():
    rewrites = json.load(open(sys.argv[1]))
    code = None
    with TestCollector(get_test_count(rewrites)) as test_collector:
        for rewrite in rewrites:
            test_rewrite(rewrite, test_collector)
        code = 0 if test_collector.ok else 1
    sys.exit(code)


main()
