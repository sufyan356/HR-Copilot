from pathlib import Path
import os
import requests
import streamlit as st


# ============================================================
# CONFIG
# ============================================================

try:
    API_BASE_URL = st.secrets["API_BASE_URL"]
except (FileNotFoundError, KeyError):
    API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

st.set_page_config(
    page_title="HR Copilot",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# DESIGN SYSTEM (CSS)
# ============================================================

def inject_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');

        /* ---------- Completely Hide Streamlit Header & Top Bar ---------- */
        header, 
        header.stAppHeader,
        [data-testid="stHeader"], 
        [data-testid="stToolbar"], 
        [data-testid="stDecoration"],
        .stAppDeployButton {
            display: none !important;
            visibility: hidden !important;
            height: 0 !important;
            opacity: 0 !important;
            pointer-events: none !important;
        }

        /* Pull the main content wrapper and block containers fully to the top */
        .stAppViewContainer, 
        .main, 
        .block-container, 
        [data-testid="stMainBlockContainer"],
        section.stMain {
            padding-top: 0rem !important;
            margin-top: 0rem !important;
            top: 0 !important;
        }

        :root {
            --ink: #16233F;
            --paper: #F3F5F8;
            --card: #FFFFFF;
            --signal: #2F6F52;
            --signal-dark: #244F3D;
            --amber: #D98E2B;
            --ash: #6B7280;
            --rust: #B23A34;
            --line: #E2E6ED;
        }

        html, body, [class*="css"] {
            font-family: 'IBM Plex Sans', sans-serif;
            color: var(--ink);
        }

        .stApp {
            background: var(--paper);
        }

        h1, h2, h3 {
            font-family: 'Fraunces', serif;
            color: var(--ink);
            letter-spacing: -0.01em;
        }

        /* ---------- Sidebar ---------- */

        [data-testid="stSidebar"] {
            background: var(--ink);
        }

        [data-testid="stSidebar"] * {
            color: #EDEFF4 !important;
        }

        [data-testid="stSidebar"] .stButton > button {
            background: transparent;
            border: 1px solid rgba(255,255,255,0.25);
            color: #EDEFF4 !important;
            border-radius: 8px;
            width: 100%;
        }

        [data-testid="stSidebar"] .stButton > button:hover {
            border-color: var(--amber);
            color: var(--amber) !important;
        }

        /* ---------- App title block ---------- */

        .app-title {
            font-family: 'Fraunces', serif;
            font-size: 1.55rem;
            font-weight: 600;
            margin: 0;
            color: #EDEFF4;
        }

        .app-caption {
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.72rem;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            color: var(--amber) !important;
            margin-top: 2px;
        }

        /* ---------- Dashboard ---------- */

        .dashboard-wrap {
            max-width: 1050px;
            margin: 2rem auto 0 auto;
            padding: 0 1.5rem;
        }

        .dashboard-kicker {
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: var(--amber);
            margin-bottom: 0.6rem;
        }

        .dashboard-title {
            font-family: 'Fraunces', serif;
            font-size: clamp(2.8rem, 6vw, 5.2rem);
            line-height: 0.98;
            font-weight: 600;
            color: var(--ink);
            margin-bottom: 1.2rem;
        }

        .dashboard-subtitle {
            max-width: 720px;
            font-size: 1.12rem;
            line-height: 1.7;
            color: var(--ash);
            margin-bottom: 2rem;
        }

        .dashboard-card {
            background: var(--card);
            border: 1px solid var(--line);
            border-radius: 14px;
            padding: 1.4rem;
            height: 100%;
            box-shadow: 0 1px 2px rgba(22,35,63,0.03);
        }

        .dashboard-card-icon {
            font-size: 1.7rem;
            margin-bottom: 0.5rem;
        }

        .dashboard-card-title {
            font-family: 'Fraunces', serif;
            font-size: 1.25rem;
            font-weight: 600;
            color: var(--ink);
            margin-bottom: 0.35rem;
        }

        .dashboard-card-text {
            color: var(--ash);
            font-size: 0.9rem;
            line-height: 1.5;
        }

        .auth-required {
            background: #FFF8EA;
            border: 1px solid #E9C37A;
            border-left: 4px solid var(--amber);
            border-radius: 10px;
            padding: 1rem 1.1rem;
            margin: 1rem 0;
            color: var(--ink);
        }

        .auth-required-title {
            font-weight: 600;
            margin-bottom: 0.2rem;
        }

        .auth-required-text {
            color: var(--ash);
            font-size: 0.9rem;
        }

        /* ---------- Auth page ---------- */

        .auth-page {
            min-height: auto;
            display: flex;
            align-items: flex-start;
            justify-content: center;
            padding: 0.5rem 1rem 2rem 1rem;
        }

        .auth-container {
            width: 50%;
            min-width: 420px;
            max-width: 680px;
            margin: 0 auto;
        }

        .auth-card {
            background: var(--card);
            border: 1px solid var(--line);
            border-radius: 16px;
            padding: 2rem 2.5rem 2rem 2.5rem;
            box-shadow: 0 2px 4px rgba(22,35,63,0.04),
                        0 18px 45px rgba(22,35,63,0.08);
        }

        .auth-brand {
            font-family: 'Fraunces', serif;
            font-size: 2rem;
            font-weight: 600;
            color: var(--ink);
            text-align: center;
        }

        .auth-sub {
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.72rem;
            color: var(--ash);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            text-align: center;
            margin: 0.35rem 0 1.2rem 0;
        }

        /* ---------- Example Suggestions Card ---------- */
        .suggestions-box {
            background: var(--card);
            border: 1px solid var(--line);
            border-radius: 10px;
            padding: 1rem 1.2rem;
            margin-bottom: 1rem;
        }

        .suggestions-title {
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--amber);
            margin-bottom: 0.5rem;
            font-weight: 600;
        }

        .suggestion-item {
            font-size: 0.9rem;
            color: var(--ash);
            margin-bottom: 0.3rem;
        }

        /* ---------- Streamlit form / input styling ---------- */

        .stTextInput > div > div > input,
        .stTextInput input,
        .stTextArea textarea,
        .stNumberInput input {
            background-color: #FFFFFF !important;
            color: #16233F !important;
            border: 1px solid #D5DAE3 !important;
            border-radius: 8px !important;
            box-shadow: none !important;
        }

        .stTextInput > div > div > input:focus,
        .stTextInput input:focus,
        .stTextArea textarea:focus,
        .stNumberInput input:focus {
            background-color: #FFFFFF !important;
            color: #16233F !important;
            border-color: #2F6F52 !important;
            box-shadow: 0 0 0 1px #2F6F52 !important;
        }

        /* Browser autofill */
        .stTextInput input:-webkit-autofill,
        .stTextInput input:-webkit-autofill:hover,
        .stTextInput input:-webkit-autofill:focus {
            -webkit-text-fill-color: #16233F !important;
            -webkit-box-shadow: 0 0 0 1000px #FFFFFF inset !important;
            box-shadow: 0 0 0 1000px #FFFFFF inset !important;
        }

        /* ---------- Buttons ---------- */

        .stButton > button,
        .stFormSubmitButton > button {
            background: var(--signal);
            color: white !important;
            border: none;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            font-weight: 500;
        }

        .stButton > button:hover,
        .stFormSubmitButton > button:hover {
            background: var(--signal-dark);
            color: white !important;
        }

        /* ---------- Chat bubbles ---------- */

        .chat-row {
            display: flex;
            margin-bottom: 14px;
        }

        .chat-row.user {
            justify-content: flex-end;
        }

        .chat-row.assistant {
            justify-content: flex-start;
        }

        .bubble {
            max-width: 72%;
            padding: 0.75rem 1rem;
            border-radius: 12px;
            font-size: 0.95rem;
            line-height: 1.5;
        }

        .bubble-user {
            background: var(--ink);
            color: #F3F5F8;
            border-bottom-right-radius: 3px;
        }

        .bubble-assistant {
            background: var(--card);
            border: 1px solid var(--line);
            border-left: 3px solid var(--signal);
            color: var(--ink);
            border-bottom-left-radius: 3px;
        }

        .bubble-error {
            background: #FBEAEA;
            border: 1px solid var(--rust);
            border-left: 3px solid var(--rust);
            color: var(--rust);
        }

        .bubble-label {
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.65rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--ash);
            margin-bottom: 4px;
        }

        /* ---------- Reference rail ---------- */

        .rail-heading {
            font-family: 'Fraunces', serif;
            font-size: 1.05rem;
            font-weight: 600;
            margin-bottom: 0.2rem;
        }

        .rail-sub {
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.68rem;
            color: var(--ash);
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin-bottom: 1rem;
        }

        .source-chip {
            background: var(--card);
            border: 1px dashed var(--amber);
            border-radius: 8px;
            padding: 0.6rem 0.75rem;
            margin-bottom: 0.6rem;
        }

        .source-chip-top {
            display: flex;
            align-items: center;
            gap: 6px;
            font-weight: 500;
            font-size: 0.85rem;
            color: var(--ink);
        }

        .source-chip-ref {
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.72rem;
            color: var(--amber);
            margin-top: 3px;
        }

        .rail-empty {
            font-size: 0.85rem;
            color: var(--ash);
            border: 1px dashed var(--line);
            border-radius: 8px;
            padding: 0.9rem;
        }

        @media (max-width: 900px) {
            .auth-container {
                width: 90%;
                min-width: 0;
            }

            .dashboard-wrap {
                margin-top: 1.5rem;
            }

            .auth-card {
                padding: 1.5rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# API HELPERS
# ============================================================

def api_post(path: str, payload: dict, token: str = None) -> dict:
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    try:
        response = requests.post(
            f"{API_BASE_URL}{path}",
            json=payload,
            headers=headers,
            timeout=60,
        )
        return response.json()
    except requests.exceptions.RequestException:
        return {
            "status": False,
            "error": "CONNECTION_ERROR",
            "message": "Could not reach the HR Copilot API. Is the backend running?",
            "data": None,
        }


def api_get(path: str, token: str = None) -> dict:
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    try:
        response = requests.get(
            f"{API_BASE_URL}{path}",
            headers=headers,
            timeout=30,
        )
        return response.json()
    except requests.exceptions.RequestException:
        return {
            "status": False,
            "error": "CONNECTION_ERROR",
            "message": "Could not reach the HR Copilot API. Is the backend running?",
            "data": None,
        }


# ============================================================
# SESSION STATE
# ============================================================

def init_state():
    defaults = {
        "token": None,
        "user_name": None,
        "user_email": None,
        "messages": [],
        "last_sources": [],
        "page": "dashboard",
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def logout():
    st.session_state.token = None
    st.session_state.user_name = None
    st.session_state.user_email = None
    st.session_state.messages = []
    st.session_state.last_sources = []
    st.session_state.page = "dashboard"


def require_auth(page_name: str):
    if st.session_state.token:
        st.session_state.page = page_name
        return True

    st.session_state.page = page_name
    return False


# ============================================================
# AUTH SCREEN
# ============================================================

def render_auth():
    st.markdown('<div class="auth-page">', unsafe_allow_html=True)
    st.markdown('<div class="auth-container">', unsafe_allow_html=True)
    st.markdown('<div class="auth-card">', unsafe_allow_html=True)

    st.markdown(
        '<div class="auth-brand">📘 HR Copilot</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="auth-sub">Acme Corp · Employee Handbook</div>',
        unsafe_allow_html=True,
    )

    tab_login, tab_signup = st.tabs(["Log in", "Sign up"])

    with tab_login:
        with st.form("login_form_unique"):
            email = st.text_input("Email", key="unique_login_email")
            password = st.text_input(
                "Password",
                type="password",
                key="unique_login_password",
            )
            submitted = st.form_submit_button(
                "Log in",
                use_container_width=True,
            )

        if submitted:
            if not email or not password:
                st.error("Enter your email and password.")
            else:
                with st.spinner("Signing you in..."):
                    result = api_post(
                        "/login",
                        {
                            "user_email": email,
                            "user_password": password,
                        },
                    )

                if result.get("status"):
                    data = result["data"]
                    st.session_state.token = data["token"]
                    st.session_state.user_name = data["user_name"]
                    st.session_state.user_email = data["user_email"]
                    st.session_state.page = "chat"
                    st.success("Successfully signed in! Redirecting...")
                    st.rerun()
                else:
                    st.error(result.get("message", "Login failed."))

    with tab_signup:
        with st.form("signup_form_unique"):
            name = st.text_input("Full name", key="unique_signup_name")
            email = st.text_input("Email", key="unique_signup_email")
            password = st.text_input(
                "Password",
                type="password",
                key="unique_signup_password",
            )
            submitted = st.form_submit_button(
                "Create account",
                use_container_width=True,
            )

        if submitted:
            if not name or not email or not password:
                st.error("Fill in all fields.")
            else:
                with st.spinner("Creating your account..."):
                    result = api_post(
                        "/signup",
                        {
                            "user_name": name,
                            "user_email": email,
                            "user_password": password,
                        },
                    )

                if result.get("status"):
                    data = result["data"]
                    st.session_state.token = data["token"]
                    st.session_state.user_name = data["user_name"]
                    st.session_state.user_email = data["user_email"]
                    st.session_state.page = "chat"
                    st.success("Account created successfully! Redirecting...")
                    st.rerun()
                else:
                    st.error(result.get("message", "Signup failed."))

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# SIDEBAR
# ============================================================

def render_sidebar():
    with st.sidebar:
        st.markdown(
            '<div class="app-title">📘 HR Copilot</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="app-caption">Acme Corp Handbook</div>',
            unsafe_allow_html=True,
        )

        st.write("")

        if st.session_state.token:
            st.write(f"Signed in as **{st.session_state.user_name}**")
            st.caption(st.session_state.user_email)
        else:
            st.caption("Guest mode")

        st.write("")

        if st.button("⌂  Dashboard", key="sidebar_dashboard", use_container_width=True):
            st.session_state.page = "dashboard"
            st.rerun()

        if st.button("💬  Chat", key="sidebar_chat", use_container_width=True):
            require_auth("chat")
            st.rerun()

        if st.button("↻  Chat History", key="sidebar_history", use_container_width=True):
            require_auth("history")
            st.rerun()

        if st.session_state.token:
            if st.button("🗑  New conversation", key="sidebar_new_conv", use_container_width=True):
                st.session_state.messages = []
                st.session_state.last_sources = []
                st.session_state.page = "chat"
                st.rerun()

            st.write("")

            if st.button("Log out", key="sidebar_logout", use_container_width=True):
                logout()
                st.rerun()
        else:
            st.write("")

            if st.button("Log in", key="sidebar_login", use_container_width=True):
                st.session_state.page = "login"
                st.rerun()

            if st.button("Sign up", key="sidebar_signup", use_container_width=True):
                st.session_state.page = "signup"
                st.rerun()


# ============================================================
# AUTH REQUIRED MESSAGE
# ============================================================

def render_auth_required(feature: str):
    if feature == "history":
        title = "Chat history requires an account"
        message = "Please log in or sign up first to view your previous conversations."
    else:
        title = "Chat requires an account"
        message = "Please log in or sign up first to use HR Copilot."

    st.markdown(
        f"""
        <div class="auth-required">
            <div class="auth-required-title">🔒 {title}</div>
            <div class="auth-required-text">{message}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, _ = st.columns([1, 1, 2])

    with col1:
        if st.button("Log in", key=f"{feature}_login_req"):
            st.session_state.page = "login"
            st.rerun()

    with col2:
        if st.button("Sign up", key=f"{feature}_signup_req"):
            st.session_state.page = "signup"
            st.rerun()


# ============================================================
# DASHBOARD
# ============================================================

def render_dashboard():
    st.markdown('<div class="dashboard-wrap">', unsafe_allow_html=True)

    st.markdown(
        '<div class="dashboard-kicker">Employee Handbook</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="dashboard-title">HR decisions, made simpler.</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="dashboard-subtitle">
            HR Copilot helps employees find answers from company HR policies,
            including leave, work from home, probation, notice period,
            reimbursement, holidays, and exit policies.
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3, gap="medium")

    with col1:
        st.markdown(
            """
            <div class="dashboard-card">
                <div class="dashboard-card-icon">💬</div>
                <div class="dashboard-card-title">Ask HR Copilot</div>
                <div class="dashboard-card-text">
                    Ask questions in natural language and get answers grounded
                    in the company's HR policy documents.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div class="dashboard-card">
                <div class="dashboard-card-icon">📚</div>
                <div class="dashboard-card-title">Policy References</div>
                <div class="dashboard-card-text">
                    Answers can show the source document and relevant page or
                    spreadsheet row used by the RAG system.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            """
            <div class="dashboard-card">
                <div class="dashboard-card-icon">🕘</div>
                <div class="dashboard-card-title">Chat History</div>
                <div class="dashboard-card-text">
                    Keep your previous HR questions and answers available after
                    signing in to your account.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")
    st.write("")

    if st.session_state.token:
        st.success(
            f"Welcome back, {st.session_state.user_name}. "
            "You are signed in and can use Chat and Chat History."
        )

        if st.button("💬 Start a conversation", key="dash_start_conv", use_container_width=True):
            st.session_state.page = "chat"
            st.rerun()
    else:
        st.info(
            "You are currently browsing as a guest. "
            "Log in or sign up to use Chat and Chat History."
        )

        col1, col2 = st.columns(2, gap="medium")

        with col1:
            if st.button("Log in", key="dash_login_btn", use_container_width=True):
                st.session_state.page = "login"
                st.rerun()

        with col2:
            if st.button("Sign up", key="dash_signup_btn", use_container_width=True):
                st.session_state.page = "signup"
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# CHAT HISTORY
# ============================================================

def load_chat_history():
    result = api_get(
        "/chat-history",
        token=st.session_state.token,
    )

    if not result.get("status"):
        st.error(result.get("message", "Could not load chat history."))
        return False

    history = result["data"]["history"]
    messages = []

    for item in history:
        messages.append(
            {
                "role": "user",
                "content": item["user_query"],
            }
        )
        messages.append(
            {
                "role": "assistant",
                "content": item["bot_response"],
            }
        )

    st.session_state.messages = messages
    return True


def render_history():
    st.markdown("### Chat History")
    st.caption("Your previous HR Copilot conversations.")

    if not st.session_state.token:
        render_auth_required("history")
        return

    if st.button("↻ Reload history", key="reload_history_btn"):
        if load_chat_history():
            st.rerun()

    if not st.session_state.messages:
        st.info("No chat history found yet.")
        return

    for message in st.session_state.messages:
        render_bubble(
            message["role"],
            message["content"],
            is_error=message.get("is_error", False),
        )


# ============================================================
# CHAT RENDERING
# ============================================================

def render_bubble(role: str, content: str, is_error: bool = False):
    if role == "user":
        st.markdown(
            f"""
            <div class="chat-row user">
                <div class="bubble bubble-user">{content}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        bubble_class = "bubble-error" if is_error else "bubble-assistant"
        label = (
            "HR Copilot · could not answer"
            if is_error
            else "HR Copilot"
        )

        st.markdown(
            f"""
            <div class="chat-row assistant">
                <div class="bubble {bubble_class}">
                    <div class="bubble-label">{label}</div>
                    {content}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


FILE_ICONS = {
    "pdf": "📄",
    ".pdf": "📄",
    "xlsx": "📊",
    ".xlsx": "📊",
    "docx": "📝",
    ".docx": "📝",
}


def render_source_chip(source: dict):
    file_name = source.get("file_name") or "Unknown file"
    file_type = (source.get("file_type") or "").lstrip(".")
    icon = FILE_ICONS.get(source.get("file_type", ""), "📎")

    if source.get("page_number") is not None:
        ref = f"PAGE {source['page_number']}"
    elif source.get("row_number") is not None:
        ref = f"ROW {source['row_number']}"
    else:
        ref = file_type.upper() or "SOURCE"

    st.markdown(
        f"""
        <div class="source-chip">
            <div class="source-chip-top">{icon} {file_name}</div>
            <div class="source-chip-ref">{ref}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_reference_rail():
    st.markdown(
        '<div class="rail-heading">References</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="rail-sub">Cited in the latest answer</div>',
        unsafe_allow_html=True,
    )

    if not st.session_state.last_sources:
        st.markdown(
            '<div class="rail-empty">'
            "Sources will appear here once you ask a question."
            "</div>",
            unsafe_allow_html=True,
        )
        return

    for source in st.session_state.last_sources:
        render_source_chip(source)


# ============================================================
# CHAT
# ============================================================

def render_chat():
    if not st.session_state.token:
        st.markdown("### HR Copilot")
        render_auth_required("chat")
        return

    col_chat, col_rail = st.columns([2.3, 1], gap="large")

    with col_chat:
        st.markdown("### Ask about company policy")

        # Example Questions reference box for users
        st.markdown(
            """
            <div class="suggestions-box">
                <div class="suggestions-title">💡 Example Questions to Try</div>
                <div class="suggestion-item">1. How many annual leave days do employees get?</div>
                <div class="suggestion-item">2. Do I need a medical certificate for sick leave?</div>
                <div class="suggestion-item">3. What is the standard notice period, and how does it change during probation?</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        for message in st.session_state.messages:
            render_bubble(
                message["role"],
                message["content"],
                is_error=message.get("is_error", False),
            )

        prompt = st.chat_input(
            "Ask about leave, WFH, notice period, reimbursement…"
        )

        if prompt:
            st.session_state.messages.append(
                {
                    "role": "user",
                    "content": prompt,
                }
            )

            with st.spinner("Searching HR policies and generating answer..."):
                result = api_post(
                    "/chat",
                    {"query": prompt},
                    token=st.session_state.token,
                )

            if result.get("status"):
                answer = result["data"]["answer"]
                sources = result["data"].get("sources", [])

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                    }
                )
                st.session_state.last_sources = sources

            else:
                error_message = result.get(
                    "message",
                    "Something went wrong.",
                )

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": error_message,
                        "is_error": True,
                    }
                )
                st.session_state.last_sources = []

            st.rerun()

    with col_rail:
        render_reference_rail()


# ============================================================
# PAGE ROUTER
# ============================================================

def render_page():
    page = st.session_state.page

    if page == "dashboard":
        render_dashboard()
    elif page == "login":
        render_auth()
    elif page == "signup":
        render_auth()
    elif page == "chat":
        render_chat()
    elif page == "history":
        render_history()
    else:
        st.session_state.page = "dashboard"
        st.rerun()


# ============================================================
# ENTRY POINT
# ============================================================

def main():
    inject_css()
    init_state()
    render_sidebar()
    render_page()


if __name__ == "__main__":
    main()