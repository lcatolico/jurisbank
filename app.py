import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import fitz
import re
import hashlib
import secrets
import urllib.request
import urllib.parse
import json
import html as html_lib
import base64
from datetime import datetime, date

st.set_page_config(
    page_title="JurisBank",
    page_icon="⚖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;0,700;1,500;1,600&family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #0d1f4e; }

[data-testid="stToolbar"] { display: none !important; }
[data-testid="stSidebarCollapsedControl"] { display: none !important; }
header[data-testid="stHeader"] { display: none !important; }
#MainMenu { display: none !important; }
[data-testid="stSidebar"] { display: none !important; }

[data-testid="stAppViewContainer"] {
    background: #eef3fe;
    min-height: 100vh;
}
.main .block-container,
[data-testid="stAppViewContainer"] .main .block-container,
[data-testid="stMainBlockContainer"] {
    padding-top: 0 !important;
    padding-left: 2.5rem !important;
    padding-right: 2.5rem !important;
    padding-bottom: 3rem !important;
    max-width: 1100px;
    background: transparent;
}

[data-testid="stMarkdownContainer"],
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] span {
    color: #0d1f4e;
}
[data-testid="stMarkdownContainer"] strong {
    color: #0d1f4e;
    font-weight: 700;
}
[data-testid="stCaptionContainer"],
.stCaptionContainer {
    color: #4a6080 !important;
    font-weight: 500;
}

