#!/usr/bin/env python3
"""Client. Calls Inventory through the Kubernetes Service name."""

import argparse
import json
import os
import time
import urllib.error
import urllib.request


def request_item(base_url):
    url = base_url.rstrip("/") + "/items/laptop"
    request = urllib.request.Request(url, headers={"Connection": "close"})
    with urllib.request.urlopen(request, timeout=3) as response:
        body = json.loads(response.read().decode())
        status = response.status
    print(
        f"GET {url} status={status} pod={body.get('pod')} "
        f"available={body.get('available')} quantity_on_hand={body.get('quantity_on_hand')}",
        flush=True,
    )


def main():
    parser = argparse.ArgumentParser(description="Send requests to the Inventory Service.")
    parser.add_argument("--count", type=int, default=int(os.environ.get("REQUEST_COUNT", "0")))
    parser.add_argument("--interval", type=float, default=float(os.environ.get("INTERVAL", "0.3")))
    args = parser.parse_args()
    base_url = os.environ.get("INVENTORY_URL", "http://inventory")
    print(f"client using inventory service at {base_url}", flush=True)

    sent = 0
    while args.count == 0 or sent < args.count:
        try:
            request_item(base_url)
        except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
            print(f"GET {base_url.rstrip('/')}/items/laptop error={exc}", flush=True)
        sent += 1
        if args.count == 0 or sent < args.count:
            time.sleep(args.interval)


if __name__ == "__main__":
    main()
