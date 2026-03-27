from __future__ import annotations

from project.core import MODE_MULTI, ROUND_SINGLE

PAGE_TITLE_VOTE = "投票系統"
PAGE_TITLE_REPORT = "資料報告"

MODE_OPTIONS = [ROUND_SINGLE, MODE_MULTI]

FORM_DELETE_ID = "delete_votes_form"

RECENT_VOTES_LIMIT = 8

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
