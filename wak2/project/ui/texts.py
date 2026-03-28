from __future__ import annotations

from project.core import MODE_MULTI, ROUND_SINGLE

PAGE_TITLE_VOTE = "投票系統"
PAGE_TITLE_REPORT = "資料報告"
PAGE_TITLE_OVERVIEW = "即時概況大屏"

MODE_OPTIONS = [ROUND_SINGLE, MODE_MULTI]

FORM_DELETE_ID = "delete_votes_form"

RECENT_VOTES_LIMIT = 8

CAPTION_VOTE_PAGE = "請輸入投票資料"
SUBHEADER_VOTE_OVERVIEW = "即時概況"
CAPTION_VOTE_OVERVIEW = "即時呈現投票統計與最新資料變化"
METRIC_MODE_NOW = "目前眾數"
METRIC_TOTAL_VOTES = "總票數"
METRIC_VOTERS = "投票者"
METRIC_ROUNDS = "輪次"
SECTION_RECENT_DATA = "#### 最近資料"
LEADER_EMPTY_PLACEHOLDER = "尚未產生"
INFO_NO_VOTE_DATA = "尚未建立任何投票資料。"

COLUMN_ROUND = "輪次"
COLUMN_NAME = "姓名"
COLUMN_DRINK = "飲料"
COLUMN_VOTES = "票數"
COLUMN_RATIO = "占比"
COLUMN_MODES = "眾數"

FORM_VOTE_ID = "vote_form"
STATE_RESET = "reset_vote_form"
STATE_VOTE_MODE = "vote_mode"
STATE_VOTE_OPTION = "vote_option"
STATE_VOTE_ROUND_CHOICE = "vote_round_choice"
STATE_VOTE_NAME = "vote_name"
STATE_VOTE_CUSTOM_OPTION = "vote_custom_option"
STATE_VOTE_CUSTOM_ROUND_NAME = "vote_custom_round_name"

TITLE_OVERVIEW_PAGE = PAGE_TITLE_OVERVIEW
CAPTION_OVERVIEW_PAGE = "適合投影或大屏展示的即時票數看板"
SUBHEADER_OVERVIEW_CHART = "即時票數分布"
SUBHEADER_OVERVIEW_RECENT = "最新投票紀錄"
