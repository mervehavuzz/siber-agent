import streamlit as st
import google.generativeai as genai
import json
import os
from datetime import datetime

# ==========================================
# 1. SAYFA AYARLARI
# ==========================================
st.set_page_config(
    page_title="Siber Hukuk Asistanı",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. VERİTABANI YÖNETİMİ
# ==========================================
DB_FILE = "chat_history.json"

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# ==========================================
# 3. ÖZEL CSS
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    * { font-family: 'Sora', sans-serif !important; }

    header[data-testid="stHeader"],
    [data-testid="stToolbar"],
    footer,
    [data-testid="stStatusWidget"],
    [data-testid="stDeployButton"],
    .stAppDeployButton { display: none !important; }

    html, body, [class*="css"], .stApp, [data-testid="stAppViewContainer"] {
        background-color: #F4F3FF !important;
        color: #1E1B3A !important;
    }

    /* Hide sidebar toggle — target material icon text too */
    button[data-testid="baseButton-headerNoPadding"],
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapsedControl"],
    div[data-testid="stSidebarCollapsedControl"],
    button[title*="keyboard"],
    button[title*="Keyboard"],
    button[aria-label*="keyboard"],
    button[aria-label*="Keyboard"],
    section[data-testid="stSidebar"] ~ div > button,
    button[kind="header"],
    .st-emotion-cache-dvne4q,
    .st-emotion-cache-1gulkj5,
    [class*="collapsedControl"],
    [class*="SidebarCollapse"],
    [class*="sidebarCollapse"] {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        pointer-events: none !important;
        width: 0 !important;
        height: 0 !important;
        overflow: hidden !important;
        position: absolute !important;
        left: -9999px !important;
    }

    /* Kill any floating button near sidebar edge */
    section[data-testid="stSidebar"] + div > button,
    section[data-testid="stSidebar"] + section > button { display: none !important; }

    /* Hide the material-icons span that shows "keyboard_double_arrow_left" text */
    .material-icons-sharp,
    .material-symbols-sharp,
    span.material-icons,
    span[class*="material"] { display: none !important; }

    /* ── SIDEBAR ── */
    section[data-testid="stSidebar"] {
        width: 272px !important;
        min-width: 272px !important;
        max-width: 272px !important;
    }
    section[data-testid="stSidebar"] > div:first-child {
        width: 272px !important;
        background: linear-gradient(160deg, #1E1B3A 0%, #2D2860 60%, #3B357A 100%) !important;
        border-right: none !important;
        padding: 0 !important;
    }

    /* Sidebar all text override */
    section[data-testid="stSidebar"] * {
        color: #E0DEFF !important;
    }

    /* New analysis button — neon purple */
    section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #A259FF 0%, #6B2FFA 100%) !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-size: 0.82rem !important;
        color: #FFFFFF !important;
        letter-spacing: 0.02em !important;
        padding: 0.5rem 1rem !important;
        box-shadow: 0 4px 18px rgba(162,89,255,0.55), 0 0 0 1px rgba(162,89,255,0.2) !important;
    }
    section[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #B36FFF 0%, #7C3FFF 100%) !important;
        box-shadow: 0 6px 24px rgba(162,89,255,0.7), 0 0 0 1px rgba(162,89,255,0.3) !important;
    }

    /* Sidebar plain buttons */
    section[data-testid="stSidebar"] .stButton > button:not([kind="primary"]) {
        border: none !important;
        background: transparent !important;
        box-shadow: none !important;
        text-align: left !important;
        font-size: 0.78rem !important;
        color: #B8B0F0 !important;
        border-radius: 8px !important;
        padding: 7px 12px !important;
        width: 100% !important;
        transition: background 0.15s !important;
    }
    section[data-testid="stSidebar"] .stButton > button:not([kind="primary"]):hover {
        background: rgba(255,255,255,0.08) !important;
        color: #E0DEFF !important;
    }
    .history-btn-active .stButton > button:not([kind="primary"]) {
        background: rgba(124,110,250,0.25) !important;
        color: #D4CFFF !important;
        font-weight: 600 !important;
        border-left: 3px solid #7C6EFA !important;
        border-radius: 0 8px 8px 0 !important;
    }

    /* ── MAIN CONTENT BACKGROUND ── */
    [data-testid="stAppViewContainer"] > section:last-child {
        background-color: #F4F3FF !important;
    }
    .block-container {
        max-width: 960px !important;
        padding-top: 0.2rem !important;
        padding-bottom: 160px !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }

    /* ── MESAJ BALONLARI ── */
    [data-testid="stChatMessage"] {
        background-color: transparent !important;
        padding: 0.4rem 0 !important;
    }

    div[data-testid="stMarkdownContainer"]:has(.usr-msg) {
        background: linear-gradient(135deg, #534AB7 0%, #7C6EFA 100%) !important;
        color: #FFFFFF !important;
        border-radius: 18px 18px 4px 18px !important;
        padding: 12px 20px !important;
        display: block !important;
        width: 100% !important;
        box-sizing: border-box !important;
        box-shadow: 0 2px 12px rgba(83,74,183,0.25) !important;
    }
    div[data-testid="stMarkdownContainer"]:has(.usr-msg) p,
    div[data-testid="stMarkdownContainer"]:has(.usr-msg) li {
        color: #FFFFFF !important;
    }

    div[data-testid="stMarkdownContainer"]:has(.ast-msg) {
        background-color: #FFFFFF !important;
        border: 1px solid #E8E4FF !important;
        border-radius: 4px 18px 18px 18px !important;
        padding: 14px 20px !important;
        color: #1E1B3A !important;
        display: block !important;
        width: 100% !important;
        box-sizing: border-box !important;
        box-shadow: 0 2px 8px rgba(83,74,183,0.07) !important;
    }
    div[data-testid="stMarkdownContainer"]:has(.ast-msg) p,
    div[data-testid="stMarkdownContainer"]:has(.ast-msg) li,
    div[data-testid="stMarkdownContainer"]:has(.ast-msg) strong {
        color: #1E1B3A !important;
    }

    /* ── WELCOME CARDS ── */
    .welcome-card {
        background: #FFFFFF !important;
        border: 1px solid #E2DDFF !important;
        border-radius: 12px !important;
        padding: 10px 14px !important;
        margin-bottom: 6px !important;
        box-shadow: 0 1px 4px rgba(83,74,183,0.06) !important;
        cursor: pointer;
    }
    .welcome-card:hover {
        border-color: #B8AEFF !important;
        box-shadow: 0 3px 12px rgba(83,74,183,0.12) !important;
    }
    .welcome-card-icon  { font-size: 1rem; margin-bottom: 3px; display: block; }
    .welcome-card-title { font-size: 0.82rem; font-weight: 600; color: #1E1B3A; line-height: 1.3; }
    .welcome-card-desc  { font-size: 0.7rem; color: #6E6B8A; margin-top: 2px; line-height: 1.4; }

    .card-trigger .stButton > button {
        margin-top: -2px !important;
        opacity: 0 !important;
        height: 2px !important;
        min-height: 2px !important;
        width: 100% !important;
        border: none !important;
    }

    .chip-wrap .stButton > button {
        background: #FFFFFF !important;
        color: #534AB7 !important;
        border: 1px solid #D4CFFF !important;
        border-radius: 20px !important;
        padding: 5px 12px !important;
        font-size: 0.76rem !important;
        box-shadow: 0 1px 3px rgba(83,74,183,0.08) !important;
    }
    .chip-wrap .stButton > button:hover {
        background: #F0EEFF !important;
        border-color: #A89EFF !important;
    }

    /* ── PORTAL TITLE ── */
    .portal-title {
        text-align: center;
        font-weight: 700;
        font-size: 1.9rem;
        color: #1E1B3A;
        margin-top: 0.2rem !important;
        margin-bottom: 0.1rem;
    }

    /* ── TOPBAR ── */
    .topbar {
        display: flex;
        align-items: center;
        padding: 6px 0 12px;
        border-bottom: 1px solid #E2DDFF;
        margin-bottom: 8px;
    }
    .status-dot { width: 7px; height: 7px; background: #22C78B; border-radius: 50%; margin-right: 8px; box-shadow: 0 0 6px rgba(34,199,139,0.5); }
    .topbar-title { font-size: 0.85rem; font-weight: 500; color: #1E1B3A; }

    /* ── SIDEBAR SECTION LABEL ── */
    .sb-section-label {
        font-size: 0.58rem;
        font-weight: 700;
        color: #7870C0 !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        padding: 10px 16px 3px;
    }

    /* ── DISCLAIMER — shown below chat input ── */
    .disclaimer {
        text-align: center;
        font-size: 0.65rem;
        color: #9896B8;
        padding: 0.3rem 1rem 0;
        line-height: 1.4;
    }

    /* ── CHAT INPUT — completely remove default and rebuild ── */
    [data-testid="stBottomBlockContainer"],
    [data-testid="stBottom"],
    .stChatFloatingInputContainer,
    div[data-testid="stChatInput"] {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
    }

    /* The actual textarea wrapper */
    [data-testid="stChatInput"] > div {
        background: #FFFFFF !important;
        border: 1.5px solid #D4CFFF !important;
        border-radius: 14px !important;
        box-shadow: 0 4px 20px rgba(83,74,183,0.10) !important;
        padding: 2px 6px !important;
        max-height: 52px !important;
    }
    [data-testid="stChatInput"] > div:focus-within {
        border-color: #7C6EFA !important;
        box-shadow: 0 4px 20px rgba(124,110,250,0.18) !important;
    }

    [data-testid="stChatInput"] textarea {
        background: transparent !important;
        color: #1E1B3A !important;
        border: none !important;
        border-radius: 0 !important;
        box-shadow: none !important;
        font-size: 0.84rem !important;
        padding: 10px 8px !important;
        max-height: 42px !important;
        min-height: 42px !important;
        resize: none !important;
    }
    [data-testid="stChatInput"] textarea::placeholder {
        color: #A8A4C8 !important;
    }
    [data-testid="stChatInput"] button {
        background: linear-gradient(135deg, #7C6EFA, #534AB7) !important;
        color: white !important;
        border-radius: 10px !important;
        width: 34px !important;
        height: 34px !important;
        min-height: 34px !important;
        border: none !important;
        margin: 4px !important;
        box-shadow: 0 2px 8px rgba(83,74,183,0.3) !important;
    }
    [data-testid="stChatInput"] button:hover {
        background: linear-gradient(135deg, #9180FF, #6B5FD6) !important;
    }

    /* Bottom container — input sits above watermark, disclaimer fits in gap below */
    [data-testid="stBottomBlockContainer"] {
        padding-bottom: 3.5rem !important;
        padding-top: 0.4rem !important;
        background: linear-gradient(to top, #F4F3FF 85%, transparent) !important;
        margin-bottom: 0 !important;
    }

    #scroll-bottom { height: 1px; }
</style>
""", unsafe_allow_html=True)

# Kill the sidebar collapse button via JS — targets material icon text nodes too
st.markdown("""
<script>
(function() {
    function killSidebarBtn() {
        // 1. Target by data-testid
        ['collapsedControl','stSidebarCollapsedControl'].forEach(function(id) {
            var el = document.querySelector('[data-testid="' + id + '"]');
            if (el) { el.remove(); }
        });
        // 2. Hide any element whose text content is exactly the material icon name
        var keywords = ['keyboard_double_arrow_left','keyboard_double_arrow_right','keyboard_arrow_left','keyboard_arrow_right'];
        document.querySelectorAll('button, span, div').forEach(function(el) {
            var txt = (el.textContent || '').trim();
            var label = (el.getAttribute('aria-label') || '');
            var title = (el.getAttribute('title') || '');
            var combined = (txt + label + title).toLowerCase();
            if (keywords.some(function(k){ return combined.includes(k); })) {
                var target = el.closest('button') || el.closest('[data-testid]') || el;
                target.style.cssText = 'display:none!important;width:0!important;height:0!important;overflow:hidden!important;position:absolute!important;left:-9999px!important;';
            }
        });
        // 3. Any button right after sidebar
        var sb = document.querySelector('section[data-testid="stSidebar"]');
        if (sb) {
            var sibling = sb.nextElementSibling;
            while (sibling) {
                var btns = sibling.querySelectorAll('button');
                btns.forEach(function(b){ b.style.cssText = 'display:none!important;'; });
                sibling = sibling.nextElementSibling;
            }
        }
    }
    // Run on load + watch DOM
    document.addEventListener('DOMContentLoaded', killSidebarBtn);
    setTimeout(killSidebarBtn, 100);
    setTimeout(killSidebarBtn, 500);
    var obs = new MutationObserver(killSidebarBtn);
    obs.observe(document.body, { childList: true, subtree: true });
})();
</script>
""", unsafe_allow_html=True)

# ==========================================
# 4. API VE MODEL
# ==========================================
SISTEM_PROMPTU = "Sen uzman bir Siber Hukuk Asistanısın. Yanıtlarını resmi, madde işaretli ve Türkiye yasalarına dayandırarak ver."

try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-3-flash-preview')
except Exception as e:
    st.error("API Hatası! Lütfen Streamlit ayarlarını kontrol edin.")
    st.stop()

# ==========================================
# 5. SESSION STATE
# ==========================================
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")
if "messages" not in st.session_state:
    db_init = load_db()
    st.session_state.messages = db_init.get(st.session_state.current_chat_id, [])
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])
if "queued_prompt" not in st.session_state:
    st.session_state.queued_prompt = ""
if "scroll_to_bottom" not in st.session_state:
    st.session_state.scroll_to_bottom = False

# ==========================================
# 6. YARDIMCI FONKSİYONLAR
# ==========================================
def group_chats_by_date(chat_dict):
    today = datetime.now().date()
    groups = {"Bugün": [], "Bu Hafta": [], "Geçen Hafta": [], "Eskiler": []}
    for cid in sorted(chat_dict.keys(), reverse=True):
        try:
            d = datetime.strptime(cid, "%Y%m%d_%H%M%S").date()
            diff = (today - d).days
            if diff == 0:      groups["Bugün"].append(cid)
            elif diff <= 7:    groups["Bu Hafta"].append(cid)
            elif diff <= 14:   groups["Geçen Hafta"].append(cid)
            else:              groups["Eskiler"].append(cid)
        except:
            groups["Eskiler"].append(cid)
    return groups

# ==========================================
# 7. SOL MENÜ (SIDEBAR)
# ==========================================
with st.sidebar:
    # ── Modern Sidebar Header ──
    st.markdown("""
        <div style="
            background: linear-gradient(135deg, rgba(124,110,250,0.15) 0%, rgba(83,74,183,0.08) 100%);
            border-bottom: 1px solid rgba(255,255,255,0.08);
            padding: 20px 16px 18px 16px;
            margin-bottom: 4px;
        ">
            <div style="
                display: flex;
                align-items: center;
                gap: 6px;
                margin-bottom: 6px;
            ">
                <div style="
                    width: 3px;
                    height: 32px;
                    background: linear-gradient(to bottom, #7C6EFA, #534AB7);
                    border-radius: 2px;
                    flex-shrink: 0;
                "></div>
                <div>
                    <div style="
                        font-size: 0.55rem;
                        font-weight: 700;
                        color: #7C6EFA !important;
                        text-transform: uppercase;
                        letter-spacing: 0.12em;
                        line-height: 1.2;
                        margin-bottom: 2px;
                    ">Bilişim Güvenliği Teknolojisi<br>Bitirme Projesi</div>
                    <div style="
                        font-size: 1.05rem;
                        font-weight: 700;
                        color: #FFFFFF !important;
                        line-height: 1.2;
                    ">⚖️ Siber Hukuk Botu</div>
                </div>
            </div>
            <div style="
                display: flex;
                align-items: center;
                gap: 8px;
                margin-top: 12px;
                padding: 8px 10px;
                background: rgba(255,255,255,0.06);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 10px;
            ">
                <div style="
                    width: 30px;
                    height: 30px;
                    border-radius: 50%;
                    background: linear-gradient(135deg, #7C6EFA, #534AB7);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 0.65rem;
                    font-weight: 700;
                    color: white !important;
                    flex-shrink: 0;
                ">MH</div>
                <div>
                    <div style="font-size: 0.75rem; font-weight: 600; color: #E0DEFF !important; line-height: 1.2;">Merve Havuz</div>
                    <div style="font-size: 0.62rem; color: #9B97D4 !important;">Proje Sahibi</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # ── New Chat Button ──
    st.markdown("<div style='padding: 12px 12px 8px;'>", unsafe_allow_html=True)
    if st.button("＋  Yeni Analiz Oluştur", type="primary", use_container_width=True):
        new_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.session_state.current_chat_id = new_id
        st.session_state.messages = []
        st.session_state.chat_session = model.start_chat(history=[])
        st.session_state.queued_prompt = ""
        st.session_state.scroll_to_bottom = False
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    # Divider
    st.markdown("<div style='height:1px;background:rgba(255,255,255,0.08);margin:0 16px;'></div>", unsafe_allow_html=True)

    # ── Chat History — always re-read DB so it stays fresh ──
    t_db = load_db()
    grouped = group_chats_by_date(t_db)

    for group_name, cids in grouped.items():
        if not cids:
            continue
        st.markdown(f"<div class='sb-section-label'>{group_name}</div>", unsafe_allow_html=True)

        for cid in cids:
            is_active = cid == st.session_state.current_chat_id
            msgs = t_db.get(cid, [])
            if msgs:
                title = msgs[0].get("title") or msgs[0]["content"][:24]
            else:
                title = "Analiz"

            if is_active:
                st.markdown("<div class='history-btn-active'>", unsafe_allow_html=True)
            if st.button(f"💬  {title}", key=f"ch_{cid}", use_container_width=True):
                st.session_state.current_chat_id = cid
                st.session_state.messages = t_db[cid]
                history_for_ai = []
                for m in t_db[cid]:
                    r = "user" if m["role"] == "user" else "model"
                    history_for_ai.append({"role": r, "parts": [m["content"]]})
                st.session_state.chat_session = model.start_chat(history=history_for_ai)
                st.session_state.queued_prompt = ""
                st.session_state.scroll_to_bottom = False
                st.rerun()
            if is_active:
                st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 8. ANA EKRAN
# ==========================================
chat_active = bool(st.session_state.messages) or bool(st.session_state.queued_prompt)

if chat_active:
    if st.session_state.messages:
        current_title = st.session_state.messages[0].get("title", st.session_state.messages[0]["content"][:35] + "…")
    else:
        current_title = st.session_state.queued_prompt[:35] + "…"

    st.markdown(f"""
        <div class='topbar'>
            <span class='status-dot'></span>
            <span class='topbar-title'>{current_title}</span>
        </div>
    """, unsafe_allow_html=True)

    # Render existing messages
    for i, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"], avatar="👤" if msg["role"] == "user" else "⚖️"):
            marker = "<div class='usr-msg'></div>" if msg["role"] == "user" else "<div class='ast-msg'></div>"
            st.markdown(marker + msg["content"], unsafe_allow_html=True)

    # Process queued prompt
    if st.session_state.queued_prompt:
        prompt = st.session_state.queued_prompt
        st.session_state.queued_prompt = ""

        with st.chat_message("user", avatar="👤"):
            st.markdown("<div class='usr-msg'></div>" + prompt, unsafe_allow_html=True)

        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant", avatar="⚖️"):
            placeholder = st.empty()
            placeholder.markdown("<div class='ast-msg'></div><span style='color:#9B97D4;font-size:0.82rem;'>⚖️ Analiz ediliyor...</span>", unsafe_allow_html=True)

            try:
                full_prompt = f"{SISTEM_PROMPTU}\n\nKullanıcı Sorusu: {prompt}"
                response = st.session_state.chat_session.send_message(full_prompt, stream=True)
                full_res = ""
                for chunk in response:
                    full_res += chunk.text
                    placeholder.markdown("<div class='ast-msg'></div>" + full_res + "▌", unsafe_allow_html=True)

                placeholder.markdown("<div class='ast-msg'></div>" + full_res, unsafe_allow_html=True)

                if len(st.session_state.messages) == 1:
                    st.session_state.messages[0]["title"] = prompt[:25]

                st.session_state.messages.append({"role": "assistant", "content": full_res})

                # Save to DB immediately so history updates
                fresh_db = load_db()
                fresh_db[st.session_state.current_chat_id] = st.session_state.messages
                save_db(fresh_db)
                st.session_state.scroll_to_bottom = True

            except Exception as e:
                placeholder.markdown("")
                st.error(f"⚠️ API Hatası: {e}")
                st.session_state.messages.pop()

        st.rerun()

    st.markdown("<div id='scroll-bottom'></div>", unsafe_allow_html=True)

else:
    # ── Welcome Screen ──
    st.markdown('<h1 class="portal-title">⚖️ Siber Hukuk Portalı</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center;color:#6E6B8A;margin-bottom:1rem;font-size:0.85rem;">Hukuki vakayı veya dijital haklarınızı yazın.</p>', unsafe_allow_html=True)

    welcome_items = [
        ("🔒", "KVKK İhlali",        "Kişisel veri ihlali durumunda ne yapmalıyım?"),
        ("💻", "Siber Saldırı",       "Sisteme izinsiz erişimde hukuki adımlar nelerdir?"),
        ("📱", "Sosyal Medya Hukuku", "İnternette hakaret ve iftira davası nasıl açılır?"),
        ("🏛️", "Şikayet Dilekçesi",  "BTK'ya şikayet dilekçesi nasıl hazırlanır?"),
    ]

    col_a, col_b = st.columns(2, gap="small")
    for idx, (icon, title, desc) in enumerate(welcome_items):
        col = col_a if idx % 2 == 0 else col_b
        with col:
            st.markdown(f"""
                <div class='welcome-card'>
                    <span class='welcome-card-icon'>{icon}</span>
                    <div class='welcome-card-title'>{title}</div>
                    <div class='welcome-card-desc'>{desc}</div>
                </div>
            """, unsafe_allow_html=True)
            st.markdown("<div class='card-trigger'>", unsafe_allow_html=True)
            if st.button(f"▸ {title}", key=f"wcard_{idx}"):
                st.session_state.queued_prompt = desc
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:0.1rem'></div>", unsafe_allow_html=True)

    chips = [
        ("📄 Dilekçe",       "Siber suç için resmi dilekçe oluşturmama yardım et."),
        ("⏱ Süre?",          "Siber suçlarda başvuru ve dava açma süreleri nedir?"),
        ("💰 Ceza?",         "Siber suçlarda öngörülen ceza miktarları nedir?"),
        ("🔍 Kanun",         "Türkiye'de siber suçlarla ilgili kanun maddeleri nelerdir?"),
    ]
    st.markdown("<div class='chip-wrap'>", unsafe_allow_html=True)
    chip_cols = st.columns(len(chips), gap="small")
    for col, (label, question) in zip(chip_cols, chips):
        with col:
            if st.button(label, key=f"chip_{label}"):
                st.session_state.queued_prompt = question
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 9. SOHBET GİRDİSİ
# ==========================================
if prompt := st.chat_input("Hukuki vakayı buraya yazın..."):
    st.session_state.queued_prompt = prompt
    st.rerun()

st.markdown("""
    <div class='disclaimer'>
        ⚠️ Bu platform hukuki tavsiye niteliği taşımamaktadır. Yalnızca genel rehberlik amaçlıdır. Hukuki süreçler için bir avukana danışmanız önerilir.
    </div>
""", unsafe_allow_html=True)
