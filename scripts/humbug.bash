#!/usr/bin/env bash

# humbug.bash - The Bugout crash reporting administration script
# Requirements:
# 1. jq - To install on Linux: `apt-get install jq`, to install on Mac with Homebrew: `brew install jq`
# 2. bugout - The Bugout CLI, available at: https://github.com/bugout-dev/bugout-go/releases/latest

set -e -o pipefail

if [ -z "$BUGOUT_ACCESS_TOKEN" ]
then
    echo "Please set the BUGOUT_ACCESS_TOKEN environment variable."
    echo "You can create an access token at https://bugout.dev/account/tokens"
    exit 1
fi

if [ -z "$BUGOUT_JOURNAL_ID" ]
then
    echo "Please set the BUGOUT_JOURNAL_ID environment variable."
    echo "This is the ID of the knowledge base you will be working with. Get this by selecting"
    echo "the desired journal at https://bugout.dev and getting the ID from the URL. The URL"
    echo "is structured like: https://bugout.dev/journals/<BUGOUT_JOURNAL_ID>."
    exit 1
fi

export BUGOUT_ACCESS_TOKEN BUGOUT_JOURNAL_ID

# We're downloading 500 reports in each batch, which can take longer than the bugout default timeout of 3 seconds.
export BUGOUT_TIMEOUT_SECONDS=15

# Batch size for data download
BUGOUT_SEARCH_LIMIT="${BUGOUT_SEARCH_LIMIT:-500}"

# Output directory. Data is dumped as a series of JSON files into this directory.
if [ -z "$BUGOUT_OUTPUT_DIRECTORY" ]
then
    BUGOUT_OUTPUT_DIRECTORY=$(mktemp -d)
fi
echo "Writing output to: $BUGOUT_OUTPUT_DIRECTORY"

if ! which bugout 1>/dev/null
then
    echo "This script requires you to have the bugout CLI installed and available as \"bugout\" on"
    echo "your PATH."
    echo "Get the latest release here: https://github.com/bugout-dev/bugout-go/releases/latest"
    exit 1
fi

if ! which jq 1>/dev/null
then
    echo "This script requires you to have jq installed and available as \"jq\" on your PATH."
    echo "Get the latest release here: https://stedolan.github.io/jq/"
    echo "To install on Debian/Ubuntu with apt: \"apt-get install jq\""
    echo "To install on Mac using Homebrew: \"brew install jq\""
    exit 1
fi

SEARCH_QUERY="$*"

TOTAL_RESULTS=$(bugout entries search "$SEARCH_QUERY" --limit 0 | jq ".total_results")
echo "Total results: $TOTAL_RESULTS"
echo "Processing in batches of size BUGOUT_SEARCH_LIMIT=$BUGOUT_SEARCH_LIMIT"

OFFSET=0
while [ "$OFFSET" -lt "$TOTAL_RESULTS" ]
do
    OUTPUT_FILE="$BUGOUT_OUTPUT_DIRECTORY/$OFFSET.json"
    echo "Processing $BUGOUT_SEARCH_LIMIT items with offset $OFFSET into $OUTPUT_FILE"
    bugout entries search "$SEARCH_QUERY" --limit "$BUGOUT_SEARCH_LIMIT" --offset "$OFFSET" > "$OUTPUT_FILE"
    OFFSET=$((OFFSET + BUGOUT_SEARCH_LIMIT))
done
