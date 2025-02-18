import streamlit as st
import requests
import uuid
import os
from dotenv import load_dotenv

print("Debug: Iniciando carregamento das variáveis de ambiente...")
# Carrega as variáveis de ambiente
load_dotenv()
print("Debug: Configurando página do Streamlit...")

# Configurações de página para melhor visualização e layout
st.set_page_config(
    page_title="Editor de Playbook e Diagrama",
    layout="wide"
)

print("Debug: Lendo valores dos webhooks do .env...")
# URLs para os três webhooks (Agente de Playbook, Agente BPMN e Agente de Mermaid)
PLAYBOOK_WEBHOOK_URL = os.getenv("PLAYBOOK_WEBHOOK_URL")  # Endpoint do Agente de Playbook
BPMN_WEBHOOK_URL = os.getenv("BPMN_WEBHOOK_URL")          # Endpoint do Agente BPMN (intermediário)
MERMAID_WEBHOOK_URL = os.getenv("MERMAID_WEBHOOK_URL")    # Endpoint do Agente de Mermaid

# Gera (ou recupera) um session_id único para cada sessão do Streamlit
if "session_id" not in st.session_state:
    st.session_state["session_id"] = str(uuid.uuid4())
    print(f"Debug: Gerando novo session_id: {st.session_state['session_id']}")
else:
    print(f"Debug: session_id já existente: {st.session_state['session_id']}")

# Inicializa variáveis de sessão
if "playbook_text" not in st.session_state:
    st.session_state["playbook_text"] = ""
    print("Debug: Inicializando playbook_text como string vazia.")

if "bpmn_text" not in st.session_state:
    st.session_state["bpmn_text"] = ""
    print("Debug: Inicializando bpmn_text como string vazia.")

if "mermaid_code" not in st.session_state:
    st.session_state["mermaid_code"] = ""
    print("Debug: Inicializando mermaid_code como string vazia.")

if "phase" not in st.session_state:
    st.session_state["phase"] = "playbook"  # Fases: "playbook" -> "bpmn" -> "mermaid"
    print("Debug: Definindo phase inicial como 'playbook'.")

# Histórico de mensagens do agente de Playbook
if "playbook_agent_messages" not in st.session_state:
    st.session_state["playbook_agent_messages"] = []
    print("Debug: Inicializando histórico de mensagens do Agente (Playbook).")

# Histórico de mensagens do agente BPMN (intermediário)
if "bpmn_agent_messages" not in st.session_state:
    st.session_state["bpmn_agent_messages"] = []
    print("Debug: Inicializando histórico de mensagens do Agente (BPMN).")

# Histórico de mensagens do agente de Mermaid
if "mermaid_agent_messages" not in st.session_state:
    st.session_state["mermaid_agent_messages"] = []
    print("Debug: Inicializando histórico de mensagens do Agente (Mermaid).")

# Título e exibição do session_id
st.title("Editor de Playbook e Diagrama – Fluxo em Três Etapas")
st.caption(f"Session ID atual: {st.session_state['session_id']}")

# Carregamos globalmente o script do Mermaid para garantir que ele estará disponível
st.markdown(
    """
    <script>
    (function() {
        var mermaidScript = document.createElement('script');
        mermaidScript.src = "https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js";
        mermaidScript.onload = function() {
            if (typeof mermaid !== 'undefined') {
                mermaid.initialize({ startOnLoad: true });
            }
        };
        document.head.appendChild(mermaidScript);
    })();
    </script>
    """,
    unsafe_allow_html=True
)

def reset_text_area():
    print("Debug: Resetando campo de texto do usuário...")
    st.session_state[st.session_state.playbook_input_key] = ""

def show_playbook_messages():
    """
    Exibe as mensagens do agente de Playbook acima da caixa de texto.
    """
    if st.session_state["playbook_agent_messages"]:
        st.markdown("### Mensagens do Agente (Playbook):")
        for msg in st.session_state["playbook_agent_messages"]:
            st.markdown(f"**Agente (Playbook)**: {msg}")

