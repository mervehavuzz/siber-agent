import streamlit as st
import google.generativeai as genai
import json
import os
from datetime import datetime

# ==========================================
# 1. SAYFA AYARLARI
# keyboard_double butonu "expanded" modda render ediliyor.
# Çözüm: collapsed baslat, JS ile hemen ac, butonu DOM'dan sil.
# ==========================================
st.set_page_config(
    page_title="Siber Hukuk Asistanı",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed"
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
    @import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700&display=swap');
    * { font-family: 'Sora', sans-serif !important; }

    header[data-testid="stHeader"],
    [data-testid="stToolbar"],
    footer,
    [data-testid="stStatusWidget"],
    [data-testid="stDeployButton"],
    .stAppDeployButton { display: none !important; }

    html, body, .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stAppViewContainer"] > section:last-child {
        background-color: #F4F3FF !important;
        color: #1E1B3A !important;
    }

    /* Sidebar collapse/expand butonunu tamamen gizle */
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapsedControl"],
    div[data-testid="stSidebarCollapsedControl"],
    button[data-testid="baseButton-headerNoPadding"],
    button[kind="header"] {
        display: none !important;
        visibility: hidden !important;
        width: 0 !important;
        height: 0 !important;
        overflow: hidden !important;
        position: fixed !important;
        left: -9999px !important;
        top: -9999px !important;
    }

    /* SIDEBAR - daima acik ve sabit */
    section[data-testid="stSidebar"] {
        width: 272px !important;
        min-width: 272px !important;
        max-width: 272px !important;
        transform: translateX(0) !important;
        left: 0 !important;
        position: fixed !important;
        top: 0 !important;
        height: 100vh !important;
        z-index: 100 !important;
        display: block !important;
        visibility: visible !important;
    }
    section[data-testid="stSidebar"] > div:first-child {
        width: 272px !important;
        background: linear-gradient(160deg, #1E1B3A 0%, #2D2860 60%, #3B357A 100%) !important;
        border-right: none !important;
        padding: 0 !important;
        height: 100vh !important;
        overflow-y: auto !important;
    }

    /* Ana icerik sidebar'in saginda baslasin */
    [data-testid="stAppViewContainer"] {
        padding-left: 272px !important;
    }

    section[data-testid="stSidebar"] * { color: #E0DEFF !important; }

    /* Yeni Analiz butonu - neon mor */
    section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #A259FF 0%, #6B2FFA 100%) !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-size: 0.82rem !important;
        color: #FFFFFF !important;
        letter-spacing: 0.02em !important;
        padding: 0.5rem 1rem !important;
        box-shadow: 0 4px 18px rgba(162,89,255,0.6), 0 0 0 1px rgba(162,89,255,0.25) !important;
    }
    section[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #B36FFF 0%, #7C3FFF 100%) !important;
        box-shadow: 0 6px 24px rgba(162,89,255,0.8) !important;
    }

    /* Sidebar history buttons */
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
    .sb-section-label {
        font-size: 0.58rem;
        font-weight: 700;
        color: #7870C0 !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        padding: 10px 16px 3px;
    }

    /* MAIN BLOCK */
    .block-container {
        max-width: 900px !important;
        margin: 0 auto !important;
        padding-top: 0.5rem !important;
        padding-bottom: 120px !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }

    /* MESAJ BALONLARI */
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
    div[data-testid="stMarkdownContainer"]:has(.usr-msg) li { color: #FFFFFF !important; }

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
    div[data-testid="stMarkdownContainer"]:has(.ast-msg) strong { color: #1E1B3A !important; }

    /* WELCOME CARDS */
    .welcome-card {
        background: #FFFFFF !important;
        border: 1px solid #E2DDFF !important;
        border-radius: 12px !important;
        padding: 10px 14px !important;
        margin-bottom: 6px !important;
        box-shadow: 0 1px 4px rgba(83,74,183,0.06) !important;
    }
    .welcome-card:hover { border-color: #B8AEFF !important; box-shadow: 0 3px 12px rgba(83,74,183,0.12) !important; }
    .welcome-card-icon  { font-size: 1rem; margin-bottom: 3px; display: block; }
    .welcome-card-title { font-size: 0.82rem; font-weight: 600; color: #1E1B3A; line-height: 1.3; }
    .welcome-card-desc  { font-size: 0.7rem; color: #6E6B8A; margin-top: 2px; line-height: 1.4; }
    .card-trigger .stButton > button {
        margin-top: -2px !important; opacity: 0 !important; height: 2px !important;
        min-height: 2px !important; width: 100% !important; border: none !important;
    }
    .chip-wrap .stButton > button {
        background: #FFFFFF !important; color: #534AB7 !important;
        border: 1px solid #D4CFFF !important; border-radius: 20px !important;
        padding: 5px 12px !important; font-size: 0.76rem !important;
    }
    .chip-wrap .stButton > button:hover { background: #F0EEFF !important; }

    .portal-title {
        text-align: center; font-weight: 700; font-size: 1.9rem;
        color: #1E1B3A; margin-top: 0.2rem; margin-bottom: 0.1rem;
    }

    /* TOPBAR */
    .topbar {
        display: flex; align-items: center;
        padding: 6px 0 12px; border-bottom: 1px solid #E2DDFF; margin-bottom: 8px;
    }
    .status-dot { width: 7px; height: 7px; background: #22C78B; border-radius: 50%; margin-right: 8px; }
    .topbar-title { font-size: 0.85rem; font-weight: 500; color: #1E1B3A; }

    /* Streamlit default chat input - TAMAMEN GIZLE */
    [data-testid="stBottom"],
    [data-testid="stBottomBlockContainer"],
    .stChatFloatingInputContainer,
    div[data-testid="stChatInput"],
    [data-testid="stChatInput"] { display: none !important; }

    /* CUSTOM FIXED INPUT BAR */
    #custom-input-bar {
        position: fixed;
        bottom: 0;
        left: 272px;
        right: 0;
        background: #F4F3FF;
        padding: 8px 24px 5px 24px;
        z-index: 999;
        border-top: 1px solid #E2DDFF;
    }
    #custom-input-wrap {
        display: flex;
        align-items: center;
        background: #FFFFFF;
        border: 1.5px solid #D4CFFF;
        border-radius: 14px;
        box-shadow: 0 4px 20px rgba(83,74,183,0.10);
        padding: 4px 8px 4px 14px;
        max-width: 900px;
        margin: 0 auto;
    }
    #custom-input-wrap:focus-within {
        border-color: #7C6EFA;
        box-shadow: 0 4px 20px rgba(124,110,250,0.18);
    }
    #custom-input-field {
        flex: 1;
        border: none;
        outline: none;
        background: transparent;
        font-family: 'Sora', sans-serif;
        font-size: 0.84rem;
        color: #1E1B3A;
        padding: 8px 4px;
        height: 38px;
    }
    #custom-input-field::placeholder { color: #A8A4C8; }
    #custom-send-btn {
        background: linear-gradient(135deg, #7C6EFA, #534AB7);
        border: none;
        border-radius: 10px;
        width: 36px;
        height: 36px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 2px 8px rgba(83,74,183,0.3);
        flex-shrink: 0;
        color: white;
        font-size: 1rem;
        line-height: 1;
    }
    #custom-send-btn:hover { background: linear-gradient(135deg, #9180FF, #6B5FD6); }

    #input-disclaimer {
        text-align: center;
        font-size: 0.62rem;
        color: #9896B8;
        padding: 3px 0 1px;
        max-width: 900px;
        margin: 0 auto;
        font-family: 'Sora', sans-serif;
    }

    #scroll-bottom { height: 1px; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# JS: Sidebar'ı ac, keyboard butonunu sil
# ==========================================
st.markdown("""
<script>
(function() {
    var SIDEBAR_KEYWORDS = [
        'keyboard_double_arrow_left',
        'keyboard_double_arrow_right',
        'keyboard_arrow_left',
        'keyboard_arrow_right',
        'keyboard'
    ];

    function removeKeyboardBtn() {
        // collapsedControl data-testid'li elementleri sil
        ['collapsedControl', 'stSidebarCollapsedControl'].forEach(function(tid) {
            var el = document.querySelector('[data-testid="' + tid + '"]');
            if (el && el.parentNode) el.parentNode.removeChild(el);
        });

        // Tum buton ve span'lara bak, keyboard iceren metni olani sil
        document.querySelectorAll('button, span, div').forEach(function(el) {
            var txt = (el.textContent || el.innerText || '').trim().toLowerCase();
            var aria = (el.getAttribute('aria-label') || '').toLowerCase();
            var title = (el.getAttribute('title') || '').toLowerCase();
            var all = txt + ' ' + aria + ' ' + title;
            for (var i = 0; i < SIDEBAR_KEYWORDS.length; i++) {
                if (all.indexOf(SIDEBAR_KEYWORDS[i]) !== -1) {
                    var target = el.closest('button') || el;
                    var parent = target.parentNode;
                    if (parent) parent.removeChild(target);
                    break;
                }
            }
        });

        // Sidebar'i her zaman acik tut
        var sb = document.querySelector('section[data-testid="stSidebar"]');
        if (sb) {
            sb.style.transform = 'translateX(0)';
            sb.style.display = 'block';
            sb.style.visibility = 'visible';
            sb.setAttribute('aria-expanded', 'true');
        }
    }

    // Custom input icin: Streamlit chat input'u bul ve tetikle
    window.sendToStreamlit = function(val) {
        if (!val || !val.trim()) return;
        // Streamlit'in gizli textarea'sini bul
        var ta = document.querySelector('textarea[data-testid="stChatInputTextArea"]');
        if (!ta) ta = document.querySelector('[data-testid="stChatInput"] textarea');
        if (!ta) ta = document.querySelector('textarea');
        if (ta) {
            var setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
            setter.call(ta, val);
            ta.dispatchEvent(new Event('input', { bubbles: true }));
            ta.dispatchEvent(new Event('change', { bubbles: true }));
            setTimeout(function() {
                ta.dispatchEvent(new KeyboardEvent('keydown', {
                    key: 'Enter', keyCode: 13, which: 13,
                    code: 'Enter', bubbles: true, cancelable: true
                }));
                ta.dispatchEvent(new KeyboardEvent('keyup', {
                    key: 'Enter', keyCode: 13, bubbles: true
                }));
            }, 50);
        }
    };

    removeKeyboardBtn();
    setTimeout(removeKeyboardBtn, 100);
    setTimeout(removeKeyboardBtn, 300);
    setTimeout(removeKeyboardBtn, 800);
    setTimeout(removeKeyboardBtn, 2000);

    var obs = new MutationObserver(function() { removeKeyboardBtn(); });
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
    st.markdown("""
        <div style="background:linear-gradient(135deg,rgba(124,110,250,0.15) 0%,rgba(83,74,183,0.08) 100%);border-bottom:1px solid rgba(255,255,255,0.08);padding:20px 16px 18px;margin-bottom:4px;">
            <div style="display:flex;align-items:center;gap:6px;margin-bottom:6px;">
                <div style="width:3px;height:32px;background:linear-gradient(to bottom,#7C6EFA,#534AB7);border-radius:2px;flex-shrink:0;"></div>
                <div>
                    <div style="font-size:0.55rem;font-weight:700;color:#7C6EFA!important;text-transform:uppercase;letter-spacing:0.12em;line-height:1.2;margin-bottom:2px;">Bilişim Güvenliği Teknolojisi<br>Bitirme Projesi</div>
                    <div style="font-size:1.05rem;font-weight:700;color:#FFFFFF!important;line-height:1.2;">⚖️ Siber Hukuk Botu</div>
                </div>
            </div>
            <div style="display:flex;align-items:center;gap:8px;margin-top:12px;padding:8px 10px;background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.1);border-radius:10px;">
                <div style="width:30px;height:30px;border-radius:50%;background:linear-gradient(135deg,#7C6EFA,#534AB7);display:flex;align-items:center;justify-content:center;font-size:0.65rem;font-weight:700;color:white!important;flex-shrink:0;">MH</div>
                <div>
                    <div style="font-size:0.75rem;font-weight:600;color:#E0DEFF!important;line-height:1.2;">Merve Havuz</div>
                    <div style="font-size:0.62rem;color:#9B97D4!important;">Proje Sahibi</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='padding:12px 12px 8px;'>", unsafe_allow_html=True)
    if st.button("＋  Yeni Analiz Oluştur", type="primary", use_container_width=True):
        new_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.session_state.current_chat_id = new_id
        st.session_state.messages = []
        st.session_state.chat_session = model.start_chat(history=[])
        st.session_state.queued_prompt = ""
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:1px;background:rgba(255,255,255,0.08);margin:0 16px;'></div>", unsafe_allow_html=True)

    t_db = load_db()
    grouped = group_chats_by_date(t_db)

    for group_name, cids in grouped.items():
        if not cids:
            continue
        st.markdown(f"<div class='sb-section-label'>{group_name}</div>", unsafe_allow_html=True)
        for cid in cids:
            is_active = cid == st.session_state.current_chat_id
            msgs = t_db.get(cid, [])
            title = (msgs[0].get("title") or msgs[0]["content"][:24]) if msgs else "Analiz"
            if is_active:
                st.markdown("<div class='history-btn-active'>", unsafe_allow_html=True)
            if st.button(f"💬  {title}", key=f"ch_{cid}", use_container_width=True):
                st.session_state.current_chat_id = cid
                st.session_state.messages = t_db[cid]
                history_for_ai = [{"role": "user" if m["role"]=="user" else "model", "parts": [m["content"]]} for m in t_db[cid]]
                st.session_state.chat_session = model.start_chat(history=history_for_ai)
                st.session_state.queued_prompt = ""
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

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="👤" if msg["role"] == "user" else "⚖️"):
            marker = "<div class='usr-msg'></div>" if msg["role"] == "user" else "<div class='ast-msg'></div>"
            st.markdown(marker + msg["content"], unsafe_allow_html=True)

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
    st.markdown('<h1 class="portal-title">⚖️ Siber Hukuk Portalı</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center;color:#6E6B8A;margin-bottom:0.8rem;font-size:0.85rem;">Hukuki vakayı veya dijital haklarınızı yazın.</p>', unsafe_allow_html=True)

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

    st.markdown("<div style='height:0.2rem'></div>", unsafe_allow_html=True)

    chips = [
        ("📄 Dilekçe",  "Siber suç için resmi dilekçe oluşturmama yardım et."),
        ("⏱ Süre?",    "Siber suçlarda başvuru ve dava açma süreleri nedir?"),
        ("💰 Ceza?",   "Siber suçlarda öngörülen ceza miktarları nedir?"),
        ("🔍 Kanun",   "Türkiye'de siber suçlarla ilgili kanun maddeleri nelerdir?"),
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
# 9. CUSTOM CHAT INPUT + DISCLAIMER
# Streamlit'in input'u CSS ile gizlendi.
# Altta sabit HTML input bar + disclaimer.
# ==========================================
st.markdown("""
<div id="custom-input-bar">
    <div id="custom-input-wrap">
        <input
            id="custom-input-field"
            type="text"
            placeholder="Hukuki vakayı buraya yazın..."
            autocomplete="off"
        />
        <button id="custom-send-btn" onclick="doSend()">&#10148;</button>
    </div>
    <div id="input-disclaimer">
        ⚠️ Bu platform hukuki tavsiye niteliği taşımamaktadır. Yalnızca genel rehberlik amaçlıdır. Hukuki süreçler için bir avukana danışmanız önerilir.
    </div>
</div>
<script>
(function() {
    function doSend() {
        var field = document.getElementById('custom-input-field');
        var val = (field ? field.value : '').trim();
        if (!val) return;

        // Streamlit'in orjinal gizli textarea'sını bul
        var ta = document.querySelector('[data-testid="stChatInput"] textarea') 
                 || document.querySelector('[data-testid="stChatInputTextArea"]');

        if (ta) {
            // React'in inputu algılayabilmesi için native setter kullanıyoruz
            var nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, "value").set;
            nativeInputValueSetter.call(ta, val);

            // React'e yazının değiştiğini bildir (Bu adım, Streamlit Gönder butonunu aktif eder)
            ta.dispatchEvent(new Event('input', { bubbles: true }));

            // Kendi görsel inputumuzu temizleyelim
            field.value = '';

            // React'in state'i güncelleyip butonu aktif hale getirmesi için 150ms bekliyoruz
            setTimeout(function() {
                // Enter tuşu simülasyonu yerine direkt Streamlit Gönder butonuna tıklıyoruz
                var sendBtn = document.querySelector('[data-testid="stChatInput"] button');
                if (sendBtn) {
                    sendBtn.click();
                } else {
                    // Olur da buton bulunamazsa yedek plan olarak Enter tuşunu fırlat
                    ta.dispatchEvent(new KeyboardEvent('keydown', {
                        key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true
                    }));
                }
            }, 150); 
        }
    }

    window.doSend = doSend;

    // Enter tuşunu dinle
    document.addEventListener('keydown', function(e) {
        var field = document.getElementById('custom-input-field');
        if (field && document.activeElement === field && e.key === 'Enter') {
            e.preventDefault(); // Sayfanın yenilenmesini engelle
            doSend();
        }
    }, true);
})();
</script>
""", unsafe_allow_html=True)

# Streamlit'in gerçek chat_input (gizli ama çalışır - CSS ile display:none)
if prompt := st.chat_input("_"):
    st.session_state.queued_prompt = prompt
    st.rerun()
