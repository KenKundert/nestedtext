#!/usr/bin/env python3
"""Demonstrate comment-preserving round trip with NestedText.

Reads a NestedText file with hand-written comments and blank-line spacing,
modifies the data, and writes it back -- preserving the original layout.

Usage:
    round_trip.py [INPUT_FILE]

If no input is given, the script uses ``b05_header_only.nt`` from this
directory.
"""

import sys
from pathlib import Path

import nestedtext as nt


def main():
    if len(sys.argv) > 1:
        path = Path(sys.argv[1])
    else:
        path = Path(__file__).parent / "b05_header_only.nt"

    keymap = {}
    data = nt.loads(path.read_text(), top="any", keymap=keymap)

    # Modify the data: bump retry_delay if present, append a port if a server
    # block exists.  These are just to show that arbitrary edits to the data
    # still round-trip cleanly.
    if isinstance(data, dict):
        if "retry_delay" in data:
            data["retry_delay"] = str(int(data["retry_delay"]) + 1)
        if "server" in data and isinstance(data["server"], dict):
            data["server"].setdefault("port", "8080")

    # Pass the keymap to dumps to reinstate the comments and spacing.
    print(nt.dumps(data, map_keys=keymap))


if __name__ == "__main__":
    main()
