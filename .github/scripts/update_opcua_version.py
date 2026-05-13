#!/usr/bin/env python3
"""Update opcua_version entries in publish.yaml.

Behaviour:
- Same major (e.g. 1023.2.1 -> 1023.3.0):
    All opcua_version entries in the matrix are bumped.
- New major (e.g. 1023.2.1 -> 1024.0.0):
    Only the generic `opcua-device-gateway` entry is updated.
    A new major-version-pinned entry (e.g. `opcua-device-gateway-1024`) is added.
    The old major-version entry (e.g. `opcua-device-gateway-1023`) is frozen.

Required environment variables:
    LATEST          new version string  (e.g. "1024.0.0")
    CURRENT         current version string (e.g. "1023.2.1")
    LATEST_MAJOR    major part of LATEST  (e.g. "1024")
    CURRENT_MAJOR   major part of CURRENT (e.g. "1023")
"""

import os
import re
import sys

publish_yaml = ".github/workflows/publish.yaml"

# --get-current: print the current version for the generic entry and exit
if "--get-current" in sys.argv:
    with open(publish_yaml) as f:
        content = f.read()
    m = re.search(r'opcua_version: "([^"]+)"\s+image: opcua-device-gateway\n', content)
    if not m:
        print("ERROR: could not find the generic opcua-device-gateway entry", file=sys.stderr)
        sys.exit(1)
    print(m.group(1))
    sys.exit(0)

latest = os.environ["LATEST"]
current = os.environ["CURRENT"]
latest_major = os.environ["LATEST_MAJOR"]
current_major = os.environ["CURRENT_MAJOR"]

publish_yaml = ".github/workflows/publish.yaml"

with open(publish_yaml) as f:
    content = f.read()

if latest_major == current_major:
    # Same major: bump ALL opcua_version entries in the matrix.
    updated = content.replace(
        f'opcua_version: "{current}"',
        f'opcua_version: "{latest}"',
    )
    if updated == content:
        print(f"ERROR: could not find opcua_version: \"{current}\" in {publish_yaml}", file=sys.stderr)
        sys.exit(1)
    content = updated
else:
    # New major:
    # Step 1 – update only the generic entry (image name has no major suffix).
    #           The regex matches the version on the line immediately before
    #           `image: opcua-device-gateway` (with no trailing `-NNN`).
    pattern = (
        r'(- opcua_version: )"'
        + re.escape(current)
        + r'"(\s+image: opcua-device-gateway\n)'
    )
    content, n = re.subn(
        pattern,
        lambda m: m.group(1) + f'"{latest}"' + m.group(2),
        content,
    )
    if n == 0:
        print(
            f"ERROR: could not locate the generic opcua-device-gateway entry in {publish_yaml}",
            file=sys.stderr,
        )
        sys.exit(1)

    # Step 2 – insert a new major-version-pinned entry right after the generic one.
    #   10 spaces match the existing `- opcua_version:` indentation in publish.yaml.
    indent = "          "
    new_entry = (
        f"\n{indent}- opcua_version: \"{latest}\"\n"
        f"{indent}  image: opcua-device-gateway-{latest_major}\n"
    )
    # "image: opcua-device-gateway\n" only matches the generic line
    # (the major-version lines have a suffix like "-1023\n").
    marker = "image: opcua-device-gateway\n"
    pos = content.find(marker)
    if pos == -1:
        print(f"ERROR: could not find insertion point in {publish_yaml}", file=sys.stderr)
        sys.exit(1)
    pos += len(marker)
    content = content[:pos] + new_entry + content[pos:]

with open(publish_yaml, "w") as f:
    f.write(content)

print(f"Updated {publish_yaml}: {current} -> {latest}")
