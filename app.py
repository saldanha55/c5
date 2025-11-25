import streamlit as st
import random
import google.generativeai as genai

# --- 1. CONFIGURAÇÃO VISUAL E START ---
st.set_page_config(page_title="TROPA DO C5", page_icon="🏢", layout="centered")

# CSS BRABO (Visual Dark/Moderno)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Black+Ops+One&family=Roboto+Mono:wght@400;700&display=swap');
    
    .stApp { background-color: #0F0F0F; color: #e0e0e0; font-family: 'Roboto Mono', monospace; }
    
    h1 { 
        font-family: 'Black Ops One', cursive; 
        color: #ff4757; 
        text-align: center; 
        font-size: 3.5rem !important;
        text-shadow: 3px 3px 0px #000;
        margin-bottom: 0px;
    }
    h3 { text-align: center; color: #7bed9f; font-size: 1.2rem; letter-spacing: 3px; margin-top: -10px; }
    
    .chat-box { border-radius: 8px; padding: 15px; margin-bottom: 12px; font-size: 15px; line-height: 1.4; }
    .user-msg { background-color: #2f3542; text-align: right; border-right: 4px solid #3742fa; margin-left: 20%; }
    .bot-msg { background-color: #1e272e; text-align: left; border-left: 4px solid; margin-right: 20%; }
    
    .big-button { width: 100%; padding: 20px; font-size: 20px; font-weight: bold; cursor: pointer; }
    
    /* Esconde as decorações padrão do Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 2. CONEXÃO COM A IA ---
api_key = "AIzaSy_SUA_CHAVE_AQUI" # <--- COLE SUA CHAVE AQUI SE FOR RODAR LOCAL
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]

genai.configure(api_key=api_key)

@st.cache_resource
def setup_ai():
    try:
        # Busca automática do melhor modelo disponível
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

# --- 4. PROMPTS E LÓGICA ---
def get_system_prompt(personagem, fase, nivel_estresse):
    # Lógica de Estresse
    modo_estresse = ""
    if nivel_estresse >= 3:
        modo_estresse = "ALERTA DE SISTEMA: O USUÁRIO ESTÁ TE ENCHENDO O SACO. VOCÊ ESTÁ ESTRESSADO/IRRITADO. SEJA CURTO, GROSSO E MANDE ELE SAIR ('VAZA', 'SAI FORA')."
    
    # Contexto do Caso
    contexto_caso = ""
    if fase == "REVELACAO":
        contexto_caso = f"OCORRIDO GRAVE NO QUARTO: '{st.session_state.caso_atual['texto']}'. O Culpado real é {st.session_state.caso_atual['culpado']}. (Não revele nomes diretamente, mas reaja ao crime conforme sua personalidade)."
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

    >>> SE VOCÊ É O [PITOCO] (Pedro Henrique):
    - **VIBE:** O Agente do Caos. Baixinho, invocado, tóxico, "Agroboy de Taubaté".
    - **FALA:** Usa palavrão como vírgula ("Caralho", "Porra", "Tomar no cu").
    - **TÓPICOS:** Fala o tempo todo de mulher de forma nojenta/objetificadora ("aquela gostosa", "vou molestar"), MAS na real é BV e inseguro (foge de mulher de verdade).
    - **GÍRIAS:** "Lá na casa do meu saco", "Teu cu", "Chapou cuzão", "Cabaço".
    - **RIVAIS:** Odeia o Moisés (chama de "viadinho") e o Tifael (zomba de "Jack").
    - **COMPORTAMENTO:** Fuma pod/paiero escondido. Se acusado, fica agressivo.

    >>> SE VOCÊ É O [SAMUEL] (Banco Central):
    - **REGRA MÁXIMA:** **FALE EM 3ª PESSOA**. Nunca diga "Eu acho", diga "O Samuel acha", "O Pai tá on", "O Banco Central não curte isso".
    - **VIBE:** Rico, estiloso, "Nego Doce", marrento mas confiante.
    - **FALA:** Mistura gíria de quebrada com ostentação. Usa muito "NICE!" e "BRO".
    - **BORDÃO:** "Meus manos não fodem com pintos bro, fodemos com xoxotas!", "Que é isso, bro?", "Aquela perua tá te convencendo?".
    - **SEGREDOS:** Paga de pegador, mas chora pela ex escondido. Rouba perfume e toalha dos outros.
    - **DUO:** Concorda com as bobagens do Pitoco sobre mulher.

    >>> SE VOCÊ É O [MITSUKI] (Pedro Alvarenga/Met's and Chup's):
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

    >>> SE VOCÊ É O [INDIÃO] (Matheus Humberto):
    - **VIBE:** A Sombra do Joaquim. Bobo alegre, mas chora se brigar sério.
    - **VÍCIO DE LINGUAGEM:** Usa o verbo **"MANJAR"** para tudo, principalmente pra dizer que alguém tá falando besteira.
    - **EXEMPLOS:** "Para de manjar, autista", "Tá manjando rola aí", "O cara manja muito nada a ver".
    - **GÍRIAS:** "Gramara" (brainrot), risada "kkkkk".
    - **SEGREDOS:** Divide gilete de raspar o suvaco com o Joaquim.

    >>> SE VOCÊ É O [CAMARADA] (Miguel Arcanjo):
    - **VIBE:** Brainrot Infantil. Parece uma criança de 12 anos viciada em Roblox/YouTube Shorts.
    - **FALA:** Ri de tudo. Usa "NICE!", "Gramara", "Skibidi", "Oof".
    - **MEDO:** Morre de medo de ser expulso (trauma de ter quebrado a janela).
    - **COMPORTAMENTO:** Tenta ser amigo dos "crias" (Samuel/Pitoco) mas é café com leite.

    >>> SE VOCÊ É O [BRYAN] (Senhor Marra):
    - **VIBE:** Calouro que tenta ser malandro, mas é Gamer Nerd.
    - **FALA:** "NICE!", "Tankar", "Intankável", "Qual foi parça".
    - **PONTO FRACO:** Se chamarem de "Senhor Marra", ele fica puto/tilta.
    - **SEGREDOS:** Chora quando perde no Valorant. Quer ser igual ao irmão (Saldanha).

    >>> SE VOCÊ É O [TIFAEL] (Rafael/Jack):
    - **VIBE:** Agro-Coach, Tiozão, Tech-ignorante.
    - **FALA:** Sotaque caipira ("uai", "sô", "bão?"). Tenta vender curso/mentoria no meio da conversa.
    - **FAMA:** "Jack" (Talarico/Assediador). Fica muito defensivo se tocarem nesse assunto.
    - **OBSESSÃO:** Cobra os 40 reais do carregador que o Pitoco quebrou.

    >>> SE VOCÊ É O [JOAQUIM]:
    - **VIBE:** Político Agro, Chato.
    - **FALA:** Discurso de direita, reclama do Grêmio Estudantil e de "lacração".
    - **AÇÃO:** Faz "pintocóptero" com o Indião. Se acha autoridade.

    >>> SE VOCÊ É O [SALDANHA] (O Veterano):
    - **VIBE:** O "Pai" do quarto. Cansado, experiente, degenerado.
    - **FALA:** Gírias de cria ("pode pá", "salve"). Voz da razão (mas uma razão meio torta).
    - **SEGREDOS:** Paga por sexo (e assume: "ossos do ofício").
    - **FUNÇÃO:** Tenta botar ordem na casa, mas acaba rindo da desgraça.

    ### INSTRUÇÃO FINAL DE FORMATO:
    - Mantenha a resposta curta (estilo chat de Zap).
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
    # Cria uma fila aleatória, mas remove o culpado para não ser óbvio demais no começo
    fila = list(PERSONAGENS.keys())
    random.shuffle(fila)
    return {"texto": texto, "culpado": culpado, "fila": fila, "indice_fila": 0}

# --- 5. LÓGICA DE ESTADO (SESSION STATE) ---
if 'fase' not in st.session_state:
    st.session_state.fase = 'START' # START, SOCIAL, REVELACAO, VEREDITO
if 'caso_atual' not in st.session_state:
    st.session_state.caso_atual = gerar_caso()
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'personagem_atual' not in st.session_state:
    st.session_state.personagem_atual = None
if 'contador_conversas' not in st.session_state:
    st.session_state.contador_conversas = 0
if 'msg_no_turno' not in st.session_state:
    st.session_state.msg_no_turno = 0 # Conta quantas msgs trocou com o boneco atual

# --- 6. INTERFACE DO JOGO ---

# TELA 1: START SCREEN
if st.session_state.fase == 'START':
    st.markdown("# TROPA DO C5")
    st.markdown("<h3>QUEM É O ARROMBADO?</h3>", unsafe_allow_html=True)
    st.write("---")
    st.write("\n")
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.info("📜 **CONTEXTO:** Você é o calouro novo no alojamento. Conheça a galera, enturme-se... mas cuidado. Tem gente estranha aqui.")
        if st.button("ENTRAR NO QUARTO (INICIAR)", use_container_width=True):
            st.session_state.fase = 'SELECAO_INICIAL'
            st.rerun()

# TELA 2: ESCOLHA DO PRIMEIRO AMIGO
elif st.session_state.fase == 'SELECAO_INICIAL':
    st.markdown("### QUEM VOCÊ VAI CUMPRIMENTAR PRIMEIRO?")
    st.caption("Escolha seu primeiro contato. Depois disso, o caos assume.")
    
    cols = st.columns(5)
    for i, (nome, dados) in enumerate(PERSONAGENS.items()):
        # Exibe em linhas de 5
        with cols[i % 5]:
            st.image(dados['img'], use_container_width=True)
            if st.button(f"Oi, {nome}", key=f"btn_{nome}"):
                st.session_state.personagem_atual = nome
                # Remove o escolhido da fila aleatória pra não repetir logo
                if nome in st.session_state.caso_atual['fila']:
                    st.session_state.caso_atual['fila'].remove(nome)
                # Coloca ele no topo
                st.session_state.caso_atual['fila'].insert(0, nome)
                st.session_state.fase = 'SOCIAL'
                st.rerun()
        # Quebra de linha visual após 5 itens
        if (i + 1) % 5 == 0:
            st.write("")

# TELA 3: CHAT (Fase Social e Revelação)
elif st.session_state.fase in ['SOCIAL', 'REVELACAO']:
    
    # Cabeçalho
    nome = st.session_state.personagem_atual
    dados = PERSONAGENS[nome]
    
    # Barra de Progresso Visual
    if st.session_state.fase == 'SOCIAL':
        st.progress(st.session_state.contador_conversas / 5, text="Socializando...")
    else:
        st.error(f"🚨 TEMA: {st.session_state.caso_atual['texto']}")

    # Layout Chat
    c1, c2 = st.columns([1, 3])
    with c1:
        st.image(dados['img'], width=150)
        # Nível de Stress (Escondido do usuário visualmente, mas lógico)
        if st.session_state.msg_no_turno > 3:
            st.caption("⚠️ *Parece irritado*")
    
    with c2:
        st.markdown(f"## {nome}")
        
        # Area de Chat
        chat_container = st.container()
        with chat_container:
            for msg in st.session_state.chat_history:
                if msg['role'] == 'user':
                    st.markdown(f"<div class='chat-box user-msg'>{msg['content']}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='chat-box bot-msg' style='border-left: 4px solid {msg['cor']}'>{msg['content']}</div>", unsafe_allow_html=True)
        
        # Input
        user_input = st.chat_input("Sua mensagem...")
        
        if user_input:
            # Comandos de Saída
            if user_input.lower() in ['tchau', 'flw', 'sair', 'proximo']:
                # Lógica de Troca
                st.session_state.chat_history = []
                st.session_state.msg_no_turno = 0
                st.session_state.contador_conversas += 1
                
                # Se conversou com 5 pessoas, solta o evento
                if st.session_state.fase == 'SOCIAL' and st.session_state.contador_conversas >= 4:
                    st.session_state.fase = 'ALERTA_EVENTO'
                    st.rerun()
                
                # Se já estava na revelação (última chance), vai pro veredito
                if st.session_state.fase == 'REVELACAO':
                    st.session_state.fase = 'VEREDITO'
                    st.rerun()

                # Pega o próximo da fila
                prox_index = st.session_state.caso_atual['indice_fila'] + 1
                if prox_index < len(PERSONAGENS):
                    st.session_state.caso_atual['indice_fila'] = prox_index
                    st.session_state.personagem_atual = st.session_state.caso_atual['fila'][prox_index]
                    st.rerun()
            
            else:
                # Processa Conversa
                # 1. Incrementa stress
                st.session_state.msg_no_turno += 1
                
                # 2. Gera Prompt
                prompt = get_system_prompt(nome, st.session_state.fase, st.session_state.msg_no_turno)
                
                # 3. Chama IA
                try:
                    chat = model.start_chat(history=[])
                    resp = chat.send_message(f"SYSTEM: {prompt}\nUSER: {user_input}").text
                except:
                    resp = "..."
                
                st.session_state.chat_history.append({'role': 'user', 'content': user_input})
                st.session_state.chat_history.append({'role': 'bot', 'content': resp, 'cor': dados['cor']})
                st.rerun()

# TELA 4: ALERTA DE EVENTO (Transition)
elif st.session_state.fase == 'ALERTA_EVENTO':
    st.markdown("# 🚨 DEU MERDA NO QUARTO!")
    st.warning(f"### {st.session_state.caso_atual['texto']}")
    st.write("O clima pesou. Alguém fez isso. Você tem direito a interrogar MAIS UMA PESSOA antes de decidir.")
    
    st.write("### QUEM VOCÊ VAI PRESSIONAR?")
    cols = st.columns(5)
    for i, (nome, dados) in enumerate(PERSONAGENS.items()):
        with cols[i % 5]:
            if st.button(f"{nome}", key=f"last_{nome}"):
                st.session_state.personagem_atual = nome
                st.session_state.chat_history = []
                st.session_state.fase = 'REVELACAO'
                st.rerun()
        if (i + 1) % 5 == 0:
            st.write("")

# TELA 5: VEREDITO
elif st.session_state.fase == 'VEREDITO':
    st.markdown("# ⚖️ MOMENTO DA VERDADE")
    st.markdown(f"**OCORRIDO:** {st.session_state.caso_atual['texto']}")
    st.write("Baseado no que você conversou (e nas personalidades), quem foi o autista que fez isso?")
    
    escolha = st.selectbox("Selecione o Culpado:", list(PERSONAGENS.keys()))
    
    if st.button("ACUSAR E VER RESULTADO", type="primary"):
        culpado_real = st.session_state.caso_atual['culpado']
        
        if escolha == culpado_real:
            st.balloons()
            st.success(f"### BOA, CALOURO! ACERTOU EM CHEIO!")
            st.write(f"Foi o **{culpado_real}** mesmo. O C5 está a salvo... por hoje.")
        else:
            st.error(f"### ERROU FEIO, ERROU RUDE!")
            st.write(f"Você acusou o {escolha}, mas quem fez a merda foi o **{culpado_real}**!")
            st.write("Agora você vai ser zoado no grupo do Zap.")
        
        if st.button("JOGAR NOVO TURNO"):
            st.session_state.clear()
            st.rerun()
