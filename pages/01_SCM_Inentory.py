import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import time
import google.generativeai as genai

st.set_page_config(page_title="Global Management Cockpit - SCM", page_icon="🌐", layout="wide", initial_sidebar_state="collapsed")

API_KEY = ""  
if API_KEY:
    genai.configure(api_key=API_KEY)

if "selected_location" not in st.session_state: st.session_state.selected_location = "US West Plant"
if "sim_transfer" not in st.session_state: st.session_state.sim_transfer = 42
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant", 
        "content": "**System Online.** 経営参謀エージェントです。全拠点のデータを統合監視中。\n\n🚨 **異常検知**: 米国西海岸工場 (US West Plant) にて部材の在庫枯渇リスク。\nマップ上の赤ピンをクリックして詳細をドリルダウンしてください。"
    }]

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

col_nav, col_title, col_user = st.columns([1, 4, 2])
with col_nav:
    st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
    if st.button("← Back to Portal", key="back_btn_inv"):
        st.switch_page("Top_Page.py")
    st.markdown('</div>', unsafe_allow_html=True)
with col_title:
    st.markdown("<h1 style='margin: 0; font-size: 2.2rem;'>Global Supplychain Management</h1><span style='color: #10B981; font-size: 0.9rem;'>● Live Monitoring Active</span>", unsafe_allow_html=True)
with col_user:
    st.markdown("<div style='text-align: right; color: #94A3B8;'><span style='font-size: 0.8rem;'>HQ_Admin</span><br><span style='font-size: 1.2rem; color: white; font-weight: bold;'>Level 5 Access</span></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

col_main, col_chat = st.columns([2.2, 1], gap="large")

with col_main:
    k1, k2, k3 = st.columns(3)
    with k1: st.metric("💰 グローバル調達総額 (YTD)", "¥ 128.4 B", "-2.4% (Cost Reduction)")
    with k2: st.metric("📦 在庫回転日数 (Global Avg)", "42.5 Days", "3.2 Days (Worsening)", delta_color="inverse")
    with k3: st.metric("🚨 供給リスク検知", "3 Alerts", "Severe", delta_color="inverse")

    st.markdown("<br>", unsafe_allow_html=True)
    
    c_map_title, c_map_nav = st.columns([3, 1])
    c_map_title.subheader("🗺️ Supply Chain Network Topology")
    
    idx = df_locations["Location"].tolist().index(st.session_state.selected_location) if st.session_state.selected_location in df_locations["Location"].tolist() else 0
    manual_loc = c_map_nav.selectbox("🎯 拠点を選択", df_locations["Location"].tolist(), index=idx, label_visibility="collapsed")

    fig = px.scatter_geo(
        df_locations, lat="lat", lon="lon", color="Status", size="Size",
        hover_name="Location", hover_data={"Detail": True, "lat": False, "lon": False, "Size": False}, custom_data=["Location"],
        color_discrete_map={"Critical Risk": "#EF4444", "Source": "#3B82F6", "Warning": "#F59E0B", "Normal": "#10B981"},
        projection="natural earth",
    )
    fig.update_traces(marker=dict(line=dict(width=2, color="rgba(255,255,255,0.8)")))
    fig.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0}, height=380, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        geo=dict(bgcolor="rgba(0,0,0,0)", showland=True, landcolor="#1E293B", showocean=True, oceancolor="#0B1120", showcountries=True, countrycolor="#334155", showcoastlines=False),
        legend=dict(y=0.1, x=0, font=dict(color="white"), bgcolor="rgba(0,0,0,0)")
    )
    
    try:
        event = st.plotly_chart(fig, on_select="rerun", selection_mode="points", use_container_width=True, key="map_select", config=PLOT_CONFIG)
        clicked_loc = None
        if event and hasattr(event, "selection") and event.selection.get("points"):
            clicked_loc = event.selection["points"][0]["customdata"][0]
        elif isinstance(event, dict) and event.get("selection") and event["selection"].get("points"):
            clicked_loc = event["selection"]["points"][0]["customdata"][0]
        
        if clicked_loc and clicked_loc != st.session_state.selected_location:
            st.session_state.selected_location = clicked_loc
            st.rerun()
    except Exception:
        st.plotly_chart(fig, use_container_width=True, config=PLOT_CONFIG)
        
    if manual_loc != st.session_state.selected_location:
        st.session_state.selected_location = manual_loc
        st.rerun()

