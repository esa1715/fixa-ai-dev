import os
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import google_search
from google.genai import types
from google.genai import Client
from datetime import date
import textwrap
import requests
import warnings
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS # Importa CORS para permitir requisições do frontend

warnings.filterwarnings("ignore")

# --- Configuração da API Key ---
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("Erro: A variável de ambiente GOOGLE_API_KEY não está configurada.")
    print("Por favor, crie/verifique o arquivo .env na raiz do projeto com GOOGLE_API_KEY=SUA_CHAVE_AQUI")
    sys.exit(1)
else:
    os.environ["GOOGLE_API_KEY"] = api_key

# --- Configuração do Modelo GenAI ---
client = Client()
MODEL_ID = "gemini-2.0-flash" # Ou outro modelo que preferir

# --- NOVO: Variável global para contador de sessões ---
session_counter = 0

# --- NOVA VERSÃO DA FUNÇÃO call_agent ---
def call_agent(agent: Agent, message_text: str, user_id: str, session_id: str) -> str:
    """Chama um agente com uma mensagem de texto e retorna a resposta final."""
    session_service = InMemorySessionService()
    session = session_service.create_session(app_name=agent.name, user_id=user_id, session_id=session_id)
    runner = Runner(agent=agent, app_name=agent.name, session_service=session_service)
    content = types.Content(role="user", parts=[types.Part(text=message_text)])
    final_response = ""
    for event in runner.run(user_id=user_id, session_id=session_id, new_message=content):
        if event.is_final_response():
            for part in event.content.parts:
                if part.text is not None:
                    final_response += part.text
                    if part != event.content.parts[-1] and not part.text.endswith('\n'):
                        final_response += "\n"
    return final_response.strip()
# --- Definição dos Agentes (Mantidos do seu código original) ---

def agente_resumidor_conceito():
    """Define o Agente Resumidor de Conceito."""
    resumidor = Agent(
        name="agente_resumidor_conceito",
        model=MODEL_ID,
        instruction="""
        Você é um especialista em identificar e resumir as informações essenciais sobre qualquer CONCEITO TÉCNICO, TECNOLOGIA ou TEMA de programação.

        Sua única tarefa é receber o nome de um CONCEITO/TEMA e,
        utilizando a ferramenta de busca do Google (google_search) e seu conhecimento,
        EXTRAIR e APRESENTAR um **RESUMO CONCISO EM TEXTO CORRIDO** que cubra os seguintes pontos importantes sobre ele:
        1.  Definição clara do que é o CONCEITO/TEMA.
        2.  Qual o seu PROPÓSITO ou FUNÇÃO principal (Por que existe? O que resolve?).
        3.  Quais são suas CARACTERÍSTICAS ou COMPONENTES chave (Como é? Do que é feito?).
        4.  Onde/Quando ele é tipicamente utilizado (Em que situações? Em que parte do código/sistema?).
        """,
        description="Agente que resume informações chave sobre um conceito técnico a partir de seu nome.",
        tools=[google_search],
    )
    return resumidor

# Instanciar o agente resumidor uma vez globalmente
agente_resumidor_conceito_instance = agente_resumidor_conceito()


