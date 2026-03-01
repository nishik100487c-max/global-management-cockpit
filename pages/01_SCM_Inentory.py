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

# API設定 (空欄のままで安全なデモモードが作動します)
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
        
        /* トップメニューボタン */
        div.stButton > button.nav-btn { height: 40px !important; font-size: 1rem !important; }
        
        [data-testid="stSidebar"] { background-color: #0F172A; border-right: 1px solid #1E293B; }
        div[data-testid="stMetric"] { background-color: transparent !important; border: none !important; padding: 0 !important; }
        div[data-testid="stMetricValue"] { color: #F8FAFC !important; font-size: 2.5rem !important; font-weight: 700 !important; text-shadow: 0 0 20px rgba(255,255,255,0.1); }
        div[data-testid="stMetricLabel"] > label { color: #94A3B8 !important; }
        .js-plotly-plot .plotly .main-svg, [data-testid="stDataFrame"] { background: transparent !important; }
        div[data-testid="stChatMessage"] { background-color: transparent !important; }
        div[data-testid="stChatMessageContent"] p { color: #F1F5F9 !important; }
        
        /* ドリルダウン領域の装飾 */
        .drilldown-container {
            background: linear-gradient(145deg, #1E293B, #0F172A);
            border: 1px solid #334155; border-radius: 12px; padding: 25px; margin-top: 10px;
        }
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
    "基準在庫(AI設定)": [50, 200, 3