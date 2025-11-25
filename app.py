import streamlit as st
import random
import google.generativeai as genai

# --- 1. CONFIGURAÇÃO DE SEGURANÇA E CONEXÃO ---
# Tenta pegar a chave dos "Secrets" do Streamlit Cloud
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    # Se estiver rodando no seu PC e não tiver secrets configurado
    st.error("ERRO: Chave de API não encontrada! Configure os Secrets no Streamlit Cloud.")
    st.stop()

# Configura a biblioteca com a chave
genai.configure(api_key=api_key)

# Tenta conectar no modelo mais rápido e gratuito (Flash)
try:
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    # Fallback para o Pro se o Flash falhar
    model = genai.GenerativeModel('gemini-pro')

# --- 2. DADOS DOS PERSONAGENS ---
PERSONAGENS = {
    "PITOCO": {"img": "imagens/pitoco.jpg", "desc": "Agroboy Fake, Tóxico e Anão.", "cor": "#32CD32"},
    "SAMUEL": {"img": "imagens/samuel.jpg", "desc": "Rico, 'Nego Doce', Fala em 3ª pessoa.", "cor": "#FFD700"},
    "BRYAN": {"img": "imagens/bryan.jpg", "desc": "Gamer chorão, tenta ser cria.", "cor": "#4169E1"},
    "SALDANHA": {"img": "imagens/saldanha.jpg", "desc": "Veterano, Degenerado, Pai do grupo.", "cor": "#DC143C"},
    "MITSUKI": {"img": "imagens/mitsuki.jpg", "desc": "Otaku Brainrot, 'sus', desenhista.", "cor": "#FF69B4"},
    "MOISÉS": {"img": "imagens/moises.jpg", "desc": "Reservado, Explosivo, Odeia o Pitoco.", "cor": "#8A2BE2"},
    "CAMARADA": {"img": "imagens/camarada.jpg", "desc": "Brainrot Infantil, Medroso, 'Gramara'.", "cor": "#FF4500"},
    "TIFAEL": {"img": "imagens/tifael.jpg", "desc": "Agro-Coach, Tiozão, 'Jack'.", "cor": "#8B4513"},
    "JOAQUIM": {"img": "imagens/joaquim.jpg", "desc": "Político Agro, Pintocóptero.", "cor": "#2E8B57"},
    "INDIÃO": {"img": "imagens/indiao.jpg", "desc": "Sombra do Joaquim, 'Para de manjar'.", "cor": "#A0522D"},
}

# --- 3. CÉREBRO DA IA (SYSTEM PROMPT) ---
SYSTEM_PROMPT = """
VOCÊ É A ENGINE DE UM JOGO DE MISTÉRIO NO ALOJAMENTO C5.
LINGUAGEM: Gírias, palavrões, informalidade total.
CONTEXTO: O usuário está investigando um caso.

PERSONAGEM ATUAL: {personagem}
CASO DO DIA: {caso}
CULPADO REAL: {culpado} (NÃO REVELE DIRETAMENTE!)

REGRAS DE OURO:
1. Se você for o CULPADO: Minta, desconverse, acuse outro (Moisés culpa Pitoco, Pitoco culpa Tifael, etc).
2. Se for INOCENTE: Faça fofoca, zoação ou reclame.
3. NUNCA diga "Fui eu" de cara. O jogador tem que pressionar.
4. NUNCA diga o nome do culpado explicitamente (Regra do X-9).
5. PITOCO fala palavrão e de mulher. SAMUEL fala em 3ª pessoa. INDIÃO fala "Para de manjar".
"""

# --- 4. FUNÇÕES DO JOGO ---
def gerar_caso():
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
    fila = list(PERSONAGENS.keys())
    random.shuffle(fila)
    return {"texto": caso_texto, "culpado": culpado_nome, "fila": fila, "indice_fila": 0}

def chat_com_ia(personagem, mensagem_usuario):
    prompt_final = SYSTEM_PROMPT.format(
        personagem=personagem,
        caso=st.session_state.caso_atual['texto'],
        culpado=st.session_state.caso_atual['culpado']
    )
    # Geração Segura
    chat = model.start_chat(history=[])
    response = chat.send_message(f"System instructions: {prompt_final}\nUser message: {mensagem_usuario}")
    return response.text

# --- 5. INTERFACE ---
st.set_page_config(page_title="Mistério no C5", page_icon="🕵️", layout="centered")

st.markdown("""
<style>
    .stApp { background-color: #1a1a1a; color: white; }
    .chat-box { border-radius: 10px; padding: 10px; margin-bottom: 10px; }
    .user-msg { background-color: #333; text-align: right; border: 1px solid #555; }
    .bot-msg { background-color: #444; text-align: left; border: 1px solid #555; }
</style>
""", unsafe_allow_html=True)

if 'caso_atual' not in st.session_state:
    st.session_state.caso_atual = gerar_caso()
if 'historico_chat' not in st.session_state:
    st.session_state.historico_chat = []

st.title("🕵️ MISTÉRIO NO C5")
st.warning(f"🚨 OCORRIDO: {st.session_state.caso_atual['texto']}")

# Lógica da Fila
if st.session_state.caso_atual['indice_fila'] < len(PERSONAGENS):
    nome_atual = st.session_state.caso_atual['fila'][st.session_state.caso_atual['indice_fila']]
    dados = PERSONAGENS[nome_atual]
    
    col1, col2 = st.columns([1, 2])
    with col1:
        try:
            st.image(dados["img"], width=150)
        except:
            st.info(f"FOTO: {nome_atual}")
    with col2:
        st.subheader(f"Conversando com: {nome_atual}")
        st.caption(dados["desc"])
        
        chat_container = st.container()
        user_input = st.chat_input("Digite sua mensagem (ou 'tchau' para o próximo)...")
        
        if user_input:
            if user_input.lower() in ["tchau", "flw", "vaza", "sai fora", "proximo"]:
                st.session_state.historico_chat = []
                st.session_state.caso_atual['indice_fila'] += 1
                st.rerun()
            else:
                resp = chat_com_ia(nome_atual, user_input)
                st.session_state.historico_chat.append({"role": "user", "content": user_input})
                st.session_state.historico_chat.append({"role": "bot", "content": resp, "cor": dados["cor"]})

        with chat_container:
            for msg in st.session_state.historico_chat:
                if msg['role'] == 'user':
                    st.markdown(f"<div class='chat-box user-msg'>{msg['content']}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='chat-box bot-msg' style='border-left: 5px solid {msg['cor']}'><b>{nome_atual}:</b> {msg['content']}</div>", unsafe_allow_html=True)
else:
    st.success("🚫 FIM DOS INTERROGATÓRIOS!")
    escolha = st.selectbox("Quem foi o autista?", list(PERSONAGENS.keys()))
    if st.button("ACUSAR AGORA"):
        if escolha == st.session_state.caso_atual['culpado']:
            st.balloons()
            st.success(f"ACERTOU! Foi o {escolha}!")
        else:
            st.error(f"ERROU! O culpado era: {st.session_state.caso_atual['culpado']}")
        
        if st.button("Novo Caso"):
            st.session_state.caso_atual = gerar_caso()
            st.session_state.historico_chat = []
            st.rerun()
