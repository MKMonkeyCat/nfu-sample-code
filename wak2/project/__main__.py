from __future__ import annotations

import streamlit as st

from project.ui import render_app


def main() -> None:
	st.set_page_config(page_title="眾數應用互動遊戲系統", page_icon="📊", layout="centered")
	render_app()


if __name__ == "__main__":
	main()
