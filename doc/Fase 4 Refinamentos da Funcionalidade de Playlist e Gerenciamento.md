#### **Fase 4: Refinamentos da Funcionalidade de Playlist e Gerenciamento**
* **Objetivo:** Aprimorar a experiência do usuário com playlists, corrigindo e refinando o download, a estrutura de histórico e a lógica de exclusão.
* **Componentes e Tarefas:**
  * **Funcionalidade de Download do ZIP:**
    * **Backend (`backend/youtube_handler.py`, `backend/app.py`):**
      * [x] Modificar a função de download do ZIP para ler o conteúdo de cada arquivo de transcrição (`.json`).
      * [x] Extrair especificamente a string de texto contida na chave `"transcript"` de cada objeto JSON.
      * [x] Para cada transcrição, criar um novo arquivo em memória, nomeado com o `video_id` e a extensão `.txt` (Ex: `video_id_exemplo.txt`).
      * [x] Adicionar todos os arquivos `.txt` ao arquivo ZIP gerado.
      * [x] Implementar uma lógica para criar um arquivo `transcricao_consolidada.txt` que contenha o texto de todas as transcrições concatenadas, separadas por uma linha divisória ou título do vídeo.
      * [x] Adicionar este arquivo consolidado ao ZIP.
      * [x] Na rota de download (`/download_playlist`), garantir que o cabeçalho `Content-Type` seja `application/zip` e que o arquivo ZIP seja retornado corretamente para o cliente.
  * **Hierarquia do Histórico (`frontend/static/js/main.js`):**
    * [x] Alterar a função `loadHistory()` para iterar sobre o histórico.
    * [x] Para cada item, verificar se ele é uma playlist (`item.type === 'playlist'`).
    * [x] Se for uma playlist, renderizar um elemento principal com um ícone de playlist e o título. Adicionar um ícone de expansão (por exemplo, `+` ou uma seta) que, quando clicado, exibe os vídeos da playlist como sub-itens.
    * [x] Se for um vídeo, verificar se ele possui um `playlist_id` associado. Se sim, **não renderizar este vídeo na lista principal**. Ele será renderizado apenas como um sub-item da sua respectiva playlist.
    * [x] Implementar a lógica de exibição/ocultação dos sub-itens da playlist.
  * **Comportamento de Clique (`frontend/static/js/main.js`):**
    * [x] Na função que lida com o evento de clique nos itens do histórico, adicionar uma condição para verificar se o item clicado é um vídeo que pertence a uma playlist.
    * [x] Se for o caso, a ação de clique deve carregar a transcrição do vídeo na área central de conteúdo, mas **sem criar um novo item de histórico na barra lateral**. A barra lateral do histórico deve permanecer no mesmo estado.
