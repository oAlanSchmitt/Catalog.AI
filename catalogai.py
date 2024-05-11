import streamlit as st
import google.generativeai as genai
from google.api_core.exceptions import GoogleAPIError  # Import corrected

# --- Configuração (oculte a chave API) ---
with open("api_key.txt") as f:
    api_key = f.read().strip()
genai.configure(api_key=api_key)

# --- Configuração do modelo ---
generation_config = {"candidate_count": 1, "temperature": 0.7}

# É altamente recomendável manter os filtros de segurança ativados!
safety_settings = {
    'HATE': 'BLOCK_NONE',
    'HARASSMENT': 'BLOCK_NONE',
    'SEXUAL' : 'BLOCK_NONE',
    'DANGEROUS' : 'BLOCK_NONE'
}

# Inicializando o modelo
model = genai.GenerativeModel(
    model_name='gemini-1.5-pro-latest',
    generation_config=generation_config,
    safety_settings=safety_settings,
)

# --- Instruções do sistema ---

# Instrução para identificar o gênero
identificar_genero_instruction = """
Você é um especialista em filmes, animes e séries.

Sua tarefa é identificar o gênero predominante em uma lista de títulos.

Responda apenas com o nome do gênero.

Por exemplo:

Títulos: The Walking Dead, Guerra Mundial Z, Zumbilândia
Gênero: Terror
"""

# Instrução para recomendar títulos
recomendar_instruction = """
Você é um assistente especializado em recomendar animes, filmes e séries.

Siga estas regras:

* **Recomendações únicas:** Nunca sugira o mesmo título que o usuário forneceu como entrada.
* **Diversidade:** Recomende um filme, um anime e uma série, um de cada.
* **Formato da resposta:** Separe as recomendações com "===" e use o seguinte formato para cada recomendação:
    * Tipo: [Filme, Anime ou Série]
    * Título: [Título]
    * Sinopse: [Breve sinopse]
    * Chances de Você Gostar: [Alta, Média ou Baixa]

Exemplo:

Informação: The Walking Dead, Guerra Mundial Z, Zumbilândia, John Wick, Mad Max
Resposta:
===
Tipo: Filme
Título: Army of the Dead
Sinopse: Um grupo de mercenários planeja um assalto a um cassino em Las Vegas durante um surto de zumbis.
Chances de Você Gostar: Alta
===
Tipo: Anime
Título: Highschool of the Dead
Sinopse: Um grupo de estudantes precisa lutar para sobreviver a um apocalipse zumbi.
Chances de Você Gostar: Média
===
Tipo: Série
Título: Kingdom
Sinopse: Um príncipe coreano precisa enfrentar uma misteriosa praga zumbi que está devastando o reino.
Chances de Você Gostar: Alta
"""

# --- Função para obter recomendações ---
def obter_recomendacoes(titulos):
    try:
        chat = model.start_chat(history=[]) 
        prompt_genero = f"Títulos: {', '.join(titulos)}\nGênero: "
        response_genero = chat.send_message(identificar_genero_instruction + prompt_genero)
        genero = response_genero.text.strip()

        prompt_recomendacoes = f"Informação: {', '.join(titulos)}.\nResposta:\n"
        response_recomendacoes = chat.send_message(recomendar_instruction + prompt_recomendacoes)
        return genero, response_recomendacoes.text.strip()
    except GoogleAPIError as e:
        if e.code == 429: 
            st.error(f"Erro na API do Gemini: {e}. Aguarde alguns instantes e tente novamente.")
        else:
            st.error(f"Erro na API do Gemini: {e}")
        return None, None

# --- Interface do Streamlit ---
st.title("✨ CatalogAI: Seu Guia Personalizado para Filmes, Animes e Séries ✨")
st.write("Conte-nos seus gostos e o CatalogAI usará inteligência artificial para te recomendar filmes, animes e séries que você vai amar! 🤖🍿")
st.write("**Experimente:** Digite 'Stranger Things, Naruto, Your Name' e veja o que o CatalogAI recomenda!")

if "titulos_input" not in st.session_state:
    st.session_state.titulos_input = ""

titulos_input = st.text_area(
    "Insira os títulos que você gosta, separados por vírgula:",
    value=st.session_state.titulos_input,
)
titulos = [t.strip() for t in titulos_input.split(",")]

if "recomendacoes" not in st.session_state:
    st.session_state.recomendacoes = None

if "genero" not in st.session_state:  # Inicializa o genero na session state
    st.session_state.genero = None

# Botão condicional
if not st.session_state.recomendacoes:
    if st.button("Obter Recomendações"):
        if all(titulos):
            with st.spinner("Pensando em recomendações incríveis..."):
                st.session_state.genero, recomendacoes_str = obter_recomendacoes(titulos)

            if st.session_state.genero and recomendacoes_str:
                st.session_state.recomendacoes = recomendacoes_str
                st.session_state.botao_visivel = False
        else:
            st.warning("Por favor, insira pelo menos um título.")

# Exibe as recomendações (se houver)
if st.session_state.recomendacoes:
    st.write(
        f"Ah, então você curte {st.session_state.genero}! 🤩 Saca só essas recomendações:"
    )
    recomendacoes = st.session_state.recomendacoes.split("===")
    for recomendacao in recomendacoes:
        if recomendacao.strip():
            linhas = recomendacao.strip().split("\n")
            tipo = linhas[0].split(":")[1].strip()
            titulo = linhas[1].split(":")[1].strip()
            sinopse = linhas[2].split(":")[1].strip()
            chances = linhas[3].split(":")[1].strip()

            st.markdown(f"## **{tipo}: {titulo}**")
            st.write(f"_{sinopse}_")
            st.write(f"**Chances de Você Gostar:** {chances}")

    # Botão para gerar novas sugestões
    if st.button("Gerar Novas Sugestões"):
        st.session_state.recomendacoes = None  # Limpa as recomendações anteriores
        st.experimental_rerun()  # Recarrega a página para gerar novas sugestões
else:
    st.warning("Por favor, insira pelo menos um título.")