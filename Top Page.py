import streamlit as st

# --- 1. ページ設定 ---
st.set_page_config(
    page_title="Global Management Cockpit",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed" # メイン画面を広く見せる
)

# --- 2. デザインシステム (Common CSS) ---
st.markdown("""
    <style>
        /* 全体背景 */
        .stApp {
            background-color: #0B1120;
            color: #F8FAFC;
        }

        /* カスタムボタン設定 */
        div.stButton > button {
            width: 100%;
            height: 120px;
            background: linear-gradient(145deg, #1E293B, #0F172A);
            border: 1px solid #334155;
            border-radius: 12px;
            color: #F8FAFC;
            font-size: 1.2rem;
            font-weight: bold;
            transition: all 0.3s ease;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }
        div.stButton > button:hover {
            background: linear-gradient(145deg, #334155, #1E293B);
            border-color: #3B82F6;
            transform: translateY(-2px);
            box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.3);
            color: #60A5FA;
        }
        
        /* サイドバー */
        [data-testid="stSidebar"] {
            background-color: #0F172A;
            border-right: 1px solid #1E293B;
        }
    </style>
""", unsafe_allow_html=True)

# --- 3. メイン画面レイアウト ---
st.markdown("""
    <div style='text-align: center; padding: 50px 0;'>
        <h1 style='font-size: 3.5rem; font-weight: 800; background: linear-gradient(to right, #60A5FA, #A78BFA); -webkit-background-clip: text; color: transparent;'>
            Global Management Cockpit
        </h1>
        <p style='color: #94A3B8; font-size: 1.2rem;'>
            Select a module to launch mission control
        </p>
    </div>
""", unsafe_allow_html=True)

# 3カラムで各種モジュールへの入り口を配置
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("##### Supply Chain & Operations")
    
    # 1つ目のダッシュボードへ遷移
    if st.button("📦 調達・生産・品質保証\nSupply Chain Mgt"):
        try:
            st.switch_page("pages/01_SCM_Inventory.py")
        except Exception:
            st.error("⚠️ 遷移先のファイル (`pages/01_SCM_Inventory.py`) が見つかりません。")
            
    # 2つ目のダッシュボードへ遷移
    if st.button("🚨 SCM危機管理モード\nCrisis Response"):
        try:
            st.switch_page("pages/02_SCM_Crisis_Mode.py")
        except Exception:
            st.error("⚠️ 遷移先のファイル (`pages/02_SCM_Crisis_Mode.py`) が見つかりません。")
            
    if st.button("🏭 研究開発\nR&D Innovation"):
        st.toast("Connecting to R&D module...")

with c2:
    st.markdown("##### Corporate Strategy")
    
    # 3つ目のダッシュボードへ遷移
    if st.button("📊 経営管理\nCorporate Strategy"):
        try:
            st.switch_page("pages/03_Corporate_Strategy.py")
        except Exception:
            st.error("⚠️ 遷移先のファイル (`pages/03_Corporate_Strategy.py`) が見つかりません。")
        
    if st.button("💼 管理\nAdmin & HR"):
        st.toast("Connecting to Admin module...")

with c3:
    st.markdown("##### Finance & Solutions")
    if st.button("💰 経理財務\nFinance & Accounting"):
        st.toast("Connecting to Finance module...")
        
    if st.button("🚀 ソリューション\nSolutions & Sales"):
        st.toast("Connecting to Sales module...")

# フッター
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #475569; font-size: 0.8rem;'>
        SECURE CONNECTION ESTABLISHED | PALANTIR FOUNDRY CORE v4.2
    </div>
""", unsafe_allow_html=True)