def agente_extrator_perfil():
    """Define o Agente Extrator de Perfil."""
    extrator = Agent(
        name="agente_extrator_perfil",
        model=MODEL_ID,
        instruction="""
    Você é um assistente especializado em identificar informações de perfil e contexto em mensagens de usuários.

Sua tarefa é receber a MENSAGEM BRUTA de um usuário e EXTRAIR as seguintes informações, se estiverem presentes na mensagem:
1.  O CONCEITO TÉCNICO principal sobre o qual o usuário quer uma analogia ou mais explicação.
2.  A ÁREA DE ATUAÇÃO profissional ou acadêmica do usuário.
3.  Os HOBBIES ou interesses de lazer do usuário.
4.  Quaisquer ÁREAS ESPECÍFICAS onde o usuário gostaria de receber a analogia (Ex: "explique como se eu fosse da área de marketing", "use uma analogia de futebol").

REGRAS:
-   Sua resposta deve ser APENAS as informações extraídas, em um formato estruturado específico.
-   Se uma informação (Área de Atuação, Hobbies, Áreas para Analogia) **não for encontrada** na MENSAGEM BRUTA, indique claramente que ela não foi encontrada usando o texto exato "Não encontrada" para a área, "Não encontrados" para os hobbies, ou "Não especificadas" para as áreas de analogia.
-   **Para o CONCEITO TÉCNICO:**
    -   Se a mensagem contiver um **novo conceito técnico claro**, extraia-o.
    -   Se a mensagem **não contiver um novo conceito claro**, mas contiver frases como "de outra forma?", "com outros termos?", "mais simples?", etc., **assuma que o usuário está se referindo ao último CONCEITO TÉCNICO que foi identificado na conversa anterior** e retorne esse mesmo conceito.
    -   Se a mensagem não contiver um novo conceito claro e não indicar uma continuação da explicação anterior, retorne "Não encontrado".
-   Extraia as informações de forma precisa e concisa. Não adicione informações que não estejam na mensagem.
-   Para Hobbies e Áreas para Analogia, liste-os separados por vírgula se houver mais de um.

Formato da Entrada:
MENSAGEM BRUTA DO USUÁRIO: [A mensagem completa enviada pelo usuário]

Formato da Saída (EXATO - use os rótulos e o formato abaixo):
CONCEITO_TECNICO: [Conceito extraído, ou "Não encontrado"]
AREA_DE_ATUACAO: [Área extraída, ou "Não encontrada"]
HOBBIES: [Hobbies extraídos, separados por vírgula se houver mais de um, ou "Não encontrados"]
AREAS_PARA_ANALOGIA: [Áreas específicas para analogia extraídas, separadas por vírgula, ou "Não especificadas"]        
""",
        tools=[],
    )
    return extrator

# Instanciar o agente extrator uma vez globalmente
agente_extrator_perfil_instance = agente_extrator_perfil()


