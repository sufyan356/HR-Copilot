# """
# HR Copilot — Streamlit frontend

# A thin UI layer over the FastAPI backend:

#     POST /signup
#     POST /login
#     POST /chat
#     GET  /chat-history

# Run:
#     uv run streamlit run FRONTEND/app.py
# """

# import requests
# import streamlit as st


# # ============================================================
# # CONFIG
# # ============================================================

# API_BASE_URL = "http://127.0.0.1:8000"

# st.set_page_config(
#     page_title="HR Copilot — Acme Corp",
#     page_icon="📘",
#     layout="wide",
#     initial_sidebar_state="expanded",
# )


# # ============================================================
# # CSS
# # ============================================================

# def inject_css():

#     st.markdown(
#         """
#         <style>

#         @import url(
#             'https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap'
#         );

#         :root {
#             --ink: #16233F;
#             --paper: #F3F5F8;
#             --card: #FFFFFF;
#             --signal: #2F6F52;
#             --signal-dark: #244F3D;
#             --amber: #D98E2B;
#             --ash: #6B7280;
#             --rust: #B23A34;
#             --line: #E2E6ED;
#         }

#         /* ====================================================
#            GLOBAL
#            ==================================================== */

#         .stApp {
#             background: var(--paper);
#         }

#         html,
#         body,
#         [class*="css"] {
#             font-family: 'IBM Plex Sans', sans-serif;
#         }

#         h1,
#         h2,
#         h3 {
#             font-family: 'Fraunces', serif !important;
#             color: var(--ink) !important;
#         }


#         /* ====================================================
#            SIDEBAR
#            ==================================================== */

#         [data-testid="stSidebar"] {
#             background: var(--ink);
#         }

#         [data-testid="stSidebar"] * {
#             color: #EDEFF4 !important;
#         }

#         [data-testid="stSidebar"] .stButton button {
#             background: transparent !important;
#             border: 1px solid rgba(255,255,255,0.25) !important;
#             color: #EDEFF4 !important;
#             border-radius: 8px !important;
#         }

#         [data-testid="stSidebar"] .stButton button:hover {
#             border-color: var(--amber) !important;
#             color: var(--amber) !important;
#         }

#         .sidebar-title {
#             font-family: 'Fraunces', serif;
#             font-size: 1.55rem;
#             font-weight: 600;
#             color: #EDEFF4;
#         }

#         .sidebar-caption {
#             font-family: 'IBM Plex Mono', monospace;
#             font-size: 0.72rem;
#             letter-spacing: 0.05em;
#             text-transform: uppercase;
#             color: var(--amber);
#         }


#         /* ====================================================
#            BUTTONS
#            ==================================================== */

#         .stButton button {
#             border-radius: 8px !important;
#         }


#         /* ====================================================
#            AUTH FORM
#            ==================================================== */

#         .auth-spacer {
#             height: 25px;
#         }

#         .auth-title {
#             text-align: center;
#             font-family: 'Fraunces', serif;
#             font-size: 2rem;
#             font-weight: 600;
#             color: var(--ink);
#         }

#         .auth-subtitle {
#             text-align: center;
#             font-family: 'IBM Plex Mono', monospace;
#             font-size: 0.72rem;
#             color: var(--ash);
#             text-transform: uppercase;
#             letter-spacing: 0.05em;
#             margin-bottom: 1.3rem;
#         }

#         /* ====================================================
#            INPUTS
#            ==================================================== */

#         .stTextInput input {
#             background-color: #FFFFFF !important;
#             color: #16233F !important;
#             border: 1px solid #E2E6ED !important;
#             border-radius: 8px !important;
#         }

#         .stTextInput input:focus {
#             border-color: #2F6F52 !important;
#             box-shadow: 0 0 0 1px #2F6F52 !important;
#         }

#         .stTextInput label {
#             color: #16233F !important;
#         }


#         /* ====================================================
#            DASHBOARD
#            ==================================================== */

#         .dashboard-kicker {
#             font-family: 'IBM Plex Mono', monospace;
#             font-size: 0.75rem;
#             text-transform: uppercase;
#             letter-spacing: 0.08em;
#             color: var(--amber);
#             margin-top: 1rem;
#             margin-bottom: 0.5rem;
#         }

#         .dashboard-title {
#             font-family: 'Fraunces', serif;
#             font-size: clamp(2.8rem, 6vw, 5.2rem);
#             line-height: 0.98;
#             font-weight: 600;
#             color: var(--ink);
#             margin-bottom: 1rem;
#         }

#         .dashboard-subtitle {
#             max-width: 720px;
#             font-size: 1.08rem;
#             line-height: 1.7;
#             color: var(--ash);
#             margin-bottom: 2rem;
#         }


#         /* ====================================================
#            CHAT
#            ==================================================== */

#         [data-testid="stChatMessage"] {
#             border-radius: 12px;
#             margin-bottom: 0.75rem;
#         }

#         [data-testid="stChatMessageContent"] {
#             line-height: 1.6;
#         }


#         /* ====================================================
#            REFERENCE CARDS
#            ==================================================== */

#         .reference-title {
#             font-family: 'Fraunces', serif;
#             font-size: 1.1rem;
#             font-weight: 600;
#             color: var(--ink);
#         }

#         .reference-subtitle {
#             font-family: 'IBM Plex Mono', monospace;
#             font-size: 0.68rem;
#             color: var(--ash);
#             text-transform: uppercase;
#             letter-spacing: 0.04em;
#         }


