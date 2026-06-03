import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import fitz
import re
import hashlib
import secrets
import urllib.request
import json
from datetime import datetime, date

st.set_page_config(
    page_title="JurisBank",
    page_icon="âš–",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Sora:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Sora', sans-serif; color: #0d1f4e; }
[data-testid="stToolbar"] { display: none !important; }
[data-testid="stSidebarCollapsedControl"] { display: none !important; }
header[data-testid="stHeader"] { display: none !important; }
#MainMenu { display: none !important; }
[data-testid="stSidebar"] { display: none !important; }

[data-testid="stAppViewContainer"] {
    background: #eef3fe;
    min-height: 100vh;
}
.main .block-container { padding: 0 2.5rem 3rem; max-width: 1100px; background: transparent; }

[data-testid="stMarkdownContainer"],
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] span {
    color: #0d1f4e;
}
[data-testid="stMarkdownContainer"] small,
[data-testid="stCaptionContainer"],
.stCaptionContainer {
    color: #4a6080 !important;
    font-weight: 500;
}
[data-testid="stMarkdownContainer"] strong {
    color: #0d1f4e;
    font-weight: 700;
}

/* â”€â”€ Topbar â”€â”€ */
.topbar {
    display: flex; align-items: center; justify-content: space-between;
    padding: 1rem 1.5rem;
    margin: 0 -2.5rem 2rem;
    flex-wrap: wrap; gap: 12px;
    background: #0d1f4e;
    border-bottom: 2px solid rgba(200,150,12,0.3);
}
.topbar-logo { display: flex; align-items: center; gap: 10px; text-decoration: none; }
.topbar-logo-icon { width: 36px; height: 36px; background: linear-gradient(135deg,#c8960c,#f0c040); border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 18px; box-shadow: 0 2px 12px rgba(200,150,12,0.3); }
.topbar-logo-name { font-family: 'Playfair Display',serif; font-size: 18px; font-weight: 700; color: #ffffff; }
.topbar-logo-sub { font-size: 9px; color: rgba(200,150,12,0.8); font-style: italic; letter-spacing:.05em; display: block; margin-top: -2px; }
.topbar-nav { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
.topbar-nav a {
    padding: 7px 14px; border-radius: 8px;
    font-size: 13px; font-weight: 600;
    color: rgba(255,255,255,0.75); text-decoration: none;
    border: 1px solid transparent;
    transition: all 0.2s;
}
.topbar-nav a:hover { color: #ffffff; background: rgba(255,255,255,0.1); }
.topbar-nav a.active { color: #f0c040; border-color: rgba(200,150,12,0.4); background: rgba(200,150,12,0.12); }
.topbar-nav a.btn-rec {
    background: rgba(255,255,255,0.12); color: #ffffff;
    border: 1px solid rgba(255,255,255,0.2); font-weight: 700;
}
.topbar-nav a.btn-rec:hover { background: rgba(255,255,255,0.2); }
.topbar-nav a.btn-cand {
    background: linear-gradient(135deg,#c8960c,#f0c040);
    color: #0d1f4e; border: none; font-weight: 700;
}
.topbar-nav a.btn-cand:hover { opacity: 0.9; color: #0d1f4e; }

/* â”€â”€ Cards â”€â”€ */
.hero-card { background: #ffffff; border: 1.5px solid #d0dcfa; border-radius: 20px; padding: 2rem 2.5rem; margin-bottom: 1.5rem; }
.page-title { font-family: 'Playfair Display',serif; font-size: clamp(28px,4vw,42px); font-weight: 900; color: #0d1f4e; margin: 0 0 8px; letter-spacing: -1px; line-height: 1.1; }
.page-title em { font-style: normal; background: linear-gradient(135deg,#c8960c,#f0c040); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
.page-sub { font-size: 15px; color: #2a4a8a; margin: 0; font-weight: 600; }
.stats-row { display: flex; gap: 12px; margin-top: 1.5rem; flex-wrap: wrap; }
.stat-pill { background: #dce8ff; border-radius: 99px; padding: 7px 16px; font-size: 13px; font-weight: 700; color: #0d1f4e; border: 1px solid #a0bcf0; }

.cand-card { background: #ffffff; border: 1.5px solid #d0dcfa; border-radius: 16px; padding: 1.2rem 1.5rem; margin-bottom: 8px; transition: all 0.2s; }
.cand-card:hover { border-color: #4070f4; box-shadow: 0 6px 24px rgba(64,112,244,0.1); transform: translateY(-1px); }
.seletivo-card { background: #ffffff; border: 1.5px solid #d0dcfa; border-radius: 16px; padding: 1.2rem 1.5rem; margin-bottom: 10px; transition: all 0.2s; }
.seletivo-card:hover { border-color: #4070f4; box-shadow: 0 6px 24px rgba(64,112,244,0.1); }

.avatar { width: 46px; height: 46px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 14px; font-weight: 700; flex-shrink: 0; color: white; }
.cand-name { font-size: 15px; font-weight: 700; color: #0d1f4e; margin: 0 0 3px; }
.cand-sub { font-size: 12px; color: #4a6080; margin: 0; font-weight: 500; }

.badge-sim { background: #e6f4ea; color: #1a7a4a; padding: 4px 12px; border-radius: 99px; font-size: 11px; font-weight: 700; border: 1px solid #b0dfc0; }
.badge-nao { background: #fff3e8; color: #c05a1a; padding: 4px 12px; border-radius: 99px; font-size: 11px; font-weight: 700; border: 1px solid #f0c8a0; }
.badge-aberto { background: #e6f4ea; color: #1a7a4a; padding: 3px 10px; border-radius: 99px; font-size: 11px; font-weight: 700; border: 1px solid #b0dfc0; }
.badge-encerrado { background: #f4f7fe; color: #4a6080; padding: 3px 10px; border-radius: 99px; font-size: 11px; font-weight: 700; border: 1px solid #d0dcfa; }
.badge-inscrito { background: #e8effe; color: #1a3a8f; padding: 3px 10px; border-radius: 99px; font-size: 11px; font-weight: 700; border: 1px solid #b0c5f5; }
.badge-pago { background: #fff8e6; color: #b45309; padding: 3px 10px; border-radius: 99px; font-size: 11px; font-weight: 700; border: 1px solid #fde68a; }

.selo { display: inline-block; font-size: 10px; font-weight: 700; padding: 3px 10px; border-radius: 99px; margin-right: 4px; margin-top: 4px; }
.selo-verificado { background: #e8effe; color: #1a3a8f; border: 1px solid #b0c5f5; }
.selo-recomendado { background: #e6f4ea; color: #15803d; border: 1px solid #b0dfc0; }
.selo-destaque { background: #fff8e6; color: #b45309; border: 1px solid #fde68a; }
.selo-experiente { background: #f3effe; color: #6d28d9; border: 1px solid #ddd6fe; }

.metric-box { background: #ffffff; border: 1.5px solid #d0dcfa; border-radius: 14px; padding: 16px 18px; text-align: center; }
.metric-label { font-size: 11px; font-weight: 700; color: #4a6080; text-transform: uppercase; letter-spacing: .08em; margin: 0 0 6px; }
.metric-value { font-size: 24px; font-weight: 800; color: #0d1f4e; margin: 0; }

.teaser-box { background: linear-gradient(135deg,#0d1f4e,#1a3a8f); border-radius: 16px; padding: 20px 24px; text-align: center; }
.teaser-num { font-family: 'Playfair Display',serif; font-size: 36px; font-weight: 900; color: #f0c040; margin: 0; }
.teaser-label { font-size: 12px; color: rgba(255,255,255,0.65); margin: 4px 0 0; }

.profile-name { font-family: 'Playfair Display',serif; font-size: 24px; font-weight: 900; color: #0d1f4e; margin: 0 0 6px; }
.section-label { font-size: 11px; font-weight: 700; color: #1a3a8f; text-transform: uppercase; letter-spacing: .1em; margin: 1.5rem 0 0.5rem; }
.info-card { background: #f0f5ff; border: 1.5px solid #c5d5f5; border-radius: 12px; padding: 14px 18px; font-size: 14px; color: #1a3a8f; line-height: 1.6; font-weight: 500; }
.custom-divider { height: 1px; background: #e8f0fe; margin: 1.5rem 0; }
.info-box { background: #e8effe; border: 1px solid #b0c5f5; border-radius: 10px; padding: 10px 14px; font-size: 13px; color: #1a3a8f; margin-top: 8px; font-weight: 500; }
.lock-box { background: #f4f7fe; border: 1.5px solid #d0dcfa; border-radius: 12px; padding: 14px 18px; font-size: 13px; color: #4a6080; text-align: center; }
.disclaimer-box { background: #fff8e6; border: 1px solid #fde68a; border-radius: 10px; padding: 12px 16px; font-size: 12px; color: #92400e; line-height: 1.6; margin-top: 1rem; }
.aviso-pago { background: linear-gradient(135deg,#0d1f4e,#1a3a8f); border-radius: 16px; padding: 20px 24px; text-align: center; margin: 1rem 0; }

.step-bar { display: flex; gap: 8px; margin-bottom: 2rem; }
.step { flex: 1; height: 4px; border-radius: 99px; background: #d0dcfa; }
.step.active { background: linear-gradient(135deg,#c8960c,#f0c040); }
.step.done { background: #1a7a4a; }
.step-title { font-size: 13px; font-weight: 700; color: #2a4a8a; margin-bottom: 0.3rem; }
.step-desc { font-family: 'Playfair Display',serif; font-size: 22px; font-weight: 700; color: #0d1f4e; margin-bottom: 1.5rem; }

.doc-sub { font-size: 12px; font-weight: 800; color: #1a3a8f; text-transform: uppercase; letter-spacing: .08em; margin: 1.5rem 0 0.5rem; }
.doc-body { font-size: 14px; color: #1a3a8f; line-height: 1.8; margin-bottom: 0.8rem; font-weight: 500; }
.doc-item { font-size: 14px; color: #1a3a8f; line-height: 1.8; padding-left: 1rem; font-weight: 500; }

/* Planos */
.plano-card { border-radius: 16px; padding: 24px; border: 1.5px solid #d0dcfa; background: #ffffff; }
.plano-card.destaque { background: linear-gradient(135deg,#0d1f4e,#1a3a8f); border-color: transparent; }
.plano-nome { font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: .08em; margin-bottom: 8px; }
.plano-preco { font-family: 'Playfair Display',serif; font-size: 32px; font-weight: 900; margin: 0 0 4px; }
.plano-periodo { font-size: 12px; margin-bottom: 16px; }
.plano-item { font-size: 13px; padding: 4px 0; display: flex; gap: 8px; align-items: flex-start; }

/* BotÃµes */
.stButton button { background: linear-gradient(135deg,#c8960c,#f0c040) !important; color: #0d1f4e !important; border: none !important; border-radius: 10px !important; font-family: 'Sora',sans-serif !important; font-weight: 700 !important; padding: 0.6rem 2rem !important; font-size: 14px !important; transition: all 0.2s !important; }
.stButton button:hover { opacity: 0.9 !important; transform: translateY(-1px) !important; }
div[data-testid="column"]:last-child .stButton button,
div[data-testid="column"]:nth-last-child(2) .stButton button { background: #e8f0fe !important; color: #1a3a8f !important; border: 1.5px solid #c5d5f5 !important; border-radius: 10px !important; padding: 0.4rem 1rem !important; font-size: 12px !important; font-weight: 600 !important; width: 100%; }
div[data-testid="column"]:last-child .stButton button:hover,
div[data-testid="column"]:nth-last-child(2) .stButton button:hover { background: #4070f4 !important; color: white !important; border-color: #4070f4 !important; }
.stTextInput input, .stTextArea textarea { border-radius: 10px !important; border-color: #d0dcfa !important; background: #ffffff !important; color: #0d1f4e !important; font-family: 'Sora',sans-serif !important; font-size: 14px !important; font-weight: 500 !important; }
.stTextInput input::placeholder, .stTextArea textarea::placeholder { color: #4a6080 !important; opacity: 1 !important; font-weight: 500 !important; }
.stTextInput input:focus, .stTextArea textarea:focus { border-color: #4070f4 !important; box-shadow: 0 0 0 3px rgba(64,112,244,0.1) !important; }
.stSelectbox > div > div { border-radius: 10px !important; border-color: #d0dcfa !important; background: #ffffff !important; color: #0d1f4e !important; }
.stSelectbox [data-baseweb="select"] * { color: #0d1f4e !important; font-weight: 500 !important; }
.stRadio label, .stCheckbox label { color: #0d1f4e !important; font-weight: 600 !important; }
.stMultiSelect > div > div { background: #ffffff !important; border-color: #d0dcfa !important; border-radius: 10px !important; }
.stMultiSelect [data-baseweb="select"] * { color: #0d1f4e !important; font-weight: 500 !important; }
label[data-baseweb="label"] { color: #0d1f4e !important; font-weight: 600 !important; }
.stTabs [data-baseweb="tab-list"] { background: #e8f0fe !important; border-radius: 12px !important; padding: 4px !important; gap: 4px !important; }
.stTabs [data-baseweb="tab"] { background: transparent !important; color: #1a3a8f !important; border-radius: 8px !important; font-weight: 600 !important; }
.stTabs [aria-selected="true"] { background: #ffffff !important; color: #1a3a8f !important; font-weight: 700 !important; }
.stAlert [data-testid="stMarkdownContainer"],
.stAlert [data-testid="stMarkdownContainer"] p {
    color: #0d1f4e !important;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# â”€â”€ Google Sheets â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
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
        "seletivos": pl.worksheet("chamadas"),
        "interesses": pl.worksheet("interesses"),
        "recomendacoes": pl.worksheet("recomendacoes"),
    }

abas = conectar_sheets()
aba_candidatos = abas["candidatos"]
aba_recrutadores = abas["recrutadores"]
aba_seletivos = abas["seletivos"]
aba_interesses = abas["interesses"]
aba_recomendacoes = abas["recomendacoes"]

# â”€â”€ NavegaÃ§Ã£o â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
params = st.query_params
p = params.get("p", "inicio")
if isinstance(p, list): p = p[0]
if p not in ["inicio","candidatos","seletivos","cadastro","recrutador","privacidade","termos","recomendar"]:
    p = "inicio"
if "pagina" not in st.session_state or params.get("p"):
    st.session_state.pagina = p
pagina = st.session_state.pagina

# â”€â”€ Constantes â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
AVATAR_CORES = ["#1a3a8f","#2e7d5e","#7b3fa0","#c05a1a","#1a6b8a","#a04040","#3a6b2a"]
DISC_LABEL = {"D":"Dominante","I":"Influente","S":"EstÃ¡vel","C":"Conformidade"}
DISC_CORES_BADGE = {"D":"#fee2e2","I":"#fef9c3","S":"#dcfce7","C":"#eff6ff"}
DISC_TEXTO_BADGE = {"D":"#991b1b","I":"#854d0e","S":"#166534","C":"#1e3a8a"}
DISC_EXPLICACOES = {
    "D â€” Dominante":"Direto e decidido. Resolve problemas com rapidez.",
    "I â€” Influente":"Comunicativo e entusiasta. Excelente no atendimento ao pÃºblico.",
    "S â€” EstÃ¡vel":"Paciente e confiÃ¡vel. Ideal para rotinas de gabinete.",
    "C â€” Conformidade":"AnalÃ­tico e preciso. Excelente em pesquisa jurÃ­dica."
}
DISC_DETALHES = {
    "D":{"nome":"Dominante","resumo":"Direto, decidido e orientado a resultados.","pontos_fortes":"Resolve problemas com rapidez, assume responsabilidades, trabalha bem sob pressÃ£o.","no_gabinete":"Ideal para demandas que exigem agilidade e tomada de decisÃ£o rÃ¡pida.","atencao":"Pode ser impaciente com processos lentos."},
    "I":{"nome":"Influente","resumo":"Comunicativo, entusiasta e orientado a pessoas.","pontos_fortes":"Excelente no atendimento ao pÃºblico e trabalho em equipe.","no_gabinete":"Ideal para MinistÃ©rios PÃºblicos ou Defensorias com alto volume de atendimento.","atencao":"Pode ter dificuldade com tarefas repetitivas."},
    "S":{"nome":"EstÃ¡vel","resumo":"Paciente, confiÃ¡vel e orientado a processos.","pontos_fortes":"ConsistÃªncia, lealdade e capacidade de manter rotinas com qualidade.","no_gabinete":"Perfil ideal para gabinetes com rotinas estabelecidas.","atencao":"Pode ter dificuldade com mudanÃ§as repentinas."},
    "C":{"nome":"Conformidade","resumo":"AnalÃ­tico, preciso e orientado Ã  qualidade.","pontos_fortes":"AtenÃ§Ã£o aos detalhes, rigor tÃ©cnico e pesquisa jurÃ­dica.","no_gabinete":"Ideal para assessorias que demandam anÃ¡lise de processos complexos.","atencao":"Pode ser perfeccionista. Precisa de clareza nas instruÃ§Ãµes."}
}
DESCRICOES_DISC = {"D":"Dominante â€” Direto, decidido e orientado a resultados.","I":"Influente â€” Comunicativo e orientado a pessoas.","S":"EstÃ¡vel â€” Paciente e orientado a processos.","C":"Conformidade â€” AnalÃ­tico e orientado a qualidade."}
CONCURSOS = ["NÃ£o estou estudando para concurso","Juiz de Direito (TJ)","Juiz Federal (TRF)","Promotor de JustiÃ§a (MP Estadual)","Procurador da RepÃºblica (MPF)","Defensor PÃºblico Estadual","Defensor PÃºblico Federal (DPU)","Procurador do Estado (PGE)","Procurador Municipal","Delegado de PolÃ­cia","Auditor Fiscal / Receita Federal","Outro concurso jurÃ­dico"]
ESTADOS = ["AC","AL","AP","AM","BA","CE","DF","ES","GO","MA","MT","MS","MG","PA","PB","PR","PE","PI","RJ","RN","RS","RO","RR","SC","SP","SE","TO"]
ORGAOS = ["Tribunal de JustiÃ§a (TJ)","MinistÃ©rio PÃºblico (MP)","Defensoria PÃºblica","Procuradoria Geral do Estado (PGE)","Procuradoria Geral do MunicÃ­pio (PGM)","Tribunal Regional Federal (TRF)","MinistÃ©rio PÃºblico Federal (MPF)","Advocacia Geral da UniÃ£o (AGU)","Tribunal de Contas (TCE/TCU)","Outro"]
CARGOS = ["Juiz de Direito","Juiz Federal","Desembargador","Promotor de JustiÃ§a","Procurador de JustiÃ§a","Defensor PÃºblico","Procurador do Estado","Procurador Municipal","Servidor â€” RH / GestÃ£o de Pessoas","Outro"]
AREAS = ["Criminal","CÃ­vel","FamÃ­lia e SucessÃµes","ExecuÃ§Ã£o Penal","InfÃ¢ncia e Juventude","Fazenda PÃºblica","Meio Ambiente","Moralidade Administrativa","ViolÃªncia DomÃ©stica","Direito PÃºblico","Direito TributÃ¡rio","Consumidor","SaÃºde","Todas as Ã¡reas"]
REGIMES = ["Integral","Parcial","Remoto","HÃ­brido"]
FORMAS_SELECAO = ["AnÃ¡lise de currÃ­culo","AnÃ¡lise de currÃ­culo + entrevista","Entrevista","AnÃ¡lise de portfÃ³lio + entrevista","Processo simplificado"]
PERGUNTAS_DISC = [
    ("Em situaÃ§Ãµes de pressÃ£o no trabalho, vocÃª tende a:",["Tomar decisÃµes rÃ¡pidas e assumir o controle","Motivar a equipe e buscar soluÃ§Ãµes criativas","Manter a calma e seguir o processo estabelecido","Analisar os dados antes de agir"]),
    ("Quando recebe uma tarefa nova, vocÃª prefere:",["Ter autonomia total para decidir como fazer","Conversar com a equipe e trocar ideias","Entender bem o processo antes de comeÃ§ar","Ter instruÃ§Ãµes detalhadas e critÃ©rios claros"]),
    ("Em reuniÃµes, vocÃª costuma:",["Liderar a discussÃ£o e propor soluÃ§Ãµes","Animar o grupo e trazer entusiasmo","Ouvir com atenÃ§Ã£o antes de opinar","Apresentar dados e anÃ¡lises detalhadas"]),
    ("Seu ponto forte no trabalho Ã©:",["Resultados rÃ¡pidos e objetivos","Relacionamentos e comunicaÃ§Ã£o","Estabilidade e confiabilidade","PrecisÃ£o e qualidade tÃ©cnica"]),
    ("Quando hÃ¡ um conflito na equipe, vocÃª:",["Enfrenta diretamente e busca resoluÃ§Ã£o imediata","Tenta mediar com diplomacia e bom humor","Evita confrontos e busca harmonia","Analisa a situaÃ§Ã£o antes de se posicionar"]),
    ("VocÃª se sente mais motivado quando:",["Tem metas desafiadoras para superar","Trabalha com pessoas e recebe reconhecimento","Tem rotina estÃ¡vel e previsÃ­vel","Pode aprofundar conhecimento e fazer bem feito"]),
    ("Seu estilo de comunicaÃ§Ã£o Ã©:",["Direto e objetivo","Entusiasmado e expressivo","Calmo e paciente","Preciso e detalhado"]),
    ("Diante de uma mudanÃ§a repentina, vocÃª:",["Adapta rapidamente e assume o controle","VÃª como oportunidade e engaja a equipe","Precisa de tempo para se adaptar","Avalia os riscos antes de aceitar"]),
    ("No trabalho em equipe, vocÃª assume o papel de:",["LÃ­der que define rumos e cobra resultados","Motivador que mantÃ©m o clima positivo","Apoiador que garante a harmonia do grupo","Especialista que garante a qualidade tÃ©cnica"]),
    ("Quando comete um erro, vocÃª:",["Assume, corrige rapidamente e segue em frente","Conversa com alguÃ©m para processar e superar","Reflete com calma antes de agir diferente","Analisa o que deu errado para nÃ£o repetir"]),
    ("Sua maior dificuldade no trabalho Ã©:",["PaciÃªncia com processos lentos","Manter o foco em tarefas repetitivas","Lidar com mudanÃ§as repentinas","Trabalhar sem informaÃ§Ãµes suficientes"]),
    ("Como vocÃª prefere receber feedback:",["Direto e objetivo, sem rodeios","De forma encorajadora e positiva","Com calma, em conversa reservada","Com dados e exemplos concretos"]),
]
LETRAS_DISC = ["D","I","S","C"]
DISCLAIMER = "âš ï¸ O JurisBank atua exclusivamente como plataforma de aproximaÃ§Ã£o. A publicaÃ§Ã£o deste Seletivo nÃ£o configura processo seletivo vinculante, concurso pÃºblico ou compromisso de contrataÃ§Ã£o. O uso do ius indicandum Ã© de responsabilidade exclusiva do recrutador."

# â”€â”€ FunÃ§Ãµes â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def cor_avatar(n): return AVATAR_CORES[sum(ord(c) for c in n)%len(AVATAR_CORES)]
def iniciais(n):
    p=n.strip().split()
    return (p[0][0]+p[-1][0]).upper() if len(p)>=2 else n[:2].upper()
def hash_senha(s): return hashlib.sha256(s.encode()).hexdigest()
def rec_logado(): return "rec_logado" in st.session_state and st.session_state.rec_logado
def cand_logado(): return "cand_logado" in st.session_state and st.session_state.cand_logado
def gerar_id(): return f"sel_{datetime.now().strftime('%Y%m%d%H%M%S')}"
def sel_aberto(s):
    if s.get("status","").lower()!="aberto": return False
    try: return datetime.strptime(s.get("prazo",""),"%d/%m/%Y").date()>=date.today()
    except: return True
def inscritos_sel(s):
    r=str(s.get("inscritos","")).strip()
    return [e.strip() for e in r.split(",") if e.strip()] if r else []
def ir(p):
    st.session_state.pagina=p
    st.query_params["p"]=p
    st.rerun()

def enviar_email(destinatario, assunto, corpo_html):
    try:
        api_key = st.secrets["resend"]["api_key"]
        remetente = st.secrets["resend"]["remetente"]
        payload = json.dumps({"from":remetente,"to":[destinatario],"subject":assunto,"html":corpo_html}).encode("utf-8")
        req = urllib.request.Request("https://api.resend.com/emails",data=payload,headers={"Authorization":f"Bearer {api_key}","Content-Type":"application/json"},method="POST")
        with urllib.request.urlopen(req) as r: return r.status==200
    except: return False

def email_recomendador(nome_cand, email_rec, link):
    assunto = f"JurisBank â€” {nome_cand} solicitou sua avaliaÃ§Ã£o"
    corpo = f"""<div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto">
        <div style="background:linear-gradient(135deg,#0d1f4e,#1a3a8f);padding:32px;text-align:center;border-radius:12px 12px 0 0">
            <h1 style="color:#ffffff;font-size:22px;margin:0">JurisBank</h1>
            <p style="color:rgba(255,255,255,0.6);font-size:12px;margin:4px 0 0;font-style:italic">ius indicandum</p>
        </div>
        <div style="padding:32px;background:#f4f6fc;border-radius:0 0 12px 12px">
            <h2 style="color:#0d1f4e;font-size:20px;margin:0 0 12px">SolicitaÃ§Ã£o de avaliaÃ§Ã£o</h2>
            <p style="color:#4a5568;font-size:15px;line-height:1.7;margin:0 0 20px">O profissional <strong>{nome_cand}</strong> indicou vocÃª como recomendador no JurisBank e solicita que vocÃª preencha uma avaliaÃ§Ã£o do seu perfil profissional.</p>
            <div style="text-align:center;margin:28px 0">
                <a href="{link}" style="display:inline-block;padding:14px 36px;background:linear-gradient(135deg,#c8960c,#f0c040);color:#0d1f4e;font-weight:700;font-size:15px;border-radius:10px;text-decoration:none">Preencher avaliaÃ§Ã£o â†’</a>
            </div>
            <p style="color:#4a6080;font-size:12px;border-top:1px solid #d0dcfa;padding-top:16px">Este link Ã© exclusivo e de uso Ãºnico. JurisBank â€” plataforma de aproximaÃ§Ã£o entre profissionais do Direito e Ã³rgÃ£os do sistema de justiÃ§a.</p>
        </div>
    </div>"""
    return enviar_email(email_rec, assunto, corpo)

def extrair_pdf(f):
    doc=fitz.open(stream=f.read(),filetype="pdf")
    return "".join(p.get_text() for p in doc)

def extrair_campos(txt):
    c={"nome":"","email":"","oab":"NÃ£o","experiencia_orgaos":"","sistemas":"","pos_graduacao":"","resumo":""}
    ls=txt.split("\n"); tc=txt.lower()
    em=re.findall(r'[\w\.\-]+@[\w\.\-]+\.\w+',txt)
    if em: c["email"]=em[0]
    if "oab" in tc or "ordem dos advogados" in tc: c["oab"]="Sim"
    sis=["Eproc","SAJ","SIG","SEEU","SISP","APOIA","GAIA","Pandora","SIMBA"]
    enc=[s for s in sis if s.lower() in tc]
    if enc: c["sistemas"]=", ".join(enc)
    for l in ls:
        l=l.strip()
        if any(x in l for x in ["PÃ³s","pÃ³s","Especializ","Mestrado","Doutorado"]):
            if len(l)>10 and not c["pos_graduacao"]: c["pos_graduacao"]=l
    om={"MPSC":"MPSC","TJSC":"TJSC","Defensoria":"Defensoria","Procuradoria":"Procuradoria","MinistÃ©rio PÃºblico":"MP","Tribunal de JustiÃ§a":"TJ","AGU":"AGU","PGE":"PGE"}
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
    return {"verificado":"Sim" if oab=="Sim" else "NÃ£o","recomendado":"Sim" if carta else "NÃ£o","destaque":"Sim" if aval else "NÃ£o","experiente":"Sim" if anos>=2 else "NÃ£o"}

def html_selos(c):
    h=""
    if c.get("selo_verificado")=="Sim": h+='<span class="selo selo-verificado">âœ“ Verificado</span>'
    if c.get("selo_recomendado")=="Sim": h+='<span class="selo selo-recomendado">â˜… Recomendado</span>'
    if c.get("selo_destaque")=="Sim": h+='<span class="selo selo-destaque">â—† Destaque</span>'
    if c.get("selo_experiente")=="Sim": h+='<span class="selo selo-experiente">â— Experiente</span>'
    return h

def html_disc(c):
    d=c.get("disc","")
    if not d: return ""
    return f'<span style="font-size:10px;font-weight:700;padding:2px 8px;border-radius:99px;background:{DISC_CORES_BADGE.get(d,"#eff6ff")};color:{DISC_TEXTO_BADGE.get(d,"#1e3a8a")};margin-left:4px">{d} {DISC_LABEL.get(d,"")}</span>'

def html_conc(c):
    if c.get("concurso") and c.get("concurso")!="NÃ£o estou estudando para concurso":
        return '<span style="font-size:10px;font-weight:700;padding:2px 8px;border-radius:99px;background:#fff8e6;color:#b45309;margin-left:4px;border:1px solid #fde68a">ðŸ“š Concursando</span>'
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
    cb=DISC_CORES_BADGE.get(d,"#f4f7fe"); tb=DISC_TEXTO_BADGE.get(d,"#1e3a8a"); det=DISC_DETALHES.get(d,{})
    return f"""<div class="info-card" style="background:{cb};border-color:{cb}">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px">
            <span style="font-weight:800;color:{tb};font-size:22px">{d}</span>
            <span style="font-weight:700;color:{tb};font-size:15px">{det.get('nome','')}</span>
        </div>
        <p style="color:{tb};font-size:13px;font-weight:600;margin:0 0 8px">{det.get('resumo','')}</p>
        <p style="color:#2a4a8a;font-size:12px;margin:0 0 4px"><strong style="color:{tb}">Pontos fortes:</strong> {det.get('pontos_fortes','')}</p>
        <p style="color:#2a4a8a;font-size:12px;margin:0 0 4px"><strong style="color:{tb}">No gabinete:</strong> {det.get('no_gabinete','')}</p>
        <p style="color:#2a4a8a;font-size:12px;margin:0"><strong style="color:{tb}">AtenÃ§Ã£o:</strong> {det.get('atencao','')}</p>
    </div>"""

def modal_planos():
    with st.expander("ðŸ’° Ver planos e preÃ§os", expanded=st.session_state.get("ver_planos", False)):
        st.markdown('<p style="font-family:\'Playfair Display\',serif;font-size:22px;font-weight:900;color:#0d1f4e;margin-bottom:1.5rem">Planos e preÃ§os</p>', unsafe_allow_html=True)

        st.markdown('<p style="font-size:13px;font-weight:700;color:#4070f4;text-transform:uppercase;letter-spacing:.08em;margin-bottom:1rem">Para Candidatos</p>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""<div class="plano-card">
                <p class="plano-nome" style="color:#2a4a8a">Gratuito</p>
                <p class="plano-preco" style="color:#0d1f4e">R$ 0</p>
                <p class="plano-periodo" style="color:#4a6080">para sempre</p>
                <div class="plano-item" style="color:#2a4a8a">âœ… Cadastro completo com selos</div>
                <div class="plano-item" style="color:#2a4a8a">âœ… Aparecer no banco de talentos</div>
                <div class="plano-item" style="color:#2a4a8a">âœ… Perfil DISC</div>
                <div class="plano-item" style="color:#2a4a8a">âœ… Ver Seletivos abertos</div>
                <div class="plano-item" style="color:#4a6080">âŒ InscriÃ§Ã£o em Seletivos</div>
                <div class="plano-item" style="color:#4a6080">âŒ Destaque no perfil</div>
            </div>""", unsafe_allow_html=True)
        with col2:
            st.markdown("""<div class="plano-card destaque">
                <p class="plano-nome" style="color:#f0c040">Ativo</p>
                <p class="plano-preco" style="color:#ffffff">R$ 29,90</p>
                <p class="plano-periodo" style="color:rgba(255,255,255,0.6)">/mÃªs</p>
                <div class="plano-item" style="color:rgba(255,255,255,0.9)">âœ… Tudo do gratuito</div>
                <div class="plano-item" style="color:rgba(255,255,255,0.9)">âœ… InscriÃ§Ã£o em Seletivos</div>
                <div class="plano-item" style="color:rgba(255,255,255,0.9)">âœ… Destaque no perfil</div>
                <div class="plano-item" style="color:rgba(255,255,255,0.9)">âœ… NotificaÃ§Ãµes de Seletivos</div>
            </div>""", unsafe_allow_html=True)

        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
        st.markdown('<p style="font-size:13px;font-weight:700;color:#4070f4;text-transform:uppercase;letter-spacing:.08em;margin-bottom:1rem">Para Recrutadores â€” Pay-per-use</p>', unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        produtos = [
            ("ðŸ” 1 perfil completo", "R$ 19,90", "Nome, e-mail, resumo e DISC"),
            ("ðŸ” 5 perfis", "R$ 79,90", "Economia de 20%"),
            ("ðŸ” 10 perfis", "R$ 139,90", "Economia de 30%"),
        ]
        for col, (nome, preco, desc) in zip([col1,col2,col3], produtos):
            with col:
                st.markdown(f"""<div class="plano-card" style="text-align:center">
                    <p style="font-size:14px;font-weight:700;color:#0d1f4e;margin-bottom:4px">{nome}</p>
                    <p style="font-family:'Playfair Display',serif;font-size:24px;font-weight:900;color:#0d1f4e;margin:0">{preco}</p>
                    <p style="font-size:12px;color:#4a6080;margin-top:4px">{desc}</p>
                </div>""", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""<div class="plano-card" style="text-align:center">
                <p style="font-size:14px;font-weight:700;color:#0d1f4e;margin-bottom:4px">ðŸ“¢ 1 Seletivo (30 dias)</p>
                <p style="font-family:'Playfair Display',serif;font-size:24px;font-weight:900;color:#0d1f4e;margin:0">R$ 89,90</p>
                <p style="font-size:12px;color:#4a6080;margin-top:4px">PublicaÃ§Ã£o + painel de inscritos</p>
            </div>""", unsafe_allow_html=True)
        with col2:
            st.markdown("""<div class="plano-card destaque" style="text-align:center">
                <p style="font-size:14px;font-weight:700;color:#f0c040;margin-bottom:4px">âš¡ 10 perfis + 1 Seletivo</p>
                <p style="font-family:'Playfair Display',serif;font-size:24px;font-weight:900;color:#ffffff;margin:0">R$ 199,90</p>
                <p style="font-size:12px;color:rgba(255,255,255,0.6);margin-top:4px">Melhor custo-benefÃ­cio</p>
            </div>""", unsafe_allow_html=True)

        st.markdown('<p style="font-size:11px;color:#4a6080;text-align:center;margin-top:1rem">Pagamentos em breve. Cadastre-se agora gratuitamente.</p>', unsafe_allow_html=True)

# â”€â”€ TOPBAR â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def render_topbar():
    nav = '<div class="topbar"><a class="topbar-logo" href="https://lcatolico.github.io/jurisbank/" target="_blank"><div class="topbar-logo-icon">âš–</div><div><span class="topbar-logo-name">JurisBank</span><span class="topbar-logo-sub">ius indicandum</span></div></a><div class="topbar-nav">'

    if rec_logado():
        rec = st.session_state.rec_logado
        nav += f'<a href="?p=recrutador" class="{"active" if pagina=="recrutador" else ""}">ðŸ› {rec["nome"].split()[0]}</a>'
        nav += '<a href="?p=seletivos" class="' + ("active" if pagina=="seletivos" else "") + '">ðŸ“¢ Seletivos</a>'
    elif cand_logado():
        cand = st.session_state.cand_logado
        nav += f'<a href="?p=inicio" class="{"active" if pagina=="inicio" else ""}">ðŸ‘¤ {cand["nome"].split()[0]}</a>'
        nav += '<a href="?p=candidatos" class="' + ("active" if pagina=="candidatos" else "") + '">ðŸ‘¥ Candidatos</a>'
        nav += '<a href="?p=seletivos" class="' + ("active" if pagina=="seletivos" else "") + '">ðŸ“¢ Seletivos</a>'
    else:
        nav += '<a href="?p=candidatos" class="' + ("active" if pagina=="candidatos" else "") + '">ðŸ‘¥ Candidatos</a>'
        nav += '<a href="?p=seletivos" class="' + ("active" if pagina=="seletivos" else "") + '">ðŸ“¢ Seletivos</a>'
        nav += '<a href="?p=recrutador" class="btn-rec">ðŸ” Recrutador</a>'
        nav += '<a href="?p=cadastro" class="btn-cand">Cadastrar â†’</a>'

    nav += '</div></div>'
    st.markdown(nav, unsafe_allow_html=True)

render_topbar()

# â”€â”€ PÃGINA: INÃCIO / DASHBOARD VISITANTE â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
if pagina == "inicio":
    dados = aba_candidatos.get_all_records()
    seletivos = aba_seletivos.get_all_records()
    total_cands = len(dados)
    total_disp = sum(1 for c in dados if c.get("disponibilidade")=="Sim")
    total_cert = sum(1 for c in dados if any(c.get(f"selo_{s}")=="Sim" for s in ["verificado","recomendado","destaque","experiente"]))
    total_sel = sum(1 for s in seletivos if sel_aberto(s))

    if cand_logado():
        # Dashboard candidato ativo
        cand = st.session_state.cand_logado
        st.markdown(f"""<div class="hero-card">
            <h1 class="page-title">OlÃ¡, <em>{cand['nome'].split()[0]}!</em></h1>
            <p class="page-sub">Seu perfil estÃ¡ ativo no JurisBank</p>
            <div class="stats-row">
                <div class="stat-pill">ðŸ“¢ {total_sel} Seletivos abertos</div>
                <div class="stat-pill">ðŸ‘¥ {total_cands} candidatos no banco</div>
            </div>
        </div>""", unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f'<div class="metric-box"><p class="metric-label">Ãrea</p><p class="metric-value" style="font-size:16px">{cand.get("area","â€”")}</p></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metric-box"><p class="metric-label">DisponÃ­vel</p><p class="metric-value" style="font-size:16px">{cand.get("disponibilidade","â€”")}</p></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="metric-box"><p class="metric-label">Perfil DISC</p><p class="metric-value" style="font-size:16px">{cand.get("disc","â€”")}</p></div>', unsafe_allow_html=True)

        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("ðŸ“¢ Ver Seletivos", use_container_width=True): ir("seletivos")
        with col2:
            if st.button("ðŸ‘¥ Ver candidatos", use_container_width=True): ir("candidatos")
        with col3:
            if st.button("Sair da conta", use_container_width=True):
                del st.session_state.cand_logado; st.rerun()

        st.markdown('<p class="section-label">Meus selos</p>', unsafe_allow_html=True)
        st.markdown(f'<div class="info-card">{html_selos(cand) or "Nenhum selo ainda. Complete seu cadastro para receber selos."}</div>', unsafe_allow_html=True)

        if cand.get("disc"):
            st.markdown('<p class="section-label">Meu perfil DISC</p>', unsafe_allow_html=True)
            st.markdown(render_disc(cand["disc"]), unsafe_allow_html=True)

    else:
        # Dashboard visitante â€” teaser
        st.markdown(f"""<div class="hero-card">
            <h1 class="page-title">Banco de Talentos<br><em>JurÃ­dicos.</em></h1>
            <p class="page-sub">Profissionais certificados para assessoria em Tribunais, MinistÃ©rios PÃºblicos, Procuradorias e Defensorias</p>
        </div>""", unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f'<div class="teaser-box"><p class="teaser-num">{total_cands}</p><p class="teaser-label">Profissionais cadastrados</p></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="teaser-box"><p class="teaser-num">{total_disp}</p><p class="teaser-label">DisponÃ­veis agora</p></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="teaser-box"><p class="teaser-num">{total_cert}</p><p class="teaser-label">Perfis certificados</p></div>', unsafe_allow_html=True)
        with col4:
            st.markdown(f'<div class="teaser-box"><p class="teaser-num">{total_sel}</p><p class="teaser-label">Seletivos abertos</p></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([2,2,2])
        with col1:
            if st.button("ðŸ“„ Cadastrar agora â€” Ã© grÃ¡tis", use_container_width=True): ir("cadastro")
        with col2:
            if st.button("ðŸ”‘ JÃ¡ tenho cadastro", use_container_width=True):
                st.session_state["login_cand"] = True; st.rerun()
        with col3:
            if st.button("ðŸ’° Ver planos", use_container_width=True):
                st.session_state["ver_planos"] = not st.session_state.get("ver_planos", False); st.rerun()

        if st.session_state.get("ver_planos"):
            modal_planos()

        if st.session_state.get("login_cand"):
            st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
            st.markdown('<p style="font-size:15px;font-weight:700;color:#0d1f4e;margin-bottom:1rem">Acessar minha conta</p>', unsafe_allow_html=True)
            em = st.text_input("Seu e-mail cadastrado", key="em_login_cand")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Entrar â†’", key="btn_login_cand"):
                    tc = aba_candidatos.get_all_records()
                    cf = next((c for c in tc if c.get("email","").lower()==em.lower()), None)
                    if cf: st.session_state.cand_logado=cf; st.session_state["login_cand"]=False; st.rerun()
                    else: st.error("E-mail nÃ£o encontrado.")
            with col2:
                if st.button("Cancelar", key="btn_canc_cand"):
                    st.session_state["login_cand"]=False; st.rerun()

        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
        st.markdown('<p style="font-size:15px;font-weight:700;color:#0d1f4e;margin-bottom:0.5rem">Receba avisos de novos Seletivos</p>', unsafe_allow_html=True)
        st.markdown('<p style="font-size:13px;color:#4a6080;margin-bottom:1rem">Deixe seu e-mail. Quando surgir um Seletivo na sua Ã¡rea, vocÃª Ã© o primeiro a saber.</p>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1: ei = st.text_input("Seu e-mail", key="ei_home")
        with col2: ai = st.multiselect("Ãreas", AREAS, key="ai_home")
        with col3: sti = st.multiselect("Estados", ESTADOS, key="sti_home")
        if st.button("Quero receber avisos", key="bint_home"):
            if not ei or not ai: st.error("Preencha e-mail e Ã¡rea.")
            else:
                aba_interesses.append_row([ei,", ".join(ai),", ".join(sti),datetime.now().strftime("%d/%m/%Y")])
                st.success("Pronto! VocÃª serÃ¡ avisado quando surgir um Seletivo compatÃ­vel.")

# â”€â”€ PÃGINA: CANDIDATOS â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
elif pagina == "candidatos":
    dados = aba_candidatos.get_all_records()
    if "cand_sel" not in st.session_state: st.session_state.cand_sel = None

    if st.session_state.cand_sel:
        c = st.session_state.cand_sel; cor = cor_avatar(c["nome"])
        if st.button("â† Voltar"): st.session_state.cand_sel=None; st.rerun()

        st.markdown(f"""<div class="hero-card">
            <div style="display:flex;align-items:center;gap:16px">
                <div class="avatar" style="width:60px;height:60px;border-radius:14px;background:{cor};font-size:20px">{iniciais(c['nome'])}</div>
                <div>
                    <div class="profile-name">{c['nome']}</div>
                    <div style="font-size:13px;color:#2a4a8a;margin-bottom:6px">{c.get('formacao','â€”')} Â· {c.get('instituicao','â€”')}</div>
                    <div>{html_selos(c)}</div>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

        col1,col2,col3,col4=st.columns(4)
        for col,lb,vl in [(col1,"Ãrea",c.get("area","â€”")),(col2,"OAB",c.get("oab","â€”")),(col3,"DisponÃ­vel",c.get("disponibilidade","â€”")),(col4,"Ã“rgÃ£os",c.get("experiencia_orgaos","â€”") or "â€”")]:
            with col: st.markdown(f'<div class="metric-box"><p class="metric-label">{lb}</p><p class="metric-value" style="font-size:16px">{vl}</p></div>',unsafe_allow_html=True)

        if c.get("disc"):
            st.markdown('<p class="section-label">Perfil DISC</p>',unsafe_allow_html=True)
            st.markdown(render_disc(c["disc"]),unsafe_allow_html=True)

        if c.get("resumo"):
            st.markdown('<p class="section-label">Resumo</p>',unsafe_allow_html=True)
            if rec_logado():
                st.markdown(f'<div class="info-card">{c["resumo"]}</div>',unsafe_allow_html=True)
            else:
                prev=c["resumo"][:150]+"..." if len(c["resumo"])>150 else c["resumo"]
                st.markdown(f'<div class="info-card">{prev}<br><br><span style="font-size:12px;color:#4070f4">ðŸ” Resumo completo disponÃ­vel para recrutadores.</span></div>',unsafe_allow_html=True)

        st.markdown('<p class="section-label">Contato</p>',unsafe_allow_html=True)
        if rec_logado():
            # Verificar se recrutador aceitou o termo de responsabilidade
            if not st.session_state.get("termo_aceito"):
                st.markdown("""<div class="disclaimer-box">
                    <strong>Termo de responsabilidade</strong><br>
                    Ao acessar os dados de contato deste candidato, vocÃª confirma que utilizarÃ¡ as informaÃ§Ãµes exclusivamente para fins de seleÃ§Ã£o profissional para cargo de livre nomeaÃ§Ã£o no seu Ã³rgÃ£o, em conformidade com os princÃ­pios da impessoalidade e vedaÃ§Ã£o ao nepotismo (SV nÂº 13 do STF e ResoluÃ§Ã£o CNJ nÂº 07/2005).
                </div>""", unsafe_allow_html=True)
                if st.button("âœ… Aceito e quero ver os dados de contato"):
                    st.session_state["termo_aceito"] = True; st.rerun()
            else:
                st.markdown(f'<div class="info-card">âœ‰ {c.get("email","â€”")}</div>',unsafe_allow_html=True)
        else:
            st.markdown('<div class="lock-box">ðŸ” DisponÃ­vel apenas para recrutadores aprovados.</div>',unsafe_allow_html=True)
    else:
        total=len(dados); disp=sum(1 for c in dados if c.get("disponibilidade")=="Sim")
        cert=sum(1 for c in dados if any(c.get(f"selo_{s}")=="Sim" for s in ["verificado","recomendado","destaque","experiente"]))

        st.markdown(f"""<div class="hero-card">
            <h1 class="page-title">Banco de Talentos<br><em>JurÃ­dicos.</em></h1>
            <p class="page-sub">Profissionais certificados para assessoria em Tribunais, MinistÃ©rios PÃºblicos, Procuradorias e Defensorias</p>
            <div class="stats-row">
                <div class="stat-pill">âš– {total} cadastrados</div>
                <div class="stat-pill">âœ“ {disp} disponÃ­veis</div>
                <div class="stat-pill">â˜… {cert} certificados</div>
            </div>
        </div>""", unsafe_allow_html=True)

        col1,col2,col3=st.columns(3)
        with col1: busca=st.text_input("Buscar por nome",placeholder="Nome...")
        with col2:
            ar=["Todas"]+sorted(set(c["area"] for c in dados if c.get("area")))
            asel=st.selectbox("Ãrea",ar)
        with col3: fsel=st.selectbox("Selo",["Todos","Verificado","Recomendado","Destaque","Experiente"])

        cf=dados
        if busca: cf=[c for c in cf if busca.lower() in c["nome"].lower()]
        if asel!="Todas": cf=[c for c in cf if c["area"]==asel]
        if fsel!="Todos":
            cm={"Verificado":"selo_verificado","Recomendado":"selo_recomendado","Destaque":"selo_destaque","Experiente":"selo_experiente"}
            cf=[c for c in cf if c.get(cm[fsel])=="Sim"]

        st.markdown(f'<p style="font-size:13px;color:#4a6080;margin-bottom:1rem">{len(cf)} candidato(s)</p>',unsafe_allow_html=True)

        for i,cand in enumerate(cf):
            cor=cor_avatar(cand["nome"]); dsp=cand.get("disponibilidade","NÃ£o")
            bdg='<span class="badge-sim">â— DisponÃ­vel</span>' if dsp=="Sim" else '<span class="badge-nao">â— IndisponÃ­vel</span>'
            cc,cb=st.columns([11,2])
            with cc:
                st.markdown(f"""<div class="cand-card">
                    <div style="display:flex;align-items:center;justify-content:space-between;gap:12px">
                        <div style="display:flex;align-items:center;gap:12px;flex:1">
                            <div class="avatar" style="background:{cor}">{iniciais(cand['nome'])}</div>
                            <div>
                                <p class="cand-name">{cand['nome']}</p>
                                <p class="cand-sub">{cand.get('formacao','â€”')} Â· {cand.get('instituicao','â€”')} Â· {cand.get('area','â€”')}</p>
                                <div style="margin-top:4px">{html_selos(cand)}{html_disc(cand)}{html_conc(cand)}</div>
                            </div>
                        </div>
                        <div>{bdg}</div>
                    </div>
                </div>""",unsafe_allow_html=True)
            with cb:
                st.write("")
                if st.button("Ver â†’",key=f"b{i}"):
                    st.session_state.cand_sel=cand; st.rerun()

# â”€â”€ PÃGINA: SELETIVOS â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
elif pagina == "seletivos":
    todas = aba_seletivos.get_all_records()

    st.markdown("""<div class="hero-card">
        <h1 class="page-title">Seletivos<br><em>Abertos.</em></h1>
        <p class="page-sub">Vagas de cargos de livre nomeaÃ§Ã£o em Tribunais, MinistÃ©rios PÃºblicos, Defensorias e Procuradorias</p>
    </div>""", unsafe_allow_html=True)
    st.markdown(f'<div class="disclaimer-box">{DISCLAIMER}</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    if not cand_logado() and not rec_logado():
        st.markdown("""<div class="aviso-pago">
            <p style="font-size:16px;font-weight:700;color:#f0c040;margin:0 0 8px">ðŸ” InscriÃ§Ã£o disponÃ­vel para candidatos ativos</p>
            <p style="font-size:13px;color:rgba(255,255,255,0.7);margin:0 0 16px">Cadastre-se gratuitamente e assine o plano Ativo para se inscrever nos Seletivos.</p>
        </div>""", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("ðŸ“„ Cadastrar agora", use_container_width=True): ir("cadastro")
        with col2:
            if st.button("ðŸ”‘ JÃ¡ tenho cadastro", use_container_width=True):
                st.session_state["login_cand_sel"]=True; st.rerun()

        if st.session_state.get("login_cand_sel"):
            st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
            em=st.text_input("Seu e-mail cadastrado",key="em_sel")
            if st.button("Entrar â†’",key="btn_sel"):
                tc=aba_candidatos.get_all_records()
                cf=next((c for c in tc if c.get("email","").lower()==em.lower()),None)
                if cf: st.session_state.cand_logado=cf; st.session_state["login_cand_sel"]=False; st.rerun()
                else: st.error("E-mail nÃ£o encontrado.")

    if cand_logado():
        cand=st.session_state.cand_logado
        col1,col2=st.columns([8,2])
        with col1: st.markdown(f'<div class="info-box">ðŸ‘¤ {cand["nome"]} â€” <span style="font-size:11px">candidato ativo</span></div>',unsafe_allow_html=True)
        with col2:
            if st.button("Sair",key="sc"): del st.session_state.cand_logado; st.rerun()

    col1,col2,col3=st.columns(3)
    with col1: fa=st.selectbox("Ãrea",["Todas"]+AREAS,key="fa")
    with col2: fe=st.selectbox("Estado",["Todos"]+ESTADOS,key="fe")
    with col3: fs=st.selectbox("Status",["Abertos","Todos","Encerrados"],key="fs")

    chf=todas
    if fa!="Todas": chf=[s for s in chf if s.get("area")==fa]
    if fe!="Todos": chf=[s for s in chf if s.get("estado")==fe]
    if fs=="Abertos": chf=[s for s in chf if sel_aberto(s)]
    elif fs=="Encerrados": chf=[s for s in chf if not sel_aberto(s)]

    st.markdown(f'<p style="font-size:13px;color:#4a6080;margin-bottom:1rem">{len(chf)} seletivo(s)</p>',unsafe_allow_html=True)

    for i,sel in enumerate(chf):
        ab=sel_aberto(sel); ins_=inscritos_sel(sel); n=len(ins_)
        sb='<span class="badge-aberto">â— Aberto</span>' if ab else '<span class="badge-encerrado">â— Encerrado</span>'
        ja=cand_logado() and st.session_state.cand_logado.get("email","") in ins_

        st.markdown(f"""<div class="seletivo-card">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:12px">
                <div style="flex:1">
                    <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">
                        {sb}
                        <span style="font-size:11px;color:#4a6080">ðŸ“… {sel.get('prazo','â€”')}</span>
                        <span style="font-size:11px;color:#4a6080">ðŸ‘¥ {n} inscrito(s)</span>
                    </div>
                    <p style="font-size:16px;font-weight:700;color:#0d1f4e;margin:0 0 4px">{sel.get('titulo','â€”')}</p>
                    <p style="font-size:13px;color:#2a4a8a;margin:0 0 8px">{sel.get('orgao','â€”')} Â· {sel.get('municipio','â€”')}/{sel.get('estado','â€”')}</p>
                    <div style="display:flex;gap:8px;flex-wrap:wrap">
                        <span style="font-size:11px;font-weight:600;padding:2px 10px;border-radius:99px;background:#e8effe;color:#1a3a8f">{sel.get('area','â€”')}</span>
                        <span style="font-size:11px;font-weight:600;padding:2px 10px;border-radius:99px;background:#f3effe;color:#6d28d9">{sel.get('regime','â€”')}</span>
                        <span style="font-size:11px;font-weight:600;padding:2px 10px;border-radius:99px;background:#e6f4ea;color:#15803d">{sel.get('vagas','â€”')} vaga(s)</span>
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
                if st.button("Inscrever-se â†’",key=f"i{i}"):
                    st.session_state[f"ci{i}"]=True; st.rerun()
            elif ja: st.markdown('<span class="badge-inscrito">âœ“ Inscrito</span>',unsafe_allow_html=True)
            elif not cand_logado() and ab:
                st.markdown('<span class="badge-pago">ðŸ” Plano Ativo</span>',unsafe_allow_html=True)

        if st.session_state.get(f"ci{i}"):
            st.markdown(f'<div class="info-card" style="margin-top:8px"><strong style="color:#0d1f4e">Inscrever em: {sel.get("titulo","")}</strong></div>',unsafe_allow_html=True)
            cons=st.checkbox("Autorizo o compartilhamento do meu perfil com o recrutador desta vaga, nos termos da LGPD.",key=f"cs{i}")
            ca,cx=st.columns(2)
            with ca:
                if st.button("Confirmar",key=f"cf{i}"):
                    if not cons: st.error("Autorize o compartilhamento para continuar.")
                    else:
                        ec=st.session_state.cand_logado.get("email",""); ia=inscritos_sel(sel)
                        if ec not in ia:
                            ia.append(ec)
                            tc=aba_seletivos.get_all_records()
                            idx=next((j for j,c in enumerate(tc) if c.get("id")==sel.get("id")),None)
                            if idx is not None: aba_seletivos.update_cell(idx+2,16,", ".join(ia))
                        del st.session_state[f"ci{i}"]
                        st.success("InscriÃ§Ã£o realizada!"); st.rerun()
            with cx:
                if st.button("Cancelar",key=f"cx{i}"):
                    del st.session_state[f"ci{i}"]; st.rerun()

        if st.session_state.get(f"vd{i}"):
            with st.expander("Detalhes",expanded=True):
                c1,c2,c3=st.columns(3)
                with c1: st.markdown(f'<div class="metric-box"><p class="metric-label">RemuneraÃ§Ã£o</p><p class="metric-value" style="font-size:13px">{sel.get("remuneracao","â€”")}</p></div>',unsafe_allow_html=True)
                with c2: st.markdown(f'<div class="metric-box"><p class="metric-label">Regime</p><p class="metric-value" style="font-size:13px">{sel.get("regime","â€”")}</p></div>',unsafe_allow_html=True)
                with c3: st.markdown(f'<div class="metric-box"><p class="metric-label">SeleÃ§Ã£o</p><p class="metric-value" style="font-size:13px">{sel.get("forma_selecao","â€”")}</p></div>',unsafe_allow_html=True)
                if sel.get("requisitos"):
                    st.markdown('<p class="section-label">Requisitos</p>',unsafe_allow_html=True)
                    st.markdown(f'<div class="info-card">{sel["requisitos"]}</div>',unsafe_allow_html=True)
                st.markdown(f'<div class="disclaimer-box">{DISCLAIMER}</div>',unsafe_allow_html=True)

# â”€â”€ PÃGINA: CADASTRO â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
elif pagina == "cadastro":
    if "et" not in st.session_state: st.session_state.et=1
    if "campos" not in st.session_state: st.session_state.campos={}
    if "dc" not in st.session_state: st.session_state.dc={}
    et=st.session_state.et
    ts=[("Seus dados\nprofissionais.","Upload do currÃ­culo ou preenchimento manual"),("CertificaÃ§Ã£o e\nreferÃªncias.","Documentos que geram selos"),("Perfil\ncomportamental.","12 perguntas â€” 3 minutos")]
    tt,ts_=ts[et-1]
    st.markdown(f'<div class="hero-card"><h1 class="page-title">{tt}</h1><p class="page-sub">{ts_}</p></div>',unsafe_allow_html=True)
    st.markdown(barra(et,3),unsafe_allow_html=True)
    st.markdown(f'<p class="step-title">Etapa {et} de 3</p>',unsafe_allow_html=True)

    if et==1:
        pdf=st.file_uploader("Upload do currÃ­culo em PDF (opcional)",type="pdf")
        if pdf and not st.session_state.campos:
            with st.spinner("Extraindo..."): st.session_state.campos=extrair_campos(extrair_pdf(pdf))
            st.rerun()
        if pdf is None: st.session_state.campos={}
        campos=st.session_state.campos
        st.markdown('<div class="custom-divider"></div>',unsafe_allow_html=True)
        c1,c2=st.columns(2)
        with c1: nome=st.text_input("Nome completo *",value=campos.get("nome",""))
        with c2: email=st.text_input("E-mail *",value=campos.get("email",""))
        c1,c2,c3=st.columns(3)
        with c1: form=st.selectbox("FormaÃ§Ã£o *",["Bacharel em Direito","PÃ³s-graduado em Direito","Mestre em Direito","Doutor em Direito"])
        with c2: inst=st.text_input("InstituiÃ§Ã£o *")
        with c3: area=st.selectbox("Ãrea *",["Tribunal","MP","Procuradoria","Defensoria","TCU/TCE"])
        c1,c2,c3=st.columns(3)
        with c1: oab=st.radio("OAB ativa?",["Sim","NÃ£o"],index=0 if campos.get("oab")=="Sim" else 1,horizontal=True)
        with c2: anos=st.number_input("Anos em Ã³rgÃ£o pÃºblico",min_value=0,max_value=40,value=0)
        with c3: disp=st.radio("DisponÃ­vel?",["Sim","NÃ£o"],horizontal=True)
        exp=st.text_input("Ã“rgÃ£os de atuaÃ§Ã£o",value=campos.get("experiencia_orgaos",""))
        sis=st.text_input("Sistemas dominados",value=campos.get("sistemas",""))
        pos=st.text_input("PÃ³s-graduaÃ§Ã£o",value=campos.get("pos_graduacao",""))
        res=st.text_area("Resumo profissional",value=campos.get("resumo",""),height=100)
        st.markdown('<div class="custom-divider"></div>',unsafe_allow_html=True)
        conc=st.selectbox("Estudando para algum concurso?",CONCURSOS)
        st.markdown('<div class="custom-divider"></div>',unsafe_allow_html=True)
        cons=st.checkbox("Li e aceito a PolÃ­tica de Privacidade e os Termos de Uso. Consinto com o tratamento dos meus dados nos termos da LGPD (Lei nÂº 13.709/2018).")
        st.markdown("<br>",unsafe_allow_html=True)
        if st.button("PrÃ³ximo â†’"):
            if not nome or not email or not inst: st.error("Preencha nome, e-mail e instituiÃ§Ã£o.")
            elif not cons: st.error("Aceite os Termos para continuar.")
            else:
                st.session_state.dc.update({"nome":nome,"email":email,"formacao":form,"instituicao":inst,"area":area,"oab":oab,"anos_experiencia":anos,"disponibilidade":disp,"experiencia":exp,"sistemas":sis,"pos":pos,"resumo":res,"concurso":conc})
                st.session_state.et=2; st.rerun()

    elif et==2:
        c1,c2=st.columns(2)
        with c1:
            st.markdown('<p style="font-weight:600;color:#b45309;margin-bottom:4px">â˜… Carta de recomendaÃ§Ã£o</p>',unsafe_allow_html=True)
            st.markdown('<p style="font-size:12px;color:#4a6080;margin-bottom:8px">De um Juiz, Promotor, Defensor ou Procurador ativo</p>',unsafe_allow_html=True)
            carta=st.file_uploader("",type="pdf",key="carta",label_visibility="collapsed")
        with c2:
            st.markdown('<p style="font-weight:600;color:#b45309;margin-bottom:4px">â—† AvaliaÃ§Ã£o de desempenho</p>',unsafe_allow_html=True)
            st.markdown('<p style="font-size:12px;color:#4a6080;margin-bottom:8px">AvaliaÃ§Ã£o formal emitida pelo Ã³rgÃ£o</p>',unsafe_allow_html=True)
            aval=st.file_uploader("",type="pdf",key="aval",label_visibility="collapsed")
        st.markdown('<div class="custom-divider"></div>',unsafe_allow_html=True)
        st.markdown('<p style="font-weight:600;color:#2a4a8a;margin-bottom:4px">E-mail do recomendador</p>',unsafe_allow_html=True)
        er=st.text_input("",placeholder="nome@mpsc.mp.br",key="er",label_visibility="collapsed")
        dv=["mpsc.mp.br","tjsc.jus.br","sc.def.br","pge.sc.gov.br","trf4.jus.br","jfsc.jus.br","mpf.mp.br","agu.gov.br"]
        if er and "@" in er:
            if er.split("@")[-1] in dv: st.markdown('<div class="info-box">âœ“ E-mail institucional reconhecido.</div>',unsafe_allow_html=True)
            else: st.warning("DomÃ­nio nÃ£o reconhecido.")

        if er and "@" in er:
            st.markdown('<div class="custom-divider"></div>',unsafe_allow_html=True)
            st.markdown('<p style="font-weight:600;color:#2a4a8a;margin-bottom:4px">Solicitar avaliaÃ§Ã£o direta na plataforma</p>',unsafe_allow_html=True)
            st.markdown('<p style="font-size:12px;color:#4a6080;margin-bottom:8px">O recomendador receberÃ¡ um link exclusivo para preencher uma avaliaÃ§Ã£o do seu perfil diretamente no JurisBank.</p>',unsafe_allow_html=True)
            if st.button("Gerar link de avaliaÃ§Ã£o â†’",key="gerar_link"):
                email_cand_temp=st.session_state.dc.get("email","")
                if not email_cand_temp: st.error("Preencha seu e-mail na etapa anterior primeiro.")
                else:
                    token=secrets.token_urlsafe(24)
                    aba_recomendacoes.append_row([token,email_cand_temp,er,"pendente",datetime.now().strftime("%d/%m/%Y %H:%M"),"",""])
                    link=f"https://jurisbank.streamlit.app/?p=recomendar&token={token}"
                    nome_cand_temp=st.session_state.dc.get("nome","candidato")
                    enviado=email_recomendador(nome_cand_temp,er,link)
                    if enviado:
                        st.markdown(f'<div class="info-box">âœ“ E-mail enviado para <strong>{er}</strong>!</div>',unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="info-box">âœ“ Link gerado! Compartilhe manualmente:<br><strong style="font-size:12px;word-break:break-all">{link}</strong></div>',unsafe_allow_html=True)
                    st.session_state.dc["token_recomendacao"]=token
                    st.info("Quando o recomendador preencher, o selo â˜… Recomendado serÃ¡ ativado automaticamente.")

        d=st.session_state.dc; sp=[]
        if d.get("oab")=="Sim": sp.append("âœ“ Verificado")
        if carta: sp.append("â˜… Recomendado")
        if aval: sp.append("â—† Destaque")
        if d.get("anos_experiencia",0)>=2: sp.append("â— Experiente")
        if sp:
            st.markdown('<div class="custom-divider"></div>',unsafe_allow_html=True)
            st.markdown('<p style="font-size:13px;font-weight:600;color:#0d1f4e">Selos:</p>',unsafe_allow_html=True)
            st.markdown(" ".join([f'<span class="selo selo-verificado">{s}</span>' for s in sp]),unsafe_allow_html=True)

        st.markdown("<br>",unsafe_allow_html=True)
        c1,c2=st.columns(2)
        with c1:
            if st.button("â† Voltar"): st.session_state.et=1; st.rerun()
        with c2:
            if st.button("PrÃ³ximo â†’"):
                st.session_state.dc.update({"carta":carta is not None,"avaliacao":aval is not None,"email_ref":er})
                st.session_state.et=3; st.rerun()

    elif et==3:
        st.markdown('<p style="font-size:14px;color:#4a6080;margin-bottom:1.5rem">NÃ£o hÃ¡ respostas certas ou erradas.</p>',unsafe_allow_html=True)
        rd=[]
        for j,(perg,ops) in enumerate(PERGUNTAS_DISC):
            r=st.radio(f"**{j+1}.** {perg}",ops,key=f"dq{j}",index=None)
            rd.append(r)
        st.markdown("<br>",unsafe_allow_html=True)
        c1,c2=st.columns(2)
        with c1:
            if st.button("â† Voltar"): st.session_state.et=2; st.rerun()
        with c2:
            if st.button("Cadastrar no JurisBank â†’"):
                if None in rd: st.error("Responda todas as 12 perguntas.")
                else:
                    d=st.session_state.dc
                    selos=calc_selos(d["oab"],d["anos_experiencia"],d.get("carta",False),d.get("avaliacao",False))
                    pd_,_,desc=calc_disc(rd)
                    aba_candidatos.append_row([d["nome"],d["email"],d["formacao"],d["instituicao"],d["area"],d["disponibilidade"],d["oab"],d["experiencia"],d["sistemas"],d["pos"],d["resumo"],d.get("email_ref",""),selos["verificado"],selos["recomendado"],selos["destaque"],selos["experiente"],pd_,d.get("concurso","NÃ£o estou estudando para concurso")])
                    st.session_state.et=1; st.session_state.campos={}; st.session_state.dc={}
                    st.success("Bem-vindo ao JurisBank!")
                    st.markdown(f'<div class="info-box">Perfil: <strong>{pd_} â€” {desc}</strong></div>',unsafe_allow_html=True)
                    st.balloons()

# â”€â”€ PÃGINA: RECRUTADOR â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
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
        msel=[s for s in aba_seletivos.get_all_records() if s.get("email_recrutador")==rec["email"]]

        st.markdown(f"""<div class="hero-card">
            <h1 class="page-title">OlÃ¡, <em>{rec['nome'].split()[0]}!</em></h1>
            <p class="page-sub">{ra.get('nome_orgao',rec.get('orgao',''))} Â· {rec.get('estado','')}</p>
            <div class="stats-row">
                <div class="stat-pill">âš– {len(dados)} candidatos</div>
                <div class="stat-pill">â˜… {len(favs)} favoritos</div>
                <div class="stat-pill">ðŸ“¢ {len(msel)} seletivos</div>
            </div>
        </div>""", unsafe_allow_html=True)

        c_sair,_=st.columns([2,8])
        with c_sair:
            if st.button("Sair da conta"): del st.session_state.rec_logado; ir("recrutador")

        tabs=st.tabs(["ðŸ” Busca","ðŸ“¢ Seletivos","â˜… Favoritos"])

        with tabs[0]:
            c1,c2,c3=st.columns(3)
            with c1: busca=st.text_input("Nome",placeholder="Buscar...")
            with c2:
                ad=["Todas"]+sorted(set(c["area"] for c in dados if c.get("area")))
                asel=st.selectbox("Ãrea",ad)
            with c3: dsel=st.selectbox("Disponibilidade",["Todos","DisponÃ­vel","IndisponÃ­vel"])
            c1,c2,c3,c4,c5,c6=st.columns(6)
            with c1: osel=st.selectbox("OAB",["Todos","Sim","NÃ£o"])
            with c2: ssel=st.selectbox("Selo",["Todos","Verificado","Recomendado","Destaque","Experiente"])
            with c3:
                dsc=st.selectbox("DISC",["Todos","D â€” Dominante","I â€” Influente","S â€” EstÃ¡vel","C â€” Conformidade"])
                if dsc!="Todos": st.markdown(f'<div class="info-box">{DISC_EXPLICACOES.get(dsc,"")}</div>',unsafe_allow_html=True)
            with c4: csel=st.selectbox("Concurso",["Todos","Concursando","NÃ£o concursando"])
            with c5: sisel=st.text_input("Sistema",placeholder="Ex: Eproc")
            with c6: emin=st.number_input("Exp. mÃ­n.",min_value=0,max_value=20,value=0)

            fi=dados
            if busca: fi=[c for c in fi if busca.lower() in c["nome"].lower()]
            if asel!="Todas": fi=[c for c in fi if c.get("area")==asel]
            if dsel!="Todos":
                v="Sim" if dsel=="DisponÃ­vel" else "NÃ£o"; fi=[c for c in fi if c.get("disponibilidade")==v]
            if osel!="Todos": fi=[c for c in fi if c.get("oab")==osel]
            if ssel!="Todos":
                cm={"Verificado":"selo_verificado","Recomendado":"selo_recomendado","Destaque":"selo_destaque","Experiente":"selo_experiente"}
                fi=[c for c in fi if c.get(cm[ssel])=="Sim"]
            if dsc!="Todos": fi=[c for c in fi if c.get("disc")==dsc[0]]
            if csel=="Concursando": fi=[c for c in fi if c.get("concurso") and c.get("concurso")!="NÃ£o estou estudando para concurso"]
            elif csel=="NÃ£o concursando": fi=[c for c in fi if not c.get("concurso") or c.get("concurso")=="NÃ£o estou estudando para concurso"]
            if sisel: fi=[c for c in fi if sisel.lower() in str(c.get("sistemas","")).lower()]

            st.markdown(f'<p style="font-size:13px;color:#4a6080;margin:1rem 0 0.5rem">{len(fi)} candidato(s)</p>',unsafe_allow_html=True)

            for i,cand in enumerate(fi):
                cor=cor_avatar(cand["nome"]); dc=cand.get("disponibilidade","NÃ£o")
                bdg='<span class="badge-sim">â— DisponÃ­vel</span>' if dc=="Sim" else '<span class="badge-nao">â— IndisponÃ­vel</span>'
                ec=cand.get("email",""); ifav=ec in favs; fi_i="â˜…" if ifav else "â˜†"
                with st.container():
                    st.markdown(f"""<div class="cand-card">
                        <div style="display:flex;align-items:center;justify-content:space-between;gap:12px">
                            <div style="display:flex;align-items:center;gap:12px;flex:1">
                                <div class="avatar" style="background:{cor}">{iniciais(cand['nome'])}</div>
                                <div>
                                    <p class="cand-name">{cand['nome']}</p>
                                    <p class="cand-sub">{cand.get('formacao','â€”')} Â· {cand.get('instituicao','â€”')} Â· {cand.get('area','â€”')}</p>
                                    <div style="margin-top:4px">{html_selos(cand)}{html_disc(cand)}{html_conc(cand)}</div>
                                </div>
                            </div>
                            <div>{bdg}</div>
                        </div>
                    </div>""",unsafe_allow_html=True)
                    ca,cb,cc=st.columns([6,2,2])
                    with cb:
                        if st.button(f"{fi_i} Fav",key=f"fv{i}"):
                            if ifav: favs.remove(ec)
                            else: favs.append(ec)
                            aba_recrutadores.update_cell(idx_r+2,12,", ".join(favs))
                            st.session_state.rec_logado=aba_recrutadores.get_all_records()[idx_r]; st.rerun()
                    with cc:
                        if st.button("Ver â†’",key=f"rb{i}"):
                            st.session_state.cr=cand
                            st.session_state["termo_aceito"]=False
                            st.rerun()

                if ec in anots: st.markdown(f'<div class="info-card" style="margin-top:-6px;margin-bottom:8px;font-size:12px">ðŸ“ {anots[ec]}</div>',unsafe_allow_html=True)

                if st.session_state.get("cr")==cand:
                    with st.expander("Perfil completo",expanded=True):
                        c1,c2,c3=st.columns(3)
                        for cl,lb,vl in [(c1,"OAB",cand.get("oab","â€”")),(c2,"Ã“rgÃ£os",cand.get("experiencia_orgaos","â€”") or "â€”"),(c3,"Sistemas",cand.get("sistemas","â€”") or "â€”")]:
                            with cl: st.markdown(f'<div class="metric-box"><p class="metric-label">{lb}</p><p class="metric-value" style="font-size:12px">{vl}</p></div>',unsafe_allow_html=True)
                        if cand.get("disc"): st.markdown(render_disc(cand["disc"]),unsafe_allow_html=True)
                        if cand.get("resumo"): st.markdown(f'<div class="info-card" style="margin-top:1rem">{cand["resumo"]}</div>',unsafe_allow_html=True)

                        # Termo de responsabilidade antes de mostrar e-mail
                        if not st.session_state.get("termo_aceito"):
                            st.markdown("""<div class="disclaimer-box">
                                <strong>Termo de responsabilidade</strong><br>
                                Ao acessar os dados de contato, vocÃª confirma que utilizarÃ¡ as informaÃ§Ãµes exclusivamente para fins de seleÃ§Ã£o profissional, em conformidade com os princÃ­pios de impessoalidade e vedaÃ§Ã£o ao nepotismo.
                            </div>""", unsafe_allow_html=True)
                            if st.button("âœ… Aceito â€” ver dados de contato", key=f"termo_{i}"):
                                st.session_state["termo_aceito"]=True; st.rerun()
                        else:
                            st.markdown(f'<div class="info-card" style="margin-top:0.5rem">âœ‰ {cand.get("email","â€”")}</div>',unsafe_allow_html=True)

                        na=anots.get(ec,""); nn=st.text_area("",value=na,height=70,key=f"nt{i}",placeholder="AnotaÃ§Ã£o privada...")
                        cs_,cf_=st.columns(2)
                        with cs_:
                            if st.button("Salvar",key=f"sv{i}"):
                                anots[ec]=nn
                                aba_recrutadores.update_cell(idx_r+2,13,"|".join([f"{k}::{v}" for k,v in anots.items()]))
                                st.success("Salvo!"); st.rerun()
                        with cf_:
                            if st.button("Fechar",key=f"fc{i}"):
                                del st.session_state["cr"]; st.rerun()

        with tabs[1]:
            ch_col,btn_col=st.columns([8,3])
            with ch_col: st.markdown('<p style="font-size:15px;font-weight:700;color:#0d1f4e">Meus Seletivos</p>',unsafe_allow_html=True)
            with btn_col:
                if st.button("+ Novo Seletivo",key="nsel"):
                    st.session_state["criar_sel"]=True; st.rerun()

            if st.session_state.get("criar_sel"):
                with st.expander("Novo Seletivo",expanded=True):
                    st.markdown(f'<div class="disclaimer-box">{DISCLAIMER}</div>',unsafe_allow_html=True)
                    st.markdown("<br>",unsafe_allow_html=True)
                    tsel=st.text_input("TÃ­tulo da vaga *",placeholder="Ex: Assessor JurÃ­dico â€” 3Âª Promotoria")
                    c1,c2=st.columns(2)
                    with c1: osel_=st.text_input("Nome do Ã³rgÃ£o *",value=ra.get("nome_orgao",""))
                    with c2: tosel=st.selectbox("Tipo de Ã³rgÃ£o *",["Selecione..."]+ORGAOS)
                    c1,c2,c3=st.columns(3)
                    with c1: asel_=st.selectbox("Ãrea *",["Selecione..."]+AREAS)
                    with c2: esel=st.selectbox("Estado *",["Selecione..."]+ESTADOS,index=ESTADOS.index(rec.get("estado","SC"))+1 if rec.get("estado","") in ESTADOS else 0)
                    with c3: msel_=st.text_input("MunicÃ­pio *",value=ra.get("municipio",""))
                    rsel=st.text_area("Requisitos *",height=80)
                    c1,c2,c3=st.columns(3)
                    with c1: remsel=st.text_input("RemuneraÃ§Ã£o *",placeholder="Ex: R$ 4.500,00")
                    with c2: regsel=st.selectbox("Regime *",["Selecione..."]+REGIMES)
                    with c3: vsel=st.number_input("Vagas *",min_value=1,max_value=20,value=1)
                    c1,c2=st.columns(2)
                    with c1: fssel=st.selectbox("Forma de seleÃ§Ã£o *",["Selecione..."]+FORMAS_SELECAO)
                    with c2: prsel=st.date_input("Prazo *",min_value=date.today())
                    st.markdown("<br>",unsafe_allow_html=True)
                    c1,c2=st.columns(2)
                    with c1:
                        if st.button("Cancelar",key="csel"): del st.session_state["criar_sel"]; st.rerun()
                    with c2:
                        if st.button("Publicar â†’",key="psel"):
                            ok=all([tsel,osel_,tosel!="Selecione...",asel_!="Selecione...",esel!="Selecione...",msel_,rsel,remsel,regsel!="Selecione...",fssel!="Selecione..."])
                            if not ok: st.error("Preencha todos os campos.")
                            else:
                                aba_seletivos.append_row([gerar_id(),tsel,osel_,tosel,asel_,esel,msel_,rsel,remsel,regsel,fssel,str(vsel),prsel.strftime("%d/%m/%Y"),"aberto",rec["email"],"",datetime.now().strftime("%d/%m/%Y")])
                                del st.session_state["criar_sel"]; st.success("Seletivo publicado!"); st.rerun()

            if not msel: st.info("Nenhum Seletivo publicado ainda.")
            else:
                for i,sel in enumerate(msel):
                    ab=sel_aberto(sel); ins_=inscritos_sel(sel); n=len(ins_)
                    sb='<span class="badge-aberto">â— Aberto</span>' if ab else '<span class="badge-encerrado">â— Encerrado</span>'
                    st.markdown(f"""<div class="seletivo-card">
                        <div style="display:flex;justify-content:space-between;align-items:center">
                            <div>
                                <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px">{sb}<span style="font-size:11px;color:#4a6080">ðŸ“… {sel.get('prazo','â€”')}</span></div>
                                <p style="font-size:15px;font-weight:700;color:#0d1f4e;margin:0 0 2px">{sel.get('titulo','â€”')}</p>
                                <p style="font-size:12px;color:#2a4a8a;margin:0">{sel.get('municipio','â€”')}/{sel.get('estado','â€”')} Â· {sel.get('area','â€”')}</p>
                            </div>
                            <div style="text-align:right">
                                <p style="font-family:'Playfair Display',serif;font-size:28px;font-weight:900;color:#c8960c;margin:0">{n}</p>
                                <p style="font-size:11px;color:#4a6080;margin:0">inscrito(s)</p>
                            </div>
                        </div>
                    </div>""",unsafe_allow_html=True)
                    cv,ce=st.columns([8,3])
                    with cv:
                        if st.button("Ver inscritos",key=f"vi{i}"):
                            st.session_state[f"vi{i}"]=not st.session_state.get(f"vi{i}",False); st.rerun()
                    with ce:
                        if ab:
                            if st.button("Encerrar",key=f"enc{i}"):
                                tc=aba_seletivos.get_all_records()
                                idx=next((j for j,c in enumerate(tc) if c.get("id")==sel.get("id")),None)
                                if idx is not None: aba_seletivos.update_cell(idx+2,14,"encerrado")
                                st.success("Encerrado."); st.rerun()
                    if st.session_state.get(f"vi{i}"):
                        with st.expander("Painel de inscritos",expanded=True):
                            if not ins_: st.info("Nenhum inscrito.")
                            else:
                                tc=aba_candidatos.get_all_records()
                                id_=[c for c in tc if c.get("email","") in ins_]
                                c1,c2,c3=st.columns(3)
                                with c1: st.markdown(f'<div class="metric-box"><p class="metric-label">Total</p><p class="metric-value">{len(id_)}</p></div>',unsafe_allow_html=True)
                                with c2: st.markdown(f'<div class="metric-box"><p class="metric-label">Com OAB</p><p class="metric-value">{sum(1 for c in id_ if c.get("oab")=="Sim")}</p></div>',unsafe_allow_html=True)
                                with c3: st.markdown(f'<div class="metric-box"><p class="metric-label">DisponÃ­veis</p><p class="metric-value">{sum(1 for c in id_ if c.get("disponibilidade")=="Sim")}</p></div>',unsafe_allow_html=True)
                                dc_={}
                                for c in id_:
                                    d=c.get("disc","")
                                    if d: dc_[d]=dc_.get(d,0)+1
                                if dc_:
                                    st.markdown('<p class="section-label">DISC</p>',unsafe_allow_html=True)
                                    cols=st.columns(4)
                                    for di,l in enumerate(["D","I","S","C"]):
                                        with cols[di]: st.markdown(f'<div class="metric-box" style="background:{DISC_CORES_BADGE.get(l,"#f4f7fe")}"><p class="metric-label" style="color:{DISC_TEXTO_BADGE.get(l,"#1e3a8a")}">{DISC_LABEL.get(l,"")}</p><p class="metric-value" style="color:{DISC_TEXTO_BADGE.get(l,"#1e3a8a")}">{dc_.get(l,0)}</p></div>',unsafe_allow_html=True)
                                st.markdown('<p class="section-label">Perfis</p>',unsafe_allow_html=True)
                                for cand in id_:
                                    cor=cor_avatar(cand["nome"])
                                    st.markdown(f"""<div class="cand-card" style="margin-bottom:8px">
                                        <div style="display:flex;align-items:center;gap:12px">
                                            <div class="avatar" style="background:{cor}">{iniciais(cand['nome'])}</div>
                                            <div style="flex:1">
                                                <p class="cand-name">{cand['nome']}</p>
                                                <p class="cand-sub">{cand.get('formacao','â€”')} Â· {cand.get('area','â€”')}</p>
                                                <div style="margin-top:4px">{html_selos(cand)}{html_disc(cand)}</div>
                                            </div>
                                            <div style="font-size:12px;color:#2a4a8a">âœ‰ {cand.get('email','â€”')}</div>
                                        </div>
                                    </div>""",unsafe_allow_html=True)

        with tabs[2]:
            fd=[c for c in dados if c.get("email","") in favs]
            if not fd: st.info("Nenhum favorito ainda.")
            else:
                for i,cand in enumerate(fd):
                    cor=cor_avatar(cand["nome"]); ec=cand.get("email",""); nt=anots.get(ec,"")
                    st.markdown(f"""<div class="cand-card">
                        <div style="display:flex;align-items:center;gap:12px">
                            <div class="avatar" style="background:{cor}">{iniciais(cand['nome'])}</div>
                            <div style="flex:1">
                                <p class="cand-name">{cand['nome']}</p>
                                <p class="cand-sub">{cand.get('formacao','â€”')} Â· {cand.get('area','â€”')}</p>
                                {html_selos(cand)}
                                {'<p style="font-size:11px;color:#4a6080;margin-top:4px">ðŸ“ '+nt+'</p>' if nt else ''}
                            </div>
                            <div>{'<span class="badge-sim">â— DisponÃ­vel</span>' if cand.get('disponibilidade')=='Sim' else '<span class="badge-nao">â— IndisponÃ­vel</span>'}</div>
                        </div>
                    </div>""",unsafe_allow_html=True)
                    if st.button("âœ• Remover",key=f"rf{i}"):
                        favs.remove(ec); aba_recrutadores.update_cell(idx_r+2,12,", ".join(favs)); st.rerun()

    elif "cad_rec" not in st.session_state:
        st.markdown("""<div class="hero-card">
            <h1 class="page-title">Ãrea do<br><em>Recrutador.</em></h1>
            <p class="page-sub">Acesse o banco de talentos jurÃ­dicos certificados</p>
        </div>""",unsafe_allow_html=True)
        tabs=st.tabs(["Entrar","Criar conta"])
        with tabs[0]:
            st.markdown('<p style="font-size:16px;font-weight:700;color:#0d1f4e;margin:1rem 0">Acesse sua conta</p>',unsafe_allow_html=True)
            el=st.text_input("E-mail institucional",key="le")
            sl=st.text_input("Senha",type="password",key="ls")
            if st.button("Entrar â†’",key="bl"):
                if el and sl:
                    recs_=aba_recrutadores.get_all_records(); sh=hash_senha(sl)
                    enc=next((r for r in recs_ if r["email"]==el and r["senha"]==sh and r["status"]=="ativo"),None)
                    if enc: st.session_state.rec_logado=enc; st.rerun()
                    else: st.error("E-mail ou senha incorretos, ou conta ainda nÃ£o aprovada.")
                else: st.error("Preencha e-mail e senha.")
        with tabs[1]:
            st.markdown('<p style="font-size:15px;font-weight:700;color:#0d1f4e;margin:1rem 0 0.5rem">Criar conta</p>',unsafe_allow_html=True)
            st.markdown('<p style="font-size:13px;color:#4a6080;margin-bottom:1rem">4 etapas. AtivaÃ§Ã£o apÃ³s validaÃ§Ã£o institucional.</p>',unsafe_allow_html=True)
            if st.button("ComeÃ§ar â†’",key="bc"):
                st.session_state.cad_rec={"etapa":1}; st.rerun()
    else:
        et=st.session_state.cad_rec.get("etapa",1)
        st.markdown(barra(et,4),unsafe_allow_html=True)
        if et==1:
            st.markdown('<p class="step-title">Etapa 1 de 4</p>',unsafe_allow_html=True)
            st.markdown('<p class="step-desc">Onde vocÃª atua?</p>',unsafe_allow_html=True)
            est=st.selectbox("Estado *",["Selecione..."]+ESTADOS)
            mun=st.text_input("MunicÃ­pio *",placeholder="Ex: FlorianÃ³polis")
            st.markdown("<br>",unsafe_allow_html=True)
            if st.button("PrÃ³ximo â†’"):
                if est=="Selecione..." or not mun: st.error("Preencha todos os campos.")
                else:
                    st.session_state.cad_rec["estado"]=est; st.session_state.cad_rec["municipio"]=mun
                    st.session_state.cad_rec["etapa"]=2; st.rerun()
        elif et==2:
            st.markdown('<p class="step-title">Etapa 2 de 4</p>',unsafe_allow_html=True)
            st.markdown('<p class="step-desc">Qual Ã© o seu Ã³rgÃ£o?</p>',unsafe_allow_html=True)
            org=st.selectbox("Tipo de Ã³rgÃ£o *",["Selecione..."]+ORGAOS)
            nom=st.text_input("Nome do Ã³rgÃ£o *",placeholder="Ex: MPSC â€” 3Âª Promotoria")
            st.markdown("<br>",unsafe_allow_html=True)
            c1,c2=st.columns(2)
            with c1:
                if st.button("â† Voltar"): st.session_state.cad_rec["etapa"]=1; st.rerun()
            with c2:
                if st.button("PrÃ³ximo â†’"):
                    if org=="Selecione..." or not nom: st.error("Preencha todos os campos.")
                    else:
                        st.session_state.cad_rec["orgao"]=org; st.session_state.cad_rec["nome_orgao"]=nom
                        st.session_state.cad_rec["etapa"]=3; st.rerun()
        elif et==3:
            st.markdown('<p class="step-title">Etapa 3 de 4</p>',unsafe_allow_html=True)
            st.markdown('<p class="step-desc">Seu perfil</p>',unsafe_allow_html=True)
            car=st.selectbox("Cargo *",["Selecione..."]+CARGOS)
            ars=st.multiselect("Ãreas *",AREAS)
            st.markdown("<br>",unsafe_allow_html=True)
            c1,c2=st.columns(2)
            with c1:
                if st.button("â† Voltar"): st.session_state.cad_rec["etapa"]=2; st.rerun()
            with c2:
                if st.button("PrÃ³ximo â†’"):
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
                if er.split("@")[-1] in dv: st.markdown('<div class="info-box">âœ“ E-mail institucional reconhecido.</div>',unsafe_allow_html=True)
                else: st.warning("DomÃ­nio nÃ£o reconhecido. ValidaÃ§Ã£o manual.")
            sr=st.text_input("Senha *",type="password"); sc=st.text_input("Confirmar senha *",type="password")
            st.markdown('<div class="custom-divider"></div>',unsafe_allow_html=True)
            cr=st.checkbox("Li e aceito a PolÃ­tica de Privacidade e os Termos de Uso. Comprometo-me a usar os dados apenas para fins de seleÃ§Ã£o, nos termos da LGPD.")
            st.markdown("<br>",unsafe_allow_html=True)
            c1,c2=st.columns(2)
            with c1:
                if st.button("â† Voltar"): st.session_state.cad_rec["etapa"]=3; st.rerun()
            with c2:
                if st.button("Finalizar â†’"):
                    if not nr or not er or not sr: st.error("Preencha todos os campos.")
                    elif sr!=sc: st.error("Senhas nÃ£o coincidem.")
                    elif len(sr)<6: st.error("MÃ­nimo 6 caracteres.")
                    elif not cr: st.error("Aceite os Termos para continuar.")
                    else:
                        dr=st.session_state.cad_rec
                        aba_recrutadores.append_row([nr,er,hash_senha(sr),dr["estado"],dr["municipio"],dr["orgao"],dr["nome_orgao"],dr["cargo"],dr["areas"],"pendente",datetime.now().strftime("%d/%m/%Y %H:%M")])
                        del st.session_state.cad_rec
                        st.success("Cadastro realizado! Aguarde a ativaÃ§Ã£o."); st.balloons()

# â”€â”€ PÃGINA: AVALIAÃ‡ÃƒO DO RECOMENDADOR â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
elif pagina == "recomendar":
    token_url = st.query_params.get("token","")
    if isinstance(token_url,list): token_url=token_url[0]

    if not token_url:
        st.markdown('<div class="hero-card"><h1 class="page-title">Link<br><em>invÃ¡lido.</em></h1></div>',unsafe_allow_html=True)
    else:
        recs_recom=aba_recomendacoes.get_all_records()
        rec_recom=next((r for r in recs_recom if r.get("token")==token_url),None)
        if not rec_recom:
            st.markdown('<div class="hero-card"><h1 class="page-title">Link<br><em>nÃ£o encontrado.</em></h1></div>',unsafe_allow_html=True)
        elif rec_recom.get("status")=="concluido":
            st.markdown('<div class="hero-card"><h1 class="page-title">AvaliaÃ§Ã£o<br><em>jÃ¡ realizada.</em></h1><p class="page-sub">Obrigado pela sua contribuiÃ§Ã£o.</p></div>',unsafe_allow_html=True)
        else:
            todos_cands=aba_candidatos.get_all_records()
            cand_recom=next((c for c in todos_cands if c.get("email")==rec_recom.get("email_candidato")),None)
            nome_cand=cand_recom["nome"] if cand_recom else rec_recom.get("email_candidato","candidato")

            st.markdown(f'<div class="hero-card"><h1 class="page-title">AvaliaÃ§Ã£o de<br><em>RecomendaÃ§Ã£o.</em></h1><p class="page-sub">VocÃª foi indicado como recomendador de <strong>{nome_cand}</strong> no JurisBank.</p></div>',unsafe_allow_html=True)
            st.markdown('<div class="disclaimer-box">Esta avaliaÃ§Ã£o Ã© de carÃ¡ter profissional e serÃ¡ exibida para recrutadores. Ao enviar, vocÃª confirma que as informaÃ§Ãµes sÃ£o verdadeiras.</div>',unsafe_allow_html=True)
            st.markdown("<br>",unsafe_allow_html=True)

            with st.form("form_rec"):
                tempo=st.selectbox("HÃ¡ quanto tempo conhece o candidato? *",["Selecione...","Menos de 1 ano","1 a 2 anos","2 a 5 anos","Mais de 5 anos"])
                contexto=st.selectbox("Em qual contexto profissional? *",["Selecione...","Assessoria direta no meu gabinete","AtuaÃ§Ã£o em outro Ã³rgÃ£o pÃºblico","Trabalho conjunto em projeto","DocÃªncia ou orientaÃ§Ã£o acadÃªmica","Outro"])
                st.markdown('<div class="custom-divider"></div>',unsafe_allow_html=True)
                pontos=st.text_area("Principais pontos fortes do candidato *",height=100,placeholder="Descreva as qualidades profissionais que mais se destacaram...")
                adequacao=st.selectbox("O candidato Ã© adequado para assessoria em Ã³rgÃ£o pÃºblico? *",["Selecione...","Sim, fortemente recomendo","Sim, com algumas ressalvas","Neutro","NÃ£o recomendo"])
                nota=st.select_slider("Nota geral (1 a 5) *",options=[1,2,3,4,5],value=4)
                comentarios=st.text_area("ComentÃ¡rios adicionais (opcional)",height=80,placeholder="ObservaÃ§Ãµes complementares...")
                st.markdown('<div class="custom-divider"></div>',unsafe_allow_html=True)
                conf=st.checkbox("Confirmo que sou membro ativo de Ã³rgÃ£o do sistema de justiÃ§a e que as informaÃ§Ãµes sÃ£o verdadeiras.")
                submitted=st.form_submit_button("Enviar avaliaÃ§Ã£o â†’")

                if submitted:
                    if tempo=="Selecione..." or contexto=="Selecione..." or adequacao=="Selecione..." or not pontos:
                        st.error("Preencha todos os campos obrigatÃ³rios.")
                    elif not conf:
                        st.error("Confirme sua responsabilidade sobre as informaÃ§Ãµes.")
                    else:
                        resposta=f"Tempo: {tempo} | Contexto: {contexto} | AdequaÃ§Ã£o: {adequacao} | Nota: {nota}/5 | Pontos fortes: {pontos}"
                        idx_recom=next((i for i,r in enumerate(recs_recom) if r.get("token")==token_url),None)
                        if idx_recom is not None:
                            aba_recomendacoes.update_cell(idx_recom+2,4,"concluido")
                            aba_recomendacoes.update_cell(idx_recom+2,6,resposta)
                            aba_recomendacoes.update_cell(idx_recom+2,7,comentarios)
                        if cand_recom:
                            todos_cands2=aba_candidatos.get_all_records()
                            idx_cand=next((i for i,c in enumerate(todos_cands2) if c.get("email")==rec_recom.get("email_candidato")),None)
                            if idx_cand is not None: aba_candidatos.update_cell(idx_cand+2,14,"Sim")
                        st.success("AvaliaÃ§Ã£o enviada! O selo â˜… Recomendado foi ativado no perfil do candidato.")
                        st.balloons()

# â”€â”€ PÃGINAS LEGAIS â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
elif pagina in ["privacidade","termos"]:
    ip=pagina=="privacidade"
    st.markdown(f'<div class="hero-card"><h1 class="page-title">{"PolÃ­tica de<br><em>Privacidade.</em>" if ip else "Termos<br><em>de Uso.</em>"}</h1><p class="page-sub">VersÃ£o 1.0</p></div>',unsafe_allow_html=True)
    if ip:
        secs=[
            ("1. Controlador",[("p","Operado por [RAZÃƒO SOCIAL A PREENCHER], CNPJ [A PREENCHER]. DPO: [E-MAIL A PREENCHER]")]),
            ("2. Dados Coletados",[("l",["Nome, e-mail, formaÃ§Ã£o, OAB","HistÃ³rico em Ã³rgÃ£os pÃºblicos","Sistemas jurÃ­dicos, perfil DISC","Documentos de referÃªncia (quando fornecidos)","E-mail e senha dos recrutadores (hash SHA-256)"])]),
            ("3. Finalidade",[("l",["GestÃ£o de perfis e selos","Viabilizar busca por recrutadores aprovados","GestÃ£o de inscriÃ§Ãµes em Seletivos","Melhoria dos serviÃ§os"])]),
            ("4. Direitos",[("l",["Acesso, correÃ§Ã£o e eliminaÃ§Ã£o","Portabilidade","RevogaÃ§Ã£o do consentimento"]),("p","Contato: [E-MAIL DO DPO A PREENCHER]")]),
        ]
    else:
        secs=[
            ("1. AceitaÃ§Ã£o",[("p","Ao usar o JurisBank vocÃª concorda com estes Termos e com a PolÃ­tica de Privacidade.")]),
            ("2. Seletivos",[("p","A publicaÃ§Ã£o de um Seletivo nÃ£o configura processo seletivo vinculante ou concurso pÃºblico. O uso do ius indicandum Ã© de responsabilidade exclusiva do recrutador.")]),
            ("3. Impessoalidade",[("l",["PrincÃ­pio da impessoalidade (art. 37, CF/88)","VedaÃ§Ã£o ao nepotismo (SV nÂº 13 do STF)","ResoluÃ§Ã£o CNJ nÂº 07/2005"])]),
            ("4. Responsabilidades",[("p","O JurisBank nÃ£o garante contrataÃ§Ãµes e nÃ£o se responsabiliza por decisÃµes dos recrutadores.")]),
            ("5. Foro",[("p","Comarca de [MUNICÃPIO A PREENCHER], Estado de [ESTADO A PREENCHER].")]),
        ]
    for ts,cont in secs:
        st.markdown(f'<div class="doc-sub">{ts}</div>',unsafe_allow_html=True)
        for tp,tx in cont:
            if tp=="p": st.markdown(f'<p class="doc-body">{tx}</p>',unsafe_allow_html=True)
            elif tp=="l":
                for it in tx: st.markdown(f'<p class="doc-item">â€¢ {it}</p>',unsafe_allow_html=True)
        st.markdown('<div class="custom-divider"></div>',unsafe_allow_html=True)
    st.markdown(f'<p style="font-size:12px;color:#4a6080;text-align:center">JurisBank â€” VersÃ£o 1.0 â€” {datetime.now().strftime("%d/%m/%Y")}</p>',unsafe_allow_html=True)

