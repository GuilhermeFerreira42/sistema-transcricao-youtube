Abaixo está um checklist detalhado para acompanhar o desenvolvimento de todas as fases do Sistema de Transcrição e Download do YouTube, baseado na documentacao de Documentacao_Sistema_Transcricao_Download_YouTube.txt

### **Checklist de Acompanhamento do Desenvolvimento**

Este checklist permite monitorar o progresso de cada fase, garantindo que todos os componentes e marcos sejam atingidos.

#### **Fase 1: MVP Básico (Duração: 2 semanas)**

*   **Objetivo:** Entregar a funcionalidade central de transcrição e download de vídeos individuais.
    *   **Componentes:**
        *   [ ] **`youtube_handler.py` completo:**
            *   [ ] Implementação da função `download_subtitles` para baixar legendas (PT-BR, PT, EN).
            *   [ ] Implementação da função `clean_subtitles` para remover timestamps e formatação.
            *   [ ] Implementação da função `download_and_clean_transcript`.
            *   [ ] Implementação da função `save_transcription` para salvar em JSON.
            *   [ ] Implementação da função `split_transcript_into_chunks`.
        *   [ ] **Rotas básicas de processamento (`routes.py`):**
            *   [ ] Rota `/process_youtube_video` para iniciar o processamento.
            *   [ ] Rota `/download_transcription/<video_id>` para download do TXT.
            *   [ ] Rota `/get_transcription/<video_id>` para obter a transcrição completa.
        *   [ ] **Interface mínima funcional (`chatUI.js`, `index.html`, CSS):**
            *   [ ] Campo de input para URL do YouTube.
            *   [ ] Botão para iniciar o processamento.
            *   [ ] Exibição da transcrição limpa na área central.
            *   [ ] Exibição de thumbnail e título do vídeo.
            *   [ ] Botão de download da transcrição em TXT.
            *   [ ] Animação de carregamento durante o processamento.
        *   [ ] **Download TXT básico:**
            *   [ ] Geração correta do arquivo TXT com conteúdo limpo.
            *   [ ] Nomeação do arquivo com o título do vídeo (sanitizado).
            *   [ ] Formatação básica do TXT (título, fonte, data).
    *   **Marcos de Conclusão da Fase:**
        *   [ ] Capacidade de processar vídeos individuais do YouTube.
        *   [ ] Exibição básica da transcrição na interface.
        *   [ ] Download funcional da transcrição em TXT.
        *   [ ] Armazenamento básico das transcrições em JSON.

---

#### **Fase 2: Histórico e Gerenciamento (Duração: 1.5 semanas)**

*   **Objetivo:** Implementar o gerenciamento do histórico de transcrições e a funcionalidade de busca.
    *   **Componentes:**
        *   [ ] **Sistema de indexação com UUIDs:**
            *   [ ] Geração de UUIDs para conversas e vídeos.
            *   [ ] Consistência na referência de IDs entre frontend e backend.
            *   [ ] Armazenamento de metadados em `history_index.json`.
        *   [ ] **Interface de histórico (barra lateral):**
            *   [ ] Exibição de lista de conversas/transcrições processadas.
            *   [ ] Navegação entre itens do histórico.
            *   [ ] Destaque visual da conversa ativa.
        *   [ ] **Busca no histórico:**
            *   [ ] Campo de busca na barra lateral.
            *   [ ] Filtragem de resultados em tempo real.
            *   [ ] Busca limitada ao índice para otimização.
            *   [ ] (Opcional) Destaque de termos pesquisados nos resultados.
        *   [ ] **Exclusão de transcrições (RF-07):**
            *   [ ] Botão de exclusão para transcrições individuais.
            *   [ ] Modal de confirmação para exclusão.
            *   [ ] Lógica de exclusão no backend (remover arquivo JSON).
            *   [ ] Atualização imediata da interface após exclusão.
    *   **Marcos de Conclusão da Fase:**
        *   [ ] Histórico persistente de conversas.
        *   [ ] Busca funcional no histórico.
        *   [ ] Exclusão de transcrições individuais.
        *   [ ] Interface refinada para navegação no histórico.

---

#### **Nova Fase 3: Implementação do Core de Playlists e Comunicação em Tempo Real**

* **Objetivo:** Implementar a funcionalidade central de processamento de playlists e o feedback de progresso em tempo real, que são os maiores avanços definidos na Parte 8.
* **Componentes:**
    * **Backend (`youtube_handler.py`, `app.py`):**
        * [ ] Modificar `extract_video_id` e a lógica de processamento para diferenciar URLs de vídeo e de playlist.
        * [cite_start][ ] Implementar a extração de todos os IDs de vídeo de uma URL de playlist[cite: 554].
        * [cite_start][ ] Adaptar o `HistoryManager` para criar e gerenciar os dois tipos de objetos no `history.json` (vídeo e playlist)[cite: 550].
        * [cite_start][ ] Integrar `Socket.IO` para emitir eventos de progresso (ex: "Iniciando playlist", "Processando vídeo 2 de 10", "Finalizado com 1 erro")[cite: 543, 555].
        * [ ] Criar uma nova rota para lidar especificamente com o processamento de playlists ou adaptar a existente.
    * **Frontend (`main.js`, `index.html`):**
        * [cite_start][ ] Implementar a conexão com o `Socket.IO` para ouvir os eventos de progresso e atualizar a UI em tempo real[cite: 559, 560].
        * [ ] Adaptar a interface do histórico (`#history-list`) para exibir ícones ou formatação diferente para vídeos e playlists.
        * [ ] Criar a interface de visualização de uma playlist, que deve listar os vídeos contidos nela e o status de cada um (concluído, falhou, em andamento).
