from __future__ import annotations

import base64
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.font_manager import FontProperties
import streamlit as st

from project.core import add_vote
from project.core import build_summary
from project.core import get_modes
from project.core import read_votes

ROOT_DIR = Path(__file__).resolve().parents[2]
FONT_PATH = ROOT_DIR / "static" / "NotoSansJP-VariableFont_wght.ttf"

font_manager.fontManager.addfont(str(FONT_PATH))
font1 = FontProperties(fname=str(FONT_PATH))
plt.rcParams["font.family"] = font1.get_name()
plt.rcParams["axes.unicode_minus"] = False


def _apply_streamlit_font() -> None:
	"""Inject custom font into Streamlit page styles."""
	font_data = base64.b64encode(FONT_PATH.read_bytes()).decode("utf-8")
	st.markdown(
		f"""
		<style>
		@font-face {{
			font-family: 'NotoSansJP';
			src: url(data:font/ttf;base64,{font_data}) format('truetype');
			font-weight: 100 900;
			font-style: normal;
		}}

		html, body, [class*="css"], [data-testid="stAppViewContainer"] * {{
			font-family: 'NotoSansJP', sans-serif;
		}}
		</style>
		""",
		unsafe_allow_html=True,
	)



def _format_mode_text(modes: list[str], count: int) -> str:
	if not modes:
		return "尚無投票資料"
	if len(modes) == 1:
		return f"{modes[0]}（{count}票）"
	return f"{'、'.join(modes)}（各{count}票）"


def _render_bar_chart(counts: dict[str, int], modes: list[str]) -> None:
	if not counts:
		st.info("尚無資料可繪圖")
		return

	options = list(counts.keys())
	values = [counts[option] for option in options]
	colors = ["#d62728" if option in modes else "#1f77b4" for option in options]

	fig, ax = plt.subplots(figsize=(7, 4))
	bars = ax.bar(options, values, color=colors)
	ax.set_title("選項票數統計圖", fontproperties=font1)
	ax.set_xlabel("選項", fontproperties=font1)
	ax.set_ylabel("票數", fontproperties=font1)
	ax.grid(axis="y", linestyle="--", alpha=0.3)

	for tick in ax.get_xticklabels() + ax.get_yticklabels():
		tick.set_fontproperties(font1)

	for bar, value in zip(bars, values):
		ax.text(
			bar.get_x() + bar.get_width() / 2,
			value + 0.05,
			str(value),
			ha="center",
			va="bottom",
		)

	st.pyplot(fig)
	plt.close(fig)


def render_app() -> None:
	_apply_streamlit_font()
	st.title("眾數應用互動遊戲系統")
	st.caption("任務涵蓋 CSV 存取、眾數計算、統計分析與圖表呈現")

	data_path = Path("data") / "votes.csv"

	with st.form("vote_form", clear_on_submit=True):
		st.subheader("任務一：互動輸入與檔案存取")
		name = st.text_input("姓名")
		option = st.text_input("選項（例如：奶茶、紅茶）")
		submitted = st.form_submit_button("新增投票")

	if submitted:
		if not name.strip() or not option.strip():
			st.error("請完整輸入姓名與選項")
		else:
			add_vote(data_path, name, option)
			records_after_add = read_votes(data_path)
			counts_after_add = build_summary(records_after_add)["counts"]
			modes, mode_count = get_modes(counts_after_add)
			st.success("已新增投票")
			st.info(f"目前眾數：{_format_mode_text(modes, mode_count)}")

	records = read_votes(data_path)
	summary = build_summary(records)

	st.subheader("目前資料")
	if records:
		st.dataframe(
			[{"姓名": name, "選項": option} for name, option in records],
			width="stretch",
		)
		list_result = [[name, option] for name, option in records]
		st.code(str(list_result), language="python")
	else:
		st.info("尚無投票資料，請先新增一筆。")

	st.subheader("任務二與三：眾數與統計分析")
	st.write(f"總人數：{summary['total']}")

	counts = summary["counts"]
	if counts:
		for option_name, count in sorted(counts.items()):
			st.write(f"{option_name}：{count}次")
		st.write(f"眾數：{'、'.join(summary['modes'])}")
		st.write(f"最少選項：{'、'.join(summary['least'])}")
	else:
		st.write("眾數：無")
		st.write("最少選項：無")

	st.subheader("任務四：統計圖")
	_render_bar_chart(counts, summary["modes"])

	st.subheader("任務五：即時顯示眾數")
	st.write("每次按下「新增投票」後，上方會立即顯示目前眾數。")
