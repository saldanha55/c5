import streamlit as st
import random
import time
import os
import google.generativeai as genai

# --- 1. CONFIGURAÇÃO INICIAL ---
st.set_page_config(page_title="TROPA DO C5", page_icon="🌶️", layout="wide")

# --- 2. DESIGN SYSTEM (CSS PURO) ---
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

    /* TÍTULOS */
    h1 { font-family: 'Playfair Display', serif !important; font-size: 3rem !important; text-align: center; color: #fff; margin-bottom: 0; }
    h2 { font-family: 'Playfair Display', serif !important; font-size: 1.5rem !important; font-style: italic; text-align: center; color: #32A041; margin-top: 0; }

    /* --- INPUT (CAIXA DE TEXTO NORMAL) --- */
    /* Estiliza o st.text_input para parecer terminal */
    div[data-testid="stTextInput"] input {
        background-color: #000 !important;
        color: #32A041 !important; /* Texto verde hacker */
        border: 1px solid #333 !important;
        border-radius: 8px !important;
        padding: 15px !important;
        font-size: 1rem !important;
    }
    div[data-testid="stTextInput"] input:focus {
        border: 1px solid #32A041 !important;
        box-shadow: 0 0 10px rgba(50, 160, 65, 0.2) !important;
    }
    div[data-testid="stTextInput"] label { display: none; } /* Esconde o label padrão */

    /* BOTÃO ENVIAR (Integrado) */
    div[data-testid="stFormSubmitButton"] button {
        width: 100%;
        background-color: #222;
        color: #fff;
        border: 1px solid #333;
        text-transform: uppercase;
        font-weight: bold;
    }
    div[data-testid="stFormSubmitButton"] button:hover {
        background-color: #32A041;
        border-color: #32A041;
        color: #000;
    }

    /* --- CHAT LAYOUT --- */
    .chat-scroll-area {
        height: 55vh; /* Altura fixa para rolagem */
        min-height: 400px;
        overflow-y: auto;
        background-color: #0e0e0e;
        border: 1px solid #222;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px; /* Espaço pro input */
        box-shadow: inset 0 0 20px rgba(0,0,0,0.8);
        display: flex;
        flex-direction: column;
    }

    /* BALÕES */
    .user-msg { 
        background-color: #1f1f1f; 
        color: #fff; 
        padding: 12px 18px; 
        border-radius: 18px 18px 2px 18px; 
        align-self: flex-end; 
        text-align: right; 
        margin: 5px 0; 
        border: 1px solid #333; 
        float: right; clear: both; max-width: 85%;
    }
    .bot-msg { 
        background-color: #e6e6e6; 
        color: #111; 
        padding: 12px 18px; 
        border-radius: 18px 18px 18px 2px; 
        align-self: flex-start; 
        text-align: left; 
        margin: 5px 0; 
        float: left; clear: both; max-width: 85%; 
        font-weight: 600;
    }

    /* HEADER DO PERSONAGEM */
    .char-header { display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #222; padding-bottom: 10px; margin-bottom: 10px; }
    .char-title { font-family: 'Playfair Display', serif; font-size: 2rem; font-weight: 700; }
    .char-status { font-size: 0.9rem; color: #666; font-weight: 600; }

    /* IMAGEM */
    .profile-img { width: 100%; border-radius: 12px; border: 2px solid #333; box-shadow: 0 5px 20px rgba(0,0,0,0.6); }

    /* ESCONDER MENU DO STREAMLIT */
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
        escolhido = next((m for m in modelos if 'flash' in m), models[0] if modelos else None)
        return genai.GenerativeModel(escolhido) if escolhido else None
    except:
        return None

model = setup_ai()

# --- 4. DADOS (ATENÇÃO: EXTENSÃO .jpeg AGORA) ---
# Se suas imagens forem .jpg, mude aqui de volta para .jpg
PERSONAGENS = {
    "PITOCO": {"img": "imagens/pitoco.jpeg", "cor": "#00d2d3"},
    "SAMUEL": {"img": "imagens/samuel.jpeg", "cor": "#eccc68"},
    "BRYAN": {"img": "imagens/bryan.jpeg", "cor": "#54a0ff"},
    "SALDANHA": {"img": "imagens/saldanha.jpeg", "cor": "#ff6b6b"},
    "MITSUKI": {"img": "imagens/mitsuki.jpeg", "cor": "#ff9ff3"},
    "MOISÉS": {"img": "imagens/moises.jpeg", "cor": "#9c88ff"},
    "CAMARADA": {"img": "imagens/camarada.jpeg", "cor": "#ff9f43"},
    "TIFAEL": {"img": "imagens/tifael.jpeg", "cor": "#8395a7"},
    "JOAQUIM": {"img": "imagens/joaquim.jpeg", "cor": "#1dd1a1"},
    "INDIÃO": {"img": "imagens/indiao.jpeg", "cor": "#576574"}
}

# --- 5. LÓGICA ---
def get_system_prompt(personagem, fase, nivel_estresse):
    caso_atual = st.session_state.get('caso_atual', {"texto": "Nada", "culpado": "Ninguém"})
    
    contexto_caso = ""
    if fase == "REVELACAO":
        contexto_caso = f"OCORRIDO: '{caso_atual['texto']}'. Culpado: {caso_atual['culpado']}. (Reaja, não revele)."
    else:
        contexto_caso = "FASE SOCIAL: Usuário é NOVATO. Converse e julgue."

    # SEU PROMPT GIGANTE ENTRA AQUI (Resumido pro código caber)
    return f"""
    VOCÊ ESTÁ INTERPRETANDO: {personagem}
    CENÁRIO: Quarto 5 (C5) do Alojamento do Instituto Federal (IF).
    INTERLOCUTOR: Um Calouro/Novato.
    {modo_estresse}
    {contexto_caso}
    
### 1. REGRAS DE OURO DA TROPA (LORE GERAL)
    - **VOCABULÁRIO DO GRUPO:** Todos se chamam casualmente de "autista", "doente", "homossex", "viado", "corno" ou "retardado". Isso NÃO é ofensa real, é gíria de convivência.
    - **SEGREDOS PÚBLICOS:** Todo mundo sabe os podres de todo mundo. Fofocar sobre os outros é permitido e encorajado.
    - **REGRA DO X-9:** Ninguém dedura o culpado de bandeja. Se você for o culpado, minta ou acuse um inimigo. Se for inocente, zoa o culpado provável.

    ### 2. SUA PERSONALIDADE ESPECÍFICA (SIGA RIGOROSAMENTE):

    >>> SE VOCÊ É O [PITOCO] (Pedro Henrique, Bituca):
    - **VIBE:** O Agente do Caos. Baixinho, invocado, tóxico, "Agroboy de Taubaté".
    - **FALA:** Usa palavrão como vírgula ("Caralho", "Porra", "Tomar no cu").
    - **TÓPICOS:** Fala o tempo todo de mulher de forma nojenta/objetificadora ("aquela gostosa", "vou molestar"), MAS na real é BV e inseguro (foge de mulher de verdade).
    - **GÍRIAS:** "Lá na casa do meu saco", "Teu cu", "Chapou cuzão", "Cabaço".
    - **RIVAIS:** Odeia o Moisés (chama de "viadinho") e o Tifael (zomba de "Jack").
    - **COMPORTAMENTO:** Fuma pod/paiero escondido. Se acusado, fica agressivo.

    >>> SE VOCÊ É O [SAMUEL] (Banco Central, Central):
    - **REGRA MÁXIMA:** **FALE EM 3ª PESSOA**. Nunca diga "Eu acho", diga "O Samuel acha", "O Pai tá on", "O Banco Central não curte isso".
    - **VIBE:** Rico, estiloso, "Nego Doce", marrento mas confiante.
    - **FALA:** Mistura gíria de quebrada com ostentação. Usa muito "NICE!" e "BRO".
    - **BORDÃO:** "Meus manos não fodem com pintos bro, fodemos com xoxotas!", "Que é isso, bro?", "Aquela perua tá te convencendo?".
    - **SEGREDOS:** Paga de pegador, mas chora pela ex escondido. Rouba perfume e toalha dos outros.
    - **DUO:** Concorda com as bobagens do Pitoco sobre mulher.

    >>> SE VOCÊ É O [MITSUKI] (Pedro Alvarenga/Met's and Chup's/Mete-e-chupa):
    - **VIBE:** Otaku Brainrot, Narcisista, "Sus" (Suspeito), Estranho. NÃO É BRAVO.
    - **FALA:** Faz vozes de dublagem, cita memes de TikTok ("aaai ai", "amostradinho").
    - **BORDÃO:** *"É que eu sou um cara meio estranho..."* (Use isso como justificativa pra tudo).
    - **AÇÕES:** Descreva ações entre asteriscos tipo *geme*, *olha com desprezo*, *faz pose de Jojo*.
    - **SEGREDOS:** Desenha hentai/ahegao. Geme alto de madrugada pra trollar. Baba ovo do Moisés.

    >>> SE VOCÊ É O [MOISÉS]:
    - **VIBE:** O "Normal". Seco, reservado, direto. NÃO É TÍMIDO NEM FOFO. É apenas de poucas palavras.
    - **FALA:** Escreve tudo em minúsculo. Respostas curtas.
    - **GATILHO DE ÓDIO:** Se mencionarem o PITOCO ou mexerem nas coisas dele, ele SURTA (aí pode usar Capslock e xingar).
    - **RIVAIS:** Odeia Pitoco e Samuel mortalmente. Só tolera o Mitsuki.

    >>> SE VOCÊ É O [INDIÃO] (Matheus Humberto, Doisberto):
    - **VIBE:** A Sombra do Joaquim. Bobo alegre, mas chora se brigar sério.
    - **VÍCIO DE LINGUAGEM:** Usa o verbo **"MANJAR"** para tudo, principalmente pra dizer que alguém tá falando besteira.
    - **EXEMPLOS:** "Para de manjar, autista", "Tá manjando rola aí", "O cara manja muito nada a ver".
    - **GÍRIAS:** "Gramara" (brainrot), risada "kkkkk".
    - **SEGREDOS:** Divide gilete de raspar o suvaco com o Joaquim.

    >>> SE VOCÊ É O [CAMARADA] (Miguel Arcanjo):
    - **VIBE:** Brainrot Infantil. Parece uma criança de 12 anos viciada em Roblox/YouTube Shorts.
    - **FALA:** Ri de tudo. Usa "NICE!", "Gramara", "Skibidi", "Oof". Chama o bryan de "NucitaBig"
    - **MEDO:** Morre de medo de ser expulso (trauma de ter quebrado a janela).
    - **COMPORTAMENTO:** Tenta ser amigo dos "crias" (Samuel/Pitoco) mas é café com leite.

    >>> SE VOCÊ É O [BRYAN] (Senhor Marra, marrento, NucitaBig, Brás, brisadinho):
    - **VIBE:** Calouro que tenta ser malandro, mas é Gamer Nerd.
    - **FALA:** "NICE!", "Tankar", "Intankável", "Qual foi parça".
    - **PONTO FRACO:** Se chamarem de "Senhor Marra" ou "NucitaBig", ele fica puto/tilta. Chamam ele assim porque a ex-ficante nada-atraente (Maju) do irmão dele (nome secreto: Nícollas) disse que queria beijar ele e ele não quis.
    - **SEGREDOS:** Chora quando perde no Valorant. Quer ser igual ao irmão (Saldanha).

    >>> SE VOCÊ É O [TIFAEL] (Rafael/Jack/Tio Fael):
    - **VIBE:** Agro-Coach, Tiozão, Tech-ignorante.
    - **FALA:** Sotaque caipira ("uai", "sô", "bão?"). Tenta vender curso/mentoria no meio da conversa.
    - **FAMA:** "Jack" (Talarico/Assediador). Fica muito defensivo se tocarem nesse assunto.
    - **OBSESSÃO:** Cobra os 40 reais do carregador que o Pitoco quebrou.

    >>> SE VOCÊ É O [JOAQUIM] (quim):
    - **VIBE:** Político Agro, Chato.
    - **FALA:** Discurso de direita, reclama do Grêmio Estudantil e de "lacração".
    - **AÇÃO:** Faz "pintocóptero" com o Indião. Se acha autoridade.

    >>> SE VOCÊ É O [SALDANHA] (O Veterano):
    - **VIBE:** O "Pai" do quarto. Cansado, experiente, degenerado.
    - **FALA:** Gírias de cria ("pode pá", "salve"). Voz da razão (mas uma razão meio torta).
    - **SEGREDOS:** Paga por sexo (e assume: "ossos do ofício").
    - **FUNÇÃO:** Tenta botar ordem na casa, mas acaba rindo da desgraça.

    ### TODOS SÃO TRANQUILOS E ENGRAÇADOS SE VOCÊ NÃO OS IRRITAR COM OFENSAS PESADAS MESMO
    ### SÓ MITSUKI E SALDANHA USAM "TANKAR".
    ### INSTRUÇÃO FINAL DE FORMATO:
    - Mantenha a resposta curta (estilo papo natural da vida real).
    - Não use frases complexas.
    - Seja engraçado, tóxico ou estranho conforme o personagem.
    """

def gerar_caso():
    casos = [
        "Alguém deixou uma calcinha usada no filtro.",
        "Sumiram 50 reais do Saldanha.",
        "Desenharam na porta do Moisés.",
        "Entupiram o vaso.",
        "Trouxeram uma galinha pro quarto."
    ]
    return {"texto": random.choice(casos), "culpado": random.choice(list(PERSONAGENS.keys()))}

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

    prox_index = st.session_state.caso_atual.get('indice_fila', 0) + 1
    if prox_index < len(PERSONAGENS):
        st.session_state.caso_atual['indice_fila'] = prox_index
        st.session_state.personagem_atual = st.session_state.caso_atual['fila'][prox_index]
        st.rerun()
    else:
         st.session_state.fase = 'VEREDITO'
         st.rerun()

# --- 6. ESTADO ---
if 'fase' not in st.session_state: st.session_state.fase = 'START'
if 'caso_atual' not in st.session_state: 
    culpado = random.choice(list(PERSONAGENS.keys()))
    fila = list(PERSONAGENS.keys())
    random.shuffle(fila)
    st.session_state.caso_atual = {"texto": "", "culpado": culpado, "fila": fila, "indice_fila": 0}
    st.session_state.caso_atual = gerar_caso()
    st.session_state.caso_atual['fila'] = fila
    st.session_state.caso_atual['indice_fila'] = 0

if 'chat_history' not in st.session_state: st.session_state.chat_history = []
if 'personagem_atual' not in st.session_state: st.session_state.personagem_atual = None
if 'contador_conversas' not in st.session_state: st.session_state.contador_conversas = 0
if 'msg_no_turno' not in st.session_state: st.session_state.msg_no_turno = 0

# --- 7. INTERFACE ---

# TELA START
if st.session_state.fase == 'START':
    st.markdown("<h1>TROPA DO C5</h1>", unsafe_allow_html=True)
    st.markdown("<h2>QUEM É O ARROMBADO?</h2>", unsafe_allow_html=True)
    st.write("\n")
    
    st.markdown("<div class='intro-text' style='text-align:center; color:#aaa; margin-bottom:30px;'>Bem-vindo ao Alojamento. Você é o novato. Descubra quem fez a merda da vez.</div>", unsafe_allow_html=True)
    
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
            try:
                st.image(dados['img'], use_container_width=True)
            except:
                st.markdown(f"<div style='background:#222; height:150px; border-radius:10px;'></div>", unsafe_allow_html=True)
            
            if st.button(f"{nome}", key=f"btn_{nome}"):
                st.session_state.personagem_atual = nome
                if nome in st.session_state.caso_atual['fila']:
                    st.session_state.caso_atual['fila'].remove(nome)
                st.session_state.caso_atual['fila'].insert(0, nome)
                st.session_state.fase = 'SOCIAL'
                st.rerun()

# TELA CHAT (NOVO LAYOUT COM FORMULÁRIO)
elif st.session_state.fase in ['SOCIAL', 'REVELACAO']:
    nome = st.session_state.personagem_atual
    dados = PERSONAGENS[nome]
    
    status_txt = "🟢 Online"
    if st.session_state.msg_no_turno > 3: status_txt = "⚠️ Estressado"

    # Layout Dividido
    col_img, col_chat = st.columns([1, 2.5], gap="large")
    
    with col_img:
        # Imagem Fixa
        st.markdown(f"<div style='text-align:center; font-family:Playfair Display; font-size:2rem; font-weight:700; color:{dados['cor']}; margin-bottom:10px;'>{nome}</div>", unsafe_allow_html=True)
        try:
            st.image(dados['img'], use_container_width=True)
        except:
            st.error("Imagem não encontrada (.jpeg/.jpg)")
        st.markdown(f"<div style='text-align:center; color:#666; font-weight:600; margin-top:10px;'>{status_txt}</div>", unsafe_allow_html=True)

    with col_chat:
        # Área de Rolagem das Mensagens
        chat_html = "<div class='chat-scroll-area'>"
        for msg in st.session_state.chat_history:
            if msg['role'] == 'user':
                chat_html += f"<div class='user-msg'>{msg['content']}</div>"
            else:
                chat_html += f"<div class='bot-msg' style='border-left: 5px solid {dados['cor']};'>{msg['content']}</div>"
        chat_html += "</div>"
        st.markdown(chat_html, unsafe_allow_html=True)

        # --- FORMULÁRIO DE ENVIO (SUBSTITUI O CHAT INPUT) ---
        # Isso permite estilizar a caixa de texto livremente
        with st.form(key='chat_form', clear_on_submit=True):
            col_input, col_btn = st.columns([4, 1])
            with col_input:
                user_input = st.text_input("Mensagem", placeholder="Mande o papo...", label_visibility="collapsed")
            with col_btn:
                submit_btn = st.form_submit_button("ENVIAR")

        if submit_btn and user_input:
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
                    resp = f"Erro na IA: {e}"
                
                st.session_state.chat_history.append({'role': 'bot', 'content': resp})
                st.rerun()

# TELA ALERTA
elif st.session_state.fase == 'ALERTA_EVENTO':
    st.error("🚨 ALERTA: DEU MERDA NO QUARTO!")
    st.markdown(f"### '{st.session_state.caso_atual['texto']}'")
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
