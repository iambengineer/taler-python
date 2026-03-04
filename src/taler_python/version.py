# SPDX-FileCopyrightText: 2026-present Benjamin Kusen <benjamin.kusen@gmail.com>
#
# SPDX-License-Identifier: MIT
import re
from typing import NamedTuple

# Target protocol versions for this SDK release.
# Merchant API v27, Exchange API v32.
MERCHANT_PROTOCOL_VERSION = 27
EXCHANGE_PROTOCOL_VERSION = 32


class LibtoolVersion(NamedTuple):
    current: int
    revision: int
    age: int


def parse_version(version_str: str) -> LibtoolVersion:
    """Parse a libtool version string like "27:0:5" into its components.

    Format is "current[:revision[:age]]" — revision and age default to 0
    if omitted.
    """
    if not version_str:
        raise ValueError("Version string must not be empty")

    parts = version_str.split(":")
    if len(parts) > 3:
        raise ValueError(f"Expected at most 3 parts, got {len(parts)}: {version_str!r}")

    for p in parts:
        if not p.isdigit():
            raise ValueError(f"Non-numeric version component: {p!r}")

    current, revision, age = (int(p) for p in parts + ["0"] * (3 -len(parts)))
    return LibtoolVersion(current, revision, age)



def check_version(server_version: str, client_version: int) -> bool:
    """Check if client_version falls within the server's supported range.

    The server supports [current - age, current]. The client is compatible
    if client_version falls within that range (inclusive on both ends).
    """
    
    parsed_server_version = parse_version(server_version)
    return client_version >= parsed_server_version.current - parsed_server_version.age and client_version <= parsed_server_version.current
