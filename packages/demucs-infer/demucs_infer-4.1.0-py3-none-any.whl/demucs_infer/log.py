# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

"""
Minimal logging replacement for dora.log to remove dora-search dependency.
"""

import sys


def fatal(msg):
    """Print error message and exit."""
    print(f"Error: {msg}", file=sys.stderr)
    sys.exit(1)


def bold(msg):
    """Return bold text (ANSI escape codes)."""
    return f"\033[1m{msg}\033[0m"
