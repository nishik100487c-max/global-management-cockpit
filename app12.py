import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import time

# --- 1. ページ設定 & 初期化 ---
st.set_page_config(page_title="Global Management Cockpit - Crisis Mode", page_icon="🌍", layout="wide", initial_sidebar_state="collapsed")

# 状態管理
if "page" not in st.session_state: st.session_state.page = "supply_chain"
if "oil_price" not in st.session_state: st.session_state.oil_price = 115.0
if "reroute_ratio" not in st.session_state: st.session_state.reroute_ratio = 40.0
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "⚠️ **CRISIS ALERT**\n\nロイター通信等の外部ニュースAPIおよび海事データ(AIS)より、**ホルムズ海峡の事実上の封鎖**を検知しました。欧州および北米東海岸向けの物流リードタイムに甚大な影響が出始めています。右側のタブから影響シミュレーションを実行してください。"
    }]

# --- 2. デザインシステム (Common CSS) ---
st.markdown("""
    <style>
        .stApp { background-color: #0B1120; color: #F8FAFC; }
        .stTabs [data-baseweb="tab-list"] { gap: 10px; border-bottom: 2px solid #334155; padding-bottom: 5px; }
        .stTabs [data-baseweb="tab"] { background-color: transparent; border: none; color: #94A3B8; font-weight: bold; font-size: 1.1rem; padding: 10px 20px; }
        .stTabs [aria-selected="true"] { color: #EF4444 !important; border-bottom: 3px solid #EF4444 !important; }
        .js-plotly-plot .plotly .main-svg { background: transparent !important; }
        div[data-testid="stChatMessage"] { background-color: transparent !important; }
        div[data-testid="stChatMessageContent"] p { color: #F1F5F9 !important; line-height: 1.6;}
        
        /* サマリーパネル (アラート用赤基調) */
        .summary-panel { background: linear-gradient(145deg, #450a0a, #1E293B); border-left: 5px solid #EF4444; padding: 18px 20px; border-radius: 8px; margin-bottom: 15px; border: 1px solid #7f1d1d; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
        .summary-panel h4 { margin-top: 0; color: #F8FAFC; margin-bottom: 10px; font-size: 1.15rem; }
        
        /* 要因割合 プログレスバー */
        .factor-bar-container { display: flex; height: 26px; border-radius: 4px; overflow: hidden; margin: 15px 0; border: 1px solid #334155; font-size: 0.85rem; font-weight: bold;}
        .factor-ext { width: 85%; background: linear-gradient(90deg, #EF4444, #991B1B); display: flex; align-items: center; justify-content: center; color: #fff; }
        .factor-int { width: 15%; background: linear-gradient(90deg, #F59E0B, #B45309); display: flex; align-items: center; justify-content: center; color: #fff; }

        /* 出典(エビデンス)カード */
        .source-card { background-color: #1E293B; border-left: 4px solid #3B82F6; padding: 12px 15px; margin-bottom: 12px; border-radius: 4px 8px 8px 4px; border: 1px solid #334155; }
        .source-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; font-size: 0.85rem; color: #94A3B8; border-bottom: 1px solid #334155; padding-bottom: 4px; }
        .source-body { font-size: 0.9rem; color: #CBD5E1; font-style: italic; line-height: 1.5; }
        .tag-ext { border: 1px solid #EF4444; color: #EF4444; background: #2A0909; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem;}
        .tag-int { border: 1px solid #F59E0B; color: #F59E0B; background: #2A1A09; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem;}
    </style>
""", unsafe_allow_html=True)

PLOT_CONFIG = {'displayModeBar': False}

