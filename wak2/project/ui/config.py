from __future__ import annotations

from pathlib import Path

DATA_DIR = Path("data")
CSV_FILE = DATA_DIR / "votes.csv"
DRINK_OPTIONS = ["奶茶", "紅茶", "綠茶", "拿鐵", "烏龍茶", "其他"]

COLOR_PALETTE = {
    "奶茶": {"primary": "#C97A2B", "soft": "#F1D1AB"},
    "紅茶": {"primary": "#B64A4A", "soft": "#E9B0B0"},
    "綠茶": {"primary": "#2F8F6B", "soft": "#B7DEC9"},
    "拿鐵": {"primary": "#7B5C99", "soft": "#D5C3E7"},
    "烏龍茶": {"primary": "#2D7F91", "soft": "#B6DCE5"},
}


def init_app() -> None:
    """初始化應用"""
    DATA_DIR.mkdir(exist_ok=True)
    # core.ensure_csv(CSV_FILE)