/* ── Topbar ── */
.topbar {
    display: flex; align-items: center; justify-content: space-between;
    width: 100vw;
    box-sizing: border-box;
    padding: 1rem max(1.25rem, calc((100vw - 1120px) / 2 + 1.25rem));
    border-bottom: 2px solid rgba(200,150,12,0.3);
    margin: 0 calc(50% - 50vw) 2rem;
    flex-wrap: wrap; gap: 12px;
    background: #0d1f4e;
}
.topbar-logo, .topbar-logo *, .topbar a, .topbar a * { text-decoration: none !important; }
.topbar-logo { display: flex; align-items: center; gap: 12px; min-width: 190px; }
.topbar-logo-icon {
    width: 38px; height: 38px;
    background: linear-gradient(135deg,#d9a514,#f0c040);
    border: 1px solid rgba(255,255,255,0.18);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    color: #0d1f4e !important;
    font-family: 'Cormorant Garamond',serif;
    font-size: 15px;
    font-weight: 900;
    letter-spacing: 0;
    box-shadow: 0 8px 20px rgba(200,150,12,0.28);
}
.topbar .topbar-logo-name {
    font-family: 'Cormorant Garamond',serif;
    font-size: 19px;
    font-weight: 900;
    color: #ffffff !important;
    letter-spacing: 0;
    line-height: 1;
}
.topbar .topbar-logo-sub {
    font-size: 10px;
    color: #f0c040 !important;
    font-style: italic;
    letter-spacing:.05em;
    display: block;
    margin-top: 3px;
}
.topbar-nav { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
.topbar-nav a {
    padding: 7px 14px; border-radius: 8px;
    font-size: 13px; font-weight: 600;
    color: rgba(255,255,255,0.82);
    text-decoration: none;
    border: 1px solid transparent;
    transition: all 0.2s;
}
.topbar-nav a:hover { color: #ffffff; background: rgba(255,255,255,0.1); }
.topbar-nav a.active { color: #f0c040; border-color: rgba(200,150,12,0.4); background: rgba(200,150,12,0.12); }
.topbar-nav a.btn-rec {
    background: linear-gradient(135deg,#c8960c,#f0c040);
    color: #0d1f4e; border: none; font-weight: 700;
}
.topbar-nav a.btn-rec:hover { opacity: 0.9; }

/* ── Cards ── */
.hero-card { background: #ffffff; border: 1.5px solid #d0dcfa; border-radius: 20px; padding: 2rem 2.5rem; margin-bottom: 1.5rem; box-shadow: 0 8px 28px rgba(13,31,78,0.06); }
.profile-shell { background: #ffffff; border: 1.5px solid #c5d5f5; border-radius: 16px; padding: 18px 22px; margin: 0 0 1rem; box-shadow: 0 10px 26px rgba(13,31,78,0.06); }
.profile-shell-title { font-size: 13px; font-weight: 900; color: #0d1f4e; text-transform: uppercase; letter-spacing: .12em; margin: 0 0 14px; }
.profile-panel { background: #ffffff; border: 1.5px solid #c5d5f5; border-radius: 22px; padding: 34px 38px; margin: 0 0 1.5rem; box-shadow: 0 12px 30px rgba(13,31,78,0.08); width: 100%; }
.profile-head { display: flex; align-items: center; gap: 18px; margin-bottom: 20px; }
.profile-avatar { width: 68px; height: 68px; border-radius: 14px; background: #247b56; color: #ffffff; display: flex; align-items: center; justify-content: center; font-size: 20px; font-weight: 900; flex-shrink: 0; }
.profile-photo { width: 68px; height: 68px; border-radius: 14px; object-fit: cover; flex-shrink: 0; border: 1px solid #d0dcfa; }
.profile-name-main { font-size: 24px; font-weight: 900; color: #0d1f4e; margin: 0 0 2px; }
.profile-sub-main { font-size: 15px; font-weight: 700; color: #587bd6; margin: 0; line-height: 1.35; }
.profile-chip-row { display: flex; gap: 8px; flex-wrap: wrap; margin: 8px 0 16px; }
.profile-chip { display: inline-flex; align-items: center; min-height: 23px; padding: 0 10px; border-radius: 999px; font-size: 11px; font-weight: 800; border: 1px solid #c5d5f5; background: #e8effe; color: #1a3a8f; }
.profile-chip-green { background: #e6f4ea; color: #15803d; border-color: #b0dfc0; }
.profile-chip-gold { background: #fff8e6; color: #b45309; border-color: #f0c040; }
.profile-disc-card { background: #f7fbf9; border: 1px solid #d8efe4; border-radius: 13px; padding: 16px 18px; display: flex; gap: 14px; align-items: center; margin-bottom: 14px; }
.profile-disc-letter { color: #15803d; font-size: 24px; font-weight: 900; min-width: 26px; }
.profile-disc-text { color: #587bd6; font-size: 13px; font-weight: 600; line-height: 1.45; margin: 0; }
.profile-concurso { background: #fff8e6; border: 1.5px solid #f0c040; color: #b45309; border-radius: 12px; padding: 12px 14px; font-size: 13px; font-weight: 800; margin: 0 0 14px; }
.profile-detail-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin: 0 0 14px; }
.profile-detail { background: #f3f7ff; border: 1px solid #d0dcfa; border-radius: 10px; padding: 14px 16px; font-size: 13px; color: #0d1f4e; line-height: 1.6; }
.profile-foot { display: flex; justify-content: space-between; align-items: center; gap: 12px; flex-wrap: wrap; margin-top: 16px; }
.profile-status { display: inline-flex; align-items: center; min-height: 27px; padding: 0 12px; border-radius: 999px; border: 1px solid #b0dfc0; background: #e6f4ea; color: #15803d; font-size: 12px; font-weight: 900; }
.profile-status-off { border-color: #f0c8a0; background: #fff3e8; color: #c05a1a; }
.profile-actions { display: flex; gap: 10px; flex-wrap: wrap; }
.profile-action { display: inline-flex; align-items: center; justify-content: center; min-height: 34px; padding: 0 16px; border-radius: 10px; background: #fff8e6; border: 1.5px solid #f0c040; color: #c8960c !important; text-decoration: none !important; font-size: 12px; font-weight: 900; }
.profile-action:hover { background: #f0c040; color: #0d1f4e !important; }
.edit-hero { background: #ffffff; border: 1.5px solid #d0dcfa; border-radius: 16px; padding: 1.35rem 1.6rem; margin-bottom: 1.2rem; box-shadow: 0 8px 24px rgba(13,31,78,0.05); }
.edit-title { font-family: 'Cormorant Garamond',serif; font-size: 32px; font-weight: 700; color: #0d1f4e; margin: 0 0 4px; line-height: 1.05; }
.edit-title em { font-style: normal; color: #d9a514; }
.edit-sub { font-size: 13px; color: #2a4a8a; margin: 0; font-weight: 600; }
@media (max-width: 760px) { .profile-panel { max-width: none; padding: 22px; } .profile-detail-grid { grid-template-columns: 1fr; } }
@media (max-width: 760px) { .topbar { padding: 0.9rem 1rem; } .topbar-logo { min-width: 160px; } .topbar-nav { width: 100%; justify-content: flex-start; } }
.page-title { font-family: 'Cormorant Garamond',serif; font-size: clamp(32px,4vw,50px); font-weight: 700; color: #0d1f4e; margin: 0 0 8px; letter-spacing: -1px; line-height: 1.05; }
.page-title em { font-style: normal; background: linear-gradient(135deg,#c8960c,#f0c040); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
.page-sub { font-size: 15px; color: #2a4a8a; margin: 0; font-weight: 600; }
.stats-row { display: flex; gap: 12px; margin-top: 1.5rem; flex-wrap: wrap; }
.stat-pill { background: #dce8ff; border-radius: 99px; padding: 7px 16px; font-size: 13px; font-weight: 700; color: #0d1f4e; border: 1px solid #a0bcf0; }
.cand-card { background: #ffffff; border: 1.5px solid #d0dcfa; border-radius: 16px; padding: 1.2rem 1.5rem; margin-bottom: 8px; transition: all 0.2s; }
.cand-card:hover { border-color: #4070f4; box-shadow: 0 6px 24px rgba(64,112,244,0.1); transform: translateY(-1px); }
.chamada-card { background: #ffffff; border: 1.5px solid #d0dcfa; border-radius: 16px; padding: 1.2rem 1.5rem; margin-bottom: 10px; transition: all 0.2s; }
.chamada-card:hover { border-color: #4070f4; box-shadow: 0 6px 24px rgba(64,112,244,0.1); }
.avatar { width: 46px; height: 46px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 14px; font-weight: 700; flex-shrink: 0; color: white; }
.cand-photo { width: 46px; height: 46px; border-radius: 12px; object-fit: cover; flex-shrink: 0; border: 1px solid #d0dcfa; }
.cand-photo-lg { width: 60px; height: 60px; border-radius: 14px; object-fit: cover; flex-shrink: 0; border: 1px solid #d0dcfa; }
.cand-name { font-size: 15px; font-weight: 700; color: #0d1f4e; margin: 0 0 3px; }
.cand-sub { font-size: 12px; color: #4a6080; margin: 0; font-weight: 500; }
.cand-card + div[data-testid="stHorizontalBlock"] { margin-top: -8px !important; margin-bottom: 18px !important; }
.cand-card + div[data-testid="stHorizontalBlock"] .stButton button { min-height: 36px !important; padding: 0.45rem 1rem !important; }
.badge-sim { background: #e6f4ea; color: #1a7a4a; padding: 4px 12px; border-radius: 99px; font-size: 11px; font-weight: 700; border: 1px solid #b0dfc0; }
.badge-nao { background: #fff3e8; color: #c05a1a; padding: 4px 12px; border-radius: 99px; font-size: 11px; font-weight: 700; border: 1px solid #f0c8a0; }
.badge-aberta { background: #e6f4ea; color: #1a7a4a; padding: 3px 10px; border-radius: 99px; font-size: 11px; font-weight: 700; border: 1px solid #b0dfc0; }
.badge-encerrada { background: #f4f7fe; color: #4a6080; padding: 3px 10px; border-radius: 99px; font-size: 11px; font-weight: 700; border: 1px solid #d0dcfa; }
.badge-inscrito { background: #e8effe; color: #1a3a8f; padding: 3px 10px; border-radius: 99px; font-size: 11px; font-weight: 700; border: 1px solid #b0c5f5; }
.selo { display: inline-block; font-size: 10px; font-weight: 700; padding: 3px 10px; border-radius: 99px; margin-right: 4px; margin-top: 4px; }
.selo-verificado { background: #e8effe; color: #1a3a8f; border: 1px solid #b0c5f5; }
.selo-recomendado { background: #e6f4ea; color: #15803d; border: 1px solid #b0dfc0; }
.selo-destaque { background: #fff8e6; color: #b45309; border: 1px solid #fde68a; }
.selo-experiente { background: #f3effe; color: #6d28d9; border: 1px solid #ddd6fe; }
.metric-box { background: #ffffff; border: 1.5px solid #d0dcfa; border-radius: 14px; padding: 16px 18px; text-align: center; }
.metric-label { font-size: 11px; font-weight: 700; color: #4a6080; text-transform: uppercase; letter-spacing: .08em; margin: 0 0 6px; }
.metric-value { font-size: 20px; font-weight: 800; color: #0d1f4e; margin: 0; }
.profile-name { font-family: 'Cormorant Garamond',serif; font-size: 28px; font-weight: 700; color: #0d1f4e; margin: 0 0 6px; }
.section-label { font-size: 11px; font-weight: 800; color: #1a3a8f; text-transform: uppercase; letter-spacing: .1em; margin: 1.5rem 0 0.5rem; }
.info-card { background: #f0f5ff; border: 1.5px solid #c5d5f5; border-radius: 12px; padding: 14px 18px; font-size: 14px; color: #1a3a8f; line-height: 1.6; font-weight: 500; }
.custom-divider { height: 1px; background: #d0dcfa; margin: 1.5rem 0; }
.info-box { background: #e8effe; border: 1px solid #b0c5f5; border-radius: 10px; padding: 10px 14px; font-size: 13px; color: #1a3a8f; margin-top: 8px; font-weight: 600; }
.lock-box { background: #f4f7fe; border: 1.5px solid #d0dcfa; border-radius: 12px; padding: 14px 18px; font-size: 13px; color: #4a6080; text-align: center; font-weight: 500; }
.disclaimer-box { background: #fff8e6; border: 1px solid #fde68a; border-radius: 10px; padding: 12px 16px; font-size: 12px; color: #92400e; line-height: 1.6; margin-top: 1rem; font-weight: 500; }
.step-bar { display: flex; gap: 8px; margin-bottom: 2rem; }
.step { flex: 1; height: 4px; border-radius: 99px; background: #d0dcfa; }
.step.active { background: linear-gradient(135deg,#c8960c,#f0c040); }
.step.done { background: #1a7a4a; }
.step-title { font-size: 13px; font-weight: 700; color: #2a4a8a; margin-bottom: 0.3rem; }
.step-desc { font-family: 'Cormorant Garamond',serif; font-size: 24px; font-weight: 700; color: #0d1f4e; margin-bottom: 1.5rem; }
.doc-sub { font-size: 12px; font-weight: 800; color: #1a3a8f; text-transform: uppercase; letter-spacing: .08em; margin: 1.5rem 0 0.5rem; }
.doc-body { font-size: 14px; color: #1a3a8f; line-height: 1.8; margin-bottom: 0.8rem; font-weight: 500; }
.doc-item { font-size: 14px; color: #1a3a8f; line-height: 1.8; padding-left: 1rem; font-weight: 500; }

/* Botões globais */
.stButton button {
    min-height: 42px !important;
    background: linear-gradient(135deg,#d9a514,#f0c040) !important;
    color: #0d1f4e !important;
    border: 1px solid rgba(13,31,78,0.08) !important;
    border-radius: 10px !important;
    font-family: 'Inter',sans-serif !important;
    font-weight: 800 !important;
    padding: 0.62rem 2rem !important;
    font-size: 14px !important;
    transition: all 0.2s !important;
    box-shadow: 0 8px 18px rgba(217,165,20,0.18) !important;
}
.stButton button:hover { opacity: 0.96 !important; transform: translateY(-1px) !important; box-shadow: 0 10px 22px rgba(217,165,20,0.24) !important; }
[data-testid="stFormSubmitButton"] button {
    min-height: 42px !important;
    background: linear-gradient(135deg,#d9a514,#f0c040) !important;
    color: #0d1f4e !important;
    border: 1px solid rgba(13,31,78,0.08) !important;
    border-radius: 10px !important;
    font-family: 'Inter',sans-serif !important;
    font-weight: 800 !important;
    padding: 0.62rem 2rem !important;
    font-size: 14px !important;
    box-shadow: 0 8px 18px rgba(217,165,20,0.18) !important;
}
[data-testid="stFormSubmitButton"] button:hover {
    background: linear-gradient(135deg,#d9a514,#f0c040) !important;
    color: #0d1f4e !important;
    border-color: rgba(13,31,78,0.08) !important;
}
div[data-testid="column"]:last-child .stButton button,
div[data-testid="column"]:nth-last-child(2) .stButton button { background: #ffffff !important; color: #0d1f4e !important; border: 1.5px solid #c5d5f5 !important; border-radius: 10px !important; padding: 0.58rem 1rem !important; font-size: 13px !important; font-weight: 800 !important; width: 100%; box-shadow: 0 6px 16px rgba(13,31,78,0.08) !important; }
div[data-testid="column"]:last-child .stButton button:hover,
div[data-testid="column"]:nth-last-child(2) .stButton button:hover { background: #e8f0fe !important; border-color: #4070f4 !important; color: #0d1f4e !important; }
.stTextInput input, .stTextArea textarea, .stDateInput input { border-radius: 10px !important; border-color: #d0dcfa !important; background: #ffffff !important; color: #0d1f4e !important; font-family: 'Inter',sans-serif !important; font-size: 14px !important; font-weight: 500 !important; }
.stTextInput input:focus, .stTextArea textarea:focus, .stDateInput input:focus { border-color: #4070f4 !important; box-shadow: 0 0 0 3px rgba(64,112,244,0.1) !important; }
.stTextInput input::placeholder, .stTextArea textarea::placeholder { color: #4a6080 !important; opacity: 1 !important; font-weight: 500 !important; }
.stSelectbox > div > div { border-radius: 10px !important; border-color: #d0dcfa !important; background: #ffffff !important; color: #0d1f4e !important; }
.stSelectbox [data-baseweb="select"] * { color: #0d1f4e !important; font-weight: 500 !important; }
.stRadio label, .stCheckbox label { color: #0d1f4e !important; font-weight: 600 !important; }
.stMultiSelect > div > div { background: #ffffff !important; border-color: #d0dcfa !important; border-radius: 10px !important; }
.stMultiSelect [data-baseweb="select"] { color: #0d1f4e !important; }
.stMultiSelect [data-baseweb="select"] svg { fill: #0d1f4e !important; color: #0d1f4e !important; }
[data-baseweb="popover"], [data-baseweb="menu"], [data-baseweb="calendar"], [role="listbox"] { background: #ffffff !important; color: #0d1f4e !important; }
[role="option"], [role="option"] *, [data-baseweb="calendar"] * { color: #0d1f4e !important; }
[role="option"]:hover, [role="option"][aria-selected="true"] { background: #e8f0fe !important; color: #0d1f4e !important; }
label[data-baseweb="label"] { color: #0d1f4e !important; font-weight: 700 !important; }
.form-item-title { font-size: 12px; font-weight: 800; color: #1a3a8f; text-transform: uppercase; letter-spacing: .08em; margin: 18px 0 8px; padding-top: 14px; border-top: 1px solid #d0dcfa; }
.add-hint { font-size: 12px; color: #4a6080; font-weight: 600; margin: -2px 0 10px; }
.highlight-panel { background: #fff8e6; border: 1.5px solid #f0c040; border-radius: 12px; padding: 12px 16px; margin: 10px 0 14px; color: #0d1f4e; font-weight: 800; }
.stTextInput input:disabled { background: #f4f7fe !important; color: #1a3a8f !important; -webkit-text-fill-color: #1a3a8f !important; border-color: #c5d5f5 !important; font-weight: 800 !important; opacity: 1 !important; }
[data-baseweb="input"], [data-baseweb="select"] { background: #ffffff !important; color: #0d1f4e !important; }
[data-baseweb="input"] button, [data-testid="stFileUploader"] button { background: #ffffff !important; color: #0d1f4e !important; border-color: #c5d5f5 !important; }
[data-testid="stFileUploader"] section { background: #ffffff !important; border-color: #c5d5f5 !important; border-radius: 12px !important; }
[data-testid="stFileUploader"] * { color: #0d1f4e !important; }
.stTabs [data-baseweb="tab-list"] {
    background: #dfeaff !important;
    border-radius: 12px !important;
    padding: 5px !important;
    gap: 5px !important;
    border: 1px solid #c5d5f5 !important;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.65) !important;
}
.stTabs [data-baseweb="tab"] {
    min-height: 38px !important;
    padding: 0 14px !important;
    background: transparent !important;
    color: #1a3a8f !important;
    border-radius: 9px !important;
    font-weight: 700 !important;
}
.stTabs [data-baseweb="tab"] p {
    color: inherit !important;
    font-weight: inherit !important;
}
.stTabs [aria-selected="true"] {
    background: #ffffff !important;
    color: #0d1f4e !important;
    font-weight: 800 !important;
    box-shadow: 0 6px 14px rgba(13,31,78,0.08) !important;
}
.stAlert [data-testid="stMarkdownContainer"],
.stAlert [data-testid="stMarkdownContainer"] p {
    color: #0d1f4e !important;
    font-weight: 600;
}

/* ── Camada visual neutra inspirada na nova landing ── */
[data-testid="stAppViewContainer"] { background: #f9f8f6 !important; }
html, body, [class*="css"] { color: #1e1e1e !important; }
.main .block-container { max-width: 1120px; }
.topbar {
    background: #1e1e1e !important;
    border-bottom: 1px solid #ddd8ce !important;
    box-shadow: 0 8px 24px rgba(30,30,30,0.08);
}
.topbar-logo-icon, .topbar-nav a.btn-rec {
    background: linear-gradient(135deg,#b8973a,#e8d48a) !important;
    color: #1e1e1e !important;
}
.topbar .topbar-logo-name { color: #ffffff !important; }
.topbar .topbar-logo-sub, .topbar-nav a.active { color: #e8d48a !important; }
.topbar-nav a.active { border-color: rgba(232,212,138,.45) !important; background: rgba(232,212,138,.1) !important; }
.hero-card, .profile-shell, .profile-panel, .edit-hero, .cand-card, .chamada-card, .metric-box,
.info-card, .lock-box, .profile-detail, [data-testid="stFileUploader"] section {
    background: #ffffff !important;
    border-color: #ddd8ce !important;
    box-shadow: 0 14px 36px rgba(30,30,30,0.06) !important;
}
.page-title, .edit-title, .profile-name-main, .profile-name, .cand-name,
.metric-value, .section-label, .profile-shell-title, .form-item-title {
    color: #1e1e1e !important;
}
.page-title em, .edit-title em {
    background: none !important;
    -webkit-text-fill-color: #b8973a !important;
    color: #b8973a !important;
}
.page-sub, .edit-sub, .cand-sub, .doc-body, .add-hint,
[data-testid="stCaptionContainer"], .stCaptionContainer {
    color: #6a6a6a !important;
}
.stButton button, [data-testid="stFormSubmitButton"] button {
    background: #b8973a !important;
    color: #1e1e1e !important;
    border-color: rgba(30,30,30,.1) !important;
    box-shadow: 0 10px 22px rgba(184,151,58,.18) !important;
}
.stButton button:hover, [data-testid="stFormSubmitButton"] button:hover {
    background: #e8d48a !important;
    color: #1e1e1e !important;
}
div[data-testid="column"]:last-child .stButton button,
div[data-testid="column"]:nth-last-child(2) .stButton button {
    background: #ffffff !important;
    color: #1e1e1e !important;
    border-color: #ddd8ce !important;
}
div[data-testid="column"]:last-child .stButton button:hover,
div[data-testid="column"]:nth-last-child(2) .stButton button:hover {
    background: #f2efe9 !important;
    border-color: #b8973a !important;
}
.profile-action {
    background: #faf6ec !important;
    border-color: #e8d48a !important;
    color: #8a6a16 !important;
}
.profile-action:hover { background: #e8d48a !important; color: #1e1e1e !important; }
.highlight-panel, .profile-concurso {
    background: #faf6ec !important;
    border-color: #e8d48a !important;
    color: #1e1e1e !important;
}
.stat-pill, .profile-chip, .badge-inscrito {
    background: #f2efe9 !important;
    color: #1e1e1e !important;
    border-color: #ddd8ce !important;
}
.custom-divider, .form-item-title { border-color: #ddd8ce !important; background: #ddd8ce !important; }
.stTextInput input, .stTextArea textarea, .stDateInput input,
.stSelectbox > div > div, .stMultiSelect > div > div,
[data-baseweb="input"], [data-baseweb="select"] {
    background: #ffffff !important;
    color: #1e1e1e !important;
    border-color: #ddd8ce !important;
}
[data-baseweb="popover"], [data-baseweb="menu"], [data-baseweb="calendar"], [role="listbox"] {
    background: #ffffff !important;
    color: #1e1e1e !important;
}
[role="option"], [role="option"] *, [data-baseweb="calendar"] * { color: #1e1e1e !important; }
[role="option"]:hover, [role="option"][aria-selected="true"] { background: #f2efe9 !important; color: #1e1e1e !important; }
.stSelectbox [data-baseweb="select"] div,
.stSelectbox [data-baseweb="select"] span {
    color: #1e1e1e !important;
    -webkit-text-fill-color: #1e1e1e !important;
}
[data-baseweb="popover"] [role="option"],
[data-baseweb="popover"] [role="option"] *,
[data-baseweb="menu"] [role="option"],
[data-baseweb="menu"] [role="option"] *,
[data-baseweb="select-dropdown"] [role="option"],
[data-baseweb="select-dropdown"] [role="option"] * {
    background-color: #ffffff !important;
    color: #1e1e1e !important;
    -webkit-text-fill-color: #1e1e1e !important;
}
[data-baseweb="popover"] [aria-selected="true"],
[data-baseweb="menu"] [aria-selected="true"],
[data-baseweb="select-dropdown"] [aria-selected="true"],
[data-baseweb="popover"] [role="option"]:hover,
[data-baseweb="menu"] [role="option"]:hover {
    background-color: #f2efe9 !important;
    color: #1e1e1e !important;
}
.stMultiSelect [data-baseweb="tag"] { color: inherit !important; }
.stTabs [data-baseweb="tab-list"] { background: #f2efe9 !important; border-color: #ddd8ce !important; }
.stTabs [data-baseweb="tab"] { color: #6a6a6a !important; }
.stTabs [aria-selected="true"] { color: #1e1e1e !important; box-shadow: 0 6px 14px rgba(30,30,30,0.08) !important; }
.profile-sub-main { color: #6a6a6a !important; font-size: 13px !important; font-weight: 600 !important; }
.profile-section-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin: 14px 0; }
.profile-section-card { background: #ffffff; border: 1px solid #ddd8ce; border-radius: 12px; padding: 14px 16px; min-width: 0; }
.profile-section-card.full { grid-column: 1 / -1; }
.profile-section-title { color: #6a6a6a; font-size: 10px; font-weight: 900; letter-spacing: .09em; text-transform: uppercase; margin: 0 0 8px; }
.profile-list { display: flex; flex-direction: column; gap: 8px; }
.profile-list-item { color: #1e1e1e; font-size: 13px; font-weight: 650; line-height: 1.45; overflow-wrap: anywhere; }
.profile-list-item span { color: #6a6a6a; font-weight: 600; }
.profile-empty { color: #6a6a6a; font-size: 13px; font-weight: 600; }
@media (max-width: 760px) { .profile-section-grid { grid-template-columns: 1fr; } .profile-section-card.full { grid-column: auto; } }
</style>
""", unsafe_allow_html=True)

# ── Google Sheets ─────────────────────────────────────────────────────────────
@st.cache_resource
def conectar_sheets():
    escopos = ["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive"]
    if "gcp_service_account" in st.secrets:
        cred = Credentials.from_service_account_info(dict(st.secrets["gcp_service_account"]),scopes=escopos)
    else:
        cred = Credentials.from_service_account_file("credenciais.json",scopes=escopos)
    cl = gspread.authorize(cred)
    pl = cl.open("JurisBank")
    return {
        "candidatos": pl.sheet1,
        "recrutadores": pl.worksheet("recrutadores"),
        "chamadas": pl.worksheet("chamadas"),
        "interesses": pl.worksheet("interesses"),
        "recomendacoes": pl.worksheet("recomendacoes"),
    }

abas = conectar_sheets()
aba_candidatos = abas["candidatos"]
aba_recrutadores = abas["recrutadores"]
aba_chamadas = abas["chamadas"]
aba_interesses = abas["interesses"]
aba_recomendacoes = abas["recomendacoes"]

CAND_COL_SENHA = 19
CAND_COL_FOTO = 20

def garantir_coluna(aba, nome, posicao):
    try:
        cabecalhos = aba.row_values(1)
        if nome not in cabecalhos:
            aba.update_cell(1, posicao, nome)
    except Exception:
        pass

garantir_coluna(aba_candidatos, "senha", CAND_COL_SENHA)
garantir_coluna(aba_candidatos, "foto", CAND_COL_FOTO)

# ── Navegação por URL ─────────────────────────────────────────────────────────
params = st.query_params
p = params.get("p", st.session_state.get("pagina", "publico"))
if isinstance(p,list): p = p[0]
if p not in ["publico","inicio","perfil","candidatos","chamadas","cadastro","recrutador","privacidade","termos","recomendar"]:
    p = "publico"
if "pagina" not in st.session_state or params.get("p"):
    st.session_state.pagina = p
pagina = st.session_state.pagina

# ── Constantes ────────────────────────────────────────────────────────────────
AVATAR_CORES = ["#1a3a8f","#2e7d5e","#7b3fa0","#c05a1a","#1a6b8a","#a04040","#3a6b2a"]
DISC_LABEL = {"D":"Dominante","I":"Influente","S":"Estável","C":"Conformidade"}
DISC_CORES_BADGE = {"D":"rgba(252,165,165,0.12)","I":"rgba(253,230,138,0.12)","S":"rgba(110,231,183,0.12)","C":"rgba(147,197,253,0.12)"}
DISC_TEXTO_BADGE = {"D":"#fca5a5","I":"#fde68a","S":"#6ee7b7","C":"#93c5fd"}
DISC_EXPLICACOES_FILTRO = {
    "D — Dominante":"Direto e decidido. Resolve problemas com rapidez. Bom para demandas urgentes.",
    "I — Influente":"Comunicativo e entusiasta. Excelente no atendimento ao público e trabalho em equipe.",
    "S — Estável":"Paciente e confiável. Ideal para rotinas de gabinete e processos repetitivos.",
    "C — Conformidade":"Analítico e preciso. Excelente em pesquisa jurídica e elaboração de minutas."
}
DISC_DETALHES = {
    "D":{"nome":"Dominante","resumo":"Direto, decidido e orientado a resultados.","pontos_fortes":"Resolve problemas com rapidez, assume responsabilidades, trabalha bem sob pressão.","no_gabinete":"Ideal para demandas que exigem agilidade, tomada de decisão rápida e autonomia.","atencao":"Pode ser impaciente com processos lentos. Funciona melhor com autonomia."},
    "I":{"nome":"Influente","resumo":"Comunicativo, entusiasta e orientado a pessoas.","pontos_fortes":"Excelente no atendimento ao público, trabalho em equipe e ambientes dinâmicos.","no_gabinete":"Ideal para Ministérios Públicos ou Defensorias com alto volume de atendimento.","atencao":"Pode ter dificuldade com tarefas repetitivas. Precisa de estímulo."},
    "S":{"nome":"Estável","resumo":"Paciente, confiável e orientado a processos.","pontos_fortes":"Consistência, lealdade e capacidade de manter rotinas com qualidade.","no_gabinete":"Perfil ideal para gabinetes com rotinas estabelecidas — minutas, prazos, organização processual.","atencao":"Pode ter dificuldade com mudanças repentinas. Prefere ambientes previsíveis."},
    "C":{"nome":"Conformidade","resumo":"Analítico, preciso e orientado à qualidade.","pontos_fortes":"Atenção aos detalhes, rigor técnico, capacidade de análise aprofundada e pesquisa jurídica.","no_gabinete":"Ideal para assessorias que demandam análise de processos complexos.","atencao":"Pode ser perfeccionista. Precisa de clareza nas instruções."}
}
DESCRICOES_DISC = {"D":"Dominante — Direto, decidido e orientado a resultados.","I":"Influente — Comunicativo, entusiasta e orientado a pessoas.","S":"Estável — Paciente, confiável e orientado a processos.","C":"Conformidade — Analítico, preciso e orientado a qualidade."}
CONCURSOS = ["Não estou estudando para concurso","Juiz de Direito (TJ)","Juiz Federal (TRF)","Promotor de Justiça (MP Estadual)","Procurador da República (MPF)","Defensor Público Estadual","Defensor Público Federal (DPU)","Procurador do Estado (PGE)","Procurador Municipal","Delegado de Polícia","Auditor Fiscal / Receita Federal","Outro concurso jurídico"]
ESTADOS = ["AC","AL","AP","AM","BA","CE","DF","ES","GO","MA","MT","MS","MG","PA","PB","PR","PE","PI","RJ","RN","RS","RO","RR","SC","SP","SE","TO"]
ORGAOS = ["Tribunal de Justiça (TJ)","Ministério Público (MP)","Defensoria Pública","Procuradoria Geral do Estado (PGE)","Procuradoria Geral do Município (PGM)","Tribunal Regional Federal (TRF)","Ministério Público Federal (MPF)","Advocacia Geral da União (AGU)","Tribunal de Contas (TCE/TCU)","Outro"]
CARGOS = ["Juiz de Direito","Juiz Federal","Desembargador","Promotor de Justiça","Procurador de Justiça","Defensor Público","Procurador do Estado","Procurador Municipal","Servidor — RH / Gestão de Pessoas","Outro"]
AREAS = ["Criminal","Cível","Família e Sucessões","Execução Penal","Infância e Juventude","Fazenda Pública","Meio Ambiente","Moralidade Administrativa","Violência Doméstica","Direito Público","Direito Tributário","Consumidor","Saúde","Todas as áreas"]
FORMACOES = ["Bacharel em Direito","Mestrado","Doutorado"]
INSTITUICOES_INTERESSE = ["Tribunais de Justiça","Ministérios Públicos","Defensorias Públicas","Procuradorias","Tribunais Regionais Federais","Ministério Público Federal","Advocacia Pública","Tribunais de Contas"]
MESES = ["01","02","03","04","05","06","07","08","09","10","11","12"]
ANOS_PERIODO = [str(a) for a in range(date.today().year, 1979, -1)]
REGIMES = ["Presencial","Parcial","Remoto","Híbrido"]
FORMAS_SELECAO = [
    "Análise curricular",
    "Análise curricular + entrevista estruturada",
    "Análise curricular + teste de escrita",
    "Análise curricular + entrevista + teste",
    "Seleção com período de experiência",
    "Processo simplificado"
]
PERGUNTAS_DISC = [
    ("Em situações de pressão no trabalho, você tende a:",["Tomar decisões rápidas e assumir o controle","Motivar a equipe e buscar soluções criativas","Manter a calma e seguir o processo estabelecido","Analisar os dados antes de agir"]),
    ("Quando recebe uma tarefa nova, você prefere:",["Ter autonomia total para decidir como fazer","Conversar com a equipe e trocar ideias","Entender bem o processo antes de começar","Ter instruções detalhadas e critérios claros"]),
    ("Em reuniões, você costuma:",["Liderar a discussão e propor soluções","Animar o grupo e trazer entusiasmo","Ouvir com atenção antes de opinar","Apresentar dados e análises detalhadas"]),
    ("Seu ponto forte no trabalho é:",["Resultados rápidos e objetivos","Relacionamentos e comunicação","Estabilidade e confiabilidade","Precisão e qualidade técnica"]),
    ("Quando há um conflito na equipe, você:",["Enfrenta diretamente e busca resolução imediata","Tenta mediar com diplomacia e bom humor","Evita confrontos e busca harmonia","Analisa a situação antes de se posicionar"]),
    ("Você se sente mais motivado quando:",["Tem metas desafiadoras para superar","Trabalha com pessoas e recebe reconhecimento","Tem rotina estável e previsível","Pode aprofundar conhecimento e fazer bem feito"]),
    ("Seu estilo de comunicação é:",["Direto e objetivo","Entusiasmado e expressivo","Calmo e paciente","Preciso e detalhado"]),
    ("Diante de uma mudança repentina, você:",["Adapta rapidamente e assume o controle","Vê como oportunidade e engaja a equipe","Precisa de tempo para se adaptar","Avalia os riscos antes de aceitar"]),
    ("No trabalho em equipe, você assume o papel de:",["Líder que define rumos e cobra resultados","Motivador que mantém o clima positivo","Apoiador que garante a harmonia do grupo","Especialista que garante a qualidade técnica"]),
    ("Quando comete um erro, você:",["Assume, corrige rapidamente e segue em frente","Conversa com alguém para processar e superar","Reflete com calma antes de agir diferente","Analisa o que deu errado para não repetir"]),
    ("Sua maior dificuldade no trabalho é:",["Paciência com processos lentos","Manter o foco em tarefas repetitivas","Lidar com mudanças repentinas","Trabalhar sem informações suficientes"]),
    ("Como você prefere receber feedback:",["Direto e objetivo, sem rodeios","De forma encorajadora e positiva","Com calma, em conversa reservada","Com dados e exemplos concretos"]),
    ("Quando há uma demanda urgente no gabinete, você primeiro:",["Define prioridades e distribui tarefas","Alinha expectativas com as pessoas envolvidas","Mantém a rotina e evita desorganização","Confere critérios, prazos e riscos"]),
    ("Em uma minuta complexa, você se destaca por:",["Chegar rapidamente a uma solução prática","Articular informações com clareza para todos","Garantir continuidade e consistência no fluxo","Pesquisar com profundidade e revisar detalhes"]),
    ("Ao lidar com atendimento ao público, você tende a:",["Resolver objetivamente o problema apresentado","Criar vínculo e deixar a pessoa à vontade","Escutar com paciência e acolhimento","Registrar informações com precisão"]),
    ("Quando precisa aprender um novo sistema, você prefere:",["Explorar sozinho e testar caminhos","Aprender com alguém e trocar dicas","Receber passo a passo e praticar com calma","Ler orientações e validar cada procedimento"]),
    ("Em tarefas de alto volume, você costuma:",["Acelerar decisões para entregar resultado","Manter energia e engajamento do grupo","Organizar uma rotina constante de produção","Criar controles para reduzir erros"]),
    ("Quando discorda de uma orientação, você:",["Apresenta sua posição de forma direta","Tenta persuadir com boa comunicação","Evita tensão e busca consenso","Fundamenta a discordância com dados e normas"]),
    ("Você se sente mais confortável em ambientes:",["Com autonomia, metas claras e decisões rápidas","Com interação, reconhecimento e troca constante","Com previsibilidade, cooperação e estabilidade","Com regras claras, qualidade técnica e precisão"]),
    ("Na entrega final de um trabalho, você valoriza mais:",["Impacto e resultado dentro do prazo","Boa apresentação e aceitação pelas pessoas","Confiabilidade e continuidade do serviço","Correção técnica e ausência de falhas"]),
]
DISC_AVISO = "O perfil DISC é um indicador comportamental de apoio. Ele não substitui análise curricular, entrevista estruturada, prova prática ou avaliação técnica do trabalho."
LETRAS_DISC = ["D","I","S","C"]
DISCLAIMER = "O JurisBank atua exclusivamente como plataforma de aproximação. A publicação deste Seletivo não configura processo seletivo vinculante, concurso público ou compromisso de contratação. O uso do ius indicandum é de responsabilidade exclusiva do recrutador, que deve observar as normas de impessoalidade e vedação ao nepotismo aplicáveis ao seu órgão."

# ── Funções ───────────────────────────────────────────────────────────────────
def cor_avatar(n): return AVATAR_CORES[sum(ord(c) for c in n)%len(AVATAR_CORES)]
def iniciais(n):
    p=n.strip().split()
    return (p[0][0]+p[-1][0]).upper() if len(p)>=2 else n[:2].upper()
def hash_senha(s): return hashlib.sha256(s.encode()).hexdigest()
def rec_logado(): return "rec_logado" in st.session_state and st.session_state.rec_logado
def cand_logado(): return "cand_logado" in st.session_state and st.session_state.cand_logado
def gerar_id(): return f"ch_{datetime.now().strftime('%Y%m%d%H%M%S')}"
def anos_num(v):
    m = re.search(r"\d+", str(v or ""))
    return int(m.group()) if m else 0
def ch_aberta(ch):
    if ch.get("status","").lower()!="aberto": return False
    try: return datetime.strptime(ch.get("prazo",""),"%d/%m/%Y").date()>=date.today()
    except: return True
def inscritos(ch):
    r=str(ch.get("inscritos","")).strip()
    return [e.strip() for e in r.split(",") if e.strip()] if r else []

def ir(p):
    st.session_state.pagina=p
    st.query_params.clear()
    st.query_params["p"]=p
    st.rerun()

def extrair_pdf(f):
    doc=fitz.open(stream=f.read(),filetype="pdf")
    return "".join(p.get_text() for p in doc)

def imagem_data_url(upload):
    if not upload:
        return ""
    mime = getattr(upload, "type", None) or "image/png"
    return f"data:{mime};base64,{base64.b64encode(upload.getvalue()).decode('utf-8')}"

def html_texto(valor):
    return html_lib.escape(str(valor or "")).replace("\n", "<br>")

def extrair_campos(txt):
    c={"nome":"","email":"","oab":"Não","experiencia_orgaos":"","sistemas":"","pos_graduacao":"","resumo":""}
    ls=txt.split("\n"); tc=txt.lower()
    em=re.findall(r'[\w\.\-]+@[\w\.\-]+\.\w+',txt)
    if em: c["email"]=em[0]
    if "oab" in tc or "ordem dos advogados" in tc: c["oab"]="Sim"
    sis=["Eproc","SAJ","SIG","SEEU","SISP","APOIA","GAIA","Pandora","SIMBA"]
    enc=[s for s in sis if s.lower() in tc]
    if enc: c["sistemas"]=", ".join(enc)
    for l in ls:
        l=l.strip()
        if any(x in l for x in ["Pós","pós","Especializ","Mestrado","Doutorado"]):
            if len(l)>10 and not c["pos_graduacao"]: c["pos_graduacao"]=l
    om={"MPSC":"MPSC","TJSC":"TJSC","Defensoria":"Defensoria","Procuradoria":"Procuradoria","Ministério Público":"MP","Tribunal de Justiça":"TJ","AGU":"AGU","PGE":"PGE"}
    eo=[]
    for o,s in om.items():
        if o.lower() in tc and s not in eo: eo.append(s)
    c["experiencia_orgaos"]=", ".join(eo)
    for l in ls:
        l=l.strip()
        if len(l)>5 and not any(x in l for x in ["@","Rua","Av.","http","www","(","PERFIL","CONTATO"]) and not re.match(r'^\d',l):
            c["nome"]=l; break
    ps=[p.strip() for p in txt.split("\n\n") if len(p.strip())>100]
    if ps: c["resumo"]=max(ps,key=len)[:500]
    return c

def calc_selos(oab,anos,carta,aval):
    return {"verificado":"Sim" if oab=="Sim" else "Não","recomendado":"Sim" if carta else "Não","destaque":"Sim" if aval else "Não","experiente":"Sim" if anos>=2 else "Não"}

def linha_candidato(email):
    todos = aba_candidatos.get_all_records()
    email = str(email or "").strip().lower()
    for i, cand in enumerate(todos):
        if str(cand.get("email","")).strip().lower() == email:
            return i + 2, cand
    return None, None

def senha_candidato(cand):
    for campo in ["senha", "senha_hash", "password"]:
        valor = str(cand.get(campo, "") or "").strip()
        if valor:
            return valor
    return ""

def login_candidato(email, senha=None, permitir_sem_senha=True):
    _, cand = linha_candidato(email)
    if cand:
        senha_salva = senha_candidato(cand)
        if senha_salva and hash_senha(senha or "") != senha_salva:
            return None
        if not senha_salva and senha and not permitir_sem_senha:
            return None
        st.session_state.cand_logado = cand
        st.session_state.cand_email_logado = cand.get("email", "")
        return cand
    return None

def restaurar_candidato_da_sessao():
    email = str(st.session_state.get("cand_email_logado", "") or "").strip().lower()
    if cand_logado() or not email:
        return
    _, cand = linha_candidato(email)
    if cand:
        st.session_state.cand_logado = cand

def restaurar_recrutador_da_sessao():
    email = str(st.session_state.get("rec_email_logado", "") or "").strip().lower()
    if rec_logado() or not email:
        return
    for rec in aba_recrutadores.get_all_records():
        if str(rec.get("email", "")).strip().lower() == email:
            st.session_state.rec_logado = rec
            return

def carregar_lista_json(valor):
    if not valor:
        return []
    try:
        dados = json.loads(valor)
        return dados if isinstance(dados, list) else []
    except Exception:
        return []

def salvar_lista_json(lista):
    return json.dumps(lista, ensure_ascii=False)

def formacoes_candidato(c):
    dados = carregar_lista_json(c.get("formacao",""))
    if dados:
        return dados
    if c.get("formacao") or c.get("instituicao"):
        return [{"grau": c.get("formacao",""), "instituicao": c.get("instituicao",""), "periodo": ""}]
    return []

def experiencias_candidato(c):
    dados = carregar_lista_json(c.get("experiencia_orgaos",""))
    if dados:
        return dados
    if c.get("experiencia_orgaos") or c.get("sistemas"):
        return [{
            "instituicao": "",
            "orgao": c.get("experiencia_orgaos",""),
            "supervisor": "",
            "supervisor_email": "",
            "inicio": "",
            "fim": "",
            "area": "",
            "atribuicoes": "",
            "sistemas": c.get("sistemas",""),
            "ferramenta_ia": "",
        }]
    return []

def resumo_formacoes(formacoes):
    partes = []
    for f in formacoes:
        grau = f.get("grau","").strip()
        inst = f.get("instituicao","").strip()
        periodo = f.get("periodo","").strip()
        texto = " · ".join([x for x in [grau, inst, periodo] if x])
        if texto:
            partes.append(texto)
    return " | ".join(partes)

def resumo_experiencias(exps):
    partes = []
    for e in exps:
        inst = e.get("instituicao","").strip()
        orgao = e.get("orgao","").strip()
        area = e.get("area","").strip()
        periodo = " a ".join([x for x in [e.get("inicio","").strip(), e.get("fim","").strip()] if x])
        texto = " · ".join([x for x in [inst, orgao, area, periodo] if x])
        if texto:
            partes.append(texto)
    return " | ".join(partes)

def sistemas_experiencias(exps):
    sis = []
    for e in exps:
        for item in str(e.get("sistemas","")).split(","):
            item = item.strip()
            if item and item not in sis:
                sis.append(item)
        ia = str(e.get("ferramenta_ia","")).strip()
        if ia and f"IA: {ia}" not in sis:
            sis.append(f"IA: {ia}")
    return ", ".join(sis)

def primeira_formacao(c):
    forms = formacoes_candidato(c)
    if forms:
        f = forms[0]
        return " · ".join([x for x in [f.get("grau","").strip(), f.get("instituicao","").strip()] if x]) or "Formação não informada"
    return c.get("instituicao","") or c.get("formacao","") or "Formação não informada"

def resumo_card_candidato(c):
    exps = experiencias_candidato(c)
    exp_txt = resumo_experiencia_recrutador(exps)
    if len(exp_txt) > 120:
        exp_txt = exp_txt[:117].rstrip() + "..."
    sistemas = str(c.get("sistemas","") or "").strip()
    if len(sistemas) > 90:
        sistemas = sistemas[:87].rstrip() + "..."
    return {
        "formacao": primeira_formacao(c),
        "interesse": c.get("area","") or "Interesse não informado",
        "experiencia": exp_txt or "Experiência não informada",
        "sistemas": sistemas or "Sistemas não informados",
        "anos": anos_experiencias(exps),
    }

def resumo_experiencia_recrutador(exps):
    partes = []
    for e in exps:
        instituicao = e.get("instituicao","").strip()
        orgao = e.get("orgao","").strip()
        local = instituicao or orgao
        if not local:
            continue
        funcao = e.get("cargo","").strip() or e.get("funcao","").strip() or e.get("area","").strip()
        duracao = duracao_experiencia_texto(e)
        texto = local
        detalhes = [x for x in [funcao, duracao] if x]
        if detalhes:
            texto += " (" + " · ".join(detalhes) + ")"
        partes.append(texto)
    return " | ".join(partes)

def duracao_experiencia_texto(e):
    ini = parse_data_periodo(e.get("inicio",""))
    fim_txt = e.get("fim","").strip()
    fim = parse_data_periodo(fim_txt) if fim_txt else datetime.today()
    if not ini or not fim or fim < ini:
        return ""
    meses = max(1, (fim.year - ini.year) * 12 + fim.month - ini.month + 1)
    anos = meses // 12
    resto = meses % 12
    if anos and resto:
        return f"{anos} ano(s) e {resto} mês(es)"
    if anos:
        return f"{anos} ano(s)"
    return f"{resto} mês(es)"

def anos_experiencias(exps):
    total = 0.0
    for e in exps:
        ini = parse_data_periodo(e.get("inicio",""))
        fim_txt = e.get("fim","").strip()
        fim = parse_data_periodo(fim_txt) if fim_txt else datetime.today()
        if not ini or not fim:
            continue
        if fim >= ini:
            total += (fim - ini).days / 365.25
    return int(total)

def lista_selecionada(valor, opcoes):
    atuais = [v.strip() for v in str(valor or "").split(",") if v.strip()]
    return [v for v in atuais if v in opcoes]

def parse_data_periodo(valor):
    valor = str(valor or "").strip()
    if not valor:
        return None
    for formato in ("%m/%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(valor, formato)
        except ValueError:
            pass
    return None

def dividir_periodo(valor):
    valor = str(valor or "").replace(" até ", " a ").replace("-", " a ").strip()
    partes = [p.strip() for p in valor.split(" a ") if p.strip()]
    ini = partes[0] if partes else ""
    fim = partes[1] if len(partes) > 1 else ""
    return ini, fim

def mes_ano(valor):
    dt = parse_data_periodo(valor)
    if dt:
        return f"{dt.month:02d}", str(dt.year)
    return f"{date.today().month:02d}", str(date.today().year)

def texto_periodo(mes_inicio, ano_inicio, mes_fim, ano_fim):
    return f"{mes_inicio}/{ano_inicio} a {mes_fim}/{ano_fim}"

def meses_periodo(mes_inicio, ano_inicio, mes_fim, ano_fim):
    try:
        inicio = int(ano_inicio) * 12 + int(mes_inicio)
        fim = int(ano_fim) * 12 + int(mes_fim)
        return max(0, fim - inicio + 1)
    except Exception:
        return 0

def texto_duracao(mes_inicio, ano_inicio, mes_fim, ano_fim):
    meses = meses_periodo(mes_inicio, ano_inicio, mes_fim, ano_fim)
    anos = meses // 12
    resto = meses % 12
    partes = []
    if anos:
        partes.append(f"{anos} ano{'s' if anos != 1 else ''}")
    if resto:
        partes.append(f"{resto} mês{'es' if resto != 1 else ''}")
    return " e ".join(partes) if partes else "0 mês"

def dividir_concurso(valor):
    valor = str(valor or "").strip()
    if " | Estuda há: " in valor:
        nome, tempo = valor.split(" | Estuda há: ", 1)
        return nome.strip(), tempo.strip()
    if valor and valor != "Não estou estudando para concurso":
        return valor, ""
    return "", ""

def formatar_concurso(nome, tempo):
    nome = str(nome or "").strip()
    tempo = str(tempo or "").strip()
    if nome and tempo:
        return f"{nome} | Estuda há: {tempo}"
    if nome:
        return nome
    if tempo:
        return f"Estuda há: {tempo}"
    return "Não estou estudando para concurso"

def html_selos(c):
    h=""
    if c.get("selo_verificado")=="Sim": h+='<span class="selo selo-verificado">✓ Verificado</span>'
    if c.get("selo_recomendado")=="Sim": h+='<span class="selo selo-recomendado">★ Recomendado</span>'
    if c.get("selo_destaque")=="Sim": h+='<span class="selo selo-destaque">◆ Destaque</span>'
    if c.get("selo_experiente")=="Sim": h+='<span class="selo selo-experiente">● Experiente</span>'
    return h

def html_disc(c):
    d=c.get("disc","")
    if not d: return ""
    return f'<span style="font-size:10px;font-weight:700;padding:2px 8px;border-radius:99px;background:{DISC_CORES_BADGE.get(d,"rgba(255,255,255,0.08)")};color:{DISC_TEXTO_BADGE.get(d,"#fff")};margin-left:4px">{d} {DISC_LABEL.get(d,"")}</span>'

def html_conc(c):
    if c.get("concurso") and c.get("concurso")!="Não estou estudando para concurso":
        return '<span style="font-size:10px;font-weight:700;padding:2px 8px;border-radius:99px;background:rgba(200,150,12,0.1);color:#f0c040;margin-left:4px;border:1px solid rgba(200,150,12,0.18)">📚 Concursando</span>'
    return ""

def barra(atual,total=3):
    h='<div class="step-bar">'
    for i in range(1,total+1):
        if i<atual: h+='<div class="step done"></div>'
        elif i==atual: h+='<div class="step active"></div>'
        else: h+='<div class="step"></div>'
    return h+'</div>'

def calc_disc(rs):
    p={"D":0,"I":0,"S":0,"C":0}
    for i,r in enumerate(rs):
        if r is None: continue
        _,ops=PERGUNTAS_DISC[i]; p[LETRAS_DISC[ops.index(r)]]+=1
    d=max(p,key=p.get)
    return d,p,DESCRICOES_DISC[d]

def render_disc(d):
    cb=DISC_CORES_BADGE.get(d,"rgba(255,255,255,0.06)"); tb=DISC_TEXTO_BADGE.get(d,"#fff"); det=DISC_DETALHES.get(d,{})
    return f"""<div class="info-card" style="background:{cb};border-color:#c5d5f5">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px">
            <span style="font-weight:800;color:{tb};font-size:22px">{d}</span>
            <span style="font-weight:700;color:{tb};font-size:15px">{det.get('nome','')}</span>
        </div>
        <p style="color:{tb};font-size:13px;font-weight:600;margin:0 0 8px">{det.get('resumo','')}</p>
        <p style="color:#2a4a8a;font-size:12px;margin:0 0 4px"><strong style="color:{tb}">Pontos fortes:</strong> {det.get('pontos_fortes','')}</p>
        <p style="color:#2a4a8a;font-size:12px;margin:0 0 4px"><strong style="color:{tb}">No gabinete:</strong> {det.get('no_gabinete','')}</p>
        <p style="color:#2a4a8a;font-size:12px;margin:0"><strong style="color:{tb}">Atenção:</strong> {det.get('atencao','')}</p>
    </div>"""


def enviar_email(destinatario, assunto, corpo_html):
    """Envia e-mail via Resend API."""
    try:
        api_key = st.secrets["resend"]["api_key"]
        remetente = st.secrets["resend"]["remetente"]
        payload = json.dumps({
            "from": remetente,
            "to": [destinatario],
            "subject": assunto,
            "html": corpo_html
        }).encode("utf-8")
        req = urllib.request.Request(
            "https://api.resend.com/emails",
            data=payload,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            method="POST"
        )
        with urllib.request.urlopen(req) as response:
            return response.status == 200
    except Exception as e:
        return False

def email_recomendador(nome_candidato, email_recomendador, link):
    assunto = f"JurisBank — {nome_candidato} solicitou sua avaliação"
    corpo = f"""
    <div style="font-family:'Segoe UI',Arial,sans-serif;max-width:600px;margin:0 auto;background:#ffffff">
        <div style="background:linear-gradient(135deg,#0d1f4e,#1a3a8f);padding:32px;text-align:center;border-radius:12px 12px 0 0">
            <div style="width:48px;height:48px;background:linear-gradient(135deg,#c8960c,#f0c040);border-radius:10px;display:inline-flex;align-items:center;justify-content:center;font-size:24px;margin-bottom:12px">⚖</div>
            <h1 style="color:#ffffff;font-size:22px;margin:0;letter-spacing:-0.5px">JurisBank</h1>
            <p style="color:rgba(255,255,255,0.6);font-size:12px;margin:4px 0 0;font-style:italic">ius indicandum</p>
        </div>
        <div style="padding:32px;background:#f4f6fc;border-radius:0 0 12px 12px">
            <h2 style="color:#0d1f4e;font-size:20px;margin:0 0 12px">Solicitação de avaliação</h2>
            <p style="color:#4a5568;font-size:15px;line-height:1.7;margin:0 0 20px">
                O profissional <strong style="color:#0d1f4e">{nome_candidato}</strong> indicou você como recomendador no JurisBank e solicita que você preencha uma avaliação do seu perfil profissional.
            </p>
            <p style="color:#4a5568;font-size:14px;line-height:1.7;margin:0 0 24px">
                A avaliação é rápida (menos de 5 minutos) e ficará disponível para recrutadores de Tribunais, Ministérios Públicos, Defensorias e Procuradorias ao analisar o perfil do candidato.
            </p>
            <div style="text-align:center;margin:28px 0">
                <a href="{link}" style="display:inline-block;padding:14px 36px;background:linear-gradient(135deg,#c8960c,#f0c040);color:#0d1f4e;font-weight:700;font-size:15px;border-radius:10px;text-decoration:none">
                    Preencher avaliação →
                </a>
            </div>
            <p style="color:#8090b8;font-size:12px;line-height:1.6;margin:0;border-top:1px solid #d0dcfa;padding-top:16px">
                Este link é exclusivo e de uso único. Caso não reconheça esta solicitação, ignore este e-mail.<br>
                <strong>JurisBank</strong> — plataforma de aproximação entre profissionais do Direito e órgãos do sistema de justiça.
            </p>
        </div>
    </div>
    """
    return enviar_email(email_recomendador, assunto, corpo)

# ── TOPBAR ────────────────────────────────────────────────────────────────────
restaurar_candidato_da_sessao()
restaurar_recrutador_da_sessao()

PAGINAS_CANDIDATO = ["inicio","perfil","cadastro","chamadas"]
PAGINAS_PUBLICAS = ["publico","candidatos","privacidade","termos","recomendar"]

if rec_logado() and pagina == "recrutador":
    dash_param = params.get("dash", "")
    if isinstance(dash_param, list):
        dash_param = dash_param[0]
    if dash_param in ["perfil","seletivos","banco"]:
        st.session_state.rec_dashboard = dash_param
    sair_param = params.get("sair", "")
    if isinstance(sair_param, list):
        sair_param = sair_param[0]
    if sair_param == "1":
        del st.session_state.rec_logado
        st.session_state.pop("rec_email_logado", None)
        ir("recrutador")

if cand_logado() and pagina in PAGINAS_CANDIDATO:
    sair_cand_param = params.get("sair_cand", "")
    if isinstance(sair_cand_param, list):
        sair_cand_param = sair_cand_param[0]
    if sair_cand_param == "1":
        del st.session_state.cand_logado
        st.session_state.pop("cand_email_logado", None)
        ir("publico")

if rec_logado():
    nav_pages = []
elif cand_logado():
    nav_pages = [
        ("inicio","Meu Perfil"),
        ("perfil","Editar Perfil"),
        ("chamadas","Seletivos"),
    ]
else:
    nav_pages = [
        ("publico","Início"),
        ("inicio","Sou Candidato"),
        ("recrutador","Sou Recrutador"),
    ]

nav_html = '<div class="topbar"><a class="topbar-logo" href="https://lcatolico.github.io/jurisbank/" target="_blank"><div class="topbar-logo-icon">JB</div><div><span class="topbar-logo-name">JurisBank</span></div></a><div class="topbar-nav">'
for pg, lb in nav_pages:
    active = "active" if pagina == pg else ""
    if not rec_logado() and not cand_logado():
        if lb == "Sou Candidato" and pagina in ["inicio","cadastro","chamadas"]:
            active = "active"
        elif lb == "Sou Recrutador" and pagina == "recrutador":
            active = "active"
    nav_html += f'<a href="?p={pg}" class="{active}">{lb}</a>'

if rec_logado():
    dash_atual = st.session_state.get("rec_dashboard","perfil")
    for dash, lb in [("perfil","Perfil"),("seletivos","Seletivos"),("banco","Banco de Candidatos")]:
        active = "active" if pagina == "recrutador" and dash_atual == dash else ""
        nav_html += f'<a href="?p=recrutador&dash={dash}" class="{active}">{lb}</a>'
    nav_html += '<a href="?p=recrutador&sair=1" class="btn-rec">Sair</a>'
elif cand_logado() and pagina in PAGINAS_CANDIDATO:
    nav_html += '<a href="?p=inicio&sair_cand=1" class="btn-rec">Sair</a>'

nav_html += '</div></div>'
st.markdown(nav_html, unsafe_allow_html=True)

# ── PÁGINA PÚBLICA ────────────────────────────────────────────────────────────
if pagina == "publico":
    st.markdown("""<div class="hero-card">
        <h1 class="page-title">JurisBank<br><em>Ambientes.</em></h1>
        <p class="page-sub">Acesse o espaço correto para consultar oportunidades, gerir seu perfil ou conduzir Seletivos.</p>
    </div>""", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""<div class="profile-section-card">
            <p class="profile-section-title">Candidato</p>
            <div class="profile-list-item">
                Consulte Seletivos, acompanhe inscrições e mantenha seu perfil profissional atualizado.
            </div>
        </div>""", unsafe_allow_html=True)
        if st.button("Entrar como candidato", key="btn_publico_candidato"):
            ir("inicio")
    with c2:
        st.markdown("""<div class="profile-section-card">
            <p class="profile-section-title">Recrutador</p>
            <div class="profile-list-item">
                Publique Seletivos, organize candidatos, favoritos, anotações e inscrições.
            </div>
        </div>""", unsafe_allow_html=True)
        if st.button("Entrar como recrutador", key="btn_publico_recrutador"):
            ir("recrutador")

# ── PÁGINA: INÍCIO / ÁREA DO CANDIDATO ────────────────────────────────────────
elif pagina == "inicio":
    if cand_logado():
        cand = st.session_state.cand_logado
        abertos = [ch for ch in aba_chamadas.get_all_records() if ch_aberta(ch)]

        formacoes_view = formacoes_candidato(cand)
        experiencias_view = experiencias_candidato(cand)

        editar_param = params.get("editar", "")
        if isinstance(editar_param, list):
            editar_param = editar_param[0]
        if editar_param == "1":
            st.session_state.editar_perfil_candidato = True

        disponivel = cand.get("disponibilidade") == "Sim"
        disponivel_txt = "Disponível" if disponivel else "Indisponível"
        selos = []
        if cand.get("selo_verificado") == "Sim":
            selos.append('<span class="profile-chip">✓ Verificado</span>')
        if cand.get("selo_recomendado") == "Sim":
            selos.append('<span class="profile-chip profile-chip-green">★ Recomendado</span>')
        if cand.get("selo_destaque") == "Sim":
            selos.append('<span class="profile-chip profile-chip-gold">◆ Destaque</span>')
        if cand.get("selo_experiente") == "Sim":
            selos.append('<span class="profile-chip">● Experiente</span>')
        selos_html = "".join(selos) or '<span class="profile-chip">Sem selos ativos</span>'
        disc_html = ""
        if cand.get("disc"):
            det_disc = DISC_DETALHES.get(cand["disc"], {})
            disc_html = f'<div class="profile-disc-card"><div class="profile-disc-letter">{html_lib.escape(cand["disc"])}</div><p class="profile-disc-text">{html_lib.escape(det_disc.get("resumo",""))}</p></div>'
        concurso_val = cand.get("concurso","Não estou estudando para concurso") or "Não estou estudando para concurso"
        concurso_html = ""
        if concurso_val != "Não estou estudando para concurso":
            concurso_html = f'<div class="profile-concurso">📚 Estudando para: {html_lib.escape(concurso_val)}</div>'
        interesses = cand.get("area","").strip()
        subtitulo = interesses or "Perfil profissional em construção"
        status_class = "" if disponivel else "profile-status-off"
        email_link = urllib.parse.quote(cand.get("email",""))
        foto_url = str(cand.get("foto","") or "").strip()
        avatar_html = f'<img class="profile-photo" src="{html_lib.escape(foto_url)}" alt="Foto de perfil">' if foto_url else f'<div class="profile-avatar">{html_lib.escape(iniciais(cand.get("nome","")))}</div>'
        formacoes_html = "".join(
            f'<div class="profile-list-item">{html_lib.escape(f.get("grau","—"))}<br><span>{html_lib.escape(" · ".join([x for x in [f.get("instituicao","").strip(), f.get("periodo","").strip()] if x]) or "Instituição/período não informados")}</span></div>'
            for f in formacoes_view
        ) or '<div class="profile-empty">Nenhuma formação informada.</div>'
        experiencias_html = "".join(
            f'<div class="profile-list-item">{html_lib.escape(e.get("orgao","") or e.get("instituicao","") or "Experiência informada")}<br><span>{html_lib.escape(" · ".join([x for x in [e.get("instituicao","").strip(), e.get("area","").strip(), " a ".join([v for v in [e.get("inicio","").strip(), e.get("fim","").strip()] if v])] if x]) or "Detalhes não informados")}</span></div>'
            for e in experiencias_view
        ) or '<div class="profile-empty">Nenhuma experiência profissional informada.</div>'
        sistemas_html = html_lib.escape(cand.get("sistemas","").strip() or "Nenhum sistema informado.")
        interesses_html = html_lib.escape(interesses or "Nenhuma instituição de interesse informada.")
        perfil_html = (
            f'<div class="profile-panel">'
            f'<div class="profile-head">'
            f'{avatar_html}'
            f'<div>'
            f'<p class="profile-name-main">{html_lib.escape(cand.get("nome",""))}</p>'
            f'<p class="profile-sub-main">{html_lib.escape(subtitulo)}</p>'
            f'<p class="cand-sub">{html_lib.escape(cand.get("email",""))}</p>'
            f'</div>'
            f'</div>'
            f'<div class="profile-chip-row">{selos_html}</div>'
            f'{disc_html}'
            f'{concurso_html}'
            f'<div class="profile-section-grid">'
            f'<div class="profile-section-card">'
            f'<p class="profile-section-title">Formação acadêmica</p>'
            f'<div class="profile-list">{formacoes_html}</div>'
            f'</div>'
            f'<div class="profile-section-card">'
            f'<p class="profile-section-title">Instituições de interesse</p>'
            f'<div class="profile-list-item">{interesses_html}</div>'
            f'</div>'
            f'<div class="profile-section-card">'
            f'<p class="profile-section-title">Resumo profissional</p>'
            f'<strong>Experiência total:</strong> {anos_experiencias(experiencias_view)} ano(s)<br>'
            f'<strong>OAB ativa:</strong> {html_lib.escape(cand.get("oab","—"))}'
            f'</div>'
            f'<div class="profile-section-card">'
            f'<p class="profile-section-title">Sistemas e IA</p>'
            f'<div class="profile-list-item">{sistemas_html}</div>'
            f'</div>'
            f'<div class="profile-section-card full">'
            f'<p class="profile-section-title">Experiência profissional</p>'
            f'<div class="profile-list">{experiencias_html}</div>'
            f'</div>'
            f'</div>'
            f'<div class="profile-foot">'
            f'<span class="profile-status {status_class}">● {disponivel_txt}</span>'
            f'</div>'
            f'</div>'
        )
        st.markdown(perfil_html, unsafe_allow_html=True)
        cver, cedit, cesp = st.columns([2, 2, 5])
        with cver:
            if st.button("Ver seletivos →", key="btn_cand_ver_seletivos"):
                ir("chamadas")
        with cedit:
            if st.button("Editar perfil →", key="btn_cand_editar_perfil"):
                ir("perfil")
        st.session_state.editar_perfil_candidato = False

    else:
        st.markdown("""<div class="hero-card">
            <h1 class="page-title">Área do<br><em>Candidato.</em></h1>
            <p class="page-sub">Entre para acompanhar seu perfil ou comece seu cadastro no JurisBank.</p>
        </div>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        tabs = st.tabs(["Já tenho cadastro","Cadastrar-me"])
        with tabs[0]:
            st.markdown('<p style="font-size:16px;font-weight:700;color:#0d1f4e;margin:1rem 0">Entrar no meu perfil</p>', unsafe_allow_html=True)
            email_login = st.text_input("E-mail cadastrado", key="login_candidato_inicio")
            senha_login = st.text_input("Senha", type="password", key="senha_candidato_inicio", help="Perfis antigos sem senha ainda podem entrar apenas com o e-mail.")
            if st.button("Entrar", key="btn_login_candidato_inicio"):
                if not email_login:
                    st.error("Informe seu e-mail.")
                elif login_candidato(email_login, senha_login, permitir_sem_senha=True):
                    st.success("Bem-vindo ao JurisBank.")
                    st.rerun()
                else:
                    st.error("E-mail ou senha inválidos.")
        with tabs[1]:
            st.markdown("""<div class="info-card">
                <strong>Cadastre seu currículo jurídico</strong><br>
                Crie seu perfil, solicite selos de certificação, responda ao DISC e apareça no banco de talentos.
            </div>""", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Começar cadastro →", key="btn_ir_cadastro_candidato"):
                ir("cadastro")

# ── PÁGINA: EDITAR PERFIL DO CANDIDATO ───────────────────────────────────────
elif pagina == "perfil":
    email_param = params.get("email", "")
    if isinstance(email_param, list):
        email_param = email_param[0]
    if not cand_logado() and email_param:
        login_candidato(email_param, permitir_sem_senha=True)
    if not cand_logado():
        st.markdown("""<div class="edit-hero">
            <h1 class="edit-title">Editar <em>Perfil.</em></h1>
            <p class="page-sub">Entre com e-mail e senha para alterar suas informações profissionais.</p>
        </div>""", unsafe_allow_html=True)
        email_editar = st.text_input("E-mail cadastrado", value=email_param, key="login_editar_email")
        senha_editar = st.text_input("Senha", type="password", key="login_editar_senha")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Entrar e editar perfil", key="btn_login_editar_perfil"):
                if not email_editar:
                    st.error("Informe seu e-mail.")
                elif login_candidato(email_editar, senha_editar, permitir_sem_senha=True):
                    st.rerun()
                else:
                    st.error("E-mail ou senha inválidos.")
        with c2:
            if st.button("Voltar à Área do Candidato", key="btn_voltar_login_cand"):
                ir("inicio")
    else:
        cand = st.session_state.cand_logado
        formacoes_base = formacoes_candidato(cand) or [{"grau":"Bacharel em Direito","instituicao":"","periodo":""}]
        experiencias_base = experiencias_candidato(cand) or [{"instituicao":"","orgao":"","cargo":"","supervisor":"","supervisor_email":"","inicio":"","fim":"","area":"","atribuicoes":"","sistemas":"","ferramenta_ia":""}]
        if "edit_qtd_form" not in st.session_state:
            st.session_state.edit_qtd_form = max(1, len(formacoes_base))
        if "edit_qtd_exp" not in st.session_state:
            st.session_state.edit_qtd_exp = max(1, len(experiencias_base))

        st.markdown("""<div class="edit-hero">
            <h1 class="edit-title">Editar <em>Perfil.</em></h1>
            <p class="edit-sub">Atualize suas informações profissionais. Nome e e-mail permanecem vinculados ao cadastro.</p>
        </div>""", unsafe_allow_html=True)

        if st.button("Voltar ao perfil", key="voltar_perfil_candidato"):
            ir("inicio")

        with st.form("form_editar_candidato_pagina"):
            st.markdown('<div class="highlight-panel">Disponível para seleção</div>', unsafe_allow_html=True)
            disponibilidade = st.radio("Disponível para seleção?", ["Sim","Não"], index=0 if cand.get("disponibilidade") == "Sim" else 1, horizontal=True)

            st.markdown('<p class="section-label">Fotografia de perfil</p>', unsafe_allow_html=True)
            foto = st.file_uploader("Fotografia de perfil", type=["jpg","jpeg","png"], key="foto_edit_cand_page")
            if foto:
                st.image(foto, width=120)
                st.caption("Prévia da foto. Para manter a imagem após reiniciar o app, será necessário configurar armazenamento permanente.")
            foto_data = imagem_data_url(foto) if foto else cand.get("foto","")

            st.markdown('<p class="section-label">Formação acadêmica</p>', unsafe_allow_html=True)
            formacoes = []
            for i in range(st.session_state.edit_qtd_form):
                base = formacoes_base[i] if i < len(formacoes_base) else {"grau":"Bacharel em Direito","instituicao":"","periodo":""}
                ini_base, fim_base = dividir_periodo(base.get("periodo",""))
                mi, ai = mes_ano(ini_base)
                mf, af = mes_ano(fim_base)
                st.markdown(f'<div class="form-item-title">Formação {i+1}</div>', unsafe_allow_html=True)
                c1, c2 = st.columns([2,3])
                with c1:
                    grau = st.selectbox("Formação", FORMACOES, index=(FORMACOES.index(base.get("grau")) if base.get("grau") in FORMACOES else 0), key=f"page_edit_grau_{i}")
                with c2:
                    instituicao = st.text_input("Instituição de ensino", value=base.get("instituicao",""), key=f"page_edit_inst_{i}")
                st.markdown('<p class="add-hint">Período da formação</p>', unsafe_allow_html=True)
                p1, p2, p3, p4, p5 = st.columns([1,1,1,1,1.4])
                with p1:
                    mes_inicio = st.selectbox("Início mês", MESES, index=MESES.index(mi), key=f"page_edit_form_mi_{i}")
                with p2:
                    ano_inicio = st.selectbox("Início ano", ANOS_PERIODO, index=ANOS_PERIODO.index(ai) if ai in ANOS_PERIODO else 0, key=f"page_edit_form_ai_{i}")
                with p3:
                    mes_fim = st.selectbox("Final mês", MESES, index=MESES.index(mf), key=f"page_edit_form_mf_{i}")
                with p4:
                    ano_fim = st.selectbox("Final ano", ANOS_PERIODO, index=ANOS_PERIODO.index(af) if af in ANOS_PERIODO else 0, key=f"page_edit_form_af_{i}")
                with p5:
                    st.text_input("Duração", value=texto_duracao(mes_inicio, ano_inicio, mes_fim, ano_fim), disabled=True, key=f"page_edit_form_dur_{i}")
                formacoes.append({"grau":grau,"instituicao":instituicao,"periodo":texto_periodo(mes_inicio, ano_inicio, mes_fim, ano_fim)})
            add_form_submit = st.form_submit_button("+ Adicionar formação")

            st.markdown('<p class="section-label">Experiência profissional</p>', unsafe_allow_html=True)
            experiencias = []
            for i in range(st.session_state.edit_qtd_exp):
                base = experiencias_base[i] if i < len(experiencias_base) else {"instituicao":"","orgao":"","cargo":"","supervisor":"","supervisor_email":"","inicio":"","fim":"","area":"","atribuicoes":"","sistemas":"","ferramenta_ia":""}
                mi, ai = mes_ano(base.get("inicio",""))
                mf, af = mes_ano(base.get("fim",""))
                st.markdown(f'<div class="form-item-title">Experiência {i+1}</div>', unsafe_allow_html=True)
                inst_exp_opcoes = ["Selecione..."] + INSTITUICOES_INTERESSE
                instituicao_sel = st.selectbox("Instituição", inst_exp_opcoes, index=(inst_exp_opcoes.index(base.get("instituicao")) if base.get("instituicao") in inst_exp_opcoes else 0), key=f"page_edit_exp_instituicao_{i}")
                instituicao_exp = "" if instituicao_sel == "Selecione..." else instituicao_sel
                c_org,c_fun=st.columns(2)
                with c_org:
                    orgao = st.text_input("Órgão de atuação", value=base.get("orgao",""), key=f"page_edit_exp_orgao_{i}")
                with c_fun:
                    cargo_exp = st.text_input("Cargo/função exercida", value=base.get("cargo",base.get("funcao","")), placeholder="Ex: Assessor jurídico, estagiário, residente", key=f"page_edit_exp_cargo_{i}")
                area_exp = st.multiselect("Áreas de atuação", AREAS, default=lista_selecionada(base.get("area",""), AREAS), key=f"page_edit_exp_area_{i}")
                c1, c2 = st.columns(2)
                with c1:
                    sistemas_exp = st.text_input("Sistemas de trabalho", value=base.get("sistemas",""), placeholder="Ex: Eproc, SAJ, SEEU", key=f"page_edit_exp_sis_{i}")
                with c2:
                    ferramenta_ia = st.text_input("Ferramenta de IA", value=base.get("ferramenta_ia",""), placeholder="Ex: ChatGPT, Gemini, Copilot", key=f"page_edit_exp_ia_{i}")
                atribuicoes = st.text_area("Atribuições desenvolvidas", value=base.get("atribuicoes",""), height=80, key=f"page_edit_exp_atr_{i}")
                st.markdown('<p class="add-hint">Tempo de experiência</p>', unsafe_allow_html=True)
                c1, c2, c3, c4, c5 = st.columns([1,1,1,1,1.4])
                with c1:
                    mes_inicio = st.selectbox("Início mês", MESES, index=MESES.index(mi), key=f"page_edit_exp_mi_{i}")
                with c2:
                    ano_inicio = st.selectbox("Início ano", ANOS_PERIODO, index=ANOS_PERIODO.index(ai) if ai in ANOS_PERIODO else 0, key=f"page_edit_exp_ai_{i}")
                with c3:
                    mes_fim = st.selectbox("Final mês", MESES, index=MESES.index(mf), key=f"page_edit_exp_mf_{i}")
                with c4:
                    ano_fim = st.selectbox("Final ano", ANOS_PERIODO, index=ANOS_PERIODO.index(af) if af in ANOS_PERIODO else 0, key=f"page_edit_exp_af_{i}")
                with c5:
                    st.text_input("Duração", value=texto_duracao(mes_inicio, ano_inicio, mes_fim, ano_fim), disabled=True, key=f"page_edit_exp_dur_{i}")
                c1, c2 = st.columns(2)
                with c1:
                    supervisor = st.text_input("Supervisor", value=base.get("supervisor",""), key=f"page_edit_exp_supervisor_{i}")
                with c2:
                    supervisor_email = st.text_input("E-mail de contato", value=base.get("supervisor_email",""), placeholder="nome@orgao.jus.br", key=f"page_edit_exp_supervisor_email_{i}")
                experiencias.append({"instituicao":instituicao_exp,"orgao":orgao,"cargo":cargo_exp,"supervisor":supervisor,"supervisor_email":supervisor_email,"inicio":f"{mes_inicio}/{ano_inicio}","fim":f"{mes_fim}/{ano_fim}","area":", ".join(area_exp),"atribuicoes":atribuicoes,"sistemas":sistemas_exp,"ferramenta_ia":ferramenta_ia})
            add_exp_submit = st.form_submit_button("+ Adicionar experiência")

            st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
            st.markdown('<p class="section-label">Outras informações acadêmicas e profissionais</p>', unsafe_allow_html=True)
            st.caption("Use este campo para cursos livres, publicações, produção acadêmica, idiomas, atividades docentes, projetos, voluntariado jurídico, premiações e outras informações que ajudem o recrutador a entender sua trajetória.")
            resumo = st.text_area("Outras informações", value=cand.get("resumo",""), height=120)

            st.markdown('<p class="section-label">OAB</p>', unsafe_allow_html=True)
            oab = st.radio("OAB ativa?", ["Sim","Não"], index=0 if cand.get("oab") == "Sim" else 1, horizontal=True)

            st.markdown('<p class="section-label">Concurso</p>', unsafe_allow_html=True)
            estuda_concurso = st.radio("Estuda para concurso?", ["Não","Sim"], index=1 if cand.get("concurso") and cand.get("concurso")!="Não estou estudando para concurso" else 0, horizontal=True)
            concurso = "Não estou estudando para concurso"
            if estuda_concurso == "Sim":
                concurso_base, tempo_base = dividir_concurso(cand.get("concurso",""))
                c1, c2 = st.columns(2)
                with c1:
                    concurso_nome = st.text_input("Qual concurso?", value=concurso_base)
                with c2:
                    concurso_tempo = st.text_input("Há quanto tempo estuda?", value=tempo_base, placeholder="Ex: 1 ano e 6 meses")
                concurso = formatar_concurso(concurso_nome, concurso_tempo)

            st.markdown('<p class="section-label">Instituições de interesse para trabalhar</p>', unsafe_allow_html=True)
            st.markdown('<div class="info-box">A indicação das instituições servirá como filtro para envio ou acesso de informações por recrutadores.</div>', unsafe_allow_html=True)
            inst_interesse = st.multiselect("Selecione uma ou mais instituições", INSTITUICOES_INTERESSE, default=lista_selecionada(cand.get("area",""), INSTITUICOES_INTERESSE), key="page_edit_inst_interesse")
            salvar = st.form_submit_button("Salvar alterações")

        if add_form_submit:
            st.session_state.edit_qtd_form = min(8, st.session_state.edit_qtd_form + 1)
            st.rerun()
        if add_exp_submit:
            st.session_state.edit_qtd_exp = min(10, st.session_state.edit_qtd_exp + 1)
            st.rerun()
        if salvar:
            linha, atual = linha_candidato(cand.get("email"))
            if not linha:
                st.error("Não encontrei seu cadastro na planilha.")
            else:
                formacoes_validas = [f for f in formacoes if f.get("grau") or f.get("instituicao") or f.get("periodo")]
                experiencias_validas = [e for e in experiencias if e.get("instituicao") or e.get("orgao") or e.get("cargo") or e.get("supervisor") or e.get("supervisor_email") or e.get("area") or e.get("atribuicoes") or e.get("sistemas") or e.get("ferramenta_ia")]
                formacao_final = salvar_lista_json(formacoes_validas)
                instituicao_final = resumo_formacoes(formacoes_validas)
                area_final = ", ".join(inst_interesse)
                experiencia_final = salvar_lista_json(experiencias_validas)
                sistemas = sistemas_experiencias(experiencias_validas)
                anos = anos_experiencias(experiencias_validas)
                selo_verificado = "Sim" if oab == "Sim" else "Não"
                selo_experiente = "Sim" if anos >= 2 else "Não"
                atual.update({
                    "formacao": formacao_final,
                    "instituicao": instituicao_final,
                    "area": area_final,
                    "disponibilidade": disponibilidade,
                    "oab": oab,
                    "experiencia_orgaos": experiencia_final,
                    "sistemas": sistemas,
                    "foto": foto_data,
                    "resumo": resumo,
                    "selo_verificado": selo_verificado,
                    "selo_experiente": selo_experiente,
                    "concurso": concurso,
                })
                aba_candidatos.update_cell(linha, 3, formacao_final)
                aba_candidatos.update_cell(linha, 4, instituicao_final)
                aba_candidatos.update_cell(linha, 5, area_final)
                aba_candidatos.update_cell(linha, 6, disponibilidade)
                aba_candidatos.update_cell(linha, 7, oab)
                aba_candidatos.update_cell(linha, 8, experiencia_final)
                aba_candidatos.update_cell(linha, 9, sistemas)
                aba_candidatos.update_cell(linha, 11, resumo)
                aba_candidatos.update_cell(linha, 13, selo_verificado)
                aba_candidatos.update_cell(linha, 16, selo_experiente)
                aba_candidatos.update_cell(linha, 18, concurso)
                aba_candidatos.update_cell(linha, CAND_COL_FOTO, foto_data)
                st.session_state.cand_logado = atual
                st.session_state.cand_email_logado = atual.get("email", "")
                st.success("Perfil atualizado com sucesso.")
                ir("inicio")

# ── PÁGINA: CANDIDATOS ────────────────────────────────────────────────────────
elif pagina == "candidatos":
    dados = aba_candidatos.get_all_records()
    if "cand_sel" not in st.session_state: st.session_state.cand_sel = None

    if st.session_state.cand_sel:
        c = st.session_state.cand_sel; cor = cor_avatar(c["nome"])
        formacoes_view = formacoes_candidato(c)
        experiencias_view = experiencias_candidato(c)
        if st.button("← Voltar"):
            st.session_state.cand_sel = None; st.rerun()

        foto_detalhe = str(c.get("foto","") or "").strip()
        avatar_detalhe = f'<img class="cand-photo-lg" src="{html_lib.escape(foto_detalhe)}" alt="Foto de perfil">' if foto_detalhe else f'<div class="avatar" style="width:60px;height:60px;border-radius:14px;background:{cor};font-size:20px">{iniciais(c["nome"])}</div>'
        st.markdown(f"""
        <div class="hero-card">
            <div style="display:flex;align-items:center;gap:16px">
                {avatar_detalhe}
                <div>
                    <div class="profile-name">{html_texto(c.get('nome','—'))}</div>
                    <div style="font-size:13px;color:#4a6080;margin-bottom:6px">{html_texto(resumo_formacoes(formacoes_view) or c.get('instituicao','—'))}</div>
                    <div>{html_selos(c)}</div>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

        col1,col2,col3,col4=st.columns(4)
        for col,lb,vl in [(col1,"Interesse",c.get("area","—")),(col2,"OAB",c.get("oab","—")),(col3,"Disponível",c.get("disponibilidade","—")),(col4,"Experiência",resumo_experiencias(experiencias_view) or "—")]:
            with col: st.markdown(f'<div class="metric-box"><p class="metric-label">{lb}</p><p class="metric-value">{html_texto(vl)}</p></div>',unsafe_allow_html=True)

        if c.get("disc"):
            st.markdown('<p class="section-label">Perfil DISC</p>',unsafe_allow_html=True)
            st.markdown(render_disc(c["disc"]),unsafe_allow_html=True)
        if c.get("concurso") and c.get("concurso")!="Não estou estudando para concurso":
            st.markdown('<p class="section-label">Concurso</p>',unsafe_allow_html=True)
            st.markdown(f'<div class="info-card">📚 {html_texto(c["concurso"])}</div>',unsafe_allow_html=True)
        if c.get("sistemas"):
            st.markdown('<p class="section-label">Sistemas</p>',unsafe_allow_html=True)
            st.markdown(f'<div class="info-card">{html_texto(c["sistemas"])}</div>',unsafe_allow_html=True)
        if c.get("resumo"):
            st.markdown('<p class="section-label">Resumo</p>',unsafe_allow_html=True)
            if rec_logado():
                st.markdown(f'<div class="info-card">{html_texto(c["resumo"])}</div>',unsafe_allow_html=True)
            else:
                prev=c["resumo"][:150]+"..." if len(c["resumo"])>150 else c["resumo"]
                st.markdown(f'<div class="info-card">{html_texto(prev)}<br><br><span style="color:#f0c040;font-size:12px">🔐 Resumo completo disponível para recrutadores.</span></div>',unsafe_allow_html=True)
        st.markdown('<p class="section-label">Contato</p>',unsafe_allow_html=True)
        if rec_logado():
            st.markdown(f'<div class="info-card">✉ {html_texto(c.get("email","—"))}</div>',unsafe_allow_html=True)
        else:
            st.markdown('<div class="lock-box">🔐 Disponível apenas para recrutadores aprovados.</div>',unsafe_allow_html=True)
    else:
        total=len(dados); disp=sum(1 for c in dados if c.get("disponibilidade")=="Sim")
        cert=sum(1 for c in dados if any(c.get(f"selo_{s}")=="Sim" for s in ["verificado","recomendado","destaque","experiente"]))
        st.markdown(f"""
        <div class="hero-card">
            <h1 class="page-title">Banco de Talentos<br><em>Jurídicos.</em></h1>
            <p class="page-sub">Profissionais certificados para assessoria em Tribunais, Ministérios Públicos, Procuradorias e Defensorias</p>
            <div class="stats-row">
                <div class="stat-pill">⚖ {total} cadastrados</div>
                <div class="stat-pill">✓ {disp} disponíveis</div>
                <div class="stat-pill">★ {cert} certificados</div>
            </div>
        </div>""", unsafe_allow_html=True)

        col1,col2,col3=st.columns(3)
        with col1: busca=st.text_input("Buscar por nome",placeholder="Nome...")
        with col2:
            ar=["Todas"]+sorted(set(c["area"] for c in dados if c.get("area")))
            asel=st.selectbox("Instituições de Interesse",ar)
        with col3: fsel=st.selectbox("Selo",["Todos","Verificado","Recomendado","Destaque","Experiente"])

        cf=dados
        if busca: cf=[c for c in cf if busca.lower() in c["nome"].lower()]
        if asel!="Todas": cf=[c for c in cf if c["area"]==asel]
        if fsel!="Todos":
            cm={"Verificado":"selo_verificado","Recomendado":"selo_recomendado","Destaque":"selo_destaque","Experiente":"selo_experiente"}
            cf=[c for c in cf if c.get(cm[fsel])=="Sim"]

        st.markdown(f'<p style="font-size:13px;color:#4a6080;font-weight:600;margin-bottom:1rem">{len(cf)} candidato(s)</p>',unsafe_allow_html=True)
        for i,cand in enumerate(cf):
            cor=cor_avatar(cand["nome"]); dsp=cand.get("disponibilidade","Não")
            formacao_res = resumo_formacoes(formacoes_candidato(cand)) or cand.get("instituicao","—")
            bdg='<span class="badge-sim">● Disponível</span>' if dsp=="Sim" else '<span class="badge-nao">● Indisponível</span>'
            foto_card = str(cand.get("foto","") or "").strip()
            avatar_card = f'<img class="cand-photo" src="{html_lib.escape(foto_card)}" alt="Foto de perfil">' if foto_card else f'<div class="avatar" style="background:{cor}">{iniciais(cand["nome"])}</div>'
            cc,cb=st.columns([11,2])
            with cc:
                st.markdown(f"""<div class="cand-card">
                    <div style="display:flex;align-items:center;justify-content:space-between;gap:12px">
                        <div style="display:flex;align-items:center;gap:12px;flex:1">
                            {avatar_card}
                            <div>
                                <p class="cand-name">{cand['nome']}</p>
                                <p class="cand-sub">{formacao_res} · {cand.get('area','—')}</p>
                                <div style="margin-top:4px">{html_selos(cand)}{html_disc(cand)}{html_conc(cand)}</div>
                            </div>
                        </div>
                        <div>{bdg}</div>
                    </div>
                </div>""",unsafe_allow_html=True)
            with cb:
                st.write("")
                if st.button("Ver →",key=f"b{i}"):
                    st.session_state.cand_sel=cand; st.rerun()

# ── PÁGINA: CHAMADAS ──────────────────────────────────────────────────────────
elif pagina == "chamadas":
    todas = aba_chamadas.get_all_records()
    email_param = params.get("email", "")
    if isinstance(email_param, list):
        email_param = email_param[0]
    if email_param and not cand_logado():
        login_candidato(email_param, permitir_sem_senha=True)

    if not cand_logado() and not rec_logado():
        with st.expander("Sou candidato cadastrado — quero me inscrever"):
            em=st.text_input("Seu e-mail cadastrado",key="cl")
            sn=st.text_input("Senha",type="password",key="cl_senha")
            if st.button("Acessar",key="bcl"):
                cf=login_candidato(em, sn, permitir_sem_senha=True)
                if cf: st.success(f"Bem-vindo, {cf['nome'].split()[0]}!"); st.rerun()
                else: st.error("E-mail ou senha inválidos.")

    if cand_logado():
        cand=st.session_state.cand_logado
        st.markdown(f'<div class="info-box">👤 {cand["nome"]}</div>',unsafe_allow_html=True)

    st.markdown("""<div class="hero-card">
        <h1 class="page-title">Seletivos<br><em>Abertos.</em></h1>
        <p class="page-sub">Vagas de cargos de livre nomeação em Tribunais, Ministérios Públicos, Defensorias e Procuradorias</p>
    </div>""",unsafe_allow_html=True)
    st.markdown(f'<div class="disclaimer-box">{DISCLAIMER}</div>',unsafe_allow_html=True)
    st.markdown("<br>",unsafe_allow_html=True)

    c1,c2,c3=st.columns(3)
    with c1: fa=st.selectbox("Área",["Todas"]+AREAS,key="fa")
    with c2: fe=st.selectbox("Estado",["Todos"]+ESTADOS,key="fe")
    with c3: fs=st.selectbox("Status",["Abertas","Todas","Encerradas"],key="fs")

    chf=todas
    if fa!="Todas": chf=[ch for ch in chf if fa.lower() in str(ch.get("area","")).lower()]
    if fe!="Todos": chf=[ch for ch in chf if ch.get("estado")==fe]
    if fs=="Abertas": chf=[ch for ch in chf if ch_aberta(ch)]
    elif fs=="Encerradas": chf=[ch for ch in chf if not ch_aberta(ch)]

    st.markdown(f'<p style="font-size:13px;color:#4a6080;font-weight:600;margin-bottom:1rem">{len(chf)} seletivo(s)</p>',unsafe_allow_html=True)

    for i,ch in enumerate(chf):
        ab=ch_aberta(ch); ins_=inscritos(ch); n=len(ins_)
        sb='<span class="badge-aberta">● Aberta</span>' if ab else '<span class="badge-encerrada">● Encerrada</span>'
        ja=cand_logado() and st.session_state.cand_logado.get("email","") in ins_

        st.markdown(f"""<div class="chamada-card">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:12px">
                <div style="flex:1">
                    <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">
                        {sb}
                        <span style="font-size:11px;color:#4a6080;font-weight:600">📅 {ch.get('prazo','—')}</span>
                        <span style="font-size:11px;color:#4a6080;font-weight:600">👥 {n} inscrito(s)</span>
                    </div>
                    <p style="font-size:16px;font-weight:700;color:#0d1f4e;margin:0 0 4px">{ch.get('titulo','—')}</p>
                    <p style="font-size:13px;color:#4a6080;font-weight:500;margin:0 0 8px">{ch.get('orgao','—')} · {ch.get('municipio','—')}/{ch.get('estado','—')}</p>
                    <div style="display:flex;gap:8px;flex-wrap:wrap">
                        <span style="font-size:11px;font-weight:700;padding:3px 10px;border-radius:99px;background:#e8effe;color:#1a3a8f;border:1px solid #c5d5f5">{ch.get('area','—')}</span>
                        <span style="font-size:11px;font-weight:700;padding:3px 10px;border-radius:99px;background:#f4f7fe;color:#0d1f4e;border:1px solid #d0dcfa">{ch.get('regime','—')}</span>
                        <span style="font-size:11px;font-weight:700;padding:3px 10px;border-radius:99px;background:#e6f4ea;color:#1a7a4a;border:1px solid #b0dfc0">{ch.get('vagas','—')} vaga(s)</span>
                    </div>
                </div>
            </div>
        </div>""",unsafe_allow_html=True)

        cd,ci=st.columns([8,3])
        with cd:
            if st.button("Ver detalhes",key=f"d{i}"):
                st.session_state[f"vd{i}"]=not st.session_state.get(f"vd{i}",False); st.rerun()
        with ci:
            if ab and cand_logado() and not ja:
                if st.button("Inscrever-se →",key=f"i{i}"):
                    st.session_state[f"ci{i}"]=True; st.rerun()
            elif ja: st.markdown('<span class="badge-inscrito">✓ Inscrito</span>',unsafe_allow_html=True)
            elif not cand_logado() and ab:
                if st.button("Entrar para se inscrever", key=f"login_insc_{i}"):
                    ir("inicio")

        if st.session_state.get(f"ci{i}"):
            st.markdown(f'<div class="info-card" style="margin-top:8px"><strong style="color:#0d1f4e">Inscrever em: {ch.get("titulo","")}</strong></div>',unsafe_allow_html=True)
            cons=st.checkbox("Autorizo o compartilhamento do meu perfil com o recrutador deste Seletivo, nos termos da LGPD.",key=f"cs{i}")
            ca,cx=st.columns(2)
            with ca:
                if st.button("Confirmar",key=f"cf{i}"):
                    if not cons: st.error("Autorize o compartilhamento para continuar.")
                    else:
                        ec=st.session_state.cand_logado.get("email",""); ia=inscritos(ch)
                        if ec not in ia:
                            ia.append(ec)
                            tc=aba_chamadas.get_all_records()
                            idx=next((j for j,c in enumerate(tc) if c.get("id")==ch.get("id")),None)
                            if idx is not None: aba_chamadas.update_cell(idx+2,16,", ".join(ia))
                        del st.session_state[f"ci{i}"]
                        st.success("Inscrição realizada!"); st.rerun()
            with cx:
                if st.button("Cancelar",key=f"cx{i}"):
                    del st.session_state[f"ci{i}"]; st.rerun()

        if st.session_state.get(f"vd{i}"):
            with st.expander("Detalhes",expanded=True):
                c1,c2,c3=st.columns(3)
                with c1: st.markdown(f'<div class="metric-box"><p class="metric-label">Remuneração</p><p class="metric-value" style="font-size:13px">{html_texto(ch.get("remuneracao","—"))}</p></div>',unsafe_allow_html=True)
                with c2: st.markdown(f'<div class="metric-box"><p class="metric-label">Regime</p><p class="metric-value" style="font-size:13px">{html_texto(ch.get("regime","—"))}</p></div>',unsafe_allow_html=True)
                with c3: st.markdown(f'<div class="metric-box"><p class="metric-label">Seleção</p><p class="metric-value" style="font-size:13px">{html_texto(ch.get("forma_selecao","—"))}</p></div>',unsafe_allow_html=True)
                if ch.get("requisitos"):
                    st.markdown('<p class="section-label">Requisitos</p>',unsafe_allow_html=True)
                    st.markdown(f'<div class="info-card">{html_texto(ch["requisitos"])}</div>',unsafe_allow_html=True)
                st.markdown(f'<div class="disclaimer-box">{DISCLAIMER}</div>',unsafe_allow_html=True)

# ── PÁGINA: CADASTRO ──────────────────────────────────────────────────────────
elif pagina == "cadastro":
    if "et" not in st.session_state: st.session_state.et=1
    if "campos" not in st.session_state: st.session_state.campos={}
    if "dc" not in st.session_state: st.session_state.dc={}
    et=st.session_state.et
    ts=[("Seus dados\nprofissionais.","Upload do currículo ou preenchimento manual"),("Certificação e\nreferências.","Documentos que geram selos"),("Perfil\ncomportamental.",f"{len(PERGUNTAS_DISC)} perguntas — uso como apoio técnico")]
    tt,ts_=ts[et-1]
    st.markdown(f'<div class="hero-card"><h1 class="page-title">{tt}</h1><p class="page-sub">{ts_}</p></div>',unsafe_allow_html=True)
    st.markdown(barra(et,3),unsafe_allow_html=True)
    st.markdown(f'<p class="step-title">Etapa {et} de 3</p>',unsafe_allow_html=True)

    if et==1:
        pdf=st.file_uploader("Upload do currículo em PDF (opcional)",type="pdf")
        if pdf and not st.session_state.campos:
            with st.spinner("Extraindo..."): st.session_state.campos=extrair_campos(extrair_pdf(pdf))
            st.rerun()
        if pdf is None: st.session_state.campos={}
        campos=st.session_state.campos
        st.markdown('<div class="custom-divider"></div>',unsafe_allow_html=True)
        st.markdown('<div class="highlight-panel">Disponível para seleção</div>', unsafe_allow_html=True)
        disp=st.radio("Disponível para seleção?",["Sim","Não"],horizontal=True)

        c1,c2=st.columns(2)
        with c1: nome=st.text_input("Nome completo *",value=campos.get("nome",""))
        with c2: email=st.text_input("E-mail *",value=campos.get("email",""))
        c1,c2=st.columns(2)
        with c1: senha_cad=st.text_input("Senha de acesso *",type="password",key="senha_candidato_cad")
        with c2: senha_conf=st.text_input("Confirmar senha *",type="password",key="senha_candidato_conf")

        foto = st.file_uploader("Fotografia de perfil (opcional)", type=["jpg","jpeg","png"], key="foto_cadastro_cand")
        if foto:
            st.image(foto, width=120)
            st.caption("Prévia da foto. Para manter a imagem após reiniciar o app, será necessário configurar armazenamento permanente.")
        foto_data = imagem_data_url(foto) if foto else st.session_state.dc.get("foto","")

        st.markdown('<p class="section-label">Formação acadêmica</p>', unsafe_allow_html=True)
        if "cad_qtd_form" not in st.session_state:
            st.session_state.cad_qtd_form = 1
        formacoes = []
        for i in range(st.session_state.cad_qtd_form):
            st.markdown(f'<div class="form-item-title">Formação {i+1}</div>', unsafe_allow_html=True)
            c1,c2=st.columns([2,3])
            with c1: grau=st.selectbox("Formação *",FORMACOES,key=f"cad_grau_{i}")
            with c2: inst=st.text_input("Instituição de ensino *",key=f"cad_inst_{i}")
            st.markdown('<p class="add-hint">Período da formação</p>', unsafe_allow_html=True)
            p1,p2,p3,p4,p5=st.columns([1,1,1,1,1.4])
            with p1: mes_inicio=st.selectbox("Início mês",MESES,key=f"cad_form_mi_{i}")
            with p2: ano_inicio=st.selectbox("Início ano",ANOS_PERIODO,key=f"cad_form_ai_{i}")
            with p3: mes_fim=st.selectbox("Final mês",MESES,key=f"cad_form_mf_{i}")
            with p4: ano_fim=st.selectbox("Final ano",ANOS_PERIODO,key=f"cad_form_af_{i}")
            with p5: st.text_input("Duração",value=texto_duracao(mes_inicio,ano_inicio,mes_fim,ano_fim),disabled=True,key=f"cad_form_dur_{i}")
            periodo=texto_periodo(mes_inicio,ano_inicio,mes_fim,ano_fim)
            formacoes.append({"grau":grau,"instituicao":inst,"periodo":periodo})
        if st.button("+ Adicionar formação", key="add_form_cad"):
            st.session_state.cad_qtd_form = min(8, st.session_state.cad_qtd_form + 1)
            st.rerun()

        st.markdown('<p class="section-label">Experiência profissional</p>', unsafe_allow_html=True)
        if "cad_qtd_exp" not in st.session_state:
            st.session_state.cad_qtd_exp = 1
        experiencias = []
        for i in range(st.session_state.cad_qtd_exp):
            st.markdown(f'<div class="form-item-title">Experiência {i+1}</div>', unsafe_allow_html=True)
            inst_exp_opcoes=["Selecione..."]+INSTITUICOES_INTERESSE
            instituicao_sel=st.selectbox("Instituição",inst_exp_opcoes,key=f"cad_exp_instituicao_{i}")
            instituicao_exp="" if instituicao_sel=="Selecione..." else instituicao_sel
            c_org,c_fun=st.columns(2)
            with c_org:
                orgao=st.text_input("Órgão de atuação",value=campos.get("experiencia_orgaos","") if i==0 else "",key=f"cad_exp_orgao_{i}")
            with c_fun:
                cargo_exp=st.text_input("Cargo/função exercida",placeholder="Ex: Assessor jurídico, estagiário, residente",key=f"cad_exp_cargo_{i}")
            area_exp=st.multiselect("Áreas de atuação",AREAS,key=f"cad_exp_area_{i}")
            c1,c2=st.columns(2)
            with c1: sistemas_exp=st.text_input("Sistemas de trabalho",value=campos.get("sistemas","") if i==0 else "",placeholder="Ex: Eproc, SAJ, SEEU",key=f"cad_exp_sis_{i}")
            with c2: ferramenta_ia=st.text_input("Ferramenta de IA",placeholder="Ex: ChatGPT, Gemini, Copilot",key=f"cad_exp_ia_{i}")
            atribuicoes=st.text_area("Atribuições desenvolvidas",height=80,key=f"cad_exp_atr_{i}")
            st.markdown('<p class="add-hint">Tempo de experiência</p>', unsafe_allow_html=True)
            c1,c2,c3,c4,c5=st.columns([1,1,1,1,1.4])
            with c1: mes_inicio=st.selectbox("Início mês",MESES,key=f"cad_exp_mi_{i}")
            with c2: ano_inicio=st.selectbox("Início ano",ANOS_PERIODO,key=f"cad_exp_ai_{i}")
            with c3: mes_fim=st.selectbox("Final mês",MESES,key=f"cad_exp_mf_{i}")
            with c4: ano_fim=st.selectbox("Final ano",ANOS_PERIODO,key=f"cad_exp_af_{i}")
            with c5: st.text_input("Duração",value=texto_duracao(mes_inicio,ano_inicio,mes_fim,ano_fim),disabled=True,key=f"cad_exp_dur_{i}")
            inicio=f"{mes_inicio}/{ano_inicio}"
            fim=f"{mes_fim}/{ano_fim}"
            c1,c2=st.columns(2)
            with c1: supervisor=st.text_input("Supervisor",key=f"cad_exp_supervisor_{i}")
            with c2: supervisor_email=st.text_input("E-mail de contato",placeholder="nome@orgao.jus.br",key=f"cad_exp_supervisor_email_{i}")
            experiencias.append({"instituicao":instituicao_exp,"orgao":orgao,"cargo":cargo_exp,"supervisor":supervisor,"supervisor_email":supervisor_email,"inicio":inicio,"fim":fim,"area":", ".join(area_exp),"atribuicoes":atribuicoes,"sistemas":sistemas_exp,"ferramenta_ia":ferramenta_ia})
        if st.button("+ Adicionar experiência", key="add_exp_cad"):
            st.session_state.cad_qtd_exp = min(10, st.session_state.cad_qtd_exp + 1)
            st.rerun()

        st.markdown('<div class="custom-divider"></div>',unsafe_allow_html=True)
        st.markdown('<p class="section-label">Outras informações acadêmicas e profissionais</p>', unsafe_allow_html=True)
        st.caption("Use este campo para cursos livres, publicações, produção acadêmica, idiomas, atividades docentes, projetos, voluntariado jurídico, premiações e outras informações que ajudem o recrutador a entender sua trajetória.")
        res=st.text_area("Outras informações",value=campos.get("resumo",""),height=100)

        st.markdown('<p class="section-label">OAB</p>', unsafe_allow_html=True)
        oab=st.radio("OAB ativa?",["Sim","Não"],index=0 if campos.get("oab")=="Sim" else 1,horizontal=True)

        st.markdown('<p class="section-label">Concurso</p>', unsafe_allow_html=True)
        estuda_concurso=st.radio("Estuda para concurso?",["Não","Sim"],horizontal=True)
        conc="Não estou estudando para concurso"
        if estuda_concurso=="Sim":
            c1,c2=st.columns(2)
            with c1:
                concurso_nome=st.text_input("Qual concurso?",placeholder="Ex: Promotor de Justiça (MP Estadual)")
            with c2:
                concurso_tempo=st.text_input("Há quanto tempo estuda?",placeholder="Ex: 1 ano e 6 meses")
            conc=formatar_concurso(concurso_nome, concurso_tempo)

        st.markdown('<p class="section-label">Instituições de interesse para trabalhar</p>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">A indicação das instituições servirá como filtro para envio ou acesso de informações por recrutadores.</div>', unsafe_allow_html=True)
        inst_interesse=st.multiselect("Selecione uma ou mais instituições *",INSTITUICOES_INTERESSE,key="cad_inst_interesse")
        st.markdown('<div class="custom-divider"></div>',unsafe_allow_html=True)
        cons=st.checkbox("Li e aceito a Política de Privacidade e os Termos de Uso. Consinto com o tratamento dos meus dados nos termos da LGPD (Lei nº 13.709/2018).")
        st.markdown("<br>",unsafe_allow_html=True)
        if st.button("Próximo →"):
            formacoes_validas=[f for f in formacoes if f.get("grau") or f.get("instituicao") or f.get("periodo")]
            experiencias_validas=[e for e in experiencias if e.get("instituicao") or e.get("orgao") or e.get("cargo") or e.get("supervisor") or e.get("supervisor_email") or e.get("area") or e.get("atribuicoes") or e.get("sistemas") or e.get("ferramenta_ia")]
            if not nome or not email or not formacoes_validas or not formacoes_validas[0].get("instituicao"): st.error("Preencha nome, e-mail e ao menos uma formação com instituição.")
            elif len(senha_cad) < 6: st.error("Crie uma senha com pelo menos 6 caracteres.")
            elif senha_cad != senha_conf: st.error("As senhas não coincidem.")
            elif not inst_interesse: st.error("Selecione ao menos uma instituição de interesse.")
            elif not cons: st.error("Aceite os Termos para continuar.")
            else:
                anos=anos_experiencias(experiencias_validas)
                st.session_state.dc.update({"nome":nome,"email":email,"senha":hash_senha(senha_cad),"foto":foto_data,"formacao":salvar_lista_json(formacoes_validas),"instituicao":resumo_formacoes(formacoes_validas),"area":", ".join(inst_interesse),"oab":oab,"anos_experiencia":anos,"disponibilidade":disp,"experiencia":salvar_lista_json(experiencias_validas),"sistemas":sistemas_experiencias(experiencias_validas),"pos":"","resumo":res,"concurso":conc})
                st.session_state.et=2; st.rerun()

    elif et==2:
        c1,c2=st.columns(2)
        with c1:
            st.markdown('<p style="font-weight:600;color:#f0c040;margin-bottom:4px">★ Carta de recomendação</p>',unsafe_allow_html=True)
            st.markdown('<p style="font-size:12px;color:#4a6080;font-weight:500;margin-bottom:8px">De um Juiz, Promotor, Defensor ou Procurador ativo</p>',unsafe_allow_html=True)
            carta=st.file_uploader("",type="pdf",key="carta",label_visibility="collapsed")
        with c2:
            st.markdown('<p style="font-weight:600;color:#f0c040;margin-bottom:4px">◆ Avaliação de desempenho</p>',unsafe_allow_html=True)
            st.markdown('<p style="font-size:12px;color:#4a6080;font-weight:500;margin-bottom:8px">Avaliação formal emitida pelo órgão</p>',unsafe_allow_html=True)
            aval=st.file_uploader("",type="pdf",key="aval",label_visibility="collapsed")

        d=st.session_state.dc; sp=[]
        if d.get("oab")=="Sim": sp.append("✓ Verificado")
        if carta: sp.append("★ Recomendado")
        if aval: sp.append("◆ Destaque")
        if d.get("anos_experiencia",0)>=2: sp.append("● Experiente")
        if sp:
            st.markdown('<div class="custom-divider"></div>',unsafe_allow_html=True)
            st.markdown('<p style="font-size:13px;font-weight:600;color:#f0c040">Selos:</p>',unsafe_allow_html=True)
            st.markdown(" ".join([f'<span class="selo selo-verificado">{s}</span>' for s in sp]),unsafe_allow_html=True)
        st.markdown("<br>",unsafe_allow_html=True)
        c1,c2=st.columns(2)
        with c1:
            if st.button("← Voltar"): st.session_state.et=1; st.rerun()
        with c2:
            if st.button("Próximo →"):
                st.session_state.dc.update({"carta":carta is not None,"avaliacao":aval is not None,"email_ref":""})
                st.session_state.et=3; st.rerun()

    elif et==3:
        st.markdown(f'<div class="info-box">{DISC_AVISO}</div>',unsafe_allow_html=True)
        st.markdown('<p style="font-size:14px;color:#4a6080;font-weight:500;margin-bottom:1.5rem">Não há respostas certas ou erradas. Responda pensando na forma como você costuma atuar no trabalho.</p>',unsafe_allow_html=True)
        rd=[]
        for j,(perg,ops) in enumerate(PERGUNTAS_DISC):
            r=st.radio(f"**{j+1}.** {perg}",ops,key=f"dq{j}",index=None)
            rd.append(r)
        st.markdown("<br>",unsafe_allow_html=True)
        c1,c2=st.columns(2)
        with c1:
            if st.button("← Voltar"): st.session_state.et=2; st.rerun()
        with c2:
            if st.button("Cadastrar no JurisBank →"):
                if None in rd: st.error(f"Responda todas as {len(PERGUNTAS_DISC)} perguntas.")
                else:
                    d=st.session_state.dc
                    selos=calc_selos(d["oab"],d["anos_experiencia"],d.get("carta",False),d.get("avaliacao",False))
                    pd_,_,desc=calc_disc(rd)
                    aba_candidatos.append_row([d["nome"],d["email"],d["formacao"],d["instituicao"],d["area"],d["disponibilidade"],d["oab"],d["experiencia"],d["sistemas"],d["pos"],d["resumo"],d.get("email_ref",""),selos["verificado"],selos["recomendado"],selos["destaque"],selos["experiente"],pd_,d.get("concurso","Não estou estudando para concurso"),d.get("senha",""),d.get("foto","")])
                    st.session_state.et=1; st.session_state.campos={}; st.session_state.dc={}
                    st.success("Bem-vindo ao JurisBank!")
                    st.markdown(f'<div class="info-box">Perfil: <strong>{pd_} — {desc}</strong></div>',unsafe_allow_html=True)
                    st.balloons()

# ── PÁGINA: RECRUTADOR ────────────────────────────────────────────────────────
elif pagina == "recrutador":
    if rec_logado():
        rec=st.session_state.rec_logado
        dados=aba_candidatos.get_all_records(); recs=aba_recrutadores.get_all_records()
        idx_r=next((i for i,r in enumerate(recs) if r["email"]==rec["email"]),None)
        ra=recs[idx_r] if idx_r is not None else rec
        favs=[f.strip() for f in str(ra.get("favoritos","")).split(",") if f.strip()]
        anots={}
        for it in str(ra.get("anotacoes","")).split("|"):
            if "::" in it:
                ec,nt=it.split("::",1); anots[ec.strip()]=nt.strip()
        mch=[ch for ch in aba_chamadas.get_all_records() if ch.get("email_recrutador")==rec["email"]]

        st.markdown(f"""<div class="hero-card">
            <h1 class="page-title">Olá, <em>{rec['nome'].split()[0]}!</em></h1>
            <p class="page-sub">{ra.get('nome_orgao',rec.get('orgao',''))} · {rec.get('estado','')}</p>
            <div class="stats-row">
                <div class="stat-pill">{len(dados)} candidatos</div>
                <div class="stat-pill">{len(favs)} favoritos</div>
                <div class="stat-pill">{len(mch)} seletivos</div>
            </div>
        </div>""",unsafe_allow_html=True)

        if "rec_dashboard" not in st.session_state:
            st.session_state.rec_dashboard = "perfil"

        if st.session_state.rec_dashboard == "perfil":
            st.markdown('<p class="section-label">Perfil do Recrutador</p>',unsafe_allow_html=True)
            st.markdown(f"""<div class="profile-section-grid">
                <div class="profile-section-card"><p class="profile-section-title">Órgão</p><div class="profile-list-item">{html_lib.escape(ra.get('nome_orgao',rec.get('orgao','—')))}</div></div>
                <div class="profile-section-card"><p class="profile-section-title">Local</p><div class="profile-list-item">{html_lib.escape(rec.get('estado','—'))} {html_lib.escape(ra.get('municipio',''))}</div></div>
                <div class="profile-section-card"><p class="profile-section-title">Responsável</p><div class="profile-list-item">{html_lib.escape(rec.get('nome','—'))}</div></div>
                <div class="profile-section-card"><p class="profile-section-title">E-mail</p><div class="profile-list-item">{html_lib.escape(rec.get('email','—'))}</div></div>
            </div>""",unsafe_allow_html=True)
            with st.expander("Editar Perfil do Recrutador", expanded=False):
                with st.form("form_editar_recrutador"):
                    c1,c2=st.columns(2)
                    with c1:
                        rec_nome=st.text_input("Nome do responsável",value=ra.get("nome",rec.get("nome","")))
                        rec_estado=st.selectbox("Estado",ESTADOS,index=ESTADOS.index(ra.get("estado",rec.get("estado","SC"))) if ra.get("estado",rec.get("estado","")) in ESTADOS else 0)
                        rec_orgao=st.selectbox("Tipo de órgão",ORGAOS,index=ORGAOS.index(ra.get("orgao","")) if ra.get("orgao","") in ORGAOS else 0)
                    with c2:
                        rec_municipio=st.text_input("Município",value=ra.get("municipio",""))
                        rec_nome_orgao=st.text_input("Nome do órgão",value=ra.get("nome_orgao",rec.get("orgao","")))
                        rec_cargo=st.selectbox("Cargo",CARGOS,index=CARGOS.index(ra.get("cargo","")) if ra.get("cargo","") in CARGOS else 0)
                    rec_areas=st.multiselect("Áreas de interesse do órgão",AREAS,default=lista_selecionada(ra.get("areas",""),AREAS))
                    salvar_rec=st.form_submit_button("Salvar perfil")
                if salvar_rec:
                    if idx_r is None:
                        st.error("Não encontrei seu cadastro de recrutador.")
                    else:
                        linha=idx_r+2
                        aba_recrutadores.update_cell(linha,1,rec_nome)
                        aba_recrutadores.update_cell(linha,4,rec_estado)
                        aba_recrutadores.update_cell(linha,5,rec_municipio)
                        aba_recrutadores.update_cell(linha,6,rec_orgao)
                        aba_recrutadores.update_cell(linha,7,rec_nome_orgao)
                        aba_recrutadores.update_cell(linha,8,rec_cargo)
                        aba_recrutadores.update_cell(linha,9,", ".join(rec_areas))
                        st.session_state.rec_logado=aba_recrutadores.get_all_records()[idx_r]
                        st.session_state.rec_email_logado=st.session_state.rec_logado.get("email","")
                        st.success("Perfil do recrutador atualizado.")
                        st.rerun()
            if st.button("Lançar Novo Seletivo", key="btn_lancar_seletivo_perfil_rec"):
                st.session_state.rec_dashboard = "seletivos"
                st.session_state["criar_ch"] = True
                st.rerun()

        if st.session_state.rec_dashboard == "banco":
            st.markdown('<p class="section-label">Dashboard do Banco de Candidatos</p>',unsafe_allow_html=True)
            st.markdown('<div class="info-box">Use os filtros para montar uma lista curta de candidatos. Favoritos e anotações ficam vinculados à sua conta.</div>',unsafe_allow_html=True)
            c1,c2,c3=st.columns(3)
            with c1: busca=st.text_input("Nome",placeholder="Buscar...")
            with c2:
                ad=["Todas"]+sorted(set(c["area"] for c in dados if c.get("area")))
                asel=st.selectbox("Instituições de Interesse",ad)
            with c3: dsel=st.selectbox("Disponibilidade",["Todos","Disponível","Indisponível"])
            c1,c2,c3,c4,c5,c6=st.columns(6)
            with c1: osel=st.selectbox("OAB",["Todos","Sim","Não"])
            with c2: ssel=st.selectbox("Selo",["Todos","Verificado","Recomendado","Destaque","Experiente"])
            with c3:
                dsc=st.selectbox("DISC",["Todos","D — Dominante","I — Influente","S — Estável","C — Conformidade"])
                if dsc!="Todos": st.markdown(f'<div style="background:#f0f5ff;border:1px solid #c5d5f5;border-radius:8px;padding:8px;font-size:11px;color:#2a4a8a;font-weight:600;margin-top:4px">ℹ {DISC_EXPLICACOES_FILTRO.get(dsc,"")}</div>',unsafe_allow_html=True)
            with c4: csel=st.selectbox("Concurso",["Todos","Concursando","Não concursando"])
            with c5: sisel=st.text_input("Sistema",placeholder="Ex: Eproc")
            with c6: emin=st.number_input("Exp. mín.",min_value=0,max_value=20,value=0)
            fav_filter=st.checkbox("Mostrar apenas favoritos")
            filtros_aplicados = any([
                bool(busca.strip()),
                asel!="Todas",
                dsel!="Todos",
                osel!="Todos",
                ssel!="Todos",
                dsc!="Todos",
                csel!="Todos",
                bool(sisel.strip()),
                bool(emin),
                fav_filter,
            ])

            fi=dados if filtros_aplicados else []
            if busca: fi=[c for c in fi if busca.lower() in c["nome"].lower()]
            if asel!="Todas": fi=[c for c in fi if c.get("area")==asel]
            if dsel!="Todos":
                v="Sim" if dsel=="Disponível" else "Não"; fi=[c for c in fi if c.get("disponibilidade")==v]
            if osel!="Todos": fi=[c for c in fi if c.get("oab")==osel]
            if ssel!="Todos":
                cm={"Verificado":"selo_verificado","Recomendado":"selo_recomendado","Destaque":"selo_destaque","Experiente":"selo_experiente"}
                fi=[c for c in fi if c.get(cm[ssel])=="Sim"]
            if dsc!="Todos": fi=[c for c in fi if c.get("disc")==dsc[0]]
            if csel=="Concursando": fi=[c for c in fi if c.get("concurso") and c.get("concurso")!="Não estou estudando para concurso"]
            elif csel=="Não concursando": fi=[c for c in fi if not c.get("concurso") or c.get("concurso")=="Não estou estudando para concurso"]
            if sisel: fi=[c for c in fi if sisel.lower() in str(c.get("sistemas","")).lower()]
            if emin: fi=[c for c in fi if anos_experiencias(experiencias_candidato(c)) >= int(emin)]
            if fav_filter: fi=[c for c in fi if c.get("email","") in favs]

            if not filtros_aplicados:
                st.markdown('<div class="info-card">Selecione ao menos um filtro para visualizar candidatos compatíveis.</div>',unsafe_allow_html=True)
            st.markdown(f'<p style="font-size:13px;color:#4a6080;font-weight:600;margin:1rem 0 0.5rem">{len(fi)} candidato(s)</p>',unsafe_allow_html=True)
            for i,cand in enumerate(fi):
                cor=cor_avatar(cand["nome"]); dc=cand.get("disponibilidade","Não")
                bdg='<span class="badge-sim">● Disponível</span>' if dc=="Sim" else '<span class="badge-nao">● Indisponível</span>'
                ec=cand.get("email",""); ifav=ec in favs; fi_i="★" if ifav else "☆"
                resumo_c = resumo_card_candidato(cand)
                anos_chip = f'<span class="profile-chip">{resumo_c["anos"]} ano(s)</span>' if resumo_c["experiencia"] != "Experiência não informada" else ""
                foto_card = str(cand.get("foto","") or "").strip()
                avatar_card = f'<img class="cand-photo" src="{html_lib.escape(foto_card)}" alt="Foto de perfil">' if foto_card else f'<div class="avatar" style="background:{cor}">{iniciais(cand["nome"])}</div>'
                with st.container():
                    st.markdown(f"""<div class="cand-card">
                        <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:16px">
                            <div style="display:flex;align-items:flex-start;gap:12px;flex:1;min-width:0">
                                {avatar_card}
                                <div style="min-width:0;flex:1">
                                    <p class="cand-name">{cand['nome']}</p>
                                    <p class="cand-sub"><strong>Formação:</strong> {html_lib.escape(resumo_c['formacao'])}</p>
                                    <p class="cand-sub"><strong>Interesse:</strong> {html_lib.escape(resumo_c['interesse'])}</p>
                                    <p class="cand-sub"><strong>Experiência:</strong> {html_lib.escape(resumo_c['experiencia'])}</p>
                                    <p class="cand-sub"><strong>Sistemas:</strong> {html_lib.escape(resumo_c['sistemas'])}</p>
                                </div>
                            </div>
                            <div style="display:flex;flex-direction:column;gap:6px;align-items:flex-end">
                                {bdg}
                                {anos_chip}
                            </div>
                        </div>
                    </div>""",unsafe_allow_html=True)
                    ca,cb,cc=st.columns([7,1.6,1.6])
                    with cb:
                        if st.button(f"{fi_i} Fav",key=f"fv{i}"):
                            if ifav: favs.remove(ec)
                            else: favs.append(ec)
                            aba_recrutadores.update_cell(idx_r+2,12,", ".join(favs))
                            st.session_state.rec_logado=aba_recrutadores.get_all_records()[idx_r]
                            st.session_state.rec_email_logado=st.session_state.rec_logado.get("email","")
                            st.rerun()
                    with cc:
                        if st.button("Ver →",key=f"rb{i}"):
                            st.session_state.cr=cand; st.rerun()
                if ec in anots: st.markdown(f'<div class="info-card" style="margin-top:-6px;margin-bottom:8px;font-size:12px">📝 {html_texto(anots[ec])}</div>',unsafe_allow_html=True)
                if st.session_state.get("cr")==cand:
                    with st.expander("Perfil completo",expanded=True):
                        c1,c2,c3=st.columns(3)
                        for cl,lb,vl in [(c1,"OAB",cand.get("oab","—")),(c2,"Órgãos",cand.get("experiencia_orgaos","—") or "—"),(c3,"Sistemas",cand.get("sistemas","—") or "—")]:
                            with cl: st.markdown(f'<div class="metric-box"><p class="metric-label">{lb}</p><p class="metric-value" style="font-size:12px">{html_texto(vl)}</p></div>',unsafe_allow_html=True)
                        if cand.get("disc"): st.markdown(render_disc(cand["disc"]),unsafe_allow_html=True)
                        if cand.get("resumo"): st.markdown(f'<div class="info-card" style="margin-top:1rem">{html_texto(cand["resumo"])}</div>',unsafe_allow_html=True)
                        st.markdown(f'<div class="info-card" style="margin-top:0.5rem">✉ {html_texto(cand.get("email","—"))}</div>',unsafe_allow_html=True)
                        na=anots.get(ec,""); nn=st.text_area("",value=na,height=70,key=f"nt{i}",placeholder="Anotação privada...")
                        cs_,cf_=st.columns(2)
                        with cs_:
                            if st.button("Salvar",key=f"sv{i}"):
                                anots[ec]=nn
                                aba_recrutadores.update_cell(idx_r+2,13,"|".join([f"{k}::{v}" for k,v in anots.items()]))
                                st.success("Salvo!"); st.rerun()
                        with cf_:
                            if st.button("Fechar",key=f"fc{i}"):
                                del st.session_state["cr"]; st.rerun()

        if st.session_state.rec_dashboard == "seletivos":
            st.markdown('<p class="section-label">Dashboard de Seletivos</p>',unsafe_allow_html=True)
            st.markdown('<div class="info-box">Crie, acompanhe e encerre Seletivos com critérios objetivos, etapas e histórico interno.</div>',unsafe_allow_html=True)
            ch_col,btn_col=st.columns([8,3])
            with ch_col: st.markdown('<p style="font-size:15px;font-weight:700;color:#1e1e1e">Meus Seletivos</p>',unsafe_allow_html=True)
            with btn_col:
                if st.button("+ Novo Seletivo",key="nch"):
                    st.session_state["criar_ch"]=True; st.rerun()

            if st.session_state.get("criar_ch"):
                with st.expander("Novo Seletivo",expanded=True):
                    st.markdown(f'<div class="disclaimer-box">{DISCLAIMER}</div>',unsafe_allow_html=True)
                    st.markdown("<br>",unsafe_allow_html=True)
                    tch=st.text_input("Título da vaga *",placeholder="Ex: Assessor Jurídico — 3ª Promotoria")
                    c1,c2=st.columns(2)
                    with c1: och=st.text_input("Nome do órgão *",value=ra.get("nome_orgao",""))
                    with c2: toch=st.selectbox("Tipo de órgão *",["Selecione..."]+ORGAOS)
                    c1,c2,c3=st.columns(3)
                    with c1: ach=st.multiselect("Áreas do Seletivo *",AREAS,key="novo_sel_areas")
                    with c2: ech=st.selectbox("Estado *",["Selecione..."]+ESTADOS,index=ESTADOS.index(rec.get("estado","SC"))+1 if rec.get("estado","") in ESTADOS else 0)
                    with c3: mch_=st.text_input("Município *",value=ra.get("municipio",""))
                    rch=st.text_area("Requisitos mínimos *",height=80,placeholder="Ex: Bacharelado em Direito, experiência em gabinete, domínio de Eproc/SAJ, disponibilidade presencial.")
                    c1,c2,c3=st.columns(3)
                    with c1: remch=st.text_input("Remuneração *",placeholder="Ex: R$ 4.500,00")
                    with c2: regch=st.selectbox("Regime *",["Selecione..."]+REGIMES)
                    with c3: vch=st.number_input("Vagas *",min_value=1,max_value=20,value=1)
                    c1,c2=st.columns(2)
                    with c1: fsch=st.selectbox("Forma de seleção *",["Selecione..."]+FORMAS_SELECAO)
                    with c2: prch=st.date_input("Prazo *",min_value=date.today())
                    st.markdown('<div class="custom-divider"></div>',unsafe_allow_html=True)
                    st.markdown('<p class="section-label">Etapas do Seletivo</p>',unsafe_allow_html=True)
                    etapas=st.multiselect(
                        "Etapas previstas",
                        ["Triagem por currículo","Entrevista estruturada","Teste de escrita","Prova prática/minuta","Checagem de referências"],
                        default=["Triagem por currículo"]
                    )
                    organizacao_etapas=st.text_area("Como pretende organizar as etapas?",height=100,placeholder="Ex: primeiro análise curricular; depois entrevista com lista curta; se necessário, teste de escrita com prazo de 2 horas.")
                    comunicacao=st.text_area("Mensagem aos candidatos compatíveis",height=70,placeholder="Texto breve para orientar candidatos sobre o Seletivo e as próximas etapas.")
                    st.markdown("<br>",unsafe_allow_html=True)
                    c1,c2=st.columns(2)
                    with c1:
                        if st.button("Cancelar",key="cch"): del st.session_state["criar_ch"]; st.rerun()
                    with c2:
                        if st.button("Publicar →",key="pch"):
                            ok=all([tch,och,toch!="Selecione...",ach,ech!="Selecione...",mch_,rch,remch,regch!="Selecione...",fsch!="Selecione..."])
                            if not ok: st.error("Preencha todos os campos.")
                            else:
                                plano_seletivo = [
                                    rch.strip(),
                                    "",
                                    "Etapas: " + (", ".join(etapas) if etapas else "Não informado"),
                                    "Organização das etapas: " + (organizacao_etapas.strip() or "Não informado"),
                                    "Mensagem aos candidatos: " + (comunicacao.strip() or "Não informado"),
                                ]
                                aba_chamadas.append_row([gerar_id(),tch,och,toch,", ".join(ach),ech,mch_,"\n".join(plano_seletivo),remch,regch,fsch,str(vch),prch.strftime("%d/%m/%Y"),"aberto",rec["email"],"",datetime.now().strftime("%d/%m/%Y")])
                                del st.session_state["criar_ch"]; st.success("Seletivo publicado!"); st.rerun()

            if not mch: st.info("Nenhum Seletivo publicado ainda.")
            else:
                for i,ch in enumerate(mch):
                    ab=ch_aberta(ch); ins_=inscritos(ch); n=len(ins_)
                    sb='<span class="badge-aberta">● Aberta</span>' if ab else '<span class="badge-encerrada">● Encerrada</span>'
                    st.markdown(f"""<div class="chamada-card">
                        <div style="display:flex;justify-content:space-between;align-items:center">
                            <div>
                                <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px">{sb}<span style="font-size:11px;color:#4a6080;font-weight:600">📅 {ch.get('prazo','—')}</span></div>
                                <p style="font-size:15px;font-weight:700;color:#0d1f4e;margin:0 0 2px">{ch.get('titulo','—')}</p>
                                <p style="font-size:12px;color:#4a6080;font-weight:500;margin:0">{ch.get('municipio','—')}/{ch.get('estado','—')} · {ch.get('area','—')}</p>
                            </div>
                            <div style="text-align:right">
                                <p style="font-size:26px;font-weight:800;color:#f0c040;margin:0">{n}</p>
                                <p style="font-size:11px;color:#4a6080;font-weight:600;margin:0">inscrito(s)</p>
                            </div>
                        </div>
                    </div>""",unsafe_allow_html=True)
                    cv,ced,ce=st.columns([6,2,2])
                    with cv:
                        if st.button("Ver inscritos",key=f"vi{i}"):
                            st.session_state[f"vi{i}"]=not st.session_state.get(f"vi{i}",False); st.rerun()
                    with ced:
                        if st.button("Editar",key=f"edch{i}"):
                            st.session_state[f"edch{i}"]=not st.session_state.get(f"edch{i}",False); st.rerun()
                    with ce:
                        if ab:
                            if st.button("Encerrar",key=f"enc{i}"):
                                tc=aba_chamadas.get_all_records()
                                idx=next((j for j,c in enumerate(tc) if c.get("id")==ch.get("id")),None)
                                if idx is not None: aba_chamadas.update_cell(idx+2,14,"encerrado")
                                st.success("Encerrada."); st.rerun()
                    if st.session_state.get(f"edch{i}"):
                        with st.expander("Editar Seletivo",expanded=True):
                            with st.form(f"form_editar_chamada_{i}"):
                                etitulo=st.text_input("Título",value=ch.get("titulo",""),key=f"edit_ch_tit_{i}")
                                earea=st.multiselect("Áreas",AREAS,default=[a.strip() for a in str(ch.get("area","")).split(",") if a.strip() in AREAS],key=f"edit_ch_area_{i}")
                                ereq=st.text_area("Requisitos e organização das etapas",value=ch.get("requisitos",""),height=130,key=f"edit_ch_req_{i}")
                                c1,c2,c3=st.columns(3)
                                with c1: erem=st.text_input("Remuneração",value=ch.get("remuneracao",""),key=f"edit_ch_rem_{i}")
                                with c2: ereg=st.selectbox("Regime",REGIMES,index=REGIMES.index(ch.get("regime","Presencial")) if ch.get("regime","") in REGIMES else 0,key=f"edit_ch_reg_{i}")
                                with c3: eforma=st.selectbox("Forma de seleção",FORMAS_SELECAO,index=FORMAS_SELECAO.index(ch.get("forma_selecao","Análise curricular")) if ch.get("forma_selecao","") in FORMAS_SELECAO else 0,key=f"edit_ch_forma_{i}")
                                salvar_ed=st.form_submit_button("Salvar alterações")
                            if salvar_ed:
                                tc=aba_chamadas.get_all_records()
                                idx=next((j for j,c in enumerate(tc) if c.get("id")==ch.get("id")),None)
                                if idx is None:
                                    st.error("Não encontrei este Seletivo na planilha.")
                                else:
                                    linha=idx+2
                                    aba_chamadas.update_cell(linha,2,etitulo)
                                    aba_chamadas.update_cell(linha,5,", ".join(earea))
                                    aba_chamadas.update_cell(linha,8,ereq)
                                    aba_chamadas.update_cell(linha,9,erem)
                                    aba_chamadas.update_cell(linha,10,ereg)
                                    aba_chamadas.update_cell(linha,11,eforma)
                                    st.success("Seletivo atualizado.")
                                    st.rerun()
                    if st.session_state.get(f"vi{i}"):
                        with st.expander("Painel de inscritos",expanded=True):
                            if not ins_: st.info("Nenhum inscrito.")
                            else:
                                tc=aba_candidatos.get_all_records()
                                id_=[c for c in tc if c.get("email","") in ins_]
                                c1,c2,c3=st.columns(3)
                                with c1: st.markdown(f'<div class="metric-box"><p class="metric-label">Total</p><p class="metric-value">{len(id_)}</p></div>',unsafe_allow_html=True)
                                with c2: st.markdown(f'<div class="metric-box"><p class="metric-label">Com OAB</p><p class="metric-value">{sum(1 for c in id_ if c.get("oab")=="Sim")}</p></div>',unsafe_allow_html=True)
                                with c3: st.markdown(f'<div class="metric-box"><p class="metric-label">Disponíveis</p><p class="metric-value">{sum(1 for c in id_ if c.get("disponibilidade")=="Sim")}</p></div>',unsafe_allow_html=True)
                                dc={}
                                for c in id_:
                                    d=c.get("disc","")
                                    if d: dc[d]=dc.get(d,0)+1
                                if dc:
                                    st.markdown('<p class="section-label">DISC</p>',unsafe_allow_html=True)
                                    cols=st.columns(4)
                                    for di,l in enumerate(["D","I","S","C"]):
                                        with cols[di]: st.markdown(f'<div class="metric-box" style="background:{DISC_CORES_BADGE.get(l,"rgba(255,255,255,0.05)")}"><p class="metric-label" style="color:{DISC_TEXTO_BADGE.get(l,"#fff")}">{DISC_LABEL.get(l,"")}</p><p class="metric-value" style="color:{DISC_TEXTO_BADGE.get(l,"#fff")}">{dc.get(l,0)}</p></div>',unsafe_allow_html=True)
                                st.markdown('<p class="section-label">Perfis</p>',unsafe_allow_html=True)
                                for cand in id_:
                                    cor=cor_avatar(cand["nome"])
                                    st.markdown(f"""<div class="cand-card" style="margin-bottom:8px">
                                        <div style="display:flex;align-items:center;gap:12px">
                                            <div class="avatar" style="background:{cor}">{iniciais(cand['nome'])}</div>
                                            <div style="flex:1">
                                                <p class="cand-name">{cand['nome']}</p>
                                                <p class="cand-sub">{cand.get('formacao','—')} · {cand.get('area','—')}</p>
                                                <div style="margin-top:4px">{html_selos(cand)}{html_disc(cand)}</div>
                                            </div>
                                            <div style="font-size:12px;color:#4a6080;font-weight:500">✉ {cand.get('email','—')}</div>
                                        </div>
                                    </div>""",unsafe_allow_html=True)

    elif "cad_rec" not in st.session_state:
        st.markdown("""<div class="hero-card">
            <h1 class="page-title">Área do<br><em>Recrutador.</em></h1>
            <p class="page-sub">Acesse o banco de talentos jurídicos certificados</p>
        </div>""",unsafe_allow_html=True)
        tabs=st.tabs(["Entrar","Criar conta"])
        with tabs[0]:
            st.markdown('<p style="font-size:16px;font-weight:700;color:#0d1f4e;margin:1rem 0">Acesse sua conta</p>',unsafe_allow_html=True)
            el=st.text_input("E-mail institucional",key="le")
            sl=st.text_input("Senha",type="password",key="ls")
            if st.button("Entrar →",key="bl"):
                if el and sl:
                    recs_=aba_recrutadores.get_all_records(); sh=hash_senha(sl)
                    enc=next((r for r in recs_ if r["email"]==el and r["senha"]==sh and r["status"]=="ativo"),None)
                    if enc:
                        st.session_state.rec_logado=enc
                        st.session_state.rec_email_logado=enc.get("email","")
                        st.rerun()
                    else: st.error("E-mail ou senha incorretos, ou conta ainda não aprovada.")
                else: st.error("Preencha e-mail e senha.")
        with tabs[1]:
            st.markdown('<p style="font-size:15px;font-weight:700;color:#0d1f4e;margin:1rem 0 0.5rem">Criar conta</p>',unsafe_allow_html=True)
            st.markdown('<p style="font-size:13px;color:#4a6080;font-weight:500;margin-bottom:1rem">4 etapas. Ativação após validação institucional.</p>',unsafe_allow_html=True)
            if st.button("Começar →",key="bc"):
                st.session_state.cad_rec={"etapa":1}; st.rerun()
    else:
        et=st.session_state.cad_rec.get("etapa",1)
        st.markdown(barra(et,4),unsafe_allow_html=True)
        if et==1:
            st.markdown('<p class="step-title">Etapa 1 de 4</p>',unsafe_allow_html=True)
            st.markdown('<p class="step-desc">Onde você atua?</p>',unsafe_allow_html=True)
            est=st.selectbox("Estado *",["Selecione..."]+ESTADOS)
            mun=st.text_input("Município *",placeholder="Ex: Florianópolis")
            st.markdown("<br>",unsafe_allow_html=True)
            if st.button("Próximo →"):
                if est=="Selecione..." or not mun: st.error("Preencha todos os campos.")
                else:
                    st.session_state.cad_rec["estado"]=est; st.session_state.cad_rec["municipio"]=mun
                    st.session_state.cad_rec["etapa"]=2; st.rerun()
        elif et==2:
            st.markdown('<p class="step-title">Etapa 2 de 4</p>',unsafe_allow_html=True)
            st.markdown('<p class="step-desc">Qual é o seu órgão?</p>',unsafe_allow_html=True)
            org=st.selectbox("Tipo de órgão *",["Selecione..."]+ORGAOS)
            nom=st.text_input("Nome do órgão *",placeholder="Ex: MPSC — 3ª Promotoria")
            st.markdown("<br>",unsafe_allow_html=True)
            c1,c2=st.columns(2)
            with c1:
                if st.button("← Voltar"): st.session_state.cad_rec["etapa"]=1; st.rerun()
            with c2:
                if st.button("Próximo →"):
                    if org=="Selecione..." or not nom: st.error("Preencha todos os campos.")
                    else:
                        st.session_state.cad_rec["orgao"]=org; st.session_state.cad_rec["nome_orgao"]=nom
                        st.session_state.cad_rec["etapa"]=3; st.rerun()
        elif et==3:
            st.markdown('<p class="step-title">Etapa 3 de 4</p>',unsafe_allow_html=True)
            st.markdown('<p class="step-desc">Seu perfil</p>',unsafe_allow_html=True)
            car=st.selectbox("Cargo *",["Selecione..."]+CARGOS)
            ars=st.multiselect("Áreas *",AREAS)
            st.markdown("<br>",unsafe_allow_html=True)
            c1,c2=st.columns(2)
            with c1:
                if st.button("← Voltar"): st.session_state.cad_rec["etapa"]=2; st.rerun()
            with c2:
                if st.button("Próximo →"):
                    if car=="Selecione..." or not ars: st.error("Preencha todos os campos.")
                    else:
                        st.session_state.cad_rec["cargo"]=car; st.session_state.cad_rec["areas"]=", ".join(ars)
                        st.session_state.cad_rec["etapa"]=4; st.rerun()
        elif et==4:
            st.markdown('<p class="step-title">Etapa 4 de 4</p>',unsafe_allow_html=True)
            st.markdown('<p class="step-desc">Crie seu acesso</p>',unsafe_allow_html=True)
            nr=st.text_input("Nome completo *")
            er=st.text_input("E-mail institucional *",placeholder="nome@mpsc.mp.br")
            dv=["mpsc.mp.br","tjsc.jus.br","sc.def.br","pge.sc.gov.br","trf4.jus.br","jfsc.jus.br","mpf.mp.br","agu.gov.br","pgfn.gov.br"]
            if er and "@" in er:
                if er.split("@")[-1] in dv: st.markdown('<div class="info-box">✓ E-mail institucional reconhecido.</div>',unsafe_allow_html=True)
                else: st.warning("Domínio não reconhecido. Validação manual.")
            sr=st.text_input("Senha *",type="password"); sc=st.text_input("Confirmar senha *",type="password")
            st.markdown('<div class="custom-divider"></div>',unsafe_allow_html=True)
            cr=st.checkbox("Li e aceito a Política de Privacidade e os Termos de Uso. Comprometo-me a usar os dados apenas para fins de seleção, nos termos da LGPD.")
            st.markdown("<br>",unsafe_allow_html=True)
            c1,c2=st.columns(2)
            with c1:
                if st.button("← Voltar"): st.session_state.cad_rec["etapa"]=3; st.rerun()
            with c2:
                if st.button("Finalizar →"):
                    if not nr or not er or not sr: st.error("Preencha todos os campos.")
                    elif sr!=sc: st.error("Senhas não coincidem.")
                    elif len(sr)<6: st.error("Mínimo 6 caracteres.")
                    elif not cr: st.error("Aceite os Termos para continuar.")
                    else:
                        dr=st.session_state.cad_rec
                        aba_recrutadores.append_row([nr,er,hash_senha(sr),dr["estado"],dr["municipio"],dr["orgao"],dr["nome_orgao"],dr["cargo"],dr["areas"],"pendente",datetime.now().strftime("%d/%m/%Y %H:%M")])
                        del st.session_state.cad_rec
                        st.success("Cadastro realizado! Aguarde a ativação."); st.balloons()


# ── PÁGINA: AVALIAÇÃO DO RECOMENDADOR ────────────────────────────────────────
elif pagina == "recomendar":
    token_url = st.query_params.get("token", "")
    if isinstance(token_url, list): token_url = token_url[0]

    if not token_url:
        st.markdown('''<div class="hero-card">
            <h1 class="page-title">Link<br><em>inválido.</em></h1>
            <p class="page-sub">Este link de avaliação não é válido ou já foi utilizado.</p>
        </div>''', unsafe_allow_html=True)
    else:
        # Buscar token na planilha
        recs_recom = aba_recomendacoes.get_all_records()
        rec_recom = next((r for r in recs_recom if r.get("token") == token_url), None)

        if not rec_recom:
            st.markdown('''<div class="hero-card">
                <h1 class="page-title">Link<br><em>não encontrado.</em></h1>
                <p class="page-sub">Este link de avaliação não existe ou expirou.</p>
            </div>''', unsafe_allow_html=True)
        elif rec_recom.get("status") == "concluido":
            st.markdown('''<div class="hero-card">
                <h1 class="page-title">Avaliação<br><em>já realizada.</em></h1>
                <p class="page-sub">Esta avaliação já foi preenchida. Obrigado pela sua contribuição.</p>
            </div>''', unsafe_allow_html=True)
        else:
            # Buscar dados do candidato
            todos_cands = aba_candidatos.get_all_records()
            cand_recom = next((c for c in todos_cands if c.get("email") == rec_recom.get("email_candidato")), None)
            nome_cand = cand_recom["nome"] if cand_recom else rec_recom.get("email_candidato", "candidato")

            st.markdown(f'''<div class="hero-card">
                <h1 class="page-title">Avaliação de<br><em>Recomendação.</em></h1>
                <p class="page-sub">Você foi indicado como recomendador de <strong style="color:#f0c040">{nome_cand}</strong> no JurisBank. Preencha a avaliação abaixo.</p>
            </div>''', unsafe_allow_html=True)

            st.markdown(f'''<div class="disclaimer-box">
                Esta avaliação é de caráter profissional e será exibida para recrutadores de Tribunais, Ministérios Públicos, Defensorias e Procuradorias. Ao enviar, você confirma que as informações prestadas são verdadeiras.
            </div>''', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

            with st.form("form_recomendacao"):
                st.markdown('<p style="font-size:15px;font-weight:700;color:#0d1f4e;margin-bottom:1rem">Sobre o candidato</p>', unsafe_allow_html=True)

                tempo = st.selectbox("Há quanto tempo conhece o candidato? *", [
                    "Selecione...", "Menos de 1 ano", "1 a 2 anos", "2 a 5 anos", "Mais de 5 anos"
                ])
                contexto = st.selectbox("Em qual contexto profissional? *", [
                    "Selecione...", "Assessoria direta no meu gabinete",
                    "Atuação em outro órgão público", "Trabalho conjunto em projeto ou força-tarefa",
                    "Docência ou orientação acadêmica", "Outro"
                ])

                st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
                st.markdown('<p style="font-size:15px;font-weight:700;color:#0d1f4e;margin-bottom:1rem">Avaliação profissional</p>', unsafe_allow_html=True)

                pontos_fortes = st.text_area(
                    "Quais os principais pontos fortes do candidato? *",
                    height=100,
                    placeholder="Descreva as qualidades profissionais que mais se destacaram..."
                )
                adequacao = st.selectbox("O candidato é adequado para assessoria em órgão público? *", [
                    "Selecione...", "Sim, fortemente recomendo",
                    "Sim, com algumas ressalvas", "Neutro", "Não recomendo"
                ])
                nota = st.select_slider(
                    "Nota geral (1 a 5) *",
                    options=[1, 2, 3, 4, 5],
                    value=4
                )
                comentarios = st.text_area(
                    "Comentários adicionais (opcional)",
                    height=80,
                    placeholder="Observações complementares sobre o candidato..."
                )

                st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
                confirmacao = st.checkbox(
                    "Confirmo que sou membro ativo de órgão do sistema de justiça e que as informações prestadas são verdadeiras, assumindo responsabilidade por seu conteúdo."
                )

                submitted = st.form_submit_button("Enviar avaliação →")

                if submitted:
                    if tempo == "Selecione..." or contexto == "Selecione..." or adequacao == "Selecione..." or not pontos_fortes:
                        st.error("Preencha todos os campos obrigatórios.")
                    elif not confirmacao:
                        st.error("Confirme sua responsabilidade sobre as informações prestadas.")
                    else:
                        resposta = f"Tempo: {tempo} | Contexto: {contexto} | Adequação: {adequacao} | Nota: {nota}/5 | Pontos fortes: {pontos_fortes}"
                        # Atualizar planilha de recomendações
                        idx_recom = next((i for i, r in enumerate(recs_recom) if r.get("token") == token_url), None)
                        if idx_recom is not None:
                            aba_recomendacoes.update_cell(idx_recom + 2, 4, "concluido")
                            aba_recomendacoes.update_cell(idx_recom + 2, 6, resposta)
                            aba_recomendacoes.update_cell(idx_recom + 2, 7, comentarios)
                        # Ativar selo recomendado no candidato
                        if cand_recom:
                            todos_cands2 = aba_candidatos.get_all_records()
                            idx_cand = next((i for i, c in enumerate(todos_cands2) if c.get("email") == rec_recom.get("email_candidato")), None)
                            if idx_cand is not None:
                                aba_candidatos.update_cell(idx_cand + 2, 14, "Sim")  # coluna N = selo_recomendado
                        st.success("Avaliação enviada com sucesso! O selo ★ Recomendado foi ativado no perfil do candidato.")
                        st.balloons()

# ── PÁGINAS LEGAIS ────────────────────────────────────────────────────────────
elif pagina in ["privacidade","termos"]:
    ip=pagina=="privacidade"
    st.markdown(f"""<div class="hero-card">
        <h1 class="page-title">{'Política de<br><em>Privacidade.</em>' if ip else 'Termos<br><em>de Uso.</em>'}</h1>
        <p class="page-sub">Versão 1.0</p>
    </div>""",unsafe_allow_html=True)
    if ip:
        secs=[
            ("1. Controlador",[("p","Operado por [RAZÃO SOCIAL A PREENCHER], CNPJ [A PREENCHER]. DPO: [E-MAIL A PREENCHER]")]),
            ("2. Dados Coletados",[("l",["Nome, e-mail, formação, OAB","Histórico em órgãos públicos","Sistemas jurídicos, perfil DISC","Documentos de referência (quando fornecidos)","Fotografia de perfil quando enviada","Senhas de acesso armazenadas em hash SHA-256"])]),
            ("3. Finalidade",[("l",["Gestão de perfis e selos","Viabilizar busca por recrutadores aprovados","Gestão de inscrições em Seletivos","Melhoria dos serviços"])]),
            ("4. Base Legal",[("l",["Consentimento (Art. 7º, I LGPD)","Legítimo interesse (Art. 7º, IX LGPD)"])]),
            ("5. Direitos",[("l",["Acesso, correção e eliminação","Portabilidade","Revogação do consentimento"]),("p","Contato: [E-MAIL DO DPO A PREENCHER]")]),
        ]
    else:
        secs=[
            ("1. Aceitação",[("p","Ao usar o JurisBank você concorda com estes Termos e com a Política de Privacidade.")]),
            ("2. Seletivos",[("p","A publicação de um Seletivo não configura processo seletivo vinculante ou concurso público. O uso do ius indicandum é de responsabilidade exclusiva do recrutador.")]),
            ("3. Impessoalidade",[("l",["Princípio da impessoalidade (art. 37, CF/88)","Vedação ao nepotismo (SV nº 13 do STF)","Resolução CNJ nº 07/2005"])]),
            ("4. Responsabilidades",[("p","O JurisBank não garante contratações e não se responsabiliza por decisões dos recrutadores.")]),
            ("5. Foro",[("p","Comarca de [MUNICÍPIO A PREENCHER], Estado de [ESTADO A PREENCHER].")]),
        ]
    for ts,cont in secs:
        st.markdown(f'<div class="doc-sub">{ts}</div>',unsafe_allow_html=True)
        for tp,tx in cont:
            if tp=="p": st.markdown(f'<p class="doc-body">{tx}</p>',unsafe_allow_html=True)
            elif tp=="l":
                for it in tx: st.markdown(f'<p class="doc-item">• {it}</p>',unsafe_allow_html=True)
        st.markdown('<div class="custom-divider"></div>',unsafe_allow_html=True)
    st.markdown(f'<p style="font-size:12px;color:#4a6080;font-weight:500;text-align:center">JurisBank — Versão 1.0 — {datetime.now().strftime("%d/%m/%Y")}</p>',unsafe_allow_html=True)

