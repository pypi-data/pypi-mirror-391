#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""String utilities for the pyvider.cty package."""

from __future__ import annotations

import unicodedata


def normalize_string(value: str) -> str:
    """Normalize a string to NFC form for consistent handling.

    NFC (Canonical Decomposition, followed by Canonical Composition) is used
    throughout the cty type system to ensure that strings with different Unicode
    representations are treated as equivalent. This is necessary for consistent
    behavior with go-cty's string handling and for use as map/object keys.

    Args:
        value: The string to normalize

    Returns:
        The normalized string in NFC form
    """
    return unicodedata.normalize("NFC", value)


# 🌊🪢🔚
