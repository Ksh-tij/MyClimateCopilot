"""
bm25_utils.py
Shared tokenization for BM25 keyword search — used identically at index-build
time (indexing.py) and query time (retrieval.py) so tokenization never drifts
between the two.
"""

import re
from typing import List

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> List[str]:
    """Lowercase + alphanumeric word split."""
    return _TOKEN_RE.findall(text.lower())
