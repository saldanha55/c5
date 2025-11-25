import streamlit as st
import random
import time
import os
import google.generativeai as genai

# --- 1. CONFIGURAÇÃO INICIAL ---
st.set_page_config(page_title="TROPA DO C5", page_icon="🌶️", layout="wide")

# --- 2. DESIGN SYSTEM (CSS FINAL - TELA INICIAL PIKA) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;800&family=Playfair+Display:ital,wght@0,700;1,400&display=swap');

    /* GERAL */
    html, body, [class*="css"], div, input, textarea { font-family: 'Montserrat', sans-serif !important; }
    
    .stApp {
        background-color: #050505;
        background-image: radial-gradient(#111 1px, transparent 1px);
        background-size: 20px 20px;
        color: #e0e0e0;
    }

    /* TÍTULOS */
    h1 { 
        font-family: 'Playfair Display', serif !important; 
        font-size: 4rem !important; 
        text-align: center; 
        color: #fff; 
        margin-bottom: 0; 
        text-shadow: 0 0 20px rgba(255,255,255,0.2); /* Brilho no título */
    }
    h2 { 
        font-family: 'Playfair Display', serif !important; 
        font-size: 1.8rem !important; 
        font-style: italic; 
        text-align: center; 
        color: #32A041; 
        margin-top: -10px;
        margin-bottom: 40px;
    }

    /* --- O CARD DA SINOPSE (ESTILO VERDE/DARK) --- */
    .intro-card {
        background-color: #0e110f; /* Fundo levemente esverdeado/escuro */
        border: 2px solid #32A041; /* Borda Verde Neon */
        border-radius: 15px;
        padding: 30px;
        text-align: center;
        font-size: 1.1rem;
        line-height: 1.8;
        color: #ccc;
        box-shadow: 0 0 30px rgba(50, 160, 65, 0.15); /* Glow verde em volta */
        margin: 0 auto 30px auto;
        max-width: 700px;
    }
    .highlight { color: #fff; font-weight: 700; }

    /* --- BOTÃO SÓLIDO (PREENCHIDO) --- */
    div.stButton > button {
        width: 100%;
        background-color: #32A041 !important; /* Verde Sólido */
        color: #ffffff !important; /* Texto Branco */
        border: none !important;
        border-radius: 8px;
        padding: 18px 24px;
        font-size: 18px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 2px;
        transition: all 0.3s ease;
        box-shadow: 0 5px 15px rgba(0,0,0,0.5);
    }
    
    div.stButton > button:hover {
        background-color: #267d32 !important; /* Verde mais escuro no hover */
        transform: translateY(-3px) scale(1.01);
        box-shadow: 0 10px 25px rgba(50, 160, 65, 0.4); /* Brilho intenso */
    }

    /* --- RESTO DO CHAT (MANTIDO IGUAL) --- */
    /* Input */
    [data-testid="stBottom"] { background-color: #050505 !important; border-top: 1px solid #222; padding-top: 1rem; padding-bottom: 1rem; }
    div[data-testid="stTextInput"] input { background-color: #000 !important; color: #fff !important; border: 1px solid #333 !important; border-radius: 8px !important; padding: 15px !important; }
    div[data-testid="stTextInput"] input:focus { border: 1px solid #32A041 !important; box-shadow: 0 0 10px rgba(50, 160, 65, 0.2) !important; }
    div[data-testid="stTextInput"] label { display: none; }
    
    /* Botão Enviar Pequeno */
    div[data-testid="stFormSubmitButton"] button { height: 52px; margin-top: 0px; background-color: #1f1f1f !important; border: 1px solid #333 !important; color: #32A041 !important; }
    div[data-testid="stFormSubmitButton"] button:hover { background-color: #32A041 !important; color: #fff !important; }

    /* Chat Layout */
    .char-name-title { font-family: 'Playfair Display', serif; font-size: 2.5rem; font-weight: 700; margin: 0; line-height: 1; text-align: center; }
    .char-subtitle { font-size: 0.85rem; color: #888; font-style: italic; margin-top: 5px; text-align: center; }
    .status-text { text-align: center; font-weight: 600; font-size: 0.9rem; margin-top: 10px; letter-spacing: 1px; }
    .chat-scroll-area { height: 55vh; min-height: 400px; overflow-y: auto; background-color: #0e0e0e; border: 1px solid #222; border-radius: 12px; padding: 20px; margin-bottom: 15px; box-shadow: inset 0 0 20px rgba(0,0,0,0.8); display: flex; flex-direction: column; }
    .user-msg { background-color: #1f1f1f; color: #fff; padding: 12px 18px; border-radius: 18px 18px 2px 18px; align-self: flex-end; text-align: right; margin: 5px 0; border: 1px solid #333; float: right; clear: both; max-width: 85%; }
    .bot-msg { background-color: #e6e6e6; color: #111; padding: 12px 18px; border-radius: 18px 18px 18px 2px; align-self: flex-start; text-align: left; margin: 5px 0; float: left; clear: both; max-width: 85%; font-weight: 600; }
    .profile-img { width: 100%; border-radius: 12px; border: 2px solid #333; box-shadow: 0 5px 20px rgba(0,0,0,0.6); margin-bottom: 15px; }

    /* Mobile */
    @media only screen and (max-width: 768px) {
        .profile-img { max-width: 150px; margin: 0 auto 10px auto; display: block; }
        .chat-scroll-area { height: 50vh; }
        h1 { font-size: 2.5rem !important; }
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
        # 1. Lista todos os modelos disponíveis na sua conta
        modelos_disponiveis = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                modelos_disponiveis.append(m.name)
        
        # 2. Lógica de prioridade: Tenta Flash -> Tenta Pro -> Pega o primeiro que tiver
        modelo_escolhido = None
        
        # Tenta achar qualquer versão 'flash' (1.5-flash, 1.5-flash-latest, etc)
        for m in modelos_disponiveis:
            if 'flash' in m:
                modelo_escolhido = m
                break
        
        # Se não achou flash, tenta 'pro'
        if not modelo_escolhido:
            for m in modelos_disponiveis:
                if 'pro' in m:
                    modelo_escolhido = m
                    break
        
        # Se não achou nenhum específico, pega o primeiro da lista (garantia)
        if not modelo_escolhido and modelos_disponiveis:
            modelo_escolhido = modelos_disponiveis[0]

        if modelo_escolhido:
            # print(f"Modelo conectado: {modelo_escolhido}") # Debug (opcional)
            return genai.GenerativeModel(modelo_escolhido)
        else:
            return None

    except Exception as e:
        st.error(f"Erro ao listar modelos: {e}")
        return None

model = setup_ai()

# --- 4. DADOS (ATENÇÃO: CERTIFIQUE-SE QUE A EXTENSÃO DAS IMAGENS ESTÁ CERTA) ---
# Se suas imagens no github forem .jpg, mude aqui para .jpg!
PERSONAGENS = {
    "PITOCO": { "img": "imagens/pitoco.jpeg", "cor": "#00d2d3", "subtitulo": "(Pedro Henrique / Bituca)" },
    "SAMUEL": { "img": "imagens/samuel.jpeg", "cor": "#eccc68", "subtitulo": "(Banco Central / Miles)" },
    "BRYAN": { "img": "imagens/bryan.jpeg", "cor": "#54a0ff", "subtitulo": "(Senhor Marra / Brás)" },
    "SALDANHA": { "img": "imagens/saldanha.jpeg", "cor": "#ff6b6b", "subtitulo": "(O Veterano)" },
    "MITSUKI": { "img": "imagens/mitsuki.jpeg", "cor": "#ff9ff3", "subtitulo": "(Mete-e-Chupa)" },
    "MOISÉS": { "img": "imagens/moises.jpeg", "cor": "#9c88ff", "subtitulo": "(O Quieto)" },
    "CAMARADA": { "img": "imagens/camarada.jpeg", "cor": "#ff9f43", "subtitulo": "(Miguel Arcanjo)" },
    "TIFAEL": { "img": "imagens/tifael.jpeg", "cor": "#8395a7", "subtitulo": "(Jack / Tio Fael)" },
    "JOAQUIM": { "img": "imagens/joaquim.jpeg", "cor": "#1dd1a1", "subtitulo": "(Quim)" },
    "INDIÃO": { "img": "imagens/indiao.jpeg", "cor": "#576574", "subtitulo": "(Doisberto)" }
}

# --- 5. LÓGICA ---
def get_system_prompt(personagem, fase, nivel_estresse):
    caso_atual = st.session_state.get('caso_atual', {"texto": "", "culpado": ""})
    contexto = f"OCORRIDO: '{caso_atual['texto']}'. Culpado: {caso_atual['culpado']}." if fase == "REVELACAO" else "FASE SOCIAL: Gabiru novo."
    
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
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h1>TROPA DO C5</h1>", unsafe_allow_html=True)
    st.markdown("<h2>QUEM É O ARROMBADO?</h2>", unsafe_allow_html=True)
    
    # O Card Verde (Estilo Pika)
    st.markdown("""
    <div class="intro-card">
        Bem-vindo ao Alojamento do IF. Você é o <span class="highlight">gabiru novo</span> no pedaço.<br><br>
        Venha conhecer os moradores, entender a dinâmica caótica do quarto e, acima de tudo...<br>
        <span class="highlight" style="font-size: 1.2rem; color: #fff; text-decoration: underline decoration-color: #32A041;">descobrir quem fez a merda da vez.</span>
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.button("ENTRAR NO QUARTO"):
            st.session_state.fase = 'SELECAO_INICIAL'
            st.rerun()

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

# TELA CHAT (LAYOUT CORRIGIDO: NOME NA ESQUERDA)
elif st.session_state.fase in ['SOCIAL', 'REVELACAO']:
    nome = st.session_state.personagem_atual
    dados = PERSONAGENS[nome]
    
    status_txt = "🟢 Online"
    cor_status = "#32A041"
    if st.session_state.msg_no_turno > 3: 
        status_txt = "⚠️ Estressado"
        cor_status = "#ff4757"
    if len(st.session_state.chat_history) > 0 and st.session_state.chat_history[-1]['role'] == 'user':
        status_txt = "✍️ Digitando..."
        cor_status = "#eccc68"

    # Layout: Esquerda (Perfil) | Direita (Chat)
    col_img, col_chat = st.columns([1, 3], gap="medium")
    
    # --- COLUNA DA ESQUERDA: PERFIL COMPLETO ---
    with col_img:
        # Nome e Subtitulo AGORA EM CIMA DA FOTO
        st.markdown(f"""
            <div style="text-align: center; margin-bottom: 10px;">
                <div style='font-family: "Playfair Display"; font-size: 2.5rem; font-weight: 700; color: {dados['cor']}; line-height: 1;'>{nome}</div>
                <div style='font-size: 0.85rem; color: #888; font-style: italic;'>{dados['subtitulo']}</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Imagem
        try:
            st.image(dados['img'], use_container_width=True)
        except:
            st.error("Erro Img")
            
        # Status embaixo da foto
        st.markdown(f"<div style='text-align:center; color:{cor_status}; font-weight:bold; margin-top:5px; letter-spacing:1px;'>{status_txt}</div>", unsafe_allow_html=True)

    # --- COLUNA DA DIREITA: APENAS CHAT ---
    with col_chat:
        chat_html = "<div class='chat-scroll-area'>"
        for msg in st.session_state.chat_history:
            if msg['role'] == 'user':
                chat_html += f"<div class='user-msg'>{msg['content']}</div>"
            else:
                chat_html += f"<div class='bot-msg' style='border-left: 5px solid {dados['cor']};'>{msg['content']}</div>"
        chat_html += "</div>"
        st.markdown(chat_html, unsafe_allow_html=True)

        # Formulário
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
                
                # --- CORREÇÃO DO ERRO 'NONE' ---
                if model:
                    try:
                        chat = model.start_chat(history=[])
                        resp = chat.send_message(f"SYSTEM: {prompt}\nUSER: {user_input}").text
                    except Exception as e:
                        resp = f"❌ Erro IA: {e}"
                else:
                    resp = "❌ Erro: IA não conectada. Verifique a chave API."
                
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
    
    # Botão de Acusar
    if st.button("ACUSAR", type="primary"):
        st.session_state.game_over = True
        st.session_state.palpite_final = escolha
    
    # Se o jogo acabou, mostra o resultado e o botão de reiniciar
    if st.session_state.get('game_over'):
        culpado_real = st.session_state.caso_atual['culpado']
        palpite = st.session_state.palpite_final
        
        if palpite == culpado_real:
            st.balloons()
            st.success(f"ACERTOU! O C5 está salvo. Foi o {culpado_real}!")
        else:
            st.error(f"ERROU! Quem fez foi o {culpado_real}!")
            
        st.write("\n")
        
        # Botão de Reiniciar (Agora fora do aninhamento)
        if st.button("🔄 JOGAR DE NOVO"):
            st.session_state.clear() # Limpa tudo
            st.rerun() # Recarrega a página do zero


