#!/usr/bin/env python3
# src/import_surgeon/modules/analysis.py

import re
from typing import List


def check_remaining_usages(
    content: str, old_module: str, symbols: List[str]
) -> List[str]:
    res = []
    for symbol in symbols:
        try:
            pattern = re.compile(rf"\b{re.escape(old_module)}\.{re.escape(symbol)}\b")
            matches = pattern.findall(content)
            if matches:
                res.append(
                    f"Potential remaining dotted usages for {symbol}: {len(matches)} instances"
                )
        except Exception:
            pass
    return res
