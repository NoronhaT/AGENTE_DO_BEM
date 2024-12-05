import os
import re
import mimetypes
from dotenv import load_dotenv, find_dotenv
import streamlit as st
from openai import OpenAI, AssistantEventHandler

# Carregar as variáveis de ambiente
load_dotenv(find_dotenv())

# Inicializar o cliente OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Cache para inicializar o assistente
@st.cache_resource
def get_or_create_assistant():
    assistants = list(client.beta.assistants.list())
    assistant_name = "ASSISTENTE_LEI_DO_BEM"

    for assistant in assistants:
        if assistant.name == assistant_name:
            return assistant


# Cache para configurar e retornar o Vector Store
@st.cache_resource
def setup_vector_store_and_files():
    # Implemente a lógica da função de setup como no seu código original
    pass

# Cache para criar uma nova thread
@st.cache_resource
def create_thread():
    thread = client.beta.threads.create(
        messages=[
            {
                "role": "user",
                "content": "Você atender dúvidas voltadas a lei do bem, não entre em qualquer outro assunto fora desse escopo mesmo que o usuário peça."
                           "Sempre utilize seu banco de conhecimento interno para responder as perguntas. Seja educado, breve e direto."
            }
        ]
    )
    return thread

# Classe para manipular eventos do assistente
class EventHandler(AssistantEventHandler):
    def on_text_created(self, text) -> None:
        st.write(f"\nassistente > {text}", end="", flush=True)

    def on_tool_call_created(self, tool_call):
        st.write(f"\nassistente > {tool_call.type}\n", flush=True)

    def on_message_done(self, message) -> None:
        for content in message.content:
            if content.type == 'text':
                st.write(f"assistente > {content.text.value}")

# Inicialização
st.title("AGENTE LEI DO BEM IMBAT")
assistant = get_or_create_assistant()
vector_store = setup_vector_store_and_files()

thread = create_thread()

# Interface com o usuário
user_input = st.text_input("Você: ", "")

if st.button("Enviar"):
    if user_input:
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_input
        )
        with client.beta.threads.runs.stream(
                thread_id=thread.id,
                assistant_id=assistant.id,
                event_handler=EventHandler()
        ) as stream:
            stream.until_done()