#         /* ====================================================
#            MOBILE
#            ==================================================== */

#         @media (max-width: 900px) {

#             .dashboard-title {
#                 font-size: 3rem;
#             }

#         }

#         </style>
#         """,
#         unsafe_allow_html=True,
#     )


# # ============================================================
# # API HELPERS
# # ============================================================

# def api_post(
#     path: str,
#     payload: dict,
#     token: str | None = None,
# ) -> dict:

#     headers = {}

#     if token:
#         headers["Authorization"] = f"Bearer {token}"

#     try:

#         response = requests.post(
#             f"{API_BASE_URL}{path}",
#             json=payload,
#             headers=headers,
#             timeout=60,
#         )

#         return response.json()

#     except requests.exceptions.RequestException:

#         return {
#             "status": False,
#             "error": "CONNECTION_ERROR",
#             "message": (
#                 "Could not reach the HR Copilot API. "
#                 "Is the backend running?"
#             ),
#             "data": None,
#         }


# def api_get(
#     path: str,
#     token: str | None = None,
# ) -> dict:

#     headers = {}

#     if token:
#         headers["Authorization"] = f"Bearer {token}"

#     try:

#         response = requests.get(
#             f"{API_BASE_URL}{path}",
#             headers=headers,
#             timeout=30,
#         )

#         return response.json()

#     except requests.exceptions.RequestException:

#         return {
#             "status": False,
#             "error": "CONNECTION_ERROR",
#             "message": (
#                 "Could not reach the HR Copilot API. "
#                 "Is the backend running?"
#             ),
#             "data": None,
#         }


# # ============================================================
# # SESSION STATE
# # ============================================================

# def init_state():

#     defaults = {
#         "token": None,
#         "user_name": None,
#         "user_email": None,
#         "messages": [],
#         "last_sources": [],
#         "page": "dashboard",
#         "history_loaded": False,
#     }

#     for key, value in defaults.items():

#         if key not in st.session_state:
#             st.session_state[key] = value


# def logout():

#     st.session_state.token = None
#     st.session_state.user_name = None
#     st.session_state.user_email = None
#     st.session_state.messages = []
#     st.session_state.last_sources = []
#     st.session_state.history_loaded = False
#     st.session_state.page = "dashboard"


# # ============================================================
# # AUTH REQUIRED
# # ============================================================

# def require_auth(page_name: str):

#     st.session_state.page = page_name

#     return bool(st.session_state.token)


# def render_auth_required(feature: str):

#     if feature == "history":

#         st.warning(
#             "🔒 Chat history requires an account.\n\n"
#             "Please log in or sign up first to view your "
#             "previous conversations."
#         )

#     else:

#         st.warning(
#             "🔒 Chat requires an account.\n\n"
#             "Please log in or sign up first to use HR Copilot."
#         )

#     col1, col2, _ = st.columns([1, 1, 3])

#     with col1:

#         if st.button(
#             "Log in",
#             key=f"{feature}_login",
#             use_container_width=True,
#         ):

#             st.session_state.page = "login"
#             st.rerun()

#     with col2:

#         if st.button(
#             "Sign up",
#             key=f"{feature}_signup",
#             use_container_width=True,
#         ):

#             st.session_state.page = "signup"
#             st.rerun()


# # ============================================================
# # AUTH PAGE
# # ============================================================

# def render_auth():

#     st.markdown(
#         '<div class="auth-spacer"></div>',
#         unsafe_allow_html=True,
#     )

#     left, center, right = st.columns(
#         [1, 2, 1]
#     )

#     with center:

#         # Native Streamlit container.
#         # No HTML card wrapper.
#         with st.container(
#             border=True,
#         ):

#             st.markdown(
#                 '<div class="auth-title">'
#                 '📘 HR Copilot'
#                 '</div>',
#                 unsafe_allow_html=True,
#             )

#             st.markdown(
#                 '<div class="auth-subtitle">'
#                 'Acme Corp · Employee Handbook'
#                 '</div>',
#                 unsafe_allow_html=True,
#             )

#             tab_login, tab_signup = st.tabs(
#                 ["Log in", "Sign up"]
#             )


#             # =================================================
#             # LOGIN
#             # =================================================

#             with tab_login:

#                 with st.form("login_form"):

#                     email = st.text_input(
#                         "Email",
#                         key="login_email",
#                     )

#                     password = st.text_input(
#                         "Password",
#                         type="password",
#                         key="login_password",
#                     )

#                     submitted = st.form_submit_button(
#                         "Log in",
#                         use_container_width=True,
#                     )

#                 if submitted:

#                     if not email or not password:

#                         st.error(
#                             "Enter your email and password."
#                         )

#                     else:

#                         result = api_post(
#                             "/login",
#                             {
#                                 "user_email": email,
#                                 "user_password": password,
#                             },
#                         )

#                         if result.get("status"):

#                             data = result["data"]

#                             st.session_state.token = data["token"]
#                             st.session_state.user_name = data["user_name"]
#                             st.session_state.user_email = data["user_email"]
#                             st.session_state.page = "chat"
#                             st.session_state.messages = []
#                             st.session_state.last_sources = []

#                             st.rerun()

#                         else:

#                             st.error(
#                                 result.get(
#                                     "message",
#                                     "Login failed.",
#                                 )
#                             )


#             # =================================================
#             # SIGN UP
#             # =================================================

#             with tab_signup:

#                 with st.form("signup_form"):

