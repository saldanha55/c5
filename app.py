import streamlit as st
import random
import google.generativeai as genai

# --- CONFIGURAÇÃO DA IA ---
# Para rodar localmente ou na nuvem, você precisa configurar sua API KEY
# No Streamlit Cloud, coloque em "Secrets" como GOOGLE_API_KEY
api_key = st.secrets["GOOGLE_API_KEY"] if "GOOGLE_API_KEY" in st.secrets else "COLE_SUA_API_KEY_AQUI_SE_RODAR_LOCAL"
genai.configure(api_key=api_key)

# Configuração do Modelo (Gemini Flash é rápido e grátis)
model = genai.GenerativeModel('gemini-1.5-flash-latest')
# --- LORE E DADOS DOS PERSONAGENS ---
PERSONAGENS = {
    "PITOCO": {"img": "imagens/pitoco.jpeg", "desc": "Agroboy Fake, Tóxico e Anão.", "cor": "#32CD32"},
    "SAMUEL": {"img": "imagens/samuel.jpeg", "desc": "Rico, 'Nego Doce', Fala em 3ª pessoa.", "cor": "#FFD700"},
    "BRYAN": {"img": "imagens/bryan.jpeg", "desc": "Gamer chorão, tenta ser cria.", "cor": "#4169E1"},
    "SALDANHA": {"img": "imagens/saldanha.jpeg", "desc": "Veterano, Degenerado, Pai do grupo.", "cor": "#DC143C"},
    "MITSUKI": {"img": "imagens/mitsuki.jpeg", "desc": "Otaku Brainrot, 'sus', desenhista.", "cor": "#FF69B4"},
    "MOISÉS": {"img": "imagens/moises.jpeg", "desc": "Reservado, Explosivo, Odeia o Pitoco.", "cor": "#8A2BE2"},
    "CAMARADA": {"img": "imagens/camarada.jpeg", "desc": "Brainrot Infantil, Medroso, 'Gramara'.", "cor": "#FF4500"},
    "TIFAEL": {"img": "imagens/tifael.jpeg", "desc": "Agro-Coach, Tiozão, 'Jack'.", "cor": "#8B4513"},
    "JOAQUIM": {"img": "imagens/joaquim.jpeg", "desc": "Político Agro, Pintocóptero.", "cor": "#2E8B57"},
    "INDIÃO": {"img": "imagens/indiao.jpeg", "desc": "Sombra do Joaquim, 'Para de manjar'.", "cor": "#A0522D"},
}

# --- SYSTEM PROMPT (A CÉREBRO DO JOGO) ---
SYSTEM_PROMPT = """
VOCÊ É A ENGINE DE UM JOGO DE MISTÉRIO NO ALOJAMENTO C5.
LINGUAGEM: Gírias, palavrões, informalidade total.
CONTEXTO: O usuário está investigando um caso.

PERSONAGEM ATUAL: {personagem}
CASO DO DIA: {caso}
CULPADO REAL: {culpado} (NÃO REVELE DIRETAMENTE!)

REGRAS DE INTERPRETAÇÃO:
1. Se você for o CULPADO: Minta, desconverse, acuse outro (Moisés culpa Pitoco, Pitoco culpa Tifael, etc).
2. Se for INOCENTE: Faça fofoca, zoação ou reclame.
3. NUNCA diga "Fui eu" de cara. O jogador tem que pressionar.
4. NUNCA diga o nome do culpado explicitamente (Regra do X-9). Dê dicas baseadas na personalidade.
5. PITOCO fala palavrão e de mulher. SAMUEL fala em 3ª pessoa ("O Samuel acha..."). INDIÃO fala "Para de manjar".
"""

# --- FUNÇÕES DO JOGO ---

def gerar_caso():
    # Lista de casos genéricos para a IA sortear e preencher
    casos_base = [
        "Alguém entupiu a privada com uma peça de roupa.",
        "Sumiram 50 reais que estavam em cima da mesa.",
        "Alguém desenhou obscenidades na porta do guarda-roupa.",
        "Apareceu um cheiro insuportável vindo de baixo de uma cama.",
        "Quebraram o ventilador e esconderam os pedaços.",
        "Alguém trouxe uma galinha viva pro quarto e ela fugiu."
    ]
    caso_texto = random.choice(casos_base)
    culpado_nome = random.choice(list(PERSONAGENS.keys()))
    
    # Embaralha a ordem de interrogatório
    fila = list(PERSONAGENS.keys())
    random.shuffle(fila)
    
    return {"texto": caso_texto, "culpado": culpado_nome, "fila": fila, "indice_fila": 0}

