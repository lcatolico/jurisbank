import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import fitz
import re
import hashlib
from datetime import datetime, date
import json

st.set_page_config(
    page_title="JurisBank",
    page_icon="⚖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Sora:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Sora', sans-serif; }

[data-testid="stToolbar"] { display: none !important; }
[data-testid="stSidebarCollapsedControl"] { display: none !important; }
header[data-testid="stHeader"] { display: none !important; }
#MainMenu { display: none !important; }
[data-testid="stSidebar"] { display: none !important; }
section[data-testid="stSidebarContent"] { display: none !important; }

[data-testid="stAppViewContainer"] {
    background: linear-gradient(160deg, #0d1f4e 0%, #162a6e 50%, #1a3a8f 100%);
    min-height: 100vh;
}
.main .block-container {
    padding: 2rem 2.5rem;
    max-width: 1100px;
    background: transparent;
}

/* Hero cards */
.hero-card {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 20px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    backdrop-filter: blur(10px);
}
.page-title {
    font-family: 'Playfair Display', serif;
    font-size: clamp(32px, 4vw, 48px);
    font-weight: 900;
    color: #ffffff;
    margin: 0 0 8px;
    letter-spacing: -1px;
    line-height: 1.1;
}
.page-title em {
    font-style: normal;
    background: linear-gradient(135deg, #c8960c, #f0c040);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.page-sub { font-size: 15px; color: rgba(255,255,255,0.6); margin: 0; font-weight: 400; }

.stats-row { display: flex; gap: 12px; margin-top: 1.5rem; flex-wrap: wrap; }
.stat-pill {
    background: rgba(255,255,255,0.08);
    border-radius: 99px;
    padding: 8px 18px;
    font-size: 13px;
    font-weight: 600;
    color: rgba(255,255,255,0.85);
    border: 1px solid rgba(255,255,255,0.12);
}

/* Cards de candidato */
.cand-card {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 16px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 8px;
    transition: all 0.2s;
}
.cand-card:hover {
    background: rgba(255,255,255,0.1);
    border-color: rgba(200,150,12,0.4);
    transform: translateY(-2px);
}

.chamada-card {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 16px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 10px;
    transition: all 0.2s;
}
.chamada-card:hover {
    background: rgba(255,255,255,0.1);
    border-color: rgba(200,150,12,0.4);
}

.avatar {
    width: 48px; height: 48px;
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 15px; font-weight: 700;
    flex-shrink: 0; color: white;
}

.cand-name { font-size: 15px; font-weight: 700; color: #ffffff; margin: 0 0 3px; }
.cand-sub { font-size: 12px; color: rgba(255,255,255,0.5); margin: 0; }

.badge-sim { background: rgba(126,217,155,0.15); color: #7ed99b; padding: 4px 12px; border-radius: 99px; font-size: 11px; font-weight: 700; border: 1px solid rgba(126,217,155,0.25); }
.badge-nao { background: rgba(255,150,80,0.15); color: #ffab6e; padding: 4px 12px; border-radius: 99px; font-size: 11px; font-weight: 700; border: 1px solid rgba(255,150,80,0.25); }
.badge-aberta { background: rgba(126,217,155,0.15); color: #7ed99b; padding: 3px 10px; border-radius: 99px; font-size: 11px; font-weight: 700; border: 1px solid rgba(126,217,155,0.2); }
.badge-encerrada { background: rgba(255,255,255,0.08); color: rgba(255,255,255,0.4); padding: 3px 10px; border-radius: 99px; font-size: 11px; font-weight: 700; border: 1px solid rgba(255,255,255,0.1); }
.badge-inscrito { background: rgba(200,150,12,0.15); color: #f0c040; padding: 3px 10px; border-radius: 99px; font-size: 11px; font-weight: 700; border: 1px solid rgba(200,150,12,0.25); }

.selo { display: inline-block; font-size: 10px; font-weight: 700; padding: 3px 10px; border-radius: 99px; margin-right: 4px; margin-top: 4px; }
.selo-verificado { background: rgba(232,239,254,0.15); color: #a8c5ff; border: 1px solid rgba(176,197,245,0.2); }
.selo-recomendado { background: rgba(230,244,234,0.15); color: #7ed99b; border: 1px solid rgba(126,217,155,0.2); }
.selo-destaque { background: rgba(255,248,230,0.15); color: #f0c040; border: 1px solid rgba(240,192,64,0.2); }
.selo-experiente { background: rgba(243,239,254,0.15); color: #c4b5fd; border: 1px solid rgba(196,181,253,0.2); }

.metric-box {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 14px;
    padding: 16px 18px;
    text-align: center;
}
.metric-label { font-size: 11px; font-weight: 600; color: rgba(255,255,255,0.45); text-transform: uppercase; letter-spacing: .08em; margin: 0 0 6px; }
.metric-value { font-size: 20px; font-weight: 800; color: #ffffff; margin: 0; }

.profile-name { font-family: 'Playfair Display', serif; font-size: 28px; font-weight: 900; color: #ffffff; margin: 0 0 6px; }
.section-label { font-size: 11px; font-weight: 700; color: #f0c040; text-transform: uppercase; letter-spacing: .1em; margin: 1.5rem 0 0.5rem; }
.info-card { background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 14px 18px; font-size: 14px; color: rgba(255,255,255,0.8); line-height: 1.6; }
.custom-divider { height: 1px; background: rgba(255,255,255,0.08); margin: 1.5rem 0; border-radius: 99px; }
.info-box { background: rgba(200,150,12,0.12); border: 1px solid rgba(200,150,12,0.25); border-radius: 10px; padding: 10px 14px; font-size: 13px; color: #f0c040; margin-top: 8px; font-weight: 500; }
.lock-box { background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 14px 18px; font-size: 13px; color: rgba(255,255,255,0.4); text-align: center; }
.disclaimer-box { background: rgba(200,150,12,0.08); border: 1px solid rgba(200,150,12,0.2); border-radius: 10px; padding: 12px 16px; font-size: 12px; color: rgba(240,192,64,0.8); line-height: 1.6; margin-top: 1rem; }

.step-bar { display: flex; gap: 8px; margin-bottom: 2rem; }
.step { flex: 1; height: 4px; border-radius: 99px; background: rgba(255,255,255,0.1); }
.step.active { background: linear-gradient(135deg, #c8960c, #f0c040); }
.step.done { background: #7ed99b; }
.step-title { font-size: 13px; font-weight: 600; color: rgba(255,255,255,0.45); margin-bottom: 0.3rem; }
.step-desc { font-family: 'Playfair Display', serif; font-size: 24px; font-weight: 700; color: #ffffff; margin-bottom: 1.5rem; }

.doc-sub { font-size: 12px; font-weight: 700; color: #f0c040; text-transform: uppercase; letter-spacing: .08em; margin: 1.5rem 0 0.5rem; }
.doc-body { font-size: 14px; color: rgba(255,255,255,0.7); line-height: 1.8; margin-bottom: 0.8rem; }
.doc-item { font-size: 14px; color: rgba(255,255,255,0.65); line-height: 1.8; padding-left: 1rem; }

/* Botões globais — dourado */
.stButton button {
    background: linear-gradient(135deg, #c8960c, #f0c040) !important;
    color: #0d1f4e !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Sora', sans-serif !important;
    font-weight: 700 !important;
    padding: 0.6rem 2rem !important;
    font-size: 14px !important;
    transition: all 0.2s !important;
}
.stButton button:hover { opacity: 0.9 !important; transform: translateY(-1px) !important; }

div[data-testid="column"]:last-child .stButton button,
div[data-testid="column"]:nth-last-child(2) .stButton button {
    background: rgba(255,255,255,0.08) !important;
    color: rgba(255,255,255,0.85) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 10px !important;
    padding: 0.4rem 1rem !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    width: 100%;
}
div[data-testid="column"]:last-child .stButton button:hover,
div[data-testid="column"]:nth-last-child(2) .stButton button:hover {
    background: rgba(200,150,12,0.2) !important;
    border-color: rgba(200,150,12,0.4) !important;
    color: #f0c040 !important;
}

.stTextInput input, .stTextArea textarea {
    border-radius: 10px !important;
    border-color: rgba(255,255,255,0.12) !important;
    background: rgba(255,255,255,0.06) !important;
    color: #ffffff !important;
    font-family: 'Sora', sans-serif !important;
    font-size: 14px !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: rgba(200,150,12,0.5) !important;
    box-shadow: 0 0 0 3px rgba(200,150,12,0.12) !important;
}
.stTextInput input::placeholder { color: rgba(255,255,255,0.3) !important; }
.stSelectbox > div > div {
    border-radius: 10px !important;
    border-color: rgba(255,255,255,0.12) !important;
    background: rgba(255,255,255,0.06) !important;
    color: #ffffff !important;
}
.stRadio label { color: rgba(255,255,255,0.8) !important; }
.stCheckbox label { color: rgba(255,255,255,0.8) !important; font-size: 13px !important; }
.stMultiSelect > div > div { background: rgba(255,255,255,0.06) !important; border-color: rgba(255,255,255,0.12) !important; border-radius: 10px !important; }
label[data-baseweb="label"] { color: rgba(255,255,255,0.8) !important; }
.stTabs [data-baseweb="tab-list"] { background: rgba(255,255,255,0.04) !important; border-radius: 12px !important; padding: 4px !important; gap: 4px !important; }
.stTabs [data-baseweb="tab"] { background: transparent !important; color: rgba(255,255,255,0.5) !important; border-radius: 8px !important; }
.stTabs [aria-selected="true"] { background: rgba(200,150,12,0.2) !important; color: #f0c040 !important; }
.stAlert { background: rgba(255,255,255,0.06) !important; border-color: rgba(255,255,255,0.1) !important; color: rgba(255,255,255,0.8) !important; border-radius: 10px !important; }
p, span, div { color: inherit; }
</style>
""", unsafe_allow_html=True)

# ── Google Sheets ─────────────────────────────────────────────────────────────
escopos = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
if "gcp_service_account" in st.secrets:
    credenciais = Credentials.from_service_account_info(dict(st.secrets["gcp_service_account"]), scopes=escopos)
else:
    credenciais = Credentials.from_service_account_file("credenciais.json", scopes=escopos)
cliente = gspread.authorize(credenciais)
planilha = cliente.open("JurisBank")
aba_candidatos = planilha.sheet1
aba_recrutadores = planilha.worksheet("recrutadores")
aba_chamadas = planilha.worksheet("chamadas")
aba_interesses = planilha.worksheet("interesses")

# ── Navegação por URL ─────────────────────────────────────────────────────────
params = st.query_params
if "embed" in params and "p" not in params:
    pagina = st.session_state.get("_pagina", "candidatos")
elif "p" in params:
    pagina = params["p"]
    st.session_state["_pagina"] = pagina
else:
    pagina = st.session_state.get("_pagina", "inicio")

# ── Constantes ────────────────────────────────────────────────────────────────
AVATAR_CORES = ["#1a3a8f","#2e7d5e","#7b3fa0","#c05a1a","#1a6b8a","#a04040","#3a6b2a"]
DISC_LABEL = {"D": "Dominante", "I": "Influente", "S": "Estável", "C": "Conformidade"}
DISC_CORES_BADGE = {"D": "rgba(254,226,226,0.15)", "I": "rgba(254,249,195,0.15)", "S": "rgba(220,252,231,0.15)", "C": "rgba(239,246,255,0.15)"}
DISC_TEXTO_BADGE = {"D": "#fca5a5", "I": "#fde68a", "S": "#6ee7b7", "C": "#93c5fd"}
DISC_EXPLICACOES_FILTRO = {
    "D — Dominante": "Direto e decidido. Resolve problemas com rapidez. Bom para demandas urgentes.",
    "I — Influente": "Comunicativo e entusiasta. Excelente no atendimento ao público e trabalho em equipe.",
    "S — Estável": "Paciente e confiável. Ideal para rotinas de gabinete e processos repetitivos.",
    "C — Conformidade": "Analítico e preciso. Excelente em pesquisa jurídica e elaboração de minutas."
}
DISC_DETALHES = {
    "D": {"nome": "Dominante", "resumo": "Direto, decidido e orientado a resultados.", "pontos_fortes": "Resolve problemas com rapidez, assume responsabilidades, trabalha bem sob pressão.", "no_gabinete": "Ideal para demandas que exigem agilidade, tomada de decisão rápida e autonomia.", "atencao": "Pode ser impaciente com processos lentos. Funciona melhor com autonomia."},
    "I": {"nome": "Influente", "resumo": "Comunicativo, entusiasta e orientado a pessoas.", "pontos_fortes": "Excelente no atendimento ao público, trabalho em equipe e ambientes dinâmicos.", "no_gabinete": "Ideal para Ministérios Públicos ou Defensorias com alto volume de atendimento ao público.", "atencao": "Pode ter dificuldade com tarefas repetitivas e isoladas. Precisa de estímulo."},
    "S": {"nome": "Estável", "resumo": "Paciente, confiável e orientado a processos.", "pontos_fortes": "Consistência, lealdade e capacidade de manter rotinas com qualidade.", "no_gabinete": "Perfil ideal para gabinetes com rotinas estabelecidas — minutas, prazos, organização processual.", "atencao": "Pode ter dificuldade com mudanças repentinas. Prefere ambientes previsíveis."},
    "C": {"nome": "Conformidade", "resumo": "Analítico, preciso e orientado à qualidade.", "pontos_fortes": "Atenção aos detalhes, rigor técnico, capacidade de análise aprofundada e pesquisa jurídica.", "no_gabinete": "Ideal para assessorias que demandam análise de processos complexos e elaboração técnica.", "atencao": "Pode ser perfeccionista. Precisa de clareza nas instruções."}
}
DESCRICOES_DISC = {
    "D": "Dominante — Direto, decidido e orientado a resultados. Trabalha bem sob pressão.",
    "I": "Influente — Comunicativo, entusiasta e orientado a pessoas. Excelente em atendimento.",
    "S": "Estável — Paciente, confiável e orientado a processos. Ideal para rotinas de gabinete.",
    "C": "Conformidade — Analítico, preciso e orientado a qualidade. Excelente em pesquisa jurídica."
}
CONCURSOS = ["Não estou estudando para concurso","Juiz de Direito (TJ)","Juiz Federal (TRF)","Promotor de Justiça (MP Estadual)","Procurador da República (MPF)","Defensor Público Estadual","Defensor Público Federal (DPU)","Procurador do Estado (PGE)","Procurador Municipal","Delegado de Polícia","Auditor Fiscal / Receita Federal","Outro concurso jurídico"]
ESTADOS = ["AC","AL","AP","AM","BA","CE","DF","ES","GO","MA","MT","MS","MG","PA","PB","PR","PE","PI","RJ","RN","RS","RO","RR","SC","SP","SE","TO"]
ORGAOS = ["Tribunal de Justiça (TJ)","Ministério Público (MP)","Defensoria Pública","Procuradoria Geral do Estado (PGE)","Procuradoria Geral do Município (PGM)","Tribunal Regional Federal (TRF)","Ministério Público Federal (MPF)","Advocacia Geral da União (AGU)","Tribunal de Contas (TCE/TCU)","Outro"]
CARGOS = ["Juiz de Direito","Juiz Federal","Desembargador","Promotor de Justiça","Procurador de Justiça","Defensor Público","Procurador do Estado","Procurador Municipal","Servidor — RH / Gestão de Pessoas","Outro"]
AREAS = ["Criminal","Cível","Família e Sucessões","Execução Penal","Infância e Juventude","Fazenda Pública","Meio Ambiente","Moralidade Administrativa","Violência Doméstica","Direito Público","Direito Tributário","Consumidor","Saúde","Todas as áreas"]
REGIMES = ["Integral","Parcial","Remoto","Híbrido"]
FORMAS_SELECAO = ["Análise de currículo","Análise de currículo + entrevista","Entrevista","Análise de portfólio + entrevista","Processo simplificado"]
PERGUNTAS_DISC = [
    ("Em situações de pressão no trabalho, você tende a:", ["Tomar decisões rápidas e assumir o controle","Motivar a equipe e buscar soluções criativas","Manter a calma e seguir o processo estabelecido","Analisar os dados antes de agir"]),
    ("Quando recebe uma tarefa nova, você prefere:", ["Ter autonomia total para decidir como fazer","Conversar com a equipe e trocar ideias","Entender bem o processo antes de começar","Ter instruções detalhadas e critérios claros"]),
    ("Em reuniões, você costuma:", ["Liderar a discussão e propor soluções","Animar o grupo e trazer entusiasmo","Ouvir com atenção antes de opinar","Apresentar dados e análises detalhadas"]),
    ("Seu ponto forte no trabalho é:", ["Resultados rápidos e objetivos","Relacionamentos e comunicação","Estabilidade e confiabilidade","Precisão e qualidade técnica"]),
    ("Quando há um conflito na equipe, você:", ["Enfrenta diretamente e busca resolução imediata","Tenta mediar com diplomacia e bom humor","Evita confrontos e busca harmonia","Analisa a situação antes de se posicionar"]),
    ("Você se sente mais motivado quando:", ["Tem metas desafiadoras para superar","Trabalha com pessoas e recebe reconhecimento","Tem rotina estável e previsível","Pode aprofundar conhecimento e fazer bem feito"]),
    ("Seu estilo de comunicação é:", ["Direto e objetivo","Entusiasmado e expressivo","Calmo e paciente","Preciso e detalhado"]),
    ("Diante de uma mudança repentina, você:", ["Adapta rapidamente e assume o controle","Vê como oportunidade e engaja a equipe","Precisa de tempo para se adaptar","Avalia os riscos antes de aceitar"]),
    ("No trabalho em equipe, você assume o papel de:", ["Líder que define rumos e cobra resultados","Motivador que mantém o clima positivo","Apoiador que garante a harmonia do grupo","Especialista que garante a qualidade técnica"]),
    ("Quando comete um erro, você:", ["Assume, corrige rapidamente e segue em frente","Conversa com alguém para processar e superar","Reflete com calma antes de agir diferente","Analisa o que deu errado para não repetir"]),
    ("Sua maior dificuldade no trabalho é:", ["Paciência com processos lentos","Manter o foco em tarefas repetitivas","Lidar com mudanças repentinas","Trabalhar sem informações suficientes"]),
    ("Como você prefere receber feedback:", ["Direto e objetivo, sem rodeios","De forma encorajadora e positiva","Com calma, em conversa reservada","Com dados e exemplos concretos"]),
]
LETRAS_DISC = ["D","I","S","C"]
DISCLAIMER_CHAMADA = "⚠️ O JurisBank atua exclusivamente como plataforma de aproximação. A publicação desta Chamada não configura processo seletivo vinculante, concurso público ou compromisso de contratação. O uso do ius indicandum é de responsabilidade exclusiva do recrutador, que deve observar as normas de impessoalidade e vedação ao nepotismo aplicáveis ao seu órgão."
LANDING_URL = "https://lcatolico.github.io/jurisbank/"

# ── Funções ───────────────────────────────────────────────────────────────────
def cor_avatar(nome): return AVATAR_CORES[sum(ord(c) for c in nome) % len(AVATAR_CORES)]
def iniciais(nome):
    p = nome.strip().split()
    return (p[0][0]+p[-1][0]).upper() if len(p)>=2 else nome[:2].upper()
def hash_senha(s): return hashlib.sha256(s.encode()).hexdigest()
def recrutador_logado(): return "recrutador_logado" in st.session_state and st.session_state.recrutador_logado
def candidato_logado(): return "candidato_logado" in st.session_state and st.session_state.candidato_logado
def gerar_id_chamada(): return f"ch_{datetime.now().strftime('%Y%m%d%H%M%S')}"
def chamada_aberta(ch):
    if ch.get("status","").lower() != "aberto": return False
    try:
        return datetime.strptime(ch.get("prazo",""), "%d/%m/%Y").date() >= date.today()
    except: return True
def inscritos_chamada(ch):
    raw = str(ch.get("inscritos","")).strip()
    return [e.strip() for e in raw.split(",") if e.strip()] if raw else []

def extrair_texto_pdf(arquivo):
    doc = fitz.open(stream=arquivo.read(), filetype="pdf")
    return "".join(p.get_text() for p in doc)

def extrair_campos(texto):
    campos = {"nome":"","email":"","oab":"Não","experiencia_orgaos":"","sistemas":"","pos_graduacao":"","resumo":""}
    linhas = texto.split("\n"); tc = texto.lower()
    emails = re.findall(r'[\w\.\-]+@[\w\.\-]+\.\w+', texto)
    if emails: campos["email"] = emails[0]
    if "oab" in tc or "ordem dos advogados" in tc: campos["oab"] = "Sim"
    sis = ["Eproc","SAJ","SIG","SEEU","SISP","APOIA","GAIA","Pandora","SIMBA"]
    enc = [s for s in sis if s.lower() in tc]
    if enc: campos["sistemas"] = ", ".join(enc)
    for l in linhas:
        l=l.strip()
        if any(x in l for x in ["Pós","pós","Especializ","Mestrado","Doutorado"]):
            if len(l)>10 and not campos["pos_graduacao"]: campos["pos_graduacao"]=l
    om = {"MPSC":"MPSC","TJSC":"TJSC","Defensoria":"Defensoria","Procuradoria":"Procuradoria","Ministério Público":"MP","Tribunal de Justiça":"TJ","AGU":"AGU","PGE":"PGE"}
    eo=[]
    for o,s in om.items():
        if o.lower() in tc and s not in eo: eo.append(s)
    campos["experiencia_orgaos"]=", ".join(eo)
    for l in linhas:
        l=l.strip()
        if len(l)>5 and not any(x in l for x in ["@","Rua","Av.","http","www","(","PERFIL","CONTATO"]) and not re.match(r'^\d',l):
            campos["nome"]=l; break
    pars=[p.strip() for p in texto.split("\n\n") if len(p.strip())>100]
    if pars: campos["resumo"]=max(pars,key=len)[:500]
    return campos

def calcular_selos(oab, anos, carta, aval):
    return {"verificado":"Sim" if oab=="Sim" else "Não","recomendado":"Sim" if carta else "Não","destaque":"Sim" if aval else "Não","experiente":"Sim" if anos>=2 else "Não"}

def html_selos(c):
    h=""
    if c.get("selo_verificado")=="Sim": h+='<span class="selo selo-verificado">✓ Verificado</span>'
    if c.get("selo_recomendado")=="Sim": h+='<span class="selo selo-recomendado">★ Recomendado</span>'
    if c.get("selo_destaque")=="Sim": h+='<span class="selo selo-destaque">◆ Destaque</span>'
    if c.get("selo_experiente")=="Sim": h+='<span class="selo selo-experiente">● Experiente</span>'
    return h

def html_disc_badge(c):
    d=c.get("disc","")
    if not d: return ""
    return f'<span style="font-size:10px;font-weight:700;padding:2px 8px;border-radius:99px;background:{DISC_CORES_BADGE.get(d,"rgba(255,255,255,0.1)")};color:{DISC_TEXTO_BADGE.get(d,"#fff")};margin-left:4px">{d} {DISC_LABEL.get(d,"")}</span>'

def html_concurso_badge(c):
    if c.get("concurso") and c.get("concurso")!="Não estou estudando para concurso":
        return '<span style="font-size:10px;font-weight:700;padding:2px 8px;border-radius:99px;background:rgba(200,150,12,0.12);color:#f0c040;margin-left:4px;border:1px solid rgba(200,150,12,0.2)">📚 Concursando</span>'
    return ""

def barra_etapas(atual, total=3):
    h='<div class="step-bar">'
    for i in range(1,total+1):
        if i<atual: h+='<div class="step done"></div>'
        elif i==atual: h+='<div class="step active"></div>'
        else: h+='<div class="step"></div>'
    return h+'</div>'

def calcular_disc(respostas):
    p={"D":0,"I":0,"S":0,"C":0}
    for i,r in enumerate(respostas):
        if r is None: continue
        _,ops=PERGUNTAS_DISC[i]; p[LETRAS_DISC[ops.index(r)]]+=1
    d=max(p,key=p.get)
    return d,p,DESCRICOES_DISC[d]

def render_disc_perfil(d):
    cor=DISC_CORES_BADGE.get(d,"rgba(255,255,255,0.08)")
    txt=DISC_TEXTO_BADGE.get(d,"#fff")
    det=DISC_DETALHES.get(d,{})
    return f"""<div class="info-card" style="background:{cor};border-color:rgba(255,255,255,0.1)">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px">
            <span style="font-weight:800;color:{txt};font-size:24px">{d}</span>
            <span style="font-weight:700;color:{txt};font-size:16px">{det.get('nome','')}</span>
        </div>
        <p style="color:{txt};font-size:14px;font-weight:600;margin:0 0 8px">{det.get('resumo','')}</p>
        <p style="color:rgba(255,255,255,0.7);font-size:12px;margin:0 0 4px"><strong style="color:{txt}">Pontos fortes:</strong> {det.get('pontos_fortes','')}</p>
        <p style="color:rgba(255,255,255,0.7);font-size:12px;margin:0 0 4px"><strong style="color:{txt}">No gabinete:</strong> {det.get('no_gabinete','')}</p>
        <p style="color:rgba(255,255,255,0.7);font-size:12px;margin:0"><strong style="color:{txt}">Atenção:</strong> {det.get('atencao','')}</p>
    </div>"""

def botao_voltar():
    st.markdown(f'<a href="{LANDING_URL}" target="_blanck" style="display:inline-flex;align-items:center;gap:6px;color:rgba(255,255,255,0.5);font-size:13px;text-decoration:none;margin-bottom:1.5rem">← Voltar à página inicial</a>', unsafe_allow_html=True)

# ── PÁGINA: INÍCIO (boas-vindas) ──────────────────────────────────────────────
if pagina == "inicio":
    st.markdown(f"""
    <div style="min-height:80vh;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:3rem 2rem">
        <div style="width:72px;height:72px;background:linear-gradient(135deg,#c8960c,#f0c040);border-radius:18px;display:flex;align-items:center;justify-content:center;font-size:36px;margin:0 auto 1.5rem;box-shadow:0 4px 24px rgba(200,150,12,0.35)">⚖</div>
        <h1 style="font-family:'Playfair Display',serif;font-size:clamp(36px,5vw,56px);font-weight:900;color:#ffffff;letter-spacing:-1.5px;line-height:1.05;margin:0 0 1rem">JurisBank</h1>
        <p style="font-size:16px;color:rgba(255,255,255,0.5);font-style:italic;margin:0 0 2rem;letter-spacing:.05em">ius indicandum</p>
        <p style="font-size:17px;color:rgba(255,255,255,0.65);max-width:480px;line-height:1.7;margin:0 0 2.5rem">Banco de talentos jurídicos certificados para assessoria em Tribunais, Ministérios Públicos, Defensorias e Procuradorias.</p>
        <a href="{LANDING_URL}" target="_blank" style="display:inline-flex;align-items:center;gap:8px;padding:16px 40px;background:linear-gradient(135deg,#c8960c,#f0c040);color:#0d1f4e;font-family:'Sora',sans-serif;font-weight:700;font-size:16px;border-radius:12px;text-decoration:none;box-shadow:0 4px 20px rgba(200,150,12,0.35)">
            Acessar o JurisBank →
        </a>
    </div>
    """, unsafe_allow_html=True)

# ── PÁGINA: CANDIDATOS ────────────────────────────────────────────────────────
elif pagina == "candidatos":
    dados = aba_candidatos.get_all_records()
    if "candidato_selecionado" not in st.session_state: st.session_state.candidato_selecionado = None

    if st.session_state.candidato_selecionado:
        c = st.session_state.candidato_selecionado
        cor = cor_avatar(c["nome"])
        if st.button("← Voltar para lista"):
            st.session_state.candidato_selecionado = None; st.rerun()

        st.markdown(f"""
        <div class="hero-card">
            <div style="display:flex;align-items:center;gap:18px">
                <div class="avatar" style="width:64px;height:64px;border-radius:16px;background:{cor};font-size:22px">{iniciais(c['nome'])}</div>
                <div>
                    <div class="profile-name">{c['nome']}</div>
                    <div style="font-size:13px;color:rgba(255,255,255,0.5);margin-bottom:8px">{c.get('formacao','—')} · {c.get('instituicao','—')}</div>
                    <div>{html_selos(c)}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col1,col2,col3,col4 = st.columns(4)
        for col,label,val in [(col1,"Área",c.get("area","—")),(col2,"OAB",c.get("oab","—")),(col3,"Disponível",c.get("disponibilidade","—")),(col4,"Órgãos",c.get("experiencia_orgaos","—") or "—")]:
            with col: st.markdown(f'<div class="metric-box"><p class="metric-label">{label}</p><p class="metric-value">{val}</p></div>', unsafe_allow_html=True)

        if c.get("disc"):
            st.markdown('<p class="section-label">Perfil DISC</p>', unsafe_allow_html=True)
            st.markdown(render_disc_perfil(c.get("disc")), unsafe_allow_html=True)

        if c.get("concurso") and c.get("concurso")!="Não estou estudando para concurso":
            st.markdown('<p class="section-label">Concurso</p>', unsafe_allow_html=True)
            st.markdown(f'<div class="info-card">📚 {c.get("concurso")}</div>', unsafe_allow_html=True)

        if c.get("sistemas"):
            st.markdown('<p class="section-label">Sistemas</p>', unsafe_allow_html=True)
            st.markdown(f'<div class="info-card">{c.get("sistemas")}</div>', unsafe_allow_html=True)

        if c.get("resumo"):
            st.markdown('<p class="section-label">Resumo profissional</p>', unsafe_allow_html=True)
            if recrutador_logado():
                st.markdown(f'<div class="info-card">{c.get("resumo")}</div>', unsafe_allow_html=True)
            else:
                prev = c.get("resumo","")[:150]+"..." if len(c.get("resumo",""))>150 else c.get("resumo","")
                st.markdown(f'<div class="info-card">{prev}<br><br><span style="font-size:12px;color:#f0c040">🔐 Resumo completo disponível para recrutadores cadastrados.</span></div>', unsafe_allow_html=True)

        st.markdown('<p class="section-label">Contato</p>', unsafe_allow_html=True)
        if recrutador_logado():
            st.markdown(f'<div class="info-card">✉ {c.get("email","—")}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="lock-box">🔐 Dados de contato disponíveis apenas para recrutadores aprovados.</div>', unsafe_allow_html=True)

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
        </div>
        """, unsafe_allow_html=True)

        col1,col2,col3 = st.columns(3)
        with col1: busca=st.text_input("Buscar por nome", placeholder="Digite um nome...")
        with col2:
            areas=["Todas"]+sorted(set(c["area"] for c in dados if c.get("area")))
            area_sel=st.selectbox("Área", areas)
        with col3: filtro_selo=st.selectbox("Selo",["Todos","Verificado","Recomendado","Destaque","Experiente"])

        cf=dados
        if busca: cf=[c for c in cf if busca.lower() in c["nome"].lower()]
        if area_sel!="Todas": cf=[c for c in cf if c["area"]==area_sel]
        if filtro_selo!="Todos":
            cm={"Verificado":"selo_verificado","Recomendado":"selo_recomendado","Destaque":"selo_destaque","Experiente":"selo_experiente"}
            cf=[c for c in cf if c.get(cm[filtro_selo])=="Sim"]

        st.markdown(f'<p style="font-size:13px;color:rgba(255,255,255,0.4);margin-bottom:1rem">{len(cf)} candidato(s)</p>', unsafe_allow_html=True)

        for i,cand in enumerate(cf):
            cor=cor_avatar(cand["nome"]); disp_c=cand.get("disponibilidade","Não")
            badge='<span class="badge-sim">● Disponível</span>' if disp_c=="Sim" else '<span class="badge-nao">● Indisponível</span>'
            col_card,col_btn=st.columns([11,2])
            with col_card:
                st.markdown(f"""
                <div class="cand-card">
                    <div style="display:flex;align-items:center;justify-content:space-between;gap:12px">
                        <div style="display:flex;align-items:center;gap:14px;flex:1">
                            <div class="avatar" style="background:{cor}">{iniciais(cand['nome'])}</div>
                            <div>
                                <p class="cand-name">{cand['nome']}</p>
                                <p class="cand-sub">{cand.get('formacao','—')} · {cand.get('instituicao','—')} · {cand.get('area','—')}</p>
                                <div style="margin-top:4px">{html_selos(cand)}{html_disc_badge(cand)}{html_concurso_badge(cand)}</div>
                            </div>
                        </div>
                        <div style="flex-shrink:0">{badge}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with col_btn:
                st.write("")
                if st.button("Ver →", key=f"btn_{i}"):
                    st.session_state.candidato_selecionado=cand; st.rerun()

# ── PÁGINA: CHAMADAS ──────────────────────────────────────────────────────────
elif pagina == "chamadas":
    todas_chamadas = aba_chamadas.get_all_records()

    if not candidato_logado() and not recrutador_logado():
        with st.expander("🔑 Sou candidato cadastrado — quero me inscrever"):
            em=st.text_input("Seu e-mail cadastrado", key="cand_login")
            if st.button("Acessar", key="btn_cand_login"):
                tc=aba_candidatos.get_all_records()
                cf=next((c for c in tc if c.get("email","").lower()==em.lower()),None)
                if cf: st.session_state.candidato_logado=cf; st.success(f"Bem-vindo, {cf['nome'].split()[0]}!"); st.rerun()
                else: st.error("E-mail não encontrado. Cadastre seu currículo primeiro.")

    if candidato_logado():
        cand=st.session_state.candidato_logado
        col1,col2=st.columns([8,2])
        with col1: st.markdown(f'<div class="info-box">👤 {cand["nome"]}</div>', unsafe_allow_html=True)
        with col2:
            if st.button("Sair", key="sair_cand"): del st.session_state.candidato_logado; st.rerun()

    st.markdown("""
    <div class="hero-card">
        <h1 class="page-title">Chamadas<br><em>Abertas.</em></h1>
        <p class="page-sub">Vagas de cargos de livre nomeação em Tribunais, Ministérios Públicos, Defensorias e Procuradorias</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown(f'<div class="disclaimer-box">{DISCLAIMER_CHAMADA}</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    col1,col2,col3=st.columns(3)
    with col1: fa=st.selectbox("Área",["Todas"]+AREAS,key="fa")
    with col2: fe=st.selectbox("Estado",["Todos"]+ESTADOS,key="fe")
    with col3: fs=st.selectbox("Status",["Abertas","Todas","Encerradas"],key="fs")

    chf=todas_chamadas
    if fa!="Todas": chf=[ch for ch in chf if ch.get("area")==fa]
    if fe!="Todos": chf=[ch for ch in chf if ch.get("estado")==fe]
    if fs=="Abertas": chf=[ch for ch in chf if chamada_aberta(ch)]
    elif fs=="Encerradas": chf=[ch for ch in chf if not chamada_aberta(ch)]

    st.markdown(f'<p style="font-size:13px;color:rgba(255,255,255,0.4);margin-bottom:1rem">{len(chf)} chamada(s)</p>', unsafe_allow_html=True)

    for i,ch in enumerate(chf):
        ab=chamada_aberta(ch); ins=inscritos_chamada(ch); n=len(ins)
        sb='<span class="badge-aberta">● Aberta</span>' if ab else '<span class="badge-encerrada">● Encerrada</span>'
        ja=candidato_logado() and st.session_state.candidato_logado.get("email","") in ins

        st.markdown(f"""
        <div class="chamada-card">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:12px">
                <div style="flex:1">
                    <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">
                        {sb}
                        <span style="font-size:11px;color:rgba(255,255,255,0.4)">📅 {ch.get('prazo','—')}</span>
                        <span style="font-size:11px;color:rgba(255,255,255,0.4)">👥 {n} inscrito(s)</span>
                    </div>
                    <p style="font-size:16px;font-weight:700;color:#ffffff;margin:0 0 4px">{ch.get('titulo','—')}</p>
                    <p style="font-size:13px;color:rgba(255,255,255,0.5);margin:0 0 8px">{ch.get('orgao','—')} · {ch.get('municipio','—')}/{ch.get('estado','—')}</p>
                    <div style="display:flex;gap:8px;flex-wrap:wrap">
                        <span style="font-size:11px;font-weight:600;padding:2px 10px;border-radius:99px;background:rgba(168,197,255,0.12);color:#a8c5ff">{ch.get('area','—')}</span>
                        <span style="font-size:11px;font-weight:600;padding:2px 10px;border-radius:99px;background:rgba(196,181,253,0.12);color:#c4b5fd">{ch.get('regime','—')}</span>
                        <span style="font-size:11px;font-weight:600;padding:2px 10px;border-radius:99px;background:rgba(110,231,183,0.12);color:#6ee7b7">{ch.get('vagas','—')} vaga(s)</span>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_d,col_i=st.columns([8,3])
        with col_d:
            if st.button("Ver detalhes", key=f"dch_{i}"):
                st.session_state[f"vch_{i}"]=not st.session_state.get(f"vch_{i}",False); st.rerun()
        with col_i:
            if ab and candidato_logado() and not ja:
                if st.button("Inscrever-se →", key=f"ins_{i}"):
                    st.session_state[f"conf_{i}"]=True; st.rerun()
            elif ja: st.markdown('<span class="badge-inscrito">✓ Inscrito</span>', unsafe_allow_html=True)
            elif not candidato_logado() and ab: st.markdown('<span style="font-size:11px;color:rgba(255,255,255,0.35)">Faça login para se inscrever</span>', unsafe_allow_html=True)

        if st.session_state.get(f"conf_{i}"):
            with st.container():
                st.markdown(f'<div class="info-card" style="margin-top:8px"><strong style="color:#ffffff">Confirmar inscrição em: {ch.get("titulo","")}</strong></div>', unsafe_allow_html=True)
                cons=st.checkbox("Autorizo o compartilhamento do meu perfil com o recrutador desta Chamada, nos termos da LGPD.", key=f"cons_{i}")
                col_c,col_x=st.columns(2)
                with col_c:
                    if st.button("Confirmar", key=f"confi_{i}"):
                        if not cons: st.error("Autorize o compartilhamento para continuar.")
                        else:
                            ec=st.session_state.candidato_logado.get("email","")
                            ia=inscritos_chamada(ch)
                            if ec not in ia:
                                ia.append(ec)
                                tc=aba_chamadas.get_all_records()
                                idx=next((j for j,c in enumerate(tc) if c.get("id")==ch.get("id")),None)
                                if idx is not None: aba_chamadas.update_cell(idx+2,16,", ".join(ia))
                            del st.session_state[f"conf_{i}"]
                            st.success("Inscrição realizada!"); st.rerun()
                with col_x:
                    if st.button("Cancelar", key=f"canc_{i}"):
                        del st.session_state[f"conf_{i}"]; st.rerun()

        if st.session_state.get(f"vch_{i}"):
            with st.expander("Detalhes", expanded=True):
                col1,col2,col3=st.columns(3)
                with col1: st.markdown(f'<div class="metric-box"><p class="metric-label">Remuneração</p><p class="metric-value" style="font-size:14px">{ch.get("remuneracao","—")}</p></div>', unsafe_allow_html=True)
                with col2: st.markdown(f'<div class="metric-box"><p class="metric-label">Regime</p><p class="metric-value" style="font-size:14px">{ch.get("regime","—")}</p></div>', unsafe_allow_html=True)
                with col3: st.markdown(f'<div class="metric-box"><p class="metric-label">Seleção</p><p class="metric-value" style="font-size:14px">{ch.get("forma_selecao","—")}</p></div>', unsafe_allow_html=True)
                if ch.get("requisitos"):
                    st.markdown('<p class="section-label">Requisitos</p>', unsafe_allow_html=True)
                    st.markdown(f'<div class="info-card">{ch.get("requisitos")}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="disclaimer-box" style="margin-top:1rem">{DISCLAIMER_CHAMADA}</div>', unsafe_allow_html=True)

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    st.markdown('<p style="font-size:15px;font-weight:700;color:#ffffff;margin-bottom:4px">Receba avisos de novas Chamadas</p>', unsafe_allow_html=True)
    st.markdown('<p style="font-size:13px;color:rgba(255,255,255,0.45);margin-bottom:1rem">Deixe seu e-mail e área de interesse.</p>', unsafe_allow_html=True)
    col1,col2,col3=st.columns(3)
    with col1: ei=st.text_input("Seu e-mail", key="ei")
    with col2: ai=st.multiselect("Áreas", AREAS, key="ai")
    with col3: sti=st.multiselect("Estados", ESTADOS, key="sti")
    if st.button("Quero receber avisos", key="btn_int"):
        if not ei or not ai: st.error("Preencha e-mail e ao menos uma área.")
        else:
            aba_interesses.append_row([ei,", ".join(ai),", ".join(sti),datetime.now().strftime("%d/%m/%Y")])
            st.success("Pronto! Você será avisado quando surgir uma Chamada compatível.")

# ── PÁGINA: CADASTRO ──────────────────────────────────────────────────────────
elif pagina == "cadastro":
    if "etapa_cand" not in st.session_state: st.session_state.etapa_cand=1
    if "campos" not in st.session_state: st.session_state.campos={}
    if "dados_cand" not in st.session_state: st.session_state.dados_cand={}

    etapa=st.session_state.etapa_cand
    titulos=[("Seus dados\nprofissionais.","Preencha ou faça upload do seu currículo em PDF"),("Certificação e\nreferências.","Documentos que geram selos e aumentam sua visibilidade"),("Perfil\ncomportamental.","12 perguntas rápidas — cerca de 3 minutos")]
    titulo,sub=titulos[etapa-1]

    st.markdown(f"""
    <div class="hero-card">
        <h1 class="page-title">{titulo}</h1>
        <p class="page-sub">{sub}</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown(barra_etapas(etapa,3), unsafe_allow_html=True)
    st.markdown(f'<p class="step-title">Etapa {etapa} de 3</p>', unsafe_allow_html=True)

    if etapa==1:
        pdf=st.file_uploader("Upload do currículo em PDF (opcional)", type="pdf")
        if pdf and not st.session_state.campos:
            with st.spinner("Extraindo dados..."): st.session_state.campos=extrair_campos(extrair_texto_pdf(pdf))
            st.rerun()
        if pdf is None: st.session_state.campos={}
        campos=st.session_state.campos
        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

        col1,col2=st.columns(2)
        with col1: nome=st.text_input("Nome completo *",value=campos.get("nome",""))
        with col2: email=st.text_input("E-mail *",value=campos.get("email",""))
        col1,col2,col3=st.columns(3)
        with col1: formacao=st.selectbox("Formação *",["Bacharel em Direito","Pós-graduado em Direito","Mestre em Direito","Doutor em Direito"])
        with col2: instituicao=st.text_input("Instituição *")
        with col3: area=st.selectbox("Área *",["Tribunal","MP","Procuradoria","Defensoria","TCU/TCE"])
        col1,col2,col3=st.columns(3)
        with col1: oab=st.radio("OAB ativa?",["Sim","Não"],index=0 if campos.get("oab")=="Sim" else 1,horizontal=True)
        with col2: anos=st.number_input("Anos em órgão público",min_value=0,max_value=40,value=0)
        with col3: disp=st.radio("Disponível?",["Sim","Não"],horizontal=True)
        exp=st.text_input("Órgãos de atuação",value=campos.get("experiencia_orgaos",""))
        sis=st.text_input("Sistemas dominados",value=campos.get("sistemas",""))
        pos=st.text_input("Pós-graduação",value=campos.get("pos_graduacao",""))
        res=st.text_area("Resumo profissional",value=campos.get("resumo",""),height=100)
        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
        conc=st.selectbox("Estudando para algum concurso?",CONCURSOS)
        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
        cons=st.checkbox("Li e aceito a Política de Privacidade e os Termos de Uso. Consinto com o tratamento dos meus dados pessoais nos termos da LGPD (Lei nº 13.709/2018).")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Próximo →"):
            if not nome or not email or not instituicao: st.error("Preencha nome, e-mail e instituição.")
            elif not cons: st.error("Aceite os Termos para continuar.")
            else:
                st.session_state.dados_cand.update({"nome":nome,"email":email,"formacao":formacao,"instituicao":instituicao,"area":area,"oab":oab,"anos_experiencia":anos,"disponibilidade":disp,"experiencia":exp,"sistemas":sis,"pos":pos,"resumo":res,"concurso":conc})
                st.session_state.etapa_cand=2; st.rerun()

    elif etapa==2:
        col1,col2=st.columns(2)
        with col1:
            st.markdown('<p style="font-weight:600;color:#f0c040;margin-bottom:4px">★ Carta de recomendação</p>', unsafe_allow_html=True)
            st.markdown('<p style="font-size:12px;color:rgba(255,255,255,0.45);margin-bottom:8px">De um Juiz, Promotor, Defensor ou Procurador ativo</p>', unsafe_allow_html=True)
            carta=st.file_uploader("",type="pdf",key="carta",label_visibility="collapsed")
        with col2:
            st.markdown('<p style="font-weight:600;color:#f0c040;margin-bottom:4px">◆ Avaliação de desempenho</p>', unsafe_allow_html=True)
            st.markdown('<p style="font-size:12px;color:rgba(255,255,255,0.45);margin-bottom:8px">Avaliação formal emitida pelo órgão</p>', unsafe_allow_html=True)
            aval=st.file_uploader("",type="pdf",key="avaliacao",label_visibility="collapsed")

        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
        st.markdown('<p style="font-weight:600;color:rgba(255,255,255,0.8);margin-bottom:4px">E-mail institucional do recomendador</p>', unsafe_allow_html=True)
        er=st.text_input("",placeholder="nome@mpsc.mp.br",key="email_ref",label_visibility="collapsed")
        dv=["mpsc.mp.br","tjsc.jus.br","sc.def.br","pge.sc.gov.br","trf4.jus.br","jfsc.jus.br","mpf.mp.br","agu.gov.br"]
        if er and "@" in er:
            if er.split("@")[-1] in dv: st.markdown('<div class="info-box">✓ E-mail institucional reconhecido.</div>', unsafe_allow_html=True)
            else: st.warning("Domínio não reconhecido.")

        d=st.session_state.dados_cand; sp=[]
        if d.get("oab")=="Sim": sp.append("✓ Verificado")
        if carta: sp.append("★ Recomendado")
        if aval: sp.append("◆ Destaque")
        if d.get("anos_experiencia",0)>=2: sp.append("● Experiente")
        if sp:
            st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
            st.markdown('<p style="font-size:13px;font-weight:600;color:#f0c040">Selos que você vai receber:</p>', unsafe_allow_html=True)
            st.markdown(" ".join([f'<span class="selo selo-verificado">{s}</span>' for s in sp]), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        col1,col2=st.columns(2)
        with col1:
            if st.button("← Voltar"): st.session_state.etapa_cand=1; st.rerun()
        with col2:
            if st.button("Próximo →"):
                st.session_state.dados_cand.update({"carta":carta is not None,"avaliacao":aval is not None,"email_ref":er})
                st.session_state.etapa_cand=3; st.rerun()

    elif etapa==3:
        st.markdown('<p style="font-size:14px;color:rgba(255,255,255,0.5);margin-bottom:1.5rem">Não há respostas certas ou erradas.</p>', unsafe_allow_html=True)
        rd=[]
        for j,(perg,ops) in enumerate(PERGUNTAS_DISC):
            r=st.radio(f"**{j+1}.** {perg}",ops,key=f"disc_{j}",index=None)
            rd.append(r)

        st.markdown("<br>", unsafe_allow_html=True)
        col1,col2=st.columns(2)
        with col1:
            if st.button("← Voltar"): st.session_state.etapa_cand=2; st.rerun()
        with col2:
            if st.button("Cadastrar no JurisBank →"):
                if None in rd: st.error("Responda todas as 12 perguntas.")
                else:
                    d=st.session_state.dados_cand
                    selos=calcular_selos(d["oab"],d["anos_experiencia"],d.get("carta",False),d.get("avaliacao",False))
                    pd_,_,desc=calcular_disc(rd)
                    aba_candidatos.append_row([d["nome"],d["email"],d["formacao"],d["instituicao"],d["area"],d["disponibilidade"],d["oab"],d["experiencia"],d["sistemas"],d["pos"],d["resumo"],d.get("email_ref",""),selos["verificado"],selos["recomendado"],selos["destaque"],selos["experiente"],pd_,d.get("concurso","Não estou estudando para concurso")])
                    st.session_state.etapa_cand=1; st.session_state.campos={}; st.session_state.dados_cand={}
                    st.success(f"Bem-vindo ao JurisBank!")
                    st.markdown(f'<div class="info-box">Perfil: <strong>{pd_} — {desc}</strong></div>', unsafe_allow_html=True)
                    st.balloons()

# ── PÁGINA: RECRUTADOR ────────────────────────────────────────────────────────
elif pagina == "recrutador":
    if recrutador_logado():
        rec=st.session_state.recrutador_logado
        dados=aba_candidatos.get_all_records()
        recs=aba_recrutadores.get_all_records()
        idx_r=next((i for i,r in enumerate(recs) if r["email"]==rec["email"]),None)
        ra=recs[idx_r] if idx_r is not None else rec
        favs=[f.strip() for f in str(ra.get("favoritos","")).split(",") if f.strip()]
        anots={}
        for it in str(ra.get("anotacoes","")).split("|"):
            if "::" in it:
                ec,nt=it.split("::",1); anots[ec.strip()]=nt.strip()

        mch=[ch for ch in aba_chamadas.get_all_records() if ch.get("email_recrutador")==rec["email"]]

        st.markdown(f"""
        <div class="hero-card">
            <h1 class="page-title">Olá, <em>{rec['nome'].split()[0]}!</em></h1>
            <p class="page-sub">{ra.get('nome_orgao',rec.get('orgao',''))} · {rec.get('estado','')}</p>
            <div class="stats-row">
                <div class="stat-pill">⚖ {len(dados)} candidatos</div>
                <div class="stat-pill">★ {len(favs)} favoritos</div>
                <div class="stat-pill">📢 {len(mch)} chamadas</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_sair,_=st.columns([2,8])
        with col_sair:
            if st.button("Sair da conta"):
                del st.session_state.recrutador_logado
                if "_menu" in st.session_state: del st.session_state["_menu"]
                st.rerun()

        tabs=st.tabs(["🔍 Busca","📢 Chamadas","★ Favoritos"])

        with tabs[0]:
            col1,col2,col3=st.columns(3)
            with col1: busca=st.text_input("Nome",placeholder="Buscar...")
            with col2:
                ad=["Todas"]+sorted(set(c["area"] for c in dados if c.get("area")))
                asel=st.selectbox("Área",ad)
            with col3: dsel=st.selectbox("Disponibilidade",["Todos","Disponível","Indisponível"])

            col1,col2,col3,col4,col5,col6=st.columns(6)
            with col1: osel=st.selectbox("OAB",["Todos","Sim","Não"])
            with col2: ssel=st.selectbox("Selo",["Todos","Verificado","Recomendado","Destaque","Experiente"])
            with col3:
                dsc=st.selectbox("DISC",["Todos","D — Dominante","I — Influente","S — Estável","C — Conformidade"])
                if dsc!="Todos": st.markdown(f'<div style="background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.1);border-radius:8px;padding:8px 12px;font-size:11px;color:rgba(255,255,255,0.6);margin-top:4px">ℹ {DISC_EXPLICACOES_FILTRO.get(dsc,"")}</div>', unsafe_allow_html=True)
            with col4: csel=st.selectbox("Concurso",["Todos","Concursando","Não concursando"])
            with col5: sisel=st.text_input("Sistema",placeholder="Ex: Eproc")
            with col6: emin=st.number_input("Exp. mín.",min_value=0,max_value=20,value=0)

            fi=dados
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

            st.markdown(f'<p style="font-size:13px;color:rgba(255,255,255,0.4);margin:1rem 0 0.5rem">{len(fi)} candidato(s)</p>', unsafe_allow_html=True)

            for i,cand in enumerate(fi):
                cor=cor_avatar(cand["nome"]); dc=cand.get("disponibilidade","Não")
                badge='<span class="badge-sim">● Disponível</span>' if dc=="Sim" else '<span class="badge-nao">● Indisponível</span>'
                ec=cand.get("email",""); ifav=ec in favs; fi_icon="★" if ifav else "☆"

                with st.container():
                    st.markdown(f"""
                    <div class="cand-card">
                        <div style="display:flex;align-items:center;justify-content:space-between;gap:12px">
                            <div style="display:flex;align-items:center;gap:14px;flex:1">
                                <div class="avatar" style="background:{cor}">{iniciais(cand['nome'])}</div>
                                <div>
                                    <p class="cand-name">{cand['nome']}</p>
                                    <p class="cand-sub">{cand.get('formacao','—')} · {cand.get('instituicao','—')} · {cand.get('area','—')}</p>
                                    <div style="margin-top:4px">{html_selos(cand)}{html_disc_badge(cand)}{html_concurso_badge(cand)}</div>
                                </div>
                            </div>
                            <div style="flex-shrink:0">{badge}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    ca,cb,cc=st.columns([6,2,2])
                    with cb:
                        if st.button(f"{fi_icon} Fav",key=f"fv_{i}"):
                            if ifav: favs.remove(ec)
                            else: favs.append(ec)
                            aba_recrutadores.update_cell(idx_r+2,12,", ".join(favs))
                            st.session_state.recrutador_logado=aba_recrutadores.get_all_records()[idx_r]; st.rerun()
                    with cc:
                        if st.button("Ver →",key=f"rb_{i}"):
                            st.session_state.cand_rec=cand; st.rerun()

                if ec in anots: st.markdown(f'<div class="info-card" style="margin-top:-6px;margin-bottom:8px;font-size:12px">📝 {anots[ec]}</div>', unsafe_allow_html=True)

                if st.session_state.get("cand_rec")==cand:
                    with st.expander("Perfil completo",expanded=True):
                        c1,c2,c3=st.columns(3)
                        for cl,lb,vl in [(c1,"OAB",cand.get("oab","—")),(c2,"Órgãos",cand.get("experiencia_orgaos","—") or "—"),(c3,"Sistemas",cand.get("sistemas","—") or "—")]:
                            with cl: st.markdown(f'<div class="metric-box"><p class="metric-label">{lb}</p><p class="metric-value" style="font-size:13px">{vl}</p></div>', unsafe_allow_html=True)
                        if cand.get("disc"): st.markdown(render_disc_perfil(cand.get("disc")), unsafe_allow_html=True)
                        if cand.get("resumo"): st.markdown(f'<div class="info-card" style="margin-top:1rem">{cand.get("resumo")}</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="info-card" style="margin-top:0.5rem">✉ {cand.get("email","—")}</div>', unsafe_allow_html=True)
                        na=anots.get(ec,"")
                        nn=st.text_area("",value=na,height=80,key=f"nt_{i}",placeholder="Anotação privada...")
                        cs,cf=st.columns(2)
                        with cs:
                            if st.button("Salvar",key=f"sv_{i}"):
                                anots[ec]=nn
                                aba_recrutadores.update_cell(idx_r+2,13,"|".join([f"{k}::{v}" for k,v in anots.items()]))
                                st.success("Salvo!"); st.rerun()
                        with cf:
                            if st.button("Fechar",key=f"fc_{i}"):
                                del st.session_state["cand_rec"]; st.rerun()

        with tabs[1]:
            ch_col,btn_col=st.columns([8,3])
            with ch_col: st.markdown('<p style="font-size:15px;font-weight:700;color:#ffffff">Minhas Chamadas</p>', unsafe_allow_html=True)
            with btn_col:
                if st.button("+ Nova Chamada",key="nch"):
                    st.session_state["criar_ch"]=True; st.rerun()

            if st.session_state.get("criar_ch"):
                with st.expander("Nova Chamada",expanded=True):
                    st.markdown(f'<div class="disclaimer-box">{DISCLAIMER_CHAMADA}</div>', unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)
                    tch=st.text_input("Título da vaga *",placeholder="Ex: Assessor Jurídico — 3ª Promotoria de Jaraguá do Sul")
                    c1,c2=st.columns(2)
                    with c1: och=st.text_input("Nome do órgão *",value=ra.get("nome_orgao",""))
                    with c2: toch=st.selectbox("Tipo de órgão *",["Selecione..."]+ORGAOS)
                    c1,c2,c3=st.columns(3)
                    with c1: ach=st.selectbox("Área *",["Selecione..."]+AREAS)
                    with c2: ech=st.selectbox("Estado *",["Selecione..."]+ESTADOS,index=ESTADOS.index(rec.get("estado","SC"))+1 if rec.get("estado","") in ESTADOS else 0)
                    with c3: mch_=st.text_input("Município *",value=ra.get("municipio",""))
                    rch=st.text_area("Requisitos *",height=80,placeholder="Descreva os requisitos...")
                    c1,c2,c3=st.columns(3)
                    with c1: remch=st.text_input("Remuneração *",placeholder="Ex: R$ 4.500,00")
                    with c2: regch=st.selectbox("Regime *",["Selecione..."]+REGIMES)
                    with c3: vch=st.number_input("Vagas *",min_value=1,max_value=20,value=1)
                    c1,c2=st.columns(2)
                    with c1: fsch=st.selectbox("Forma de seleção *",["Selecione..."]+FORMAS_SELECAO)
                    with c2: prch=st.date_input("Prazo *",min_value=date.today())

                    st.markdown("<br>", unsafe_allow_html=True)
                    c1,c2=st.columns(2)
                    with c1:
                        if st.button("Cancelar",key="cch"): del st.session_state["criar_ch"]; st.rerun()
                    with c2:
                        if st.button("Publicar Chamada →",key="pch"):
                            ok=all([tch,och,toch!="Selecione...",ach!="Selecione...",ech!="Selecione...",mch_,rch,remch,regch!="Selecione...",fsch!="Selecione..."])
                            if not ok: st.error("Preencha todos os campos.")
                            else:
                                aba_chamadas.append_row([gerar_id_chamada(),tch,och,toch,ach,ech,mch_,rch,remch,regch,fsch,str(vch),prch.strftime("%d/%m/%Y"),"aberto",rec["email"],"",datetime.now().strftime("%d/%m/%Y")])
                                del st.session_state["criar_ch"]; st.success("Chamada publicada!"); st.rerun()

            if not mch: st.info("Você ainda não publicou nenhuma Chamada.")
            else:
                for i,ch in enumerate(mch):
                    ab=chamada_aberta(ch); ins=inscritos_chamada(ch); n=len(ins)
                    sb='<span class="badge-aberta">● Aberta</span>' if ab else '<span class="badge-encerrada">● Encerrada</span>'
                    st.markdown(f"""
                    <div class="chamada-card">
                        <div style="display:flex;justify-content:space-between;align-items:center">
                            <div>
                                <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px">{sb}<span style="font-size:11px;color:rgba(255,255,255,0.4)">📅 {ch.get('prazo','—')}</span></div>
                                <p style="font-size:15px;font-weight:700;color:#ffffff;margin:0 0 4px">{ch.get('titulo','—')}</p>
                                <p style="font-size:12px;color:rgba(255,255,255,0.45);margin:0">{ch.get('municipio','—')}/{ch.get('estado','—')} · {ch.get('area','—')}</p>
                            </div>
                            <div style="text-align:right">
                                <p style="font-size:28px;font-weight:800;color:#f0c040;margin:0">{n}</p>
                                <p style="font-size:11px;color:rgba(255,255,255,0.4);margin:0">inscrito(s)</p>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    cv,ce=st.columns([8,3])
                    with cv:
                        if st.button("Ver inscritos",key=f"vi_{i}"):
                            st.session_state[f"vi_ch_{i}"]=not st.session_state.get(f"vi_ch_{i}",False); st.rerun()
                    with ce:
                        if ab:
                            if st.button("Encerrar",key=f"enc_{i}"):
                                tc=aba_chamadas.get_all_records()
                                idx=next((j for j,c in enumerate(tc) if c.get("id")==ch.get("id")),None)
                                if idx is not None: aba_chamadas.update_cell(idx+2,14,"encerrado")
                                st.success("Encerrada."); st.rerun()

                    if st.session_state.get(f"vi_ch_{i}"):
                        with st.expander("Painel de inscritos",expanded=True):
                            if not ins: st.info("Nenhum inscrito ainda.")
                            else:
                                tc=aba_candidatos.get_all_records()
                                id_=[c for c in tc if c.get("email","") in ins]
                                c1,c2,c3=st.columns(3)
                                with c1: st.markdown(f'<div class="metric-box"><p class="metric-label">Total</p><p class="metric-value">{len(id_)}</p></div>', unsafe_allow_html=True)
                                with c2: st.markdown(f'<div class="metric-box"><p class="metric-label">Com OAB</p><p class="metric-value">{sum(1 for c in id_ if c.get("oab")=="Sim")}</p></div>', unsafe_allow_html=True)
                                with c3: st.markdown(f'<div class="metric-box"><p class="metric-label">Disponíveis</p><p class="metric-value">{sum(1 for c in id_ if c.get("disponibilidade")=="Sim")}</p></div>', unsafe_allow_html=True)

                                dc={}
                                for c in id_:
                                    d=c.get("disc","")
                                    if d: dc[d]=dc.get(d,0)+1
                                if dc:
                                    st.markdown('<p class="section-label">DISC</p>', unsafe_allow_html=True)
                                    cols=st.columns(4)
                                    for di,l in enumerate(["D","I","S","C"]):
                                        with cols[di]: st.markdown(f'<div class="metric-box" style="background:{DISC_CORES_BADGE.get(l,"rgba(255,255,255,0.06)")}"><p class="metric-label" style="color:{DISC_TEXTO_BADGE.get(l,"#fff")}">{DISC_LABEL.get(l,"")}</p><p class="metric-value" style="color:{DISC_TEXTO_BADGE.get(l,"#fff")}">{dc.get(l,0)}</p></div>', unsafe_allow_html=True)

                                st.markdown('<p class="section-label">Perfis inscritos</p>', unsafe_allow_html=True)
                                for cand in id_:
                                    cor=cor_avatar(cand["nome"])
                                    st.markdown(f"""
                                    <div class="cand-card" style="margin-bottom:8px">
                                        <div style="display:flex;align-items:center;gap:14px">
                                            <div class="avatar" style="background:{cor}">{iniciais(cand['nome'])}</div>
                                            <div style="flex:1">
                                                <p class="cand-name">{cand['nome']}</p>
                                                <p class="cand-sub">{cand.get('formacao','—')} · {cand.get('area','—')}</p>
                                                <div style="margin-top:4px">{html_selos(cand)}{html_disc_badge(cand)}</div>
                                            </div>
                                            <div style="font-size:12px;color:rgba(255,255,255,0.5)">✉ {cand.get('email','—')}</div>
                                        </div>
                                    </div>
                                    """, unsafe_allow_html=True)

        with tabs[2]:
            fd=[c for c in dados if c.get("email","") in favs]
            if not fd: st.info("Nenhum favorito ainda.")
            else:
                for i,cand in enumerate(fd):
                    cor=cor_avatar(cand["nome"]); ec=cand.get("email",""); nt=anots.get(ec,"")
                    with st.container(border=False):
                        st.markdown(f"""
                        <div class="cand-card">
                            <div style="display:flex;align-items:center;gap:14px">
                                <div class="avatar" style="background:{cor}">{iniciais(cand['nome'])}</div>
                                <div style="flex:1">
                                    <p class="cand-name">{cand['nome']}</p>
                                    <p class="cand-sub">{cand.get('formacao','—')} · {cand.get('area','—')}</p>
                                    {html_selos(cand)}
                                    {'<p style="font-size:11px;color:rgba(255,255,255,0.4);margin-top:4px">📝 '+nt+'</p>' if nt else ''}
                                </div>
                                <div>{'<span class="badge-sim">● Disponível</span>' if cand.get('disponibilidade')=='Sim' else '<span class="badge-nao">● Indisponível</span>'}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        if st.button("✕ Remover",key=f"rf_{i}"):
                            favs.remove(ec)
                            aba_recrutadores.update_cell(idx_r+2,12,", ".join(favs)); st.rerun()

    elif "cadastro_rec" not in st.session_state:
        st.markdown("""
        <div class="hero-card">
            <h1 class="page-title">Área do<br><em>Recrutador.</em></h1>
            <p class="page-sub">Acesse o banco de talentos jurídicos certificados</p>
        </div>
        """, unsafe_allow_html=True)

        tabs=st.tabs(["Entrar","Criar conta"])
        with tabs[0]:
            st.markdown('<p style="font-size:16px;font-weight:700;color:#ffffff;margin:1rem 0">Acesse sua conta</p>', unsafe_allow_html=True)
            el=st.text_input("E-mail institucional",key="le")
            sl=st.text_input("Senha",type="password",key="ls")
            if st.button("Entrar →",key="btn_login"):
                if el and sl:
                    recs=aba_recrutadores.get_all_records(); sh=hash_senha(sl)
                    enc=next((r for r in recs if r["email"]==el and r["senha"]==sh and r["status"]=="ativo"),None)
                    if enc: st.session_state.recrutador_logado=enc; st.rerun()
                    else: st.error("E-mail ou senha incorretos, ou conta ainda não aprovada.")
                else: st.error("Preencha e-mail e senha.")
        with tabs[1]:
            st.markdown('<p style="font-size:15px;font-weight:700;color:#ffffff;margin:1rem 0 0.5rem">Criar conta</p>', unsafe_allow_html=True)
            st.markdown('<p style="font-size:13px;color:rgba(255,255,255,0.45);margin-bottom:1rem">4 etapas rápidas. Conta ativada após validação institucional.</p>', unsafe_allow_html=True)
            if st.button("Começar →",key="btn_cad"):
                st.session_state.cadastro_rec={"etapa":1}; st.rerun()

    else:
        et=st.session_state.cadastro_rec.get("etapa",1)
        st.markdown(barra_etapas(et,4), unsafe_allow_html=True)

        if et==1:
            st.markdown('<p class="step-title">Etapa 1 de 4</p>', unsafe_allow_html=True)
            st.markdown('<p class="step-desc">Onde você atua?</p>', unsafe_allow_html=True)
            est=st.selectbox("Estado *",["Selecione..."]+ESTADOS)
            mun=st.text_input("Município *",placeholder="Ex: Florianópolis")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Próximo →"):
                if est=="Selecione..." or not mun: st.error("Preencha todos os campos.")
                else:
                    st.session_state.cadastro_rec["estado"]=est; st.session_state.cadastro_rec["municipio"]=mun
                    st.session_state.cadastro_rec["etapa"]=2; st.rerun()

        elif et==2:
            st.markdown('<p class="step-title">Etapa 2 de 4</p>', unsafe_allow_html=True)
            st.markdown('<p class="step-desc">Qual é o seu órgão?</p>', unsafe_allow_html=True)
            org=st.selectbox("Tipo de órgão *",["Selecione..."]+ORGAOS)
            nom=st.text_input("Nome do órgão *",placeholder="Ex: MPSC — 3ª Promotoria de Jaraguá do Sul")
            st.markdown("<br>", unsafe_allow_html=True)
            c1,c2=st.columns(2)
            with c1:
                if st.button("← Voltar"): st.session_state.cadastro_rec["etapa"]=1; st.rerun()
            with c2:
                if st.button("Próximo →"):
                    if org=="Selecione..." or not nom: st.error("Preencha todos os campos.")
                    else:
                        st.session_state.cadastro_rec["orgao"]=org; st.session_state.cadastro_rec["nome_orgao"]=nom
                        st.session_state.cadastro_rec["etapa"]=3; st.rerun()

        elif et==3:
            st.markdown('<p class="step-title">Etapa 3 de 4</p>', unsafe_allow_html=True)
            st.markdown('<p class="step-desc">Seu perfil</p>', unsafe_allow_html=True)
            car=st.selectbox("Cargo *",["Selecione..."]+CARGOS)
            ars=st.multiselect("Áreas *",AREAS)
            st.markdown("<br>", unsafe_allow_html=True)
            c1,c2=st.columns(2)
            with c1:
                if st.button("← Voltar"): st.session_state.cadastro_rec["etapa"]=2; st.rerun()
            with c2:
                if st.button("Próximo →"):
                    if car=="Selecione..." or not ars: st.error("Preencha todos os campos.")
                    else:
                        st.session_state.cadastro_rec["cargo"]=car; st.session_state.cadastro_rec["areas"]=", ".join(ars)
                        st.session_state.cadastro_rec["etapa"]=4; st.rerun()

        elif et==4:
            st.markdown('<p class="step-title">Etapa 4 de 4</p>', unsafe_allow_html=True)
            st.markdown('<p class="step-desc">Crie seu acesso</p>', unsafe_allow_html=True)
            nr=st.text_input("Nome completo *")
            er=st.text_input("E-mail institucional *",placeholder="nome@mpsc.mp.br")
            dv=["mpsc.mp.br","tjsc.jus.br","sc.def.br","pge.sc.gov.br","trf4.jus.br","jfsc.jus.br","mpf.mp.br","agu.gov.br","pgfn.gov.br"]
            if er and "@" in er:
                if er.split("@")[-1] in dv: st.markdown('<div class="info-box">✓ E-mail institucional reconhecido.</div>', unsafe_allow_html=True)
                else: st.warning("Domínio não reconhecido. Validação manual.")
            sr=st.text_input("Senha *",type="password"); sc=st.text_input("Confirmar senha *",type="password")
            st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
            cr=st.checkbox("Li e aceito a Política de Privacidade e os Termos de Uso. Comprometo-me a utilizar os dados exclusivamente para fins de seleção profissional, nos termos da LGPD.")
            st.markdown("<br>", unsafe_allow_html=True)
            c1,c2=st.columns(2)
            with c1:
                if st.button("← Voltar"): st.session_state.cadastro_rec["etapa"]=3; st.rerun()
            with c2:
                if st.button("Finalizar →"):
                    if not nr or not er or not sr: st.error("Preencha todos os campos.")
                    elif sr!=sc: st.error("Senhas não coincidem.")
                    elif len(sr)<6: st.error("Senha mínima: 6 caracteres.")
                    elif not cr: st.error("Aceite os Termos para continuar.")
                    else:
                        dr=st.session_state.cadastro_rec
                        aba_recrutadores.append_row([nr,er,hash_senha(sr),dr["estado"],dr["municipio"],dr["orgao"],dr["nome_orgao"],dr["cargo"],dr["areas"],"pendente",datetime.now().strftime("%d/%m/%Y %H:%M")])
                        del st.session_state.cadastro_rec
                        st.success("Cadastro realizado! Aguarde a ativação."); st.balloons()

# ── PÁGINAS LEGAIS ────────────────────────────────────────────────────────────
elif pagina in ["privacidade","termos"]:
    is_priv = pagina=="privacidade"
    st.markdown(f"""
    <div class="hero-card">
        <h1 class="page-title">{'Política de<br><em>Privacidade.</em>' if is_priv else 'Termos<br><em>de Uso.</em>'}</h1>
        <p class="page-sub">Versão 1.0</p>
    </div>
    """, unsafe_allow_html=True)

    if is_priv:
        secoes=[
            ("1. Identificação do Controlador",[("p","O JurisBank é operado por [RAZÃO SOCIAL A PREENCHER], CNPJ [A PREENCHER], com sede em [ENDEREÇO A PREENCHER]."),("p","DPO: [E-MAIL A PREENCHER]")]),
            ("2. Dados Coletados",[("l",["Nome completo e e-mail","Formação e instituição","OAB (quando aplicável)","Histórico em órgãos públicos","Sistemas jurídicos","Perfil DISC","Documentos de referência (quando fornecidos)","E-mail institucional e senha (recrutadores)"])]),
            ("3. Finalidade",[("l",["Gestão de perfis de candidatos","Atribuição de selos de certificação","Viabilizar busca por recrutadores aprovados","Gestão de inscrições em Chamadas","Melhoria dos serviços"])]),
            ("4. Base Legal (LGPD)",[("l",["Consentimento (Art. 7º, I)","Legítimo interesse (Art. 7º, IX)","Obrigação legal (Art. 7º, II)"])]),
            ("5. Direitos dos Titulares",[("l",["Acesso, correção e eliminação dos dados","Portabilidade","Revogação do consentimento a qualquer momento"]),("p","Contato: [E-MAIL DO DPO A PREENCHER]")]),
            ("6. Contato",[("l",["E-mail: [A PREENCHER]","ANPD: www.gov.br/anpd"])]),
        ]
    else:
        secoes=[
            ("1. Aceitação",[("p","Ao usar o JurisBank você concorda com estes Termos e com a Política de Privacidade.")]),
            ("2. Chamadas",[("p","Chamadas são publicações de vagas de cargos de livre nomeação por recrutadores aprovados. O JurisBank é plataforma de aproximação — o uso do ius indicandum é de responsabilidade exclusiva do recrutador."),("p","A publicação não configura processo seletivo vinculante, concurso público ou compromisso de contratação.")]),
            ("3. Impessoalidade e Nepotismo",[("l",["Princípio da impessoalidade (art. 37, caput, CF/88)","Vedação ao nepotismo (SV nº 13 do STF)","Resolução CNJ nº 07/2005 e normas do CNMP"]),("p","O recrutador é o único responsável pelo cumprimento dessas normas.")]),
            ("4. Obrigações",[("l",["Fornecer informações verdadeiras","Não usar a plataforma para fins ilegais","Não compartilhar dados de candidatos com terceiros"])]),
            ("5. Responsabilidades",[("p","O JurisBank não garante contratações, não valida documentos independentemente e não se responsabiliza por decisões dos recrutadores.")]),
            ("6. Foro",[("p","Comarca de [MUNICÍPIO A PREENCHER], Estado de [ESTADO A PREENCHER].")]),
        ]

    for ts,cont in secoes:
        st.markdown(f'<div class="doc-sub">{ts}</div>', unsafe_allow_html=True)
        for tp,tx in cont:
            if tp=="p": st.markdown(f'<p class="doc-body">{tx}</p>', unsafe_allow_html=True)
            elif tp=="l":
                for it in tx: st.markdown(f'<p class="doc-item">• {it}</p>', unsafe_allow_html=True)
        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    st.markdown(f'<p style="font-size:12px;color:rgba(255,255,255,0.25);text-align:center">JurisBank — Versão 1.0 — {datetime.now().strftime("%d/%m/%Y")}</p>', unsafe_allow_html=True)

else:
    st.query_params["p"] = "inicio"
    st.rerun()