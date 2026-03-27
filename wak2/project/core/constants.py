from __future__ import annotations

import re

ROUND_OPTIONS = [f"day{i}" for i in range(1, 8)]
ROUND_SINGLE = "單輪"
MODE_MULTI = "多輪"
DEFAULT_ROUND = ROUND_SINGLE

CUSTOM_ROUND_OPTION = "自訂輪次"
ROUND_NAME_PATTERN = re.compile(r"^[0-9A-Za-z\u4e00-\u9fff_-]+$")

CSV_HEADER_WITH_ROUND = ["輪次", "姓名", "選項"]
CSV_HEADER_NO_ROUND = ["姓名", "選項"]
CSV_COL_ROUND = "輪次"
CSV_COL_NAME = "姓名"
CSV_COL_OPTION = "選項"

MAX_NAME_LENGTH = 50
MAX_OPTION_LENGTH = 50
MAX_CUSTOM_ROUND_LENGTH = 20

ERR_NAME_EMPTY = "姓名不能為空"
ERR_OPTION_EMPTY = "選項不能為空"
ERR_NAME_TOO_LONG = f"姓名長度不能超過{MAX_NAME_LENGTH}字"
ERR_OPTION_TOO_LONG = f"選項長度不能超過{MAX_OPTION_LENGTH}字"
ERR_DUPLICATE_VOTE = "同一位投票者在同一輪次只能投一次"
ERR_ROUND_EMPTY = "輪次名稱不能為空"
ERR_CUSTOM_ROUND_TOO_LONG = f"自訂輪次名稱不能超過{MAX_CUSTOM_ROUND_LENGTH}字"
ERR_CUSTOM_ROUND_INVALID = "自訂輪次只允許中文、英文、數字、-、_"
