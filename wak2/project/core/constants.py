from __future__ import annotations

import re

ROUND_OPTIONS = [f"day{i}" for i in range(1, 8)]
CUSTOM_ROUND_OPTION = "自訂輪次"
ROUND_NAME_PATTERN = re.compile(r"^[0-9A-Za-z\u4e00-\u9fff_-]+$")