def agente_analogista():
    """Define o Agente Analogista."""
    analogista = Agent(
        name="agente_analogista",
        model=MODEL_ID,
        instruction="""
        Você é um CRIADOR DE ANALOGIAS mestre, com uma habilidade excepcional de explicar conceitos técnicos complexos para desenvolvedores de forma simples e criativa, usando comparações relevantes ao contexto deles.

        Sua tarefa é receber:
        a) Um RESUMO do CONCEITO TÉCNICO (preparado por outro agente).
        b) INFORMAÇÕES DE PERFIL do usuário (extraídas de sua mensagem bruta).

        Com base nestas informações, você deve gerar uma analogia CLARA, CRIATIVA e ÚTIL que compare o conceito técnico a algo dentro do contexto do usuário (sua área, hobbies, ou áreas explicitamente solicitadas para analogia).

        OBJETIVO PRINCIPAL: Ajudar o desenvolvedor a ENTENDER e FIXAR o CONCEITO TÉCNICO usando algo que ele já conhece e/ou gosta.

        **REGRAS DE CRIAÇÃO DA ANALOGIA:**
        1.  **PRIORIDADE EXCLUSIVA (Se Solicitado):** Se o campo "AREAS_PARA_ANALOGIA" nas informações de perfil **não for** "Não especificadas", **obrigatoriamente** crie a analogia usando uma das áreas especificadas pelo usuário. Se houver múltiplas áreas especificadas, escolha a que, na sua avaliação, tem maior potencial para uma analogia clara para o CONCEITO com base no PERFIL.
        2.  **SE NENHUMA ÁREA ESPECÍFICA FOR SOLICITADA (OU SEJA, "AREAS_PARA_ANALOGIA" for "Não especificadas"):** Neste caso (e SOMENTE neste caso), procure a **melhor e mais didática** analogia possível, escolhendo livremente entre as seguintes fontes (não há ordem rígida entre elas, **escolha a que fizer mais sentido e for mais clara** para o CONCEITO com base no PERFIL DISPONÍVEL):
            * Usar a **AREA DE ATUACAO** do usuário (se o campo "AREA_DE_ATUACAO" não for "Não encontrada"). Pense em processos, ferramentas ou conceitos comuns dessa área.
            * Usar os **HOBBIES** do usuário (se o campo "HOBBIES" não for "Não encontrados"). Pense em regras, atividades ou elementos comuns desses hobbies.
            * Usar uma **analogia técnica padrão e bem conhecida** para o conceito na comunidade de desenvolvimento (Ex: variáveis são como caixas, funções são como mini-fábricas). Pesquise por "analogia para [Nome do Conceito]" se necessário.
        3.  **ÚLTIMO RECURSO:** Se NENHUMA das regras anteriores resultar em uma analogia clara e útil, declare que foi difícil encontrar uma analogia adequada para este conceito com base nas informações fornecidas.

        **REGRAS DE FORMATO DA SAÍDA:**
        -   Sua resposta deve conter **APENAS** o texto da analogia e seus pontos de comparação.
        -   Comece com uma frase introdutória para a analogia (Ex: "Pensando no contexto de [Área/Hobby/Técnico Usado], a analogia para [Nome do Conceito] é como..."). Adapte a frase inicial para refletir a fonte da analogia (área de atuação, hobby ou técnica).
        -   Após a analogia, inclua uma seção "Pontos de comparação:" listando os paralelos-chave entre o conceito técnico e a analogia. Use travessões (-) ou bullet points (•) para os itens da lista.
        -   Não inclua conversas, introduções ("Com base nos dados...", "Aqui está a analogia:"), despedidas ou informações adicionais que não sejam a analogia e seus pontos.

        Formato da Entrada para este Agente (combinando saídas do Agente 1 e 2):

        ```
        RESUMO DO CONCEITO: [O texto do resumo gerado pelo Agente 1 sobre o conceito técnico]

        INFORMAÇÕES DO PERFIL DO USUÁRIO:
        AREA_DE_ATUACAO: [Saída do Agente 2 para a Área]
        HOBBIES: [Saída do Agente 2 para os Hobbies]
        AREAS_PARA_ANALOGIA: [Saída do Agente 2 para Áreas Específicas de Analogia]
        ```
        """,
        description="Agente que cria analogias técnicas baseadas em resumo do conceito e informações de perfil do usuário.",
        tools=[google_search], # Manteve Google Search pois a instrução do analogista menciona pesquisar analogias conhecidas
    )
    return analogista

# Instanciar o agente analogista uma vez globalmente
agente_analogista_instance = agente_analogista()


