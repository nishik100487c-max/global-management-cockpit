import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import time

st.set_page_config(page_title="Corporate Strategy", page_icon="📊", layout="wide", initial_sidebar_state="collapsed")

if "sim_vc" not in st.session_state: st.session_state.sim_vc = 0.0
if "sim_promo" not in st.session_state: st.session_state.sim_promo = 0.0
if "sim_fix" not in st.session_state: st.session_state.sim_fix = 0.0
if "selected_region" not in st.session_state: st.session_state.selected_region = "MLE" 
if "prev_sel_l" not in st.session_state: st.session_state.prev_sel_l = None
if "prev_sel_r" not in st.session_state: st.session_state.prev_sel_r = None

if "messages_strategy" not in st.session_state:
    st.session_state.messages_strategy = [{
        "role": "assistant",
        "content": "**System Online.** 経営参謀エージェントです。公式ドキュメント（レポート・会議録等）を接続したビジネスオントロジー（構造モデル）との同期を完了しました。\n\n⚠️ **異常検知:** MLE地域のHardware事業において、利益(EBITDA)が計画比で大幅未達（計画25.0Mに対し実績見込5.0M）となっています。要因の深掘り分析を実行しますか？"
    }]

# --- Mac-like モダンデザイン & Plotly点滅アニメーション ---
st.markdown("""
    <style>
        .stApp { background-color: #0B1120; color: #F8FAFC; }
        div.stButton > button.nav-btn { height: 40px !important; font-size: 1rem !important; }
        
        /* Plotlyの赤いバー（未達）を最初の数秒だけ点滅させるアニメーション */
        @keyframes urgentBlink {
            0% { fill-opacity: 1; stroke: rgba(239, 68, 68, 1); stroke-width: 0; }
            30% { fill-opacity: 0.3; stroke: rgba(255, 100, 100, 1); stroke-width: 5px; filter: drop-shadow(0 0 10px rgba(239,68,68,0.8)); }
            100% { fill-opacity: 1; stroke: transparent; stroke-width: 0; }
        }
        /* グラフ描画後に赤いバーだけを狙い撃ち (3回点滅して自然に止まる) */
        g.point path[style*="fill: rgb(239, 68, 68)"],
        g.point path[style*="fill: #EF4444"] {
            animation: urgentBlink 1.2s ease-in-out 3;
            transform-origin: center;
        }

        /* macOS風 グラスモーフィズム・サマリーパネル */
        .mac-panel {
            background: rgba(30, 41, 59, 0.6);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
        }
        .mac-panel h4 { margin-top: 0; color: #F8FAFC; margin-bottom: 20px; font-size: 1.3rem; font-weight: 700; letter-spacing: 0.5px; }
        .mac-list { list-style: none; padding: 0; margin: 0; }
        .mac-list li { margin-bottom: 16px; display: flex; align-items: flex-start; line-height: 1.6; color: #E2E8F0; font-size: 0.95rem; }
        .mac-list li:last-child { margin-bottom: 0; }
        
        /* Mac風 ピル型バッジ */
        .badge {
            display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 0.7rem; font-weight: 700; letter-spacing: 0.8px; text-transform: uppercase; margin-right: 14px; white-space: nowrap; border: 1px solid transparent; box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
        .badge-success { background: rgba(16, 185, 129, 0.15); color: #34D399; border-color: rgba(16, 185, 129, 0.3); }
        .badge-alert { background: rgba(239, 68, 68, 0.15); color: #F87171; border-color: rgba(239, 68, 68, 0.4); animation: subtlePulse 2s infinite; }
        .badge-info { background: rgba(59, 130, 246, 0.15); color: #60A5FA; border-color: rgba(59, 130, 246, 0.3); }

        @keyframes subtlePulse {
            0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4); }
            70% { box-shadow: 0 0 0 6px rgba(239, 68, 68, 0); }
            100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
        }

        .kpi-card { background: linear-gradient(145deg, #1E293B, #0F172A); border: 1px solid #334155; padding: 20px; border-radius: 12px; text-align: center; }
        .kpi-title { color: #94A3B8; font-size: 1.1rem; font-weight: bold; margin-bottom: 5px; }
        .kpi-value { color: #F8FAFC; font-size: 2.6rem; font-weight: 800; margin-bottom: 12px; line-height: 1.1; }
        .delta-green { color: #10B981; } .delta-red { color: #EF4444; }
        .stTabs [data-baseweb="tab-list"] { gap: 10px; border-bottom: 2px solid #334155; padding-bottom: 5px; }
        .stTabs [data-baseweb="tab"] { background-color: transparent; border: none; color: #94A3B8; font-weight: bold; font-size: 1.1rem; padding: 10px 15px; }
        .stTabs [aria-selected="true"] { color: #60A5FA !important; border-bottom: 3px solid #3B82F6 !important; }
        .quad-title { font-size: 1.2rem; font-weight: bold; color: #E2E8F0; text-align: center; border-bottom: 2px solid #334155; padding-bottom: 8px; margin-bottom: 15px; }
        .quad-subtitle { font-size: 1.05rem; font-weight: bold; color: #94A3B8; margin-top: 15px; }
        .js-plotly-plot .plotly .main-svg { background: transparent !important; }
        div[data-testid="stChatMessage"] { background-color: transparent !important; }
        div[data-testid="stChatMessageContent"] p { color: #F1F5F9 !important; line-height: 1.6; }
        .factor-bar-container { display: flex; height: 26px; border-radius: 4px; overflow: hidden; margin: 15px 0; border: 1px solid #334155; font-size: 0.85rem; font-weight: bold; box-shadow: 0 2px 4px rgba(0,0,0,0.2);}
        .factor-ext { width: 65%; background: linear-gradient(90deg, #F59E0B, #D97706); display: flex; align-items: center; justify-content: center; color: #fff; }
        .factor-int { width: 35%; background: linear-gradient(90deg, #EF4444, #B91C1C); display: flex; align-items: center; justify-content: center; color: #fff; }
        .source-card { background-color: #1E293B; border-left: 4px solid #3B82F6; padding: 12px 15px; margin-bottom: 12px; border-radius: 4px 8px 8px 4px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.3); }
        .source-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; font-size: 0.85rem; color: #94A3B8; border-bottom: 1px solid #334155; padding-bottom: 4px; }
        .source-body { font-size: 0.9rem; color: #CBD5E1; font-style: italic; line-height: 1.5; }
        .source-tag { background-color: #0F172A; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; border: 1px solid #334155; color: #E2E8F0; }
        .tag-ext { border-color: #F59E0B; color: #F59E0B; }
        .tag-int { border-color: #EF4444; color: #EF4444; }
    </style>
""", unsafe_allow_html=True)

