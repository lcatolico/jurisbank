import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import fitz
import re
import hashlib
from datetime import datetime, date

st.set_page_config(
    page_title="JurisBank",
    page_icon="⚖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Sora', sans-serif; }

[data-testid="stAppViewContainer"] { background: #eef3fe; }
.main .block-container { padding: 2.5rem 3rem; max-width: 1100px; background: #eef3fe; }

.page-hero {
    background: #ffffff;
    border-radius: 24px;
    padding: 2.5rem 3rem;
    margin-bottom: 2rem;
    border: 1.5px solid #d0dcfa;
}
.page-title { font-size: 38px; font-weight: 800; color: #1a3a8f; margin: 0 0 8px; letter-spacing: -1px; line-height: 1.1; }
.page-sub { font-size: 15px; color: #6080c0; margin: 0; font-weight: 400; }

.stats-row { display: flex; gap: 12px; margin-top: 1.5rem; flex-wrap: wrap; }
.stat-pill { background: #eef3fe; border-radius: 99px; padding: 8px 18px; font-size: 13px; font-weight: 600; color: #1a3a8f; border: 1.5px solid #c5d5f5; }

.cand-card { background: #ffffff; border: 1.5px solid #d0dcfa; border-radius: 18px; padding: 1.4rem 1.6rem; margin-bottom: 6px; transition: all 0.2s; }
.cand-card:hover { border-color: #4070f4; box-shadow: 0 6px 24px rgba(64,112,244,0.12); transform: translateY(-2px); }

.chamada-card { background: #ffffff; border: 1.5px solid #d0dcfa; border-radius: 18px; padding: 1.4rem 1.6rem; margin-bottom: 10px; transition: all 0.2s; }
.chamada-card:hover { border-color: #4070f4; box-shadow: 0 6px 24px rgba(64,112,244,0.12); }
.chamada-card.encerrada { opacity: 0.6; }

.avatar { width: 50px; height: 50px; border-radius: 14px; display: flex; align-items: center; justify-content: center; font-size: 16px; font-weight: 700; flex-shrink: 0; color: white; }
.cand-name { font-size: 16px; font-weight: 700; color: #1a3a8f; margin: 0 0 3px; }
.cand-sub { font-size: 12px; color: #8090b8; margin: 0; }

.badge-sim { background: #e6f4ea; color: #1a7a4a; padding: 5px 14px; border-radius: 99px; font-size: 11px; font-weight: 700; border: 1.5px solid #b0dfc0; }
.badge-nao { background: #fff3e8; color: #c05a1a; padding: 5px 14px; border-radius: 99px; font-size: 11px; font-weight: 700; border: 1.5px solid #f0c8a0; }
.badge-aberta { background: #e6f4ea; color: #1a7a4a; padding: 4px 12px; border-radius: 99px; font-size: 11px; font-weight: 700; border: 1px solid #b0dfc0; }
.badge-encerrada { background: #f4f4f4; color: #888; padding: 4px 12px; border-radius: 99px; font-size: 11px; font-weight: 700; border: 1px solid #ddd; }
.badge-inscrito { background: #e8effe; color: #1a3a8f; padding: 4px 12px; border-radius: 99px; font-size: 11px; font-weight: 700; border: 1px solid #b0c5f5; }

.selo { display: inline-block; font-size: 10px; font-weight: 700; padding: 3px 10px; border-radius: 99px; margin-right: 4px; margin-top: 6px; }
.selo-verificado { background: #e8effe; color: #1a3a8f; border: 1px solid #b0c5f5; }
.selo-recomendado { background: #e6f4ea; color: #15803d; border: 1px solid #b0dfc0; }
.selo-destaque { background: #fff8e6; color: #b45309; border: 1px solid #fde68a; }
.selo-experiente { background: #f3effe; color: #6d28d9; border: 1px solid #ddd6fe; }

.metric-box { background: #ffffff; border: 1.5px solid #d0dcfa; border-radius: 16px; padding: 18px 20px; text-align: center; }
.metric-label { font-size: 11px; font-weight: 600; color: #8090b8; text-transform: uppercase; letter-spacing: .08em; margin: 0 0 6px; }
.metric-value { font-size: 20px; font-weight: 800; color: #1a3a8f; margin: 0; }

.profile-name { font-size: 32px; font-weight: 800; color: #1a3a8f; margin: 0 0 6px; letter-spacing: -0.5px; }
.section-label { font-size: 11px; font-weight: 700; color: #4070f4; text-transform: uppercase; letter-spacing: .1em; margin: 1.5rem 0 0.5rem; }
.info-card { background: #f4f7fe; border: 1.5px solid #d0dcfa; border-radius: 14px; padding: 14px 18px; font-size: 14px; color: #3a5a9a; line-height: 1.6; }
.custom-divider { height: 2px; background: linear-gradient(90deg, #eef3fe, #4070f444, #eef3fe); margin: 1.5rem 0; border-radius: 99px; }
.info-box { background: #e8effe; border: 1px solid #b0c5f5; border-radius: 10px; padding: 10px 14px; font-size: 13px; color: #1a3a8f; margin-top: 8px; font-weight: 500; }
.lock-box { background: #f4f7fe; border: 1.5px solid #d0dcfa; border-radius: 14px; padding: 14px 18px; font-size: 13px; color: #8090b8; text-align: center; }
.disclaimer-box { background: #fff8e6; border: 1px solid #fde68a; border-radius: 10px; padding: 12px 16px; font-size: 12px; color: #92400e; line-height: 1.6; margin-top: 1rem; }

.step-bar { display: flex; gap: 8px; margin-bottom: 2rem; }
.step { flex: 1; height: 6px; border-radius: 99px; background: #d0dcfa; }
.step.active { background: #4070f4; }
.step.done { background: #1a7a4a; }
.step-title { font-size: 13px; font-weight: 600; color: #8090b8; margin-bottom: 0.3rem; }
.step-desc { font-size: 22px; font-weight: 800; color: #1a3a8f; margin-bottom: 1.5rem; letter-spacing: -0.5px; }

.logo-box { display: flex; align-items: center; gap: 12px; padding: 1.5rem 0 1.2rem; border-bottom: 1px solid #c5d5f5; margin-bottom: 1.5rem; }
.logo-icon { width: 40px; height: 40px; background: linear-gradient(135deg, #c8960c, #f0c040); border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 22px; flex-shrink: 0; box-shadow: 0 2px 8px rgba(200,150,12,0.3); }
.logo-text { font-size: 20px; font-weight: 800; color: #1a3a8f; letter-spacing: -0.5px; line-height: 1.1; }
.logo-sub { font-size: 10px; color: #6080c0; font-weight: 400; margin-top: 2px; font-style: italic; }

.doc-sub { font-size: 13px; font-weight: 700; color: #4070f4; text-transform: uppercase; letter-spacing: .08em; margin: 1.5rem 0 0.5rem; }
.doc-body { font-size: 14px; color: #3a5a9a; line-height: 1.8; margin-bottom: 0.8rem; }
.doc-item { font-size: 14px; color: #3a5a9a; line-height: 1.8; padding-left: 1rem; }

.stButton button { background: #4070f4 !important; color: #ffffff !important; border: none !important; border-radius: 12px !important; font-family: 'Sora', sans-serif !important; font-weight: 700 !important; padding: 0.6rem 2rem !important; font-size: 14px !important; transition: all 0.2s !important; }
.stButton button:hover { background: #1a3a8f !important; transform: translateY(-1px) !important; }

div[data-testid="column"]:last-child .stButton button,
div[data-testid="column"]:nth-last-child(2) .stButton button { background: #e8f0fe !important; color: #4070f4 !important; border: 1.5px solid #c5d5f5 !important; border-radius: 10px !important; padding: 0.4rem 1rem !important; font-size: 12px !important; font-weight: 600 !important; width: 100%; }
div[data-testid="column"]:last-child .stButton button:hover,
div[data-testid="column"]:nth-last-child(2) .stButton button:hover { background: #4070f4 !important; color: white !important; border-color: #4070f4 !important; }

.stTextInput input, .stTextArea textarea { border-radius: 12px !important; border-color: #d0dcfa !important; background: #ffffff !important; font-family: 'Sora', sans-serif !important; font-size: 14px !important; }
.stTextInput input:focus, .stTextArea textarea:focus { border-color: #4070f4 !important; box-shadow: 0 0 0 3px rgba(64,112,244,0.15) !important; }
.stSelectbox > div > div { border-radius: 12px !important; border-color: #d0dcfa !important; background: #ffffff !important; }

[data-testid="stSidebar"] { background: #e8f0fe; border-right: 1px solid #c5d5f5; }
[data-testid="stSidebar"] * { color: #1a3a8f !important; }
[data-testid="stSidebar"] .stButton button { background: transparent !important; color: #1a3a8f !important; border: none !important; border-radius: 10px !important; font-size: 15px !important; font-weight: 700 !important; padding: 10px 14px !important; text-align: left !important; width: 100% !important; box-shadow: none !important; display: flex !important; justify-content: flex-start !important; letter-spacing: -0.3px !important; transform: none !important; }
[data-testid="stSidebar"] .stButton button:hover { background: #c5d5f5 !important; transform: none !important; }
</style>
""", unsafe_allow_html=True)

# ── Google Sheets ─────────────────────────────────────────────────────────────
escopos = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
import json
if "gcp_service_account" in st.secrets:
    credenciais = Credentials.from_service_account_info(
        dict(st.secrets["gcp_service_account"]), scopes=escopos
    )
else:
    credenciais = Credentials.from_service_account_file("credenciais.json", scopes=escopos)
cliente = gspread.authorize(credenciais)
planilha = cliente.open("JurisBank")
aba_candidatos = planilha.sheet1
aba_recrutadores = planilha.worksheet("recrutadores")
aba_chamadas = planilha.worksheet("chamadas")
aba_interesses = planilha.worksheet("interesses")

# ── Constantes ────────────────────────────────────────────────────────────────
AVATAR_CORES = ["#1a3a8f","#2e7d5e","#7b3fa0","#c05a1a","#1a6b8a","#a04040","#3a6b2a"]
DISC_LABEL = {"D": "Dominante", "I": "Influente", "S": "Estável", "C": "Conformidade"}
DISC_CORES_BADGE = {"D": "#fee2e2", "I": "#fef9c3", "S": "#dcfce7", "C": "#eff6ff"}
DISC_TEXTO_BADGE = {"D": "#991b1b", "I": "#854d0e", "S": "#166534", "C": "#1e3a8a"}
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
CONCURSOS = [
    "Não estou estudando para concurso",
    "Juiz de Direito (TJ)", "Juiz Federal (TRF)",
    "Promotor de Justiça (MP Estadual)", "Procurador da República (MPF)",
    "Defensor Público Estadual", "Defensor Público Federal (DPU)",
    "Procurador do Estado (PGE)", "Procurador Municipal",
    "Delegado de Polícia", "Auditor Fiscal / Receita Federal",
    "Outro concurso jurídico",
]
ESTADOS = ["AC","AL","AP","AM","BA","CE","DF","ES","GO","MA","MT","MS","MG",
           "PA","PB","PR","PE","PI","RJ","RN","RS","RO","RR","SC","SP","SE","TO"]
ORGAOS = ["Tribunal de Justiça (TJ)","Ministério Público (MP)","Defensoria Pública",
          "Procuradoria Geral do Estado (PGE)","Procuradoria Geral do Município (PGM)",
          "Tribunal Regional Federal (TRF)","Ministério Público Federal (MPF)",
          "Advocacia Geral da União (AGU)","Tribunal de Contas (TCE/TCU)","Outro"]
CARGOS = ["Juiz de Direito","Juiz Federal","Desembargador","Promotor de Justiça",
          "Procurador de Justiça","Defensor Público","Procurador do Estado",
          "Procurador Municipal","Servidor — RH / Gestão de Pessoas","Outro"]
AREAS = ["Criminal","Cível","Família e Sucessões","Execução Penal","Infância e Juventude",
         "Fazenda Pública","Meio Ambiente","Moralidade Administrativa","Violência Doméstica",
         "Direito Público","Direito Tributário","Consumidor","Saúde","Todas as áreas"]
REGIMES = ["Integral","Parcial","Remoto","Híbrido"]
FORMAS_SELECAO = ["Análise de currículo","Análise de currículo + entrevista","Entrevista","Análise de portfólio + entrevista","Processo simplificado"]
PERGUNTAS_DISC = [
    ("Em situações de pressão no trabalho, você tende a:", ["Tomar decisões rápidas e assumir o controle", "Motivar a equipe e buscar soluções criativas", "Manter a calma e seguir o processo estabelecido", "Analisar os dados antes de agir"]),
    ("Quando recebe uma tarefa nova, você prefere:", ["Ter autonomia total para decidir como fazer", "Conversar com a equipe e trocar ideias", "Entender bem o processo antes de começar", "Ter instruções detalhadas e critérios claros"]),
    ("Em reuniões, você costuma:", ["Liderar a discussão e propor soluções", "Animar o grupo e trazer entusiasmo", "Ouvir com atenção antes de opinar", "Apresentar dados e análises detalhadas"]),
    ("Seu ponto forte no trabalho é:", ["Resultados rápidos e objetivos", "Relacionamentos e comunicação", "Estabilidade e confiabilidade", "Precisão e qualidade técnica"]),
    ("Quando há um conflito na equipe, você:", ["Enfrenta diretamente e busca resolução imediata", "Tenta mediar com diplomacia e bom humor", "Evita confrontos e busca harmonia", "Analisa a situação antes de se posicionar"]),
    ("Você se sente mais motivado quando:", ["Tem metas desafiadoras para superar", "Trabalha com pessoas e recebe reconhecimento", "Tem rotina estável e previsível", "Pode aprofundar conhecimento e fazer bem feito"]),
    ("Seu estilo de comunicação é:", ["Direto e objetivo", "Entusiasmado e expressivo", "Calmo e paciente", "Preciso e detalhado"]),
    ("Diante de uma mudança repentina, você:", ["Adapta rapidamente e assume o controle", "Vê como oportunidade e engaja a equipe", "Precisa de tempo para se adaptar", "Avalia os riscos antes de aceitar"]),
    ("No trabalho em equipe, você assume o papel de:", ["Líder que define rumos e cobra resultados", "Motivador que mantém o clima positivo", "Apoiador que garante a harmonia do grupo", "Especialista que garante a qualidade técnica"]),
    ("Quando comete um erro, você:", ["Assume, corrige rapidamente e segue em frente", "Conversa com alguém para processar e superar", "Reflete com calma antes de agir diferente", "Analisa o que deu errado para não repetir"]),
    ("Sua maior dificuldade no trabalho é:", ["Paciência com processos lentos", "Manter o foco em tarefas repetitivas", "Lidar com mudanças repentinas", "Trabalhar sem informações suficientes"]),
    ("Como você prefere receber feedback:", ["Direto e objetivo, sem rodeios", "De forma encorajadora e positiva", "Com calma, em conversa reservada", "Com dados e exemplos concretos"]),
]
LETRAS_DISC = ["D", "I", "S", "C"]
DISCLAIMER_CHAMADA = "⚠️ O JurisBank atua exclusivamente como plataforma de aproximação entre profissionais e órgãos do sistema de justiça. A publicação desta Chamada não configura processo seletivo vinculante, concurso público ou compromisso de contratação. O uso do ius indicandum é de responsabilidade exclusiva do recrutador, que deve observar as normas de impessoalidade e vedação ao nepotismo aplicáveis ao seu órgão."

# ── Funções utilitárias ───────────────────────────────────────────────────────
def cor_avatar(nome):
    return AVATAR_CORES[sum(ord(c) for c in nome) % len(AVATAR_CORES)]

def iniciais(nome):
    partes = nome.strip().split()
    return (partes[0][0] + partes[-1][0]).upper() if len(partes) >= 2 else nome[:2].upper()

def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

def recrutador_logado():
    return "recrutador_logado" in st.session_state and st.session_state.recrutador_logado

def candidato_logado():
    return "candidato_logado" in st.session_state and st.session_state.candidato_logado

def gerar_id_chamada():
    return f"ch_{datetime.now().strftime('%Y%m%d%H%M%S')}"

def extrair_texto_pdf(arquivo):
    doc = fitz.open(stream=arquivo.read(), filetype="pdf")
    return "".join(p.get_text() for p in doc)

def extrair_campos(texto):
    campos = {"nome": "", "email": "", "oab": "Não", "experiencia_orgaos": "", "sistemas": "", "pos_graduacao": "", "resumo": ""}
    linhas = texto.split("\n")
    texto_completo = texto.lower()
    emails = re.findall(r'[\w\.\-]+@[\w\.\-]+\.\w+', texto)
    if emails: campos["email"] = emails[0]
    if "oab" in texto_completo or "ordem dos advogados" in texto_completo: campos["oab"] = "Sim"
    sistemas = ["Eproc", "SAJ", "SIG", "SEEU", "SISP", "APOIA", "GAIA", "Pandora", "SIMBA"]
    encontrados = [s for s in sistemas if s.lower() in texto_completo]
    if encontrados: campos["sistemas"] = ", ".join(encontrados)
    for linha in linhas:
        l = linha.strip()
        if any(x in l for x in ["Pós", "pós", "Especializ", "Mestrado", "Doutorado"]):
            if len(l) > 10 and not campos["pos_graduacao"]: campos["pos_graduacao"] = l
    orgaos_map = {"MPSC": "MPSC", "TJSC": "TJSC", "Defensoria": "Defensoria", "Procuradoria": "Procuradoria", "Ministério Público": "MP", "Tribunal de Justiça": "TJ", "AGU": "AGU", "PGE": "PGE"}
    encontrados_orgaos = []
    for orgao, sigla in orgaos_map.items():
        if orgao.lower() in texto_completo and sigla not in encontrados_orgaos: encontrados_orgaos.append(sigla)
    campos["experiencia_orgaos"] = ", ".join(encontrados_orgaos)
    for linha in linhas:
        l = linha.strip()
        if (len(l) > 5 and not any(x in l for x in ["@", "Rua", "Av.", "http", "www", "(", "PERFIL", "CONTATO"]) and not re.match(r'^\d', l)):
            campos["nome"] = l; break
    paragrafos = [p.strip() for p in texto.split("\n\n") if len(p.strip()) > 100]
    if paragrafos: campos["resumo"] = max(paragrafos, key=len)[:500]
    return campos

def calcular_selos(oab, anos_experiencia, tem_carta, tem_avaliacao):
    return {"verificado": "Sim" if oab == "Sim" else "Não", "recomendado": "Sim" if tem_carta else "Não", "destaque": "Sim" if tem_avaliacao else "Não", "experiente": "Sim" if anos_experiencia >= 2 else "Não"}

def html_selos(candidato):
    html = ""
    if candidato.get("selo_verificado") == "Sim": html += '<span class="selo selo-verificado">✓ Verificado</span>'
    if candidato.get("selo_recomendado") == "Sim": html += '<span class="selo selo-recomendado">★ Recomendado</span>'
    if candidato.get("selo_destaque") == "Sim": html += '<span class="selo selo-destaque">◆ Destaque</span>'
    if candidato.get("selo_experiente") == "Sim": html += '<span class="selo selo-experiente">● Experiente</span>'
    return html

def html_disc_badge(candidato):
    d = candidato.get("disc", "")
    if not d: return ""
    return f'<span title="{DESCRICOES_DISC.get(d,"")}" style="font-size:10px;font-weight:700;padding:2px 8px;border-radius:99px;background:{DISC_CORES_BADGE.get(d,"#eff6ff")};color:{DISC_TEXTO_BADGE.get(d,"#1e3a8a")};margin-left:4px;cursor:help">{d} {DISC_LABEL.get(d,"")}</span>'

def html_concurso_badge(candidato):
    if candidato.get("concurso") and candidato.get("concurso") != "Não estou estudando para concurso":
        return '<span style="font-size:10px;font-weight:700;padding:2px 8px;border-radius:99px;background:#fff8e6;color:#b45309;margin-left:4px">📚 Concursando</span>'
    return ""

def barra_etapas(atual, total=4):
    html = '<div class="step-bar">'
    for i in range(1, total + 1):
        if i < atual: html += '<div class="step done"></div>'
        elif i == atual: html += '<div class="step active"></div>'
        else: html += '<div class="step"></div>'
    html += '</div>'
    return html

def calcular_disc(respostas):
    p = {"D": 0, "I": 0, "S": 0, "C": 0}
    for i, r in enumerate(respostas):
        if r is None: continue
        _, opcoes = PERGUNTAS_DISC[i]
        p[LETRAS_DISC[opcoes.index(r)]] += 1
    dominante = max(p, key=p.get)
    return dominante, p, DESCRICOES_DISC[dominante]

def render_disc_perfil(d):
    cor_d = DISC_CORES_BADGE.get(d, "#f4f7fe")
    txt_d = DISC_TEXTO_BADGE.get(d, "#3a5a9a")
    det = DISC_DETALHES.get(d, {})
    return f"""<div class="info-card" style="background:{cor_d};border-color:{cor_d}">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px">
            <span style="font-weight:800;color:{txt_d};font-size:24px">{d}</span>
            <span style="font-weight:700;color:{txt_d};font-size:16px">{det.get('nome','')}</span>
        </div>
        <p style="color:{txt_d};font-size:14px;font-weight:600;margin:0 0 8px">{det.get('resumo','')}</p>
        <p style="color:{txt_d};font-size:12px;margin:0 0 4px"><strong>Pontos fortes:</strong> {det.get('pontos_fortes','')}</p>
        <p style="color:{txt_d};font-size:12px;margin:0 0 4px"><strong>No gabinete:</strong> {det.get('no_gabinete','')}</p>
        <p style="color:{txt_d};font-size:12px;margin:0"><strong>Atenção:</strong> {det.get('atencao','')}</p>
    </div>"""

def chamada_aberta(ch):
    if ch.get("status","").lower() != "aberto": return False
    try:
        prazo = datetime.strptime(ch.get("prazo",""), "%d/%m/%Y").date()
        return prazo >= date.today()
    except: return True

def inscritos_chamada(ch):
    raw = str(ch.get("inscritos","")).strip()
    if not raw: return []
    return [e.strip() for e in raw.split(",") if e.strip()]

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="logo-box">
        <div class="logo-icon">⚖</div>
        <div>
            <div class="logo-text">JurisBank</div>
            <div class="logo-sub">ius indicandum</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if recrutador_logado():
        rec = st.session_state.recrutador_logado
        st.markdown(f'<p style="font-size:12px;font-weight:600;color:#1a3a8f;margin-bottom:2px">👤 {rec["nome"]}</p>', unsafe_allow_html=True)
        st.markdown(f'<p style="font-size:11px;color:#6080c0;margin-bottom:1rem">{rec.get("orgao","")}</p>', unsafe_allow_html=True)
        for item, label in [
            ("Área do Recrutador", "🏛 Área do Recrutador"),
            ("Chamadas", "📢 Chamadas"),
            ("Candidatos", "👤 Candidatos"),
        ]:
            if st.button(label, key=f"menu_{item}", use_container_width=True):
                st.session_state["_menu"] = item; st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Sair", use_container_width=True):
            del st.session_state.recrutador_logado
            if "_menu" in st.session_state: del st.session_state["_menu"]
            st.rerun()
        pagina = st.session_state.get("_menu", "Área do Recrutador")
    else:
        for item, label in [
            ("Candidatos", "👤 Candidatos"),
            ("Chamadas", "📢 Chamadas"),
            ("Cadastrar currículo", "📄 Cadastrar currículo"),
            ("Área do Recrutador", "🔐 Área do Recrutador"),
        ]:
            if st.button(label, key=f"menu_{item}", use_container_width=True):
                st.session_state["_menu"] = item; st.rerun()
        st.markdown('<div style="border-top:1px solid #c5d5f5;margin:1rem 0 0.5rem"></div>', unsafe_allow_html=True)
        for item, label in [
            ("Política de Privacidade", "📋 Política de Privacidade"),
            ("Termos de Uso", "📋 Termos de Uso"),
        ]:
            if st.button(label, key=f"menu_{item}", use_container_width=True):
                st.session_state["_menu"] = item; st.rerun()
        pagina = st.session_state.get("_menu", "Candidatos")

# ── Página: Candidatos ────────────────────────────────────────────────────────
if pagina == "Candidatos":
    dados = aba_candidatos.get_all_records()
    if "candidato_selecionado" not in st.session_state:
        st.session_state.candidato_selecionado = None

    if st.session_state.candidato_selecionado:
        c = st.session_state.candidato_selecionado
        cor = cor_avatar(c["nome"])
        if st.button("← Voltar para lista"):
            st.session_state.candidato_selecionado = None; st.rerun()

        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#e8f0fe,#f0f4ff);border-radius:20px;padding:2rem;margin-bottom:1.5rem;border:1.5px solid #d0dcfa">
            <div style="display:flex;align-items:center;gap:18px">
                <div class="avatar" style="width:64px;height:64px;border-radius:16px;background:{cor};font-size:22px">{iniciais(c['nome'])}</div>
                <div>
                    <div class="profile-name">{c['nome']}</div>
                    <div style="font-size:13px;color:#6080c0;margin-bottom:8px">{c.get('formacao','—')} · {c.get('instituicao','—')}</div>
                    <div>{html_selos(c)}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)
        for col, label, val in [(col1,"Área",c.get("area","—")),(col2,"OAB",c.get("oab","—")),(col3,"Disponível",c.get("disponibilidade","—")),(col4,"Órgãos",c.get("experiencia_orgaos","—") or "—")]:
            with col: st.markdown(f'<div class="metric-box"><p class="metric-label">{label}</p><p class="metric-value">{val}</p></div>', unsafe_allow_html=True)

        if c.get("disc"):
            st.markdown('<p class="section-label">Perfil comportamental DISC</p>', unsafe_allow_html=True)
            st.markdown(render_disc_perfil(c.get("disc")), unsafe_allow_html=True)

        if c.get("concurso") and c.get("concurso") != "Não estou estudando para concurso":
            st.markdown('<p class="section-label">Estudando para concurso</p>', unsafe_allow_html=True)
            st.markdown(f'<div class="info-card" style="background:#fff8e6;border-color:#fde68a">📚 {c.get("concurso")}<br><span style="font-size:12px;color:#8090b8">Este candidato pode deixar a vaga ao ser aprovado no concurso.</span></div>', unsafe_allow_html=True)

        if c.get("sistemas"):
            st.markdown('<p class="section-label">Sistemas dominados</p>', unsafe_allow_html=True)
            st.markdown(f'<div class="info-card">{c.get("sistemas")}</div>', unsafe_allow_html=True)

        if c.get("pos_graduacao"):
            st.markdown('<p class="section-label">Pós-graduação</p>', unsafe_allow_html=True)
            st.markdown(f'<div class="info-card">{c.get("pos_graduacao")}</div>', unsafe_allow_html=True)

        if c.get("resumo"):
            st.markdown('<p class="section-label">Resumo profissional</p>', unsafe_allow_html=True)
            if recrutador_logado():
                st.markdown(f'<div class="info-card">{c.get("resumo")}</div>', unsafe_allow_html=True)
            else:
                preview = c.get("resumo","")[:150] + "..." if len(c.get("resumo","")) > 150 else c.get("resumo","")
                st.markdown(f'<div class="info-card">{preview}<br><br><span style="font-size:12px;color:#4070f4">🔐 Resumo completo disponível apenas para recrutadores cadastrados.</span></div>', unsafe_allow_html=True)

        st.markdown('<p class="section-label">Contato</p>', unsafe_allow_html=True)
        if recrutador_logado():
            st.markdown(f'<div class="info-card">✉ {c.get("email","—")}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="lock-box">🔐 Dados de contato disponíveis apenas para recrutadores cadastrados e aprovados.</div>', unsafe_allow_html=True)

    else:
        total = len(dados)
        disponiveis = sum(1 for c in dados if c.get("disponibilidade") == "Sim")
        certificados = sum(1 for c in dados if any(c.get(f"selo_{s}") == "Sim" for s in ["verificado","recomendado","destaque","experiente"]))

        st.markdown(f"""
        <div class="page-hero">
            <div class="page-title">Banco de Talentos<br>Jurídicos.</div>
            <div class="page-sub">Profissionais certificados para assessoria em Tribunais, Ministérios Públicos, Procuradorias e Defensorias</div>
            <div class="stats-row">
                <div class="stat-pill">⚖ {total} cadastrados</div>
                <div class="stat-pill">✓ {disponiveis} disponíveis</div>
                <div class="stat-pill">★ {certificados} certificados</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1: busca = st.text_input("Buscar por nome", placeholder="Digite um nome...")
        with col2:
            areas = ["Todas"] + sorted(set(c["area"] for c in dados if c.get("area")))
            area_selecionada = st.selectbox("Área", areas)
        with col3: filtro_selo = st.selectbox("Selo", ["Todos", "Verificado", "Recomendado", "Destaque", "Experiente"])

        candidatos_filtrados = dados
        if busca: candidatos_filtrados = [c for c in candidatos_filtrados if busca.lower() in c["nome"].lower()]
        if area_selecionada != "Todas": candidatos_filtrados = [c for c in candidatos_filtrados if c["area"] == area_selecionada]
        if filtro_selo != "Todos":
            col_map = {"Verificado": "selo_verificado", "Recomendado": "selo_recomendado", "Destaque": "selo_destaque", "Experiente": "selo_experiente"}
            candidatos_filtrados = [c for c in candidatos_filtrados if c.get(col_map[filtro_selo]) == "Sim"]

        st.markdown(f'<p style="font-size:13px;color:#8090b8;margin-bottom:1rem;font-weight:500">{len(candidatos_filtrados)} candidato(s) encontrado(s)</p>', unsafe_allow_html=True)

        for i, candidato in enumerate(candidatos_filtrados):
            cor = cor_avatar(candidato["nome"])
            disp = candidato.get("disponibilidade", "Não")
            badge = '<span class="badge-sim">● Disponível</span>' if disp == "Sim" else '<span class="badge-nao">● Indisponível</span>'
            col_card, col_btn = st.columns([11, 2])
            with col_card:
                st.markdown(f"""
                <div class="cand-card">
                    <div style="display:flex;align-items:center;justify-content:space-between;gap:12px">
                        <div style="display:flex;align-items:center;gap:14px;flex:1">
                            <div class="avatar" style="background:{cor}">{iniciais(candidato['nome'])}</div>
                            <div>
                                <p class="cand-name">{candidato['nome']}</p>
                                <p class="cand-sub">{candidato.get('formacao','—')} · {candidato.get('instituicao','—')} · {candidato.get('area','—')}</p>
                                <div style="margin-top:4px">{html_selos(candidato)}{html_disc_badge(candidato)}{html_concurso_badge(candidato)}</div>
                            </div>
                        </div>
                        <div style="flex-shrink:0">{badge}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with col_btn:
                st.write("")
                if st.button("Ver perfil →", key=f"btn_{i}"):
                    st.session_state.candidato_selecionado = candidato; st.rerun()

# ── Página: Chamadas ──────────────────────────────────────────────────────────
elif pagina == "Chamadas":
    todas_chamadas = aba_chamadas.get_all_records()

    # Login rápido de candidato (por e-mail)
    if not candidato_logado() and not recrutador_logado():
        with st.expander("🔑 Sou candidato cadastrado — quero me inscrever nas Chamadas"):
            email_cand_login = st.text_input("Seu e-mail cadastrado no JurisBank", key="cand_login_email")
            if st.button("Acessar Chamadas", key="btn_cand_login"):
                todos_cands = aba_candidatos.get_all_records()
                cand_encontrado = next((c for c in todos_cands if c.get("email","").lower() == email_cand_login.lower()), None)
                if cand_encontrado:
                    st.session_state.candidato_logado = cand_encontrado
                    st.success(f"Bem-vindo, {cand_encontrado['nome'].split()[0]}!")
                    st.rerun()
                else:
                    st.error("E-mail não encontrado. Cadastre seu currículo primeiro.")

    if candidato_logado():
        cand = st.session_state.candidato_logado
        st.markdown(f'<div class="info-box">👤 Acessando como <strong>{cand["nome"]}</strong> · <a href="#" style="color:#4070f4;font-size:12px" onclick="">Sair</a></div>', unsafe_allow_html=True)
        col_sair, _ = st.columns([2, 8])
        with col_sair:
            if st.button("Sair da conta", key="sair_cand"):
                del st.session_state.candidato_logado; st.rerun()

    st.markdown("""
    <div class="page-hero">
        <div class="page-title">Chamadas<br>Abertas.</div>
        <div class="page-sub">Vagas de cargos de livre nomeação em Tribunais, Ministérios Públicos, Defensorias e Procuradorias</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f'<div class="disclaimer-box">{DISCLAIMER_CHAMADA}</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # Filtros públicos
    col1, col2, col3 = st.columns(3)
    with col1: filtro_area_ch = st.selectbox("Área", ["Todas"] + AREAS, key="filtro_area_ch")
    with col2: filtro_estado_ch = st.selectbox("Estado", ["Todos"] + ESTADOS, key="filtro_estado_ch")
    with col3: filtro_status_ch = st.selectbox("Status", ["Abertas", "Todas", "Encerradas"], key="filtro_status_ch")

    chamadas_filtradas = todas_chamadas
    if filtro_area_ch != "Todas": chamadas_filtradas = [ch for ch in chamadas_filtradas if ch.get("area") == filtro_area_ch]
    if filtro_estado_ch != "Todos": chamadas_filtradas = [ch for ch in chamadas_filtradas if ch.get("estado") == filtro_estado_ch]
    if filtro_status_ch == "Abertas": chamadas_filtradas = [ch for ch in chamadas_filtradas if chamada_aberta(ch)]
    elif filtro_status_ch == "Encerradas": chamadas_filtradas = [ch for ch in chamadas_filtradas if not chamada_aberta(ch)]

    st.markdown(f'<p style="font-size:13px;color:#8090b8;margin-bottom:1rem;font-weight:500">{len(chamadas_filtradas)} chamada(s) encontrada(s)</p>', unsafe_allow_html=True)

    for i, ch in enumerate(chamadas_filtradas):
        aberta = chamada_aberta(ch)
        inscritos = inscritos_chamada(ch)
        n_inscritos = len(inscritos)
        status_badge = '<span class="badge-aberta">● Aberta</span>' if aberta else '<span class="badge-encerrada">● Encerrada</span>'
        card_class = "chamada-card" if aberta else "chamada-card encerrada"

        # Verifica se candidato está inscrito
        ja_inscrito = False
        if candidato_logado():
            ja_inscrito = st.session_state.candidato_logado.get("email","") in inscritos

        st.markdown(f"""
        <div class="{card_class}">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:12px">
                <div style="flex:1">
                    <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">
                        {status_badge}
                        <span style="font-size:11px;color:#8090b8">📅 Prazo: {ch.get('prazo','—')}</span>
                        <span style="font-size:11px;color:#8090b8">👥 {n_inscritos} inscrito(s)</span>
                    </div>
                    <p style="font-size:17px;font-weight:700;color:#1a3a8f;margin:0 0 4px">{ch.get('titulo','—')}</p>
                    <p style="font-size:13px;color:#6080c0;margin:0 0 8px">{ch.get('orgao','—')} · {ch.get('municipio','—')}/{ch.get('estado','—')}</p>
                    <div style="display:flex;gap:8px;flex-wrap:wrap">
                        <span style="font-size:11px;font-weight:600;padding:2px 10px;border-radius:99px;background:#e8effe;color:#1a3a8f">{ch.get('area','—')}</span>
                        <span style="font-size:11px;font-weight:600;padding:2px 10px;border-radius:99px;background:#f3effe;color:#6d28d9">{ch.get('regime','—')}</span>
                        <span style="font-size:11px;font-weight:600;padding:2px 10px;border-radius:99px;background:#e6f4ea;color:#15803d">{ch.get('vagas','—')} vaga(s)</span>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_det, col_ins = st.columns([8, 3])
        with col_det:
            if st.button("Ver detalhes", key=f"det_ch_{i}"):
                st.session_state[f"ver_ch_{i}"] = not st.session_state.get(f"ver_ch_{i}", False)
                st.rerun()
        with col_ins:
            if aberta and candidato_logado() and not ja_inscrito:
                if st.button("Inscrever-se →", key=f"ins_ch_{i}"):
                    st.session_state[f"confirmar_inscricao_{i}"] = True; st.rerun()
            elif ja_inscrito:
                st.markdown('<span class="badge-inscrito">✓ Inscrito</span>', unsafe_allow_html=True)
            elif not candidato_logado() and aberta:
                st.markdown('<span style="font-size:11px;color:#8090b8">Faça login para se inscrever</span>', unsafe_allow_html=True)

        # Confirmação de inscrição com consentimento
        if st.session_state.get(f"confirmar_inscricao_{i}"):
            with st.container():
                st.markdown('<div class="info-card" style="margin-top:8px">', unsafe_allow_html=True)
                st.markdown("**Confirmar inscrição**")
                st.markdown(f"Você está se inscrevendo em: **{ch.get('titulo','')}** — {ch.get('orgao','')}")
                consentimento_ins = st.checkbox(
                    "Autorizo que meu nome, perfil e dados profissionais sejam compartilhados com o recrutador responsável por esta Chamada, nos termos da LGPD.",
                    key=f"consent_ins_{i}"
                )
                col_conf, col_canc = st.columns(2)
                with col_conf:
                    if st.button("Confirmar inscrição", key=f"conf_ins_{i}"):
                        if not consentimento_ins:
                            st.error("É necessário autorizar o compartilhamento dos dados para se inscrever.")
                        else:
                            email_cand = st.session_state.candidato_logado.get("email","")
                            inscritos_atuais = inscritos_chamada(ch)
                            if email_cand not in inscritos_atuais:
                                inscritos_atuais.append(email_cand)
                                # Encontrar linha da chamada na planilha
                                todas = aba_chamadas.get_all_records()
                                idx_ch = next((j for j, c in enumerate(todas) if c.get("id") == ch.get("id")), None)
                                if idx_ch is not None:
                                    aba_chamadas.update_cell(idx_ch + 2, 16, ", ".join(inscritos_atuais))
                            del st.session_state[f"confirmar_inscricao_{i}"]
                            st.success("Inscrição realizada com sucesso!")
                            st.rerun()
                with col_canc:
                    if st.button("Cancelar", key=f"canc_ins_{i}"):
                        del st.session_state[f"confirmar_inscricao_{i}"]; st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

        # Detalhes expandidos
        if st.session_state.get(f"ver_ch_{i}"):
            with st.expander("Detalhes da Chamada", expanded=True):
                col1, col2, col3 = st.columns(3)
                with col1: st.markdown(f'<div class="metric-box"><p class="metric-label">Remuneração</p><p class="metric-value" style="font-size:15px">{ch.get("remuneracao","—")}</p></div>', unsafe_allow_html=True)
                with col2: st.markdown(f'<div class="metric-box"><p class="metric-label">Regime</p><p class="metric-value" style="font-size:15px">{ch.get("regime","—")}</p></div>', unsafe_allow_html=True)
                with col3: st.markdown(f'<div class="metric-box"><p class="metric-label">Forma de seleção</p><p class="metric-value" style="font-size:15px">{ch.get("forma_selecao","—")}</p></div>', unsafe_allow_html=True)
                if ch.get("requisitos"):
                    st.markdown('<p class="section-label">Requisitos</p>', unsafe_allow_html=True)
                    st.markdown(f'<div class="info-card">{ch.get("requisitos")}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="disclaimer-box" style="margin-top:1rem">{DISCLAIMER_CHAMADA}</div>', unsafe_allow_html=True)

    # Cadastro de interesse (Nível 2)
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    st.markdown('<p style="font-size:15px;font-weight:700;color:#1a3a8f;margin-bottom:4px">Receba avisos de novas Chamadas</p>', unsafe_allow_html=True)
    st.markdown('<p style="font-size:13px;color:#8090b8;margin-bottom:1rem">Deixe seu e-mail e área de interesse. Quando surgir uma Chamada compatível, você será avisado.</p>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1: email_interesse = st.text_input("Seu e-mail", key="email_interesse")
    with col2: areas_interesse = st.multiselect("Áreas de interesse", AREAS, key="areas_interesse")
    with col3: estados_interesse = st.multiselect("Estados", ESTADOS, key="estados_interesse")
    if st.button("Quero receber avisos", key="btn_interesse"):
        if not email_interesse or not areas_interesse:
            st.error("Preencha e-mail e ao menos uma área de interesse.")
        else:
            aba_interesses.append_row([email_interesse, ", ".join(areas_interesse), ", ".join(estados_interesse), datetime.now().strftime("%d/%m/%Y")])
            st.success("Pronto! Você será avisado quando surgir uma Chamada compatível.")

# ── Página: Cadastrar currículo ───────────────────────────────────────────────
elif pagina == "Cadastrar currículo":
    if "etapa_cand" not in st.session_state: st.session_state.etapa_cand = 1
    if "campos" not in st.session_state: st.session_state.campos = {}
    if "dados_cand" not in st.session_state: st.session_state.dados_cand = {}

    etapa = st.session_state.etapa_cand
    titulos = [
        ("Seus dados\nprofissionais.", "Preencha ou faça upload do seu currículo em PDF"),
        ("Certificação e\nreferências.", "Documentos que geram selos e aumentam sua visibilidade"),
        ("Perfil\ncomportamental.", "12 perguntas rápidas — cerca de 3 minutos"),
    ]
    titulo, subtitulo = titulos[etapa - 1]
    st.markdown(f'<div class="page-hero"><div class="page-title">{titulo}</div><div class="page-sub">{subtitulo}</div></div>', unsafe_allow_html=True)
    st.markdown(barra_etapas(etapa, total=3), unsafe_allow_html=True)
    st.markdown(f'<p class="step-title">Etapa {etapa} de 3</p>', unsafe_allow_html=True)

    if etapa == 1:
        pdf = st.file_uploader("Upload do currículo em PDF (opcional — preenche os campos automaticamente)", type="pdf")
        if pdf and not st.session_state.campos:
            with st.spinner("Extraindo dados do currículo..."):
                texto = extrair_texto_pdf(pdf)
                st.session_state.campos = extrair_campos(texto)
            st.rerun()
        if pdf is None: st.session_state.campos = {}
        campos = st.session_state.campos
        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1: nome = st.text_input("Nome completo *", value=campos.get("nome", ""))
        with col2: email = st.text_input("E-mail *", value=campos.get("email", ""))
        col1, col2, col3 = st.columns(3)
        with col1: formacao = st.selectbox("Formação *", ["Bacharel em Direito", "Pós-graduado em Direito", "Mestre em Direito", "Doutor em Direito"])
        with col2: instituicao = st.text_input("Instituição *")
        with col3: area = st.selectbox("Área de interesse *", ["Tribunal", "MP", "Procuradoria", "Defensoria", "TCU/TCE"])
        col1, col2, col3 = st.columns(3)
        with col1: oab = st.radio("OAB ativa?", ["Sim", "Não"], index=0 if campos.get("oab") == "Sim" else 1, horizontal=True)
        with col2: anos_experiencia = st.number_input("Anos em órgão público", min_value=0, max_value=40, value=0)
        with col3: disponibilidade = st.radio("Disponível?", ["Sim", "Não"], horizontal=True)

        experiencia = st.text_input("Órgãos de atuação", value=campos.get("experiencia_orgaos", ""))
        sistemas = st.text_input("Sistemas dominados", value=campos.get("sistemas", ""))
        pos = st.text_input("Pós-graduação", value=campos.get("pos_graduacao", ""))
        resumo = st.text_area("Resumo profissional", value=campos.get("resumo", ""), height=120)

        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
        st.markdown('<p style="font-weight:600;color:#1a3a8f;margin-bottom:4px">Está estudando para algum concurso?</p>', unsafe_allow_html=True)
        concurso = st.selectbox("", CONCURSOS, label_visibility="collapsed")

        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
        consentimento = st.checkbox("Li e aceito a Política de Privacidade e os Termos de Uso do JurisBank. Consinto com o tratamento dos meus dados pessoais para as finalidades descritas nesses documentos, nos termos da Lei nº 13.709/2018 (LGPD).")
        st.markdown('<p style="font-size:11px;color:#8090b8;margin-top:4px">Acesse a Política de Privacidade e os Termos de Uso no menu lateral.</p>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Próximo →"):
            if not nome or not email or not instituicao: st.error("Preencha os campos obrigatórios: nome, e-mail e instituição.")
            elif not consentimento: st.error("É necessário aceitar a Política de Privacidade e os Termos de Uso para continuar.")
            else:
                st.session_state.dados_cand.update({"nome": nome, "email": email, "formacao": formacao, "instituicao": instituicao, "area": area, "oab": oab, "anos_experiencia": anos_experiencia, "disponibilidade": disponibilidade, "experiencia": experiencia, "sistemas": sistemas, "pos": pos, "resumo": resumo, "concurso": concurso})
                st.session_state.etapa_cand = 2; st.rerun()

    elif etapa == 2:
        st.markdown('<p style="font-size:14px;color:#8090b8;margin-bottom:1.5rem">Estes documentos são opcionais mas geram selos que destacam seu perfil para os recrutadores.</p>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<p style="font-weight:600;color:#1a3a8f;margin-bottom:4px">★ Carta de recomendação</p>', unsafe_allow_html=True)
            st.markdown('<p style="font-size:12px;color:#8090b8;margin-bottom:8px">De um Juiz, Promotor, Defensor ou Procurador ativo</p>', unsafe_allow_html=True)
            carta = st.file_uploader("", type="pdf", key="carta", label_visibility="collapsed")
        with col2:
            st.markdown('<p style="font-weight:600;color:#1a3a8f;margin-bottom:4px">◆ Avaliação de desempenho</p>', unsafe_allow_html=True)
            st.markdown('<p style="font-size:12px;color:#8090b8;margin-bottom:8px">Avaliação formal emitida pelo órgão</p>', unsafe_allow_html=True)
            avaliacao = st.file_uploader("", type="pdf", key="avaliacao", label_visibility="collapsed")

        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
        st.markdown('<p style="font-weight:600;color:#1a3a8f;margin-bottom:4px">E-mail institucional do recomendador</p>', unsafe_allow_html=True)
        email_ref = st.text_input("", placeholder="nome@mpsc.mp.br ou nome@tjsc.jus.br", key="email_ref", label_visibility="collapsed")
        dominios_validos = ["mpsc.mp.br", "tjsc.jus.br", "sc.def.br", "pge.sc.gov.br", "trf4.jus.br", "jfsc.jus.br", "mpf.mp.br", "agu.gov.br"]
        if email_ref and "@" in email_ref:
            dominio = email_ref.split("@")[-1]
            if dominio in dominios_validos: st.markdown('<div class="info-box">✓ E-mail institucional reconhecido.</div>', unsafe_allow_html=True)
            else: st.warning("Domínio não reconhecido. Verifique se o e-mail é institucional.")

        selos_preview = []
        d = st.session_state.dados_cand
        if d.get("oab") == "Sim": selos_preview.append("✓ Verificado")
        if carta: selos_preview.append("★ Recomendado")
        if avaliacao: selos_preview.append("◆ Destaque")
        if d.get("anos_experiencia", 0) >= 2: selos_preview.append("● Experiente")
        if selos_preview:
            st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
            st.markdown('<p style="font-size:13px;font-weight:600;color:#1a3a8f">Selos que você vai receber:</p>', unsafe_allow_html=True)
            st.markdown(" ".join([f'<span class="selo selo-verificado">{s}</span>' for s in selos_preview]), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Voltar"): st.session_state.etapa_cand = 1; st.rerun()
        with col2:
            if st.button("Próximo →"):
                st.session_state.dados_cand.update({"carta": carta is not None, "avaliacao": avaliacao is not None, "email_ref": email_ref})
                st.session_state.etapa_cand = 3; st.rerun()

    elif etapa == 3:
        st.markdown('<p style="font-size:14px;color:#8090b8;margin-bottom:1.5rem">Escolha a opção que mais se identifica em cada situação. Não há respostas certas ou erradas.</p>', unsafe_allow_html=True)
        respostas_disc = []
        for j, (pergunta, opcoes) in enumerate(PERGUNTAS_DISC):
            resp = st.radio(f"**{j+1}.** {pergunta}", opcoes, key=f"disc_{j}", index=None)
            respostas_disc.append(resp)

        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Voltar"): st.session_state.etapa_cand = 2; st.rerun()
        with col2:
            if st.button("Cadastrar no JurisBank →"):
                if None in respostas_disc: st.error("Responda todas as 12 perguntas para concluir o cadastro.")
                else:
                    d = st.session_state.dados_cand
                    selos = calcular_selos(d["oab"], d["anos_experiencia"], d.get("carta", False), d.get("avaliacao", False))
                    perfil_disc, _, descricao_disc = calcular_disc(respostas_disc)
                    aba_candidatos.append_row([d["nome"], d["email"], d["formacao"], d["instituicao"], d["area"], d["disponibilidade"], d["oab"], d["experiencia"], d["sistemas"], d["pos"], d["resumo"], d.get("email_ref", ""), selos["verificado"], selos["recomendado"], selos["destaque"], selos["experiente"], perfil_disc, d.get("concurso", "Não estou estudando para concurso")])
                    st.session_state.etapa_cand = 1
                    st.session_state.campos = {}
                    st.session_state.dados_cand = {}
                    st.success(f"Bem-vindo ao JurisBank, {d['nome']}!")
                    st.markdown(f'<div class="info-box" style="margin-top:1rem">Seu perfil comportamental: <strong>{perfil_disc} — {descricao_disc}</strong></div>', unsafe_allow_html=True)
                    st.balloons()

# ── Página: Área do Recrutador ────────────────────────────────────────────────
elif pagina == "Área do Recrutador":
    if recrutador_logado():
        rec = st.session_state.recrutador_logado
        dados = aba_candidatos.get_all_records()
        recrutadores = aba_recrutadores.get_all_records()
        idx_rec = next((i for i, r in enumerate(recrutadores) if r["email"] == rec["email"]), None)
        rec_atual = recrutadores[idx_rec] if idx_rec is not None else rec
        favoritos = [f.strip() for f in str(rec_atual.get("favoritos", "")).split(",") if f.strip()]
        anotacoes = {}
        for item in str(rec_atual.get("anotacoes", "")).split("|"):
            if "::" in item:
                email_cand, nota = item.split("::", 1)
                anotacoes[email_cand.strip()] = nota.strip()

        minhas_chamadas = [ch for ch in aba_chamadas.get_all_records() if ch.get("email_recrutador") == rec["email"]]

        st.markdown(f"""
        <div class="page-hero">
            <div class="page-title">Olá, {rec['nome'].split()[0]}!</div>
            <div class="page-sub">{rec_atual.get('nome_orgao', rec.get('orgao',''))} · {rec.get('estado','')}</div>
            <div class="stats-row">
                <div class="stat-pill">⚖ {len(dados)} candidatos</div>
                <div class="stat-pill">★ {len(favoritos)} favoritos</div>
                <div class="stat-pill">📢 {len(minhas_chamadas)} chamadas</div>
                <div class="stat-pill">✓ {sum(1 for c in dados if c.get('disponibilidade')=='Sim')} disponíveis</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        aba_dashboard = st.tabs(["🔍 Busca avançada", "📢 Minhas Chamadas", "★ Favoritos"])

        # ── Aba: Busca avançada ──
        with aba_dashboard[0]:
            st.markdown('<p style="font-size:15px;font-weight:700;color:#1a3a8f;margin-bottom:1rem">Filtros</p>', unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)
            with col1: busca = st.text_input("Nome", placeholder="Buscar por nome...")
            with col2:
                areas_disp = ["Todas"] + sorted(set(c["area"] for c in dados if c.get("area")))
                area_sel = st.selectbox("Área", areas_disp)
            with col3: disp_sel = st.selectbox("Disponibilidade", ["Todos", "Disponível", "Indisponível"])

            col1, col2, col3, col4, col5, col6 = st.columns(6)
            with col1: oab_sel = st.selectbox("OAB", ["Todos", "Sim", "Não"])
            with col2: selo_sel = st.selectbox("Selo", ["Todos", "Verificado", "Recomendado", "Destaque", "Experiente"])
            with col3:
                disc_sel = st.selectbox("DISC", ["Todos", "D — Dominante", "I — Influente", "S — Estável", "C — Conformidade"])
                if disc_sel != "Todos":
                    st.markdown(f'<div style="background:#eff6ff;border:1px solid #b0c5f5;border-radius:8px;padding:8px 12px;font-size:11px;color:#1e3a8a;margin-top:4px">ℹ {DISC_EXPLICACOES_FILTRO.get(disc_sel,"")}</div>', unsafe_allow_html=True)
            with col4: concurso_sel = st.selectbox("Concurso", ["Todos", "Concursando", "Não concursando"])
            with col5: sistema_sel = st.text_input("Sistema", placeholder="Ex: Eproc")
            with col6: exp_min = st.number_input("Exp. mín.", min_value=0, max_value=20, value=0)

            filtrados = dados
            if busca: filtrados = [c for c in filtrados if busca.lower() in c["nome"].lower()]
            if area_sel != "Todas": filtrados = [c for c in filtrados if c.get("area") == area_sel]
            if disp_sel != "Todos":
                val = "Sim" if disp_sel == "Disponível" else "Não"
                filtrados = [c for c in filtrados if c.get("disponibilidade") == val]
            if oab_sel != "Todos": filtrados = [c for c in filtrados if c.get("oab") == oab_sel]
            if selo_sel != "Todos":
                col_map = {"Verificado": "selo_verificado", "Recomendado": "selo_recomendado", "Destaque": "selo_destaque", "Experiente": "selo_experiente"}
                filtrados = [c for c in filtrados if c.get(col_map[selo_sel]) == "Sim"]
            if disc_sel != "Todos": filtrados = [c for c in filtrados if c.get("disc") == disc_sel[0]]
            if concurso_sel == "Concursando": filtrados = [c for c in filtrados if c.get("concurso") and c.get("concurso") != "Não estou estudando para concurso"]
            elif concurso_sel == "Não concursando": filtrados = [c for c in filtrados if not c.get("concurso") or c.get("concurso") == "Não estou estudando para concurso"]
            if sistema_sel: filtrados = [c for c in filtrados if sistema_sel.lower() in str(c.get("sistemas","")).lower()]

            st.markdown(f'<p style="font-size:13px;color:#8090b8;margin:1rem 0 0.5rem;font-weight:500">{len(filtrados)} candidato(s) encontrado(s)</p>', unsafe_allow_html=True)

            for i, candidato in enumerate(filtrados):
                cor = cor_avatar(candidato["nome"])
                disp = candidato.get("disponibilidade", "Não")
                badge = '<span class="badge-sim">● Disponível</span>' if disp == "Sim" else '<span class="badge-nao">● Indisponível</span>'
                email_c = candidato.get("email", "")
                is_fav = email_c in favoritos
                fav_icon = "★" if is_fav else "☆"

                with st.container():
                    st.markdown(f"""
                    <div class="cand-card">
                        <div style="display:flex;align-items:center;justify-content:space-between;gap:12px">
                            <div style="display:flex;align-items:center;gap:14px;flex:1">
                                <div class="avatar" style="background:{cor}">{iniciais(candidato['nome'])}</div>
                                <div>
                                    <p class="cand-name">{candidato['nome']}</p>
                                    <p class="cand-sub">{candidato.get('formacao','—')} · {candidato.get('instituicao','—')} · {candidato.get('area','—')}</p>
                                    <div style="margin-top:4px">{html_selos(candidato)}{html_disc_badge(candidato)}{html_concurso_badge(candidato)}</div>
                                </div>
                            </div>
                            <div style="flex-shrink:0">{badge}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    col_a, col_b, col_c = st.columns([6, 2, 2])
                    with col_b:
                        if st.button(f"{fav_icon} Favoritar", key=f"fav_{i}"):
                            if is_fav: favoritos.remove(email_c)
                            else: favoritos.append(email_c)
                            aba_recrutadores.update_cell(idx_rec + 2, 12, ", ".join(favoritos))
                            st.session_state.recrutador_logado = aba_recrutadores.get_all_records()[idx_rec]
                            st.rerun()
                    with col_c:
                        if st.button("Ver perfil →", key=f"rec_btn_{i}"):
                            st.session_state.candidato_selecionado_rec = candidato; st.rerun()

                if email_c in anotacoes:
                    st.markdown(f'<div class="info-card" style="margin-top:-8px;margin-bottom:8px;font-size:12px">📝 {anotacoes[email_c]}</div>', unsafe_allow_html=True)

                if st.session_state.get("candidato_selecionado_rec") == candidato:
                    with st.expander("Perfil completo", expanded=True):
                        col1, col2, col3 = st.columns(3)
                        for col, label, val in [(col1,"OAB",candidato.get("oab","—")),(col2,"Órgãos",candidato.get("experiencia_orgaos","—") or "—"),(col3,"Sistemas",candidato.get("sistemas","—") or "—")]:
                            with col: st.markdown(f'<div class="metric-box"><p class="metric-label">{label}</p><p class="metric-value" style="font-size:13px">{val}</p></div>', unsafe_allow_html=True)
                        if candidato.get("disc"): st.markdown(render_disc_perfil(candidato.get("disc")), unsafe_allow_html=True)
                        if candidato.get("concurso") and candidato.get("concurso") != "Não estou estudando para concurso":
                            st.markdown(f'<div class="info-card" style="margin-top:1rem;background:#fff8e6;border-color:#fde68a">📚 <strong>Estudando para:</strong> {candidato.get("concurso")}</div>', unsafe_allow_html=True)
                        if candidato.get("resumo"): st.markdown(f'<div class="info-card" style="margin-top:1rem">{candidato.get("resumo")}</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="info-card" style="margin-top:0.5rem">✉ {candidato.get("email","—")}</div>', unsafe_allow_html=True)
                        st.markdown('<p style="font-size:12px;font-weight:600;color:#1a3a8f;margin-top:1rem">Anotação privada</p>', unsafe_allow_html=True)
                        nota_atual = anotacoes.get(email_c, "")
                        nova_nota = st.text_area("", value=nota_atual, height=80, key=f"nota_{i}", placeholder="Suas anotações sobre este candidato...")
                        col_salvar, col_fechar = st.columns(2)
                        with col_salvar:
                            if st.button("Salvar anotação", key=f"salvar_nota_{i}"):
                                anotacoes[email_c] = nova_nota
                                aba_recrutadores.update_cell(idx_rec + 2, 13, "|".join([f"{k}::{v}" for k, v in anotacoes.items()]))
                                st.success("Anotação salva!"); st.rerun()
                        with col_fechar:
                            if st.button("Fechar", key=f"fechar_{i}"):
                                del st.session_state["candidato_selecionado_rec"]; st.rerun()

        # ── Aba: Minhas Chamadas ──
        with aba_dashboard[1]:
            col_titulo, col_btn = st.columns([8, 3])
            with col_titulo: st.markdown('<p style="font-size:15px;font-weight:700;color:#1a3a8f">Minhas Chamadas</p>', unsafe_allow_html=True)
            with col_btn:
                if st.button("+ Nova Chamada", key="btn_nova_chamada"):
                    st.session_state["criar_chamada"] = True; st.rerun()

            # Formulário de criação
            if st.session_state.get("criar_chamada"):
                with st.expander("Nova Chamada", expanded=True):
                    st.markdown('<p style="font-size:15px;font-weight:700;color:#1a3a8f;margin-bottom:1rem">Publicar nova Chamada</p>', unsafe_allow_html=True)
                    st.markdown(f'<div class="disclaimer-box">{DISCLAIMER_CHAMADA}</div>', unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)

                    titulo_ch = st.text_input("Título da vaga *", placeholder="Ex: Assessor Jurídico — 3ª Promotoria de Jaraguá do Sul")
                    col1, col2 = st.columns(2)
                    with col1: orgao_ch = st.text_input("Nome do órgão *", value=rec_atual.get("nome_orgao", ""))
                    with col2: tipo_orgao_ch = st.selectbox("Tipo de órgão *", ["Selecione..."] + ORGAOS)
                    col1, col2, col3 = st.columns(3)
                    with col1: area_ch = st.selectbox("Área *", ["Selecione..."] + AREAS)
                    with col2: estado_ch = st.selectbox("Estado *", ["Selecione..."] + ESTADOS, index=ESTADOS.index(rec.get("estado","SC")) + 1 if rec.get("estado","") in ESTADOS else 0)
                    with col3: municipio_ch = st.text_input("Município *", value=rec_atual.get("municipio", ""))
                    requisitos_ch = st.text_area("Requisitos *", height=100, placeholder="Descreva os requisitos para a vaga...")
                    col1, col2, col3 = st.columns(3)
                    with col1: remuneracao_ch = st.text_input("Remuneração *", placeholder="Ex: R$ 4.500,00")
                    with col2: regime_ch = st.selectbox("Regime *", ["Selecione..."] + REGIMES)
                    with col3: vagas_ch = st.number_input("Nº de vagas *", min_value=1, max_value=20, value=1)
                    col1, col2 = st.columns(2)
                    with col1: forma_selecao_ch = st.selectbox("Forma de seleção *", ["Selecione..."] + FORMAS_SELECAO)
                    with col2: prazo_ch = st.date_input("Prazo de inscrição *", min_value=date.today())

                    st.markdown("<br>", unsafe_allow_html=True)
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Cancelar", key="cancelar_chamada"):
                            del st.session_state["criar_chamada"]; st.rerun()
                    with col2:
                        if st.button("Publicar Chamada →", key="publicar_chamada"):
                            campos_ok = all([titulo_ch, orgao_ch, tipo_orgao_ch != "Selecione...", area_ch != "Selecione...", estado_ch != "Selecione...", municipio_ch, requisitos_ch, remuneracao_ch, regime_ch != "Selecione...", forma_selecao_ch != "Selecione..."])
                            if not campos_ok: st.error("Preencha todos os campos obrigatórios.")
                            else:
                                novo_id = gerar_id_chamada()
                                aba_chamadas.append_row([
                                    novo_id, titulo_ch, orgao_ch, tipo_orgao_ch, area_ch,
                                    estado_ch, municipio_ch, requisitos_ch, remuneracao_ch,
                                    regime_ch, forma_selecao_ch, str(vagas_ch),
                                    prazo_ch.strftime("%d/%m/%Y"), "aberto",
                                    rec["email"], "", datetime.now().strftime("%d/%m/%Y")
                                ])
                                del st.session_state["criar_chamada"]
                                st.success("Chamada publicada com sucesso!")
                                st.rerun()

            # Lista de chamadas do recrutador
            if not minhas_chamadas:
                st.info("Você ainda não publicou nenhuma Chamada. Clique em '+ Nova Chamada' para começar.")
            else:
                for i, ch in enumerate(minhas_chamadas):
                    aberta = chamada_aberta(ch)
                    inscritos = inscritos_chamada(ch)
                    n_inscritos = len(inscritos)
                    status_badge = '<span class="badge-aberta">● Aberta</span>' if aberta else '<span class="badge-encerrada">● Encerrada</span>'

                    st.markdown(f"""
                    <div class="chamada-card">
                        <div style="display:flex;justify-content:space-between;align-items:flex-start">
                            <div>
                                <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px">
                                    {status_badge}
                                    <span style="font-size:11px;color:#8090b8">📅 {ch.get('prazo','—')}</span>
                                </div>
                                <p style="font-size:16px;font-weight:700;color:#1a3a8f;margin:0 0 4px">{ch.get('titulo','—')}</p>
                                <p style="font-size:13px;color:#6080c0;margin:0">{ch.get('municipio','—')}/{ch.get('estado','—')} · {ch.get('area','—')} · {ch.get('regime','—')}</p>
                            </div>
                            <div style="text-align:right;flex-shrink:0">
                                <p style="font-size:24px;font-weight:800;color:#1a3a8f;margin:0">{n_inscritos}</p>
                                <p style="font-size:11px;color:#8090b8;margin:0">inscrito(s)</p>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    col_ver, col_enc = st.columns([8, 3])
                    with col_ver:
                        if st.button("Ver inscritos", key=f"ver_ins_{i}"):
                            st.session_state[f"ver_ins_ch_{i}"] = not st.session_state.get(f"ver_ins_ch_{i}", False)
                            st.rerun()
                    with col_enc:
                        if aberta:
                            if st.button("Encerrar Chamada", key=f"enc_ch_{i}"):
                                todas = aba_chamadas.get_all_records()
                                idx_ch = next((j for j, c in enumerate(todas) if c.get("id") == ch.get("id")), None)
                                if idx_ch is not None:
                                    aba_chamadas.update_cell(idx_ch + 2, 14, "encerrado")
                                st.success("Chamada encerrada.")
                                st.rerun()

                    # Dashboard de inscritos — sem nomes, só dados agregados
                    if st.session_state.get(f"ver_ins_ch_{i}"):
                        with st.expander("Inscritos — Painel", expanded=True):
                            if not inscritos:
                                st.info("Nenhum inscrito ainda.")
                            else:
                                todos_cands = aba_candidatos.get_all_records()
                                inscritos_dados = [c for c in todos_cands if c.get("email","") in inscritos]

                                # Métricas agregadas
                                total_ins = len(inscritos_dados)
                                com_oab = sum(1 for c in inscritos_dados if c.get("oab") == "Sim")
                                disponiveis_ins = sum(1 for c in inscritos_dados if c.get("disponibilidade") == "Sim")
                                col1, col2, col3 = st.columns(3)
                                with col1: st.markdown(f'<div class="metric-box"><p class="metric-label">Total inscritos</p><p class="metric-value">{total_ins}</p></div>', unsafe_allow_html=True)
                                with col2: st.markdown(f'<div class="metric-box"><p class="metric-label">Com OAB ativa</p><p class="metric-value">{com_oab}</p></div>', unsafe_allow_html=True)
                                with col3: st.markdown(f'<div class="metric-box"><p class="metric-label">Disponíveis</p><p class="metric-value">{disponiveis_ins}</p></div>', unsafe_allow_html=True)

                                # Distribuição DISC
                                disc_count = {}
                                for c in inscritos_dados:
                                    d = c.get("disc","")
                                    if d: disc_count[d] = disc_count.get(d, 0) + 1
                                if disc_count:
                                    st.markdown('<p class="section-label">Distribuição de perfis DISC</p>', unsafe_allow_html=True)
                                    cols_disc = st.columns(4)
                                    for idx_d, letra in enumerate(["D","I","S","C"]):
                                        with cols_disc[idx_d]:
                                            cor_bg = DISC_CORES_BADGE.get(letra, "#f4f4f4")
                                            cor_txt = DISC_TEXTO_BADGE.get(letra, "#333")
                                            st.markdown(f'<div class="metric-box" style="background:{cor_bg}"><p class="metric-label" style="color:{cor_txt}">{DISC_LABEL.get(letra,"")}</p><p class="metric-value" style="color:{cor_txt}">{disc_count.get(letra,0)}</p></div>', unsafe_allow_html=True)

                                # Lista de inscritos com perfil completo (só para o recrutador)
                                st.markdown('<p class="section-label">Perfis inscritos</p>', unsafe_allow_html=True)
                                for candidato in inscritos_dados:
                                    cor = cor_avatar(candidato["nome"])
                                    st.markdown(f"""
                                    <div class="cand-card" style="margin-bottom:8px">
                                        <div style="display:flex;align-items:center;gap:14px">
                                            <div class="avatar" style="background:{cor}">{iniciais(candidato['nome'])}</div>
                                            <div style="flex:1">
                                                <p class="cand-name">{candidato['nome']}</p>
                                                <p class="cand-sub">{candidato.get('formacao','—')} · {candidato.get('instituicao','—')}</p>
                                                <div style="margin-top:4px">{html_selos(candidato)}{html_disc_badge(candidato)}</div>
                                            </div>
                                            <div style="font-size:13px;color:#3a5a9a">✉ {candidato.get('email','—')}</div>
                                        </div>
                                    </div>
                                    """, unsafe_allow_html=True)

        # ── Aba: Favoritos ──
        with aba_dashboard[2]:
            favoritos_dados = [c for c in dados if c.get("email", "") in favoritos]
            if not favoritos_dados:
                st.info("Você ainda não tem candidatos favoritos. Use ★ Favoritar na busca para salvar candidatos.")
            else:
                st.markdown(f'<p style="font-size:13px;color:#8090b8;margin-bottom:1rem;font-weight:500">{len(favoritos_dados)} candidato(s) favoritado(s)</p>', unsafe_allow_html=True)
                for i, candidato in enumerate(favoritos_dados):
                    cor = cor_avatar(candidato["nome"])
                    email_c = candidato.get("email", "")
                    nota = anotacoes.get(email_c, "")
                    disp = candidato.get("disponibilidade", "Não")
                    with st.container(border=True):
                        col_av, col_info, col_badge, col_btn = st.columns([1, 7, 2, 1])
                        with col_av: st.markdown(f'<div class="avatar" style="background:{cor};margin-top:6px">{iniciais(candidato["nome"])}</div>', unsafe_allow_html=True)
                        with col_info:
                            st.markdown(f'<p class="cand-name" style="margin-top:6px">{candidato["nome"]}</p>', unsafe_allow_html=True)
                            st.markdown(f'<p class="cand-sub">{candidato.get("formacao","—")} · {candidato.get("instituicao","—")} · {candidato.get("area","—")}</p>', unsafe_allow_html=True)
                            if html_selos(candidato): st.markdown(html_selos(candidato), unsafe_allow_html=True)
                            if nota: st.markdown(f'<p style="font-size:11px;color:#8090b8;margin-top:4px">📝 {nota}</p>', unsafe_allow_html=True)
                        with col_badge:
                            st.write("")
                            if disp == "Sim": st.markdown('<span class="badge-sim">● Disponível</span>', unsafe_allow_html=True)
                            else: st.markdown('<span class="badge-nao">● Indisponível</span>', unsafe_allow_html=True)
                        with col_btn:
                            st.write("")
                            if st.button("✕", key=f"rem_fav_{i}", help="Remover dos favoritos"):
                                favoritos.remove(email_c)
                                aba_recrutadores.update_cell(idx_rec + 2, 12, ", ".join(favoritos))
                                st.rerun()

    elif "cadastro_rec" not in st.session_state:
        st.markdown("""
        <div class="page-hero">
            <div class="page-title">Área do<br>Recrutador.</div>
            <div class="page-sub">Acesse o banco de talentos jurídicos certificados</div>
        </div>
        """, unsafe_allow_html=True)
        aba = st.tabs(["Entrar", "Criar conta"])
        with aba[0]:
            st.markdown('<p style="font-size:16px;font-weight:700;color:#1a3a8f;margin:1rem 0 1rem">Acesse sua conta</p>', unsafe_allow_html=True)
            email_login = st.text_input("E-mail institucional", key="login_email")
            senha_login = st.text_input("Senha", type="password", key="login_senha")
            if st.button("Entrar →", key="btn_login"):
                if email_login and senha_login:
                    recrutadores = aba_recrutadores.get_all_records()
                    senha_hash = hash_senha(senha_login)
                    encontrado = next((r for r in recrutadores if r["email"] == email_login and r["senha"] == senha_hash and r["status"] == "ativo"), None)
                    if encontrado: st.session_state.recrutador_logado = encontrado; st.rerun()
                    else: st.error("E-mail ou senha incorretos, ou conta ainda não aprovada.")
                else: st.error("Preencha e-mail e senha.")
        with aba[1]:
            st.markdown('<p style="font-size:16px;font-weight:700;color:#1a3a8f;margin:1rem 0 0.5rem">Criar conta de recrutador</p>', unsafe_allow_html=True)
            st.markdown('<p style="font-size:13px;color:#8090b8;margin-bottom:1rem">Preencha em 4 etapas rápidas. Sua conta será ativada após validação do e-mail institucional.</p>', unsafe_allow_html=True)
            if st.button("Começar cadastro →", key="btn_cadastro"):
                st.session_state.cadastro_rec = {"etapa": 1}; st.rerun()

    else:
        etapa = st.session_state.cadastro_rec.get("etapa", 1)
        st.markdown(barra_etapas(etapa), unsafe_allow_html=True)

        if etapa == 1:
            st.markdown('<p class="step-title">Etapa 1 de 4</p>', unsafe_allow_html=True)
            st.markdown('<p class="step-desc">Onde você atua?</p>', unsafe_allow_html=True)
            estado = st.selectbox("Estado *", ["Selecione..."] + ESTADOS)
            municipio = st.text_input("Município *", placeholder="Ex: Florianópolis")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Próximo →"):
                if estado == "Selecione..." or not municipio: st.error("Preencha todos os campos.")
                else:
                    st.session_state.cadastro_rec["estado"] = estado
                    st.session_state.cadastro_rec["municipio"] = municipio
                    st.session_state.cadastro_rec["etapa"] = 2; st.rerun()

        elif etapa == 2:
            st.markdown('<p class="step-title">Etapa 2 de 4</p>', unsafe_allow_html=True)
            st.markdown('<p class="step-desc">Qual é o seu órgão?</p>', unsafe_allow_html=True)
            orgao = st.selectbox("Tipo de órgão *", ["Selecione..."] + ORGAOS)
            nome_orgao = st.text_input("Nome do órgão/comarca *", placeholder="Ex: MPSC — 3ª Promotoria de Jaraguá do Sul")
            st.markdown("<br>", unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                if st.button("← Voltar"): st.session_state.cadastro_rec["etapa"] = 1; st.rerun()
            with col2:
                if st.button("Próximo →"):
                    if orgao == "Selecione..." or not nome_orgao: st.error("Preencha todos os campos.")
                    else:
                        st.session_state.cadastro_rec["orgao"] = orgao
                        st.session_state.cadastro_rec["nome_orgao"] = nome_orgao
                        st.session_state.cadastro_rec["etapa"] = 3; st.rerun()

        elif etapa == 3:
            st.markdown('<p class="step-title">Etapa 3 de 4</p>', unsafe_allow_html=True)
            st.markdown('<p class="step-desc">Seu perfil de atuação</p>', unsafe_allow_html=True)
            cargo = st.selectbox("Seu cargo *", ["Selecione..."] + CARGOS)
            areas_sel = st.multiselect("Áreas de atuação *", AREAS)
            st.markdown("<br>", unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                if st.button("← Voltar"): st.session_state.cadastro_rec["etapa"] = 2; st.rerun()
            with col2:
                if st.button("Próximo →"):
                    if cargo == "Selecione..." or not areas_sel: st.error("Preencha todos os campos.")
                    else:
                        st.session_state.cadastro_rec["cargo"] = cargo
                        st.session_state.cadastro_rec["areas"] = ", ".join(areas_sel)
                        st.session_state.cadastro_rec["etapa"] = 4; st.rerun()

        elif etapa == 4:
            st.markdown('<p class="step-title">Etapa 4 de 4</p>', unsafe_allow_html=True)
            st.markdown('<p class="step-desc">Crie seu acesso</p>', unsafe_allow_html=True)
            nome_rec = st.text_input("Nome completo *")
            email_rec = st.text_input("E-mail institucional *", placeholder="nome@mpsc.mp.br ou nome@tjsc.jus.br")
            dominios_validos = ["mpsc.mp.br", "tjsc.jus.br", "sc.def.br", "pge.sc.gov.br", "trf4.jus.br", "jfsc.jus.br", "mpf.mp.br", "agu.gov.br", "pgfn.gov.br"]
            if email_rec and "@" in email_rec:
                dominio = email_rec.split("@")[-1]
                if dominio in dominios_validos: st.markdown('<div class="info-box">✓ E-mail institucional reconhecido.</div>', unsafe_allow_html=True)
                else: st.warning("Domínio não reconhecido. Sua conta passará por validação manual.")
            senha_rec = st.text_input("Senha *", type="password")
            senha_conf = st.text_input("Confirmar senha *", type="password")
            st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
            consentimento_rec = st.checkbox("Li e aceito a Política de Privacidade e os Termos de Uso do JurisBank. Comprometo-me a utilizar os dados dos candidatos exclusivamente para fins de seleção profissional, nos termos da Lei nº 13.709/2018 (LGPD).")
            st.markdown("<br>", unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                if st.button("← Voltar"): st.session_state.cadastro_rec["etapa"] = 3; st.rerun()
            with col2:
                if st.button("Finalizar cadastro →"):
                    if not nome_rec or not email_rec or not senha_rec: st.error("Preencha todos os campos.")
                    elif senha_rec != senha_conf: st.error("As senhas não coincidem.")
                    elif len(senha_rec) < 6: st.error("A senha deve ter pelo menos 6 caracteres.")
                    elif not consentimento_rec: st.error("É necessário aceitar a Política de Privacidade e os Termos de Uso.")
                    else:
                        dados_rec = st.session_state.cadastro_rec
                        aba_recrutadores.append_row([nome_rec, email_rec, hash_senha(senha_rec), dados_rec["estado"], dados_rec["municipio"], dados_rec["orgao"], dados_rec["nome_orgao"], dados_rec["cargo"], dados_rec["areas"], "pendente", datetime.now().strftime("%d/%m/%Y %H:%M")])
                        del st.session_state.cadastro_rec
                        st.success("Cadastro realizado! Sua conta será ativada após validação. Aguarde o contato do JurisBank.")
                        st.balloons()

# ── Página: Política de Privacidade ──────────────────────────────────────────
elif pagina == "Política de Privacidade":
    st.markdown('<div class="page-hero"><div class="page-title">Política de<br>Privacidade.</div><div class="page-sub">Versão 1.0 — Como tratamos seus dados pessoais</div></div>', unsafe_allow_html=True)
    secoes = [
        ("1. Identificação do Controlador", [("p", "O JurisBank é uma plataforma de banco de talentos jurídicos certificados, operada por [RAZÃO SOCIAL A PREENCHER], inscrita no CNPJ sob o nº [CNPJ A PREENCHER], com sede em [ENDEREÇO A PREENCHER]."), ("p", "Contato do Encarregado de Proteção de Dados (DPO): [E-MAIL DO DPO A PREENCHER]")]),
        ("2. Dados Coletados", [("h", "Candidatos"), ("l", ["Nome completo", "Endereço de e-mail", "Formação acadêmica e instituição de ensino", "Área de interesse profissional", "Número de inscrição na OAB (quando aplicável)", "Histórico de atuação em órgãos públicos", "Sistemas jurídicos dominados", "Pós-graduação", "Resumo profissional", "Perfil comportamental DISC", "Informação sobre preparação para concursos", "Documentos de referência (quando fornecidos)"]), ("h", "Recrutadores"), ("l", ["Nome completo", "E-mail institucional", "Estado e município de atuação", "Órgão e cargo", "Áreas de atuação", "Senha de acesso (armazenada em hash SHA-256)"])]),
        ("3. Finalidade do Tratamento", [("l", ["Criação e gestão de perfis de candidatos", "Verificação e atribuição de selos de certificação", "Viabilizar a busca e seleção por recrutadores de órgãos públicos", "Envio de comunicações relacionadas ao cadastro", "Gestão de inscrições em Chamadas publicadas na plataforma", "Melhoria contínua dos serviços", "Cumprimento de obrigações legais"])]),
        ("4. Base Legal (LGPD)", [("l", ["Consentimento do titular (Art. 7º, I): para o cadastro e inscrição em Chamadas", "Legítimo interesse do controlador (Art. 7º, IX): para melhoria dos serviços e segurança", "Cumprimento de obrigação legal (Art. 7º, II): quando aplicável"])]),
        ("5. Compartilhamento de Dados", [("p", "Os dados dos candidatos são visíveis para recrutadores cadastrados e aprovados na plataforma. Ao se inscrever em uma Chamada, o candidato autoriza expressamente o compartilhamento de seu perfil com o recrutador responsável pela vaga."), ("p", "O JurisBank não vende, aluga ou compartilha dados pessoais com terceiros para fins comerciais.")]),
        ("6. Armazenamento e Segurança", [("p", "Os dados são armazenados em ambiente seguro com acesso restrito. As senhas dos recrutadores são armazenadas exclusivamente em formato de hash criptográfico (SHA-256), sendo impossível sua recuperação em texto puro.")]),
        ("7. Direitos dos Titulares", [("p", "Nos termos da LGPD, o titular tem direito a:"), ("l", ["Confirmação da existência de tratamento", "Acesso aos dados", "Correção de dados incompletos ou desatualizados", "Eliminação dos dados tratados com base no consentimento", "Portabilidade dos dados", "Revogação do consentimento a qualquer momento"]), ("p", "Para exercer seus direitos: [E-MAIL DO DPO A PREENCHER]")]),
        ("8. Contato", [("l", ["E-mail: [E-MAIL DE CONTATO A PREENCHER]", "DPO: [NOME DO DPO A PREENCHER]", "ANPD: www.gov.br/anpd"])]),
    ]
    for titulo_sec, conteudo in secoes:
        st.markdown(f'<div class="doc-sub">{titulo_sec}</div>', unsafe_allow_html=True)
        for tipo, texto in conteudo:
            if tipo == "p": st.markdown(f'<p class="doc-body">{texto}</p>', unsafe_allow_html=True)
            elif tipo == "h": st.markdown(f'<p style="font-weight:700;color:#1a3a8f;font-size:14px;margin:1rem 0 0.3rem">{texto}</p>', unsafe_allow_html=True)
            elif tipo == "l":
                for item in texto: st.markdown(f'<p class="doc-item">• {item}</p>', unsafe_allow_html=True)
        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    st.markdown(f'<p style="font-size:12px;color:#8090b8;text-align:center">JurisBank — Política de Privacidade — Versão 1.0 — {datetime.now().strftime("%d/%m/%Y")}</p>', unsafe_allow_html=True)

# ── Página: Termos de Uso ─────────────────────────────────────────────────────
elif pagina == "Termos de Uso":
    st.markdown('<div class="page-hero"><div class="page-title">Termos<br>de Uso.</div><div class="page-sub">Versão 1.0 — Regras e condições de uso da plataforma</div></div>', unsafe_allow_html=True)
    secoes_tu = [
        ("1. Aceitação dos Termos", [("p", "Ao acessar ou utilizar a plataforma JurisBank, você concorda com estes Termos de Uso e com a Política de Privacidade. Caso não concorde, não utilize a plataforma.")]),
        ("2. Descrição do Serviço", [("p", "O JurisBank é uma plataforma digital de banco de talentos jurídicos certificados, que conecta profissionais do Direito a recrutadores de Tribunais, Ministérios Públicos, Defensorias, Procuradorias e demais órgãos do sistema de justiça.")]),
        ("3. Chamadas", [("p", "As Chamadas são publicações de vagas de cargos de livre nomeação realizadas por recrutadores aprovados na plataforma. O JurisBank atua exclusivamente como intermediário e não se responsabiliza pelas decisões dos recrutadores."), ("p", "A publicação de uma Chamada não configura processo seletivo vinculante, concurso público ou compromisso de contratação. O uso do ius indicandum é de responsabilidade exclusiva do recrutador, que deve observar as normas de impessoalidade e vedação ao nepotismo aplicáveis ao seu órgão."), ("p", "Ao se inscrever em uma Chamada, o candidato autoriza expressamente o compartilhamento de seu perfil e dados profissionais com o recrutador responsável pela vaga.")]),
        ("4. Cadastro de Candidatos", [("l", ["Ser bacharel em Direito ou possuir formação jurídica equivalente", "Fornecer informações verdadeiras, precisas e atualizadas", "Consentir com o tratamento de seus dados conforme a Política de Privacidade"])]),
        ("5. Cadastro de Recrutadores", [("l", ["Ser membro ativo de órgão do sistema de justiça", "Possuir e-mail institucional válido", "Ter a conta aprovada pelo JurisBank após verificação"]), ("p", "O recrutador se compromete a utilizar os dados dos candidatos exclusivamente para fins de seleção profissional.")]),
        ("6. Impessoalidade e Vedação ao Nepotismo", [("l", ["Princípio da impessoalidade (art. 37, caput, CF/88)", "Vedação ao nepotismo (Súmula Vinculante nº 13 do STF)", "Resolução CNJ nº 07/2005 e normas equivalentes do CNMP"]), ("p", "O recrutador é o único responsável pelo cumprimento dessas normas no âmbito de seu órgão.")]),
        ("7. Obrigações dos Usuários", [("l", ["Fornecer informações verdadeiras e atualizadas", "Não utilizar a plataforma para fins ilegais", "Não acessar áreas restritas sem autorização", "Não reproduzir ou comercializar conteúdo da plataforma sem autorização"])]),
        ("8. Responsabilidades", [("p", "O JurisBank não garante a contratação de candidatos cadastrados, não valida independentemente documentos enviados, e não se responsabiliza por decisões de seleção tomadas pelos recrutadores.")]),
        ("9. Foro", [("p", "Estes Termos são regidos pela legislação brasileira. Fica eleito o foro da Comarca de [MUNICÍPIO A PREENCHER], Estado de [ESTADO A PREENCHER].")]),
        ("10. Contato", [("l", ["E-mail: [E-MAIL DE CONTATO A PREENCHER]", "Endereço: [ENDEREÇO A PREENCHER]"])]),
    ]
    for titulo_sec, conteudo in secoes_tu:
        st.markdown(f'<div class="doc-sub">{titulo_sec}</div>', unsafe_allow_html=True)
        for tipo, texto in conteudo:
            if tipo == "p": st.markdown(f'<p class="doc-body">{texto}</p>', unsafe_allow_html=True)
            elif tipo == "h": st.markdown(f'<p style="font-weight:700;color:#1a3a8f;font-size:14px;margin:1rem 0 0.3rem">{texto}</p>', unsafe_allow_html=True)
            elif tipo == "l":
                for item in texto: st.markdown(f'<p class="doc-item">• {item}</p>', unsafe_allow_html=True)
        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    st.markdown(f'<p style="font-size:12px;color:#8090b8;text-align:center">JurisBank — Termos de Uso — Versão 1.0 — {datetime.now().strftime("%d/%m/%Y")}</p>', unsafe_allow_html=True)