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
    page_title="IndicaJur",
    page_icon="IJ",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;0,700;1,500;1,600&family=Inter:wght@300;400;500;600;700;800&display=swap');
:root { --ij-navy:#071D49; --ij-gold:#C49A2C; --ij-gold-soft:#E7D28A; --ij-off:#FBFAF7; --ij-cream:#F4F0E6; --ij-border:#D9D2C3; --ij-text:#071D49; --ij-muted:#5E6675; --ij-white:#FFFFFF; }

html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #071D49; }

[data-testid="stToolbar"] { display: none !important; }
[data-testid="stSidebarCollapsedControl"] { display: none !important; }
header[data-testid="stHeader"] { display: none !important; }
#MainMenu { display: none !important; }
[data-testid="stSidebar"] { display: none !important; }

[data-testid="stAppViewContainer"] {
    background: #FBFAF7;
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
    color: #071D49;
}
[data-testid="stMarkdownContainer"] strong {
    color: #071D49;
    font-weight: 700;
}
[data-testid="stCaptionContainer"],
.stCaptionContainer {
    color: #5E6675 !important;
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
    background: #071D49;
}
.topbar-logo, .topbar-logo *, .topbar a, .topbar a * { text-decoration: none !important; }
.topbar-logo { display: flex; align-items: center; gap: 12px; min-width: 190px; }
.topbar-logo-icon {
    width: 38px; height: 38px;
    background: linear-gradient(135deg,#C49A2C,#C49A2C);
    border: 1px solid rgba(255,255,255,0.18);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    color: #071D49 !important;
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
    color: #C49A2C !important;
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
.topbar-nav a.active { color: #C49A2C; border-color: rgba(200,150,12,0.4); background: rgba(200,150,12,0.12); }
.topbar-nav a.btn-rec {
    background: linear-gradient(135deg,#C49A2C,#C49A2C);
    color: #071D49; border: none; font-weight: 700;
}
.topbar-nav a.btn-rec:hover { opacity: 0.9; }

/* ── Cards ── */
.hero-card { background: #ffffff; border: 1.5px solid #D9D2C3; border-radius: 20px; padding: 2rem 2.5rem; margin-bottom: 1.5rem; box-shadow: 0 8px 28px rgba(13,31,78,0.06); }
.profile-shell { background: #ffffff; border: 1.5px solid #D9D2C3; border-radius: 16px; padding: 18px 22px; margin: 0 0 1rem; box-shadow: 0 10px 26px rgba(13,31,78,0.06); }
.profile-shell-title { font-size: 13px; font-weight: 900; color: #071D49; text-transform: uppercase; letter-spacing: .12em; margin: 0 0 14px; }
.profile-panel { background: #ffffff; border: 1.5px solid #D9D2C3; border-radius: 22px; padding: 34px 38px; margin: 0 0 1.5rem; box-shadow: 0 12px 30px rgba(13,31,78,0.08); width: 100%; }
.profile-head { display: flex; align-items: center; gap: 18px; margin-bottom: 20px; }
.profile-avatar { width: 68px; height: 68px; border-radius: 14px; background: #247b56; color: #ffffff; display: flex; align-items: center; justify-content: center; font-size: 20px; font-weight: 900; flex-shrink: 0; }
.profile-photo { width: 68px; height: 68px; border-radius: 14px; object-fit: cover; flex-shrink: 0; border: 1px solid #D9D2C3; }
.profile-name-main { font-size: 24px; font-weight: 900; color: #071D49; margin: 0 0 2px; }
.profile-sub-main { font-size: 15px; font-weight: 700; color: #5E6675; margin: 0; line-height: 1.35; }
.profile-chip-row { display: flex; gap: 8px; flex-wrap: wrap; margin: 8px 0 16px; }
.profile-chip { display: inline-flex; align-items: center; min-height: 23px; padding: 0 10px; border-radius: 999px; font-size: 11px; font-weight: 800; border: 1px solid #D9D2C3; background: #F4F0E6; color: #071D49; }
.profile-chip-green { background: #e6f4ea; color: #15803d; border-color: #b0dfc0; }
.profile-chip-gold { background: #fff8e6; color: #b45309; border-color: #C49A2C; }
.profile-disc-card { background: #f7fbf9; border: 1px solid #d8efe4; border-radius: 13px; padding: 16px 18px; display: flex; gap: 14px; align-items: center; margin-bottom: 14px; }
.profile-disc-letter { color: #15803d; font-size: 24px; font-weight: 900; min-width: 26px; }
.profile-disc-text { color: #5E6675; font-size: 13px; font-weight: 600; line-height: 1.45; margin: 0; }
.profile-concurso { background: #fff8e6; border: 1.5px solid #C49A2C; color: #b45309; border-radius: 12px; padding: 12px 14px; font-size: 13px; font-weight: 800; margin: 0 0 14px; }
.profile-detail-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin: 0 0 14px; }
.profile-detail { background: #f3f7ff; border: 1px solid #D9D2C3; border-radius: 10px; padding: 14px 16px; font-size: 13px; color: #071D49; line-height: 1.6; }
.profile-foot { display: flex; justify-content: space-between; align-items: center; gap: 12px; flex-wrap: wrap; margin-top: 16px; }
.profile-status { display: inline-flex; align-items: center; min-height: 27px; padding: 0 12px; border-radius: 999px; border: 1px solid #b0dfc0; background: #e6f4ea; color: #15803d; font-size: 12px; font-weight: 900; }
.profile-status-off { border-color: #f0c8a0; background: #fff3e8; color: #c05a1a; }
.profile-actions { display: flex; gap: 10px; flex-wrap: wrap; }
.profile-action { display: inline-flex; align-items: center; justify-content: center; min-height: 34px; padding: 0 16px; border-radius: 10px; background: #fff8e6; border: 1.5px solid #C49A2C; color: #C49A2C !important; text-decoration: none !important; font-size: 12px; font-weight: 900; }
.profile-action:hover { background: #C49A2C; color: #071D49 !important; }
.rec-action-row { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; margin: 18px 0 4px; max-width: 720px; }
.rec-action-card { display: flex; flex-direction: column; gap: 4px; min-height: 78px; justify-content: center; padding: 16px 18px; border-radius: 14px; background: #ffffff; border: 1.5px solid #D9D2C3; color: #071D49 !important; text-decoration: none !important; box-shadow: 0 12px 28px rgba(7,29,73,0.06); transition: all .18s ease; }
.rec-action-card.primary { background: #071D49; border-color: #071D49; color: #ffffff !important; }
.rec-action-card:hover { transform: translateY(-1px); border-color: #C49A2C; box-shadow: 0 16px 34px rgba(7,29,73,0.1); }
.rec-action-title { font-size: 14px; font-weight: 900; color: inherit !important; }
.rec-action-text { font-size: 12px; font-weight: 600; color: inherit !important; opacity: .72; line-height: 1.35; }
.edit-hero { background: #ffffff; border: 1.5px solid #D9D2C3; border-radius: 16px; padding: 1.35rem 1.6rem; margin-bottom: 1.2rem; box-shadow: 0 8px 24px rgba(13,31,78,0.05); }
.edit-title { font-family: 'Cormorant Garamond',serif; font-size: 32px; font-weight: 700; color: #071D49; margin: 0 0 4px; line-height: 1.05; }
.edit-title em { font-style: normal; color: #C49A2C; }
.edit-sub { font-size: 13px; color: #5E6675; margin: 0; font-weight: 600; }
@media (max-width: 760px) { .profile-panel { max-width: none; padding: 22px; } .profile-detail-grid, .rec-action-row { grid-template-columns: 1fr; } }
@media (max-width: 760px) { .topbar { padding: 0.9rem 1rem; } .topbar-logo { min-width: 160px; } .topbar-nav { width: 100%; justify-content: flex-start; } }
.page-title { font-family: 'Cormorant Garamond',serif; font-size: clamp(32px,4vw,50px); font-weight: 700; color: #071D49; margin: 0 0 8px; letter-spacing: -1px; line-height: 1.05; }
.page-title em { font-style: normal; background: linear-gradient(135deg,#C49A2C,#C49A2C); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
.page-sub { font-size: 15px; color: #5E6675; margin: 0; font-weight: 600; }
.stats-row { display: flex; gap: 12px; margin-top: 1.5rem; flex-wrap: wrap; }
.stat-pill { background: #F4F0E6; border-radius: 99px; padding: 7px 16px; font-size: 13px; font-weight: 700; color: #071D49; border: 1px solid #D9D2C3; }
.cand-card { background: #ffffff; border: 1.5px solid #D9D2C3; border-radius: 16px; padding: 1.2rem 1.5rem; margin-bottom: 8px; transition: all 0.2s; }
.cand-card:hover { border-color: #C49A2C; box-shadow: 0 6px 24px rgba(64,112,244,0.1); transform: translateY(-1px); }
.chamada-card { background: #ffffff; border: 1.5px solid #D9D2C3; border-radius: 16px; padding: 1.2rem 1.5rem; margin-bottom: 10px; transition: all 0.2s; }
.chamada-card:hover { border-color: #C49A2C; box-shadow: 0 6px 24px rgba(64,112,244,0.1); }
.avatar { width: 46px; height: 46px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 14px; font-weight: 700; flex-shrink: 0; color: white; }
.cand-photo { width: 46px; height: 46px; border-radius: 12px; object-fit: cover; flex-shrink: 0; border: 1px solid #D9D2C3; }
.cand-photo-lg { width: 60px; height: 60px; border-radius: 14px; object-fit: cover; flex-shrink: 0; border: 1px solid #D9D2C3; }
.cand-name { font-size: 15px; font-weight: 700; color: #071D49; margin: 0 0 3px; }
.cand-sub { font-size: 12px; color: #5E6675; margin: 0; font-weight: 500; }
.cand-card + div[data-testid="stHorizontalBlock"] { margin-top: -8px !important; margin-bottom: 18px !important; }
.cand-card + div[data-testid="stHorizontalBlock"] .stButton button { min-height: 36px !important; padding: 0.45rem 1rem !important; }
.badge-sim { background: #e6f4ea; color: #1a7a4a; padding: 4px 12px; border-radius: 99px; font-size: 11px; font-weight: 700; border: 1px solid #b0dfc0; }
.badge-nao { background: #fff3e8; color: #c05a1a; padding: 4px 12px; border-radius: 99px; font-size: 11px; font-weight: 700; border: 1px solid #f0c8a0; }
.badge-aberta { background: #e6f4ea; color: #1a7a4a; padding: 3px 10px; border-radius: 99px; font-size: 11px; font-weight: 700; border: 1px solid #b0dfc0; }
.badge-encerrada { background: #F7F4ED; color: #5E6675; padding: 3px 10px; border-radius: 99px; font-size: 11px; font-weight: 700; border: 1px solid #D9D2C3; }
.badge-inscrito { background: #F4F0E6; color: #071D49; padding: 3px 10px; border-radius: 99px; font-size: 11px; font-weight: 700; border: 1px solid #D9D2C3; }
.selo { display: inline-block; font-size: 10px; font-weight: 700; padding: 3px 10px; border-radius: 99px; margin-right: 4px; margin-top: 4px; }
.selo-verificado { background: #F4F0E6; color: #071D49; border: 1px solid #D9D2C3; }
.selo-recomendado { background: #e6f4ea; color: #15803d; border: 1px solid #b0dfc0; }
.selo-destaque { background: #fff8e6; color: #b45309; border: 1px solid #fde68a; }
.selo-experiente { background: #f3effe; color: #6d28d9; border: 1px solid #ddd6fe; }
.metric-box { background: #ffffff; border: 1.5px solid #D9D2C3; border-radius: 14px; padding: 16px 18px; text-align: center; }
.metric-label { font-size: 11px; font-weight: 700; color: #5E6675; text-transform: uppercase; letter-spacing: .08em; margin: 0 0 6px; }
.metric-value { font-size: 20px; font-weight: 800; color: #071D49; margin: 0; }
.profile-name { font-family: 'Cormorant Garamond',serif; font-size: 28px; font-weight: 700; color: #071D49; margin: 0 0 6px; }
.section-label { font-size: 11px; font-weight: 800; color: #071D49; text-transform: uppercase; letter-spacing: .1em; margin: 1.5rem 0 0.5rem; }
.info-card { background: #F7F4ED; border: 1.5px solid #D9D2C3; border-radius: 12px; padding: 14px 18px; font-size: 14px; color: #071D49; line-height: 1.6; font-weight: 500; }
.custom-divider { height: 1px; background: #D9D2C3; margin: 1.5rem 0; }
.info-box { background: #F4F0E6; border: 1px solid #D9D2C3; border-radius: 10px; padding: 10px 14px; font-size: 13px; color: #071D49; margin-top: 8px; font-weight: 600; }
.lock-box { background: #F7F4ED; border: 1.5px solid #D9D2C3; border-radius: 12px; padding: 14px 18px; font-size: 13px; color: #5E6675; text-align: center; font-weight: 500; }
.disclaimer-box { background: #fff8e6; border: 1px solid #fde68a; border-radius: 10px; padding: 12px 16px; font-size: 12px; color: #92400e; line-height: 1.6; margin-top: 1rem; font-weight: 500; }
.step-bar { display: flex; gap: 8px; margin-bottom: 2rem; }
.step { flex: 1; height: 4px; border-radius: 99px; background: #D9D2C3; }
.step.active { background: linear-gradient(135deg,#C49A2C,#C49A2C); }
.step.done { background: #1a7a4a; }
.step-title { font-size: 13px; font-weight: 700; color: #5E6675; margin-bottom: 0.3rem; }
.step-desc { font-family: 'Cormorant Garamond',serif; font-size: 24px; font-weight: 700; color: #071D49; margin-bottom: 1.5rem; }
.doc-sub { font-size: 12px; font-weight: 800; color: #071D49; text-transform: uppercase; letter-spacing: .08em; margin: 1.5rem 0 0.5rem; }
.doc-body { font-size: 14px; color: #071D49; line-height: 1.8; margin-bottom: 0.8rem; font-weight: 500; }
.doc-item { font-size: 14px; color: #071D49; line-height: 1.8; padding-left: 1rem; font-weight: 500; }

/* Botões globais */
.stButton button {
    min-height: 42px !important;
    background: linear-gradient(135deg,#C49A2C,#C49A2C) !important;
    color: #071D49 !important;
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
    background: linear-gradient(135deg,#C49A2C,#C49A2C) !important;
    color: #071D49 !important;
    border: 1px solid rgba(13,31,78,0.08) !important;
    border-radius: 10px !important;
    font-family: 'Inter',sans-serif !important;
    font-weight: 800 !important;
    padding: 0.62rem 2rem !important;
    font-size: 14px !important;
    box-shadow: 0 8px 18px rgba(217,165,20,0.18) !important;
}
[data-testid="stFormSubmitButton"] button:hover {
    background: linear-gradient(135deg,#C49A2C,#C49A2C) !important;
    color: #071D49 !important;
    border-color: rgba(13,31,78,0.08) !important;
}
div[data-testid="column"]:last-child .stButton button,
div[data-testid="column"]:nth-last-child(2) .stButton button { background: #ffffff !important; color: #071D49 !important; border: 1.5px solid #D9D2C3 !important; border-radius: 10px !important; padding: 0.58rem 1rem !important; font-size: 13px !important; font-weight: 800 !important; width: 100%; box-shadow: 0 6px 16px rgba(13,31,78,0.08) !important; }
div[data-testid="column"]:last-child .stButton button:hover,
div[data-testid="column"]:nth-last-child(2) .stButton button:hover { background: #F4F0E6 !important; border-color: #C49A2C !important; color: #071D49 !important; }
.stTextInput input, .stTextArea textarea, .stDateInput input { border-radius: 10px !important; border-color: #D9D2C3 !important; background: #ffffff !important; color: #071D49 !important; font-family: 'Inter',sans-serif !important; font-size: 14px !important; font-weight: 500 !important; }
.stTextInput input:focus, .stTextArea textarea:focus, .stDateInput input:focus { border-color: #C49A2C !important; box-shadow: 0 0 0 3px rgba(64,112,244,0.1) !important; }
.stTextInput input::placeholder, .stTextArea textarea::placeholder { color: #5E6675 !important; opacity: 1 !important; font-weight: 500 !important; }
.stSelectbox > div > div { border-radius: 10px !important; border-color: #D9D2C3 !important; background: #ffffff !important; color: #071D49 !important; }
.stSelectbox [data-baseweb="select"] * { color: #071D49 !important; font-weight: 500 !important; }
.stRadio label, .stCheckbox label { color: #071D49 !important; font-weight: 600 !important; }
.stMultiSelect > div > div { background: #ffffff !important; border-color: #D9D2C3 !important; border-radius: 10px !important; }
.stMultiSelect [data-baseweb="select"] { color: #071D49 !important; }
.stMultiSelect [data-baseweb="select"] svg { fill: #071D49 !important; color: #071D49 !important; }
[data-baseweb="popover"], [data-baseweb="menu"], [data-baseweb="calendar"], [role="listbox"] { background: #ffffff !important; color: #071D49 !important; }
[role="option"], [role="option"] *, [data-baseweb="calendar"] * { color: #071D49 !important; }
[role="option"]:hover, [role="option"][aria-selected="true"] { background: #F4F0E6 !important; color: #071D49 !important; }
label[data-baseweb="label"] { color: #071D49 !important; font-weight: 700 !important; }
.form-item-title { font-size: 12px; font-weight: 800; color: #071D49; text-transform: uppercase; letter-spacing: .08em; margin: 18px 0 8px; padding-top: 14px; border-top: 1px solid #D9D2C3; }
.add-hint { font-size: 12px; color: #5E6675; font-weight: 600; margin: -2px 0 10px; }
.highlight-panel { background: #fff8e6; border: 1.5px solid #C49A2C; border-radius: 12px; padding: 12px 16px; margin: 10px 0 14px; color: #071D49; font-weight: 800; }
.stTextInput input:disabled { background: #F7F4ED !important; color: #071D49 !important; -webkit-text-fill-color: #071D49 !important; border-color: #D9D2C3 !important; font-weight: 800 !important; opacity: 1 !important; }
[data-baseweb="input"], [data-baseweb="select"] { background: #ffffff !important; color: #071D49 !important; }
[data-baseweb="input"] button, [data-testid="stFileUploader"] button { background: #ffffff !important; color: #071D49 !important; border-color: #D9D2C3 !important; }
[data-testid="stFileUploader"] section { background: #ffffff !important; border-color: #D9D2C3 !important; border-radius: 12px !important; }
[data-testid="stFileUploader"] * { color: #071D49 !important; }
.stTabs [data-baseweb="tab-list"] {
    background: #F4F0E6 !important;
    border-radius: 12px !important;
    padding: 5px !important;
    gap: 5px !important;
    border: 1px solid #D9D2C3 !important;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.65) !important;
}
.stTabs [data-baseweb="tab"] {
    min-height: 38px !important;
    padding: 0 14px !important;
    background: transparent !important;
    color: #071D49 !important;
    border-radius: 9px !important;
    font-weight: 700 !important;
}
.stTabs [data-baseweb="tab"] p {
    color: inherit !important;
    font-weight: inherit !important;
}
.stTabs [aria-selected="true"] {
    background: #ffffff !important;
    color: #071D49 !important;
    font-weight: 800 !important;
    box-shadow: 0 6px 14px rgba(13,31,78,0.08) !important;
}
.stAlert [data-testid="stMarkdownContainer"],
.stAlert [data-testid="stMarkdownContainer"] p {
    color: #071D49 !important;
    font-weight: 600;
}

/* ── Camada visual neutra inspirada na nova landing ── */
[data-testid="stAppViewContainer"] { background: #FBFAF7 !important; }
html, body, [class*="css"] { color: #071D49 !important; }
.main .block-container { max-width: 1120px; }
.topbar {
    background: #071D49 !important;
    border-bottom: 1px solid #D9D2C3 !important;
    box-shadow: 0 8px 24px rgba(30,30,30,0.08);
}
.topbar-logo-icon, .topbar-nav a.btn-rec {
    background: linear-gradient(135deg,#C49A2C,#E7D28A) !important;
    color: #071D49 !important;
}
.topbar .topbar-logo-name { color: #ffffff !important; }
.topbar .topbar-logo-sub, .topbar-nav a.active { color: #E7D28A !important; }
.topbar-nav a.active { border-color: rgba(232,212,138,.45) !important; background: rgba(232,212,138,.1) !important; }
.hero-card, .profile-shell, .profile-panel, .edit-hero, .cand-card, .chamada-card, .metric-box,
.info-card, .lock-box, .profile-detail, [data-testid="stFileUploader"] section {
    background: #ffffff !important;
    border-color: #D9D2C3 !important;
    box-shadow: 0 14px 36px rgba(30,30,30,0.06) !important;
}
.page-title, .edit-title, .profile-name-main, .profile-name, .cand-name,
.metric-value, .section-label, .profile-shell-title, .form-item-title {
    color: #071D49 !important;
}
.page-title em, .edit-title em {
    background: none !important;
    -webkit-text-fill-color: #C49A2C !important;
    color: #C49A2C !important;
}
.page-sub, .edit-sub, .cand-sub, .doc-body, .add-hint,
[data-testid="stCaptionContainer"], .stCaptionContainer {
    color: #5E6675 !important;
}
.stButton button, [data-testid="stFormSubmitButton"] button {
    background: #C49A2C !important;
    color: #071D49 !important;
    border-color: rgba(30,30,30,.1) !important;
    box-shadow: 0 10px 22px rgba(184,151,58,.18) !important;
}
.stButton button:hover, [data-testid="stFormSubmitButton"] button:hover {
    background: #E7D28A !important;
    color: #071D49 !important;
}
div[data-testid="column"]:last-child .stButton button,
div[data-testid="column"]:nth-last-child(2) .stButton button {
    background: #ffffff !important;
    color: #071D49 !important;
    border-color: #D9D2C3 !important;
}
div[data-testid="column"]:last-child .stButton button:hover,
div[data-testid="column"]:nth-last-child(2) .stButton button:hover {
    background: #F4F0E6 !important;
    border-color: #C49A2C !important;
}
.profile-action {
    background: #FFF8E6 !important;
    border-color: #E7D28A !important;
    color: #8a6a16 !important;
}
.profile-action:hover { background: #E7D28A !important; color: #071D49 !important; }
.highlight-panel, .profile-concurso {
    background: #FFF8E6 !important;
    border-color: #E7D28A !important;
    color: #071D49 !important;
}
.stat-pill, .profile-chip, .badge-inscrito {
    background: #F4F0E6 !important;
    color: #071D49 !important;
    border-color: #D9D2C3 !important;
}
.custom-divider, .form-item-title { border-color: #D9D2C3 !important; background: #D9D2C3 !important; }
.stTextInput input, .stTextArea textarea, .stDateInput input,
.stSelectbox > div > div, .stMultiSelect > div > div,
[data-baseweb="input"], [data-baseweb="select"] {
    background: #ffffff !important;
    color: #071D49 !important;
    border-color: #D9D2C3 !important;
}
[data-baseweb="popover"], [data-baseweb="menu"], [data-baseweb="calendar"], [role="listbox"] {
    background: #ffffff !important;
    color: #071D49 !important;
}
[role="option"], [role="option"] *, [data-baseweb="calendar"] * { color: #071D49 !important; }
[role="option"]:hover, [role="option"][aria-selected="true"] { background: #F4F0E6 !important; color: #071D49 !important; }
.stSelectbox [data-baseweb="select"] div,
.stSelectbox [data-baseweb="select"] span {
    color: #071D49 !important;
    -webkit-text-fill-color: #071D49 !important;
}
[data-baseweb="popover"] [role="option"],
[data-baseweb="popover"] [role="option"] *,
[data-baseweb="menu"] [role="option"],
[data-baseweb="menu"] [role="option"] *,
[data-baseweb="select-dropdown"] [role="option"],
[data-baseweb="select-dropdown"] [role="option"] * {
    background-color: #ffffff !important;
    color: #071D49 !important;
    -webkit-text-fill-color: #071D49 !important;
}
[data-baseweb="popover"] [aria-selected="true"],
[data-baseweb="menu"] [aria-selected="true"],
[data-baseweb="select-dropdown"] [aria-selected="true"],
[data-baseweb="popover"] [role="option"]:hover,
[data-baseweb="menu"] [role="option"]:hover {
    background-color: #F4F0E6 !important;
    color: #071D49 !important;
}
.stMultiSelect [data-baseweb="tag"] { color: inherit !important; }
.stTabs [data-baseweb="tab-list"] { background: #F4F0E6 !important; border-color: #D9D2C3 !important; }
.stTabs [data-baseweb="tab"] { color: #5E6675 !important; }
.stTabs [aria-selected="true"] { color: #071D49 !important; box-shadow: 0 6px 14px rgba(30,30,30,0.08) !important; }
.profile-sub-main { color: #5E6675 !important; font-size: 13px !important; font-weight: 600 !important; }
.profile-section-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin: 14px 0; }
.profile-section-card { background: #ffffff; border: 1px solid #D9D2C3; border-radius: 12px; padding: 14px 16px; min-width: 0; }
.profile-section-card.full { grid-column: 1 / -1; }
.profile-section-title { color: #5E6675; font-size: 10px; font-weight: 900; letter-spacing: .09em; text-transform: uppercase; margin: 0 0 8px; }
.profile-list { display: flex; flex-direction: column; gap: 8px; }
.profile-list-item { color: #071D49; font-size: 13px; font-weight: 650; line-height: 1.45; overflow-wrap: anywhere; }
.profile-list-item span { color: #5E6675; font-weight: 600; }
.profile-empty { color: #5E6675; font-size: 13px; font-weight: 600; }
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
        "tokens": pl.worksheet("tokens"),
    }

abas = conectar_sheets()
aba_candidatos = abas["candidatos"]
aba_recrutadores = abas["recrutadores"]
aba_chamadas = abas["chamadas"]
aba_interesses = abas["interesses"]
aba_recomendacoes = abas["recomendacoes"]
aba_tokens = abas["tokens"]

CAND_COL_SENHA = 19
CAND_COL_FOTO = 20
CH_COL_RESULTADO_TIPO = 18
CH_COL_SELECIONADOS = 19
CH_COL_MSG_APROVADOS = 20
CH_COL_MSG_REPROVADOS = 21
CH_COL_MOTIVO_ENCERRAMENTO = 22
CH_COL_ENCERRADO_EM = 23
CH_COL_COMUNICACAO_RESULTADO = 24

def garantir_coluna(aba, nome, posicao):
    try:
        cabecalhos = aba.row_values(1)
        if nome not in cabecalhos:
            aba.update_cell(1, posicao, nome)
    except Exception:
        pass

garantir_coluna(aba_candidatos, "senha", CAND_COL_SENHA)
garantir_coluna(aba_candidatos, "foto", CAND_COL_FOTO)
garantir_coluna(aba_chamadas, "resultado_tipo", CH_COL_RESULTADO_TIPO)
garantir_coluna(aba_chamadas, "selecionados", CH_COL_SELECIONADOS)
garantir_coluna(aba_chamadas, "mensagem_aprovados", CH_COL_MSG_APROVADOS)
garantir_coluna(aba_chamadas, "mensagem_reprovados", CH_COL_MSG_REPROVADOS)
garantir_coluna(aba_chamadas, "motivo_encerramento", CH_COL_MOTIVO_ENCERRAMENTO)
garantir_coluna(aba_chamadas, "encerrado_em", CH_COL_ENCERRADO_EM)
garantir_coluna(aba_chamadas, "comunicacao_resultado", CH_COL_COMUNICACAO_RESULTADO)

# ── Navegação por URL ─────────────────────────────────────────────────────────
params = st.query_params
p = params.get("p", st.session_state.get("pagina", "publico"))
if isinstance(p,list): p = p[0]
if p not in ["publico","avisos","inicio","perfil","candidatos","chamadas","cadastro","recrutador","privacidade","termos","recomendar","esqueci","redefinir"]:
    p = "publico"
if "pagina" not in st.session_state or params.get("p"):
    st.session_state.pagina = p
pagina = st.session_state.pagina

# ── Constantes ────────────────────────────────────────────────────────────────
AVATAR_CORES = ["#071D49","#2e7d5e","#7b3fa0","#c05a1a","#1a6b8a","#a04040","#3a6b2a"]
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
DISCLAIMER = "O IndicaJur atua exclusivamente como plataforma de aproximação. A publicação deste Seletivo não configura processo seletivo vinculante, concurso público ou compromisso de contratação. O uso do ius indicandum é de responsabilidade exclusiva do recrutador, que deve observar as normas de impessoalidade e vedação ao nepotismo aplicáveis ao seu órgão."

# ── Funções ───────────────────────────────────────────────────────────────────
def cor_avatar(n): return AVATAR_CORES[sum(ord(c) for c in n)%len(AVATAR_CORES)]
def iniciais(n):
    p=n.strip().split()
    return (p[0][0]+p[-1][0]).upper() if len(p)>=2 else n[:2].upper()
def hash_senha(s): return hashlib.sha256(s.encode()).hexdigest()
def rec_logado(): return "rec_logado" in st.session_state and st.session_state.rec_logado
def cand_logado(): return "cand_logado" in st.session_state and st.session_state.cand_logado
def auth_salt():
    try:
        return st.secrets.get("auth", {}).get("salt", "indicajur-session")
    except Exception:
        return "indicajur-session"
def token_recrutador(rec):
    email = str(rec.get("email","") or "").strip().lower()
    senha = str(rec.get("senha","") or "")
    assinatura = hashlib.sha256(f"{email}|{senha}|{auth_salt()}".encode()).hexdigest()
    bruto = f"{email}|{assinatura}".encode("utf-8")
    return base64.urlsafe_b64encode(bruto).decode("utf-8").rstrip("=")
def validar_token_recrutador(token):
    token = str(token or "").strip()
    if not token:
        return None
    try:
        padding = "=" * (-len(token) % 4)
        email, assinatura = base64.urlsafe_b64decode((token + padding).encode("utf-8")).decode("utf-8").split("|", 1)
    except Exception:
        return None
    for rec in aba_recrutadores.get_all_records():
        if str(rec.get("email","")).strip().lower() == email and str(rec.get("status","")).lower() == "ativo":
            esperado = token_recrutador(rec)
            if esperado == token:
                return rec
    return None
def auth_rec_query():
    token = st.session_state.get("rec_auth_token", "")
    return f"&auth={urllib.parse.quote(token)}" if token else ""
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
    auth_param = st.query_params.get("auth", "")
    if isinstance(auth_param, list):
        auth_param = auth_param[0]
    if not rec_logado() and auth_param:
        rec_token = validar_token_recrutador(auth_param)
        if rec_token:
            st.session_state.rec_logado = rec_token
            st.session_state.rec_email_logado = rec_token.get("email", "")
            st.session_state.rec_auth_token = auth_param
            return
    email = str(st.session_state.get("rec_email_logado", "") or "").strip().lower()
    if rec_logado() or not email:
        return
    for rec in aba_recrutadores.get_all_records():
        if str(rec.get("email", "")).strip().lower() == email:
            st.session_state.rec_logado = rec
            st.session_state.rec_auth_token = token_recrutador(rec)
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

def parse_data_br(valor):
    valor = str(valor or "").strip()
    try:
        return datetime.strptime(valor, "%d/%m/%Y").date()
    except ValueError:
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


def salvar_candidato_batch(aba, linha, dados: dict):
    """Grava campos do candidato em uma única chamada batch — substitui 12 update_cell."""
    MAPA = {
        "formacao": 3, "instituicao": 4, "area": 5, "disponibilidade": 6,
        "oab": 7, "experiencia_orgaos": 8, "sistemas": 9, "resumo": 11,
        "selo_verificado": 13, "selo_recomendado": 14, "selo_destaque": 15,
        "selo_experiente": 16, "concurso": 18, "foto": CAND_COL_FOTO,
    }
    updates = []
    for campo, col in MAPA.items():
        if campo in dados:
            cell = gspread.utils.rowcol_to_a1(linha, col)
            updates.append({"range": cell, "values": [[dados[campo]]]})
    if updates:
        aba.batch_update(updates, value_input_option="RAW")


def salvar_recrutador_batch(aba, linha, dados: dict):
    """Grava campos do recrutador em uma única chamada batch."""
    MAPA = {
        "nome": 1, "estado": 4, "municipio": 5, "orgao": 6,
        "nome_orgao": 7, "cargo": 8, "areas": 9,
    }
    updates = []
    for campo, col in MAPA.items():
        if campo in dados:
            cell = gspread.utils.rowcol_to_a1(linha, col)
            updates.append({"range": cell, "values": [[dados[campo]]]})
    if updates:
        aba.batch_update(updates, value_input_option="RAW")


def salvar_resultado_seletivo(aba, linha, dados: dict):
    MAPA = {
        "status": 14,
        "resultado_tipo": CH_COL_RESULTADO_TIPO,
        "selecionados": CH_COL_SELECIONADOS,
        "mensagem_aprovados": CH_COL_MSG_APROVADOS,
        "mensagem_reprovados": CH_COL_MSG_REPROVADOS,
        "motivo_encerramento": CH_COL_MOTIVO_ENCERRAMENTO,
        "encerrado_em": CH_COL_ENCERRADO_EM,
        "comunicacao_resultado": CH_COL_COMUNICACAO_RESULTADO,
    }
    updates = []
    for campo, col in MAPA.items():
        if campo in dados:
            cell = gspread.utils.rowcol_to_a1(linha, col)
            updates.append({"range": cell, "values": [[dados[campo]]]})
    if updates:
        aba.batch_update(updates, value_input_option="RAW")


def email_resultado_seletivo(destinatario, nome_candidato, titulo, orgao, situacao, mensagem):
    assunto = f"IndicaJur — Resultado do Seletivo: {titulo}"
    corpo = f"""
    <div style="font-family:'Segoe UI',Arial,sans-serif;max-width:640px;margin:0 auto;background:#ffffff;color:#071D49">
        <div style="background:#071D49;padding:28px;border-radius:14px 14px 0 0">
            <h1 style="color:#ffffff;font-size:22px;margin:0">IndicaJur</h1>
            <p style="color:#E7D28A;font-size:13px;margin:6px 0 0">Comunicação de resultado de Seletivo</p>
        </div>
        <div style="border:1px solid #D9D2C3;border-top:0;padding:26px;border-radius:0 0 14px 14px">
            <p style="font-size:15px;line-height:1.7;margin:0 0 14px">Olá, <strong>{html_lib.escape(nome_candidato or 'candidato')}</strong>.</p>
            <p style="font-size:15px;line-height:1.7;margin:0 0 14px">
                O recrutador registrou uma atualização no Seletivo <strong>{html_lib.escape(titulo)}</strong>, vinculado a <strong>{html_lib.escape(orgao)}</strong>.
            </p>
            <div style="background:#F4F0E6;border:1px solid #D9D2C3;border-radius:10px;padding:14px 16px;margin:18px 0">
                <strong style="font-size:13px;text-transform:uppercase;letter-spacing:.06em;color:#5E6675">Situação</strong>
                <p style="font-size:16px;font-weight:700;margin:6px 0 0;color:#071D49">{html_lib.escape(situacao)}</p>
            </div>
            <p style="font-size:15px;line-height:1.7;margin:0 0 18px">{html_lib.escape(mensagem or '').replace(chr(10), '<br>')}</p>
            <p style="font-size:12px;line-height:1.6;color:#5E6675;margin:22px 0 0;border-top:1px solid #D9D2C3;padding-top:14px">
                Esta mensagem é informativa. A decisão final e a condução do procedimento são de responsabilidade do recrutador.
            </p>
        </div>
    </div>
    """
    return enviar_email(destinatario, assunto, corpo)


def email_ja_cadastrado(aba, email):
    """Verifica duplicidade de e-mail antes de cadastrar."""
    try:
        todos = aba.get_all_records()
        email_norm = str(email or "").strip().lower()
        return any(str(c.get("email","")).strip().lower() == email_norm for c in todos)
    except Exception:
        return False



def gerar_token_senha():
    """Gera token seguro de 32 bytes para redefinição de senha."""
    return secrets.token_urlsafe(32)


def salvar_token(email, tipo, token):
    """
    Salva token na aba 'tokens'.
    Colunas: token | email | tipo (candidato/recrutador) | criado_em | usado
    """
    try:
        # Invalidar tokens anteriores do mesmo email+tipo
        todos = aba_tokens.get_all_records()
        for i, row in enumerate(todos):
            if row.get("email","").lower() == email.lower() and row.get("tipo") == tipo and row.get("usado") != "sim":
                aba_tokens.update_cell(i + 2, 5, "sim")
        # Inserir novo token
        aba_tokens.append_row([
            token, email, tipo,
            datetime.now().strftime("%d/%m/%Y %H:%M"),
            "nao"
        ])
        return True
    except Exception as e:
        return False


def buscar_token(token):
    """Retorna o registro do token se válido e não expirado (2h)."""
    try:
        todos = aba_tokens.get_all_records()
        for row in todos:
            if row.get("token") == token and row.get("usado") != "sim":
                criado_str = row.get("criado_em", "")
                try:
                    criado = datetime.strptime(criado_str, "%d/%m/%Y %H:%M")
                    if (datetime.now() - criado).total_seconds() < 7200:  # 2h
                        return row
                except Exception:
                    return row  # sem data = aceita
        return None
    except Exception:
        return None


def invalidar_token(token):
    """Marca token como usado."""
    try:
        todos = aba_tokens.get_all_records()
        for i, row in enumerate(todos):
            if row.get("token") == token:
                aba_tokens.update_cell(i + 2, 5, "sim")
                return True
    except Exception:
        pass
    return False


def email_redefinicao(destinatario, link, tipo):
    """Envia e-mail com link de redefinição de senha."""
    label = "candidato" if tipo == "candidato" else "recrutador"
    assunto = "IndicaJur — Redefinição de senha"
    corpo = f"""
    <div style="font-family:'Segoe UI',Arial,sans-serif;max-width:600px;margin:0 auto;background:#ffffff">
        <div style="background:#071D49;padding:32px;text-align:center;border-radius:12px 12px 0 0">
            <h1 style="color:#ffffff;font-size:22px;margin:0;letter-spacing:-.5px">Juris<span style="color:#C49A2C">dica</span></h1>
            <p style="color:rgba(255,255,255,0.5);font-size:12px;margin:4px 0 0;font-style:italic">ius indicandum</p>
        </div>
        <div style="padding:32px;background:#FBFAF7;border-radius:0 0 12px 12px">
            <h2 style="color:#071D49;font-size:20px;margin:0 0 12px">Redefinição de senha</h2>
            <p style="color:#5E6675;font-size:15px;line-height:1.7;margin:0 0 20px">
                Recebemos uma solicitação de redefinição de senha para sua conta de <strong style="color:#071D49">{label}</strong> no IndicaJur.
            </p>
            <p style="color:#5E6675;font-size:14px;line-height:1.7;margin:0 0 24px">
                Clique no botão abaixo para criar uma nova senha. O link é válido por <strong>2 horas</strong>.
            </p>
            <div style="text-align:center;margin:28px 0">
                <a href="{link}" style="display:inline-block;padding:14px 36px;background:#C49A2C;color:#071D49;font-weight:700;font-size:15px;border-radius:10px;text-decoration:none">
                    Redefinir minha senha →
                </a>
            </div>
            <p style="color:#9a9a9a;font-size:12px;line-height:1.6;margin:0;border-top:1px solid #D9D2C3;padding-top:16px">
                Se você não solicitou a redefinição, ignore este e-mail — sua senha não será alterada.<br>
                <strong>IndicaJur</strong> — banco de talentos jurídicos certificados.
            </p>
        </div>
    </div>
    """
    return enviar_email(destinatario, assunto, corpo)


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
        return '<span style="font-size:10px;font-weight:700;padding:2px 8px;border-radius:99px;background:rgba(200,150,12,0.1);color:#C49A2C;margin-left:4px;border:1px solid rgba(200,150,12,0.18)">📚 Concursando</span>'
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
    return f"""<div class="info-card" style="background:{cb};border-color:#D9D2C3">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px">
            <span style="font-weight:800;color:{tb};font-size:22px">{d}</span>
            <span style="font-weight:700;color:{tb};font-size:15px">{det.get('nome','')}</span>
        </div>
        <p style="color:{tb};font-size:13px;font-weight:600;margin:0 0 8px">{det.get('resumo','')}</p>
        <p style="color:#5E6675;font-size:12px;margin:0 0 4px"><strong style="color:{tb}">Pontos fortes:</strong> {det.get('pontos_fortes','')}</p>
        <p style="color:#5E6675;font-size:12px;margin:0 0 4px"><strong style="color:{tb}">No gabinete:</strong> {det.get('no_gabinete','')}</p>
        <p style="color:#5E6675;font-size:12px;margin:0"><strong style="color:{tb}">Atenção:</strong> {det.get('atencao','')}</p>
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
    assunto = f"IndicaJur — {nome_candidato} solicitou sua avaliação"
    corpo = f"""
    <div style="font-family:'Segoe UI',Arial,sans-serif;max-width:600px;margin:0 auto;background:#ffffff">
        <div style="background:linear-gradient(135deg,#071D49,#071D49);padding:32px;text-align:center;border-radius:12px 12px 0 0">
            <div style="width:48px;height:48px;background:linear-gradient(135deg,#C49A2C,#C49A2C);border-radius:10px;display:inline-flex;align-items:center;justify-content:center;font-size:24px;margin-bottom:12px">⚖</div>
            <h1 style="color:#ffffff;font-size:22px;margin:0;letter-spacing:-0.5px">IndicaJur</h1>
            <p style="color:rgba(255,255,255,0.6);font-size:12px;margin:4px 0 0;font-style:italic">ius indicandum</p>
        </div>
        <div style="padding:32px;background:#f4f6fc;border-radius:0 0 12px 12px">
            <h2 style="color:#071D49;font-size:20px;margin:0 0 12px">Solicitação de avaliação</h2>
            <p style="color:#4a5568;font-size:15px;line-height:1.7;margin:0 0 20px">
                O profissional <strong style="color:#071D49">{nome_candidato}</strong> indicou você como recomendador no IndicaJur e solicita que você preencha uma avaliação do seu perfil profissional.
            </p>
            <p style="color:#4a5568;font-size:14px;line-height:1.7;margin:0 0 24px">
                A avaliação é rápida (menos de 5 minutos) e ficará disponível para recrutadores de Tribunais, Ministérios Públicos, Defensorias e Procuradorias ao analisar o perfil do candidato.
            </p>
            <div style="text-align:center;margin:28px 0">
                <a href="{link}" style="display:inline-block;padding:14px 36px;background:linear-gradient(135deg,#C49A2C,#C49A2C);color:#071D49;font-weight:700;font-size:15px;border-radius:10px;text-decoration:none">
                    Preencher avaliação →
                </a>
            </div>
            <p style="color:#8090b8;font-size:12px;line-height:1.6;margin:0;border-top:1px solid #D9D2C3;padding-top:16px">
                Este link é exclusivo e de uso único. Caso não reconheça esta solicitação, ignore este e-mail.<br>
                <strong>IndicaJur</strong> — plataforma de aproximação entre profissionais do Direito e órgãos do sistema de justiça.
            </p>
        </div>
    </div>
    """
    return enviar_email(email_recomendador, assunto, corpo)

# ── TOPBAR ────────────────────────────────────────────────────────────────────
restaurar_candidato_da_sessao()
restaurar_recrutador_da_sessao()

PAGINAS_CANDIDATO = ["inicio","perfil","cadastro","chamadas"]
PAGINAS_PUBLICAS = ["publico","avisos","candidatos","privacidade","termos","recomendar"]

if rec_logado() and pagina == "recrutador":
    dash_param = params.get("dash", "")
    if isinstance(dash_param, list):
        dash_param = dash_param[0]
    if dash_param in ["perfil","editar_rec","novo_seletivo","seletivos","banco"]:
        st.session_state.rec_dashboard = dash_param
    sair_param = params.get("sair", "")
    if isinstance(sair_param, list):
        sair_param = sair_param[0]
    if sair_param == "1":
        del st.session_state.rec_logado
        st.session_state.pop("rec_email_logado", None)
        st.session_state.pop("rec_auth_token", None)
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
        ("chamadas","Ver Seletivos"),
    ]
else:
    nav_pages = [
        ("publico","Início"),
        ("inicio","Sou Candidato"),
        ("recrutador","Sou Recrutador"),
    ]

nav_html = '<div class="topbar"><a class="topbar-logo" href="https://lcatolico.github.io/jurisbank/" target="_blank"><div class="topbar-logo-icon">IJ</div><div><span class="topbar-logo-name">IndicaJur</span><span class="topbar-logo-sub">indicações jurídicas com critério</span></div></a><div class="topbar-nav">'
for pg, lb in nav_pages:
    active = "active" if pagina == pg else ""
    if not rec_logado() and not cand_logado():
        if lb == "Sou Candidato" and pagina in ["inicio","cadastro","chamadas","avisos"]:
            active = "active"
        elif lb == "Sou Recrutador" and pagina == "recrutador":
            active = "active"
    nav_html += f'<a href="?p={pg}" class="{active}">{lb}</a>'

if rec_logado():
    dash_atual = st.session_state.get("rec_dashboard","perfil")
    auth_qs = auth_rec_query()
    for dash, lb in [("perfil","Perfil"),("editar_rec","Editar Perfil"),("seletivos","Seletivos"),("banco","Banco de Candidatos")]:
        active = "active" if pagina == "recrutador" and dash_atual == dash else ""
        nav_html += f'<a href="?p=recrutador&dash={dash}{auth_qs}" class="{active}">{lb}</a>'
    nav_html += f'<a href="?p=recrutador&sair=1{auth_qs}" class="btn-rec">Sair</a>'
elif cand_logado() and pagina in PAGINAS_CANDIDATO:
    nav_html += '<a href="?p=inicio&sair_cand=1" class="btn-rec">Sair</a>'

nav_html += '</div></div>'
st.markdown(nav_html, unsafe_allow_html=True)

# ── PÁGINA PÚBLICA ────────────────────────────────────────────────────────────
if pagina == "publico":
    st.markdown("""<div class="hero-card">
        <h1 class="page-title">IndicaJur<br><em>Ambientes.</em></h1>
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

# ── PÁGINA PÚBLICA: AVISOS ───────────────────────────────────────────────────
elif pagina == "avisos":
    st.markdown("""<div class="hero-card">
        <h1 class="page-title">Avisos de<br><em>Seletivos.</em></h1>
        <p class="page-sub">Informe suas preferências para ser avisado quando houver oportunidade compatível. A participação efetiva exige cadastro completo e inscrição no Seletivo.</p>
    </div>""", unsafe_allow_html=True)
    with st.form("form_avisos_publico"):
        aviso_email = st.text_input("E-mail para avisos", placeholder="seuemail@exemplo.com")
        c1, c2 = st.columns(2)
        with c1:
            aviso_inst = st.multiselect("Instituições de interesse", INSTITUICOES_INTERESSE)
        with c2:
            aviso_areas = st.multiselect("Áreas de interesse", AREAS)
        aviso_estados = st.multiselect("Estados de interesse", ESTADOS)
        st.markdown('<div class="disclaimer-box">Este cadastro é apenas para aviso de compatibilidade. Para participar de um Seletivo, será necessário completar o cadastro, autorizar o compartilhamento do perfil e realizar a inscrição quando a funcionalidade estiver ativa.</div>', unsafe_allow_html=True)
        registrar_aviso = st.form_submit_button("Registrar interesse")
    if registrar_aviso:
        if not aviso_email or "@" not in aviso_email:
            st.error("Informe um e-mail válido.")
        elif not aviso_areas:
            st.error("Selecione ao menos uma área de interesse.")
        else:
            preferencias = []
            if aviso_inst:
                preferencias.append("Instituições: " + ", ".join(aviso_inst))
            if aviso_estados:
                preferencias.append("Estados: " + ", ".join(aviso_estados))
            try:
                aba_interesses.append_row([aviso_email.strip(), ", ".join(aviso_areas), " | ".join(preferencias), datetime.now().strftime("%d/%m/%Y")])
                st.success("Interesse registrado. Quando houver Seletivo compatível, você poderá ser avisado.")
            except Exception as e:
                st.error(f"Erro ao registrar interesse. Tente novamente. ({e})")

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
        st.session_state.editar_perfil_candidato = False

    else:
        st.markdown("""<div class="hero-card">
            <h1 class="page-title">Área do<br><em>Candidato.</em></h1>
            <p class="page-sub">Entre para acompanhar seu perfil ou comece seu cadastro no IndicaJur.</p>
        </div>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        tabs = st.tabs(["Já tenho cadastro","Cadastrar-me"])
        with tabs[0]:
            st.markdown('<p style="font-size:16px;font-weight:700;color:#071D49;margin:1rem 0">Entrar no meu perfil</p>', unsafe_allow_html=True)
            with st.form("form_login_candidato_inicio"):
                email_login = st.text_input("E-mail cadastrado", key="login_candidato_inicio")
                senha_login = st.text_input("Senha", type="password", key="senha_candidato_inicio", help="Perfis antigos sem senha ainda podem entrar apenas com o e-mail.")
                entrar_login = st.form_submit_button("Entrar")
            if entrar_login:
                if not email_login:
                    st.error("Informe seu e-mail.")
                elif login_candidato(email_login, senha_login, permitir_sem_senha=True):
                    st.success("Bem-vindo ao IndicaJur.")
                    st.rerun()
                else:
                    st.error("E-mail ou senha inválidos.")
            st.markdown('<p style="font-size:12px;color:#5E6675;margin-top:8px">Esqueceu a senha? <a href="?p=esqueci" style="color:#C49A2C;font-weight:700">Recuperar acesso →</a></p>', unsafe_allow_html=True)
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
        with st.form("form_login_editar_perfil"):
            email_editar = st.text_input("E-mail cadastrado", value=email_param, key="login_editar_email")
            senha_editar = st.text_input("Senha", type="password", key="login_editar_senha")
            entrar_editar = st.form_submit_button("Entrar e editar perfil")
        if entrar_editar:
            if not email_editar:
                st.error("Informe seu e-mail.")
            elif login_candidato(email_editar, senha_editar, permitir_sem_senha=True):
                st.rerun()
            else:
                st.error("E-mail ou senha inválidos.")
        if st.button("Voltar à Área do Candidato", key="btn_voltar_login_cand"):
            ir("inicio")
    else:
        cand = st.session_state.cand_logado
        formacoes_base = formacoes_candidato(cand) or [{"grau":"Bacharel em Direito","instituicao":"","periodo":""}]
        experiencias_base = experiencias_candidato(cand) or [{"instituicao":"","orgao":"","cargo":"","supervisor":"","supervisor_email":"","inicio":"","fim":"","area":"","atribuicoes":"","sistemas":"","ferramenta_ia":""}]
        # Sempre sincroniza com a planilha ao entrar na página (evita estado stale)
        st.session_state.edit_qtd_form = max(1, len(formacoes_base))
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
                payload = {
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
                }
                try:
                    salvar_candidato_batch(aba_candidatos, linha, payload)
                    atual.update(payload)
                    st.session_state.cand_logado = atual
                    st.session_state.cand_email_logado = atual.get("email", "")
                    st.success("Perfil atualizado com sucesso.")
                    ir("inicio")
                except Exception as e:
                    st.error(f"Erro ao salvar perfil. Tente novamente. ({e})")

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
                    <div style="font-size:13px;color:#5E6675;margin-bottom:6px">{html_texto(resumo_formacoes(formacoes_view) or c.get('instituicao','—'))}</div>
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
                st.markdown(f'<div class="info-card">{html_texto(prev)}<br><br><span style="color:#C49A2C;font-size:12px">🔐 Resumo completo disponível para recrutadores.</span></div>',unsafe_allow_html=True)
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

        st.markdown(f'<p style="font-size:13px;color:#5E6675;font-weight:600;margin-bottom:1rem">{len(cf)} candidato(s)</p>',unsafe_allow_html=True)
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
    restaurar_candidato_da_sessao()
    email_param = params.get("email", "")
    if isinstance(email_param, list):
        email_param = email_param[0]
    if not cand_logado() and st.session_state.get("cand_email_logado"):
        login_candidato(st.session_state.get("cand_email_logado"), permitir_sem_senha=True)
    if email_param and not cand_logado():
        login_candidato(email_param, permitir_sem_senha=True)

    if not cand_logado() and not rec_logado():
        with st.expander("Sou candidato cadastrado — quero me inscrever"):
            with st.form("form_login_candidato_chamadas"):
                em=st.text_input("Seu e-mail cadastrado",key="cl")
                sn=st.text_input("Senha",type="password",key="cl_senha")
                acessar_chamadas = st.form_submit_button("Acessar")
            if acessar_chamadas:
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

    st.markdown(f'<p style="font-size:13px;color:#5E6675;font-weight:600;margin-bottom:1rem">{len(chf)} seletivo(s)</p>',unsafe_allow_html=True)

    for i,ch in enumerate(chf):
        ab=ch_aberta(ch); ins_=inscritos(ch); n=len(ins_)
        sb='<span class="badge-aberta">● Aberta</span>' if ab else '<span class="badge-encerrada">● Encerrada</span>'
        ja=cand_logado() and st.session_state.cand_logado.get("email","") in ins_

        st.markdown(f"""<div class="chamada-card">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:12px">
                <div style="flex:1">
                    <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">
                        {sb}
                        <span style="font-size:11px;color:#5E6675;font-weight:600">📅 {ch.get('prazo','—')}</span>
                        <span style="font-size:11px;color:#5E6675;font-weight:600">👥 {n} inscrito(s)</span>
                    </div>
                    <p style="font-size:16px;font-weight:700;color:#071D49;margin:0 0 4px">{ch.get('titulo','—')}</p>
                    <p style="font-size:13px;color:#5E6675;font-weight:500;margin:0 0 8px">{ch.get('orgao','—')} · {ch.get('municipio','—')}/{ch.get('estado','—')}</p>
                    <div style="display:flex;gap:8px;flex-wrap:wrap">
                        <span style="font-size:11px;font-weight:700;padding:3px 10px;border-radius:99px;background:#F4F0E6;color:#071D49;border:1px solid #D9D2C3">{ch.get('area','—')}</span>
                        <span style="font-size:11px;font-weight:700;padding:3px 10px;border-radius:99px;background:#F7F4ED;color:#071D49;border:1px solid #D9D2C3">{ch.get('regime','—')}</span>
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
                if st.button("Entrar como candidato", key=f"login_insc_{i}"):
                    ir("inicio")

        if st.session_state.get(f"ci{i}"):
            st.markdown(f'<div class="info-card" style="margin-top:8px"><strong style="color:#071D49">Inscrever em: {ch.get("titulo","")}</strong></div>',unsafe_allow_html=True)
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
            elif email_ja_cadastrado(aba_candidatos, email):
                st.error("Este e-mail já está cadastrado. Use a aba 'Já tenho cadastro'.")
            else:
                anos=anos_experiencias(experiencias_validas)
                st.session_state.dc.update({"nome":nome,"email":email,"senha":hash_senha(senha_cad),"foto":foto_data,"formacao":salvar_lista_json(formacoes_validas),"instituicao":resumo_formacoes(formacoes_validas),"area":", ".join(inst_interesse),"oab":oab,"anos_experiencia":anos,"disponibilidade":disp,"experiencia":salvar_lista_json(experiencias_validas),"sistemas":sistemas_experiencias(experiencias_validas),"pos":"","resumo":res,"concurso":conc})
                st.session_state.et=2; st.rerun()

    elif et==2:
        c1,c2=st.columns(2)
        with c1:
            st.markdown('<p style="font-weight:600;color:#C49A2C;margin-bottom:4px">★ Carta de recomendação</p>',unsafe_allow_html=True)
            st.markdown('<p style="font-size:12px;color:#5E6675;font-weight:500;margin-bottom:8px">De um Juiz, Promotor, Defensor ou Procurador ativo</p>',unsafe_allow_html=True)
            carta=st.file_uploader("",type="pdf",key="carta",label_visibility="collapsed")
        with c2:
            st.markdown('<p style="font-weight:600;color:#C49A2C;margin-bottom:4px">◆ Avaliação de desempenho</p>',unsafe_allow_html=True)
            st.markdown('<p style="font-size:12px;color:#5E6675;font-weight:500;margin-bottom:8px">Avaliação formal emitida pelo órgão</p>',unsafe_allow_html=True)
            aval=st.file_uploader("",type="pdf",key="aval",label_visibility="collapsed")

        d=st.session_state.dc; sp=[]
        if d.get("oab")=="Sim": sp.append("✓ Verificado")
        if carta: sp.append("★ Recomendado")
        if aval: sp.append("◆ Destaque")
        if d.get("anos_experiencia",0)>=2: sp.append("● Experiente")
        if sp:
            st.markdown('<div class="custom-divider"></div>',unsafe_allow_html=True)
            st.markdown('<p style="font-size:13px;font-weight:600;color:#C49A2C">Selos:</p>',unsafe_allow_html=True)
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
        st.markdown('<p style="font-size:14px;color:#5E6675;font-weight:500;margin-bottom:1.5rem">Não há respostas certas ou erradas. Responda pensando na forma como você costuma atuar no trabalho.</p>',unsafe_allow_html=True)
        rd=[]
        for j,(perg,ops) in enumerate(PERGUNTAS_DISC):
            r=st.radio(f"**{j+1}.** {perg}",ops,key=f"dq{j}",index=None)
            rd.append(r)
        st.markdown("<br>",unsafe_allow_html=True)
        c1,c2=st.columns(2)
        with c1:
            if st.button("← Voltar"): st.session_state.et=2; st.rerun()
        with c2:
            if st.button("Cadastrar no IndicaJur →"):
                if None in rd: st.error(f"Responda todas as {len(PERGUNTAS_DISC)} perguntas.")
                else:
                    d=st.session_state.dc
                    selos=calc_selos(d["oab"],d["anos_experiencia"],d.get("carta",False),d.get("avaliacao",False))
                    pd_,_,desc=calc_disc(rd)
                    try:
                        aba_candidatos.append_row([d["nome"],d["email"],d["formacao"],d["instituicao"],d["area"],d["disponibilidade"],d["oab"],d["experiencia"],d["sistemas"],d["pos"],d["resumo"],d.get("email_ref",""),selos["verificado"],selos["recomendado"],selos["destaque"],selos["experiente"],pd_,d.get("concurso","Não estou estudando para concurso"),d.get("senha",""),d.get("foto","")])
                        st.session_state.et=1; st.session_state.campos={}; st.session_state.dc={}
                        st.session_state.pop("cad_qtd_form", None); st.session_state.pop("cad_qtd_exp", None)
                        st.success("Bem-vindo ao IndicaJur!")
                        st.markdown(f'<div class="info-box">Perfil: <strong>{pd_} — {desc}</strong></div>',unsafe_allow_html=True)
                        st.balloons()
                    except Exception as e:
                        st.error(f"Erro ao salvar cadastro. Tente novamente. ({e})")

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
            auth_qs_rec = auth_rec_query()
            st.markdown(f"""<div class="rec-action-row">
                <a class="rec-action-card primary" href="?p=recrutador&dash=novo_seletivo{auth_qs_rec}">
                    <span class="rec-action-title">Novo Seletivo</span>
                    <span class="rec-action-text">Publicar oportunidade, etapas e prazos.</span>
                </a>
                <a class="rec-action-card" href="?p=recrutador&dash=seletivos{auth_qs_rec}">
                    <span class="rec-action-title">Meus Seletivos</span>
                    <span class="rec-action-text">Acompanhar inscritos, editar e encerrar.</span>
                </a>
            </div>""", unsafe_allow_html=True)


        if st.session_state.rec_dashboard == "editar_rec":
            st.markdown('<p class="section-label">Editar Perfil do Recrutador</p>', unsafe_allow_html=True)
            st.markdown('<div class="info-box">Atualize os dados institucionais usados no perfil, nos Seletivos e na comunicação com candidatos.</div>', unsafe_allow_html=True)
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
                    payload_rec = {
                        "nome": rec_nome, "estado": rec_estado,
                        "municipio": rec_municipio, "orgao": rec_orgao,
                        "nome_orgao": rec_nome_orgao, "cargo": rec_cargo,
                        "areas": ", ".join(rec_areas),
                    }
                    try:
                        salvar_recrutador_batch(aba_recrutadores, idx_r+2, payload_rec)
                        st.session_state.rec_logado=aba_recrutadores.get_all_records()[idx_r]
                        st.session_state.rec_email_logado=st.session_state.rec_logado.get("email","")
                        st.session_state.rec_auth_token=token_recrutador(st.session_state.rec_logado)
                        st.success("Perfil do recrutador atualizado.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao salvar perfil. Tente novamente. ({e})")

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
                if dsc!="Todos": st.markdown(f'<div style="background:#F7F4ED;border:1px solid #D9D2C3;border-radius:8px;padding:8px;font-size:11px;color:#5E6675;font-weight:600;margin-top:4px">ℹ {DISC_EXPLICACOES_FILTRO.get(dsc,"")}</div>',unsafe_allow_html=True)
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
            st.markdown(f'<p style="font-size:13px;color:#5E6675;font-weight:600;margin:1rem 0 0.5rem">{len(fi)} candidato(s)</p>',unsafe_allow_html=True)
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
                            st.session_state.rec_auth_token=token_recrutador(st.session_state.rec_logado)
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

        if st.session_state.rec_dashboard in ["novo_seletivo","seletivos"]:
            if st.session_state.rec_dashboard == "novo_seletivo":
                st.markdown('<p class="section-label">Lançar Novo Seletivo</p>',unsafe_allow_html=True)
                st.markdown('<div class="info-box">Preencha os dados do Seletivo, etapas previstas e prazos de cada etapa.</div>',unsafe_allow_html=True)
                st.session_state["criar_ch"]=True
            else:
                st.markdown('<p class="section-label">Meus Seletivos</p>',unsafe_allow_html=True)
                st.markdown('<div class="info-box">Consulte, edite, acompanhe inscritos e encerre Seletivos publicados.</div>',unsafe_allow_html=True)

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
                    with c2: prch_txt=st.text_input("Prazo final para inscrições *",placeholder="dd/mm/aaaa")
                    st.markdown('<div class="custom-divider"></div>',unsafe_allow_html=True)
                    st.markdown('<p class="section-label">Etapas do Seletivo</p>',unsafe_allow_html=True)
                    etapas=st.multiselect(
                        "Etapas previstas",
                        ["Triagem por currículo","Entrevista estruturada","Teste de escrita","Prova prática/minuta","Checagem de referências"],
                        default=["Triagem por currículo"]
                    )
                    prazos_etapas = {}
                    if etapas:
                        st.markdown('<div class="info-box">Informe o prazo final previsto para cada etapa selecionada. Use o formato dd/mm/aaaa.</div>', unsafe_allow_html=True)
                        for etapa in etapas:
                            etapa_key = re.sub(r"[^a-zA-Z0-9]+", "_", etapa).strip("_").lower()
                            prazos_etapas[etapa] = st.text_input(f"Prazo final - {etapa}", placeholder="dd/mm/aaaa", key=f"novo_sel_prazo_etapa_{etapa_key}")
                    organizacao_etapas=st.text_area("Como pretende organizar as etapas?",height=100,placeholder="Ex: primeiro análise curricular; depois entrevista com lista curta; se necessário, teste de escrita com prazo de 2 horas.")
                    comunicacao=st.text_area("Mensagem aos candidatos compatíveis",height=70,placeholder="Texto breve para orientar candidatos sobre o Seletivo e as próximas etapas.")
                    st.markdown("<br>",unsafe_allow_html=True)
                    c1,c2=st.columns(2)
                    with c1:
                        if st.button("Cancelar",key="cch"):
                            del st.session_state["criar_ch"]
                            st.session_state.rec_dashboard="seletivos"
                            st.rerun()
                    with c2:
                        if st.button("Publicar →",key="pch"):
                            prazo_principal = parse_data_br(prch_txt)
                            prazos_invalidos = [et for et, dtxt in prazos_etapas.items() if not parse_data_br(dtxt)]
                            ok=all([tch,och,toch!="Selecione...",ach,ech!="Selecione...",mch_,rch,remch,regch!="Selecione...",fsch!="Selecione...",prazo_principal])
                            if not ok: st.error("Preencha todos os campos.")
                            elif prazos_invalidos: st.error("Informe os prazos das etapas no formato dd/mm/aaaa.")
                            else:
                                etapas_descritas = []
                                for etapa in etapas:
                                    etapas_descritas.append(f"{etapa} até {prazos_etapas.get(etapa,'Não informado')}")
                                plano_seletivo = [
                                    rch.strip(),
                                    "",
                                    "Etapas e prazos: " + ("; ".join(etapas_descritas) if etapas_descritas else "Não informado"),
                                    "Organização das etapas: " + (organizacao_etapas.strip() or "Não informado"),
                                    "Mensagem aos candidatos: " + (comunicacao.strip() or "Não informado"),
                                ]
                                try:
                                    aba_chamadas.append_row([gerar_id(),tch,och,toch,", ".join(ach),ech,mch_,"\n".join(plano_seletivo),remch,regch,fsch,str(vch),prazo_principal.strftime("%d/%m/%Y"),"aberto",rec["email"],"",datetime.now().strftime("%d/%m/%Y")])
                                    del st.session_state["criar_ch"]; st.session_state.rec_dashboard="seletivos"; st.success("Seletivo publicado!"); st.rerun()
                                except Exception as e:
                                    st.error(f"Erro ao publicar Seletivo. Tente novamente. ({e})")

            if st.session_state.rec_dashboard == "novo_seletivo":
                pass
            elif not mch: st.info("Nenhum Seletivo publicado ainda.")
            else:
                for i,ch in enumerate(mch):
                    ch_key = re.sub(r"[^a-zA-Z0-9_]+", "_", str(ch.get("id") or i))
                    painel_inscritos_key = f"painel_inscritos_{ch_key}"
                    painel_resultado_key = f"painel_resultado_{ch_key}"
                    ab=ch_aberta(ch); ins_=inscritos(ch); n=len(ins_)
                    status_ch = str(ch.get("status","")).strip().lower()
                    if ab:
                        sb='<span class="badge-aberta">Aberta</span>'
                    elif status_ch == "deserto":
                        sb='<span class="badge-encerrada">Deserto</span>'
                    elif status_ch == "interrompido":
                        sb='<span class="badge-encerrada">Interrompido</span>'
                    else:
                        sb='<span class="badge-encerrada">Encerrada</span>'
                    resultado_resumo = str(ch.get("resultado_tipo","") or "").strip()
                    resultado_html = f'<span style="font-size:11px;color:#5E6675;font-weight:700">Resultado: {html_texto(resultado_resumo)}</span>' if resultado_resumo else ''
                    st.markdown(f"""<div class="chamada-card">
                        <div style="display:flex;justify-content:space-between;align-items:center">
                            <div>
                                <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px">{sb}<span style="font-size:11px;color:#5E6675;font-weight:600">📅 {ch.get('prazo','—')}</span></div>
                                <p style="font-size:15px;font-weight:700;color:#071D49;margin:0 0 2px">{ch.get('titulo','—')}</p>
                                <p style="font-size:12px;color:#5E6675;font-weight:500;margin:0">{ch.get('municipio','—')}/{ch.get('estado','—')} · {ch.get('area','—')}</p>
                                {resultado_html}
                            </div>
                            <div style="text-align:right">
                                <p style="font-size:26px;font-weight:800;color:#C49A2C;margin:0">{n}</p>
                                <p style="font-size:11px;color:#5E6675;font-weight:600;margin:0">inscrito(s)</p>
                            </div>
                        </div>
                    </div>""",unsafe_allow_html=True)
                    cv,crs=st.columns([6,3])
                    with cv:
                        if st.button("Ver inscritos",key=f"btn_vi_{ch_key}"):
                            st.session_state[painel_inscritos_key]=not st.session_state.get(painel_inscritos_key,False); st.rerun()
                    with crs:
                        if st.button("Resultado / Encerrar",key=f"btn_res_{ch_key}"):
                            st.session_state[painel_resultado_key]=not st.session_state.get(painel_resultado_key,False); st.rerun()
                    with st.expander("Editar Seletivo",expanded=False):
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
                    if st.session_state.get(painel_resultado_key):
                        with st.expander("Resultado e encerramento do Seletivo", expanded=True):
                            todos_cands_resultado = aba_candidatos.get_all_records()
                            inscritos_cands = [c for c in todos_cands_resultado if c.get("email","") in ins_]
                            opcoes_candidatos = [
                                f"{c.get('nome','Sem nome')} <{c.get('email','')}>"
                                for c in inscritos_cands
                            ]
                            mapa_opcao_email = {
                                f"{c.get('nome','Sem nome')} <{c.get('email','')}>": c.get("email","")
                                for c in inscritos_cands
                            }
                            mapa_email_nome = {c.get("email",""): c.get("nome","") for c in inscritos_cands}
                            st.markdown("""<div class="info-box">
                                Registre o desfecho do Seletivo e, se desejar, envie comunicação aos candidatos inscritos.
                                Use uma mensagem objetiva: resultado, próximos passos e contato do órgão.
                            </div>""", unsafe_allow_html=True)
                            with st.form(f"form_resultado_chamada_{i}"):
                                tipo_resultado = st.selectbox(
                                    "Desfecho do Seletivo",
                                    [
                                        "Selecionado(s) entre candidatos do IndicaJur",
                                        "Sem selecionados entre os inscritos",
                                        "Procedimento deserto",
                                        "Interrompido pelo recrutador",
                                    ],
                                    key=f"res_tipo_{ch_key}",
                                )
                                selecionados_opcoes = []
                                if tipo_resultado == "Selecionado(s) entre candidatos do IndicaJur":
                                    selecionados_opcoes = st.multiselect(
                                        "Candidato(s) selecionado(s)",
                                        opcoes_candidatos,
                                        key=f"res_sel_{ch_key}",
                                    )
                                motivo_resultado = st.text_area(
                                    "Registro interno do encerramento",
                                    height=90,
                                    placeholder="Ex: candidato escolhido por aderência à experiência exigida; procedimento interrompido por conveniência administrativa; ausência de candidatos compatíveis.",
                                    key=f"res_motivo_{ch_key}",
                                )
                                msg_aprovados = st.text_area(
                                    "Mensagem para selecionado(s)",
                                    value="Você foi selecionado neste Seletivo. O recrutador poderá entrar em contato para os próximos encaminhamentos.",
                                    height=90,
                                    key=f"res_msg_ap_{ch_key}",
                                )
                                msg_reprovados = st.text_area(
                                    "Mensagem para não selecionado(s) ou demais inscritos",
                                    value="Agradecemos sua participação. Neste momento, seu perfil não foi selecionado para este Seletivo. Você continuará podendo participar de novas oportunidades compatíveis no IndicaJur.",
                                    height=110,
                                    key=f"res_msg_rep_{ch_key}",
                                )
                                enviar_comunicacao = st.checkbox(
                                    "Enviar comunicação por e-mail aos candidatos inscritos",
                                    value=False,
                                    key=f"res_email_{ch_key}",
                                )
                                confirmar_resultado = st.form_submit_button("Salvar resultado e encerrar")
                            if confirmar_resultado:
                                if tipo_resultado == "Selecionado(s) entre candidatos do IndicaJur" and not selecionados_opcoes:
                                    st.error("Selecione ao menos um candidato aprovado.")
                                elif tipo_resultado != "Procedimento deserto" and not ins_:
                                    st.error("Este Seletivo não possui inscritos. Use o desfecho 'Procedimento deserto'.")
                                else:
                                    selecionados_emails = [mapa_opcao_email[o] for o in selecionados_opcoes if mapa_opcao_email.get(o)]
                                    if tipo_resultado == "Procedimento deserto":
                                        status_final = "deserto"
                                    elif tipo_resultado == "Interrompido pelo recrutador":
                                        status_final = "interrompido"
                                    else:
                                        status_final = "encerrado"
                                    payload_resultado = {
                                        "status": status_final,
                                        "resultado_tipo": tipo_resultado,
                                        "selecionados": ", ".join(selecionados_emails),
                                        "mensagem_aprovados": msg_aprovados,
                                        "mensagem_reprovados": msg_reprovados,
                                        "motivo_encerramento": motivo_resultado,
                                        "encerrado_em": datetime.now().strftime("%d/%m/%Y %H:%M"),
                                        "comunicacao_resultado": "enviada" if enviar_comunicacao else "não enviada",
                                    }
                                    tc=aba_chamadas.get_all_records()
                                    idx=next((j for j,c in enumerate(tc) if c.get("id")==ch.get("id")),None)
                                    if idx is None:
                                        st.error("Não encontrei este Seletivo na planilha.")
                                    else:
                                        try:
                                            salvar_resultado_seletivo(aba_chamadas, idx+2, payload_resultado)
                                            falhas_email = []
                                            if enviar_comunicacao:
                                                for email_inscrito in ins_:
                                                    if tipo_resultado == "Procedimento deserto":
                                                        situacao_email = "Procedimento deserto"
                                                        mensagem_email = msg_reprovados
                                                    elif tipo_resultado == "Interrompido pelo recrutador":
                                                        situacao_email = "Seletivo interrompido pelo recrutador"
                                                        mensagem_email = msg_reprovados
                                                    elif email_inscrito in selecionados_emails:
                                                        situacao_email = "Selecionado"
                                                        mensagem_email = msg_aprovados
                                                    else:
                                                        situacao_email = "Não selecionado"
                                                        mensagem_email = msg_reprovados
                                                    ok_email = email_resultado_seletivo(
                                                        email_inscrito,
                                                        mapa_email_nome.get(email_inscrito, ""),
                                                        ch.get("titulo","Seletivo"),
                                                        ch.get("orgao",""),
                                                        situacao_email,
                                                        mensagem_email,
                                                    )
                                                    if not ok_email:
                                                        falhas_email.append(email_inscrito)
                                            st.session_state[painel_resultado_key] = False
                                            if falhas_email:
                                                st.warning("Resultado salvo, mas houve falha no envio para: " + ", ".join(falhas_email))
                                            else:
                                                st.success("Resultado registrado e Seletivo encerrado.")
                                            st.rerun()
                                        except Exception as e:
                                            st.error(f"Erro ao salvar resultado. ({e})")
                    if st.session_state.get(painel_inscritos_key):
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
                                            <div style="font-size:12px;color:#5E6675;font-weight:500">✉ {cand.get('email','—')}</div>
                                        </div>
                                    </div>""",unsafe_allow_html=True)

    elif "cad_rec" not in st.session_state:
        st.markdown("""<div class="hero-card">
            <h1 class="page-title">Área do<br><em>Recrutador.</em></h1>
            <p class="page-sub">Acesse o banco de talentos jurídicos certificados</p>
        </div>""",unsafe_allow_html=True)
        tabs=st.tabs(["Entrar","Criar conta"])
        with tabs[0]:
            st.markdown('<p style="font-size:16px;font-weight:700;color:#071D49;margin:1rem 0">Acesse sua conta</p>',unsafe_allow_html=True)
            with st.form("form_login_recrutador"):
                el=st.text_input("E-mail institucional",key="le")
                sl=st.text_input("Senha",type="password",key="ls")
                entrar_rec = st.form_submit_button("Entrar →")
            if entrar_rec:
                if el and sl:
                    recs_=aba_recrutadores.get_all_records(); sh=hash_senha(sl)
                    enc=next((r for r in recs_ if r["email"]==el and r["senha"]==sh and r["status"]=="ativo"),None)
                    if enc:
                        st.session_state.rec_logado=enc
                        st.session_state.rec_email_logado=enc.get("email","")
                        st.session_state.rec_auth_token=token_recrutador(enc)
                        st.query_params["p"]="recrutador"
                        st.query_params["auth"]=st.session_state.rec_auth_token
                        st.rerun()
                    else: st.error("E-mail ou senha incorretos, ou conta ainda não aprovada.")
                else: st.error("Preencha e-mail e senha.")
            st.markdown('<p style="font-size:12px;color:#5E6675;margin-top:8px">Esqueceu a senha? <a href="?p=esqueci&tipo=recrutador" style="color:#C49A2C;font-weight:700">Recuperar acesso →</a></p>', unsafe_allow_html=True)
        with tabs[1]:
            st.markdown('<p style="font-size:15px;font-weight:700;color:#071D49;margin:1rem 0 0.5rem">Criar conta</p>',unsafe_allow_html=True)
            st.markdown('<p style="font-size:13px;color:#5E6675;font-weight:500;margin-bottom:1rem">4 etapas. Ativação após validação institucional.</p>',unsafe_allow_html=True)
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
                        try:
                            aba_recrutadores.append_row([nr,er,hash_senha(sr),dr["estado"],dr["municipio"],dr["orgao"],dr["nome_orgao"],dr["cargo"],dr["areas"],"pendente",datetime.now().strftime("%d/%m/%Y %H:%M")])
                            del st.session_state.cad_rec
                            st.success("Cadastro realizado! Aguarde a ativação."); st.balloons()
                        except Exception as e:
                            st.error(f"Erro ao finalizar cadastro. Tente novamente. ({e})")


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
                <p class="page-sub">Você foi indicado como recomendador de <strong style="color:#C49A2C">{nome_cand}</strong> no IndicaJur. Preencha a avaliação abaixo.</p>
            </div>''', unsafe_allow_html=True)

            st.markdown(f'''<div class="disclaimer-box">
                Esta avaliação é de caráter profissional e será exibida para recrutadores de Tribunais, Ministérios Públicos, Defensorias e Procuradorias. Ao enviar, você confirma que as informações prestadas são verdadeiras.
            </div>''', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

            with st.form("form_recomendacao"):
                st.markdown('<p style="font-size:15px;font-weight:700;color:#071D49;margin-bottom:1rem">Sobre o candidato</p>', unsafe_allow_html=True)

                tempo = st.selectbox("Há quanto tempo conhece o candidato? *", [
                    "Selecione...", "Menos de 1 ano", "1 a 2 anos", "2 a 5 anos", "Mais de 5 anos"
                ])
                contexto = st.selectbox("Em qual contexto profissional? *", [
                    "Selecione...", "Assessoria direta no meu gabinete",
                    "Atuação em outro órgão público", "Trabalho conjunto em projeto ou força-tarefa",
                    "Docência ou orientação acadêmica", "Outro"
                ])

                st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
                st.markdown('<p style="font-size:15px;font-weight:700;color:#071D49;margin-bottom:1rem">Avaliação profissional</p>', unsafe_allow_html=True)

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
                        try:
                            resposta = f"Tempo: {tempo} | Contexto: {contexto} | Adequação: {adequacao} | Nota: {nota}/5 | Pontos fortes: {pontos_fortes}"
                            idx_recom = next((i for i, r in enumerate(recs_recom) if r.get("token") == token_url), None)
                            if idx_recom is not None:
                                aba_recomendacoes.update_cell(idx_recom + 2, 4, "concluido")
                                aba_recomendacoes.update_cell(idx_recom + 2, 6, resposta)
                                aba_recomendacoes.update_cell(idx_recom + 2, 7, comentarios)
                            if cand_recom:
                                todos_cands2 = aba_candidatos.get_all_records()
                                idx_cand = next((i for i, c in enumerate(todos_cands2) if c.get("email") == rec_recom.get("email_candidato")), None)
                                if idx_cand is not None:
                                    aba_candidatos.update_cell(idx_cand + 2, 14, "Sim")
                            st.success("Avaliação enviada! O selo ★ Recomendado foi ativado no perfil do candidato.")
                            st.balloons()
                        except Exception as e:
                            st.error(f"Erro ao registrar avaliação. Tente novamente. ({e})")

# ── PÁGINA: ESQUECI A SENHA ──────────────────────────────────────────────────
elif pagina == "esqueci":
    tipo_param = params.get("tipo", "candidato")
    if isinstance(tipo_param, list): tipo_param = tipo_param[0]
    tipo = "recrutador" if tipo_param == "recrutador" else "candidato"
    label_tipo = "Recrutador" if tipo == "recrutador" else "Candidato"

    st.markdown(f"""<div class="hero-card">
        <h1 class="page-title">Recuperar<br><em>Acesso.</em></h1>
        <p class="page-sub">Informe seu e-mail cadastrado. Enviaremos um link para redefinir sua senha.</p>
    </div>""", unsafe_allow_html=True)

    with st.form("form_esqueci_senha"):
        tipo_sel = st.radio("Tipo de conta", ["Candidato", "Recrutador"],
                            index=1 if tipo == "recrutador" else 0, horizontal=True)
        email_rec_senha = st.text_input("Seu e-mail cadastrado", placeholder="seu@email.com")
        enviar_link = st.form_submit_button("Enviar link de redefinição →")

    if enviar_link:
        tipo_real = "recrutador" if tipo_sel == "Recrutador" else "candidato"
        if not email_rec_senha:
            st.error("Informe seu e-mail.")
        else:
            # Verificar se e-mail existe
            encontrado = False
            if tipo_real == "candidato":
                _, cand_rec = linha_candidato(email_rec_senha)
                encontrado = cand_rec is not None
            else:
                recs_todos = aba_recrutadores.get_all_records()
                encontrado = any(r.get("email","").lower() == email_rec_senha.lower() for r in recs_todos)

            # Sempre mostrar a mesma mensagem (não revelar se e-mail existe)
            if encontrado:
                token = gerar_token_senha()
                app_url = "https://jurisbank.streamlit.app"
                link = f"{app_url}/?p=redefinir&token={token}&tipo={tipo_real}"
                ok_token = salvar_token(email_rec_senha.lower(), tipo_real, token)
                ok_email = email_redefinicao(email_rec_senha, link, tipo_real)
            st.success("Se este e-mail estiver cadastrado, você receberá o link em instantes. Verifique também a pasta de spam.")
            if st.button("Voltar ao login", key="btn_voltar_login_esqueci"):
                ir("inicio" if tipo_real == "candidato" else "recrutador")

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("← Candidato", key="btn_login_cand_esqueci"):
            ir("inicio")
    with c2:
        if st.button("← Recrutador", key="btn_login_rec_esqueci"):
            ir("recrutador")


# ── PÁGINA: REDEFINIR SENHA ───────────────────────────────────────────────────
elif pagina == "redefinir":
    token_url = params.get("token", "")
    if isinstance(token_url, list): token_url = token_url[0]
    tipo_url = params.get("tipo", "candidato")
    if isinstance(tipo_url, list): tipo_url = tipo_url[0]

    if not token_url:
        st.markdown('''<div class="hero-card">
            <h1 class="page-title">Link<br><em>inválido.</em></h1>
            <p class="page-sub">Este link não é válido. Solicite um novo link de redefinição.</p>
        </div>''', unsafe_allow_html=True)
        if st.button("Solicitar novo link", key="btn_novo_link_invalido"):
            ir("esqueci")
    else:
        registro = buscar_token(token_url)
        if not registro:
            st.markdown('''<div class="hero-card">
                <h1 class="page-title">Link<br><em>expirado.</em></h1>
                <p class="page-sub">Este link expirou ou já foi utilizado. Válido por 2 horas.</p>
            </div>''', unsafe_allow_html=True)
            if st.button("Solicitar novo link", key="btn_novo_link_exp"):
                ir("esqueci")
        else:
            tipo_real = registro.get("tipo", tipo_url)
            email_real = registro.get("email", "")

            st.markdown(f"""<div class="hero-card">
                <h1 class="page-title">Nova<br><em>Senha.</em></h1>
                <p class="page-sub">Crie uma nova senha para <strong>{html_lib.escape(email_real)}</strong></p>
            </div>""", unsafe_allow_html=True)

            with st.form("form_redefinir_senha"):
                nova_senha = st.text_input("Nova senha *", type="password",
                                           help="Mínimo 6 caracteres")
                conf_senha = st.text_input("Confirmar nova senha *", type="password")
                salvar_nova = st.form_submit_button("Salvar nova senha →")

            if salvar_nova:
                if len(nova_senha) < 6:
                    st.error("A senha deve ter pelo menos 6 caracteres.")
                elif nova_senha != conf_senha:
                    st.error("As senhas não coincidem.")
                else:
                    nova_hash = hash_senha(nova_senha)
                    try:
                        if tipo_real == "candidato":
                            linha_n, _ = linha_candidato(email_real)
                            if linha_n:
                                aba_candidatos.update_cell(linha_n, CAND_COL_SENHA, nova_hash)
                            else:
                                st.error("Candidato não encontrado.")
                                st.stop()
                        else:
                            recs_todos = aba_recrutadores.get_all_records()
                            idx_r = next((i for i, r in enumerate(recs_todos)
                                          if r.get("email","").lower() == email_real.lower()), None)
                            if idx_r is not None:
                                aba_recrutadores.update_cell(idx_r + 2, 3, nova_hash)
                            else:
                                st.error("Recrutador não encontrado.")
                                st.stop()
                        invalidar_token(token_url)
                        st.success("Senha redefinida com sucesso! Faça login com sua nova senha.")
                        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
                        if st.button("Ir para o login →", key="btn_pos_redefinicao"):
                            ir("inicio" if tipo_real == "candidato" else "recrutador")
                    except Exception as e:
                        st.error(f"Erro ao salvar nova senha. Tente novamente. ({e})")


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
            ("1. Aceitação",[("p","Ao usar o IndicaJur você concorda com estes Termos e com a Política de Privacidade.")]),
            ("2. Seletivos",[("p","A publicação de um Seletivo não configura processo seletivo vinculante ou concurso público. O uso do ius indicandum é de responsabilidade exclusiva do recrutador.")]),
            ("3. Impessoalidade",[("l",["Princípio da impessoalidade (art. 37, CF/88)","Vedação ao nepotismo (SV nº 13 do STF)","Resolução CNJ nº 07/2005"])]),
            ("4. Responsabilidades",[("p","O IndicaJur não garante contratações e não se responsabiliza por decisões dos recrutadores.")]),
            ("5. Foro",[("p","Comarca de [MUNICÍPIO A PREENCHER], Estado de [ESTADO A PREENCHER].")]),
        ]
    for ts,cont in secs:
        st.markdown(f'<div class="doc-sub">{ts}</div>',unsafe_allow_html=True)
        for tp,tx in cont:
            if tp=="p": st.markdown(f'<p class="doc-body">{tx}</p>',unsafe_allow_html=True)
            elif tp=="l":
                for it in tx: st.markdown(f'<p class="doc-item">• {it}</p>',unsafe_allow_html=True)
        st.markdown('<div class="custom-divider"></div>',unsafe_allow_html=True)
    st.markdown(f'<p style="font-size:12px;color:#5E6675;font-weight:500;text-align:center">IndicaJur — Versão 1.0 — {datetime.now().strftime("%d/%m/%Y")}</p>',unsafe_allow_html=True)