# 地域名の変更 (North America -> MLA, EMEA -> MLE, APAC -> MLAP, LatAm -> Japan)
regions = ["MLA", "MLE", "MLAP", "Japan"]
bizs = ["Hardware", "Rental & O&M", "Solutions"]
reg_rev_plan = [460, 310, 290, 150]; reg_rev_act = [450, 300, 305, 140]; reg_rev_py = [420, 280, 260, 130]
reg_ebitda_plan = [68, 45, 40, 20];  reg_ebitda_act = [65, 25, 42, 18];  reg_ebitda_py = [60, 42, 35, 15]

biz_data = {
    "All":           {"r_p":[640, 370, 200], "r_a":[630, 380, 195], "r_py":[580, 330, 180], "e_p":[78, 70, 25], "e_a":[48, 77, 20], "e_py":[66, 64, 22]},
    "MLA":           {"r_p":[250, 130, 80],  "r_a":[245, 135, 70],  "r_py":[230, 120, 70],  "e_p":[35, 25, 8],  "e_a":[34, 25, 6],  "e_py":[30, 22, 8]},
    "MLE":           {"r_p":[160, 100, 50],  "r_a":[150, 105, 45],  "r_py":[150, 90, 40],   "e_p":[25, 15, 5],  "e_a":[5,  18, 2],  "e_py":[20, 15, 6]},
    "MLAP":          {"r_p":[150, 90, 50],   "r_a":[160, 95, 50],   "r_py":[130, 80, 50],   "e_p":[18, 15, 7],  "e_a":[20, 16, 6],  "e_py":[15, 14, 6]},
    "Japan":         {"r_p":[80, 50, 20],    "r_a":[75, 45, 20],    "r_py":[70, 40, 20],    "e_p":[10, 8, 2],   "e_a":[8,  8, 2],   "e_py":[8,  5, 2]}
}

