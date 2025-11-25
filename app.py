import streamlit as st
import random
import time
import os
import google.generativeai as genai

# --- 1. CONFIGURAÇÃO INICIAL ---
st.set_page_config(page_title="TROPA DO C5", page_icon="🌶️", layout="wide")

# --- 2. DESIGN SYSTEM (CSS OTIMIZADO) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600&family=Playfair+Display:ital,wght@0,700;1,400&display=swap');

    /* GERAL */
    html, body, [class*="css"], div, input, textarea { font-family: 'Montserrat', sans-serif !important; }
    
    .stApp {
        background-color: #050505;
        background-image: radial-gradient(#111 1px, transparent 1px);
        background-size: 20px 20px;
        color: #e0e0e0;
    }

    /* --- CORREÇÃO: REMOVER ESPAÇO VAZIO NO TOPO --- */
    .block-container {
        padding-top: 1rem !important; /* Cola o conteúdo no topo */
        padding-bottom: 2rem !important;
    }

    /* TIPOGRAFIA */
    h1 { font-family: 'Playfair Display', serif !important; font-size: 3rem !important; text-align: center; color: #fff; margin-bottom: 0; }
    h2 { font-family: 'Playfair Display', serif !important; font-size: 1.5rem !important; font-style: italic; text-align: center; color: #32A041; margin-top: 0; }

    /* --- CUSTOM INPUT (SUBSTITUI O CHAT INPUT) --- */
    /* Remove bordas do form */
    [data-testid="stForm"] {
        border: none;
        padding: 0;
        margin-top: 10px;
    }

    /* Caixa de Texto */
    div[data-testid="stTextInput"] input {
        background-color: #000 !important;
        color: #fff !important;
        border: 1px solid #333 !important;
        border-radius: 8px !important;
        padding: 12px !important;
        font-size: 1rem !important;
    }
    div[data-testid="stTextInput"] input:focus {
        border: 1px solid #32A041 !important;
        box-shadow: 0 0 10px rgba(50, 160, 65, 0.2) !important;
    }
    /* Esconde label */
    div[data-testid="stTextInput"] label { display: none; }

    /* Botão Enviar */
    div[data-testid="stFormSubmitButton"] button {
        background-color: #1f1f1f;
        color: #32A041;
        border: 1px solid #333;
        border-radius: 8px;
        height: 48px; /* Altura igual ao input */
        margin-top: 0px; /* Alinhamento */
        width: 100%;
        text-transform: uppercase;
        font-weight: bold;
    }
    div[data-testid="stFormSubmitButton"] button:hover {
        background-color: #32A041;
        color: #000;
        border-color: #32A041;
    }

    /* --- AREA DO CHAT --- */
    .chat-scroll-area {
        height: 60vh; /* Altura fixa */
        min-height: 400px;
        overflow-y: auto;
        background-color: #0e0e0e;
        border: 1px solid #222;
        border-radius: 12px;
        padding: 20px;
        box-shadow: inset 0 0 20px rgba(0,0,0,0.8);
        display: flex;
        flex-direction: column;
    }

    /* Balões */
    .user-msg { background-color: #1f1f1f; color: #fff; padding: 12px 18px; border-radius: 18px 18px 2px 18px; align-self: flex-end; text-align: right; margin: 8px 0; border: 1px solid #333; float: right; clear: both; max-width: 85%; }
    .bot-msg { background-color: #f2f2f2; color: #111; padding: 12px 18px; border-radius: 18px 18px 18px 2px; align-self: flex-start; text-align: left; margin: 8px 0; float: left; clear: both; max-width: 85%; font-weight: 600; box-shadow: 0 2px 5px rgba(0,0,0,0.2); }

    /* HEADER CHAT */
    .char-name-title { font-family: 'Playfair Display', serif; font-size: 2.2rem; font-weight: 700; margin: 0; line-height: 1; }
    .char-subtitle { font-size: 0.85rem; color: #888; font-style: italic; margin-top: 5px; }
    .status-text { font-weight: 600; font-size: 0.9rem; letter-spacing: 1px; text-align: right; }

    /* IMAGEM */
    .profile-img { width: 100%; border-radius: 12px; border: 2px solid #333; box-shadow: 0 5px 20px rgba(0,0,0,0.6); }

    /* Botoes de Seleção */
    div.stButton > button { background: transparent; color: #32A041; border: 2px solid #32A041; border-radius: 6px; text-transform: uppercase; font-weight: 700; }
    div.stButton > button:hover { background: #32A041; color: #000; }

    /* Mobile */
    @media only screen and (max-width: 768px) {
        .profile-img { max-width: 150px; margin: 0 auto 10px auto; display: block; }
        .chat-header-wrapper { text-align: center; }
        .chat-scroll-area { height: 50vh; }
    }

    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 3. CONEXÃO COM A IA ---
api_key = st.secrets["GOOGLE_API_KEY"] if "GOOGLE_API_KEY" in st.secrets else os.environ.get("GOOGLE_API_KEY")

if not api_key:
    st.error("🚨 ERRO: API Key não encontrada.")
    st.stop()

genai.configure(api_key=api_key)

@st.cache_resource
def setup_ai():
    try:
        modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        escolhido = next((m for m in modelos if 'flash' in m), models[0] if models else None)
        return genai.GenerativeModel(escolhido) if escolhido else None
    except:
        return None

model = setup_ai()

# --- 4. DADOS (ATENÇÃO: CERTIFIQUE-SE QUE A EXTENSÃO DAS IMAGENS ESTÁ CERTA) ---
# Se suas imagens no github forem .jpg, mude aqui para .jpg!
PERSONAGENS = {
    "PITOCO": { "img": "imagens/pitoco.png", "cor": "#00d2d3", "subtitulo": "(Pedro Henrique / Bituca)" },
    "SAMUEL": { "img": "imagens/samuel.png", "cor": "#eccc68", "subtitulo": "(Banco Central / Miles)" },
    "BRYAN": { "img": "imagens/bryan.png", "cor": "#54a0ff", "subtitulo": "(Senhor Marra / Brás)" },
    "SALDANHA": { "img": "imagens/saldanha.png", "cor": "#ff6b6b", "subtitulo": "(O Veterano)" },
    "MITSUKI": { "img": "imagens/mitsuki.png", "cor": "#ff9ff3", "subtitulo": "(Mete-e-Chupa)" },
    "MOISÉS": { "img": "imagens/moises.png", "cor": "#9c88ff", "subtitulo": "(O Quieto)" },
    "CAMARADA": { "img": "imagens/camarada.png", "cor": "#ff9f43", "subtitulo": "(Miguel Arcanjo)" },
    "TIFAEL": { "img": "imagens/tifael.png", "cor": "#8395a7", "subtitulo": "(Jack / Tio Fael)" },
    "JOAQUIM": { "img": "imagens/joaquim.png", "cor": "#1dd1a1", "subtitulo": "(Quim)" },
    "INDIÃO": { "img": "imagens/indiao.png", "cor": "#576574", "subtitulo": "(Doisberto)" }
}

# --- 5. LÓGICA ---
def get_system_prompt(personagem, fase, nivel_estresse):
    caso_atual = st.session_state.get('caso_atual', {"texto": "", "culpado": ""})
    contexto = f"OCORRIDO: '{caso_atual['texto']}'. Culpado: {caso_atual['culpado']}." if fase == "REVELACAO" else "FASE SOCIAL: Calouro novo."
    
    return f"""
    PERSONAGEM: {personagem}. CENÁRIO: Alojamento C5.
    {contexto}
    PERSONALIDADES:
    - PITOCO: Tóxico, palavrão. - SAMUEL: 3ª Pessoa, 'Nice'. - MITSUKI: Estranho, 'Yamete'.
    - SALDANHA: Gíria de cria. - BRYAN: Gamer chorão. - INDIÃO: 'Manjar'.
    - CAMARADA: Brainrot. - TIFAEL: Caipira.
    RESPOSTA: Curta, informal, gírias.
    """

def gerar_caso():
    casos = ["Calcinha no filtro", "Sumiram 50 reais", "Desenho na porta", "Vaso entupido", "Galinha no quarto"]
    return {"texto": random.choice(casos), "culpado": random.choice(list(PERSONAGENS.keys()))}

def avancar_personagem():
    st.session_state.chat_history = []
    st.session_state.msg_no_turno = 0
    st.session_state.contador_conversas += 1
    if st.session_state.fase == 'SOCIAL' and st.session_state.contador_conversas >= 4: st.session_state.fase = 'ALERTA_EVENTO'; st.rerun()
    if st.session_state.fase == 'REVELACAO': st.session_state.fase = 'VEREDITO'; st.rerun()
    
    prox = st.session_state.caso_atual['indice_fila'] + 1
    if prox < len(PERSONAGENS):
        st.session_state.caso_atual['indice_fila'] = prox
        st.session_state.personagem_atual = st.session_state.caso_atual['fila'][prox]
        st.rerun()
    else:
        st.session_state.fase = 'VEREDITO'; st.rerun()

# --- 6. ESTADOS ---
if 'fase' not in st.session_state: st.session_state.fase = 'START'
if 'caso_atual' not in st.session_state: 
    culpado = random.choice(list(PERSONAGENS.keys()))
    fila = list(PERSONAGENS.keys()); random.shuffle(fila)
    st.session_state.caso_atual = {"texto": "", "culpado": culpado, "fila": fila, "indice_fila": 0}
    st.session_state.caso_atual = gerar_caso()
    st.session_state.caso_atual['fila'] = fila
    st.session_state.caso_atual['indice_fila'] = 0

if 'chat_history' not in st.session_state: st.session_state.chat_history = []
if 'msg_no_turno' not in st.session_state: st.session_state.msg_no_turno = 0
if 'contador_conversas' not in st.session_state: st.session_state.contador_conversas = 0

# --- 7. INTERFACE ---

# TELA START
if st.session_state.fase == 'START':
    st.markdown("<h1>TROPA DO C5</h1><h2>QUEM É O ARROMBADO?</h2>", unsafe_allow_html=True)
    st.write("\n")
    st.markdown("<div class='intro-text'>Bem-vindo ao Alojamento. Você é o novato. Descubra quem fez a merda da vez.</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.button("ENTRAR NO QUARTO"): st.session_state.fase = 'SELECAO_INICIAL'; st.rerun()

# TELA SELEÇÃO
elif st.session_state.fase == 'SELECAO_INICIAL':
    st.markdown("<h2>QUEM VOCÊ VAI CUMPRIMENTAR?</h2>", unsafe_allow_html=True)
    cols = st.columns(5)
    for i, (nome, dados) in enumerate(PERSONAGENS.items()):
        with cols[i % 5]:
            try: st.image(dados['img'], use_container_width=True)
            except: st.error(f"Erro Imagem")
            if st.button(f"{nome}", key=f"btn_{nome}"):
                st.session_state.personagem_atual = nome
                if nome in st.session_state.caso_atual['fila']: st.session_state.caso_atual['fila'].remove(nome)
                st.session_state.caso_atual['fila'].insert(0, nome)
                st.session_state.fase = 'SOCIAL'; st.rerun()

# TELA CHAT (LAYOUT NOVO SEM BARRA BRANCA)
elif st.session_state.fase in ['SOCIAL', 'REVELACAO']:
    nome = st.session_state.personagem_atual
    dados = PERSONAGENS[nome]
    
    status_txt = "🟢 Online"
    cor_status = "#32A041"
    if st.session_state.msg_no_turno > 3: status_txt = "⚠️ Estressado"; cor_status = "#ff4757"
    if len(st.session_state.chat_history) > 0 and st.session_state.chat_history[-1]['role'] == 'user': status_txt = "✍️ Digitando..."; cor_status = "#eccc68"

    col_img, col_chat = st.columns([1, 2.5], gap="large")
    
    with col_img:
        try: st.image(dados['img'], use_container_width=True)
        except: st.error("Erro IMG")
    
    with col_chat:
        # Header do Chat
        st.markdown(f"""
            <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #333; padding-bottom:10px; margin-bottom:10px;">
                <div>
                    <div class='char-name-title' style='color: {dados['cor']};'>{nome}</div>
                    <div class='char-subtitle'>{dados['subtitulo']}</div>
                </div>
                <div class='status-text' style='color: {cor_status};'>{status_txt}</div>
            </div>
        """, unsafe_allow_html=True)

        # Chat Scroll
        chat_html = "<div class='chat-scroll-area'>"
        for msg in st.session_state.chat_history:
            if msg['role'] == 'user':
                chat_html += f"<div class='user-msg'>{msg['content']}</div>"
            else:
                chat_html += f"<div class='bot-msg' style='border-left: 5px solid {dados['cor']};'>{msg['content']}</div>"
        chat_html += "</div>"
        st.markdown(chat_html, unsafe_allow_html=True)

        # Formulário de Envio (Input + Botão)
        with st.form(key='chat_form', clear_on_submit=True):
            c1, c2 = st.columns([5, 1])
            with c1:
                user_input = st.text_input("msg", placeholder="Mande o papo...", label_visibility="collapsed")
            with c2:
                submitted = st.form_submit_button("ENVIAR")

        if submitted and user_input:
            if user_input.lower() in ['tchau', 'flw', 'vlw', 'vaza', 'sair', 'proximo', 'fui']:
                avancar_personagem()
            else:
                st.session_state.chat_history.append({'role': 'user', 'content': user_input})
                st.session_state.msg_no_turno += 1
                
                prompt = get_system_prompt(nome, st.session_state.fase, st.session_state.msg_no_turno)
                try:
                    chat = model.start_chat(history=[])
                    resp = chat.send_message(f"SYSTEM: {prompt}\nUSER: {user_input}").text
                except Exception as e:
                    resp = f"Erro IA: {e}"
                st.session_state.chat_history.append({'role': 'bot', 'content': resp})
                st.rerun()

# TELA ALERTA
elif st.session_state.fase == 'ALERTA_EVENTO':
    st.error("🚨 ALERTA: DEU MERDA NO QUARTO!")
    st.markdown(f"### '{st.session_state.caso_atual['texto']}'")
    st.write("O clima pesou. Você pode pressionar MAIS UM antes de decidir.")
    cols = st.columns(5)
    for i, (nome, dados) in enumerate(PERSONAGENS.items()):
        with cols[i % 5]:
            if st.button(f"{nome}", key=f"last_{nome}"):
                st.session_state.personagem_atual = nome; st.session_state.chat_history = []; st.session_state.fase = 'REVELACAO'; st.rerun()

# TELA VEREDITO
elif st.session_state.fase == 'VEREDITO':
    st.markdown("<h1 class='serif-h1'>QUEM FOI?</h1>", unsafe_allow_html=True)
    st.markdown(f"**OCORRIDO:** {st.session_state.caso_atual['texto']}")
    escolha = st.selectbox("Selecione o Culpado:", list(PERSONAGENS.keys()))
    if st.button("ACUSAR", type="primary"):
        if escolha == st.session_state.caso_atual['culpado']:
            st.balloons(); st.success("ACERTOU! O C5 está salvo.")
        else:
            st.error(f"ERROU! Foi o {st.session_state.caso_atual['culpado']}!")
        if st.button("JOGAR DE NOVO"): st.session_state.clear(); st.rerun()