def chat_com_ia(personagem, mensagem_usuario):
    # Monta o prompt
    prompt_final = SYSTEM_PROMPT.format(
        personagem=personagem,
        caso=st.session_state.caso_atual['texto'],
        culpado=st.session_state.caso_atual['culpado']
    )
    
    chat = model.start_chat(history=[])
    response = chat.send_message(f"System: {prompt_final}\nUser: {mensagem_usuario}")
    return response.text

# --- INTERFACE (STREAMLIT) ---

st.set_page_config(page_title="Mistério no C5", page_icon="🕵️", layout="centered")

# CSS para deixar bonito (Estilo Dark/Gamer)
st.markdown("""
<style>
    .stApp { background-color: #1a1a1a; color: white; }
    .chat-box { border-radius: 10px; padding: 10px; margin-bottom: 10px; }
    .user-msg { background-color: #333; text-align: right; }
    .bot-msg { background-color: #444; text-align: left; }
    h1 { color: #ff4b4b; text-align: center; font-family: 'Courier New', monospace; }
</style>
""", unsafe_allow_html=True)

# Inicialização do Estado
if 'caso_atual' not in st.session_state:
    st.session_state.caso_atual = gerar_caso()
if 'historico_chat' not in st.session_state:
    st.session_state.historico_chat = []
if 'troca_personagem' not in st.session_state:
    st.session_state.troca_personagem = False

# Cabeçalho
st.title("🕵️ MISTÉRIO NO C5")
st.warning(f"🚨 OCORRIDO: {st.session_state.caso_atual['texto']}")

# Lógica da Fila de Personagens
if st.session_state.caso_atual['indice_fila'] < len(PERSONAGENS):
    nome_atual = st.session_state.caso_atual['fila'][st.session_state.caso_atual['indice_fila']]
    dados_personagem = PERSONAGENS[nome_atual]
    
    # Exibe Imagem e Nome
    col1, col2 = st.columns([1, 2])
    with col1:
        # Tenta carregar imagem, se não tiver usa um placeholder
        try:
            st.image(dados_personagem["img"], caption=nome_atual, width=150)
        except:
            st.info(f"FOTO: {nome_atual}") # Placeholder se não tiver a imagem na pasta
            
    with col2:
        st.subheader(f"Conversando com: {nome_atual}")
        st.caption(dados_personagem["desc"])
        
        # Área de Chat
        chat_container = st.container()
        
        # Input do Usuário
        user_input = st.chat_input("Mande o papo (digite 'tchau' para o próximo)...")
        
        if user_input:
            # Verifica se o usuário quer sair
            if user_input.lower() in ["tchau", "flw", "vaza", "sai fora", "proximo"]:
                st.session_state.historico_chat = [] # Limpa chat para o próximo
                st.session_state.caso_atual['indice_fila'] += 1
                st.rerun()
            else:
                # Gera resposta da IA
                resposta = chat_com_ia(nome_atual, user_input)
                st.session_state.historico_chat.append({"role": "user", "content": user_input})
                st.session_state.historico_chat.append({"role": "bot", "content": resposta, "cor": dados_personagem["cor"]})

        # Renderiza Histórico
        with chat_container:
            for msg in st.session_state.historico_chat:
                if msg['role'] == 'user':
                    st.markdown(f"<div class='chat-box user-msg'>Você: {msg['content']}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='chat-box bot-msg' style='border-left: 5px solid {msg['cor']}'><b>{nome_atual}:</b> {msg['content']}</div>", unsafe_allow_html=True)

else:
    # FIM DA FILA - HORA DO VEREDITO
    st.success("🚫 FIM DOS INTERROGATÓRIOS!")
    st.write("Quem foi o autista que fez isso?")
    
    escolha = st.selectbox("Escolha o culpado:", list(PERSONAGENS.keys()))
    
    if st.button("ACUSAR AGORA"):
        if escolha == st.session_state.caso_atual['culpado']:
            st.balloons()
            st.success(f"BOA! Foi o {escolha} mesmo! O C5 está salvo (por enquanto).")
        else:
            st.error(f"ERROU FEIO! Não foi o {escolha}. O culpado era o {st.session_state.caso_atual['culpado']}!")
        
        if st.button("Novo Caso"):
            st.session_state.caso_atual = gerar_caso()
            st.session_state.historico_chat = []

            st.rerun()

