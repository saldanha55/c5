import streamlit as st
import random
import time
import google.generativeai as genai

# --- 1. CONFIGURAÇÃO VISUAL E START ---
st.set_page_config(page_title="TROPA DO C5", page_icon="🌶️", layout="wide")

# --- DESIGN SYSTEM: PREMIUM EDITORIAL (DARK MODE) ---
st.markdown("""
<style>
    /* 1. IMPORTANDO FONTES */
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600&family=Playfair+Display:ital,wght@0,700;1,400&display=swap');

    /* --- 2. GERAL --- */
    html, body, [class*="css"], div, input, textarea { font-family: 'Montserrat', sans-serif !important; }
    
    .stApp {
        background-color: #0a0a0a;
        background-image: radial-gradient(#222 1px, transparent 1px);
        background-size: 20px 20px;
        color: #e0e0e0;
    }

    /* --- 3. INPUT (TUDO PRETO) --- */
    [data-testid="stBottom"] {
        background-color: #0a0a0a !important;
        border-top: 1px solid #333;
        padding-bottom: 30px;
        padding-top: 20px;
    }

    .stChatInput textarea {
        background-color: #000000 !important;
        color: #ffffff !important;
        border: 2px solid #333 !important;
        border-radius: 12px !important;
        padding: 15px !important;
        caret-color: #32A041;
    }
    
    .stChatInput textarea:focus {
        border: 2px solid #32A041 !important;
        box-shadow: 0 0 15px rgba(50, 160, 65, 0.2) !important;
    }

    ::placeholder { color: #666 !important; opacity: 1; }

    /* --- 4. BOTÕES --- */
    div.stButton > button {
        width: 100%;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        background-color: transparent;
        color: #32A041;
        border: 2px solid #32A041;
        border-radius: 8px;
        padding: 12px 5px;
        font-size: 14px;
        font-weight: 600;
        text-transform: uppercase;
        transition: all 0.2s ease;
    }
    div.stButton > button:hover {
        background-color: #32A041;
        color: white;
        transform: scale(1.02);
        box-shadow: 0 5px 15px rgba(50, 160, 65, 0.4);
    }

    /* --- 5. ÁREA DE CHAT --- */
    .user-msg { background-color: #1f1f1f; color: #fff; padding: 15px; border-radius: 20px 20px 4px 20px; text-align: right; float: right; clear: both; margin: 5px 0; border: 1px solid #333; max-width: 90%; }
    .bot-msg { background-color: #f5f5f5; color: #1a1a1a; padding: 15px; border-radius: 20px 20px 20px 4px; text-align: left; float: left; clear: both; margin: 5px 0; border-left: 5px solid #B30000; font-weight: 600; max-width: 90%; }

    /* --- 6. TÍTULOS --- */
    h1 { font-family: 'Playfair Display', serif !important; font-size: 3.5rem !important; text-align: center; color: #fff; letter-spacing: -1px; margin-top: 10px; }
    h2 { font-family: 'Playfair Display', serif !important; color: #32A041; text-align: center; font-style: italic; font-size: 2rem !important;}
    
    .char-img {
        border-radius: 12px;
        border: 2px solid #333;
        box-shadow: 0 5px 15px rgba(0,0,0,0.5);
    }

    @media only screen and (max-width: 600px) {
        h1 { font-size: 2.5rem !important; }
        div.stButton > button { font-size: 18px !important; padding: 15px !important; }
    }

    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 2. CONEXÃO COM A IA ---
api_key = "AIzaSyD7AzNyB2fbAS8AmD0bSxKKXlgl1MZnnUE" 

genai.configure(api_key=api_key)

@st.cache_resource
def setup_ai():
    try:
        modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        escolhido = next((m for m in modelos if 'flash' in m), modelos[0] if modelos else None)
        return genai.GenerativeModel(escolhido) if escolhido else None
    except Exception as e:
        print("Erro no setup_ai:", e)
        return None

model = setup_ai()

PERSONAGENS = {
    "PITOCO": {"img": "imagens/pitoco.jpeg", "cor": "#00d2d3", "desc_oculta": "Agroboy Fake"},
    "SAMUEL": {"img": "imagens/samuel.jpeg", "cor": "#eccc68", "desc_oculta": "Rico Marrento"},
    "BRYAN": {"img": "imagens/bryan.jpeg", "cor": "#54a0ff", "desc_oculta": "Gamer Chorão"},
    "SALDANHA": {"img": "imagens/saldanha.jpeg", "cor": "#ff6b6b", "desc_oculta": "Veterano"},
    "MITSUKI": {"img": "imagens/mitsuki.jpeg", "cor": "#ff9ff3", "desc_oculta": "Otaku Sus"},
    "MOISÉS": {"img": "imagens/moises.jpeg", "cor": "#5f27cd", "desc_oculta": "Explosivo"},
    "CAMARADA": {"img": "imagens/camarada.jpeg", "cor": "#ff9f43", "desc_oculta": "Brainrot"},
    "TIFAEL": {"img": "imagens/tifael.jpeg", "cor": "#8395a7", "desc_oculta": "Tiozão"},
    "JOAQUIM": {"img": "imagens/joaquim.jpeg", "cor": "#1dd1a1", "desc_oculta": "Político"},
    "INDIÃO": {"img": "imagens/indiao.jpeg", "cor": "#576574", "desc_oculta": "Sombra"}
}

# --- 4. PROMPTS E LÓGICA (AQUI ESTÁ A ATUALIZAÇÃO) ---
def get_system_prompt(personagem, fase, nivel_estresse):
    modo_estresse = ""
    if nivel_estresse >= 3:
        modo_estresse = "ALERTA DE SISTEMA: O USUÁRIO ESTÁ TE ENCHENDO O SACO. VOCÊ ESTÁ ESTRESSADO/IRRITADO. SEJA CURTO, GROSSO E MANDE ELE SAIR ('VAZA', 'SAI FORA')."
    
    contexto_caso = ""
    caso_atual = st.session_state.get('caso_atual', {"texto": "", "culpado": ""})
    if fase == "REVELACAO":
        contexto_caso = f"OCORRIDO GRAVE NO QUARTO: '{caso_atual['texto']}'. O Culpado real é {caso_atual['culpado']}. (Não revele nomes diretamente, mas reaja ao crime conforme sua personalidade)."
    else:
        contexto_caso = "FASE SOCIAL: O usuário é um NOVATO (Calouro) chegando no quarto C5. Você ainda não sabe de crime nenhum. Apenas converse, julgue o novato ou tente enturmá-lo."

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

    ### SÓ MITSUKI E SALDANHA USAM "TANKAR".
    ### INSTRUÇÃO FINAL DE FORMATO:
    - Mantenha a resposta curta (estilo papo natural da vida real).
    - Não use frases complexas.
    - Seja engraçado, tóxico ou estranho conforme o personagem.
    """

def gerar_caso():
    casos = [
        "Alguém deixou uma calcinha usada dentro do filtro de água.",
        "Sumiram 50 reais da carteira do Saldanha.",
        "Apareceu um desenho obsceno na porta do armário do Moisés.",
        "Entupiram o vaso e a água tá vazando pro corredor.",
        "Trouxeram uma galinha viva e ela cagou na cama do Bryan.",
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

# --- 5. ESTADOS ---
if 'fase' not in st.session_state: st.session_state.fase = 'START'
if 'caso_atual' not in st.session_state: st.session_state.caso_atual = gerar_caso()
if 'chat_history' not in st.session_state: st.session_state.chat_history = []
if 'personagem_atual' not in st.session_state: st.session_state.personagem_atual = None
if 'contador_conversas' not in st.session_state: st.session_state.contador_conversas = 0
if 'msg_no_turno' not in st.session_state: st.session_state.msg_no_turno = 0

# --- 6. INTERFACE ---

# TELA START
if st.session_state.fase == 'START':
    st.markdown("<h1>TROPA DO C5</h1>", unsafe_allow_html=True)
    st.markdown("<h2>QUEM É O ARROMBADO?</h2>", unsafe_allow_html=True)
    st.write("\n\n")
    
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        st.info("Você é o calouro novo. Tente sobreviver ao alojamento.")
        if st.button("ENTRAR NO QUARTO", use_container_width=True):
            st.session_state.fase = 'SELECAO_INICIAL'
            st.rerun()

# TELA SELEÇÃO
elif st.session_state.fase == 'SELECAO_INICIAL':
    st.markdown("<h2>QUEM VOCÊ VAI CUMPRIMENTAR?</h2>", unsafe_allow_html=True)
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

# TELA CHAT (LAYOUT NOVO LADO A LADO)
elif st.session_state.fase in ['SOCIAL', 'REVELACAO']:
    nome = st.session_state.personagem_atual
    dados = PERSONAGENS[nome]
    
    # CRIAÇÃO DE COLUNAS LADO A LADO (1/4 Imagem, 3/4 Chat)
    col_left, col_right = st.columns([1, 3])
    
    # --- COLUNA DA ESQUERDA (IMAGEM) ---
    with col_left:
        st.markdown(f"<img src='{dados['img']}' class='char-img' style='width:100%'>", unsafe_allow_html=True)
        st.markdown(f"<h2>{nome}</h2>", unsafe_allow_html=True)
        status_placeholder = st.empty()
        if st.session_state.msg_no_turno > 3:
            status_placeholder.caption("⚠️ ESTRESSADO")
        else:
            status_placeholder.caption("🟢 Online")

    # --- COLUNA DA DIREITA (CHAT SCROLLABLE) ---
    with col_right:
        chat_container = st.container(height=500) # Altura fixa com scroll
        with chat_container:
            for msg in st.session_state.chat_history:
                if msg['role'] == 'user':
                    st.markdown(f"<div class='user-msg'>{msg['content']}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='bot-msg'>{msg['content']}</div>", unsafe_allow_html=True)

    # --- INPUT FIXO EMBAIXO ---
    user_input = st.chat_input("Mande o papo (ou 'tchau' para sair)...")

    if user_input:
        if user_input.lower() in ['tchau', 'flw', 'vlw', 'vaza', 'sair', 'proximo', 'fui']:
            avancar_personagem()
        else:
            st.session_state.chat_history.append({'role': 'user', 'content': user_input})
            st.session_state.msg_no_turno += 1
            status_placeholder.caption(f"✍️ {nome} está digitando...")
            time.sleep(1) 
            
            prompt = get_system_prompt(nome, st.session_state.fase, st.session_state.msg_no_turno)
            try:
                chat = model.start_chat(history=[])
                resp = chat.send_message(f"SYSTEM: {prompt}\nUSER: {user_input}").text
            except Exception as e:
                print("Erro ao enviar mensagem para o modelo:", e)
                resp = "..."
            
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
    st.markdown("<h1>QUEM FOI?</h1>", unsafe_allow_html=True)
    st.markdown(f"**OCORRIDO:** {st.session_state.caso_atual['texto']}")
    
    escolha = st.selectbox("Selecione o Culpado:", list(PERSONAGENS.keys()))
    
    if st.button("ACUSAR", type="primary"):
        culpado_real = st.session_state.caso_atual['culpado']
        if escolha == culpado_real:
            st.balloons()
            st.success(f"ACERTOU! Foi o {culpado_real}!")
        else:
            st.error(f"ERROU! Quem fez foi o {culpado_real}!")
        
        if st.button("JOGAR DE NOVO"):
            st.session_state.clear()
            st.rerun()
