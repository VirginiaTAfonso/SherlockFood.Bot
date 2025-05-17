# SherlockFoodBot - Seu Analisador Inteligente de Rótulos Alimentares

## Resumo do Projeto

SherlockFood é um chatbot inteligente desenvolvido em Python que auxilia usuários a entenderem melhor os rótulos de alimentos em relação aos seus objetivos de saúde e nutrição. Ao enviar uma foto nítida do rótulo de um alimento, o bot utiliza a poderosa API do Gemini (Google AI) para analisar o conteúdo do rótulo e fornecer uma classificação (em português claro para o usuário leigo: **RECOMENDADO**, **AS_VEZES**, **NAO_INDICADO**, **NÃO_ALIMENTO**) juntamente com um breve resumo dos principais nutrientes e informações relevantes para o objetivo selecionado pelo usuário (emagrecimento, vida saudável, consumo de proteína).

O bot guia o usuário através de uma conversa simples, primeiro solicitando o objetivo desejado e, em seguida, pedindo a foto do rótulo para análise. Após a análise, apresenta a classificação de forma clara e um resumo conciso em tópicos, sugerindo uma quantidade ideal de consumo diário (se aplicável) e uma opção de substituição saudável (se possível), tornando a interpretação de rótulos mais acessível e informada.

## Dependências

Este projeto utiliza as seguintes bibliotecas Python:

* [`python-telegram-bot`](https://github.com/python-telegram-bot/python-telegram-bot): Framework para interagir com a API do Telegram, permitindo a criação e gerenciamento do chatbot.
* [`Pillow (PIL Fork)`](https://pypi.org/project/Pillow/): Biblioteca de processamento de imagens (embora atualmente não haja manipulação de imagem explícita no código fornecido, pode ser utilizada para futuras funcionalidades).
* [`io`](https://docs.python.org/3/library/io.html): Módulo para trabalhar com fluxos de dados, utilizado para ler a imagem do rótulo diretamente da memória.
* [`google-generativeai`](https://ai.google.dev/docs/reference/rest): Biblioteca da Google para acessar a API do Gemini, responsável pela análise do conteúdo do rótulo da imagem.
* [`google-generativeai.types`](https://ai.google.dev/docs/reference/rest/client-libraries): Submódulo da biblioteca `google-generativeai` para lidar com tipos específicos, como `HarmCategory` e `HarmBlockThreshold` para configurações de segurança do modelo.
* [`os`](https://docs.python.org/3/library/os.html): Módulo para interagir com o sistema operacional, utilizado para manipulação de arquivos (como salvar e deletar a imagem do rótulo localmente).

## Como executar o projeto

1.  Clone este repositório:
    ```bash
    git clone https://github.com/VirginiaTAfonso/SherlockFood.Bot
    cd SherlockFood
    ```
2.  Certifique-se de ter o Python instalado em seu sistema ([Python Downloads](https://www.python.org/downloads/)).
3.  Crie um ambiente virtual:
    ```bash
    python -m venv venv
    ```
4.  Ative o ambiente virtual:
    * No Windows:
        ```bash
        venv\Scripts\activate
        ```
    * No macOS/Linux:
        ```bash
        source venv/bin/activate
        ```
5.  Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```
6.  Configure seu Token do Telegram e sua Google API Key no script `chatbot.py`. Substitua os placeholders pelas suas chaves reais:
    ```python
    TOKEN = 'SEU_TOKEN_TELEGRAM'
    GOOGLE_API_KEY = 'SUA_GOOGLE_API_KEY'
    ```
7.  Execute o bot:
    ```bash
    python chatbot.py
    ```
8.  Inicie uma conversa com o bot no Telegram usando o comando `/start`.

## Observações

* Certifique-se de ter uma conexão de internet estável para que o bot possa se comunicar com a API do Telegram e a API do Gemini.
* A qualidade da análise depende da nitidez da foto do rótulo enviada.
* O modelo Gemini utilizado nesta versão é o `'gemini-2.0-flash'`.
