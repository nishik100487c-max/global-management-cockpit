import streamlit as st

# --- 1. ページ設定 ---
st.set_page_config(
    page_title="Global Management Cockpit",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
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
            font-size: 1.15rem;
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

# 視線誘導に合わせた3カラム配置（左：経営 ➔ 中：アラート ➔ 右：現場解決）
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("##### 1. Corporate Strategy")
    # 左上：一番最初に見てほしい経営ダッシュボード
    if st.button("📊 グローバル経営数値管理\nExecutive Dashboard"):
        try:
            st.switch_page("pages/03_Corporate_Strategy.py")
        except Exception:
            st.error("⚠️ ファイル `pages/03_Corporate_Strategy.py` が見つかりません。")
            
    # その下の適当な配置
    if st.button("💼 管理・HR\nAdmin & HR"):
        st.toast("Connecting to Admin module...")

with c2:
    st.markdown("##### 2. Crisis Response")
    # 中央：アラート画面
    if st.button("🚨 SCM Alert (中東危機)\nCrisis Simulation"):
        try:
            st.switch_page("pages/02_SCM_Crisis_Mode.py")
        except Exception:
            st.error("⚠️ ファイル `pages/02_SCM_Crisis_Mode.py` が見つかりません。")
            
    if st.button("🏭 研究開発\nR&D Innovation"):
        st.toast("Connecting to R&D module...")

with c3:
    st.markdown("##### 3. Supply Chain Operations")
    # 右上：シミュレーション画面
    if st.button("📦 SCM Simulation\nInventory & Procurement"):
        # 💡 万が一スペルミス（Inentory）のままでも動くように、安全策を組んでいます
        try:
            st.switch_page("pages/01_SCM_Inventory.py")
        except Exception:
            try:
                st.switch_page("pages/01_SCM_Inentory.py")
            except Exception:
                st.error("⚠️ ファイルが見つかりません（ファイル名をご確認ください）。")
                
    if st.button("💰 経理財務\nFinance & Accounting"):
        st.toast("Connecting to Finance module...")

# フッター
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #475569; font-size: 0.8rem;'>
        SECURE CONNECTION ESTABLISHED | PALANTIR FOUNDRY CORE v4.2
    </div>
""", unsafe_allow_html=True)