#                     name = st.text_input(
#                         "Full name",
#                         key="signup_name",
#                     )

#                     email = st.text_input(
#                         "Email",
#                         key="signup_email",
#                     )

#                     password = st.text_input(
#                         "Password",
#                         type="password",
#                         key="signup_password",
#                     )

#                     submitted = st.form_submit_button(
#                         "Create account",
#                         use_container_width=True,
#                     )

#                 if submitted:

#                     if not name or not email or not password:

#                         st.error(
#                             "Fill in all fields."
#                         )

#                     else:

#                         result = api_post(
#                             "/signup",
#                             {
#                                 "user_name": name,
#                                 "user_email": email,
#                                 "user_password": password,
#                             },
#                         )

#                         if result.get("status"):

#                             data = result["data"]

#                             st.session_state.token = data["token"]
#                             st.session_state.user_name = data["user_name"]
#                             st.session_state.user_email = data["user_email"]
#                             st.session_state.page = "chat"
#                             st.session_state.messages = []
#                             st.session_state.last_sources = []

#                             st.rerun()

#                         else:

#                             st.error(
#                                 result.get(
#                                     "message",
#                                     "Signup failed.",
#                                 )
#                             )


# # ============================================================
# # SIDEBAR
# # ============================================================

# def render_sidebar():

#     with st.sidebar:

#         st.markdown(
#             '<div class="sidebar-title">'
#             '📘 HR Copilot'
#             '</div>',
#             unsafe_allow_html=True,
#         )

#         st.markdown(
#             '<div class="sidebar-caption">'
#             'Acme Corp Handbook'
#             '</div>',
#             unsafe_allow_html=True,
#         )

#         st.write("")

#         if st.session_state.token:

#             st.write(
#                 f"Signed in as "
#                 f"**{st.session_state.user_name}**"
#             )

#             st.caption(
#                 st.session_state.user_email
#             )

#         else:

#             st.caption("Guest mode")

#         st.write("")


#         # Dashboard

#         if st.button(
#             "⌂  Dashboard",
#             use_container_width=True,
#         ):

#             st.session_state.page = "dashboard"
#             st.rerun()


#         # Chat

#         if st.button(
#             "💬  Chat",
#             use_container_width=True,
#         ):

#             st.session_state.page = "chat"
#             st.rerun()


#         # History

#         if st.button(
#             "↻  Chat History",
#             use_container_width=True,
#         ):

#             st.session_state.page = "history"
#             st.rerun()


#         st.write("")


#         if st.session_state.token:

#             if st.button(
#                 "🗑  New conversation",
#                 use_container_width=True,
#             ):

#                 st.session_state.messages = []
#                 st.session_state.last_sources = []
#                 st.session_state.page = "chat"

#                 st.rerun()

#             st.write("")

#             if st.button(
#                 "Log out",
#                 use_container_width=True,
#             ):

#                 logout()
#                 st.rerun()

#         else:

#             if st.button(
#                 "Log in",
#                 use_container_width=True,
#             ):

#                 st.session_state.page = "login"
#                 st.rerun()

#             if st.button(
#                 "Sign up",
#                 use_container_width=True,
#             ):

#                 st.session_state.page = "signup"
#                 st.rerun()


# # ============================================================
# # DASHBOARD
# # ============================================================

# def render_dashboard():

#     st.markdown(
#         '<div class="dashboard-kicker">'
#         'Acme Corp · Employee Handbook'
#         '</div>',
#         unsafe_allow_html=True,
#     )

#     st.markdown(
#         '<div class="dashboard-title">'
#         'HR decisions, made simpler.'
#         '</div>',
#         unsafe_allow_html=True,
#     )

#     st.markdown(
#         """
#         <div class="dashboard-subtitle">
#             HR Copilot helps employees find answers from company HR policies,
#             including leave, work from home, probation, notice period,
#             reimbursement, holidays, and exit policies.
#         </div>
#         """,
#         unsafe_allow_html=True,
#     )


#     # ========================================================
#     # NATIVE STREAMLIT CARDS
#     # ========================================================

#     col1, col2, col3 = st.columns(
#         3,
#         gap="medium",
#     )


#     # ========================================================
#     # CARD 1
#     # ========================================================

#     with col1:

#         with st.container(
#             border=True,
#         ):

#             st.markdown("## 💬")

#             st.subheader(
#                 "Ask HR Copilot"
#             )

#             st.write(
#                 "Ask questions in natural language and "
#                 "get answers grounded in the company's "
#                 "HR policy documents."
#             )


#     # ========================================================
#     # CARD 2
#     # ========================================================

#     with col2:

#         with st.container(
#             border=True,
#         ):

#             st.markdown("## 📚")

#             st.subheader(
#                 "Policy References"
#             )

#             st.write(
#                 "Answers can show the source document "
#                 "and relevant page or spreadsheet row "
#                 "used by the RAG system."
#             )


#     # ========================================================
#     # CARD 3
#     # ========================================================

#     with col3:

#         with st.container(
#             border=True,
#         ):

#             st.markdown("## 🕘")

#             st.subheader(
#                 "Chat History"
#             )

#             st.write(
#                 "Keep your previous HR questions and "
#                 "answers available after signing in "
#                 "to your account."
#             )


#     st.write("")
#     st.write("")


#     # ========================================================
#     # USER STATE
#     # ========================================================

#     if st.session_state.token:

#         st.success(
#             f"Welcome back, {st.session_state.user_name}. "
#             "You are signed in and can use Chat and Chat History."
#         )

