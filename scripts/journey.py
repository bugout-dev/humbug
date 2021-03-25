#!/usr/bin/env python3
"""
Visualizes a single journey using the Bugout API.

Install requirements:
    pip3 install bugout python-dateutil
"""
import argparse
from datetime import time
import os

from bugout.app import Bugout
from dateutil.parser import parse as parse_date

parser = argparse.ArgumentParser(description="Humbug journey visualizer")
parser.add_argument(
    "-t",
    "--token",
    type=str,
    default=None,
    help="Bugout access token (if not specified, checks BUGOUT_ACCESS_TOKEN environment variable)",
)
parser.add_argument(
    "-j",
    "--journal",
    type=str,
    default=None,
    help="Bugout journal ID (if not specified, checks the BUGOUT_JOURNAL_ID environment variable",
)
parser.add_argument(
    "query",
    nargs="*",
    help='Bugout search query whose results define the user journey (e.g.: "session:<session_id>")',
)
parser.add_argument(
    "-N",
    "--batch-size",
    type=int,
    default=500,
    help="Number of entries to download at a time",
)


def render_entry(entry):
    print("- - -")
    print(entry.title)
    print("  Link: {}".format(entry.entry_url))
    print("  Created at: {}".format(entry.created_at))
    print("  Tags:")
    for tag in sorted(entry.tags):
        print("  - {}".format(tag))
    print("- - -")


args = parser.parse_args()

token = args.token
if token is None:
    token = os.environ.get("BUGOUT_ACCESS_TOKEN")
if token is None:
    raise ValueError(
        "Please specify --token or set your BUGOUT_ACCESS_TOKEN environment variable"
    )

journal = args.journal
if journal is None:
    journal = os.environ.get("BUGOUT_JOURNAL_ID")
if journal is None:
    raise ValueError(
        "Please specify --journal or set your BUGOUT_JOURNAL_ID environment variable"
    )


query = " ".join(args.query)

bugout_client = Bugout()

limit = args.batch_size
current_offset = 0
results = bugout_client.search(
    token, journal, query, limit=limit, offset=current_offset
)
entries = results.results
total_results = results.total_results
print("Total results:", total_results)
print("")

while len(entries) < total_results:
    print(current_offset)
    current_offset += limit
    results = bugout_client.search(
        token, journal, query, limit=limit, offset=current_offset
    )
    entries.extend(results.results)

timestamped_entries = []
for entry in entries:
    entry_created_at_seconds = parse_date(entry.created_at)
    timestamped_entries.append((entry_created_at_seconds, entry))

timestamped_entries.sort(key=lambda i: i[0])

last_timestamp, last_entry = timestamped_entries[0]
render_entry(last_entry)

for timestamp, entry in timestamped_entries[1:]:
    print("")
    print("    gap: {}".format(timestamp - last_timestamp))
    print("")
    render_entry(entry)
    last_timestamp = timestamp
    last_entry = entry
