import streamlit as st
import google.generativeai as genai
import json
import os
from datetime import datetime

# ─────────────────────────────────────────
# SAYFA AYARI
# ─────────────────────────────────────────
st.set_page_config(
    page_title="Siber Hukuk Asistanı",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────
# VERİTABANI
# ─────────────────────────────────────────
DB_FILE = "chat_history.json"

def load_db() -> dict:
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_db(data: dict) -> None:
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def save_current() -> None:
    db = load_db()
    db[st.session_state.chat_id] = st.session_state.messages
    save_db(db)

# ─────────────────────────────────────────
# CSS
# ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&display=swap');

*, *::before, *::after { box-sizing: border-box; }
html, body, .stApp { font-family: 'DM Sans', sans-serif !important; }

header[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDeployButton"],
.stAppDeployButton,
footer,
[data-testid="stStatusWidget"] { display: none !important; }

[data-testid="collapsedControl"],
[data-testid="stSidebarCollapsedControl"],
button[data-testid="baseButton-headerNoPadding"] {
    display: none !important;
    position: fixed !important;
    left: -9999px !important;
}

html, body, .stApp,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > section:last-child {
    background: #F8F7FF !important;
    color: #18172B !important;
}

/* ── SIDEBAR ── */
section[data-testid="stSidebar"] {
    width: 260px !important;
    min-width: 260px !important;
    max-width: 260px !important;
    transform: translateX(0) !important;
    position: fixed !important;
    top: 0 !important; left: 0 !important;
    height: 100vh !important;
    z-index: 200 !important;
    display: block !important;
    visibility: visible !important;
}
section[data-testid="stSidebar"] > div:first-child {
    width: 260px !important;
    /* Neon mor → koyu mor gradyan */
    background: linear-gradient(160deg, #5B2FD9 0%, #7C3FFC 40%, #6A2EE8 100%) !important;
    border-right: none !important;
    padding: 0 !important;
    height: 100vh !important;
    overflow-y: auto !important;
    box-shadow: 4px 0 32px rgba(124,63,252,0.35) !important;
}
section[data-testid="stSidebar"] * { color: #EDE9FF !important; }

/* Yeni Analiz butonu — parlayan neon mor */
section[data-testid="stSidebar"] button[kind="primary"] {
    background: linear-gradient(135deg, #C47FFF 0%, #A040FF 50%, #8A1FFF 100%) !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-size: 0.84rem !important;
    color: #fff !important;
    height: 40px !important;
    letter-spacing: 0.01em !important;
    box-shadow:
        0 0 0 1px rgba(196,127,255,0.4),
        0 4px 20px rgba(160,64,255,0.7),
        0 0 40px rgba(160,64,255,0.35) !important;
    transition: all .2s ease !important;
}
section[data-testid="stSidebar"] button[kind="primary"]:hover {
    background: linear-gradient(135deg, #D490FF 0%, #B050FF 50%, #9A30FF 100%) !important;
    box-shadow:
        0 0 0 1px rgba(212,144,255,0.5),
        0 6px 28px rgba(160,64,255,0.85),
        0 0 60px rgba(160,64,255,0.5) !important;
    transform: translateY(-1px) !important;
}

/* Sidebar geçmiş butonları */
section[data-testid="stSidebar"] button:not([kind="primary"]) {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    text-align: left !important;
    font-size: 0.76rem !important;
    color: rgba(237,233,255,0.75) !important;
    border-radius: 6px !important;
    padding: 6px 10px !important;
    width: 100% !important;
}
section[data-testid="stSidebar"] button:not([kind="primary"]):hover {
    background: rgba(255,255,255,0.12) !important;
    color: #fff !important;
}
.sb-active button:not([kind="primary"]) {
    background: rgba(255,255,255,0.18) !important;
    color: #fff !important;
    font-weight: 600 !important;
    border-left: 2px solid rgba(255,255,255,0.9) !important;
    border-radius: 0 6px 6px 0 !important;
    padding-left: 8px !important;
}
.sb-group-label {
    font-size: 0.56rem !important;
    font-weight: 700 !important;
    color: rgba(255,255,255,0.45) !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
    padding: 10px 14px 2px !important;
    display: block;
}

[data-testid="stAppViewContainer"] { padding-left: 260px !important; }

/* ── Main content ── */
.block-container {
    max-width: 820px !important;
    margin: 0 auto !important;
    padding: 1.5rem 2rem 130px 2rem !important;
}

/* ── Chat messages ── */
[data-testid="stChatMessage"] {
    background: transparent !important;
    padding: 0.3rem 0 !important;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stMarkdownContainer"] {
    background: #7C5CFC !important;
    color: #fff !important;
    border-radius: 16px 16px 4px 16px !important;
    padding: 11px 16px !important;
    box-shadow: 0 2px 10px rgba(124,92,252,.28) !important;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stMarkdownContainer"] p,
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stMarkdownContainer"] li {
    color: #fff !important;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) [data-testid="stMarkdownContainer"] {
    background: #fff !important;
    color: #18172B !important;
    border: 1px solid #E4E0FF !important;
    border-radius: 4px 16px 16px 16px !important;
    padding: 13px 18px !important;
    box-shadow: 0 1px 6px rgba(80,70,180,.07) !important;
}

/* ── Welcome ── */
.wlc-title {
    font-size: 2rem; font-weight: 700; color: #18172B;
    text-align: center; margin: 1.5rem 0 0.3rem; letter-spacing: -0.02em;
}
.wlc-sub {
    text-align: center; color: #6B6890; font-size: 0.86rem; margin-bottom: 1.6rem;
}
.sug-card {
    background: #fff; border: 1.5px solid #E4E0FF; border-radius: 12px;
    padding: 12px 14px; margin-bottom: 0;
}
.sug-icon  { font-size: 1.1rem; margin-bottom: 4px; }
.sug-title { font-size: 0.82rem; font-weight: 600; color: #18172B; line-height: 1.3; }
.sug-desc  { font-size: 0.69rem; color: #7B78A0; margin-top: 2px; line-height: 1.45; }
.card-btn button {
    opacity: 0 !important;
    position: absolute !important;
    inset: 0 !important;
    width: 100% !important; height: 1px !important;
    min-height: 1px !important;
    border: none !important; background: transparent !important;
    margin: 0 !important; padding: 0 !important;
}
.chip-row button {
    background: #fff !important; color: #5B3FD9 !important;
    border: 1.5px solid #D4CFFF !important; border-radius: 100px !important;
    padding: 5px 14px !important; font-size: 0.75rem !important;
    font-weight: 500 !important;
}
.chip-row button:hover { background: #EDE9FF !important; border-color: #7C5CFC !important; }

/* ── Chat topbar ── */
.chat-topbar {
    display: flex; align-items: center; gap: 8px;
    padding: 4px 0 14px; border-bottom: 1px solid #E4E0FF; margin-bottom: 10px;
}
.chat-topbar-dot { width:7px;height:7px;background:#22D49A;border-radius:50%;flex-shrink:0; }
.chat-topbar-title { font-size:0.83rem;font-weight:500;color:#18172B; }

/* ── Native chat input ── */
[data-testid="stBottom"],
[data-testid="stBottomBlockContainer"] {
    position: fixed !important;
    bottom: 0 !important;
    left: 260px !important; right: 0 !important;
    background: #F8F7FF !important;
    border-top: 1px solid #E4E0FF !important;
    padding: 10px 24px 8px !important;
    z-index: 999 !important;
}
[data-testid="stBottomBlockContainer"] .block-container {
    max-width: 820px !important; padding: 0 !important; margin: 0 auto !important;
}
[data-testid="stChatInput"] {
    background: #fff !important;
    border: 1.5px solid #D4CFFF !important;
    border-radius: 12px !important;
    box-shadow: 0 2px 14px rgba(90,75,200,.08) !important;
    padding: 2px 6px 2px 14px !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: #7C5CFC !important;
    box-shadow: 0 2px 20px rgba(124,92,252,.16) !important;
}
[data-testid="stChatInput"] textarea {
    background: transparent !important; border: none !important;
    outline: none !important; box-shadow: none !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.85rem !important; color: #18172B !important;
    padding: 8px 0 !important; resize: none !important;
}
[data-testid="stChatInput"] textarea::placeholder { color: #AAA7CC !important; }
[data-testid="stChatInput"] button {
    background: linear-gradient(135deg, #7C5CFC, #5038C8) !important;
    border: none !important; border-radius: 8px !important;
    width: 34px !important; min-width: 34px !important; height: 34px !important;
    box-shadow: 0 2px 8px rgba(90,75,200,.35) !important; color: #fff !important;
}
[data-testid="stChatInput"] button:hover {
    background: linear-gradient(135deg, #8F70FF, #6348E0) !important;
}
[data-testid="stChatInput"] button svg { fill:#fff !important; stroke:#fff !important; }
</style>
""", unsafe_allow_html=True)

# JS: sidebar açık tut
st.markdown("""
<div style="display:none;">
<script>
(function(){
    function fix(){
        var sb=document.querySelector('section[data-testid="stSidebar"]');
        if(sb){sb.style.transform='translateX(0)';sb.style.visibility='visible';}
        ['collapsedControl','stSidebarCollapsedControl'].forEach(function(id){
            var el=document.querySelector('[data-testid="'+id+'"]');
            if(el&&el.parentNode)el.parentNode.removeChild(el);
        });
    }
    [0,200,600,1500].forEach(function(t){setTimeout(fix,t);});
    new MutationObserver(fix).observe(document.body,{childList:true,subtree:true});
})();
</script>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# API & MODEL
# ─────────────────────────────────────────
SYSTEM_PROMPT = (
    "Sen uzman bir Siber Hukuk Asistanısın. "
    "Yanıtlarını resmi, maddeli ve Türkiye yasalarına (TCK, KVKK, 5651 sayılı Kanun vb.) "
    "dayandırarak ver. Gerektiğinde ilgili kanun maddelerini belirt. "
    "Yanıtların net, anlaşılır ve uygulanabilir olsun."
)

try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    _model = genai.GenerativeModel("gemini-2.0-flash")
except Exception as e:
    st.error(f"API Hatası: {e}")
    st.stop()

# ─────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────
if "chat_id" not in st.session_state:
    st.session_state.chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")

if "messages" not in st.session_state:
    db0 = load_db()
    st.session_state.messages = db0.get(st.session_state.chat_id, [])

if "gem_session" not in st.session_state:
    history = [
        {"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]}
        for m in st.session_state.messages
    ]
    st.session_state.gem_session = _model.start_chat(history=history)

if "queued" not in st.session_state:
    st.session_state.queued = ""

# ─────────────────────────────────────────
# YARDIMCILAR
# ─────────────────────────────────────────
def stream_response(prompt: str, placeholder) -> str:
    full_prompt = f"{SYSTEM_PROMPT}\n\nKullanıcı: {prompt}"
    response = st.session_state.gem_session.send_message(full_prompt, stream=True)
    text = ""
    for chunk in response:
        text += chunk.text
        placeholder.markdown(text + "▌")
    placeholder.markdown(text)
    return text

def process_message(user_text: str) -> None:
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_text)
    st.session_state.messages.append({"role": "user", "content": user_text})

    with st.chat_message("assistant", avatar="⚖️"):
        ph = st.empty()
        try:
            answer = stream_response(user_text, ph)
            st.session_state.messages.append({"role": "assistant", "content": answer})
            if len(st.session_state.messages) == 2:
                st.session_state.messages[0]["title"] = user_text[:30]
            save_current()
        except Exception as err:
            ph.error(f"⚠️ Hata: {err}")
            st.session_state.messages.pop()

def load_chat(cid: str) -> None:
    db = load_db()
    msgs = db.get(cid, [])
    st.session_state.chat_id = cid
    st.session_state.messages = msgs
    st.session_state.gem_session = _model.start_chat(history=[
        {"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]}
        for m in msgs
    ])
    st.session_state.queued = ""

def new_chat() -> None:
    st.session_state.chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    st.session_state.messages = []
    st.session_state.gem_session = _model.start_chat(history=[])
    st.session_state.queued = ""

def group_by_date(db: dict) -> dict:
    today = datetime.now().date()
    groups: dict = {"Bugün": [], "Bu Hafta": [], "Geçen Hafta": [], "Eskiler": []}
    for cid in sorted(db.keys(), reverse=True):
        try:
            diff = (today - datetime.strptime(cid, "%Y%m%d_%H%M%S").date()).days
            if   diff == 0:    groups["Bugün"].append(cid)
            elif diff <= 7:    groups["Bu Hafta"].append(cid)
            elif diff <= 14:   groups["Geçen Hafta"].append(cid)
            else:              groups["Eskiler"].append(cid)
        except Exception:
            groups["Eskiler"].append(cid)
    return groups

# ─────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────
with st.sidebar:
    # ── Başlık & profil — büyütülmüş ve daha üstte ──
    st.markdown("""
    <div style="padding:22px 16px 20px;border-bottom:1px solid rgba(255,255,255,0.15);">

        <!-- Proje etiketi -->
        <div style="font-size:0.58rem;font-weight:700;color:rgba(255,255,255,0.55);
                    text-transform:uppercase;letter-spacing:0.13em;
                    line-height:1.5;margin-bottom:8px;">
            Bilişim Güvenliği Teknolojisi<br>Bitirme Projesi
        </div>

        <!-- Bot adı -->
        <div style="font-size:1.3rem;font-weight:800;color:#fff;
                    letter-spacing:-0.01em;line-height:1.2;margin-bottom:16px;">
            ⚖️ Siber Hukuk Botu
        </div>

        <!-- Profil kartı -->
        <div style="display:flex;align-items:center;gap:10px;
                    padding:10px 12px;
                    background:rgba(255,255,255,0.12);
                    border:1px solid rgba(255,255,255,0.2);
                    border-radius:10px;
                    backdrop-filter:blur(4px);">
            <!-- Avatar -->
            <div style="width:36px;height:36px;border-radius:50%;
                        background:rgba(255,255,255,0.25);
                        border:2px solid rgba(255,255,255,0.5);
                        display:flex;align-items:center;justify-content:center;
                        font-size:0.75rem;font-weight:800;color:#fff;
                        flex-shrink:0;letter-spacing:0;">MH</div>
            <div>
                <div style="font-size:0.88rem;font-weight:700;color:#fff;
                            line-height:1.2;">Merve Havuz</div>
                <div style="font-size:0.65rem;color:rgba(255,255,255,0.65);
                            margin-top:1px;">Proje Sahibi</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='padding:14px 12px 8px;'>", unsafe_allow_html=True)
    if st.button("＋  Yeni Analiz", type="primary", use_container_width=True):
        new_chat()
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:1px;background:rgba(255,255,255,0.15);margin:0 12px 4px;'></div>",
                unsafe_allow_html=True)

    db_sb = load_db()
    for grp, cids in group_by_date(db_sb).items():
        if not cids:
            continue
        st.markdown(f"<span class='sb-group-label'>{grp}</span>", unsafe_allow_html=True)
        for cid in cids:
            msgs_s = db_sb.get(cid, [])
            lbl = (msgs_s[0].get("title") or msgs_s[0]["content"][:22] + "…") if msgs_s else "Analiz"
            active = cid == st.session_state.chat_id
            if active:
                st.markdown("<div class='sb-active'>", unsafe_allow_html=True)
            if st.button(f"💬  {lbl}", key=f"h_{cid}", use_container_width=True):
                load_chat(cid)
                st.rerun()
            if active:
                st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────
# ANA ALAN
# ─────────────────────────────────────────
pending = st.session_state.queued
if pending:
    st.session_state.queued = ""

in_chat = bool(st.session_state.messages) or bool(pending)

# ── WELCOME ──
if not in_chat:
    st.markdown('<h1 class="wlc-title">⚖️ Siber Hukuk Portalı</h1>', unsafe_allow_html=True)
    st.markdown('<p class="wlc-sub">Hukuki vakayı veya dijital haklarınızı yazın, analiz edelim.</p>',
                unsafe_allow_html=True)

    CARDS = [
        ("🔒", "KVKK İhlali",        "Kişisel veri ihlali durumunda ne yapmalıyım?"),
        ("💻", "Siber Saldırı",       "Sisteme izinsiz erişimde hukuki adımlar nelerdir?"),
        ("📱", "Sosyal Medya Hukuku", "İnternette hakaret ve iftira davası nasıl açılır?"),
        ("🏛️", "Şikayet Dilekçesi",  "BTK'ya şikayet dilekçesi nasıl hazırlanır?"),
    ]
    c1, c2 = st.columns(2, gap="small")
    for i, (icon, title, desc) in enumerate(CARDS):
        col = c1 if i % 2 == 0 else c2
        with col:
            st.markdown(f"""
            <div class="sug-card">
                <div class="sug-icon">{icon}</div>
                <div class="sug-title">{title}</div>
                <div class="sug-desc">{desc}</div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("<div class='card-btn'>", unsafe_allow_html=True)
            if st.button(title, key=f"card_{i}"):
                st.session_state.queued = desc
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    CHIPS = [
        ("📄 Dilekçe",  "Siber suç için resmi dilekçe oluşturmama yardım et."),
        ("⏱ Süre?",    "Siber suçlarda başvuru ve dava açma süreleri nedir?"),
        ("💰 Ceza?",   "Siber suçlarda öngörülen ceza miktarları nedir?"),
        ("🔍 Kanun",   "Türkiye'de siber suçlarla ilgili kanun maddeleri nelerdir?"),
    ]
    st.markdown("<div class='chip-row'>", unsafe_allow_html=True)
    for col, (label, question) in zip(st.columns(len(CHIPS), gap="small"), CHIPS):
        with col:
            if st.button(label, key=f"chip_{label}"):
                st.session_state.queued = question
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# ── CHAT ──
else:
    if st.session_state.messages:
        ttl = st.session_state.messages[0].get(
            "title", st.session_state.messages[0]["content"][:50] + "…"
        )
    else:
        ttl = (pending[:50] + "…") if pending else "Yeni Analiz"

    st.markdown(f"""
    <div class="chat-topbar">
        <span class="chat-topbar-dot"></span>
        <span class="chat-topbar-title">{ttl}</span>
    </div>
    """, unsafe_allow_html=True)

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="👤" if msg["role"] == "user" else "⚖️"):
            st.markdown(msg["content"])

    if pending:
        process_message(pending)

# ─────────────────────────────────────────
# CHAT INPUT
# ─────────────────────────────────────────
st.markdown("""
<div style="position:fixed;bottom:54px;left:260px;right:0;
            text-align:center;font-size:0.6rem;color:#9896B8;
            font-family:'DM Sans',sans-serif;pointer-events:none;
            z-index:998;padding:0 24px;">
⚠️ Bu platform hukuki tavsiye niteliği taşımamaktadır. Yalnızca genel rehberlik amaçlıdır.
</div>
""", unsafe_allow_html=True)

if new_input := st.chat_input("Hukuki vakayı buraya yazın..."):
    if not in_chat:
        st.session_state.queued = new_input
        st.rerun()
    else:
        process_message(new_input)