def show_bpmn_messages():
    """
    Exibe as mensagens do agente BPMN (intermediário) acima da caixa de texto.
    """
    if st.session_state["bpmn_agent_messages"]:
        st.markdown("### Mensagens do Agente (BPMN):")
        for msg in st.session_state["bpmn_agent_messages"]:
            st.markdown(f"**Agente (BPMN)**: {msg}")

def show_mermaid_messages_and_diagram():
    """
    Exibe as mensagens do agente de Mermaid + diagrama acima da caixa de texto.
    """
    if st.session_state["mermaid_agent_messages"]:
        st.markdown("### Mensagens do Agente (Mermaid):")
        for msg in st.session_state["mermaid_agent_messages"]:
            st.markdown(f"**Agente (Mermaid)**: {msg}")

    if st.session_state["mermaid_code"]:
        st.markdown("### Versão Atual do Diagrama:")
        st.components.v1.html(
            f"""
            <div class="mermaid">
            {st.session_state["mermaid_code"]}
            </div>
            <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
            <script>
            mermaid.initialize({{ startOnLoad: true }});
            </script>
            """,
            height=600,
            scrolling=True
        )
    else:
        st.info("Nenhum diagrama foi gerado ainda.")


# ----------------------------
# FASE 1: Conversa com Agente de Playbook
# ----------------------------
if st.session_state["phase"] == "playbook":
    print("Debug: Entrando na fase 'playbook'.")
    st.subheader("Fase 1: Validar e Refinar o Playbook")

    show_playbook_messages()

    if "playbook_input_key" not in st.session_state:
        st.session_state["playbook_input_key"] = "playbook_input"

    user_input_playbook = st.text_area(
        "Digite sua mensagem para o Agente de Playbook:",
        placeholder="Descreva seu processo ou responda ao Agente de Playbook...",
        key=st.session_state["playbook_input_key"],
        height=150
    )

    if st.button("Enviar para Agente de Playbook", key="send_to_playbook_agent"):
        print("Debug: Botão 'Enviar para Agente de Playbook' clicado.")
        print(f"Debug: user_input_playbook = {user_input_playbook}")
        if not user_input_playbook.strip():
            st.warning("Você precisa digitar alguma mensagem antes de enviar.")
        else:
            try:
                if not PLAYBOOK_WEBHOOK_URL:
                    st.error("PLAYBOOK_WEBHOOK_URL não foi configurado. Verifique o .env.")
                else:
                    payload = {
                        "chatInput": user_input_playbook,
                        "session_id": st.session_state["session_id"]
                    }
                    print(f"Debug: Payload para Agente de Playbook: {payload}")
                    response = requests.post(PLAYBOOK_WEBHOOK_URL, json=payload)
                    print(f"Debug: Resposta (status_code) do Agente de Playbook: {response.status_code}")
                    if response.status_code == 200:
                        data = response.json()
                        print(f"Debug: Conteúdo da resposta do Agente de Playbook: {data}")
                        agent_output = data.get("output", "")
                        st.session_state["playbook_agent_messages"].append(agent_output)
                        st.session_state["playbook_text"] = agent_output
                        st.success("Resposta do Agente de Playbook recebida e armazenada.")

                        reset_text_area()
                        st.rerun()
                    else:
                        st.error(f"Erro ao chamar o webhook do Agente de Playbook: {response.text}")
            except Exception as e:
                st.error(f"Ocorreu um erro ao chamar o Agente de Playbook: {e}")

        st.rerun()

    if st.button("Estrutura do Playbook Realizada (Ajustar Fluxo)"):
        print("Debug: Botão 'Estrutura do Playbook Realizada (Ajustar Fluxo)' clicado.")
        if not st.session_state["playbook_text"].strip():
            st.warning("O Playbook está vazio. Adicione conteúdo ou revise-o antes de enviar ao Agente BPMN.")
        else:
            try:
                if not BPMN_WEBHOOK_URL:
                    st.error("BPMN_WEBHOOK_URL não foi configurado. Verifique o .env.")
                else:
                    # Envia o conteúdo completo (playbook_text) para o Agente BPMN
                    payload = {
                        "chatInput": st.session_state["playbook_text"],
                        "session_id": st.session_state["session_id"]
                    }
                    print(f"Debug: Payload para Agente BPMN (inicial): {payload}")
                    response = requests.post(BPMN_WEBHOOK_URL, json=payload)
                    print(f"Debug: Resposta (status_code) do Agente BPMN: {response.status_code}")
                    if response.status_code == 200:
                        data = response.json()
                        # Adotamos o mesmo padrão: "output" para o texto retornado.
                        agent_output = data.get("output", "")
                        st.session_state["bpmn_agent_messages"].append(agent_output)
                        st.session_state["bpmn_text"] = agent_output

                        st.session_state["phase"] = "bpmn"
                        st.success("Retornando fluxo do Agente BPMN.")
                        st.rerun()
                    else:
                        st.error(f"Erro ao chamar o webhook do Agente BPMN: {response.text}")
            except Exception as e:
                st.error(f"Ocorreu um erro ao chamar o Agente BPMN: {e}")