#         if st.button(
#             "💬 Start a conversation",
#             use_container_width=True,
#         ):

#             st.session_state.page = "chat"
#             st.rerun()

#     else:

#         st.info(
#             "You are currently browsing as a guest. "
#             "Log in or sign up to use Chat and Chat History."
#         )

#         col1, col2 = st.columns(2)

#         with col1:

#             if st.button(
#                 "Log in",
#                 use_container_width=True,
#             ):

#                 st.session_state.page = "login"
#                 st.rerun()

#         with col2:

#             if st.button(
#                 "Sign up",
#                 use_container_width=True,
#             ):

#                 st.session_state.page = "signup"
#                 st.rerun()


# # ============================================================
# # LOAD CHAT HISTORY
# # ============================================================

# def load_chat_history():

#     if not st.session_state.token:
#         return False

#     result = api_get(
#         "/chat-history",
#         token=st.session_state.token,
#     )

#     if not result.get("status"):

#         st.error(
#             result.get(
#                 "message",
#                 "Could not load chat history.",
#             )
#         )

#         return False


#     data = result.get("data") or {}

#     history = data.get(
#         "history",
#         [],
#     )


#     messages = []


#     for item in history:

#         user_query = item.get(
#             "user_query",
#             "",
#         )

#         bot_response = item.get(
#             "bot_response",
#             "",
#         )


#         messages.append(
#             {
#                 "role": "user",
#                 "content": user_query,
#             }
#         )

#         messages.append(
#             {
#                 "role": "assistant",
#                 "content": bot_response,
#             }
#         )


#     st.session_state.messages = messages
#     st.session_state.history_loaded = True

#     return True


# # ============================================================
# # CHAT MESSAGE
# # ============================================================

# def render_message(
#     role: str,
#     content: str,
#     is_error: bool = False,
# ):

#     if role == "user":

#         with st.chat_message(
#             "user",
#         ):

#             st.write(content)

#     else:

#         if is_error:

#             with st.chat_message(
#                 "assistant",
#             ):

#                 st.error(content)

#         else:

#             with st.chat_message(
#                 "assistant",
#             ):

#                 st.write(content)


# # ============================================================
# # CHAT HISTORY PAGE
# # ============================================================

# def render_history():

#     if not st.session_state.token:

#         st.title(
#             "Chat History"
#         )

#         render_auth_required(
#             "history"
#         )

#         return


#     st.title(
#         "Chat History"
#     )

#     st.caption(
#         "Your previous HR Copilot conversations."
#     )


#     # --------------------------------------------------------
#     # RELOAD
#     # --------------------------------------------------------

#     if st.button(
#         "↻ Reload history",
#     ):

#         if load_chat_history():
#             st.rerun()


#     # --------------------------------------------------------
#     # AUTOMATIC FIRST LOAD
#     # --------------------------------------------------------

#     if not st.session_state.history_loaded:

#         with st.spinner(
#             "Loading your chat history..."
#         ):

#             load_chat_history()


#     # --------------------------------------------------------
#     # NO HISTORY
#     # --------------------------------------------------------

#     if not st.session_state.messages:

#         st.info(
#             "No chat history found yet."
#         )

#         return


#     # --------------------------------------------------------
#     # DISPLAY HISTORY
#     # --------------------------------------------------------

#     for message in st.session_state.messages:

#         render_message(
#             role=message["role"],
#             content=message["content"],
#             is_error=message.get(
#                 "is_error",
#                 False,
#             ),
#         )


# # ============================================================
# # FILE ICONS
# # ============================================================

# FILE_ICONS = {
#     "pdf": "📄",
#     ".pdf": "📄",
#     "xlsx": "📊",
#     ".xlsx": "📊",
#     "docx": "📝",
#     ".docx": "📝",
#     "txt": "📃",
#     ".txt": "📃",
# }


# # ============================================================
# # SOURCE
# # ============================================================

# def render_source(source: dict):

#     file_name = source.get(
#         "file_name",
#         "Unknown file",
#     )

#     file_type = (
#         source.get(
#             "file_type",
#             "",
#         )
#         or ""
#     ).lstrip(".")

#     icon = FILE_ICONS.get(
#         source.get(
#             "file_type",
#             "",
#         ),
#         "📎",
#     )


#     if source.get("page_number") is not None:

#         reference = (
#             f"Page {source['page_number']}"
#         )

#     elif source.get("row_number") is not None:

#         reference = (
#             f"Row {source['row_number']}"
#         )

#     else:

#         reference = (
#             file_type.upper()
#             if file_type
#             else "SOURCE"
#         )


#     with st.container(
#         border=True,
#     ):

#         st.write(
#             f"{icon} **{file_name}**"
#         )

#         st.caption(
#             reference
#         )


# # ============================================================
# # REFERENCE RAIL
# # ============================================================

# def render_reference_rail():

#     st.subheader(
#         "References"
#     )

#     st.caption(
#         "Cited in the latest answer"
#     )


#     if not st.session_state.last_sources:

#         st.info(
#             "Sources will appear here once "
#             "you ask a question."
#         )

#         return


#     for source in st.session_state.last_sources:

#         render_source(
#             source
#         )


# # ============================================================
# # CHAT PAGE
# # ============================================================

# def render_chat():

#     if not st.session_state.token:

#         st.title(
#             "HR Copilot"
#         )

#         render_auth_required(
#             "chat"
#         )

#         return


#     col_chat, col_rail = st.columns(
#         [2.3, 1],
#         gap="large",
#     )


