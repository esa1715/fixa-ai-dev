<p align="center">
  <img src="https://raw.githubusercontent.com/esa1715/fixa-ai-dev/refs/heads/main/fixai-logo.png" alt="Logo do FIXA AI DEV" width="500"/> </p>

# FIXA AI DEV 🚀

> Dificuldade para aprender um conceito Tech? 🤔 Conheça o Fixa AI DEV!
> Em um chat interativo, a IA usa múltiplos agentes e consegue criar analogias até mesmo personalizadas para que você encontre uma conexão 🤝 com sua área e/ou seus hobbies. Além disso, ela te dá ideias de projetos 💡 para que você possa praticar e aprender de verdade. Tudo isso para tentar lhe ajudar a entender e FIXAR conceitos o mais rápido possível! 🚀

## Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Funcionalidades Principais](#funcionalidades-principais)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Instalação](#instalação)
  - [Pré-requisitos](#pré-requisitos)
  - [Configuração](#configuração)
- [Como Usar](#como-usar)
- [Licença](#licença)
- [Autor](#autor)

## Sobre o Projeto

O FIXA AI DEV nasceu da necessidade de superar um desafio comum na jornada de aprendizado em tecnologia: a dificuldade inicial em **entender conceitos complexos** e, mais importante, a capacidade de **fixá-los na memória** a longo prazo.

Desenvolvido com base nos conhecimentos adquiridos durante a **Imersão IA da Alura + Google**, este projeto busca oferecer uma nova abordagem para o estudo, tornando o processo mais intuitivo e prático.

A ideia central é utilizar a inteligência artificial de forma colaborativa, empregando múltiplos "agentes" de IA, cada um com uma função específica, para processar a dúvida do usuário e gerar respostas que realmente ajudem na compreensão e memorização.

## Funcionalidades Principais

O FIXA AI DEV oferece duas funcionalidades centrais para auxiliar no seu aprendizado:

-   **Analogias Personalizadas:** Digite qualquer conceito Tech que você esteja com dificuldade de entender. A IA irá gerar analogias relevantes, buscando conectar o conceito com a sua área de interesse ou até mesmo seus hobbies, tornando a memorização mais fácil e natural.
-   **Ideias de Projetos Práticos:** Receba sugestões de projetos práticos relacionados ao conceito estudado. Colocar a mão na massa é uma das melhores formas de fixar o aprendizado, e o FIXA AI DEV te dá o ponto de partida.

## Tecnologias Utilizadas

Este projeto foi construído utilizando as seguintes tecnologias:

-   **Frontend:** HTML, CSS, JavaScript
-   **Backend:** Python com Flask
-   **Inteligência Artificial:** [Mencionar qual API/Modelo de IA do Google foi usado - Gemini?]

É recomendado usar um ambiente virtual Python (como `venv` ou `conda`) para isolar as dependências do projeto.

### Configuração

1.  Clone o repositório para a sua máquina:
    ```bash
    git clone https://github.com/esa1715/fixa-ai-dev.git
    ```

2.  Navegue até a pasta raiz do projeto clonado:
    ```bash
    cd fixa-ai-dev
    ```

3.  Instale as dependências necessárias listadas no `requirements.txt`. Certifique-se de que você tem o arquivo `requirements.txt` na pasta raiz do projeto (ele deve ter vindo com o clone).
    ```bash
    pip install -r requirements.txt
    ```

4.  Configure sua Chave de API do Google Gemini.
    * Crie um arquivo na pasta raiz do projeto (`fixa-ai-dev`) chamado `.env`.
    * Abra este arquivo `.env` em um editor de texto.
    * Adicione a seguinte linha, substituindo `SUA_CHAVE_AQUI` pela sua chave de API real obtida do Google AI Studio:
        ```plaintext
        GOOGLE_API_KEY=SUA_CHAVE_AQUI
        ```
    * Salve e feche o arquivo `.env`.
    * **Importante:** Não compartilhe seu arquivo `.env` ou sua chave de API!

## Como Usar

Após seguir os passos de instalação e configuração, você pode iniciar o servidor Flask para rodar a aplicação localmente:

No terminal, dentro da pasta `fixa-ai-dev`, execute:

  ```bash
      flask run
  ```

O servidor será iniciado, e você poderá acessar a aplicação através do seu navegador, geralmente no endereço `http://127.0.0.1:5000/`.

Interaja com o chat na página para testar as funcionalidades de analogias e sugestões de projetos.

## Licença

Este projeto está sob a Licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## Autor

Desenvolvido por:

- [Erik Alves](https://portfolio-pessoal-alpha-nine.vercel.app/)
