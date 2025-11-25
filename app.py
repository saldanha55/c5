import streamlit as st
import random
import time
import os
import google.generativeai as genai

# --- 1. CONFIGURAÇÃO INICIAL ---
st.set_page_config(page_title="TROPA DO C5", page_icon="🌶️", layout="wide")

# --- 2. CONEXÃO COM IA (ROBUSTA) ---
# Tenta pegar dos secrets (Nuvem) ou usa a variável local (PC)
api_key = st.secrets["GOOGLE_API_KEY"] if "GOOGLE_API_KEY" in st.secrets else os.environ.get("GOOGLE_API_KEY")

# Se não tiver chave nenhuma, avisa o usuário
if not api_key:
    st.error("🚨 ERRO: API Key não encontrada. Adicione nos 'Secrets' do Streamlit.")
    st.stop()

genai.configure(api_key=api_key)

@st.cache_resource
def setup_ai():
    try:
        # Tenta achar o modelo Flash (mais rápido), senão pega o padrão
        modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        escolhido = next((m for m in modelos if 'flash' in m), modelos[0] if modelos else None)
        return genai.GenerativeModel(escolhido) if escolhido else None
    except:
        return None

model = setup_ai()

# --- 3. DESIGN SYSTEM (CSS CORRIGIDO) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600&family=Playfair+Display:ital,wght@0,700;1,400&display=swap');

    /* GERAL */
    html, body, [class*="css"], div, input, textarea { font-family: 'Montserrat', sans-serif !important; }
    
    .stApp {
        background-color: #050505;
        background-image: radial-gradient(#1a1a1a 1px, transparent 1px);
        background-size: 20px 20px;
        color: #e0e0e0;
    }

    /* TIPOGRAFIA */
    h1, .serif-h1 { font-family: 'Playfair Display', serif !important; font-size: 3rem !important; font-weight: 700 !important; text-align: center; color: #fff; margin: 0; }
    h2, .serif-h2 { font-family: 'Playfair Display', serif !important; font-size: 1.5rem !important; font-style: italic; text-align: center; color: #32A041; margin-top: 0; }

    /* NOME DO PERSONAGEM (Estilo Título) */
    .char-name-display {
        font-family: 'Playfair Display', serif !important;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 10px;
        text-align: right;
        /* A cor será definida dinamicamente no Python */
    }

    /* BALÕES DE CHAT */
    .chat-scroll-area {
        height: 500px;
        overflow-y: auto;
        padding-right: 10px;
        display: flex;
        flex-direction: column;
    }
    
    .user-msg { 
        background-color: #1e1e1e; 
        color: #eee; 
        padding: 12px 18px; 
        border-radius: 18px 18px 2px 18px; 
        align-self: flex-end; 
        text-align: right; 
        margin: 5px 0; 
        border: 1px solid #333; 
        float: right;
        clear: both;
        max-width: 80%;
    }
    
    .bot-msg { 
        background-color: #f0f0f0; 
        color: #111; 
        padding: 12px 18px; 
        border-radius: 18px 18px 18px 2px; 
        align-self: flex-start; 
        text-align: left; 
        margin: 5px 0; 
        float: left;
        clear: both;
        max-width: 80%;
        font-weight: 500;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        /* A borda colorida será inserida inline no Python */
    }

    /* INPUT 100% PRETO */
    .stChatInput textarea {
        background-color: #000 !important;
        color: #fff !important;
        border: 1px solid #333 !important;
        border-radius: 12px !important;
    }
    .stChatInput textarea:focus {
        border: 1px solid #32A041 !important;
        box-shadow: 0 0 10px rgba(50, 160, 65, 0.2) !important;
    }
    [data-testid="stBottom"] {
        background-color: #050505 !important;
        border-top: 1px solid #222;
    }

    /* IMAGEM */
    .profile-img {
        width: 100%;
        border-radius: 15px;
        border: 2px solid #333;
        box-shadow: 0 5px 15px rgba(0,0,0,0.5);
        margin-bottom: 10px;
    }

    /* MOBILE RESPONSIVE */
    @media only screen and (max-width: 768px) {
        .profile-img { max-width: 200px; margin: 0 auto 15px auto; display: block; }
        .char-name-display { text-align: center; font-size: 2rem; }
        .chat-scroll-area { height: 400px; }
        h1 { font-size: 2.2rem !important; }
    }

    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 4. DADOS (CORRIGIDO: CHAVES FECHADAS) ---
PERSONAGENS = {
    "PITOCO": {"img": "imagens/pitoco.jpeg", "cor": "#00d2d3", "desc_oculta": "Agroboy Fake"},
    "SAMUEL": {"img": "imagens/samuel.jpeg", "cor": "#eccc68", "desc_oculta": "Rico Marrento"},
    "BRYAN": {"img": "imagens/bryan.jpeg", "cor": "#54a0ff", "desc_oculta": "Gamer Chorão"},
    "SALDANHA": {"img": "imagens/saldanha.jpeg", "cor": "#ff6b6b", "desc_oculta": "Veterano"},
    "MITSUKI": {"img": "imagens/mitsuki.jpeg", "cor": "#ff9ff3", "desc_oculta": "Otaku Sus"},
    "MOISÉS": {"img": "imagens/moises.jpeg", "cor": "#9c88ff", "desc_oculta": "Explosivo"},
    "CAMARADA": {"img": "imagens/camarada.jpeg", "cor": "#ff9f43", "desc_oculta": "Brainrot"},
    "TIFAEL": {"img": "imagens/tifael.jpeg", "cor": "#8395a7", "desc_oculta": "Tiozão"},
    "JOAQUIM": {"img": "imagens/joaquim.jpeg", "cor": "#1dd1a1", "desc_oculta": "Político"},
    "INDIÃO": {"img": "imagens/indiao.jpeg", "cor": "#576574", "desc_oculta": "Sombra"}
} # <--- AQUI ESTAVA O ERRO: Faltava essa chave de fechamento!

# --- 5. LÓGICA ---
def get_system_prompt(personagem, fase, nivel_estresse):
    # Recortado conforme seu pedido (Você cola seu prompt gigante aqui depois)
    return f"Você é {personagem}. Aja exatamente como sua personalidade manda. Responda curto."

def gerar_caso():
    casos = [
        "Alguém deixou uma calcinha usada no filtro.",
        "Sumiram 50 reais do Saldanha.",
        "Desenharam na porta do Moisés.",
        "Entupiram o vaso.",
        "Trouxeram uma galinha pro quarto."
    ]
    texto = random.choice(casos)
    culpado = random.choice(list(PERSONAGENS.keys()))
    fila = list(PERSONAGENS.keys())
    random.shuffle(fila)
    return {"texto": texto, "culpado": culpado, "fila": fila, "indice_fila": 0}

def avancar_personagem():
    st.session_state.chat_history = []
    st.session_state.msg_no_turno = 0
    st.session_state.contador_conversas += 1
    
    if st.session_state.fase == 'SOCIAL' and st.session_state.contador_conversas >= 4:
        st.session_state.fase = 'ALERTA_EVENTO'
        st.rerun()
    if st.session_state.fase == 'REVELACAO':
        st.session_state.fase = 'VEREDITO'
        st.rerun()

    prox_index = st.session_state.caso_atual['indice_fila'] + 1
    if prox_index < len(PERSONAGENS):
        st.session_state.caso_atual['indice_fila'] = prox_index
        st.session_state.personagem_atual = st.session_state.caso_atual['fila'][prox_index]
        st.rerun()
    else:
         st.session_state.fase = 'VEREDITO'
         st.rerun()

# --- 6. ESTADOS ---
if 'fase' not in st.session_state: st.session_state.fase = 'START'
if 'caso_atual' not in st.session_state: st.session_state.caso_atual = gerar_caso()
if 'chat_history' not in st.session_state: st.session_state.chat_history = []
if 'personagem_atual' not in st.session_state: st.session_state.personagem_atual = None
if 'contador_conversas' not in st.session_state: st.session_state.contador_conversas = 0
if 'msg_no_turno' not in st.session_state: st.session_state.msg_no_turno = 0

# --- 7. INTERFACE ---

# TELA START
if st.session_state.fase == 'START':
    st.markdown("<h1 class='serif-h1'>TROPA DO C5</h1>", unsafe_allow_html=True)
    st.markdown("<h2 class='serif-h2'>QUEM É O ARROMBADO?</h2>", unsafe_allow_html=True)
    st.write("\n\n")
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        if st.button("ENTRAR NO QUARTO", use_container_width=True):
            st.session_state.fase = 'SELECAO_INICIAL'
            st.rerun()

# TELA SELEÇÃO
elif st.session_state.fase == 'SELECAO_INICIAL':
    st.markdown("<h2 class='serif-h2'>QUEM VOCÊ VAI CUMPRIMENTAR?</h2>", unsafe_allow_html=True)
    cols = st.columns(5)
    for i, (nome, dados) in enumerate(PERSONAGENS.items()):
        with cols[i % 5]:
            st.image(dados['img'], use_container_width=True)
            if st.button(f"{nome}", key=f"btn_{nome}"):
                st.session_state.personagem_atual = nome
                if nome in st.session_state.caso_atual['fila']:
                    st.session_state.caso_atual['fila'].remove(nome)
                st.session_state.caso_atual['fila'].insert(0, nome)
                st.session_state.fase = 'SOCIAL'
                st.rerun()

# TELA CHAT (DESIGN FINAL)
elif st.session_state.fase in ['SOCIAL', 'REVELACAO']:
    nome = st.session_state.personagem_atual
    dados = PERSONAGENS[nome]
    
    # Lógica do Status
    status_txt = "Online"
    if st.session_state.msg_no_turno > 3: 
        status_txt = "⚠️ Estressado"
    if len(st.session_state.chat_history) > 0 and st.session_state.chat_history[-1]['role'] == 'user':
        status_txt = "✍️ Digitando..."

    # Layout: 1/3 Imagem, 2/3 Chat
    col_img, col_chat = st.columns([1, 2.5])
    
    with col_img:
        # Montando HTML da imagem de forma segura
        img_html = f'<img src="{dados["img"]}" class="profile-img">'
        status_html = f'<div style="text-align:center; color:#aaa; font-weight:600;">{status_txt}</div>'
        st.markdown(img_html + status_html, unsafe_allow_html=True)
        
    with col_chat:
        # Nome com a cor do personagem
        st.markdown(f"<div class='char-name-display' style='color: {dados['cor']};'>{nome}</div>", unsafe_allow_html=True)
        
        # Montando o Chat Container linha a linha para não quebrar o código
        chat_html = "<div class='chat-scroll-area'>"
        
        for msg in st.session_state.chat_history:
            if msg['role'] == 'user':
                chat_html += f"<div class='user-msg'>{msg['content']}</div>"
            else:
                # Borda esquerda colorida igual ao personagem
                chat_html += f"<div class='bot-msg' style='border-left: 5px solid {dados['cor']};'>{msg['content']}</div>"
        
        chat_html += "</div>"
        
        # Renderiza o chat
        st.markdown(chat_html, unsafe_allow_html=True)

    # Input Fixo
    user_input = st.chat_input("Mande o papo...")

    if user_input:
        if user_input.lower() in ['tchau', 'flw', 'vlw', 'vaza', 'sair', 'proximo', 'fui']:
            avancar_personagem()
        else:
            st.session_state.chat_history.append({'role': 'user', 'content': user_input})
            st.session_state.msg_no_turno += 1
            time.sleep(0.3)
            
            prompt = get_system_prompt(nome, st.session_state.fase, st.session_state.msg_no_turno)
            try:
                chat = model.start_chat(history=[])
                resp = chat.send_message(f"SYSTEM: {prompt}\nUSER: {user_input}").text
            except Exception as e:
                resp = f"Erro na IA: {e}"
            
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
                st.session_state.personagem_atual = nome
                st.session_state.chat_history = []
                st.session_state.fase = 'REVELACAO'
                st.rerun()

# TELA VEREDITO
elif st.session_state.fase == 'VEREDITO':
    st.markdown("<h1 class='serif-h1'>QUEM FOI?</h1>", unsafe_allow_html=True)
    st.markdown(f"**OCORRIDO:** {st.session_state.caso_atual['texto']}")
    escolha = st.selectbox("Selecione o Culpado:", list(PERSONAGENS.keys()))
    if st.button("ACUSAR", type="primary"):
        if escolha == st.session_state.caso_atual['culpado']:
            st.balloons()
            st.success("ACERTOU! O C5 está salvo.")
        else:
            st.error(f"ERROU! Foi o {st.session_state.caso_atual['culpado']}!")
        if st.button("JOGAR DE NOVO"):
            st.session_state.clear()
            st.rerun()