# --- 3. データ層 ---
locations_data = {
    "Location": ["Strait of Hormuz", "EU Hub (Rotterdam)", "US East (Newark)", "APAC Hub (Singapore)", "Cape of Good Hope"],
    "lat": [26.56, 51.92, 40.71, 1.35, -34.35],
    "lon": [56.25, 4.47, -74.17, 103.81, 18.47],
    "Status": ["Critical Blockade", "Warning (Low Inv)", "Warning (Low Inv)", "Normal (Source)", "Alt Route"],
    "Detail": ["軍事衝突による海峡封鎖", "到着遅延: +18日", "到着遅延: +21日", "代替在庫引き当て可能", "喜望峰迂回ルート（+14日）"],
    "Color": ["#EF4444", "#F59E0B", "#F59E0B", "#10B981", "#3B82F6"],
    "Size": [30, 20, 20, 15, 12]
}
df_locations = pd.DataFrame(locations_data)

# --- 4. AI機能 (固定HTML出力) ---
def get_ai_analysis_html():
    return """
**【地政学リスク：中東情勢悪化に伴う影響分析】**
外部ニュースAPI（ロイター/Bloomberg）、海事データ（AIS）、および自社のERPパイプラインを統合解析しました。

<div class="factor-bar-container">
    <div class="factor-ext">外部要因 (地政学・マクロ経済) 85%</div>
    <div class="factor-int">内部要因 (調達網の脆弱性) 15%</div>
</div>

**🌪️ 外部要因（コントロール不可）**
* **ホルムズ海峡の封鎖:** 米国による軍事ストライキの報復措置として、イランがホルムズ海峡の航行を遮断。スエズ運河経由の欧州・北米向けルートが物理的に停止。
* **原油価格の歴史的高騰:** WTI原油が一時$115/bblを突破。バンカー油（船舶燃料）のサーチャージが前週比+300%に急騰。

**🏭 内部要因（コントロール可能・改善余地あり）**
* **単一ソース依存のリスク:** EUハブ向けの主要化学部材の65%が中東のプラントに依存しており、代替調達先（デュアルソーシング）の事前登録が完了していない。

---
###### 📚 判断根拠（ビジネスオントロジー抽出データ）

<div class="source-card" style="border-left-color: #EF4444;">
    <div class="source-header">
        <span>🌐 <b>Reuters API Feed</b> (Real-time)</span>
        <span class="tag-ext">外部要因</span>
    </div>
    <div class="source-body">
        「FLASH: イラン革命防衛隊、ホルムズ海峡の全面封鎖を宣言。米国の軍事施設攻撃に対する報復措置。国際海運各社はアラビア海への進入を即座に停止。」
    </div>
</div>

<div class="source-card" style="border-left-color: #F59E0B;">
    <div class="source-header">
        <span>📑 <b>グローバルSCMリスク管理会議 議事録</b> (2日前)</span>
        <span class="tag-int">内部要因</span>
    </div>
    <div class="source-body">
        「（調達部）中東情勢の緊迫化を受け、EU向けの部材調達をAPAC（シンガポールハブ）へ切り替える準備を進めているが、現地サプライヤーの品質監査プロセスが完了しておらず、即時切り替えにボトルネックが生じている。」
    </div>
</div>

💡 **推奨アクション**
中央の「📉 2. 収益圧迫シミュレーション」タブを開き、原油高によるコスト増と、APACからの代替航空便・喜望峰迂回ルートへの切り替え（Rerouting）による影響額を算定してください。その後、ERPへ計画変更をコミットします。
"""