* **Marcos de Conclusão da Fase:**
    * [ ] Sistema capaz de processar uma playlist completa e salvar as transcrições individuais.
    * [ ] Histórico exibe corretamente tanto vídeos individuais quanto playlists.
    * [ ] Interface fornece feedback em tempo real sobre o progresso do processamento da playlist.

---

#### **Fase 4: Refinamentos da Funcionalidade de Playlist e Gerenciamento**
* **Objetivo:** Aprimorar a experiência do usuário com playlists, corrigindo e refinando o download, a estrutura de histórico e a lógica de exclusão.
* **Componentes e Tarefas:**
  * **Funcionalidade de Download do ZIP:**
    * **Backend (`backend/youtube_handler.py`, `backend/app.py`):**
      * \[ \] Modificar a função de download do ZIP para ler o conteúdo de cada arquivo de transcrição (`.json`).
      * \[ \] Extrair especificamente a string de texto contida na chave `"transcript"` de cada objeto JSON.
      * \[ \] Para cada transcrição, criar um novo arquivo em memória, nomeado com o `video_id` e a extensão `.txt` (Ex: `video_id_exemplo.txt`).
      * \[ \] Adicionar todos os arquivos `.txt` ao arquivo ZIP gerado.
      * \[ \] Implementar uma lógica para criar um arquivo `transcricao_consolidada.txt` que contenha o texto de todas as transcrições concatenadas, separadas por uma linha divisória ou título do vídeo.
      * \[ \] Adicionar este arquivo consolidado ao ZIP.
      * \[ \] Na rota de download (`/download_playlist`), garantir que o cabeçalho `Content-Type` seja `application/zip` e que o arquivo ZIP seja retornado corretamente para o cliente.
  * **Hierarquia do Histórico (`frontend/static/js/main.js`):**
    * \[ \] Alterar a função `loadHistory()` para iterar sobre o histórico.
    * \[ \] Para cada item, verificar se ele é uma playlist (`item.type === 'playlist'`).
    * \[ \] Se for uma playlist, renderizar um elemento principal com um ícone de playlist e o título. Adicionar um ícone de expansão (por exemplo, `+` ou uma seta) que, quando clicado, exibe os vídeos da playlist como sub-itens.
    * \[ \] Se for um vídeo, verificar se ele possui um `playlist_id` associado. Se sim, **não renderizar este vídeo na lista principal**. Ele será renderizado apenas como um sub-item da sua respectiva playlist.
    * \[ \] Implementar a lógica de exibição/ocultação dos sub-itens da playlist.
  * **Comportamento de Clique (`frontend/static/js/main.js`):**
    * \[ \] Na função que lida com o evento de clique nos itens do histórico, adicionar uma condição para verificar se o item clicado é um vídeo que pertence a uma playlist.
    * \[ \] Se for o caso, a ação de clique deve carregar a transcrição do vídeo na área central de conteúdo, mas **sem criar um novo item de histórico na barra lateral**. A barra lateral do histórico deve permanecer no mesmo estado.

---

#### **Fase 5: Revisão Geral do Layout, UX e Finalização**
* **Objetivo:** Finalizar a implementação com um layout e experiência de usuário alinhados com a documentação original e com as expectativas.
* **Componentes e Tarefas:**
  * **Layout e Responsividade (`frontend/templates/index.html`, `frontend/static/css/style.css`):**
    * \[ \] Revisar o arquivo `style.css` para aplicar a paleta de cores, fontes (`Roboto` ou `Inter`) e a estrutura de três seções (`Header`, `Main`, `Footer`) conforme documentado.
    * \[ \] Utilizar Media Queries ou classes de framework responsivo (se aplicável) para garantir que o layout se ajuste perfeitamente em telas de desktops, tablets e smartphones, eliminando barras de rolagem horizontais.
    * \[ \] Implementar a lógica para alternar entre temas claro e escuro, modificando as variáveis CSS.
    * \[ \] Utilizar o `localStorage` para persistir a escolha do tema, garantindo que a preferência do usuário seja mantida ao recarregar a página.
  * **Tratamento de Erros e Mensagens:**
    * \[ \] Garantir que mensagens de erro retornadas pelo backend (ex: URL inválida, vídeo privado) sejam exibidas de forma clara e amigável ao usuário no frontend.
    * \[ \] Exibir mensagens de feedback em tempo real para ações como "Processando", "Concluído", "Falha".
  * **Marcos de Conclusão da Fase:**
    * \[ \] A interface possui um design consistente e está alinhada com a documentação.
    * \[ \] O sistema é totalmente responsivo e funcional em diferentes dispositivos.
    * \[ \] O tratamento de erros e a experiência do usuário foram refinados.