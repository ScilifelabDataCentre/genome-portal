#!/bin/env python
import csv
import os
import sys
from urllib.parse import urlparse


def list_pages(hugo_dir):
    cmd = f"hugo list -s {hugo_dir} published"
    reader = csv.DictReader(os.popen(cmd))
    return [urlparse(line["permalink"]).path for line in reader]


if __name__ == "__main__":
    try:
        hugo_dir = sys.argv[1]
    except IndexError:
        sys.stderr.write("Usage: list_pages.py HUGO_SOURCE_DIR")
        exit(1)
    print("\n".join(list_pages(hugo_dir)))