#     # ========================================================
#     # CHAT
#     # ========================================================

#     with col_chat:

#         st.title(
#             "Ask about company policy"
#         )

#         st.caption(
#             "Ask questions about leave, WFH, "
#             "notice period, reimbursement and other "
#             "HR policies."
#         )


#         # ----------------------------------------------------
#         # PREVIOUS MESSAGES
#         # ----------------------------------------------------

#         for message in st.session_state.messages:

#             render_message(
#                 role=message["role"],
#                 content=message["content"],
#                 is_error=message.get(
#                     "is_error",
#                     False,
#                 ),
#             )


#         # ----------------------------------------------------
#         # INPUT
#         # ----------------------------------------------------

#         prompt = st.chat_input(
#             "Ask about leave, WFH, notice period, reimbursement…"
#         )


#         if prompt:

#             # ------------------------------------------------
#             # SHOW USER MESSAGE
#             # ------------------------------------------------

#             st.session_state.messages.append(
#                 {
#                     "role": "user",
#                     "content": prompt,
#                 }
#             )


#             # ------------------------------------------------
#             # API REQUEST + LOADING
#             # ------------------------------------------------

#             with st.chat_message(
#                 "assistant"
#             ):

#                 with st.spinner(
#                     "🤖 HR Copilot is thinking..."
#                 ):

#                     result = api_post(
#                         "/chat",
#                         {
#                             "query": prompt,
#                         },
#                         token=st.session_state.token,
#                     )


#             # ------------------------------------------------
#             # SUCCESS
#             # ------------------------------------------------

#             if result.get("status"):

#                 data = result.get(
#                     "data",
#                     {},
#                 )

#                 answer = data.get(
#                     "answer",
#                     "I could not generate an answer.",
#                 )

#                 sources = data.get(
#                     "sources",
#                     [],
#                 )


#                 st.session_state.messages.append(
#                     {
#                         "role": "assistant",
#                         "content": answer,
#                     }
#                 )

#                 st.session_state.last_sources = sources


#             # ------------------------------------------------
#             # ERROR
#             # ------------------------------------------------

#             else:

#                 error_message = result.get(
#                     "message",
#                     "Something went wrong.",
#                 )

#                 st.session_state.messages.append(
#                     {
#                         "role": "assistant",
#                         "content": error_message,
#                         "is_error": True,
#                     }
#                 )

#                 st.session_state.last_sources = []


#             # Re-render page

#             st.rerun()


#     # ========================================================
#     # REFERENCES
#     # ========================================================

#     with col_rail:

#         render_reference_rail()


# # ============================================================
# # PAGE ROUTER
# # ============================================================

# def render_page():

#     page = st.session_state.page


#     if page == "dashboard":

#         render_dashboard()


#     elif page == "login":

#         render_auth()


#     elif page == "signup":

#         render_auth()


#     elif page == "chat":

#         render_chat()


#     elif page == "history":

#         render_history()


#     else:

#         st.session_state.page = "dashboard"

#         st.rerun()


# # ============================================================
# # MAIN
# # ============================================================

# def main():

#     inject_css()

#     init_state()

#     render_sidebar()

#     render_page()


# # ============================================================
# # ENTRY POINT
# # ============================================================

# if __name__ == "__main__":

#     main()

"""
HR Copilot — Streamlit frontend

A thin UI layer over the FastAPI backend:

    POST /signup
    POST /login
    POST /chat
    GET  /chat-history

Run:
    uv run streamlit run FRONTEND/app.py
"""

import requests
import streamlit as st


# ============================================================
# CONFIG
# ============================================================

API_BASE_URL = st.secrets.get(
    "API_BASE_URL",          # ← Streamlit Cloud Secret
    "http://127.0.0.1:8000", # ← Local fallback
).rstrip("/")

