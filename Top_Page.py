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

        /* 💡 Streamlitが生成するボタンの外枠(コンテナ)の高さを絶対に固定する */
        div.stButton {
            height: 120px !important;
            min-height: 120px !important;
            max-height: 120px !important;
            margin-bottom: 0 !important;
        }

        /* 💡 カスタムボタン設定（コンテナの枠いっぱいに広げる） */
        div.stButton > button {
            width: 100% !important;
            height: 100% !important;
            min-height: 100% !important;
            max-height: 100% !important;
            background: linear-gradient(145deg, #1E293B, #0F172A) !important;
            border: 1px solid #334155 !important;
            border-radius: 12px !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3) !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            padding: 10px !important;
        }
        
        /* 💡 ボタン内のテキスト設定（完全な中央揃え） */
        div.stButton > button p {
            color: #F8FAFC !important;
            font-size: 1.05rem !important; /* 長い文字が勝手に折り返さないようスマートに調整 */
            font-weight: bold !important;
            text-align: center !important;
            white-space: pre-wrap !important;
            line-height: 1.5 !important;
            margin: 0 !important;
            width: 100% !important;
        }
        
        div.stButton > button:hover {
            background: linear-gradient(145deg, #334155, #1E293B) !important;
            border-color: #3B82F6 !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.3) !important;
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

# 視線誘導に合わせた3カラム配置
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("##### 1. Corporate Strategy")
    # use_container_width=True を追加して横幅も強制統一
    if st.button("📊 グローバル経営数値管理\nExecutive Dashboard", use_container_width=True):
        try:
            st.switch_page("pages/03_Corporate_Strategy.py")
        except Exception:
            st.error("⚠️ ファイルが見つかりません。")
            
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("##### 4. Corporate Administration")
    if st.button("💼 管理・HR\nAdmin & HR", use_container_width=True):
        st.toast("Connecting to Admin module...")

with c2:
    st.markdown("##### 2. Risk Management")
    if st.button("🚨 SCMリスク管理・アラート\nCrisis Simulation", use_container_width=True):
        try:
            st.switch_page("pages/02_SCM_Crisis_Mode.py")
        except Exception:
            st.error("⚠️ ファイルが見つかりません。")
            
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("##### 5. Research & Development")
    if st.button("🏭 研究開発\nR&D Innovation", use_container_width=True):
        st.toast("Connecting to R&D module...")

with c3:
    st.markdown("##### 3. Supply Chain Operations")
    if st.button("📦 在庫・調達シミュレーション\nInventory & Procurement", use_container_width=True):
        try:
            st.switch_page("pages/01_SCM_Inventory.py")
        except Exception:
            st.error("⚠️ ファイルが見つかりません。")
                
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("##### 6. Finance & Accounting")
    if st.button("💰 経理財務\nFinance & Accounting", use_container_width=True):
        st.toast("Connecting to Finance module...")

# フッター
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #475569; font-size: 0.8rem;'>
        SECURE CONNECTION ESTABLISHED | PALANTIR FOUNDRY CORE v4.2
    </div>
""", unsafe_allow_html=True)
