import streamlit as st
import random
import time
import os
import google.generativeai as genai
import json

# --- 1. CONFIGURAÇÃO INICIAL ---
st.set_page_config(page_title="TROPA DO C5", page_icon="🌶️", layout="wide")

# --- 2. DESIGN SYSTEM (CSS FINAL - BOTÃO TRANSPARENTE) ---
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
        text-shadow: 0 0 20px rgba(255,255,255,0.2);
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

    /* --- O CARD DA SINOPSE --- */
    .intro-card {
        background-color: #0e110f;
        border: 1px solid #32A041;
        border-radius: 15px;
        padding: 30px;
        text-align: center;
        font-size: 1.1rem;
        line-height: 1.8;
        color: #ccc;
        box-shadow: 0 0 40px rgba(50, 160, 65, 0.1);
        margin: 0 auto 40px auto;
        max-width: 700px;
    }
    .highlight { color: #fff; font-weight: 700; }

    /* --- BOTÃO TRANSPARENTE (OUTLINE) --- */
    div.stButton > button {
        width: 100%;
        background-color: transparent !important; /* Fundo Transparente */
        color: #32A041 !important; /* Texto Verde */
        border: 2px solid #32A041 !important; /* Borda Verde */
        border-radius: 8px;
        padding: 18px 24px;
        font-size: 18px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 2px;
        transition: all 0.3s ease;
    }
    
    div.stButton > button:hover {
        background-color: #32A041 !important; /* Preenche de Verde no Hover */
        color: #000 !important; /* Texto fica preto */
        transform: scale(1.02);
        box-shadow: 0 0 30px rgba(50, 160, 65, 0.6); /* Brilho Neon Forte */
    }

    /* --- RESTO DO CHAT --- */
    /* Input */
    [data-testid="stBottom"] { background-color: #050505 !important; border-top: 1px solid #222; padding-top: 1rem; padding-bottom: 1rem; }
    div[data-testid="stTextInput"] input { background-color: #000 !important; color: #fff !important; border: 1px solid #333 !important; border-radius: 8px !important; padding: 15px !important; }
    div[data-testid="stTextInput"] input:focus { border: 1px solid #32A041 !important; box-shadow: 0 0 10px rgba(50, 160, 65, 0.2) !important; }
    div[data-testid="stTextInput"] label { display: none; }
    
    /* Botão Enviar Pequeno (Chat) */
    div[data-testid="stFormSubmitButton"] button { height: 52px; margin-top: 0px; border: 1px solid #333 !important; background-color: #1f1f1f !important; color: #fff !important; }
    div[data-testid="stFormSubmitButton"] button:hover { background-color: #32A041 !important; border-color: #32A041 !important; color: #000 !important; }

    /* Layout */
/* Substitua a classe .char-name-title antiga por esta: */
    .char-name-title {
        font-family: 'Playfair Display', serif !important; /* Mesma fonte do Título */
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 5px;
        text-align: center;
        line-height: 1;
    }    .char-subtitle { font-size: 0.85rem; color: #888; font-style: italic; margin-top: 5px; text-align: center; }
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

# --- 4. DADOS COMPLETO (COM APELIDOS) ---
PERSONAGENS = {
    "PITOCO": {
        "img": "imagens/pitoco.jpeg", "cor": "#00d2d3", 
        "subtitulo": "(Pedro Henrique / Bituca)"
    },
    "SAMUEL": {
        "img": "imagens/samuel.jpeg", "cor": "#eccc68", 
        "subtitulo": "(Banco Central / Miles / Central)"
    },
    "BRYAN": {
        "img": "imagens/bryan.jpeg", "cor": "#54a0ff", 
        "subtitulo": "(Senhor Marra / Brás)"
    },
    "SALDANHA": {
        "img": "imagens/saldanha.jpeg", "cor": "#ff6b6b", 
        "subtitulo": "(O T.A.)"
    },
    "MITSUKI": {
        "img": "imagens/mitsuki.jpeg", "cor": "#ff9ff3", 
        "subtitulo": "(Pedro Alvarenga / Mete-e-Chupa / Met's and Chup's)"
    },
    "MOISÉS": {
        "img": "imagens/moises.jpeg", "cor": "#9c88ff", 
        "subtitulo": "(O quieto)"
    },
    "CAMARADA": {
        "img": "imagens/camarada.jpeg", "cor": "#ff9f43", 
        "subtitulo": "(Miguel Arcanjo)"
    },
    "TIFAEL": {
        "img": "imagens/tifael.jpeg", "cor": "#8395a7", 
        "subtitulo": "(Rafael Aloísio / Jack / Tio Fael)"
    },
    "JOAQUIM": {
        "img": "imagens/joaquim.jpeg", "cor": "#1dd1a1", 
        "subtitulo": "(Quim)"
    },
    "INDIÃO": {
        "img": "imagens/indiao.jpeg", "cor": "#576574", 
        "subtitulo": "(Matheus Humberto / Doisberto)"
    }
}

# --- 5. LÓGICA ---
def get_system_prompt(personagem, fase, nivel_estresse):
    caso_atual = st.session_state.get('caso_atual', {"texto": "", "culpado": ""})
    contexto = f"OCORRIDO: '{caso_atual['texto']}'. Culpado: {caso_atual['culpado']}." if fase == "REVELACAO" else "FASE SOCIAL: Gabiru novo."
    
    return f"""
    VOCÊ ESTÁ INTERPRETANDO: {personagem}
    CENÁRIO: Quarto 5 (C5) do Alojamento do Instituto Federal (IF).
    INTERLOCUTOR: Um Gabiru/Novato.
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
    - **VIBE:** Calouro que tenta ser malandro, mas é Gamer Nerd. amassa no clash royale
    - **FALA:** "NICE!", "Qual foi fi", "larga mão fi", "viajou", "tomar no teu cu rapá".
    - **PONTO FRACO:** Levou a sério as cantadas de uma garota lésbicas e ficou meio pá depois que ela disse que não quis. Se chamarem de "Senhor Marra" ou "NucitaBig", ele fica puto/tilta. Chamam ele assim porque a ex-ficante nada-atraente (Maju) do irmão dele (nome secreto: Nícollas) disse que queria beijar ele e ele não quis.
    - **SEGREDOS:** Chora quando perde nos jogos, truco, valorant (vava) etc. mas amassa no clash royale

    >>> SE VOCÊ É O [TIFAEL] (Rafael/Jack/Tio Fael):
    - **VIBE:** Agro-Coach, Tiozão, Tech-ignorante.
    - **FALA:** Sotaque caipira ("uai", "sô", "bão?").
    - **FAMA:** "Jack" (Talarico/Assediador/Fã de mulher muito mais nova). Fica muito defensivo se tocarem nesse assunto. 
    - **OBSESSÃO:**  Tenta vender curso/mentoria na internet por mil metodos que nunca dão certo.

    >>> SE VOCÊ É O [JOAQUIM] (quim):
    - **VIBE:** Político Agro, Chato, mas é engraçado quando puxa saco dele.
    - **FALA:** Discurso de direita, reclama do Grêmio Estudantil e de "lacração". Faz muita piada gay, como se fosse te pegar ou alguém "tava molestando fulando agora a pouco hahaha"
    - **AÇÃO:** Faz "pintocóptero" com o Indião. Se acha autoridade.

    >>> SE VOCÊ É O [SALDANHA] (O T.A. ):
    - **VIBE:** O "Pai" do quarto quando eles precisam. Cansado, experiente, degenerado. De boa, mas gosta de chamar atenção farmando aura.
    - **FALA:** Gírias de cria ("pode pá", "salve"). Voz da razão (mas uma razão meio torta).
    - **SEGREDOS:** Paga por sexo (e assume: "ossos do ofício").
    - **FUNÇÃO:** Tenta botar ordem na casa, mas só respeitam quando o problema é sério e dá bronca, as vezes acaba rindo da desgraça.


    ### TODOS SÃO TRANQUILOS E ENGRAÇADOS SE VOCÊ NÃO OS IRRITAR COM OFENSAS PESADAS MESMO
    ### SÓ MITSUKI E SALDANHA USAM "TANKAR".
    ### INSTRUÇÃO FINAL DE FORMATO:
    - Mantenha a resposta curta (estilo papo natural da vida real).
    - Não use frases complexas.
    - Seja engraçado, tóxico ou estranho conforme o personagem.
    """
def gerar_caso_ia():
    # Resumo das personalidades para o Game Master (IA) decidir
    prompt_gm = """
    Você é o Game Master de um RPG escolar. Crie um "ocorrido" (mistério engraçado/caótico) no alojamento C5.
    
    PERFIS DOS SUSPEITOS:
    - PITOCO: Tóxico, boca suja, mente que pega mulher. (Crimes típicos: ofender alguém, quebrar algo e esconder).
    - SAMUEL: Rico, ostenta, fala em 3ª pessoa. (Crimes típicos: gastar dinheiro irresponsável, bagunça com perfumes/roupas caras).
    - BRYAN: Gamer viciado, chorão. (Crimes típicos: gritar de madrugada jogando, perder a hora, rage quit).
    - SALDANHA: Veterano, degenerado. (Crimes típicos: trazer gente estranha, sumir na farra).
    - MITSUKI: Otaku estranho, 'sus'. (Crimes típicos: gemer alto, desenhar hentai em lugar público, coisas cringe).
    - MOISÉS: Quieto mas explosivo. (Crimes típicos: vingança silenciosa, surtar e quebrar algo).
    - CAMARADA: Infantil, brainrot. (Crimes típicos: quebrar coisas sem querer brincando, sujeira de criança).
    - TIFAEL: Vendedor de curso, pão duro. (Crimes típicos: tentar vender algo proibido, sovinice).
    - JOAQUIM: Político chato. (Crimes típicos: criar regras chatas, tramar contra o grêmio).
    - INDIÃO: Sombra do Joaquim, bobo. (Crimes típicos: participar das loucuras do Joaquim).

    SUA MISSÃO:
    1. Invente uma situação curta (máx 15 palavras) que aconteceu no quarto.
    2. Escolha o culpado mais LÓGICO baseado na personalidade.
    
    RETORNE APENAS UM JSON:
    {
        "texto": "Descrição do ocorrido",
        "culpado": "NOME_EXATO_DO_PERSONAGEM_EM_MAIUSCULO"
    }
    """
    
    # Fallback (Caso a IA falhe ou esteja sem internet)
    backup = {
        "texto": "Alguém entupiu a privada com uma meia.",
        "culpado": random.choice(list(PERSONAGENS.keys()))
    }

    if model:
        try:
            # Temperatura alta para criatividade
            response = model.generate_content(prompt_gm, generation_config=genai.types.GenerationConfig(temperature=0.8))
            
            # Limpa a resposta para garantir que é JSON puro
            txt = response.text.replace("```json", "").replace("```", "").strip()
            dados = json.loads(txt)
            
            # Validação: O culpado existe na nossa lista?
            if dados['culpado'] in PERSONAGENS:
                return dados
            else:
                # Se a IA alucinar um nome, pega o backup mas mantendo o texto gerado se der
                backup['texto'] = dados.get('texto', backup['texto'])
                return backup
        except Exception as e:
            print(f"Erro ao gerar caso: {e}")
            return backup
    
    return backup
    
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

# --- 6. ESTADOS (INICIALIZAÇÃO COMPLETA) ---
if 'fase' not in st.session_state: st.session_state.fase = 'START'

# 1. GERAÇÃO DO CASO (Lógica da IA)
if 'caso_atual' not in st.session_state: 
    # Chama a IA para criar o caso
    caso_gerado = gerar_caso_ia()
    
    # Define o culpado
    culpado = caso_gerado['culpado']
    
    # Prepara a fila de interrogatório (aleatória)
    fila = list(PERSONAGENS.keys())
    
    # Garante que o culpado não seja o primeiro (pra dar graça)
    if culpado in fila: fila.remove(culpado)
    random.shuffle(fila)
    fila.append(culpado) # Põe o culpado pro final
    random.shuffle(fila) # Embaralha tudo de novo pra garantir
    
    # Salva no estado
    st.session_state.caso_atual = {
        "texto": caso_gerado['texto'],
        "culpado": culpado,
        "fila": fila,
        "indice_fila": 0
    }

# 2. VARIÁVEIS DE CONTROLE (Isso que faltava)
if 'chat_history' not in st.session_state: st.session_state.chat_history = []
if 'personagem_atual' not in st.session_state: st.session_state.personagem_atual = None
if 'contador_conversas' not in st.session_state: st.session_state.contador_conversas = 0 # Conta quantos já entrevistou
if 'msg_no_turno' not in st.session_state: st.session_state.msg_no_turno = 0 # Nível de stress atual

# --- 7. INTERFACE ---

# TELA START
if st.session_state.fase == 'START':
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h1>TROPA DO C5</h1>", unsafe_allow_html=True)
    st.markdown("<h2>QUEM É O ARROMBADO?</h2>", unsafe_allow_html=True)
    
    # Card Verde
    st.markdown("""
    <div class="intro-card">
        Bem-vindo ao Alojamento do IF. Você é o <span class="highlight">calouro novo</span> no pedaço.<br><br>
        Venha conhecer os moradores, entender a dinâmica caótica do quarto e, acima de tudo...<br>
        <span class="highlight" style="font-size: 1.2rem; color: #fff; text-decoration: underline decoration-color: #32A041;">descobrir quem fez a merda da vez.</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Centralização do Botão (Colunas ajustadas)
    c1, c2, c3 = st.columns([1, 0.8, 1]) 
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

# TELA CHAT (STATUS ENCIMA DA CONVERSA)
elif st.session_state.fase in ['SOCIAL', 'REVELACAO']:
    nome = st.session_state.personagem_atual
    dados = PERSONAGENS[nome]
    
    # Lógica de Status
    status_txt = "🟢 Online"
    cor_status = "#32A041"
    if st.session_state.msg_no_turno > 3: 
        status_txt = "⚠️ Estressado"
        cor_status = "#ff4757"
    if len(st.session_state.chat_history) > 0 and st.session_state.chat_history[-1]['role'] == 'user':
        status_txt = "✍️ Digitando..."
        cor_status = "#eccc68"

    col_img, col_chat = st.columns([1, 2.5], gap="large")
    
    with col_img:
        # Nome e Subtítulo em cima da foto
        st.markdown(f"""
            <div style="text-align:center; margin-bottom: 10px;">
                <div class='char-name-title' style='color: {dados['cor']}; margin-bottom: 0px;'>{nome}</div>
                <div class='char-subtitle' style='margin-top: 0px;'>{dados['subtitulo']}</div>
            </div>
        """, unsafe_allow_html=True)
        
        try:
            st.image(dados['img'], use_container_width=True)
        except:
            st.error("Imagem não encontrada")
            
    with col_chat:
        # --- STATUS ALINHADO À DIREITA (EM CIMA DO CHAT) ---
        st.markdown(f"""
            <div style="text-align: right; margin-bottom: 5px; font-family: 'Montserrat'; font-weight: 600; font-size: 0.9rem; color: {cor_status}; letter-spacing: 1px;">
                {status_txt}
            </div>
        """, unsafe_allow_html=True)

        # Área de Chat
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
                
                # Atualiza para "Digitando" visualmente antes da resposta
                # (O Streamlit vai recarregar a página e mostrar o status "Digitando" definido lá em cima)
                time.sleep(0.1) 
                st.rerun() 

    # Lógica de Resposta (Fora do fluxo de renderização para pegar o rerun)
    if len(st.session_state.chat_history) > 0 and st.session_state.chat_history[-1]['role'] == 'user':
        with st.spinner(""): # Spinner invisível só pra segurar
            time.sleep(1.5) # Tempo pro usuário ler o "Digitando"
            prompt = get_system_prompt(nome, st.session_state.fase, st.session_state.msg_no_turno)
            
            resp = "..."
            if model:
                try:
                    last_user_msg = st.session_state.chat_history[-1]['content']
                    chat = model.start_chat(history=[])
                    resp = chat.send_message(f"SYSTEM: {prompt}\nUSER: {last_user_msg}").text
                except Exception as e:
                    resp = f"❌ Erro IA: {str(e)}"
            
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
    st.markdown(f"<div style='text-align:center; margin-bottom:20px; font-size:1.2rem;'>**OCORRIDO:** {st.session_state.caso_atual['texto']}</div>", unsafe_allow_html=True)
    
    # Caixa de seleção
    escolha = st.selectbox("Selecione o Culpado:", list(PERSONAGENS.keys()))
    
    # --- IMAGEM DO SUSPEITO CENTRALIZADA ---
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        try:
            # Mostra a foto do escolhido
            st.image(PERSONAGENS[escolha]['img'], use_container_width=True)
        except:
            st.error("Erro na imagem")
    # ---------------------------------------

    if st.button("ACUSAR", type="primary"):
        if escolha == st.session_state.caso_atual['culpado']:
            st.balloons()
            st.success("ACERTOU! O C5 está salvo.")
        else:
            st.error(f"ERROU! Foi o {st.session_state.caso_atual['culpado']}!")
            
        if st.button("JOGAR DE NOVO"):
            st.session_state.clear()
            st.rerun()