st.set_page_config(
    page_title="HR Copilot — Acme Corp",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CSS
# ============================================================

def inject_css():

    st.markdown(
        """
        <style>

        @import url(
            'https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap'
        );

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

        /* ====================================================
           GLOBAL
           ==================================================== */

        .stApp {
            background: var(--paper);
        }

        html,
        body,
        [class*="css"] {
            font-family: 'IBM Plex Sans', sans-serif;
        }

        h1,
        h2,
        h3 {
            font-family: 'Fraunces', serif !important;
            color: var(--ink) !important;
        }


        /* ====================================================
           SIDEBAR
           ==================================================== */

        [data-testid="stSidebar"] {
            background: var(--ink);
        }

        [data-testid="stSidebar"] * {
            color: #EDEFF4 !important;
        }

        [data-testid="stSidebar"] .stButton button {
            background: transparent !important;
            border: 1px solid rgba(255,255,255,0.25) !important;
            color: #EDEFF4 !important;
            border-radius: 8px !important;
        }

        [data-testid="stSidebar"] .stButton button:hover {
            border-color: var(--amber) !important;
            color: var(--amber) !important;
        }

        .sidebar-title {
            font-family: 'Fraunces', serif;
            font-size: 1.55rem;
            font-weight: 600;
            color: #EDEFF4;
        }

        .sidebar-caption {
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.72rem;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            color: var(--amber);
        }


        /* ====================================================
           BUTTONS
           ==================================================== */

        .stButton button {
            border-radius: 8px !important;
        }


        /* ====================================================
           AUTH FORM
           ==================================================== */

        .auth-spacer {
            height: 25px;
        }

        .auth-title {
            text-align: center;
            font-family: 'Fraunces', serif;
            font-size: 2rem;
            font-weight: 600;
            color: var(--ink);
        }

        .auth-subtitle {
            text-align: center;
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.72rem;
            color: var(--ash);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 1.3rem;
        }


        /* ====================================================
           INPUTS
           ==================================================== */

        .stTextInput input {
            background-color: #FFFFFF !important;
            color: #16233F !important;
            border: 1px solid #E2E6ED !important;
            border-radius: 8px !important;
        }

        .stTextInput input:focus {
            border-color: #2F6F52 !important;
            box-shadow: 0 0 0 1px #2F6F52 !important;
        }

        .stTextInput label {
            color: #16233F !important;
        }


        /* ====================================================
           DASHBOARD
           ==================================================== */

        .dashboard-kicker {
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: var(--amber);
            margin-top: 1rem;
            margin-bottom: 0.5rem;
        }

        .dashboard-title {
            font-family: 'Fraunces', serif;
            font-size: clamp(2.8rem, 6vw, 5.2rem);
            line-height: 0.98;
            font-weight: 600;
            color: var(--ink);
            margin-bottom: 1rem;
        }

        .dashboard-subtitle {
            max-width: 720px;
            font-size: 1.08rem;
            line-height: 1.7;
            color: var(--ash);
            margin-bottom: 2rem;
        }


        /* ====================================================
           CHAT
           ==================================================== */

        [data-testid="stChatMessage"] {
            border-radius: 12px;
            margin-bottom: 0.75rem;
        }

        [data-testid="stChatMessageContent"] {
            line-height: 1.6;
        }


        /* ====================================================
           REFERENCE CARDS
           ==================================================== */

        .reference-title {
            font-family: 'Fraunces', serif;
            font-size: 1.1rem;
            font-weight: 600;
            color: var(--ink);
        }

        .reference-subtitle {
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.68rem;
            color: var(--ash);
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }


        /* ====================================================
           MOBILE
           ==================================================== */

        @media (max-width: 900px) {

            .dashboard-title {
                font-size: 3rem;
            }

        }

        </style>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# API HELPERS
# ============================================================

def api_post(
    path: str,
    payload: dict,
    token: str | None = None,
) -> dict:

    headers = {}

    if token:
        headers["Authorization"] = f"Bearer {token}"

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
            "message": (
                "Could not reach the HR Copilot API. "
                "Is the backend running?"
            ),
            "data": None,
        }


def api_get(
    path: str,
    token: str | None = None,
) -> dict:

    headers = {}

    if token:
        headers["Authorization"] = f"Bearer {token}"

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
            "message": (
                "Could not reach the HR Copilot API. "
                "Is the backend running?"
            ),
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
        "history_loaded": False,
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
    st.session_state.history_loaded = False
    st.session_state.page = "dashboard"


# ============================================================
# AUTH REQUIRED
# ============================================================

def require_auth(page_name: str):

    st.session_state.page = page_name

    return bool(st.session_state.token)


def render_auth_required(feature: str):

    if feature == "history":

        st.warning(
            "🔒 Chat history requires an account.\n\n"
            "Please log in or sign up first to view your "
            "previous conversations."
        )

    else:

        st.warning(
            "🔒 Chat requires an account.\n\n"
            "Please log in or sign up first to use HR Copilot."
        )

    col1, col2, _ = st.columns([1, 1, 3])

    with col1:

        if st.button(
            "Log in",
            key=f"{feature}_login",
            use_container_width=True,
        ):

            st.session_state.page = "login"
            st.rerun()

    with col2:

        if st.button(
            "Sign up",
            key=f"{feature}_signup",
            use_container_width=True,
        ):

            st.session_state.page = "signup"
            st.rerun()


# ============================================================
# AUTH PAGE
# ============================================================

def render_auth():

    st.markdown(
        '<div class="auth-spacer"></div>',
        unsafe_allow_html=True,
    )

    left, center, right = st.columns(
        [1, 2, 1]
    )

    with center:

        with st.container(
            border=True,
        ):

            st.markdown(
                '<div class="auth-title">'
                '📘 HR Copilot'
                '</div>',
                unsafe_allow_html=True,
            )

            st.markdown(
                '<div class="auth-subtitle">'
                'Acme Corp · Employee Handbook'
                '</div>',
                unsafe_allow_html=True,
            )

            tab_login, tab_signup = st.tabs(
                ["Log in", "Sign up"]
            )


            # =================================================
            # LOGIN
            # =================================================

            with tab_login:

                with st.form("login_form"):

                    email = st.text_input(
                        "Email",
                        key="login_email",
                    )

                    password = st.text_input(
                        "Password",
                        type="password",
                        key="login_password",
                    )

                    submitted = st.form_submit_button(
                        "Log in",
                        use_container_width=True,
                    )

                if submitted:

                    if not email or not password:

                        st.error(
                            "Enter your email and password."
                        )

                    else:

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
                            st.session_state.messages = []
                            st.session_state.last_sources = []

                            st.rerun()

                        else:

                            st.error(
                                result.get(
                                    "message",
                                    "Login failed.",
                                )
                            )


            # =================================================
            # SIGN UP
            # =================================================

            with tab_signup:

                with st.form("signup_form"):

                    name = st.text_input(
                        "Full name",
                        key="signup_name",
                    )

                    email = st.text_input(
                        "Email",
                        key="signup_email",
                    )

                    password = st.text_input(
                        "Password",
                        type="password",
                        key="signup_password",
                    )

                    submitted = st.form_submit_button(
                        "Create account",
                        use_container_width=True,
                    )

                if submitted:

                    if not name or not email or not password:

                        st.error(
                            "Fill in all fields."
                        )

                    else:

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
                            st.session_state.messages = []
                            st.session_state.last_sources = []

                            st.rerun()

                        else:

                            st.error(
                                result.get(
                                    "message",
                                    "Signup failed.",
                                )
                            )


# ============================================================
# SIDEBAR
# ============================================================

def render_sidebar():

    with st.sidebar:

        st.markdown(
            '<div class="sidebar-title">'
            '📘 HR Copilot'
            '</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="sidebar-caption">'
            'Acme Corp Handbook'
            '</div>',
            unsafe_allow_html=True,
        )

        st.write("")

        if st.session_state.token:

            st.write(
                f"Signed in as "
                f"**{st.session_state.user_name}**"
            )

            st.caption(
                st.session_state.user_email
            )

        else:

            st.caption("Guest mode")

        st.write("")


        # Dashboard

        if st.button(
            "⌂  Dashboard",
            key="sidebar_dashboard",
            use_container_width=True,
        ):

            st.session_state.page = "dashboard"
            st.rerun()


        # Chat

        if st.button(
            "💬  Chat",
            key="sidebar_chat",
            use_container_width=True,
        ):

            st.session_state.page = "chat"
            st.rerun()


        # History

        if st.button(
            "↻  Chat History",
            key="sidebar_history",
            use_container_width=True,
        ):

            st.session_state.page = "history"
            st.rerun()


        st.write("")


        if st.session_state.token:

            if st.button(
                "🗑  New conversation",
                key="sidebar_new_conversation",
                use_container_width=True,
            ):

                st.session_state.messages = []
                st.session_state.last_sources = []
                st.session_state.page = "chat"

                st.rerun()

            st.write("")

            if st.button(
                "Log out",
                key="sidebar_logout",
                use_container_width=True,
            ):

                logout()
                st.rerun()

        else:

            if st.button(
                "Log in",
                key="sidebar_login",
                use_container_width=True,
            ):

                st.session_state.page = "login"
                st.rerun()

            if st.button(
                "Sign up",
                key="sidebar_signup",
                use_container_width=True,
            ):

                st.session_state.page = "signup"
                st.rerun()


# ============================================================
# DASHBOARD
# ============================================================

def render_dashboard():

    st.markdown(
        '<div class="dashboard-kicker">'
        'Acme Corp · Employee Handbook'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="dashboard-title">'
        'HR decisions, made simpler.'
        '</div>',
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


    # ========================================================
    # NATIVE STREAMLIT CARDS
    # ========================================================

    col1, col2, col3 = st.columns(
        3,
        gap="medium",
    )


    # ========================================================
    # CARD 1
    # ========================================================

    with col1:

        with st.container(
            border=True,
        ):

            st.markdown("## 💬")

            st.subheader(
                "Ask HR Copilot"
            )

            st.write(
                "Ask questions in natural language and "
                "get answers grounded in the company's "
                "HR policy documents."
            )


    # ========================================================
    # CARD 2
    # ========================================================

    with col2:

        with st.container(
            border=True,
        ):

            st.markdown("## 📚")

            st.subheader(
                "Policy References"
            )

            st.write(
                "Answers can show the source document "
                "and relevant page or spreadsheet row "
                "used by the RAG system."
            )


    # ========================================================
    # CARD 3
    # ========================================================

    with col3:

        with st.container(
            border=True,
        ):

            st.markdown("## 🕘")

            st.subheader(
                "Chat History"
            )

            st.write(
                "Keep your previous HR questions and "
                "answers available after signing in "
                "to your account."
            )


    st.write("")
    st.write("")


    # ========================================================
    # USER STATE
    # ========================================================

    if st.session_state.token:

        st.success(
            f"Welcome back, {st.session_state.user_name}. "
            "You are signed in and can use Chat and Chat History."
        )

        if st.button(
            "💬 Start a conversation",
            key="dashboard_start_conversation",
            use_container_width=True,
        ):

            st.session_state.page = "chat"
            st.rerun()

    else:

        st.info(
            "You are currently browsing as a guest. "
            "Log in or sign up to use Chat and Chat History."
        )

        col1, col2 = st.columns(2)

        with col1:

            if st.button(
                "Log in",
                key="dashboard_login",
                use_container_width=True,
            ):

                st.session_state.page = "login"
                st.rerun()

        with col2:

            if st.button(
                "Sign up",
                key="dashboard_signup",
                use_container_width=True,
            ):

                st.session_state.page = "signup"
                st.rerun()


# ============================================================
# LOAD CHAT HISTORY
# ============================================================

def load_chat_history():

    if not st.session_state.token:
        return False

    result = api_get(
        "/chat-history",
        token=st.session_state.token,
    )

    if not result.get("status"):

        st.error(
            result.get(
                "message",
                "Could not load chat history.",
            )
        )

        return False


    data = result.get("data") or {}

    history = data.get(
        "history",
        [],
    )


    messages = []


    for item in history:

        user_query = item.get(
            "user_query",
            "",
        )

        bot_response = item.get(
            "bot_response",
            "",
        )


        messages.append(
            {
                "role": "user",
                "content": user_query,
            }
        )

        messages.append(
            {
                "role": "assistant",
                "content": bot_response,
            }
        )


    st.session_state.messages = messages
    st.session_state.history_loaded = True

    return True


# ============================================================
# CHAT MESSAGE
# ============================================================

def render_message(
    role: str,
    content: str,
    is_error: bool = False,
):

    if role == "user":

        with st.chat_message(
            "user",
        ):

            st.write(content)

    else:

        if is_error:

            with st.chat_message(
                "assistant",
            ):

                st.error(content)

        else:

            with st.chat_message(
                "assistant",
            ):

                st.write(content)


# ============================================================
# CHAT HISTORY PAGE
# ============================================================

def render_history():

    if not st.session_state.token:

        st.title(
            "Chat History"
        )

        render_auth_required(
            "history"
        )

        return


    st.title(
        "Chat History"
    )

    st.caption(
        "Your previous HR Copilot conversations."
    )


    # --------------------------------------------------------
    # RELOAD
    # --------------------------------------------------------

    if st.button(
        "↻ Reload history",
        key="history_reload",
    ):

        if load_chat_history():
            st.rerun()


    # --------------------------------------------------------
    # AUTOMATIC FIRST LOAD
    # --------------------------------------------------------

    if not st.session_state.history_loaded:

        with st.spinner(
            "Loading your chat history..."
        ):

            load_chat_history()


    # --------------------------------------------------------
    # NO HISTORY
    # --------------------------------------------------------

    if not st.session_state.messages:

        st.info(
            "No chat history found yet."
        )

        return


    # --------------------------------------------------------
    # DISPLAY HISTORY
    # --------------------------------------------------------

    for message in st.session_state.messages:

        render_message(
            role=message["role"],
            content=message["content"],
            is_error=message.get(
                "is_error",
                False,
            ),
        )


# ============================================================
# FILE ICONS
# ============================================================

FILE_ICONS = {
    "pdf": "📄",
    ".pdf": "📄",
    "xlsx": "📊",
    ".xlsx": "📊",
    "docx": "📝",
    ".docx": "📝",
    "txt": "📃",
    ".txt": "📃",
}


# ============================================================
# SOURCE
# ============================================================

def render_source(source: dict):

    file_name = source.get(
        "file_name",
        "Unknown file",
    )

    file_type = (
        source.get(
            "file_type",
            "",
        )
        or ""
    ).lstrip(".")

    icon = FILE_ICONS.get(
        source.get(
            "file_type",
            "",
        ),
        "📎",
    )


    if source.get("page_number") is not None:

        reference = (
            f"Page {source['page_number']}"
        )

    elif source.get("row_number") is not None:

        reference = (
            f"Row {source['row_number']}"
        )

    else:

        reference = (
            file_type.upper()
            if file_type
            else "SOURCE"
        )


    with st.container(
        border=True,
    ):

        st.write(
            f"{icon} **{file_name}**"
        )

        st.caption(
            reference
        )


# ============================================================
# REFERENCE RAIL
# ============================================================

def render_reference_rail():

    st.subheader(
        "References"
    )

    st.caption(
        "Cited in the latest answer"
    )


    if not st.session_state.last_sources:

        st.info(
            "Sources will appear here once "
            "you ask a question."
        )

        return


    for source in st.session_state.last_sources:

        render_source(
            source
        )


# ============================================================
# CHAT PAGE
# ============================================================

def render_chat():

    if not st.session_state.token:

        st.title(
            "HR Copilot"
        )

        render_auth_required(
            "chat"
        )

        return


    col_chat, col_rail = st.columns(
        [2.3, 1],
        gap="large",
    )


    # ========================================================
    # CHAT
    # ========================================================

    with col_chat:

        st.title(
            "Ask about company policy"
        )

        st.caption(
            "Ask questions about leave, WFH, "
            "notice period, reimbursement and other "
            "HR policies."
        )


        # ----------------------------------------------------
        # PREVIOUS MESSAGES
        # ----------------------------------------------------

        for message in st.session_state.messages:

            render_message(
                role=message["role"],
                content=message["content"],
                is_error=message.get(
                    "is_error",
                    False,
                ),
            )


        # ----------------------------------------------------
        # INPUT
        # ----------------------------------------------------

        prompt = st.chat_input(
            "Ask about leave, WFH, notice period, reimbursement…"
        )


        if prompt:

            # ------------------------------------------------
            # SHOW USER MESSAGE
            # ------------------------------------------------

            st.session_state.messages.append(
                {
                    "role": "user",
                    "content": prompt,
                }
            )


            # ------------------------------------------------
            # API REQUEST + LOADING
            # ------------------------------------------------

            with st.chat_message(
                "assistant"
            ):

                with st.spinner(
                    "🤖 HR Copilot is thinking..."
                ):

                    result = api_post(
                        "/chat",
                        {
                            "query": prompt,
                        },
                        token=st.session_state.token,
                    )


            # ------------------------------------------------
            # SUCCESS
            # ------------------------------------------------

            if result.get("status"):

                data = result.get(
                    "data",
                    {},
                )

                answer = data.get(
                    "answer",
                    "I could not generate an answer.",
                )

                sources = data.get(
                    "sources",
                    [],
                )


                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                    }
                )

                st.session_state.last_sources = sources


            # ------------------------------------------------
            # ERROR
            # ------------------------------------------------

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


            # Re-render page

            st.rerun()


    # ========================================================
    # REFERENCES
    # ========================================================

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
# MAIN
# ============================================================

def main():

    inject_css()

    init_state()

    render_sidebar()

    render_page()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()