def draw_bar_in_bar_monthly(metric):
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    plan = np.linspace(100, 150, 12) if metric == "Revenue" else np.linspace(15, 25, 12)
    py = plan * 0.85
    act = np.zeros(12); act[:8] = plan[:8] * np.random.uniform(0.95, 1.05, 8); act[8:] = plan[8:] * np.random.uniform(0.85, 0.92, 4)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=months, y=py, name="PY", marker_color="rgba(148, 163, 184, 0.3)", width=0.7))
    colors = ["#3B82F6" if a >= p else "#EF4444" for a, p in zip(act, plan)]
    fig.add_trace(go.Bar(x=months, y=act, name="Act+FCST", marker_color=colors, width=0.4))
    fig.add_trace(go.Scatter(x=months, y=plan, mode="markers", name="Plan", marker=dict(symbol="line-ew", size=30, color="#FFF", line=dict(width=2))))
    fig.update_layout(title=f"グローバル月次推移 - {metric} ($M)", barmode='overlay', height=280, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#FFF"), margin=dict(t=40,b=20,l=0,r=0), yaxis=dict(gridcolor="#334155"))
    fig.add_vline(x=7.5, line_width=2, line_dash="dash", line_color="#94A3B8")
    return fig

def draw_horizontal_bar(categories, plan, act, py, selected_cat=None):
    fig = go.Figure()
    fig.add_trace(go.Bar(y=categories, x=py, name="PY", orientation='h', marker_color="rgba(148, 163, 184, 0.2)", width=0.7, hoverinfo='none'))
    colors = []
    for c, a, p in zip(categories, act, plan):
        base_color = "#3B82F6" if a >= p else "#EF4444"
        if selected_cat and c != selected_cat:
            colors.append("rgba(100, 116, 139, 0.3)")
        else:
            colors.append(base_color)
    fig.add_trace(go.Bar(y=categories, x=act, name="Act+FCST", orientation='h', marker_color=colors, width=0.4))
    fig.add_trace(go.Scatter(y=categories, x=plan, mode="markers", name="Plan", marker=dict(symbol="line-ns", size=25, color="#F8FAFC", line=dict(width=2)), hoverinfo='none'))
    fig.update_layout(barmode='overlay', height=200, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#F8FAFC"), margin=dict(t=10, b=0, l=0, r=20), showlegend=False, xaxis=dict(gridcolor="#334155", zeroline=False), yaxis=dict(autorange="reversed"))
    return fig

def get_ai_analysis_html():
    return """
**【MLE - Hardware事業 利益未達要因分析】**
公式発行の週報レポートや各種会議の議事録・トランスクリプト（AI自動生成）から構築されたビジネスオントロジーを解析し、計画減少幅（▲ $20.0M）の要因を特定しました。

<div class="factor-bar-container">
    <div class="factor-ext">外部要因 65% (▲ $13.0M)</div>
    <div class="factor-int">内部要因 35% (▲ $7.0M)</div>
</div>

**🌪️ 外部要因（自身ではコントロール困難な要因）**
* **顧客先の建築工期遅れ:** 現地ゼネコンの環境アセスメント遅延に伴う納品延期、および外部倉庫での機材待機・保管費用の高騰。

**🏭 内部要因（自社で改善・対応可能な要因）**
* **歩留まり率悪化・欠品発生:** サプライヤーからの特定部品（コンデンサ）納品遅延に伴う欠品発生と、代替品でのテスト生産に伴う歩留まり悪化（想定98%→実績78%）。

---
###### 📚 判断根拠（ビジネスオントロジー抽出データ）

<div class="source-card" style="border-left-color: #F59E0B;">
    <div class="source-header">
        <span>📄 <b>欧州営業本部 週報</b> (第32週)</span>
        <span class="source-tag tag-ext">外部要因</span>
    </div>
    <div class="source-body">
        「ミュンヘンのデータセンター案件について、ゼネコンの環境アセスメント遅延に伴う基礎工事の3ヶ月延期が確定。機材出荷が滞り、外部倉庫の保管料が月額$2Mペースで発生中。」
    </div>
</div>

<div class="source-card" style="border-left-color: #EF4444;">
    <div class="source-header">
        <span>📑 <b>MLE生産管理会議 議事録</b></span>
        <span class="source-tag tag-int">内部要因</span>
    </div>
    <div class="source-body">
        「主要部品の入荷遅延によりラインが一時停止。急遽手配した代替部品でのテスト生産を行っているが、歩留まり率が78%まで落ち込んでおり、廃棄ロスが利益を圧迫している旨が報告された。」
    </div>
</div>

💡 **推奨アクション**
外部要因による巨大な待機費用を圧縮するため、現在滞留している在庫の一部を需要が逼迫しているMLAPへ転送（在庫融通）する方針が有効です。左側の**「🛠️ 3. 収益構造シミュレーション」**タブから、振替によるリカバリー額のシミュレーションを実行してください。
"""

col_nav, col_title, col_user = st.columns([1, 4, 2])
with col_nav:
    st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
    if st.button("← Back to Portal", key="back_btn_strategy"):
        st.switch_page("Top_Page.py")
    st.markdown('</div>', unsafe_allow_html=True)
with col_title:
    st.markdown("<h1 style='margin: 0; font-size: 2.2rem;'>グローバル経営数値管理ダッシュボード</h1><span style='color: #10B981; font-size: 0.9rem;'>● Live Monitoring Active</span>", unsafe_allow_html=True)
with col_user:
    st.markdown("<div style='text-align: right; color: #94A3B8;'><span style='font-size: 0.8rem;'>HQ_Admin</span><br><span style='font-size: 1.2rem; color: white; font-weight: bold;'>Level 5 Access</span></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- 刷新されたエグゼクティブサマリー ---
st.markdown("""
<div class="mac-panel">
    <h4>Executive Summary</h4>
    <ul class="mac-list">
        <li>
            <span class="badge badge-success">Growth</span>
            <span>全社売上は前年比 <strong style="color: #34D399; font-size: 1.15rem;">+5.1%</strong> と着実な成長を維持しています。</span>
        </li>
        <li>
            <span class="badge badge-alert">Alert</span>
            <span>年間利益(EBITDA)は計画比 <strong style="color: #F87171; font-size: 1.15rem;">▲8.7%</strong> と大幅な未達見込みのアラートが検知されました。</span>
        </li>
        <li>
            <span class="badge badge-info">Insight</span>
            <span>AI分析により、最大の要因は <strong style="color: #F8FAFC; border-bottom: 2px dashed #F87171; padding-bottom: 2px;">MLE地域のHardware事業</strong>（利益計画 $25.0M → 実績見込 $5.0M）における利益急減と特定されました。右側のAIエージェントに詳細な要因を質問してください。</span>
        </li>
    </ul>
</div>
""", unsafe_allow_html=True)

with st.expander("💡 このダッシュボードの見方 & 次のステップ（高度分析への誘導）", expanded=False):
    st.markdown("""
    **【ダッシュボードの活用ステップ】**
    * **📊 1. 全体俯瞰 & 🧭 2. ポートフォリオ**: 全社トレンドから地域別・事業別のボトルネックをドリルダウンで特定します。（※グラフ内のバーをクリックすると下段が連動します）
    * **🛠️ 3. 収益構造シミュレーション**: アラート対象事業に対するコスト削減などのリカバリー策をシミュレーションし、結果をERP（基幹システム）の修正予算として書き戻します。
    * **🧠 右側 AI Agent**: 専門家の知見に基づき、事業構造やKPIの因果関係を定義した**「ビジネスオントロジー（構造モデル）」**を基盤に活用。この構造に公式の週報や会議議事録、トランスクリプトを接続することで、未達の「定性的要因」を対話形式で即座に抽出します。
    
    ---
    🚀 **Next Action**: 外部マクロ指標を取り込んだ機械学習ベースの着地予測や、複数シナリオに基づく多次元要因分析（What-If分析）を実行する場合は、専用の次期ダッシュボードをご利用ください。
    """)

st.markdown("<br>", unsafe_allow_html=True)

col_dash, col_chat = st.columns([2.3, 1], gap="large")

with col_dash:
    tab1, tab2, tab3 = st.tabs(["📊 1. 全体俯瞰 (Overview)", "🧭 2. 地域・事業ポートフォリオ", "🛠️ 3. 収益構造シミュレーション"])

    with tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        k1, k2 = st.columns(2, gap="large")
        with k1: st.markdown("<div class='kpi-card'><div class='kpi-title'>Annual Revenue (年間売上 実績+見込)</div><div class='kpi-value'>$ 1,480.5 M</div><div class='kpi-deltas'>計画比: <span class='delta-red'>▼ -2.4%</span> | 前年比: <span class='delta-green'>▲ +5.1%</span></div></div>", unsafe_allow_html=True)
        with k2: st.markdown("<div class='kpi-card' style='border: 1px solid #EF4444;'><div class='kpi-title'>Annual EBITDA (年間利益 実績+見込) ⚠️ Alert</div><div class='kpi-value'>$ 215.3 M</div><div class='kpi-deltas'>計画比: <span class='delta-red'>▼ -8.7%</span> | 前年比: <span class='delta-green'>▲ +1.5%</span></div></div>", unsafe_allow_html=True)
        metric = st.radio("表示パラメータ切替", ["Revenue", "EBITDA"], horizontal=True, label_visibility="collapsed")
        st.plotly_chart(draw_bar_in_bar_monthly(metric), use_container_width=True)

    with tab2:
        col_nav1, col_nav2 = st.columns([3, 1])
        with col_nav1:
            st.info("💡 **操作**: グラフ内の『地域(Region)』のバーをクリックするか、右側のメニューで選択すると下段の事業別グラフが切り替わります。")
        with col_nav2:
            idx = (["Global (全地域)"] + regions).index(st.session_state.selected_region) if st.session_state.selected_region in regions else 0
            manual_selection = st.selectbox("🎯 地域を絞り込む", ["Global (全地域)"] + regions, index=idx)

        col_l, col_r = st.columns(2, gap="large")
        
        with col_l:
            st.markdown("<div class='quad-title'>💰 左側：売上 (Revenue)</div>", unsafe_allow_html=True)
            st.markdown("<div class='quad-subtitle'>【上段】地域毎 (Region) ※クリック連動 👇</div>", unsafe_allow_html=True)
            fig_reg_rev = draw_horizontal_bar(regions, reg_rev_plan, reg_rev_act, reg_rev_py, st.session_state.selected_region)
            try:
                event_l = st.plotly_chart(fig_reg_rev, on_select="rerun", selection_mode="points", key="click_l", use_container_width=True)
            except Exception:
                st.plotly_chart(fig_reg_rev, use_container_width=True)
                event_l = None
                
        with col_r:
            st.markdown("<div class='quad-title'>📈 右側：利益 (EBITDA)</div>", unsafe_allow_html=True)
            st.markdown("<div class='quad-subtitle'>【上段】地域毎 (Region) ※クリック連動 👇</div>", unsafe_allow_html=True)
            fig_reg_ebitda = draw_horizontal_bar(regions, reg_ebitda_plan, reg_ebitda_act, reg_ebitda_py, st.session_state.selected_region)
            try:
                event_r = st.plotly_chart(fig_reg_ebitda, on_select="rerun", selection_mode="points", key="click_r", use_container_width=True)
            except Exception:
                st.plotly_chart(fig_reg_ebitda, use_container_width=True)
                event_r = None

        def get_sel(ev):
            if ev and getattr(ev, "selection", None) and ev.selection.get("points"): return ev.selection["points"][0]["y"]
            if ev and isinstance(ev, dict) and ev.get("selection") and ev["selection"].get("points"): return ev["selection"]["points"][0]["y"]
            return None

        curr_sel_l = get_sel(event_l)
        curr_sel_r = get_sel(event_r)
        changed_l = curr_sel_l != st.session_state.prev_sel_l
        changed_r = curr_sel_r != st.session_state.prev_sel_r
        
        new_region = st.session_state.selected_region

        if changed_r: new_region = curr_sel_r
        elif changed_l: new_region = curr_sel_l

        st.session_state.prev_sel_l = curr_sel_l
        st.session_state.prev_sel_r = curr_sel_r

        if manual_selection != "Global (全地域)" and manual_selection != st.session_state.selected_region and not changed_l and not changed_r:
            new_region = manual_selection
        elif manual_selection == "Global (全地域)" and st.session_state.selected_region is not None and not changed_l and not changed_r:
            new_region = None

        if new_region != st.session_state.selected_region:
            st.session_state.selected_region = new_region
            st.rerun()

        current_reg = st.session_state.selected_region if st.session_state.selected_region else "All"
        d = biz_data[current_reg]
        title_suffix = f" <span style='color:#60A5FA;'>- {current_reg}</span>" if current_reg != "All" else " <span style='color:#94A3B8;'>- Global (全地域)</span>"
        
        with col_l:
            st.markdown(f"<div class='quad-subtitle'>【下段】事業毎 (Business){title_suffix}</div>", unsafe_allow_html=True)
            st.plotly_chart(draw_horizontal_bar(bizs, d["r_p"], d["r_a"], d["r_py"]), use_container_width=True, key="biz_rev")

        with col_r:
            st.markdown(f"<div class='quad-subtitle'>【下段】事業毎 (Business){title_suffix}</div>", unsafe_allow_html=True)
            st.plotly_chart(draw_horizontal_bar(bizs, d["e_p"], d["e_a"], d["e_py"]), use_container_width=True, key="biz_ebitda")

    with tab3:
        st.markdown("### 🛠️ 収益リカバリー・シミュレーション")
        st.caption("対象スコープ: [Region: MLE] × [Business: Hardware] の赤字リカバリー")

        base_plan = 25.0  
        current_act = 5.0 
        
        total_vc_base = 150.0   
        total_promo_base = 30.0 
        total_fix_base = 80.0  
        
        st.markdown("#### 🎛️ コスト削減・在庫融通シミュレーター (全コストベースに対する改善 %)")
        st.caption("※右側のAIが提案する「他地域への在庫融通」等により、発生中の待機費用(Variable Cost)を何％圧縮できるかシミュレーションします。")
        
        c1, c2, c3 = st.columns(3)
        st.session_state.sim_vc = c1.slider("⚙️ Variable Cost 削減 (%)", 0.0, 15.0, st.session_state.sim_vc, 1.0)
        st.session_state.sim_promo = c2.slider("📢 Promotion 費用削減 (%)", 0.0, 15.0, st.session_state.sim_promo, 1.0)
        st.session_state.sim_fix = c3.slider("🏢 Fix Cost 削減 (%)", 0.0, 15.0, st.session_state.sim_fix, 1.0)

        savings_vc = total_vc_base * (st.session_state.sim_vc / 100.0)
        savings_promo = total_promo_base * (st.session_state.sim_promo / 100.0)
        savings_fix = total_fix_base * (st.session_state.sim_fix / 100.0)
        simulated_ebitda = current_act + savings_vc + savings_promo + savings_fix
        
        df_wf = pd.DataFrame({
            "Factor": ["Current FCST<br>(現状着地見込)", "VC 削減効果<br>(+)", "Promo 削減効果<br>(+)", "Fix 削減効果<br>(+)", "Simulated<br>Actual"],
            "Amount": [current_act, savings_vc, savings_promo, savings_fix, simulated_ebitda],
            "Measure": ["absolute", "relative", "relative", "relative", "total"]
        })
        
        fig_wf = go.Figure(go.Waterfall(
            name="EBITDA Bridge", orientation="v", measure=df_wf["Measure"],
            x=df_wf["Factor"], y=df_wf["Amount"],
            text=[f"{x:+.1f}" if 0<i<4 else f"{x:.1f}" for i, x in enumerate(df_wf["Amount"])],
            textposition="outside", connector={"line":{"color":"#94A3B8"}},
            decreasing={"marker":{"color":"#EF4444"}}, increasing={"marker":{"color":"#10B981"}},
            totals={"marker":{"color":"#3B82F6" if simulated_ebitda >= base_plan else "#EF4444"}}
        ))
        fig_wf.update_layout(height=400, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#F8FAFC"), margin=dict(t=40, b=20), yaxis=dict(title="EBITDA ($M)", gridcolor="#334155"))
        fig_wf.add_hline(y=base_plan, line_dash="dash", line_color="#F8FAFC", annotation_text=f"Target Plan ({base_plan})", annotation_position="top left")
        
        st.plotly_chart(fig_wf, use_container_width=True)

        _, c_btn, _ = st.columns([1, 2, 1])
        button_type = "primary" if simulated_ebitda >= base_plan else "secondary"
        
        if c_btn.button("⚡ Apply Target to ERP (シミュレーション結果をシステムへ書き戻し)", type=button_type, use_container_width=True):
            if simulated_ebitda >= base_plan:
                with st.spinner("Connecting to SAP S/4HANA... Writing back Targets..."): time.sleep(1.0)
                st.success("✅ システム反映完了: 次期修正予算としてERPに登録・上書きされました。")
            else:
                st.error("❌ 未達アラート: シミュレーション結果がTarget Plan（計画）に届いていないため、書き戻せません。")

with col_chat:
    st.markdown("### 🧠 Ontology Agent")
    st.markdown("<span style='color:#10B981; font-size: 0.85rem; font-weight: bold;'>● Business Ontology Sync Active</span>", unsafe_allow_html=True)
    st.markdown("---")
    
    if st.button("💡 デモ: MLE Hardwareの要因分析を実行", use_container_width=True):
        st.session_state.messages_strategy.append({"role": "user", "content": "MLEのHardware事業において利益が大幅未達となっている要因を分析して。"})
        with st.spinner("ビジネスオントロジーを解析中..."):
            time.sleep(1.5)
        st.session_state.messages_strategy.append({"role": "assistant", "content": get_ai_analysis_html()})
        st.rerun()

    chat_container = st.container(height=650)
    with chat_container:
        for msg in st.session_state.messages_strategy:
            with st.chat_message(msg["role"], avatar="🦅" if msg["role"] == "assistant" else "👤"):
                st.markdown(msg["content"], unsafe_allow_html=True)

    if prompt := st.chat_input("Ask agent..."):
        st.session_state.messages_strategy.append({"role": "user", "content": prompt})
        with chat_container:
            with st.chat_message("user", avatar="👤"):
                st.markdown(prompt)
            with st.chat_message("assistant", avatar="🦅"):
                if any(word in prompt for word in ["MLE", "要因", "分析", "なぜ", "未達", "ハード"]):
                    with st.spinner("ビジネスオントロジーを解析・統合中..."):
                        time.sleep(1.5)
                    response = get_ai_analysis_html()
                else:
                    response = "承知しました。社内のビジネスオントロジーには常時接続しています。具体的な分析対象（例: 「MLEの要因分析をして」）を指示してください。"
                st.markdown(response, unsafe_allow_html=True)
        st.session_state.messages_strategy.append({"role": "assistant", "content": response})
