# 减脂体重记录 - 强制背景色 100% 必生效版
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os
import json

# ================== 页面设置 ==================
st.set_page_config(
    page_title="减脂体重记录",
    page_icon="🔥",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ================== 强制背景颜色（必生效！） ==================
import random
# 每日随机马卡龙色系
colors = [
    ("#f8eaf3", "#fddfeb", "#e5f3ff"),  # 粉紫系
    ("#e5f0ff", "#d1e0ff", "#f0f8ff"),  # 蓝白系
    ("#f9f3e6", "#f7ead0", "#fff8e8"),  # 奶油黄系
    ("#e8f4ea", "#d4eed8", "#f0fcf4"),  # 薄荷绿系
]
# 按日期固定颜色（每天换一种，不随机跳）
today = datetime.now().day
chosen_colors = colors[today % len(colors)]

st.markdown(f"""
<style>
.stApp {{
    background: linear-gradient(45deg, {chosen_colors[0]}, {chosen_colors[1]}, {chosen_colors[2]}) !important;
    background-attachment: fixed !important;
}}
</style>
""", unsafe_allow_html=True)

plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False

# ================== 配置文件 ==================
CONFIG_FILE = "user_config.json"
DATA_FILE = "my_weight.csv"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"target_weight": 60.0, "height": 1.70}

def save_config(target_weight, height):
    data = {"target_weight": target_weight, "height": height}
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=["日期", "体重(kg)"])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# ================== 加载数据 ==================
config = load_config()
df = load_data()
last_weight_value = df["体重(kg)"].iloc[-1] if not df.empty else 30.0

# ================== 界面 ==================
st.title("🔥 我的减脂体重记录")
st.markdown("---")

col1, col2 = st.columns([3, 1])
with col1:
    weight = st.number_input(
        "当前体重 (kg)",
        min_value=30.0,
        max_value=200.0,
        value=last_weight_value,
        step=0.1,
        format="%.1f"
    )
with col2:
    st.write("")
    if st.button("✅ 保存", use_container_width=True, type="primary"):
        if weight <= 0:
            st.warning("请输入有效体重！")
        else:
            now = datetime.now().strftime("%Y-%m-%d %H:%M")
            new_row = {"日期": now, "体重(kg)": weight}
            df_new = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            save_data(df_new)
            st.success("保存成功！")
            st.rerun()

st.markdown("---")

if not df.empty:
    last_weight = df["体重(kg)"].iloc[-1]
    target_weight = st.number_input(
        "🎯 目标体重 (kg)",
        min_value=30.0,
        max_value=200.0,
        value=float(config["target_weight"]),
        step=0.5,
        format="%.1f"
    )
    height = st.number_input(
        "身高 (m)",
        min_value=1.0,
        max_value=2.3,
        value=float(config["height"]),
        step=0.01,
        format="%.2f"
    )
    save_config(target_weight, height)

    remaining = last_weight - target_weight
    if remaining > 0:
        st.success(f"📉 距离目标还差：{remaining:.1f} kg")
    else:
        st.balloons()
        st.success("🎉 恭喜达成目标！")

    bmi = last_weight / (height ** 2)
    bmi_text = "偏瘦" if bmi < 18.5 else "正常✅" if bmi < 24 else "超重" if bmi < 28 else "肥胖"
    st.info(f"📊 当前 BMI：{bmi:.1f}  —— 【{bmi_text}】")

st.markdown("---")

if not df.empty:
    st.subheader("📉 体重变化趋势")
    df["日期"] = pd.to_datetime(df["日期"])
    df_sorted = df.sort_values("日期")
    first = df_sorted["体重(kg)"].iloc[0]
    last = df_sorted["体重(kg)"].iloc[-1]
    change = last - first
    trend = "📉 下降" if change < 0 else "📈 上升"
    st.info(f"累计变化：{trend} {abs(change):.1f} kg")

    fig, ax = plt.subplots(figsize=(8, 3.5))
    ax.plot(df_sorted["日期"], df_sorted["体重(kg)"], marker="o", color="#1677ff", linewidth=2)
    ax.grid(alpha=0.3)
    plt.xticks(rotation=45, fontsize=9)
    plt.tight_layout()
    st.pyplot(fig)

    st.markdown("### 📋 最近记录")
    df_recent = df.sort_values("日期", ascending=False)
    st.dataframe(df_recent, use_container_width=True, hide_index=True)
else:
    st.info("快来输入体重开始你的减脂之旅吧！💪")

st.markdown("---")
st.caption("✅ 柔美马卡龙背景已生效")