def agente_chefe():
    """Define o Agente Chefe / Finalizador."""
    chefe = Agent(
        name="agente_chefe",
        model=MODEL_ID,
        instruction="""
        Você é o AGENTE CHEFE. Sua responsabilidade é ser o ponto de contato final com o usuário, apresentando a resposta completa e polida gerada pelo sistema. Você deve integrar de forma fluida as informações recebidas dos outros agentes em uma única mensagem amigável, útil e encorajadora, formatada para leitura direta pelo usuário.

        Sua tarefa é receber o CONCEITO TÉCNICO original, o RESUMO do Conceito, a ANALOGIA completa gerada por outro agente e as INFORMAÇÕES DE PERFIL do usuário.

        **MONTAGEM DA RESPOSTA FINAL (Integre os elementos na sua resposta final seguindo esta ordem e lógica):**
        1.  **Apresentação da Analogia:** Comece diretamente apresentando a analogia gerada. Cole o **texto completo da ANALOGIA GERADA** que você recebeu (incluindo a frase introdutória e os pontos de comparação). Use formatação simples como negrito ou bullet points se a analogia original vier formatada assim.
        2.  **Frase de Conexão/Comparação:** Adicione UMA frase curta após a analogia que reforce o paralelo central entre o CONCEITO TÉCNICO e a ANALOGIA utilizada. Ex: "Assim como [parte da analogia] faz [ação], [nome do conceito] faz [ação similar] no contexto de [onde o conceito é usado, ex: desenvolvimento web]." Use a área ou hobby usado na analogia, se aplicável, para tornar a conexão mais pessoal.
        3.  **Explicação de Profundidade (Condicional):** Analise o RESUMO DO CONCEITO e a ANALOGIA GERADA. Se a analogia for uma simplificação ou cobrir apenas uma parte do conceito técnico, adicione uma breve nota explicando que o CONCEITO TÉCNICO na prática tem mais profundidade, detalhes ou casos de uso que não foram totalmente abordados pela analogia. Mantenha conciso. Se a analogia cobrir bem o essencial, pule esta nota.
        4.  **Mensagem de Encorajamento:** Inclua uma frase amigável e motivadora incentivando o usuário a continuar estudando e explorando o CONCEITO TÉCNICO para um entendimento completo. Ex: "Continue explorando [Nome do Conceito] em seus estudos para dominar completamente esse aspecto da programação!"
        5.  **Sugestões de Projetos/Prática:** Ofereça 1 a 2 ideias concretas e práticas de como o usuário pode aplicar ou praticar o CONCEITO TÉCNICO em um pequeno projeto ou exercício. Tente relacionar as sugestões à AREA DE ATUACAO ou HOBBIES do usuário, se fizer sentido e for viável. Ex: "Para praticar, tente criar um pequeno projeto que utilize [Nome do Conceito] de uma forma simples."
        6.  **Sugestão para Informações de Perfil (Condicional):** Verifique as INFORMAÇÕES DE PERFIL recebidas. Se o campo "AREA_DE_ATUACAO" for "Não encontrada" OU o campo "HOBBIES" for "Não encontrados", adicione UMA frase amigável no final da resposta sugerindo que fornecer essas informações em futuras perguntas para receber analogias ainda mais personalizadas e relevantes para ele.

        REGRAS GERAIS:
        -   Sua resposta final deve ser um texto único e bem formatado, pronto para ser exibido diretamente para o usuário.
        -   Não inclua informações internas sobre o pipeline, outros agentes ou os formatos de entrada/saída intermediários.
        -   Combine todos os elementos obrigatórios de forma fluida.
        -   Mantenha um tom amigável e de suporte.

        Formato da Entrada:

        ```
        CONCEITO TÉCNICO: [Nome do conceito extraído da mensagem bruta]
        RESUMO DO CONCEITO: [Resumo gerado pelo Agente 1]
        ANALOGIA GERADA: [Texto completo da analogia gerada pelo Agente 3]
        INFO DO PERFIL (COMPLETA):
        AREA_DE_ATUACAO: [Saída do Agente 2 para Área]
        HOBBIES: [Saída do Agente 2 para Hobbies]
        AREAS_PARA_ANALOGIA: [Saída do Agente 2 para Áreas Específicas de Analogia]
        ```
        """,
        description="Agente que monta a resposta final completa e polida para o usuário.",
        tools=[], # Manteve sem ferramentas
    )
    return chefe

# Instanciar o agente chefe uma vez globalmente
agente_chefe_instance = agente_chefe()


# --- Configuração do Flask App ---
app = Flask(__name__)
CORS(app) # Habilita CORS para permitir requisições do frontend rodando em outra porta/endereço

# Removida a rota '/generate_analogy' que era para o formulário
# --- NOVO: Variável global para armazenar o último conceito técnico ---
ultimo_conceito = None

