# gitsnap 📸

`gitsnap` é uma ferramenta de linha de comandos (TUI - Terminal User Interface) construída em Python com a biblioteca [Textual](https://textual.textualize.io/). Ela oferece um fluxo de trabalho de "snapshots" simples e intuitivo sobre o Git, abstraindo comandos complexos e permitindo que os utilizadores salvem e restaurem versões do seu trabalho de forma rápida e segura.

A filosofia do `gitsnap` é ser local-primeiro ("local-first"), com sincronização online opcional.

![Demonstração do gitsnap](https://raw.githubusercontent.com/mefrraz/gitsnap/main/demo.gif) 
*(Nota: Este link de imagem é um placeholder. Após o upload do projeto, você pode criar um GIF de demonstração e atualizar este link.)*

## Funcionalidades Principais

- **Interface Intuitiva no Terminal:** Uma experiência de aplicação rica diretamente no seu terminal.
- **Inicialização de Repositórios:** Inicia um repositório Git numa pasta que ainda não o seja.
- **Criação de Snapshots:** Salva o estado atual do seu trabalho (ficheiros modificados e novos) como um "snapshot" local (um `commit` e `tag` Git).
- **Listagem e Gestão de Snapshots:**
    - Vê uma lista de todos os snapshots criados.
    - Restaura qualquer snapshot anterior com um clique.
    - Renomeia a mensagem de um snapshot.
    - Elimina snapshots locais que já não são necessários.
- **Descartar Alterações:** Reverte todos os ficheiros para o estado do último snapshot, de forma segura e com confirmação.
- **Sincronização com o GitHub:**
    - Um ecrã dedicado para comparar os seus snapshots locais com os do repositório remoto.
    - Faz "Push" dos novos snapshots para o GitHub com um único botão.
    - Lida com a autenticação de forma segura (através de um ficheiro de configuração local).
    - Deteta automaticamente o ramo principal (`main` ou `master`).

## Instalação

O `gitsnap` foi construído com Python. Para o executar, você precisa de ter o Python 3.8+ e o `git` instalados no seu sistema.

1.  **Clone o Repositório:**
    ```bash
    git clone https://github.com/SEU_NOME_DE_UTILIZADOR/gitsnap.git
    cd gitsnap
    ```
    *(Substitua `SEU_NOME_DE_UTILIZADOR` pelo seu nome de utilizador do GitHub)*

2.  **Crie e Ative um Ambiente Virtual:**
    Este passo é recomendado para isolar as dependências do projeto.
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Instale as Dependências:**
    O comando seguinte instala o `gitsnap` e as bibliotecas necessárias (como o Textual) em modo "editável".
    ```bash
    pip install -e .
    ```

## Como Usar

Depois de instalar, certifique-se de que o seu ambiente virtual está ativo (`source .venv/bin/activate`).

Para iniciar a aplicação em qualquer pasta do seu sistema, basta executar:
```bash
gitsnap
```

A aplicação irá abrir e analisar a pasta atual.

### Fluxo de Trabalho Básico

1.  Navegue para a pasta do seu projeto.
2.  Execute `gitsnap`.
3.  Se a pasta não for um repositório Git, a aplicação irá oferecer-se para o inicializar.
4.  Faça alterações nos seus ficheiros. A interface do `gitsnap` irá mostrá-los.
5.  Escreva uma mensagem descritiva e clique em "Salvar Snapshot" para guardar o seu trabalho localmente.
6.  Quando estiver pronto para enviar as suas alterações para o GitHub:
    *   Certifique-se de que o seu repositório local está ligado a um remoto (`git remote add origin ...`).
    *   Clique em "Sincronizar com GitHub".
    *   No novo ecrã, reveja os snapshots a serem enviados e clique em "Fazer Push".

### Configurar a Sincronização com o GitHub

Para a funcionalidade de "Push" funcionar, o `gitsnap` precisa de um **Token de Acesso Pessoal (PAT)** do GitHub.

1.  **Gere um Token:**
    *   Vá a [GitHub > Settings > Developer settings > Personal access tokens > Tokens (classic)](https://github.com/settings/tokens/new).
    *   Clique em "Generate new token".
    *   Dê um nome (ex: `gitsnap-cli`), defina uma data de expiração, e selecione o escopo **`repo`**.
    *   Copie o token gerado (começa com `ghp_...`).

2.  **Crie o Ficheiro de Configuração:**
    Crie o ficheiro `~/.config/gitsnap/config.json` com o seguinte conteúdo, substituindo `SEU_TOKEN_AQUI` pelo token que você copiou:
    ```bash
    mkdir -p ~/.config/gitsnap
    echo '{"github_token": "SEU_TOKEN_AQUI"}' > ~/.config/gitsnap/config.json
    ```
    **Aviso:** Esta abordagem guarda o token em texto simples. Use um token com o mínimo de permissões necessárias e uma data de expiração curta.

## Contribuir

Este projeto foi desenvolvido com a ajuda de uma IA. Se encontrar bugs ou tiver ideias para novas funcionalidades, sinta-se à vontade para abrir uma "Issue" ou um "Pull Request".
