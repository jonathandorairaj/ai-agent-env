def get_css(T: dict) -> str:
    return f"""
<style>

/* APP BACKGROUND */
.stApp {{
    background-color: {T["app_bg"]};
}}

/* TOP HEADER BAR */
header[data-testid="stHeader"] {{
    background-color: {T["app_bg"]};
}}

/* BOTTOM CHAT INPUT BAR */
[data-testid="stBottom"] {{
    background-color: {T["app_bg"]};
}}
[data-testid="stBottom"] > div {{
    background-color: {T["app_bg"]};
}}

/* CHAT INPUT - container, textarea, placeholder, send button */
[data-testid="stChatInput"] {{
    background-color: {T["input_bg"]} !important;
    border: 1px solid {T["btn_border"]} !important;
    border-radius: 12px !important;
}}
[data-testid="stChatInput"] textarea,
[data-testid="stChatInputTextArea"] {{
    background-color: {T["input_bg"]} !important;
    color: {T["input_text"]} !important;
}}
[data-testid="stChatInput"] textarea::placeholder {{
    color: {T["travel_time"]} !important;
}}
[data-testid="stChatInput"] button {{
    background-color: transparent !important;
    color: {T["input_text"]} !important;
    border: none !important;
}}
[data-testid="stChatInput"] button:hover {{
    background-color: {T["btn_bg_hover"]} !important;
}}

/* BUTTONS */
.stButton > button,
.stDownloadButton > button {{
    background-color: {T["btn_bg"]} !important;
    color: {T["btn_text"]} !important;
    border: 1px solid {T["btn_border"]} !important;
}}
.stButton > button:hover,
.stDownloadButton > button:hover {{
    background-color: {T["btn_bg_hover"]} !important;
    border-color: {T["section_border"]} !important;
    color: {T["btn_text"]} !important;
}}

/* SIDEBAR */
section[data-testid="stSidebar"] {{
    background-color: {T["sidebar_bg"]};
}}
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {{
    color: {T["card_text"]} !important;
}}

/* CHAT MESSAGES */
[data-testid="stChatMessageContent"] p,
[data-testid="stChatMessageContent"] li {{
    color: {T["card_text"]};
}}

/* HERO CARD */
.hero {{
    background: linear-gradient(135deg, {T["hero_grad_a"]}, {T["hero_grad_b"]});
    padding: 40px;
    border-radius: 12px;
    text-align: center;
    border: 1px solid {T["hero_border"]};
    box-shadow: 0 10px 30px {T["shadow"]};
}}

/* HERO TEXT */
.hero-title {{
    font-size: 42px;
    font-weight: 700;
    color: {T["hero_title"]};
}}

.hero-sub {{
    font-size: 18px;
    opacity: 0.9;
    color: {T["hero_sub"]};
}}

/* CARDS */
.card {{
    background-color: {T["card_bg"]};
    color: {T["card_text"]};
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 6px 20px {T["shadow"]};
    margin-bottom: 15px;
    border: 1px solid {T["card_border"]};
}}

/* CARD TITLE */
.card-title {{
    font-size: 18px;
    font-weight: 600;
    color: {T["card_title"]};
}}

/* SECTION HEADER */
.section-header {{
    font-size: 26px;
    font-weight: 700;
    margin-top: 25px;
    color: {T["section_text"]};
    border-left: 4px solid {T["section_border"]};
    padding-left: 10px;
}}

/* TRAVEL TIME CONNECTOR */
.travel-time {{
    color: {T["travel_time"]};
    font-size: 13px;
    margin: 4px 0 4px 8px;
}}

</style>
"""
