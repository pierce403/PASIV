#!/bin/bash
# PASIV Key-Address Matcher Wrapper
# Automatically activates virtual environment and runs the matcher

# Change to script directory
cd "$(dirname "$0")"

# Activate virtual environment
source venv/bin/activate

# Run the key-address matcher with all provided arguments
python3 src/attacks/key_address_matcher.py "$@" 