# ----------------------------
# FASE 2: Conversa com Agente BPMN (Intermediário)
# ----------------------------
elif st.session_state["phase"] == "bpmn":
    st.subheader("Fase 2: Ajustar Fluxo (Agente BPMN)")

    # Exibe as mensagens do agente BPMN (igual ao 'playbook_agent_messages')
    show_bpmn_messages()

    user_input_bpmn = st.text_area(
        "Digite ajustes ou perguntas para o Agente BPMN:",
        key="bpmn_input",
        height=150,
        placeholder="Ex.: Refinar a etapa de aprovação, incluir evento intermediário, etc."
    )

    if st.button("Enviar para Agente BPMN"):
        if not user_input_bpmn.strip():
            st.warning("Digite alguma mensagem antes de enviar.")
        else:
            try:
                if not BPMN_WEBHOOK_URL:
                    st.error("BPMN_WEBHOOK_URL não foi configurado. Verifique o .env.")
                else:
                    payload = {
                        "chatInput": user_input_bpmn,
                        "session_id": st.session_state["session_id"]
                    }
                    response = requests.post(BPMN_WEBHOOK_URL, json=payload)
                    if response.status_code == 200:
                        data = response.json()
                        agent_output = data.get("output", "")
                        st.session_state["bpmn_agent_messages"].append(agent_output)
                        st.session_state["bpmn_text"] = agent_output

                        st.success("Fluxo BPMN atualizado.")
                        st.rerun()
                    else:
                        st.error(f"Erro ao atualizar fluxo BPMN: {response.text}")
            except Exception as e:
                st.error(f"Erro ao enviar ajustes ao Agente BPMN: {e}")

    # Botão para avançar (Agente Mermaid)
    if st.button("Pronto! Gerar/Editar Diagrama"):
        print("Debug: Botão 'Pronto! Gerar/Editar Diagrama' clicado (fase BPMN).")
        if not st.session_state["bpmn_text"].strip():
            st.warning("Não há texto retornado do Agente BPMN para gerar o diagrama.")
        else:
            st.session_state["phase"] = "mermaid"
            try:
                if not MERMAID_WEBHOOK_URL:
                    st.error("MERMAID_WEBHOOK_URL não foi configurado. Verifique o .env.")
                else:
                    # Enviamos todo o texto atual do BPMN para gerar o diagrama
                    payload = {
                        "chatInput": st.session_state["bpmn_text"],
                        "session_id": st.session_state["session_id"],
                        "user_message": "Gerar primeira versão do diagrama a partir do BPMN."
                    }
                    print(f"Debug: Payload para primeira versão do diagrama (Mermaid): {payload}")
                    response = requests.post(MERMAID_WEBHOOK_URL, json=payload)
                    print(f"Debug: Resposta (status_code) do Agente de Mermaid: {response.status_code}")
                    if response.status_code == 200:
                        data = response.json()
                        first_mermaid_code = data.get("output", "")
                        st.session_state["mermaid_code"] = first_mermaid_code
                        st.session_state["mermaid_agent_messages"].append("Primeira versão do diagrama gerada.")
                        st.success("Primeira versão do diagrama foi gerada com sucesso.")
                        st.write("Verifique abaixo o diagrama na próxima sessão.")
                        st.session_state["mermaid_initialized"] = True
                        st.rerun()
                    else:
                        st.error(f"Erro ao chamar o webhook de Mermaid: {response.text}")
            except Exception as e:
                st.error(f"Erro ao gerar a primeira versão do diagrama: {e}")


