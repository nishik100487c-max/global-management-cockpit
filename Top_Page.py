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
            white-space: pre-wrap !important; /* 💡指定した位置(\n)での改行を強制する */
            line-height: 1.4 !important;
        }
        /* ボタン内のテキスト要素にも改行ルールを適用 */
        div.stButton > button * {
            white-space: pre-wrap !important;
            text-align: center !important;
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

# 視線誘導に合わせた3カラム配置
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("##### 1. Corporate Strategy")
    # 💡 英語と日本語の間で綺麗に改行されます
    if st.button("📊 グローバル経営数値管理\nExecutive Dashboard"):
        try:
            st.switch_page("pages/03_Corporate_Strategy.py")
        except Exception:
            st.error("⚠️ ファイルが見つかりません。")
            
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("##### 4. Corporate Administration")
    if st.button("💼 管理・HR\nAdmin & HR"):
        st.toast("Connecting to Admin module...")

with c2:
    st.markdown("##### 2. Risk Management")
    # 💡 日本語の汎用名称を追加し、フォーマットを統一しました
    if st.button("🚨 SCMリスク管理・アラート\nCrisis Simulation"):
        try:
            st.switch_page("pages/02_SCM_Crisis_Mode.py")
        except Exception:
            st.error("⚠️ ファイルが見つかりません。")
            
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("##### 5. Research & Development")
    if st.button("🏭 研究開発\nR&D Innovation"):
        st.toast("Connecting to R&D module...")

with c3:
    st.markdown("##### 3. Supply Chain Operations")
    # 💡 日本語の汎用名称を追加し、フォーマットを統一しました
    if st.button("📦 在庫・調達シミュレーション\nInventory & Procurement"):
        try:
            st.switch_page("pages/01_SCM_Inventory.py")
        except Exception:
            st.error("⚠️ ファイルが見つかりません。")
                
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("##### 6. Finance & Accounting")
    if st.button("💰 経理財務\nFinance & Accounting"):
        st.toast("Connecting to Finance module...")

# フッター
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #475569; font-size: 0.8rem;'>
        SECURE CONNECTION ESTABLISHED | PALANTIR FOUNDRY CORE v4.2
    </div>
""", unsafe_allow_html=True)
