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

[data-testid="stAppViewContainer"] {
    background: #eef3fe;
    min-height: 100vh;
}
.main .block-container { padding: 0 2.5rem 3rem; max-width: 1100px; background: transparent; }

/* ── Topbar ── */
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

/* ── Cards ── */
.hero-card { background: #ffffff; border: 1.5px solid #d0dcfa; border-radius: 20px; padding: 2rem 2.5rem; margin-bottom: 1.5rem; }
.page-title { font-family: 'Playfair Display',serif; font-size: clamp(28px,4vw,42px); font-weight: 900; color: #0d1f4e; margin: 0 0 8px; letter-spacing: -1px; line-height: 1.1; }
.page-title em { font-style: normal; background: linear-gradient(135deg,#c8960c,#f0c040); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
.page-sub { font-size: 15px; color: #6080c0; margin: 0; }
.stats-row { display: flex; gap: 12px; margin-top: 1.5rem; flex-wrap: wrap; }
.stat-pill { background: #eef3fe; border-radius: 99px; padding: 7px 16px; font-size: 13px; font-weight: 600; color: #1a3a8f; border: 1px solid #c5d5f5; }

.cand-card { background: #ffffff; border: 1.5px solid #d0dcfa; border-radius: 16px; padding: 1.2rem 1.5rem; margin-bottom: 8px; transition: all 0.2s; }
.cand-card:hover { border-color: #4070f4; box-shadow: 0 6px 24px rgba(64,112,244,0.1); transform: translateY(-1px); }
.seletivo-card { background: #ffffff; border: 1.5px solid #d0dcfa; border-radius: 16px; padding: 1.2rem 1.5rem; margin-bottom: 10px; transition: all 0.2s; }
.seletivo-card:hover { border-color: #4070f4; box-shadow: 0 6px 24px rgba(64,112,244,0.1); }

.avatar { width: 46px; height: 46px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 14px; font-weight: 700; flex-shrink: 0; color: white; }
.cand-name { font-size: 15px; font-weight: 700; color: #0d1f4e; margin: 0 0 3px; }
.cand-sub { font-size: 12px; color: #8090b8; margin: 0; }

.badge-sim { background: #e6f4ea; color: #1a7a4a; padding: 4px 12px; border-radius: 99px; font-size: 11px; font-weight: 700; border: 1px solid #b0dfc0; }
.badge-nao { background: #fff3e8; color: #c05a1a; padding: 4px 12px; border-radius: 99px; font-size: 11px; font-weight: 700; border: 1px solid #f0c8a0; }
.badge-aberto { background: #e6f4ea; color: #1a7a4a; padding: 3px 10px; border-radius: 99px; font-size: 11px; font-weight: 700; border: 1px solid #b0dfc0; }
.badge-encerrado { background: #f4f4f4; color: #888; padding: 3px 10px; border-radius: 99px; font-size: 11px; font-weight: 700; border: 1px solid #ddd; }
.badge-inscrito { background: #e8effe; color: #1a3a8f; padding: 3px 10px; border-radius: 99px; font-size: 11px; font-weight: 700; border: 1px solid #b0c5f5; }
.badge-pago { background: #fff8e6; color: #b45309; padding: 3px 10px; border-radius: 99px; font-size: 11px; font-weight: 700; border: 1px solid #fde68a; }

.selo { display: inline-block; font-size: 10px; font-weight: 700; padding: 3px 10px; border-radius: 99px; margin-right: 4px; margin-top: 4px; }
.selo-verificado { background: #e8effe; color: #1a3a8f; border: 1px solid #b0c5f5; }
.selo-recomendado { background: #e6f4ea; color: #15803d; border: 1px solid #b0dfc0; }
.selo-destaque { background: #fff8e6; color: #b45309; border: 1px solid #fde68a; }
.selo-experiente { background: #f3effe; color: #6d28d9; border: 1px solid #ddd6fe; }

.metric-box { background: #ffffff; border: 1.5px solid #d0dcfa; border-radius: 14px; padding: 16px 18px; text-align: center; }
.metric-label { font-size: 11px; font-weight: 600; color: #8090b8; text-transform: uppercase; letter-spacing: .08em; margin: 0 0 6px; }
.metric-value { font-size: 24px; font-weight: 800; color: #0d1f4e; margin: 0; }

.teaser-box { background: linear-gradient(135deg,#0d1f4e,#1a3a8f); border-radius: 16px; padding: 20px 24px; text-align: center; }
.teaser-num { font-family: 'Playfair Display',serif; font-size: 36px; font-weight: 900; color: #f0c040; margin: 0; }
.teaser-label { font-size: 12px; color: rgba(255,255,255,0.65); margin: 4px 0 0; }

.profile-name { font-family: 'Playfair Display',serif; font-size: 24px; font-weight: 900; color: #0d1f4e; margin: 0 0 6px; }
.section-label { font-size: 11px; font-weight: 700; color: #4070f4; text-transform: uppercase; letter-spacing: .1em; margin: 1.5rem 0 0.5rem; }
.info-card { background: #f4f7fe; border: 1.5px solid #d0dcfa; border-radius: 12px; padding: 14px 18px; font-size: 14px; color: #3a5a9a; line-height: 1.6; }
.custom-divider { height: 1px; background: #e8f0fe; margin: 1.5rem 0; }
.info-box { background: #e8effe; border: 1px solid #b0c5f5; border-radius: 10px; padding: 10px 14px; font-size: 13px; color: #1a3a8f; margin-top: 8px; font-weight: 500; }
.lock-box { background: #f4f7fe; border: 1.5px solid #d0dcfa; border-radius: 12px; padding: 14px 18px; font-size: 13px; color: #8090b8; text-align: center; }
.disclaimer-box { background: #fff8e6; border: 1px solid #fde68a; border-radius: 10px; padding: 12px 16px; font-size: 12px; color: #92400e; line-height: 1.6; margin-top: 1rem; }
.aviso-pago { background: linear-gradient(135deg,#0d1f4e,#1a3a8f); border-radius: 16px; padding: 20px 24px; text-align: center; margin: 1rem 0; }

.step-bar { display: flex; gap: 8px; margin-bottom: 2rem; }
.step { flex: 1; height: 4px; border-radius: 99px; background: #d0dcfa; }
.step.active { background: linear-gradient(135deg,#c8960c,#f0c040); }
.step.done { background: #1a7a4a; }
.step-title { font-size: 13px; font-weight: 600; color: #8090b8; margin-bottom: 0.3rem; }
.step-desc { font-family: 'Playfair Display',serif; font-size: 22px; font-weight: 700; color: #0d1f4e; margin-bottom: 1.5rem; }

.doc-sub { font-size: 12px; font-weight: 700; color: #4070f4; text-transform: uppercase; letter-spacing: .08em; margin: 1.5rem 0 0.5rem; }
.doc-body { font-size: 14px; color: #3a5a9a; line-height: 1.8; margin-bottom: 0.8rem; }
.doc-item { font-size: 14px; color: #3a5a9a; line-height: 1.8; padding-left: 1rem; }

/* Planos */
.plano-card { border-radius: 16px; padding: 24px; border: 1.5px solid #d0dcfa; background: #ffffff; }
.plano-card.destaque { background: linear-gradient(135deg,#0d1f4e,#1a3a8f); border-color: transparent; }
.plano-nome { font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: .08em; margin-bottom: 8px; }
.plano-preco { font-family: 'Playfair Display',serif; font-size: 32px; font-weight: 900; margin: 0 0 4px; }
.plano-periodo { font-size: 12px; margin-bottom: 16px; }
.plano-item { font-size: 13px; padding: 4px 0; display: flex; gap: 8px; align-items: flex-start; }

/* Botões */
.stButton button { background: linear-gradient(135deg,#c8960c,#f0c040) !important; color: #0d1f4e !important; border: none !important; border-radius: 10px !important; font-family: 'Sora',sans-serif !important; font-weight: 700 !important; padding: 0.6rem 2rem !important; font-size: 14px !important; transition: all 0.2s !important; }
.stButton button:hover { opacity: 0.9 !important; transform: translateY(-1px) !important; }
div[data-testid="column"]:last-child .stButton button,
div[data-testid="column"]:nth-last-child(2) .stButton button { background: #e8f0fe !important; color: #1a3a8f !important; border: 1.5px solid #c5d5f5 !important; border-radius: 10px !important; padding: 0.4rem 1rem !important; font-size: 12px !important; font-weight: 600 !important; width: 100%; }
div[data-testid="column"]:last-child .stButton button:hover,
div[data-testid="column"]:nth-last-child(2) .stButton button:hover { background: #4070f4 !important; color: white !important; border-color: #4070f4 !important; }
.stTextInput input, .stTextArea textarea { border-radius: 10px !important; border-color: #d0dcfa !important; background: #ffffff !important; color: #0d1f4e !important; font-family: 'Sora',sans-serif !important; font-size: 14px !important; }
.stTextInput input:focus, .stTextArea textarea:focus { border-color: #4070f4 !important; box-shadow: 0 0 0 3px rgba(64,112,244,0.1) !important; }
.stSelectbox > div > div { border-radius: 10px !important; border-color: #d0dcfa !important; background: #ffffff !important; }
.stRadio label, .stCheckbox label { color: #3a5a9a !important; }
.stMultiSelect > div > div { background: #ffffff !important; border-color: #d0dcfa !important; border-radius: 10px !important; }
label[data-baseweb="label"] { color: #3a5a9a !important; }
.stTabs [data-baseweb="tab-list"] { background: #e8f0fe !important; border-radius: 12px !important; padding: 4px !important; gap: 4px !important; }
.stTabs [data-baseweb="tab"] { background: transparent !important; color: #6080c0 !important; border-radius: 8px !important; }
.stTabs [aria-selected="true"] { background: #ffffff !important; color: #1a3a8f !important; font-weight: 700 !important; }
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

# ── Navegação ─────────────────────────────────────────────────────────────────
params = st.query_params
p = params.get("p", "inicio")
if isinstance(p, list): p = p[0]
if p not in ["inicio","candidatos","seletivos","cadastro","recrutador","privacidade","termos","recomendar"]:
    p = "inicio"
if "pagina" not in st.session_state or params.get("p"):
    st.session_state.pagina = p
pagina = st.session_state.pagina

# ── Constantes ────────────────────────────────────────────────────────────────
AVATAR_CORES = ["#1a3a8f","#2e7d5e","#7b3fa0","#c05a1a","#1a6b8a","#a04040","#3a6b2a"]
DISC_LABEL = {"D":"Dominante","I":"Influente","S":"Estável","C":"Conformidade"}
DISC_CORES_BADGE = {"D":"#fee2e2","I":"#fef9c3","S":"#dcfce7","C":"#eff6ff"}
DISC_TEXTO_BADGE = {"D":"#991b1b","I":"#854d0e","S":"#166534","C":"#1e3a8a"}
DISC_EXPLICACOES = {
    "D — Dominante":"Direto e decidido. Resolve problemas com rapidez.",
    "I — Influente":"Comunicativo e entusiasta. Excelente no atendimento ao público.",
    "S — Estável":"Paciente e confiável. Ideal para rotinas de gabinete.",
    "C — Conformidade":"Analítico e preciso. Excelente em pesquisa jurídica."
}
DISC_DETALHES = {
    "D":{"nome":"Dominante","resumo":"Direto, decidido e orientado a resultados.","pontos_fortes":"Resolve problemas com rapidez, assume responsabilidades, trabalha bem sob pressão.","no_gabinete":"Ideal para demandas que exigem agilidade e tomada de decisão rápida.","atencao":"Pode ser impaciente com processos lentos."},
    "I":{"nome":"Influente","resumo":"Comunicativo, entusiasta e orientado a pessoas.","pontos_fortes":"Excelente no atendimento ao público e trabalho em equipe.","no_gabinete":"Ideal para Ministérios Públicos ou Defensorias com alto volume de atendimento.","atencao":"Pode ter dificuldade com tarefas repetitivas."},
    "S":{"nome":"Estável","resumo":"Paciente, confiável e orientado a processos.","pontos_fortes":"Consistência, lealdade e capacidade de manter rotinas com qualidade.","no_gabinete":"Perfil ideal para gabinetes com rotinas estabelecidas.","atencao":"Pode ter dificuldade com mudanças repentinas."},
    "C":{"nome":"Conformidade","resumo":"Analítico, preciso e orientado à qualidade.","pontos_fortes":"Atenção aos detalhes, rigor técnico e pesquisa jurídica.","no_gabinete":"Ideal para assessorias que demandam análise de processos complexos.","atencao":"Pode ser perfeccionista. Precisa de clareza nas instruções."}
}
DESCRICOES_DISC = {"D":"Dominante — Direto, decidido e orientado a resultados.","I":"Influente — Comunicativo e orientado a pessoas.","S":"Estável — Paciente e orientado a processos.","C":"Conformidade — Analítico e orientado a qualidade."}
CONCURSOS = ["Não estou estudando para concurso","Juiz de Direito (TJ)","Juiz Federal (TRF)","Promotor de Justiça (MP Estadual)","Procurador da República (MPF)","Defensor Público Estadual","Defensor Público Federal (DPU)","Procurador do Estado (PGE)","Procurador Municipal","Delegado de Polícia","Auditor Fiscal / Receita Federal","Outro concurso jurídico"]
ESTADOS = ["AC","AL","AP","AM","BA","CE","DF","ES","GO","MA","MT","MS","MG","PA","PB","PR","PE","PI","RJ","RN","RS","RO","RR","SC","SP","SE","TO"]
ORGAOS = ["Tribunal de Justiça (TJ)","Ministério Público (MP)","Defensoria Pública","Procuradoria Geral do Estado (PGE)","Procuradoria Geral do Município (PGM)","Tribunal Regional Federal (TRF)","Ministério Público Federal (MPF)","Advocacia Geral da União (AGU)","Tribunal de Contas (TCE/TCU)","Outro"]
CARGOS = ["Juiz de Direito","Juiz Federal","Desembargador","Promotor de Justiça","Procurador de Justiça","Defensor Público","Procurador do Estado","Procurador Municipal","Servidor — RH / Gestão de Pessoas","Outro"]
AREAS = ["Criminal","Cível","Família e Sucessões","Execução Penal","Infância e Juventude","Fazenda Pública","Meio Ambiente","Moralidade Administrativa","Violência Doméstica","Direito Público","Direito Tributário","Consumidor","Saúde","Todas as áreas"]
REGIMES = ["Integral","Parcial","Remoto","Híbrido"]
FORMAS_SELECAO = ["Análise de currículo","Análise de currículo + entrevista","Entrevista","Análise de portfólio + entrevista","Processo simplificado"]
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
]
LETRAS_DISC = ["D","I","S","C"]
DISCLAIMER = "⚠️ O JurisBank atua exclusivamente como plataforma de aproximação. A publicação deste Seletivo não configura processo seletivo vinculante, concurso público ou compromisso de contratação. O uso do ius indicandum é de responsabilidade exclusiva do recrutador."

# ── Funções ───────────────────────────────────────────────────────────────────
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
    assunto = f"JurisBank — {nome_cand} solicitou sua avaliação"
    corpo = f"""<div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto">
        <div style="background:linear-gradient(135deg,#0d1f4e,#1a3a8f);padding:32px;text-align:center;border-radius:12px 12px 0 0">
            <h1 style="color:#ffffff;font-size:22px;margin:0">JurisBank</h1>
            <p style="color:rgba(255,255,255,0.6);font-size:12px;margin:4px 0 0;font-style:italic">ius indicandum</p>
        </div>
        <div style="padding:32px;background:#f4f6fc;border-radius:0 0 12px 12px">
            <h2 style="color:#0d1f4e;font-size:20px;margin:0 0 12px">Solicitação de avaliação</h2>
            <p style="color:#4a5568;font-size:15px;line-height:1.7;margin:0 0 20px">O profissional <strong>{nome_cand}</strong> indicou você como recomendador no JurisBank e solicita que você preencha uma avaliação do seu perfil profissional.</p>
            <div style="text-align:center;margin:28px 0">
                <a href="{link}" style="display:inline-block;padding:14px 36px;background:linear-gradient(135deg,#c8960c,#f0c040);color:#0d1f4e;font-weight:700;font-size:15px;border-radius:10px;text-decoration:none">Preencher avaliação →</a>
            </div>
            <p style="color:#8090b8;font-size:12px;border-top:1px solid #d0dcfa;padding-top:16px">Este link é exclusivo e de uso único. JurisBank — plataforma de aproximação entre profissionais do Direito e órgãos do sistema de justiça.</p>
        </div>
    </div>"""
    return enviar_email(email_rec, assunto, corpo)

def extrair_pdf(f):
    doc=fitz.open(stream=f.read(),filetype="pdf")
    return "".join(p.get_text() for p in doc)

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
    return f'<span style="font-size:10px;font-weight:700;padding:2px 8px;border-radius:99px;background:{DISC_CORES_BADGE.get(d,"#eff6ff")};color:{DISC_TEXTO_BADGE.get(d,"#1e3a8a")};margin-left:4px">{d} {DISC_LABEL.get(d,"")}</span>'

def html_conc(c):
    if c.get("concurso") and c.get("concurso")!="Não estou estudando para concurso":
        return '<span style="font-size:10px;font-weight:700;padding:2px 8px;border-radius:99px;background:#fff8e6;color:#b45309;margin-left:4px;border:1px solid #fde68a">📚 Concursando</span>'
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
        <p style="color:#3a5a9a;font-size:12px;margin:0 0 4px"><strong style="color:{tb}">Pontos fortes:</strong> {det.get('pontos_fortes','')}</p>
        <p style="color:#3a5a9a;font-size:12px;margin:0 0 4px"><strong style="color:{tb}">No gabinete:</strong> {det.get('no_gabinete','')}</p>
        <p style="color:#3a5a9a;font-size:12px;margin:0"><strong style="color:{tb}">Atenção:</strong> {det.get('atencao','')}</p>
    </div>"""

def modal_planos():
    with st.expander("💰 Ver planos e preços", expanded=st.session_state.get("ver_planos", False)):
        st.markdown('<p style="font-family:\'Playfair Display\',serif;font-size:22px;font-weight:900;color:#0d1f4e;margin-bottom:1.5rem">Planos e preços</p>', unsafe_allow_html=True)

        st.markdown('<p style="font-size:13px;font-weight:700;color:#4070f4;text-transform:uppercase;letter-spacing:.08em;margin-bottom:1rem">Para Candidatos</p>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""<div class="plano-card">
                <p class="plano-nome" style="color:#6080c0">Gratuito</p>
                <p class="plano-preco" style="color:#0d1f4e">R$ 0</p>
                <p class="plano-periodo" style="color:#8090b8">para sempre</p>
                <div class="plano-item" style="color:#3a5a9a">✅ Cadastro completo com selos</div>
                <div class="plano-item" style="color:#3a5a9a">✅ Aparecer no banco de talentos</div>
                <div class="plano-item" style="color:#3a5a9a">✅ Perfil DISC</div>
                <div class="plano-item" style="color:#3a5a9a">✅ Ver Seletivos abertos</div>
                <div class="plano-item" style="color:#8090b8">❌ Inscrição em Seletivos</div>
                <div class="plano-item" style="color:#8090b8">❌ Destaque no perfil</div>
            </div>""", unsafe_allow_html=True)
        with col2:
            st.markdown("""<div class="plano-card destaque">
                <p class="plano-nome" style="color:#f0c040">Ativo</p>
                <p class="plano-preco" style="color:#ffffff">R$ 29,90</p>
                <p class="plano-periodo" style="color:rgba(255,255,255,0.6)">/mês</p>
                <div class="plano-item" style="color:rgba(255,255,255,0.9)">✅ Tudo do gratuito</div>
                <div class="plano-item" style="color:rgba(255,255,255,0.9)">✅ Inscrição em Seletivos</div>
                <div class="plano-item" style="color:rgba(255,255,255,0.9)">✅ Destaque no perfil</div>
                <div class="plano-item" style="color:rgba(255,255,255,0.9)">✅ Notificações de Seletivos</div>
            </div>""", unsafe_allow_html=True)

        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
        st.markdown('<p style="font-size:13px;font-weight:700;color:#4070f4;text-transform:uppercase;letter-spacing:.08em;margin-bottom:1rem">Para Recrutadores — Pay-per-use</p>', unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        produtos = [
            ("🔍 1 perfil completo", "R$ 19,90", "Nome, e-mail, resumo e DISC"),
            ("🔍 5 perfis", "R$ 79,90", "Economia de 20%"),
            ("🔍 10 perfis", "R$ 139,90", "Economia de 30%"),
        ]
        for col, (nome, preco, desc) in zip([col1,col2,col3], produtos):
            with col:
                st.markdown(f"""<div class="plano-card" style="text-align:center">
                    <p style="font-size:14px;font-weight:700;color:#0d1f4e;margin-bottom:4px">{nome}</p>
                    <p style="font-family:'Playfair Display',serif;font-size:24px;font-weight:900;color:#0d1f4e;margin:0">{preco}</p>
                    <p style="font-size:12px;color:#8090b8;margin-top:4px">{desc}</p>
                </div>""", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""<div class="plano-card" style="text-align:center">
                <p style="font-size:14px;font-weight:700;color:#0d1f4e;margin-bottom:4px">📢 1 Seletivo (30 dias)</p>
                <p style="font-family:'Playfair Display',serif;font-size:24px;font-weight:900;color:#0d1f4e;margin:0">R$ 89,90</p>
                <p style="font-size:12px;color:#8090b8;margin-top:4px">Publicação + painel de inscritos</p>
            </div>""", unsafe_allow_html=True)
        with col2:
            st.markdown("""<div class="plano-card destaque" style="text-align:center">
                <p style="font-size:14px;font-weight:700;color:#f0c040;margin-bottom:4px">⚡ 10 perfis + 1 Seletivo</p>
                <p style="font-family:'Playfair Display',serif;font-size:24px;font-weight:900;color:#ffffff;margin:0">R$ 199,90</p>
                <p style="font-size:12px;color:rgba(255,255,255,0.6);margin-top:4px">Melhor custo-benefício</p>
            </div>""", unsafe_allow_html=True)

        st.markdown('<p style="font-size:11px;color:#8090b8;text-align:center;margin-top:1rem">Pagamentos em breve. Cadastre-se agora gratuitamente.</p>', unsafe_allow_html=True)

# ── TOPBAR ────────────────────────────────────────────────────────────────────
def render_topbar():
    nav = '<div class="topbar"><a class="topbar-logo" href="https://lcatolico.github.io/jurisbank/" target="_blank"><div class="topbar-logo-icon">⚖</div><div><span class="topbar-logo-name">JurisBank</span><span class="topbar-logo-sub">ius indicandum</span></div></a><div class="topbar-nav">'

    if rec_logado():
        rec = st.session_state.rec_logado
        nav += f'<a href="?p=recrutador" class="{"active" if pagina=="recrutador" else ""}">🏛 {rec["nome"].split()[0]}</a>'
        nav += '<a href="?p=seletivos" class="' + ("active" if pagina=="seletivos" else "") + '">📢 Seletivos</a>'
    elif cand_logado():
        cand = st.session_state.cand_logado
        nav += f'<a href="?p=inicio" class="{"active" if pagina=="inicio" else ""}">👤 {cand["nome"].split()[0]}</a>'
        nav += '<a href="?p=candidatos" class="' + ("active" if pagina=="candidatos" else "") + '">👥 Candidatos</a>'
        nav += '<a href="?p=seletivos" class="' + ("active" if pagina=="seletivos" else "") + '">📢 Seletivos</a>'
    else:
        nav += '<a href="?p=candidatos" class="' + ("active" if pagina=="candidatos" else "") + '">👥 Candidatos</a>'
        nav += '<a href="?p=seletivos" class="' + ("active" if pagina=="seletivos" else "") + '">📢 Seletivos</a>'
        nav += '<a href="?p=recrutador" class="btn-rec">🔐 Recrutador</a>'
        nav += '<a href="?p=cadastro" class="btn-cand">Cadastrar →</a>'

    nav += '</div></div>'
    st.markdown(nav, unsafe_allow_html=True)

render_topbar()

# ── PÁGINA: INÍCIO / DASHBOARD VISITANTE ─────────────────────────────────────
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
            <h1 class="page-title">Olá, <em>{cand['nome'].split()[0]}!</em></h1>
            <p class="page-sub">Seu perfil está ativo no JurisBank</p>
            <div class="stats-row">
                <div class="stat-pill">📢 {total_sel} Seletivos abertos</div>
                <div class="stat-pill">👥 {total_cands} candidatos no banco</div>
            </div>
        </div>""", unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f'<div class="metric-box"><p class="metric-label">Área</p><p class="metric-value" style="font-size:16px">{cand.get("area","—")}</p></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metric-box"><p class="metric-label">Disponível</p><p class="metric-value" style="font-size:16px">{cand.get("disponibilidade","—")}</p></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="metric-box"><p class="metric-label">Perfil DISC</p><p class="metric-value" style="font-size:16px">{cand.get("disc","—")}</p></div>', unsafe_allow_html=True)

        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📢 Ver Seletivos", use_container_width=True): ir("seletivos")
        with col2:
            if st.button("👥 Ver candidatos", use_container_width=True): ir("candidatos")
        with col3:
            if st.button("Sair da conta", use_container_width=True):
                del st.session_state.cand_logado; st.rerun()

        st.markdown('<p class="section-label">Meus selos</p>', unsafe_allow_html=True)
        st.markdown(f'<div class="info-card">{html_selos(cand) or "Nenhum selo ainda. Complete seu cadastro para receber selos."}</div>', unsafe_allow_html=True)

        if cand.get("disc"):
            st.markdown('<p class="section-label">Meu perfil DISC</p>', unsafe_allow_html=True)
            st.markdown(render_disc(cand["disc"]), unsafe_allow_html=True)

    else:
        # Dashboard visitante — teaser
        st.markdown(f"""<div class="hero-card">
            <h1 class="page-title">Banco de Talentos<br><em>Jurídicos.</em></h1>
            <p class="page-sub">Profissionais certificados para assessoria em Tribunais, Ministérios Públicos, Procuradorias e Defensorias</p>
        </div>""", unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f'<div class="teaser-box"><p class="teaser-num">{total_cands}</p><p class="teaser-label">Profissionais cadastrados</p></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="teaser-box"><p class="teaser-num">{total_disp}</p><p class="teaser-label">Disponíveis agora</p></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="teaser-box"><p class="teaser-num">{total_cert}</p><p class="teaser-label">Perfis certificados</p></div>', unsafe_allow_html=True)
        with col4:
            st.markdown(f'<div class="teaser-box"><p class="teaser-num">{total_sel}</p><p class="teaser-label">Seletivos abertos</p></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([2,2,2])
        with col1:
            if st.button("📄 Cadastrar agora — é grátis", use_container_width=True): ir("cadastro")
        with col2:
            if st.button("🔑 Já tenho cadastro", use_container_width=True):
                st.session_state["login_cand"] = True; st.rerun()
        with col3:
            if st.button("💰 Ver planos", use_container_width=True):
                st.session_state["ver_planos"] = not st.session_state.get("ver_planos", False); st.rerun()

        if st.session_state.get("ver_planos"):
            modal_planos()

        if st.session_state.get("login_cand"):
            st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
            st.markdown('<p style="font-size:15px;font-weight:700;color:#0d1f4e;margin-bottom:1rem">Acessar minha conta</p>', unsafe_allow_html=True)
            em = st.text_input("Seu e-mail cadastrado", key="em_login_cand")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Entrar →", key="btn_login_cand"):
                    tc = aba_candidatos.get_all_records()
                    cf = next((c for c in tc if c.get("email","").lower()==em.lower()), None)
                    if cf: st.session_state.cand_logado=cf; st.session_state["login_cand"]=False; st.rerun()
                    else: st.error("E-mail não encontrado.")
            with col2:
                if st.button("Cancelar", key="btn_canc_cand"):
                    st.session_state["login_cand"]=False; st.rerun()

        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
        st.markdown('<p style="font-size:15px;font-weight:700;color:#0d1f4e;margin-bottom:0.5rem">Receba avisos de novos Seletivos</p>', unsafe_allow_html=True)
        st.markdown('<p style="font-size:13px;color:#8090b8;margin-bottom:1rem">Deixe seu e-mail. Quando surgir um Seletivo na sua área, você é o primeiro a saber.</p>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1: ei = st.text_input("Seu e-mail", key="ei_home")
        with col2: ai = st.multiselect("Áreas", AREAS, key="ai_home")
        with col3: sti = st.multiselect("Estados", ESTADOS, key="sti_home")
        if st.button("Quero receber avisos", key="bint_home"):
            if not ei or not ai: st.error("Preencha e-mail e área.")
            else:
                aba_interesses.append_row([ei,", ".join(ai),", ".join(sti),datetime.now().strftime("%d/%m/%Y")])
                st.success("Pronto! Você será avisado quando surgir um Seletivo compatível.")

# ── PÁGINA: CANDIDATOS ────────────────────────────────────────────────────────
elif pagina == "candidatos":
    dados = aba_candidatos.get_all_records()
    if "cand_sel" not in st.session_state: st.session_state.cand_sel = None

    if st.session_state.cand_sel:
        c = st.session_state.cand_sel; cor = cor_avatar(c["nome"])
        if st.button("← Voltar"): st.session_state.cand_sel=None; st.rerun()

        st.markdown(f"""<div class="hero-card">
            <div style="display:flex;align-items:center;gap:16px">
                <div class="avatar" style="width:60px;height:60px;border-radius:14px;background:{cor};font-size:20px">{iniciais(c['nome'])}</div>
                <div>
                    <div class="profile-name">{c['nome']}</div>
                    <div style="font-size:13px;color:#6080c0;margin-bottom:6px">{c.get('formacao','—')} · {c.get('instituicao','—')}</div>
                    <div>{html_selos(c)}</div>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

        col1,col2,col3,col4=st.columns(4)
        for col,lb,vl in [(col1,"Área",c.get("area","—")),(col2,"OAB",c.get("oab","—")),(col3,"Disponível",c.get("disponibilidade","—")),(col4,"Órgãos",c.get("experiencia_orgaos","—") or "—")]:
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
                st.markdown(f'<div class="info-card">{prev}<br><br><span style="font-size:12px;color:#4070f4">🔐 Resumo completo disponível para recrutadores.</span></div>',unsafe_allow_html=True)

        st.markdown('<p class="section-label">Contato</p>',unsafe_allow_html=True)
        if rec_logado():
            # Verificar se recrutador aceitou o termo de responsabilidade
            if not st.session_state.get("termo_aceito"):
                st.markdown("""<div class="disclaimer-box">
                    <strong>Termo de responsabilidade</strong><br>
                    Ao acessar os dados de contato deste candidato, você confirma que utilizará as informações exclusivamente para fins de seleção profissional para cargo de livre nomeação no seu órgão, em conformidade com os princípios da impessoalidade e vedação ao nepotismo (SV nº 13 do STF e Resolução CNJ nº 07/2005).
                </div>""", unsafe_allow_html=True)
                if st.button("✅ Aceito e quero ver os dados de contato"):
                    st.session_state["termo_aceito"] = True; st.rerun()
            else:
                st.markdown(f'<div class="info-card">✉ {c.get("email","—")}</div>',unsafe_allow_html=True)
        else:
            st.markdown('<div class="lock-box">🔐 Disponível apenas para recrutadores aprovados.</div>',unsafe_allow_html=True)
    else:
        total=len(dados); disp=sum(1 for c in dados if c.get("disponibilidade")=="Sim")
        cert=sum(1 for c in dados if any(c.get(f"selo_{s}")=="Sim" for s in ["verificado","recomendado","destaque","experiente"]))

        st.markdown(f"""<div class="hero-card">
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
            asel=st.selectbox("Área",ar)
        with col3: fsel=st.selectbox("Selo",["Todos","Verificado","Recomendado","Destaque","Experiente"])

        cf=dados
        if busca: cf=[c for c in cf if busca.lower() in c["nome"].lower()]
        if asel!="Todas": cf=[c for c in cf if c["area"]==asel]
        if fsel!="Todos":
            cm={"Verificado":"selo_verificado","Recomendado":"selo_recomendado","Destaque":"selo_destaque","Experiente":"selo_experiente"}
            cf=[c for c in cf if c.get(cm[fsel])=="Sim"]

        st.markdown(f'<p style="font-size:13px;color:#8090b8;margin-bottom:1rem">{len(cf)} candidato(s)</p>',unsafe_allow_html=True)

        for i,cand in enumerate(cf):
            cor=cor_avatar(cand["nome"]); dsp=cand.get("disponibilidade","Não")
            bdg='<span class="badge-sim">● Disponível</span>' if dsp=="Sim" else '<span class="badge-nao">● Indisponível</span>'
            cc,cb=st.columns([11,2])
            with cc:
                st.markdown(f"""<div class="cand-card">
                    <div style="display:flex;align-items:center;justify-content:space-between;gap:12px">
                        <div style="display:flex;align-items:center;gap:12px;flex:1">
                            <div class="avatar" style="background:{cor}">{iniciais(cand['nome'])}</div>
                            <div>
                                <p class="cand-name">{cand['nome']}</p>
                                <p class="cand-sub">{cand.get('formacao','—')} · {cand.get('instituicao','—')} · {cand.get('area','—')}</p>
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

# ── PÁGINA: SELETIVOS ─────────────────────────────────────────────────────────
elif pagina == "seletivos":
    todas = aba_seletivos.get_all_records()

    st.markdown("""<div class="hero-card">
        <h1 class="page-title">Seletivos<br><em>Abertos.</em></h1>
        <p class="page-sub">Vagas de cargos de livre nomeação em Tribunais, Ministérios Públicos, Defensorias e Procuradorias</p>
    </div>""", unsafe_allow_html=True)
    st.markdown(f'<div class="disclaimer-box">{DISCLAIMER}</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    if not cand_logado() and not rec_logado():
        st.markdown("""<div class="aviso-pago">
            <p style="font-size:16px;font-weight:700;color:#f0c040;margin:0 0 8px">🔐 Inscrição disponível para candidatos ativos</p>
            <p style="font-size:13px;color:rgba(255,255,255,0.7);margin:0 0 16px">Cadastre-se gratuitamente e assine o plano Ativo para se inscrever nos Seletivos.</p>
        </div>""", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📄 Cadastrar agora", use_container_width=True): ir("cadastro")
        with col2:
            if st.button("🔑 Já tenho cadastro", use_container_width=True):
                st.session_state["login_cand_sel"]=True; st.rerun()

        if st.session_state.get("login_cand_sel"):
            st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
            em=st.text_input("Seu e-mail cadastrado",key="em_sel")
            if st.button("Entrar →",key="btn_sel"):
                tc=aba_candidatos.get_all_records()
                cf=next((c for c in tc if c.get("email","").lower()==em.lower()),None)
                if cf: st.session_state.cand_logado=cf; st.session_state["login_cand_sel"]=False; st.rerun()
                else: st.error("E-mail não encontrado.")

    if cand_logado():
        cand=st.session_state.cand_logado
        col1,col2=st.columns([8,2])
        with col1: st.markdown(f'<div class="info-box">👤 {cand["nome"]} — <span style="font-size:11px">candidato ativo</span></div>',unsafe_allow_html=True)
        with col2:
            if st.button("Sair",key="sc"): del st.session_state.cand_logado; st.rerun()

    col1,col2,col3=st.columns(3)
    with col1: fa=st.selectbox("Área",["Todas"]+AREAS,key="fa")
    with col2: fe=st.selectbox("Estado",["Todos"]+ESTADOS,key="fe")
    with col3: fs=st.selectbox("Status",["Abertos","Todos","Encerrados"],key="fs")

    chf=todas
    if fa!="Todas": chf=[s for s in chf if s.get("area")==fa]
    if fe!="Todos": chf=[s for s in chf if s.get("estado")==fe]
    if fs=="Abertos": chf=[s for s in chf if sel_aberto(s)]
    elif fs=="Encerrados": chf=[s for s in chf if not sel_aberto(s)]

    st.markdown(f'<p style="font-size:13px;color:#8090b8;margin-bottom:1rem">{len(chf)} seletivo(s)</p>',unsafe_allow_html=True)

    for i,sel in enumerate(chf):
        ab=sel_aberto(sel); ins_=inscritos_sel(sel); n=len(ins_)
        sb='<span class="badge-aberto">● Aberto</span>' if ab else '<span class="badge-encerrado">● Encerrado</span>'
        ja=cand_logado() and st.session_state.cand_logado.get("email","") in ins_

        st.markdown(f"""<div class="seletivo-card">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:12px">
                <div style="flex:1">
                    <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">
                        {sb}
                        <span style="font-size:11px;color:#8090b8">📅 {sel.get('prazo','—')}</span>
                        <span style="font-size:11px;color:#8090b8">👥 {n} inscrito(s)</span>
                    </div>
                    <p style="font-size:16px;font-weight:700;color:#0d1f4e;margin:0 0 4px">{sel.get('titulo','—')}</p>
                    <p style="font-size:13px;color:#6080c0;margin:0 0 8px">{sel.get('orgao','—')} · {sel.get('municipio','—')}/{sel.get('estado','—')}</p>
                    <div style="display:flex;gap:8px;flex-wrap:wrap">
                        <span style="font-size:11px;font-weight:600;padding:2px 10px;border-radius:99px;background:#e8effe;color:#1a3a8f">{sel.get('area','—')}</span>
                        <span style="font-size:11px;font-weight:600;padding:2px 10px;border-radius:99px;background:#f3effe;color:#6d28d9">{sel.get('regime','—')}</span>
                        <span style="font-size:11px;font-weight:600;padding:2px 10px;border-radius:99px;background:#e6f4ea;color:#15803d">{sel.get('vagas','—')} vaga(s)</span>
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
                st.markdown('<span class="badge-pago">🔐 Plano Ativo</span>',unsafe_allow_html=True)

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
                        st.success("Inscrição realizada!"); st.rerun()
            with cx:
                if st.button("Cancelar",key=f"cx{i}"):
                    del st.session_state[f"ci{i}"]; st.rerun()

        if st.session_state.get(f"vd{i}"):
            with st.expander("Detalhes",expanded=True):
                c1,c2,c3=st.columns(3)
                with c1: st.markdown(f'<div class="metric-box"><p class="metric-label">Remuneração</p><p class="metric-value" style="font-size:13px">{sel.get("remuneracao","—")}</p></div>',unsafe_allow_html=True)
                with c2: st.markdown(f'<div class="metric-box"><p class="metric-label">Regime</p><p class="metric-value" style="font-size:13px">{sel.get("regime","—")}</p></div>',unsafe_allow_html=True)
                with c3: st.markdown(f'<div class="metric-box"><p class="metric-label">Seleção</p><p class="metric-value" style="font-size:13px">{sel.get("forma_selecao","—")}</p></div>',unsafe_allow_html=True)
                if sel.get("requisitos"):
                    st.markdown('<p class="section-label">Requisitos</p>',unsafe_allow_html=True)
                    st.markdown(f'<div class="info-card">{sel["requisitos"]}</div>',unsafe_allow_html=True)
                st.markdown(f'<div class="disclaimer-box">{DISCLAIMER}</div>',unsafe_allow_html=True)

# ── PÁGINA: CADASTRO ──────────────────────────────────────────────────────────
elif pagina == "cadastro":
    if "et" not in st.session_state: st.session_state.et=1
    if "campos" not in st.session_state: st.session_state.campos={}
    if "dc" not in st.session_state: st.session_state.dc={}
    et=st.session_state.et
    ts=[("Seus dados\nprofissionais.","Upload do currículo ou preenchimento manual"),("Certificação e\nreferências.","Documentos que geram selos"),("Perfil\ncomportamental.","12 perguntas — 3 minutos")]
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
        c1,c2=st.columns(2)
        with c1: nome=st.text_input("Nome completo *",value=campos.get("nome",""))
        with c2: email=st.text_input("E-mail *",value=campos.get("email",""))
        c1,c2,c3=st.columns(3)
        with c1: form=st.selectbox("Formação *",["Bacharel em Direito","Pós-graduado em Direito","Mestre em Direito","Doutor em Direito"])
        with c2: inst=st.text_input("Instituição *")
        with c3: area=st.selectbox("Área *",["Tribunal","MP","Procuradoria","Defensoria","TCU/TCE"])
        c1,c2,c3=st.columns(3)
        with c1: oab=st.radio("OAB ativa?",["Sim","Não"],index=0 if campos.get("oab")=="Sim" else 1,horizontal=True)
        with c2: anos=st.number_input("Anos em órgão público",min_value=0,max_value=40,value=0)
        with c3: disp=st.radio("Disponível?",["Sim","Não"],horizontal=True)
        exp=st.text_input("Órgãos de atuação",value=campos.get("experiencia_orgaos",""))
        sis=st.text_input("Sistemas dominados",value=campos.get("sistemas",""))
        pos=st.text_input("Pós-graduação",value=campos.get("pos_graduacao",""))
        res=st.text_area("Resumo profissional",value=campos.get("resumo",""),height=100)
        st.markdown('<div class="custom-divider"></div>',unsafe_allow_html=True)
        conc=st.selectbox("Estudando para algum concurso?",CONCURSOS)
        st.markdown('<div class="custom-divider"></div>',unsafe_allow_html=True)
        cons=st.checkbox("Li e aceito a Política de Privacidade e os Termos de Uso. Consinto com o tratamento dos meus dados nos termos da LGPD (Lei nº 13.709/2018).")
        st.markdown("<br>",unsafe_allow_html=True)
        if st.button("Próximo →"):
            if not nome or not email or not inst: st.error("Preencha nome, e-mail e instituição.")
            elif not cons: st.error("Aceite os Termos para continuar.")
            else:
                st.session_state.dc.update({"nome":nome,"email":email,"formacao":form,"instituicao":inst,"area":area,"oab":oab,"anos_experiencia":anos,"disponibilidade":disp,"experiencia":exp,"sistemas":sis,"pos":pos,"resumo":res,"concurso":conc})
                st.session_state.et=2; st.rerun()

    elif et==2:
        c1,c2=st.columns(2)
        with c1:
            st.markdown('<p style="font-weight:600;color:#b45309;margin-bottom:4px">★ Carta de recomendação</p>',unsafe_allow_html=True)
            st.markdown('<p style="font-size:12px;color:#8090b8;margin-bottom:8px">De um Juiz, Promotor, Defensor ou Procurador ativo</p>',unsafe_allow_html=True)
            carta=st.file_uploader("",type="pdf",key="carta",label_visibility="collapsed")
        with c2:
            st.markdown('<p style="font-weight:600;color:#b45309;margin-bottom:4px">◆ Avaliação de desempenho</p>',unsafe_allow_html=True)
            st.markdown('<p style="font-size:12px;color:#8090b8;margin-bottom:8px">Avaliação formal emitida pelo órgão</p>',unsafe_allow_html=True)
            aval=st.file_uploader("",type="pdf",key="aval",label_visibility="collapsed")
        st.markdown('<div class="custom-divider"></div>',unsafe_allow_html=True)
        st.markdown('<p style="font-weight:600;color:#3a5a9a;margin-bottom:4px">E-mail do recomendador</p>',unsafe_allow_html=True)
        er=st.text_input("",placeholder="nome@mpsc.mp.br",key="er",label_visibility="collapsed")
        dv=["mpsc.mp.br","tjsc.jus.br","sc.def.br","pge.sc.gov.br","trf4.jus.br","jfsc.jus.br","mpf.mp.br","agu.gov.br"]
        if er and "@" in er:
            if er.split("@")[-1] in dv: st.markdown('<div class="info-box">✓ E-mail institucional reconhecido.</div>',unsafe_allow_html=True)
            else: st.warning("Domínio não reconhecido.")

        if er and "@" in er:
            st.markdown('<div class="custom-divider"></div>',unsafe_allow_html=True)
            st.markdown('<p style="font-weight:600;color:#3a5a9a;margin-bottom:4px">Solicitar avaliação direta na plataforma</p>',unsafe_allow_html=True)
            st.markdown('<p style="font-size:12px;color:#8090b8;margin-bottom:8px">O recomendador receberá um link exclusivo para preencher uma avaliação do seu perfil diretamente no JurisBank.</p>',unsafe_allow_html=True)
            if st.button("Gerar link de avaliação →",key="gerar_link"):
                email_cand_temp=st.session_state.dc.get("email","")
                if not email_cand_temp: st.error("Preencha seu e-mail na etapa anterior primeiro.")
                else:
                    token=secrets.token_urlsafe(24)
                    aba_recomendacoes.append_row([token,email_cand_temp,er,"pendente",datetime.now().strftime("%d/%m/%Y %H:%M"),"",""])
                    link=f"https://jurisbank.streamlit.app/?p=recomendar&token={token}"
                    nome_cand_temp=st.session_state.dc.get("nome","candidato")
                    enviado=email_recomendador(nome_cand_temp,er,link)
                    if enviado:
                        st.markdown(f'<div class="info-box">✓ E-mail enviado para <strong>{er}</strong>!</div>',unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="info-box">✓ Link gerado! Compartilhe manualmente:<br><strong style="font-size:12px;word-break:break-all">{link}</strong></div>',unsafe_allow_html=True)
                    st.session_state.dc["token_recomendacao"]=token
                    st.info("Quando o recomendador preencher, o selo ★ Recomendado será ativado automaticamente.")

        d=st.session_state.dc; sp=[]
        if d.get("oab")=="Sim": sp.append("✓ Verificado")
        if carta: sp.append("★ Recomendado")
        if aval: sp.append("◆ Destaque")
        if d.get("anos_experiencia",0)>=2: sp.append("● Experiente")
        if sp:
            st.markdown('<div class="custom-divider"></div>',unsafe_allow_html=True)
            st.markdown('<p style="font-size:13px;font-weight:600;color:#0d1f4e">Selos:</p>',unsafe_allow_html=True)
            st.markdown(" ".join([f'<span class="selo selo-verificado">{s}</span>' for s in sp]),unsafe_allow_html=True)

        st.markdown("<br>",unsafe_allow_html=True)
        c1,c2=st.columns(2)
        with c1:
            if st.button("← Voltar"): st.session_state.et=1; st.rerun()
        with c2:
            if st.button("Próximo →"):
                st.session_state.dc.update({"carta":carta is not None,"avaliacao":aval is not None,"email_ref":er})
                st.session_state.et=3; st.rerun()

    elif et==3:
        st.markdown('<p style="font-size:14px;color:#8090b8;margin-bottom:1.5rem">Não há respostas certas ou erradas.</p>',unsafe_allow_html=True)
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
                if None in rd: st.error("Responda todas as 12 perguntas.")
                else:
                    d=st.session_state.dc
                    selos=calc_selos(d["oab"],d["anos_experiencia"],d.get("carta",False),d.get("avaliacao",False))
                    pd_,_,desc=calc_disc(rd)
                    aba_candidatos.append_row([d["nome"],d["email"],d["formacao"],d["instituicao"],d["area"],d["disponibilidade"],d["oab"],d["experiencia"],d["sistemas"],d["pos"],d["resumo"],d.get("email_ref",""),selos["verificado"],selos["recomendado"],selos["destaque"],selos["experiente"],pd_,d.get("concurso","Não estou estudando para concurso")])
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
        msel=[s for s in aba_seletivos.get_all_records() if s.get("email_recrutador")==rec["email"]]

        st.markdown(f"""<div class="hero-card">
            <h1 class="page-title">Olá, <em>{rec['nome'].split()[0]}!</em></h1>
            <p class="page-sub">{ra.get('nome_orgao',rec.get('orgao',''))} · {rec.get('estado','')}</p>
            <div class="stats-row">
                <div class="stat-pill">⚖ {len(dados)} candidatos</div>
                <div class="stat-pill">★ {len(favs)} favoritos</div>
                <div class="stat-pill">📢 {len(msel)} seletivos</div>
            </div>
        </div>""", unsafe_allow_html=True)

        c_sair,_=st.columns([2,8])
        with c_sair:
            if st.button("Sair da conta"): del st.session_state.rec_logado; ir("recrutador")

        tabs=st.tabs(["🔍 Busca","📢 Seletivos","★ Favoritos"])

        with tabs[0]:
            c1,c2,c3=st.columns(3)
            with c1: busca=st.text_input("Nome",placeholder="Buscar...")
            with c2:
                ad=["Todas"]+sorted(set(c["area"] for c in dados if c.get("area")))
                asel=st.selectbox("Área",ad)
            with c3: dsel=st.selectbox("Disponibilidade",["Todos","Disponível","Indisponível"])
            c1,c2,c3,c4,c5,c6=st.columns(6)
            with c1: osel=st.selectbox("OAB",["Todos","Sim","Não"])
            with c2: ssel=st.selectbox("Selo",["Todos","Verificado","Recomendado","Destaque","Experiente"])
            with c3:
                dsc=st.selectbox("DISC",["Todos","D — Dominante","I — Influente","S — Estável","C — Conformidade"])
                if dsc!="Todos": st.markdown(f'<div class="info-box">{DISC_EXPLICACOES.get(dsc,"")}</div>',unsafe_allow_html=True)
            with c4: csel=st.selectbox("Concurso",["Todos","Concursando","Não concursando"])
            with c5: sisel=st.text_input("Sistema",placeholder="Ex: Eproc")
            with c6: emin=st.number_input("Exp. mín.",min_value=0,max_value=20,value=0)

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

            st.markdown(f'<p style="font-size:13px;color:#8090b8;margin:1rem 0 0.5rem">{len(fi)} candidato(s)</p>',unsafe_allow_html=True)

            for i,cand in enumerate(fi):
                cor=cor_avatar(cand["nome"]); dc=cand.get("disponibilidade","Não")
                bdg='<span class="badge-sim">● Disponível</span>' if dc=="Sim" else '<span class="badge-nao">● Indisponível</span>'
                ec=cand.get("email",""); ifav=ec in favs; fi_i="★" if ifav else "☆"
                with st.container():
                    st.markdown(f"""<div class="cand-card">
                        <div style="display:flex;align-items:center;justify-content:space-between;gap:12px">
                            <div style="display:flex;align-items:center;gap:12px;flex:1">
                                <div class="avatar" style="background:{cor}">{iniciais(cand['nome'])}</div>
                                <div>
                                    <p class="cand-name">{cand['nome']}</p>
                                    <p class="cand-sub">{cand.get('formacao','—')} · {cand.get('instituicao','—')} · {cand.get('area','—')}</p>
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
                        if st.button("Ver →",key=f"rb{i}"):
                            st.session_state.cr=cand
                            st.session_state["termo_aceito"]=False
                            st.rerun()

                if ec in anots: st.markdown(f'<div class="info-card" style="margin-top:-6px;margin-bottom:8px;font-size:12px">📝 {anots[ec]}</div>',unsafe_allow_html=True)

                if st.session_state.get("cr")==cand:
                    with st.expander("Perfil completo",expanded=True):
                        c1,c2,c3=st.columns(3)
                        for cl,lb,vl in [(c1,"OAB",cand.get("oab","—")),(c2,"Órgãos",cand.get("experiencia_orgaos","—") or "—"),(c3,"Sistemas",cand.get("sistemas","—") or "—")]:
                            with cl: st.markdown(f'<div class="metric-box"><p class="metric-label">{lb}</p><p class="metric-value" style="font-size:12px">{vl}</p></div>',unsafe_allow_html=True)
                        if cand.get("disc"): st.markdown(render_disc(cand["disc"]),unsafe_allow_html=True)
                        if cand.get("resumo"): st.markdown(f'<div class="info-card" style="margin-top:1rem">{cand["resumo"]}</div>',unsafe_allow_html=True)

                        # Termo de responsabilidade antes de mostrar e-mail
                        if not st.session_state.get("termo_aceito"):
                            st.markdown("""<div class="disclaimer-box">
                                <strong>Termo de responsabilidade</strong><br>
                                Ao acessar os dados de contato, você confirma que utilizará as informações exclusivamente para fins de seleção profissional, em conformidade com os princípios de impessoalidade e vedação ao nepotismo.
                            </div>""", unsafe_allow_html=True)
                            if st.button("✅ Aceito — ver dados de contato", key=f"termo_{i}"):
                                st.session_state["termo_aceito"]=True; st.rerun()
                        else:
                            st.markdown(f'<div class="info-card" style="margin-top:0.5rem">✉ {cand.get("email","—")}</div>',unsafe_allow_html=True)

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
                    tsel=st.text_input("Título da vaga *",placeholder="Ex: Assessor Jurídico — 3ª Promotoria")
                    c1,c2=st.columns(2)
                    with c1: osel_=st.text_input("Nome do órgão *",value=ra.get("nome_orgao",""))
                    with c2: tosel=st.selectbox("Tipo de órgão *",["Selecione..."]+ORGAOS)
                    c1,c2,c3=st.columns(3)
                    with c1: asel_=st.selectbox("Área *",["Selecione..."]+AREAS)
                    with c2: esel=st.selectbox("Estado *",["Selecione..."]+ESTADOS,index=ESTADOS.index(rec.get("estado","SC"))+1 if rec.get("estado","") in ESTADOS else 0)
                    with c3: msel_=st.text_input("Município *",value=ra.get("municipio",""))
                    rsel=st.text_area("Requisitos *",height=80)
                    c1,c2,c3=st.columns(3)
                    with c1: remsel=st.text_input("Remuneração *",placeholder="Ex: R$ 4.500,00")
                    with c2: regsel=st.selectbox("Regime *",["Selecione..."]+REGIMES)
                    with c3: vsel=st.number_input("Vagas *",min_value=1,max_value=20,value=1)
                    c1,c2=st.columns(2)
                    with c1: fssel=st.selectbox("Forma de seleção *",["Selecione..."]+FORMAS_SELECAO)
                    with c2: prsel=st.date_input("Prazo *",min_value=date.today())
                    st.markdown("<br>",unsafe_allow_html=True)
                    c1,c2=st.columns(2)
                    with c1:
                        if st.button("Cancelar",key="csel"): del st.session_state["criar_sel"]; st.rerun()
                    with c2:
                        if st.button("Publicar →",key="psel"):
                            ok=all([tsel,osel_,tosel!="Selecione...",asel_!="Selecione...",esel!="Selecione...",msel_,rsel,remsel,regsel!="Selecione...",fssel!="Selecione..."])
                            if not ok: st.error("Preencha todos os campos.")
                            else:
                                aba_seletivos.append_row([gerar_id(),tsel,osel_,tosel,asel_,esel,msel_,rsel,remsel,regsel,fssel,str(vsel),prsel.strftime("%d/%m/%Y"),"aberto",rec["email"],"",datetime.now().strftime("%d/%m/%Y")])
                                del st.session_state["criar_sel"]; st.success("Seletivo publicado!"); st.rerun()

            if not msel: st.info("Nenhum Seletivo publicado ainda.")
            else:
                for i,sel in enumerate(msel):
                    ab=sel_aberto(sel); ins_=inscritos_sel(sel); n=len(ins_)
                    sb='<span class="badge-aberto">● Aberto</span>' if ab else '<span class="badge-encerrado">● Encerrado</span>'
                    st.markdown(f"""<div class="seletivo-card">
                        <div style="display:flex;justify-content:space-between;align-items:center">
                            <div>
                                <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px">{sb}<span style="font-size:11px;color:#8090b8">📅 {sel.get('prazo','—')}</span></div>
                                <p style="font-size:15px;font-weight:700;color:#0d1f4e;margin:0 0 2px">{sel.get('titulo','—')}</p>
                                <p style="font-size:12px;color:#6080c0;margin:0">{sel.get('municipio','—')}/{sel.get('estado','—')} · {sel.get('area','—')}</p>
                            </div>
                            <div style="text-align:right">
                                <p style="font-family:'Playfair Display',serif;font-size:28px;font-weight:900;color:#c8960c;margin:0">{n}</p>
                                <p style="font-size:11px;color:#8090b8;margin:0">inscrito(s)</p>
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
                                with c3: st.markdown(f'<div class="metric-box"><p class="metric-label">Disponíveis</p><p class="metric-value">{sum(1 for c in id_ if c.get("disponibilidade")=="Sim")}</p></div>',unsafe_allow_html=True)
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
                                                <p class="cand-sub">{cand.get('formacao','—')} · {cand.get('area','—')}</p>
                                                <div style="margin-top:4px">{html_selos(cand)}{html_disc(cand)}</div>
                                            </div>
                                            <div style="font-size:12px;color:#6080c0">✉ {cand.get('email','—')}</div>
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
                                <p class="cand-sub">{cand.get('formacao','—')} · {cand.get('area','—')}</p>
                                {html_selos(cand)}
                                {'<p style="font-size:11px;color:#8090b8;margin-top:4px">📝 '+nt+'</p>' if nt else ''}
                            </div>
                            <div>{'<span class="badge-sim">● Disponível</span>' if cand.get('disponibilidade')=='Sim' else '<span class="badge-nao">● Indisponível</span>'}</div>
                        </div>
                    </div>""",unsafe_allow_html=True)
                    if st.button("✕ Remover",key=f"rf{i}"):
                        favs.remove(ec); aba_recrutadores.update_cell(idx_r+2,12,", ".join(favs)); st.rerun()

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
                    if enc: st.session_state.rec_logado=enc; st.rerun()
                    else: st.error("E-mail ou senha incorretos, ou conta ainda não aprovada.")
                else: st.error("Preencha e-mail e senha.")
        with tabs[1]:
            st.markdown('<p style="font-size:15px;font-weight:700;color:#0d1f4e;margin:1rem 0 0.5rem">Criar conta</p>',unsafe_allow_html=True)
            st.markdown('<p style="font-size:13px;color:#8090b8;margin-bottom:1rem">4 etapas. Ativação após validação institucional.</p>',unsafe_allow_html=True)
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
    token_url = st.query_params.get("token","")
    if isinstance(token_url,list): token_url=token_url[0]

    if not token_url:
        st.markdown('<div class="hero-card"><h1 class="page-title">Link<br><em>inválido.</em></h1></div>',unsafe_allow_html=True)
    else:
        recs_recom=aba_recomendacoes.get_all_records()
        rec_recom=next((r for r in recs_recom if r.get("token")==token_url),None)
        if not rec_recom:
            st.markdown('<div class="hero-card"><h1 class="page-title">Link<br><em>não encontrado.</em></h1></div>',unsafe_allow_html=True)
        elif rec_recom.get("status")=="concluido":
            st.markdown('<div class="hero-card"><h1 class="page-title">Avaliação<br><em>já realizada.</em></h1><p class="page-sub">Obrigado pela sua contribuição.</p></div>',unsafe_allow_html=True)
        else:
            todos_cands=aba_candidatos.get_all_records()
            cand_recom=next((c for c in todos_cands if c.get("email")==rec_recom.get("email_candidato")),None)
            nome_cand=cand_recom["nome"] if cand_recom else rec_recom.get("email_candidato","candidato")

            st.markdown(f'<div class="hero-card"><h1 class="page-title">Avaliação de<br><em>Recomendação.</em></h1><p class="page-sub">Você foi indicado como recomendador de <strong>{nome_cand}</strong> no JurisBank.</p></div>',unsafe_allow_html=True)
            st.markdown('<div class="disclaimer-box">Esta avaliação é de caráter profissional e será exibida para recrutadores. Ao enviar, você confirma que as informações são verdadeiras.</div>',unsafe_allow_html=True)
            st.markdown("<br>",unsafe_allow_html=True)

            with st.form("form_rec"):
                tempo=st.selectbox("Há quanto tempo conhece o candidato? *",["Selecione...","Menos de 1 ano","1 a 2 anos","2 a 5 anos","Mais de 5 anos"])
                contexto=st.selectbox("Em qual contexto profissional? *",["Selecione...","Assessoria direta no meu gabinete","Atuação em outro órgão público","Trabalho conjunto em projeto","Docência ou orientação acadêmica","Outro"])
                st.markdown('<div class="custom-divider"></div>',unsafe_allow_html=True)
                pontos=st.text_area("Principais pontos fortes do candidato *",height=100,placeholder="Descreva as qualidades profissionais que mais se destacaram...")
                adequacao=st.selectbox("O candidato é adequado para assessoria em órgão público? *",["Selecione...","Sim, fortemente recomendo","Sim, com algumas ressalvas","Neutro","Não recomendo"])
                nota=st.select_slider("Nota geral (1 a 5) *",options=[1,2,3,4,5],value=4)
                comentarios=st.text_area("Comentários adicionais (opcional)",height=80,placeholder="Observações complementares...")
                st.markdown('<div class="custom-divider"></div>',unsafe_allow_html=True)
                conf=st.checkbox("Confirmo que sou membro ativo de órgão do sistema de justiça e que as informações são verdadeiras.")
                submitted=st.form_submit_button("Enviar avaliação →")

                if submitted:
                    if tempo=="Selecione..." or contexto=="Selecione..." or adequacao=="Selecione..." or not pontos:
                        st.error("Preencha todos os campos obrigatórios.")
                    elif not conf:
                        st.error("Confirme sua responsabilidade sobre as informações.")
                    else:
                        resposta=f"Tempo: {tempo} | Contexto: {contexto} | Adequação: {adequacao} | Nota: {nota}/5 | Pontos fortes: {pontos}"
                        idx_recom=next((i for i,r in enumerate(recs_recom) if r.get("token")==token_url),None)
                        if idx_recom is not None:
                            aba_recomendacoes.update_cell(idx_recom+2,4,"concluido")
                            aba_recomendacoes.update_cell(idx_recom+2,6,resposta)
                            aba_recomendacoes.update_cell(idx_recom+2,7,comentarios)
                        if cand_recom:
                            todos_cands2=aba_candidatos.get_all_records()
                            idx_cand=next((i for i,c in enumerate(todos_cands2) if c.get("email")==rec_recom.get("email_candidato")),None)
                            if idx_cand is not None: aba_candidatos.update_cell(idx_cand+2,14,"Sim")
                        st.success("Avaliação enviada! O selo ★ Recomendado foi ativado no perfil do candidato.")
                        st.balloons()

# ── PÁGINAS LEGAIS ────────────────────────────────────────────────────────────
elif pagina in ["privacidade","termos"]:
    ip=pagina=="privacidade"
    st.markdown(f'<div class="hero-card"><h1 class="page-title">{"Política de<br><em>Privacidade.</em>" if ip else "Termos<br><em>de Uso.</em>"}</h1><p class="page-sub">Versão 1.0</p></div>',unsafe_allow_html=True)
    if ip:
        secs=[
            ("1. Controlador",[("p","Operado por [RAZÃO SOCIAL A PREENCHER], CNPJ [A PREENCHER]. DPO: [E-MAIL A PREENCHER]")]),
            ("2. Dados Coletados",[("l",["Nome, e-mail, formação, OAB","Histórico em órgãos públicos","Sistemas jurídicos, perfil DISC","Documentos de referência (quando fornecidos)","E-mail e senha dos recrutadores (hash SHA-256)"])]),
            ("3. Finalidade",[("l",["Gestão de perfis e selos","Viabilizar busca por recrutadores aprovados","Gestão de inscrições em Seletivos","Melhoria dos serviços"])]),
            ("4. Direitos",[("l",["Acesso, correção e eliminação","Portabilidade","Revogação do consentimento"]),("p","Contato: [E-MAIL DO DPO A PREENCHER]")]),
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
    st.markdown(f'<p style="font-size:12px;color:#8090b8;text-align:center">JurisBank — Versão 1.0 — {datetime.now().strftime("%d/%m/%Y")}</p>',unsafe_allow_html=True)