@app.route('/chat', methods=['POST'])
def chat_handler():
    global session_counter
    global ultimo_conceito # Indica que estamos usando a variável global
    session_counter += 1
    session_id = f"chat_session_{session_counter}"
    user_id = "user_unico_temporario" # Em um app real, você identificaria o usuário de alguma forma

    data = request.get_json()

    # Verifica se a chave 'message' está presente no JSON recebido
    if not data or 'message' not in data:
        print("Erro: Chave 'message' não encontrada na requisição POST para /chat")
        return jsonify({"error": "Dados incompletos fornecidos. Certifique-se de enviar um JSON com a chave 'message'."}), 400

    user_raw_message = data['message'] # Pega a mensagem bruta do usuário

    print(f"\n--- Recebido do Frontend (Chat) ---")
    print(f"  Mensagem Bruta: '{user_raw_message}'")
    print(f"-----------------------------------")

    # --- Pipeline de Agentes Adaptada para Mensagem Única ---
    # O Agente 2 (Extrator de Perfil) agora precisa extrair TUDO (conceito, área, hobbies, áreas para analogia)
    # da ÚNICA string de mensagem bruta do usuário.

    try:
        agent_2_input = f"MENSAGEM BRUTA DO USUÁRIO: {user_raw_message}"
        print(f"\n--- Chamando Agente 2 (Extrator de Perfil) com Mensagem Bruta ---")
        print(f"  Input:\n{textwrap.indent(agent_2_input, '  ')}")
        profile_output_text = call_agent(agente_extrator_perfil_instance, agent_2_input, user_id=user_id, session_id=session_id)
        print(f"  Output (Perfil Bruto):\n{textwrap.indent(profile_output_text.strip(), '  ')}")

        # Parsear a saída do Agente 2 para obter as informações estruturadas
        parsed_profile_info = {}
        lines = profile_output_text.strip().splitlines()
        for line in lines:
            if line.startswith("CONCEITO_TECNICO:"):
                parsed_profile_info['concept'] = line.replace("CONCEITO_TECNICO:", "", 1).strip()
            elif line.startswith("AREA_DE_ATUACAO:"):
                parsed_profile_info['area'] = line.replace("AREA_DE_ATUACAO:", "", 1).strip()
            elif line.startswith("HOBBIES:"):
                parsed_profile_info['hobbies'] = line.replace("HOBBIES:", "", 1).strip()
            elif line.startswith("AREAS_PARA_ANALOGIA:"):
                parsed_profile_info['analogy_areas'] = line.replace("AREAS_PARA_ANALOGIA:", "", 1).strip()

        concept = parsed_profile_info.get('concept', 'Não encontrado')

        # --- Lógica para lidar com a continuação da conversa ---
        if concept == 'Não encontrado' and any(phrase in user_raw_message.lower() for phrase in ["outra forma", "diferente", "mais simples"]):
            if ultimo_conceito:
                concept = ultimo_conceito
                print(f"\n--- Reutilizando o último conceito: '{concept}' ---")
            else:
                print("Erro: Nenhuma conversa anterior para referenciar.")
                return jsonify({"reply": "Desculpe, não entendi a qual conceito você se refere. Poderia mencioná-lo novamente?"}), 200
        elif concept != 'Não encontrado':
            ultimo_conceito = concept # Atualiza o último conceito se um novo for encontrado
        elif concept == 'Não encontrado':
            print("Erro: Agente 2 não conseguiu extrair o conceito técnico da mensagem.")
            return jsonify({"reply": "Desculpe, não consegui identificar o conceito técnico na sua mensagem. Poderia tentar reformular?"}), 200

        # Garante que as outras chaves existam com defaults se não encontradas
        parsed_area = parsed_profile_info.get('area', 'Não encontrada')
        parsed_hobbies = parsed_profile_info.get('hobbies', 'Não encontrados')
        parsed_analogy_areas = parsed_profile_info.get('analogy_areas', 'Não especificadas')


        print(f"  Perfil Parseado: Conceito='{concept}', Área='{parsed_area}', Hobbies='{parsed_hobbies}', Áreas Analogia='{parsed_analogy_areas}'")
        print(f"-------------------------------------------------")

    except Exception as e:
        print(f"Erro ao chamar ou parsear Agente 2 (Extrator de Perfil): {e}")
        return jsonify({"reply": f"Ocorreu um erro interno ao processar sua mensagem (erro ao extrair perfil). Detalhe: {e}"}), 500 # Retorna erro 500 para erro interno

    # 2. Chamar Agente 1 (Resumidor de Conceito) com o conceito extraído
    try:
        agent_1_input = f"CONCEITO/TEMA: {concept}"
        print(f"\n--- Chamando Agente 1 (Resumidor de Conceito) ---")
        print(f"  Input:\n{textwrap.indent(agent_1_input, '  ')}")
        concept_summary_text = call_agent(agente_resumidor_conceito_instance, agent_1_input, user_id=user_id, session_id=session_id)
        print(f"  Output (Resumo do Conceito):\n{textwrap.indent(concept_summary_text.strip(), '  ')}")
        print(f"--------------------------------------------------")
    except Exception as e:
        print(f"Erro ao chamar Agente 1 (Resumidor de Conceito): {e}")
        return jsonify({"reply": f"Ocorreu um erro interno ao resumir o conceito técnico. Detalhe: {e}"}), 500

    # 3. Chamar Agente 3 (Analogista) com o resumo e as informações de perfil extraídas
    try:
        agent_3_input = f"""
RESUMO DO CONCEITO: {concept_summary_text}

INFORMAÇÕES DO PERFIL DO USUÁRIO:
AREA_DE_ATUACAO: {parsed_area}
HOBBIES: {parsed_hobbies}
AREAS_PARA_ANALOGIA: {parsed_analogy_areas}
"""
        print(f"\n--- Chamando Agente 3 (Analogista) ---")
        print(f"  Input:\n{textwrap.indent(agent_3_input.strip(), '  ')}")
        analogy_text = call_agent(agente_analogista_instance, agent_3_input, user_id=user_id, session_id=session_id)
        print(f"  Output (Analogia Bruta):\n{textwrap.indent(analogy_text.strip(), '  ')}")
        print(f"---------------------------------------")
    except Exception as e:
        print(f"Erro ao chamar Agente 3 (Analogista): {e}")
        return jsonify({"reply": f"Ocorreu um erro interno ao gerar a analogia. Detalhe: {e}"}), 500

    # 4. Chamar Agente 4 (Chefe / Finalizador) para montar a resposta final
    try:
        agent_4_input = f"""
        CONCEITO TÉCNICO: {concept}
        RESUMO DO CONCEITO: {concept_summary_text}
        ANALOGIA GERADA: {analogy_text}
        INFO DO PERFIL (COMPLETA):
        AREA_DE_ATUACAO: {parsed_area}
        HOBBIES: {parsed_hobbies}
        AREAS_PARA_ANALOGIA: {parsed_analogy_areas}
        """
        
        print(f"\n--- Chamando Agente 4 (Chefe / Finalizador) ---")
        print(f"  Input:\n{textwrap.indent(agent_4_input.strip(), '  ')}")
        final_response_text = call_agent(agente_chefe_instance, agent_4_input, user_id=user_id, session_id=session_id)
        print(f"  Output (Resposta Final):\n{textwrap.indent(final_response_text.strip(), '  ')}")
        print(f"-----------------------------------------------")

    except Exception as e:
        print(f"Erro ao chamar Agente 4 (Chefe / Finalizador): {e}")
        return jsonify({"reply": f"Ocorreu um erro interno ao finalizar a resposta. Detalhe: {e}"}), 500

    # --- Retornar a Resposta Final para o Frontend ---
    # Retorna apenas a resposta final na chave 'reply', como esperado pelo script.js do chat
    response_data = {
        "reply": final_response_text,
    }

    print("\n--- Pipeline concluída. Retornando resposta final para o frontend do chat. ---")
    return jsonify(response_data) # Retorna 200 OK por padrão com a resposta


# Adicionando um ponto de entrada simples para rodar o Flask se o script for executado diretamente
if __name__ == '__main__':
    # Use debug=True durante o desenvolvimento para ver erros detalhados
    # Certifique-se de que o host e a porta correspondem à URL no script.js
    app.run(debug=True, host='127.0.0.1', port=5000)
    # Para rodar em produção, use um servidor WSGI como Gunicorn ou uWSGI