# --- 5. メイン画面描画 ---
def render_crisis_dashboard():
    # ヘッダー
    col_nav, col_title = st.columns([1, 6])
    col_nav.markdown('<div style="margin-top:10px;"><button style="background:transparent; border:1px solid #334155; color:#94A3B8; padding:5px 15px; border-radius:5px;">← Portal</button></div>', unsafe_allow_html=True)
    col_title.markdown("<h1 style='margin: 0; font-size: 2.2rem; color: #EF4444;'>🚨 Global Cockpit: Middle East Crisis Mode</h1><span style='color: #F59E0B; font-size: 0.9rem;'>● Real-time Ontology Sync Active</span>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # エグゼクティブサマリー
    st.markdown("""
    <div class="summary-panel">
        <h4>⚠️ 緊急事態宣言: 中東物流ルート遮断および原油価格高騰</h4>
        <p style="margin-bottom: 0; color: #CBD5E1; font-size: 0.95rem; line-height: 1.6;">
            米国とイランの軍事衝突をトリガーに、ホルムズ海峡が封鎖されました。現在、当社手配のコンテナ船12隻がアラビア海で足止めされており、欧州・北米の生産ラインに2週間以内の停止リスクが発生しています。同時に、原油価格（WTI）の高騰により、年間の輸送コストが大幅に上振れする見込みです。
        </p>
    </div>
    """, unsafe_allow_html=True)

    # メインレイアウト（左：ダッシュボード機能、右：AI）
    col_dash, col_chat = st.columns([2.2, 1], gap="large")

    with col_dash:
        tab_map, tab_sim, tab_act = st.tabs(["🌍 1. グローバル影響俯瞰", "📉 2. 収益圧迫・原油高シミュレーション", "⚡ 3. 対策実行 (ERP連携)"])

        # === タブ1: マップ ===
        with tab_map:
            st.markdown("<br>", unsafe_allow_html=True)
            k1, k2, k3 = st.columns(3)
            k1.metric("WTI 原油価格 (リアルタイム)", "$ 115.4 /bbl", "▲ $35.2 (急騰)", delta_color="inverse")
            k2.metric("影響を受けるコンテナ船", "12 隻", "総額 $420M 相当")
            k3.metric("EU工場 ライン停止までの猶予", "14 日", "▼ 7日 (悪化)", delta_color="inverse")

            fig = px.scatter_geo(
                df_locations, lat="lat", lon="lon", color="Status", size="Size",
                hover_name="Location", text="Location",
                color_discrete_map={"Critical Blockade": "#EF4444", "Warning (Low Inv)": "#F59E0B", "Normal (Source)": "#10B981", "Alt Route": "#3B82F6"},
                projection="natural earth"
            )
            # 航路のラインを描画
            fig.add_trace(go.Scattergeo(lon=[56.25, 4.47], lat=[26.56, 51.92], mode="lines", line=dict(width=2, color="#EF4444", dash="dot"), name="Blocked Route (EU)"))
            fig.add_trace(go.Scattergeo(lon=[103.81, 18.47, 4.47], lat=[1.35, -34.35, 51.92], mode="lines", line=dict(width=2, color="#3B82F6"), name="Alt Route (Cape)"))

            fig.update_traces(textposition='bottom center', textfont=dict(color="white"))
            fig.update_layout(
                margin={"r":0,"t":0,"l":0,"b":0}, height=450, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                geo=dict(bgcolor="rgba(0,0,0,0)", showland=True, landcolor="#1E293B", showocean=True, oceancolor="#0B1120", showcountries=True, countrycolor="#334155", showcoastlines=False),
                legend=dict(y=0.1, x=0, font=dict(color="white"), bgcolor="rgba(0,0,0,0)")
            )
            st.plotly_chart(fig, use_container_width=True, config=PLOT_CONFIG)

        # === タブ2: シミュレーション ===
        with tab_sim:
            st.markdown("### 🎛️ What-If シミュレーション")
            st.caption("マクロ指標（原油価格）の変動と、現場のオペレーション変更（迂回ルートへの切り替え比率）が、今四半期のEBITDAに与えるインパクトをリアルタイムに計算します。")
            
            c1, c2 = st.columns(2, gap="large")
            st.session_state.oil_price = c1.slider("🛢️ 予想原油価格帯 ($/bbl)", 70.0, 150.0, st.session_state.oil_price, 5.0)
            st.session_state.reroute_ratio = c2.slider("🚢 喜望峰・航空便への切り替え比率 (%)", 0.0, 100.0, st.session_state.reroute_ratio, 5.0)

            # ロジック計算
            base_ebitda = 120.0 
            oil_penalty = -((st.session_state.oil_price - 75.0) * 0.4) if st.session_state.oil_price > 75.0 else 0
            wait_ratio = (100.0 - st.session_state.reroute_ratio) / 100.0
            opportunity_loss = -(wait_ratio * 45.0) 
            reroute_cost = -(st.session_state.reroute_ratio / 100.0 * 15.0)
            
            simulated_ebitda = base_ebitda + oil_penalty + opportunity_loss + reroute_cost
            
            df_wf = pd.DataFrame({
                "Factor": ["Base Plan<br>(初期計画)", "原油高騰インパクト<br>(輸送費増)", "ライン停止・機会損失<br>(待機した場合)", "迂回・航空便手配<br>(追加手配コスト)", "Simulated<br>EBITDA"],
                "Amount": [base_ebitda, oil_penalty, opportunity_loss, reroute_cost, simulated_ebitda],
                "Measure": ["absolute", "relative", "relative", "relative", "total"]
            })
            
            fig_wf = go.Figure(go.Waterfall(
                name="EBITDA", orientation="v", measure=df_wf["Measure"], x=df_wf["Factor"], y=df_wf["Amount"],
                text=[f"{x:+.1f}M" if 0<i<4 else f"{x:.1f}M" for i, x in enumerate(df_wf["Amount"])],
                textposition="outside", connector={"line":{"color":"#94A3B8"}},
                decreasing={"marker":{"color":"#EF4444"}}, increasing={"marker":{"color":"#10B981"}},
                totals={"marker":{"color":"#3B82F6" if simulated_ebitda >= 80 else "#EF4444"}}
            ))
            fig_wf.update_layout(height=350, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#F8FAFC"), margin=dict(t=30, b=20), yaxis=dict(title="EBITDA ($M)", gridcolor="#334155"))
            st.plotly_chart(fig_wf, use_container_width=True, config=PLOT_CONFIG)

        # === タブ3: 対策実行 ===
        with tab_act:
            st.markdown("### ⚡ アクション実行とERP連携")
            st.info(f"現在のシミュレーション結果: **切り替え比率 {st.session_state.reroute_ratio}%** / 着地見込 **${simulated_ebitda:.1f}M**")
            
            st.markdown("#### 承認待ちのトランザクション")
            st.markdown(f"""
            1. **[SAP S/4HANA]** EU工場向け発注残(PO)の輸送ルートを「スエズ経由」から「喜望峰迂回ルート」へ変更 ({st.session_state.reroute_ratio}%分)
            2. **[SAP S/4HANA]** APAC(Singapore)ハブからEU工場への緊急航空便の在庫転送指示(STO)を発行
            3. **[SAP BPC]** 当四半期の予算マスタに対し、輸送費高騰分のアロケーションを再計算し上書き
            """)
            
            st.markdown("<br>", unsafe_allow_html=True)
            _, c_btn, _ = st.columns([1, 2, 1])
            if c_btn.button("🚀 Execute Decisions (上記計画をERPへ書き戻し)", type="primary", use_container_width=True):
                with st.spinner("Executing API Calls to SAP Instances..."):
                    time.sleep(2.0)
                st.success("✅ **Committed:** 全ての基幹システムに対してトランザクションが正常に発行されました。各拠点の担当者へアラートメールが送信されました。")

    # === 右側: AIエージェント ===
    with col_chat:
        st.markdown("### 🧠 Ontology Agent")
        st.markdown("<span style='color:#EF4444; font-size: 0.85rem; font-weight: bold;'>● Crisis Response Mode</span>", unsafe_allow_html=True)
        st.markdown("---")
        
        chat_container = st.container(height=650)
        with chat_container:
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"], avatar="🦅" if msg["role"] == "assistant" else "👤"):
                    st.markdown(msg["content"], unsafe_allow_html=True)

        # ユーザー入力に対する応答（固定）
        if prompt := st.chat_input("何が起きているか分析して..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with chat_container:
                with st.chat_message("user", avatar="👤"): st.markdown(prompt)
                with st.chat_message("assistant", avatar="🦅"):
                    # APIを使わず、待機演出のみでそれっぽく見せる
                    with st.spinner("ニュースストリーム・海事データ・ERPを統合解析中..."):
                        time.sleep(1.5)
                    response = get_ai_analysis_html()
                    st.markdown(response, unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": response})

render_crisis_dashboard()