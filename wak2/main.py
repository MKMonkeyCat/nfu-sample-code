import streamlit as st
import csv
import os
import matplotlib.pyplot as plt
from collections import Counter

# --- 基礎設定 ---
# 解決 Matplotlib 中文顯示問題
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei'] 
plt.rcParams['axes.unicode_minus'] = False
FILE_NAME = 'class_votes.csv'

# --- 核心邏輯 (任務一：檔案存取)  ---
def init_csv():
    """初始化 CSV 檔案，寫入標題列 [cite: 19-20]"""
    if not os.path.exists(FILE_NAME):
        with open(FILE_NAME, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(['姓名', '選項'])

def save_vote(name, option):
    """將資料寫入 CSV 檔案 [cite: 13, 21-23]"""
    with open(FILE_NAME, 'a', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow([name, option])

def load_data():
    """讀取 CSV 並返回 List [cite: 13, 24]"""
    data = []
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            next(reader)  # 跳過標題
            data = list(reader)
    return data

def clear_data():
    """清空所有資料 (進階管理功能)"""
    if os.path.exists(FILE_NAME):
        os.remove(FILE_NAME)
    init_csv()

# --- 頁面佈局 ---
st.set_page_config(page_title="眾數分析系統", layout="wide")
init_csv()

st.title("🥤 眾數應用互動遊戲系統")
st.info("本系統由 Python 原生邏輯開發，不依賴 pandas，專注於統計分析與決策支援。")

# --- 側邊欄 (任務一：互動輸入) [cite: 12-18] ---
with st.sidebar:
    st.header("🗳️ 進行投票")
    name = st.text_input("請輸入姓名", placeholder="例如：小明")
    option = st.selectbox("最喜歡的飲料", ["奶茶", "紅茶", "綠茶", "拿鐵", "烏龍茶"])
    
    col_submit, col_clear = st.columns(2)
    with col_submit:
        if st.button("送出投票", use_container_width=True):
            if name:
                save_vote(name, option)
                st.success(f"已記錄：{name} 投給 {option}")
            else:
                st.error("請輸入姓名！")
    
    with col_clear:
        if st.button("清空所有資料", type="secondary", use_container_width=True):
            clear_data()
            st.rerun()

# --- 讀取與計算 (任務二 & 三) [cite: 25-40] ---
raw_data = load_data()
options_only = [row[1] for row in raw_data]

if options_only:
    # 統計分析邏輯 (不使用 pandas) 
    counts = Counter(options_only)
    total_count = len(options_only)
    
    # 找出眾數 (任務二：處理並列眾數) [cite: 26-28]
    max_votes = max(counts.values())
    modes = [opt for opt, val in counts.items() if val == max_votes]
    
    # 找出最少選項 [cite: 34]
    min_votes = min(counts.values())
    least_options = [opt for opt, val in counts.items() if val == min_votes]

    # --- 畫面呈現：統計分析 (任務三 & 任務五即時顯示) [cite: 29-40, 47-51] ---
    col1, col2, col3 = st.columns(3)
    col1.metric("總人數 (Total)", f"{total_count} 人")
    col2.metric("目前眾數 (Mode)", "、".join(modes), f"{max_votes} 票")
    col3.metric("參與度最低", "、".join(least_options), f"{min_votes} 票", delta_color="inverse")

    st.divider()

    # --- 統計圖 (任務四)  ---
    st.subheader("📊 資料視覺化趨勢")
    fig, ax = plt.subplots(figsize=(10, 4))
    
    # 攝影美學配色：眾數為亮藍色，其餘為柔和灰色
    colors = ['#3498db' if opt in modes else '#ecf0f1' for opt in counts.keys()]
    edge_colors = ['#2980b9' if opt in modes else '#bdc3c7' for opt in counts.keys()]
    
    bars = ax.bar(counts.keys(), counts.values(), color=colors, edgecolor=edge_colors, linewidth=1.5)
    ax.set_title("各品項票數分佈情形", fontsize=14)
    ax.set_ylabel("投票數")
    
    # 在柱狀圖上方標註數據 [cite: 43]
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, yval + 0.05, f'{int(yval)}', ha='center', va='bottom')

    st.pyplot(fig)

    # 任務一驗證：預期讀取結果展示 [cite: 24]
    with st.expander("查看底層 CSV 資料 (驗證 Task 1)"):
        st.write("讀取後的資料結構為：", raw_data)
else:
    st.warning("目前尚無資料，請於側邊欄輸入投票。")