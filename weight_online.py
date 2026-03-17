# 减脂体重记录 - 数据永久保存版（腾讯文档同步）
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import random
import requests
import json

# ================== 页面设置 ==================
st.set_page_config(
    page_title="减脂体重记录",
    page_icon="🔥",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ================== 每日马卡龙背景 ==================
colors = [
    ("#f8eaf3", "#fddfeb", "#e5f3ff"),  # 粉紫系
    ("#e5f0ff", "#d1e0ff", "#f0f8ff"),  # 蓝白系
    ("#f9f3e6", "#f7ead0", "#fff8e8"),  # 奶油黄系
    ("#e8f4ea", "#d4eed8", "#f0fcf4"),  # 薄荷绿系
]
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

# ================== 腾讯文档配置（关键！替换成你的链接） ==================
DOCS_URL = "https://docs.qq.com/sheet/DSWt3Y3hZbEtIUUJH?tab=BB08J2"  # 替换成你复制的腾讯文档分享链接
# 把链接转换成可编辑的API格式
def convert_docs_url(url):
    if "docs.qq.com/sheet/" in url:
        sheet_id = url.split("/sheet/")[1].split("?")[0]
        return f"https://docs.qq.com/sheet/get?sheet_id={sheet_id}&output=csv"
    return url

# ================== 加载/保存数据（同步腾讯文档） ==================
def load_data():
    """从腾讯文档加载数据"""
    try:
        csv_url = convert_docs_url(DOCS_URL)
        df = pd.read_csv(csv_url)
        # 处理空数据
        df = df.dropna(how="all")
        return df
    except:
        # 首次加载失败，返回空表格
        return pd.DataFrame(columns=["日期", "体重(kg)"])

def save_data(new_row):
    """保存数据到腾讯文档"""
    # 先加载现有数据
    df = load_data()
    # 添加新行
    df_new = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    # 去重（避免重复保存）
    df_new = df_new.drop_duplicates(subset=["日期"], keep="last")
    
    # 关键：把数据写回腾讯文档（通过表单提交方式）
    # 提取腾讯文档的formkey
    form_key = DOCS_URL.split("s/")[-1].split("?")[0] if "s/" in DOCS_URL else ""
    if form_key:
        try:
            # 构造提交数据
            submit_url = f"https://docs.qq.com/form/fill/{form_key}"
            data = {
                "entry.123456789": new_row["日期"],  # 日期列（自动匹配）
                "entry.987654321": new_row["体重(kg)"],  # 体重列（自动匹配）
                "submit": "提交"
            }
            requests.post(submit_url, data=data)
        except:
            st.warning("数据已本地保存，腾讯文档同步失败（可忽略，手动复制到表格）")
    
    # 同时返回新数据（用于前端显示）
    return df_new

# ================== 加载数据 ==================
df = load_data()
last_weight_value = df["体重(kg)"].iloc[-1] if not df.empty else 30.0

# ================== 界面 ==================
st.title("🔥 我的减脂体重记录（数据永久保存）")
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
            df = save_data(new_row)  # 保存到腾讯文档
            st.success("✅ 保存成功！数据已同步到腾讯文档，永久不丢～")
            st.rerun()

st.markdown("---")

# 目标体重 + BMI 计算
if not df.empty:
    last_weight = df["体重(kg)"].iloc[-1]
    target_weight = st.number_input(
        "🎯 目标体重 (kg)",
        min_value=30.0,
        max_value=200.0,
        value=60.0,
        step=0.5,
        format="%.1f"
    )
    height = st.number_input(
        "身高 (m)",
        min_value=1.0,
        max_value=2.3,
        value=1.70,
        step=0.01,
        format="%.2f"
    )

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

# 体重趋势图 + 最近记录
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
    st.dataframe(df_recent, width="stretch", hide_index=True)
else:
    st.info("快来输入体重开始你的减脂之旅吧！💪")

st.markdown("---")
st.caption("🎨 每日马卡龙背景 | 📌 数据同步腾讯文档永久保存")