# ----------------------------
# FASE 3: Conversa com Agente de Mermaid
# ----------------------------
elif st.session_state["phase"] == "mermaid":
    st.subheader("Fase 3: Gerar e Ajustar Diagrama Mermaid")

    if "mermaid_initialized" not in st.session_state:
        st.session_state["mermaid_initialized"] = True
        if st.session_state["bpmn_text"].strip():
            if not MERMAID_WEBHOOK_URL:
                st.error("MERMAID_WEBHOOK_URL não foi configurado no .env.")
            else:
                try:
                    payload = {
                        "chatInput": st.session_state["bpmn_text"],
                        "session_id": st.session_state["session_id"],
                        "user_message": "Gerar primeira versão do diagrama a partir do BPMN."
                    }
                    response = requests.post(MERMAID_WEBHOOK_URL, json=payload)
                    if response.status_code == 200:
                        data = response.json()
                        st.session_state["mermaid_code"] = data.get("output", "")
                        st.session_state["mermaid_agent_messages"].append("Primeira versão do diagrama gerada.")
                        st.rerun()
                    else:
                        st.error(f"Erro ao gerar primeira versão do diagrama: {response.text}")
                except Exception as e:
                    st.error(f"Erro: {e}")
        else:
            st.info("Não há texto retornado do BPMN para gerar o diagrama.")

    show_mermaid_messages_and_diagram()

    user_input_mermaid = st.text_area(
        "Digite ajustes ou perguntas para o Agente de Mermaid:",
        key="mermaid_input",
        height=150,
        placeholder="Ex.: Adicione uma etapa de revisão após a segunda atividade..."
    )

    if st.button("Enviar para Agente de Mermaid"):
        if not user_input_mermaid.strip():
            st.warning("Digite alguma mensagem antes de enviar.")
        else:
            try:
                payload = {
                    "chatInput": st.session_state["bpmn_text"],
                    "session_id": st.session_state["session_id"],
                    "user_message": user_input_mermaid
                }
                response = requests.post(MERMAID_WEBHOOK_URL, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    st.session_state["mermaid_code"] = data.get("output", "")
                    st.session_state["mermaid_agent_messages"].append(
                        f"Diagrama atualizado com base no pedido: {user_input_mermaid}"
                    )
                    st.success("Diagrama atualizado.")
                    st.rerun()
                else:
                    st.error(f"Erro ao atualizar diagrama: {response.text}")
            except Exception as e:
                st.error(f"Erro ao enviar ajustes: {e}")

    if st.button("Finalizar diagrama"):
        st.markdown("### Conteúdo Final do Playbook, BPMN e Diagrama:")
        final_text = (
            "#### Playbook Final:\n"
            f"{st.session_state['playbook_text']}\n\n"
            "#### Conteúdo Final do BPMN:\n"
            f"{st.session_state['bpmn_text']}\n\n"
            "#### Diagrama Mermaid:\n"
            "```mermaid\n"
            f"{st.session_state['mermaid_code']}\n"
            "```"
        )
        st.markdown(final_text)
        st.success("Playbook, BPMN e diagrama finalizados.")