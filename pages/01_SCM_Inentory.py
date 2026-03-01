import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import time
import google.generativeai as genai

# --- 1. ページ設定 & 初期化 ---
st.set_page_config(
    page_title="Global Management Cockpit - SCM",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# API設定
API_KEY = ""  
if API_KEY:
    genai.configure(api_key=API_KEY)

# セッションステート初期化
if "selected_location" not in st.session_state: st.session_state.selected_location = "US West Plant"
if "sim_transfer" not in st.session_state: st.session_state.sim_transfer = 42

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant", 
        "content": "**System Online.** 経営参謀エージェントです。全拠点のデータを統合監視中。\n\n🚨 **異常検知**: 米国西海岸工場 (US West Plant) にて部材の在庫枯渇リスク。\nマップ上の赤ピンをクリックして詳細をドリルダウンしてください。"
    })

# --- 2. デザインシステム (Common CSS) ---
st.markdown("""
    <style>
        .stApp { background-color: #0B1120; color: #F8FAFC; }
        div.stButton > button.nav-btn { height: 40px !important; font-size: 1rem !important; }
        [data-testid="stSidebar"] { background-color: #0F172A; border-right: 1px solid #1E293B; }
        div[data-testid="stMetric"] { background-color: transparent !important; border: none !important; padding: 0 !important; }
        div[data-testid="stMetricValue"] { color: #F8FAFC !important; font-size: 2.5rem !important; font-weight: 700 !important; text-shadow: 0 0 20px rgba(255,255,255,0.1); }
        div[data-testid="stMetricLabel"] > label { color: #94A3B8 !important; }
        .js-plotly-plot .plotly .main-svg, [data-testid="stDataFrame"] { background: transparent !important; }
        div[data-testid="stChatMessage"] { background-color: transparent !important; }
        div[data-testid="stChatMessageContent"] p { color: #F1F5F9 !important; }
        .drilldown-container { background: linear-gradient(145deg, #1E293B, #0F172A); border: 1px solid #334155; border-radius: 12px; padding: 25px; margin-top: 10px; }
    </style>
""", unsafe_allow_html=True)

PLOT_CONFIG = {'displayModeBar': False}

# --- 3. データ層 ---
locations_data = {
    "Location": ["US West Plant", "Mexico Plant", "SE Asia Hub", "EU Hub"],
    "lat": [34.05, 19.43, 13.75, 51.16],
    "lon": [-118.24, -99.13, 100.50, 10.45],
    "Status": ["Critical Risk", "Source", "Warning", "Normal"],
    "Detail": ["在庫枯渇リスク (残1.2日)", "余剰在庫あり (即納可)", "物流遅延兆候", "稼働率 98%"],
    "Color": ["#EF4444", "#3B82F6", "#F59E0B", "#10B981"],
    "Size": [25, 20, 15, 12]
}
df_locations = pd.DataFrame(locations_data)

sku_data = {
    "倉庫": ["WH-A (メイン組立)", "WH-A (メイン組立)", "WH-B (電装部品)", "WH-C (外装)"],
    "部材(SKU)": ["高トルクサーボモーター", "制御基板 X-100", "光センサーモジュール", "チタン合金フレーム"],
    "需要標準偏差(σ)": [2.5, 15.2, 5.8, 1.5],
    "基準在庫(AI設定)": [50, 200, 30, 10], 
    "現在庫": [8, 195, 35, 12],
    "ステータス": ["🔴 欠品寸前", "🟡 警告", "🔵 余剰", "🟢 正常"]
}
df_sku = pd.DataFrame(sku_data)

# --- 4. AI機能 ---
def agent_response(user_input):
    if not API_KEY:
        time.sleep(1)
        return "⚠️ APIキー未設定 (Demo Mode)\n\n**AI分析インサイト**:\n米国西海岸工場の「高トルクサーボモーター」は、需要の標準偏差(σ=2.5)から算出された基準在庫(50)に対し、現在庫(8)と致命的な水準です。\nこのままではラインが停止し、**最大$420,000の機会損失**が発生します。\n\n**推奨アクション**:\nマップ上で青色(Source)となっている「Mexico Plant」には同部品の余剰在庫があります。緊急空輸コスト($21,000)を支払ってでも、直ちに42個の在庫転送(STO)を実行し、限界利益を確保してください。"
    try:
        model = genai.GenerativeModel("gemini-1.5-pro")
        response = model.generate_content(user_input)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

# --- 5. メイン画面描画 ---
col_nav, col_title, col_user = st.columns([1, 4, 2])
with col_nav:
    st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
    if st.button("← Back to Portal", key="back_btn"):
        st.switch_page("Top_Page.py")
    st.markdown('</div>', unsafe_allow_html=True)
with col_title:
    st.markdown("<h1 style='margin: 0; font-size: 2.2rem;'>Global Supplychain Management</h1><span style='color: #10B981; font-size: 0.9rem;'>● Live Monitoring Active</span>", unsafe_allow_html=True)
with col_user:
    st.markdown("<div style='text-align: right; color: #94A3B8;'><span style='font-size: 0.8rem;'>HQ_