with col_chat:
    st.markdown("### 🧠 AI Executive Agent")
    chat_container = st.container(height=520)
    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"], avatar="🦅" if msg["role"] == "assistant" else "👤"):
                st.markdown(msg["content"])

    if prompt := st.chat_input("Ask agent..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with chat_container:
            with st.chat_message("user", avatar="👤"): st.markdown(prompt)
            with st.chat_message("assistant", avatar="🦅"):
                response = agent_response(prompt)
                st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

if st.session_state.selected_location:
    st.markdown("<div class='drilldown-container'>", unsafe_allow_html=True)
    st.markdown(f"### 📍 拠点ドリルダウン: <span style='color:#60A5FA;'>{st.session_state.selected_location}</span>", unsafe_allow_html=True)
    
    if st.session_state.selected_location == "US West Plant":
        col_tbl, col_sim = st.columns([1, 1.2], gap="large")
        
        with col_tbl:
            st.markdown("#### 1. 倉庫・部材(SKU) 在庫ステータス")
            st.caption("統計的需要ブレ(σ)からAIが自動算出した基準在庫との乖離をモニタリング")
            
            def highlight_status(val):
                color = '#EF4444' if '欠品寸前' in val else '#F59E0B' if '警告' in val else '#3B82F6' if '余剰' in val else '#10B981'
                return f'color: {color}; font-weight: bold;'
            
            st.dataframe(df_sku.style.map(highlight_status, subset=['ステータス']), use_container_width=True, hide_index=True)
            
        with col_sim:
            st.markdown("#### 2. 機会損失 vs 輸送コスト シミュレーター")
            st.caption("対象: [高トルクサーボモーター] | 融通元: [Mexico Plant (青色ピン: 余剰あり)]")
            
            shortage_qty = 42 
            opp_loss_per_unit = 10000 
            transfer_cost_per_unit = 500 
            
            st.session_state.sim_transfer = st.slider("✈️ Mexico拠点からの緊急転送数 (個)", 0, 60, st.session_state.sim_transfer, 1)
            
            effective_transfer = min(st.session_state.sim_transfer, shortage_qty) 
            base_loss = -(shortage_qty * opp_loss_per_unit) 
            transfer_cost = -(st.session_state.sim_transfer * transfer_cost_per_unit) 
            recovered_profit = effective_transfer * opp_loss_per_unit 
            net_impact = base_loss + transfer_cost + recovered_profit 
            
            df_wf = pd.DataFrame({
                "Factor": ["想定機会損失額<br>(放置した場合)", "機会損失の回避<br>(売上確保: +)", "緊急空輸コスト<br>(費用増: -)", "純利益への影響<br>(Net Profit)"],
                "Amount": [base_loss, recovered_profit, transfer_cost, net_impact],
                "Measure": ["absolute", "relative", "relative", "total"]
            })
            
            fig_wf = go.Figure(go.Waterfall(
                name="Impact", orientation="v", measure=df_wf["Measure"], x=df_wf["Factor"], y=df_wf["Amount"],
                text=[f"${x/1000:+.1f}k" for x in df_wf["Amount"]], textposition="outside",
                connector={"line":{"color":"#94A3B8"}},
                decreasing={"marker":{"color":"#EF4444"}}, increasing={"marker":{"color":"#10B981"}},
                totals={"marker":{"color":"#3B82F6" if net_impact >= 0 else "#EF4444"}}
            ))
            fig_wf.update_layout(height=280, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#F8FAFC"), margin=dict(t=30, b=10), yaxis=dict(title="USD ($)", gridcolor="#334155"))
            st.plotly_chart(fig_wf, use_container_width=True, config=PLOT_CONFIG)
            
            _, c_btn = st.columns([1, 2])
            btn_type = "primary" if st.session_state.sim_transfer > 0 else "secondary"
            if c_btn.button(f"⚡ ERPへ在庫転送指示(STO)を書き戻し", type=btn_type, use_container_width=True):
                if st.session_state.sim_transfer > 0:
                    with st.spinner("Connecting to SAP S/4HANA... Generating STO..."): time.sleep(1.2)
                    st.success(f"✅ システム反映完了: Mexico ➔ US West へ {st.session_state.sim_transfer}個の在庫転送指示(STO)が発行されました。")
                else:
                    st.error("転送数を1以上設定してください。")
    else:
        st.info(f"📍 {st.session_state.selected_location} の詳細データは現在正常（またはデモ環境でのアクセス制限中）です。赤ピンの『US West Plant』をクリックしてください。")
        
    st.markdown("</div>", unsafe_allow_html=True)
