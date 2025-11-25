import streamlit as st
import random
import time
import google.generativeai as genai

# --- 1. CONFIGURAÇÃO VISUAL ---
st.set_page_config(page_title="TROPA DO C5", page_icon="🌶️", layout="centered")

# --- DESIGN SYSTEM: LITERATURE & MODERN ---
st.markdown("""
<style>
    /* Importando as fontes */
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600&family=Playfair+Display:wght@700;900&display=swap');

    /* --- 1. FONTE DO CORPO (Moderno/Clean) --- */
    html, body, [class*="css"], button, input, textarea, div {
        font-family: 'Montserrat', sans-serif !important;
    }

    /* --- 2. FONTE DE TÍTULOS (Literature) --- */
    h1, h2, h3, h4, .role-title {
        font-family: 'Playfair Display', serif !important;
    }

    /* --- 3. FUNDO E CORES --- */
    .stApp { 
        background-color: #0e0e0e; 
        color: #e0e0e0; 
    }

    /* --- 4. BARRA DE DIGITAÇÃO (Clean & Dark) --- */
    [data-testid="stBottom"] {
        background-color: #121212 !important; 
        border-top: 1px solid #333;
        padding-top: 15px;
        padding-bottom: 25px;
    }
    
    /* A caixa de texto (Input) */
    .stChatInput textarea {
        background-color: #262626 !important; /* Cinza Chumbo */
        color: #ffffff !important;
        border: 1px solid #444 !important;
        border-radius: 12px !important; /* Bordas arredondadas modernas */
        font-size: 16px !important;
    }
    
    /* Foco na caixa de texto */
    .stChatInput textarea:focus {
        border: 1px solid #B30000 !important; /* Vermelho IF sutil ao clicar */
        box-shadow: none !important;
    }

    /* --- 5. TÍTULOS ESTILIZADOS --- */
    h1 { 
        color: #f1f1f1;
        background: linear-gradient(90deg, #B30000 0%, #7c0000 100%); /* Degradê Vermelho */
        padding: 20px;
        border-radius: 0px 0px 15px 15px;
        text-align: center;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 2.8rem !important;
        border-bottom: 4px solid #32A041; /* Verde IF */
        margin-top: -50px !important; /* Cola no topo */
    }
    
    h2 { color: #32A041; font-size: 1.8rem !important; margin-bottom: 0px; }
    h3 { color: #aaa; font-style: italic; font-weight: 400; font-size: 1.2rem !important;}

    /* --- 6. BALÕES DE CHAT (Moderno) --- */
    .user-msg { 
        background-color: #2b2b2b; 
        color: #fff; 
        padding: 12px 18px; 
        border-radius: 18px 18px 4px 18px; /* Formato de balão moderno */
        margin: 8px 0; 
        text-align: right; 
        float: right;
        clear: both;
        max-width: 85%;
        border-right: 3px solid #32A041; /* Detalhe Verde */
        box-shadow: 0 2px 5px rgba(0,0,0,0.3);
    }
    .bot-msg { 
        background-color: #B30000; /* Vermelho IF */
        color: #fff; 
        padding: 12px 18px; 
        border-radius: 18px 18px 18px 4px; 
        margin: 8px 0; 
        text-align: left; 
        float: left;
        clear: both;
        max-width: 85%;
        box-shadow: 0 2px 5px rgba(0,0,0,0.3);
        font-weight: 500;
    }

    /* --- 7. BOTÕES --- */
    div.stButton > button { 
        background-color: #32A041; 
        color: white; 
        border: none; 
        border-radius: 8px;
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 600;
        text-transform: uppercase;
        padding: 15px;
        letter-spacing: 1px;
        transition: 0.2s;
    }
    div.stButton > button:hover { 
        background-color: #267d32; 
        transform: translateY(-2px);
        box-shadow: 0 4px 10px rgba(50, 160, 65, 0.4);
    }
    
    /* Esconde menu padrão */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 2. CONEXÃO COM A IA ---
api_key = "AIzaSyD7AzNyB2fbAS8AmD0bSxKKXlgl1MZnnUE" # <--- COLE A CHAVE AQUI SE RODAR LOCAL
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]

genai.configure(api_key=api_key)

@st.cache_resource
def setup_ai():
    try:
        modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        escolhido = next((m for m in modelos if 'flash' in m), modelos[0] if modelos else None)
        return genai.GenerativeModel(escolhido) if escolhido else None
    except:
        return None

model = setup_ai()

# --- 3. DADOS DO JOGO ---
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
    "INDIÃO": {"img": "imagens/indiao.jpeg", "cor": "#576574", "desc_oculta": "Sombra"},
}

# --- 4. FUNÇÕES LÓGICAS ---
def get_system_prompt(personagem, fase, nivel_estresse):
    modo_estresse = ""
    if nivel_estresse >= 3:
        modo_estresse = "ALERTA: O USUÁRIO ESTÁ TE ENCHENDO O SACO. VOCÊ ESTÁ ESTRESSADO. SEJA CURTO, GROSSO E MANDE ELE SAIR."
    
    contexto_caso = ""
    if fase == "REVELACAO":
        contexto_caso = f"OCORRIDO GRAVE: '{st.session_state.caso_atual['texto']}'. O Culpado real é {st.session_state.caso_atual['culpado']}. (Não revele nomes, mas reaja ao crime)."
    else:
        contexto_caso = "FASE SOCIAL: O usuário é um NOVATO (Calouro) chegando no quarto. Você ainda não sabe de crime nenhum. Apenas converse e julgue o novato."

    return f"""
    VOCÊ INTERPRETA: {personagem} no Alojamento C5 (Instituto Federal).
    USUÁRIO: Novato/Calouro.
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
    
    # Checagem de Fases
    if st.session_state.fase == 'SOCIAL' and st.session_state.contador_conversas >= 4:
        st.session_state.fase = 'ALERTA_EVENTO'
        st.rerun()
    
    if st.session_state.fase == 'REVELACAO':
        st.session_state.fase = 'VEREDITO'
        st.rerun()

    # Próximo da fila
    prox_index = st.session_state.caso_atual['indice_fila'] + 1
    if prox_index < len(PERSONAGENS):
        st.session_state.caso_atual['indice_fila'] = prox_index
        st.session_state.personagem_atual = st.session_state.caso_atual['fila'][prox_index]
        st.rerun()

# --- 5. LÓGICA DE ESTADO ---
if 'fase' not in st.session_state: st.session_state.fase = 'START'
if 'caso_atual' not in st.session_state: st.session_state.caso_atual = gerar_caso()
if 'chat_history' not in st.session_state: st.session_state.chat_history = []
if 'personagem_atual' not in st.session_state: st.session_state.personagem_atual = None
if 'contador_conversas' not in st.session_state: st.session_state.contador_conversas = 0
if 'msg_no_turno' not in st.session_state: st.session_state.msg_no_turno = 0

# --- 6. INTERFACE (TELAS) ---

# TELA START
if st.session_state.fase == 'START':
    st.markdown("<h1>TROPA DO C5</h1>", unsafe_allow_html=True)
    st.markdown("<h3>QUEM É O ARROMBADO?</h3>", unsafe_allow_html=True)
    st.write("\n\n")
    
    c1, c2, c3 = st.columns([1,8,1])
    with c2:
        st.success("Bem-vindo ao Alojamento do IF. Você é o novato. Tente sobreviver.")
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
        if (i + 1) % 5 == 0: st.write("")

# TELA CHAT (PRINCIPAL)
elif st.session_state.fase in ['SOCIAL', 'REVELACAO']:
    nome = st.session_state.personagem_atual
    dados = PERSONAGENS[nome]
    
    # Header com Layout de Colunas
    col_img, col_txt = st.columns([1, 4])
    
    with col_img:
        st.image(dados['img'], use_container_width=True)
    
    with col_txt:
        st.markdown(f"## {nome}")
        
        # --- AQUI ESTÁ O TRUQUE DO STATUS ---
        # Criamos um "espaço vazio" (placeholder) para poder mudar o texto depois
        status_placeholder = st.empty()
        
        # Lógica inicial do status
        if st.session_state.msg_no_turno > 3:
            status_placeholder.caption("⚠️ ESTRESSADO: Melhor sair logo.")
        else:
            status_placeholder.caption("🟢 Online")

    # ÁREA DE CHAT COM SCROLL
    chat_container = st.container(height=350)
    
    with chat_container:
        for msg in st.session_state.chat_history:
            if msg['role'] == 'user':
                st.markdown(f"<div class='user-msg'>{msg['content']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='bot-msg'>{msg['content']}</div>", unsafe_allow_html=True)

    # Input Fixo Embaixo
    user_input = st.chat_input("Mande o papo (ou 'tchau' para sair)...")

    if user_input:
        # 1. Checa Saída
        if user_input.lower() in ['tchau', 'flw', 'vaza', 'sair', 'proximo', 'fui']:
            avancar_personagem()
        else:
            # 2. Exibe msg do usuário imediatamente
            st.session_state.chat_history.append({'role': 'user', 'content': user_input})
            st.session_state.msg_no_turno += 1
            
            # --- EFEITO VISUAL DE DIGITANDO ---
            # Atualizamos aquele espaço vazio lá de cima
            status_placeholder.caption(f"✍️ {nome} está digitando...")
            
            # Pequeno delay para dar tempo de ver o status mudando
            time.sleep(0.5) 
            
            # 3. Gera Resposta IA
            prompt = get_system_prompt(nome, st.session_state.fase, st.session_state.msg_no_turno)
            try:
                chat = model.start_chat(history=[])
                resp = chat.send_message(f"SYSTEM: {prompt}\nUSER: {user_input}").text
            except:
                resp = "..."
            
            # 4. Salva e Atualiza
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
        if (i + 1) % 5 == 0: st.write("")

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









