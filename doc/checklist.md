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

#### **Nova Fase 4: Refinamento da Interface e Gerenciamento Avançado**

* **Objetivo:** Aprimorar a experiência do usuário com as funcionalidades de gerenciamento, download e visuais que foram detalhadas.
* **Componentes:**
    * **Backend:**
        * [cite_start][ ] Implementar a lógica de download unificado para playlists: criar um arquivo ZIP em memória contendo os JSONs individuais e o TXT consolidado[cite: 536].
        * [ ] Criar o endpoint `DELETE` para excluir uma playlist inteira (removendo a entrada do histórico e todos os JSONs associados).
        * [cite_start][ ] Implementar a lógica de reprocessamento de falhas para vídeos dentro de uma playlist[cite: 537].
        * [cite_start][ ] Implementar a lógica de cancelamento de um processo em andamento[cite: 538].
    * **Frontend:**
        * [cite_start][ ] Implementar a alternância de temas claro/escuro, persistindo a escolha no `localStorage`[cite: 542, 565].
        * [ ] Adicionar o botão de download de ZIP na visualização de playlist.
        * [ ] Adicionar o botão de "Reprocessar falhas" e "Cancelar" na interface da playlist.
        * [cite_start][ ] Garantir que a interface seja totalmente responsiva em desktops, tablets e celulares[cite: 541].
* **Marcos de Conclusão da Fase:**
    * [ ] Download de ZIP para playlists está funcional.
    * [ ] Exclusão, reprocessamento e cancelamento de playlists funcionam como esperado.
    * [ ] Temas claro/escuro e responsividade completa implementados.

---

#### **Nova Fase 5: Otimização, Robustez e Finalização**

* **Objetivo:** Garantir que o sistema seja robusto, eficiente e confiável, tratando casos extremos e otimizando o uso de recursos.
* **Componentes:**
    * **Backend:**
        * [cite_start][ ] Implementar uma fila de processamento para limitar o número de transcrições simultâneas, monitorando o uso de CPU/RAM[cite: 545].
        * [cite_start][ ] Implementar o sistema de recuperação de estado para que processos de playlist longos possam ser retomados em caso de reinicialização do servidor[cite: 547].
        * [cite_start][ ] Implementar o limite de 3 tentativas para reprocessamento de vídeos com falha[cite: 548].
    * **Frontend:**
        * [ ] Exibir o status "Falha Permanente" para vídeos que atingiram o limite de reprocessamento.
        * [cite_start][ ] Exibir mensagens de erro mais detalhadas e amigáveis, com links para um possível FAQ, conforme definido em RNF-06[cite: 546].
    * **Geral:**
        * [cite_start][ ] Realizar testes de usabilidade e compatibilidade nos principais navegadores (Chrome, Firefox, Edge)[cite: 449].
        * [ ] Finalizar e revisar toda a documentação do projeto.
* **Marcos de Conclusão da Fase:**
    * [ ] Sistema otimizado para não sobrecarregar o servidor.
    * [ ] Recuperação de estado e tratamento de falhas permanentes estão funcionais.
    * [ ] Projeto testado, documentado e pronto para um lançamento estável.
