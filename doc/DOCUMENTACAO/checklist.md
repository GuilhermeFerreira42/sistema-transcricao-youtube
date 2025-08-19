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

## **Checklist de Implementação Detalhado - Fases 5, 6 e 7**

Este documento fornece um checklist granular e exaustivo para a implementação das Fases 5, 6 e 7 do Sistema de Transcrição e Download do YouTube. As instruções são formuladas para serem literais e não deixar margem para interpretação, visando a execução precisa por parte dos desenvolvedores.

### **1. Fase 5: Modularização Estrutural**

**1.1. Objetivo**

Refatorar a base de código do backend e do frontend, aplicando princípios de modularização e separação de responsabilidades para criar uma arquitetura de software sustentável e escalável.

**1.2. Requisitos Funcionais (RF)**

**1.2.1. RF-20: Estrutura Modular do Backend**

*   **Descrição:** O sistema backend deve ser reorganizado em uma arquitetura modular com separação clara de responsabilidades entre rotas, serviços e utilitários.
*   **Critérios de Aceitação:**
    *   **1.2.1.1. Rotas Flask:**
        *   [ ] Todas as definições de rotas Flask devem ser movidas para o diretório `backend/routes/`.
        *   [ ] Cada grupo lógico de rotas (ex: transcrição, histórico) deve ter seu próprio arquivo de Blueprint (ex: `transcription_routes.py`, `history_routes.py`).
        *   [ ] O arquivo `backend/routes/__init__.py` deve ser criado e pode ser vazio ou conter inicializações de Blueprints se necessário.
    *   **1.2.1.2. Lógica de Negócio (Serviços):**
        *   [ ] Toda a lógica de negócio (interação com APIs externas como YouTube, gerenciamento de dados, manipulação de arquivos JSON) deve ser encapsulada em classes ou funções dentro do diretório `backend/services/`.
        *   [ ] Cada serviço deve ter uma responsabilidade única (ex: `TranscriptionService` para lógica de transcrição, `HistoryService` para gerenciamento de histórico, `ProcessingService` para orquestração de tarefas em background).
        *   [ ] O arquivo `backend/services/__init__.py` deve ser criado e pode ser vazio.
    *   **1.2.1.3. Funções Utilitárias:**
        *   [ ] Funções utilitárias genéricas que não pertencem a uma lógica de negócio específica (ex: sanitização de nomes de arquivo, validação de URL, extração de ID de vídeo) devem ser movidas para o diretório `backend/utils/`.
        *   [ ] Exemplos de arquivos: `helpers.py` (para funções gerais), `file_utils.py` (para operações de arquivo).
        *   [ ] O arquivo `backend/utils/__init__.py` deve ser criado e pode ser vazio.
    *   **1.2.1.4. `app.py` (Arquivo Principal):**
        *   [ ] O arquivo `backend/app.py` deve conter apenas a configuração inicial do aplicativo Flask, a inicialização do Socket.IO e o registro dos Blueprints definidos em `backend/routes/`.
        *   [ ] Nenhum código de lógica de negócio (ex: chamadas diretas a `youtube_handler` ou manipulação de dados) deve permanecer em `app.py`.
        *   [ ] As funções `process_video_task` e `process_playlist_task` devem ser movidas para um serviço apropriado (ex: `ProcessingService`) e chamadas a partir das rotas.
    *   **1.2.1.5. Injeção de Dependências:**
        *   [ ] Serviços devem ser instanciados e utilizados pelas rotas ou por outros serviços conforme necessário, garantindo que as dependências sejam explícitas.
*   **Status:** Parcialmente Implementado (Requer verificação e conclusão de todos os sub-itens).

**1.2.2. RF-21: Modularização do Frontend**

*   **Descrição:** O código JavaScript do frontend deve ser dividido em módulos especializados que seguem o princípio de responsabilidade única, utilizando o sistema de módulos ES6.
*   **Critérios de Aceitação:**
    *   **1.2.2.1. Estrutura de Módulos:**
        *   [ ] O diretório `frontend/static/js/` deve conter os seguintes arquivos de módulo:
            *   [ ] `ui.js`: Responsável por toda a manipulação do DOM, renderização da interface do usuário e tratamento de eventos de UI.
            *   [ ] `api.js`: Responsável por todas as requisições HTTP (fetch) para o backend.
            *   [ ] `socket.js`: Responsável por gerenciar a conexão Socket.IO e ouvir/emitir eventos em tempo real.
            *   [ ] `utils.js`: Responsável por funções utilitárias genéricas do frontend (ex: formatação de data, validação de entrada simples).
            *   [ ] `main.js`: Deve ser o ponto de entrada principal, responsável apenas por importar e inicializar os outros módulos.
    *   **1.2.2.2. Sistema de Módulos ES6:**
        *   [ ] Todos os módulos (exceto `main.js` que os importa) devem usar `export` para disponibilizar suas funções/classes e `import` para consumir funcionalidades de outros módulos.
        *   [ ] O arquivo `frontend/templates/index.html` deve carregar `main.js` com `type="module"` (ex: `<script type="module" src="/static/js/main.js"></script>`).
    *   **1.2.2.3. Separação de Lógica:**
        *   [ ] Funções de manipulação da interface (ex: `addLoadingMessage`, `renderYouTubeTranscription`, `showNotification`, `showConfirmationModal`) devem ser movidas para `ui.js`.
        *   [ ] Funções de comunicação com a API (ex: `processUrl`, `getHistory`, `deleteEntry`, `searchHistory`, `processUrls`) devem ser movidas para `api.js`.
        *   [ ] A lógica de conexão e tratamento de eventos Socket.IO (ex: `socket.on`, `socket.emit`) deve ser encapsulada em `socket.js`.
        *   [ ] Funções de utilidade (ex: `generateConversationId`, `generateMessageId`, `sanitizeFilename` se houver no frontend) devem ser movidas para `utils.js`.
    *   **1.2.2.4. Inicialização:**
        *   [ ] A lógica de inicialização do aplicativo (ex: `document.addEventListener('DOMContentLoaded', ...)`) deve estar em `main.js` e chamar métodos de inicialização dos outros módulos (ex: `UI.init()`, `Socket.init()`).
        *   [ ] Nenhum código deve ser executado imediatamente ao carregar um script de módulo (exceto a definição de funções/classes e exportações).
*   **Status:** Parcialmente Implementado (Requer verificação e conclusão de todos os sub-itens).

**1.3. Requisitos Não Funcionais (RNF)**

**1.3.1. RNF-21: Legibilidade do Código**

*   **Descrição:** A nova estrutura modular deve melhorar significativamente a legibilidade e a facilidade de navegação no código-fonte.
*   **Critérios de Aceitação:**
    *   **1.3.1.1. Identificação de Componentes:**
        *   [ ] Um desenvolvedor familiarizado com Flask e princípios de arquitetura (MVC/camadas) deve ser capaz de identificar a localização de uma rota, um serviço ou uma função utilitária em menos de 30 segundos.
    *   **1.3.1.2. Dependência Unidirecional:**
        *   [ ] A dependência entre módulos deve ser clara e, preferencialmente, unidirecional (rotas chamam serviços, serviços chamam outros serviços ou utilitários; módulos de UI chamam API/Socket, API/Socket não chamam UI).
    *   **1.3.1.3. Tamanho de Arquivo:**
        *   [ ] Nenhum arquivo de código-fonte (Python ou JavaScript) deve exceder 300 linhas de código (excluindo comentários e linhas em branco).
    *   **1.3.1.4. Docstrings/Comentários:**
        *   [ ] Todos os módulos, classes e funções principais devem ter docstrings (Python) ou comentários (JavaScript) claros explicando sua responsabilidade, parâmetros, retornos e exceções.
*   **Status:** Parcialmente Implementado (Requer revisão e ajuste de todos os sub-itens).

**1.3.2. RNF-22: Escalabilidade**

*   **Descrição:** A arquitetura modular deve permitir a adição de novas funcionalidades com impacto mínimo na estrutura existente.
*   **Critérios de Aceitação:**
    *   **1.3.2.1. Adição de Recurso:**
        *   [ ] A adição de um novo recurso (ex: suporte a outro provedor de vídeos, nova funcionalidade de análise de texto) deve requerer alterações em no máximo 3 módulos existentes (excluindo a criação de novos módulos para o recurso).
    *   **1.3.2.2. Novos Endpoints:**
        *   [ ] Novos endpoints de API devem ser adicionados criando um novo arquivo de Blueprint em `backend/routes/` sem modificar `backend/app.py` (além do registro do novo Blueprint).
    *   **1.3.2.3. Nova Lógica de Negócio:**
        *   [ ] A nova lógica de negócio deve ser adicionada criando novos serviços em `backend/services/` sem modificar os serviços existentes, a menos que seja uma extensão direta de funcionalidade.
    *   **1.3.2.4. Novas Funcionalidades Frontend:**
        *   [ ] O frontend deve permitir a adição de novas funcionalidades através da criação de novos módulos JavaScript ou extensão dos módulos existentes sem reescrever grandes seções de código.
*   **Status:** Parcialmente Implementado (Requer validação prática na Fase 6).

**1.3.3. RNF-23: Testabilidade**

*   **Descrição:** A separação da lógica de negócio (serviços) da lógica de apresentação (rotas) deve aumentar a testabilidade do sistema, permitindo a criação de testes unitários focados nos serviços sem a necessidade de um contexto de requisição HTTP.
*   **Critérios de Aceitação:**
    *   **1.3.3.1. Teste Isolado de Serviços:**
        *   [ ] Todos os serviços em `backend/services/` devem poder ser instanciados e testados isoladamente, sem a necessidade de iniciar o servidor Flask ou simular requisições HTTP completas.
    *   **1.3.3.2. Cobertura de Testes:**
        *   [ ] Os testes unitários devem cobrir pelo menos 70% da lógica de negócio implementada nos serviços do backend.
    *   **1.3.3.3. Mocking de Dependências:**
        *   [ ] Deve ser possível mockar (simular) dependências externas (ex: chamadas à API do YouTube, operações de sistema de arquivos, chamadas a outros serviços) para testes unitários, garantindo que apenas a lógica do serviço em questão seja testada.
    *   **1.3.3.4. Execução Independente:**
        *   [ ] Os testes devem ser executáveis independentemente do frontend e de qualquer estado persistente do sistema (ex: arquivos `history.json`).
*   **Status:** Não Iniciado (Requer implementação completa na Fase 5).

**1.3.4. RNF-24: Consistência da API**

*   **Descrição:** A refatoração do backend não deve alterar a interface da API exposta ao frontend. As URLs, métodos HTTP e a estrutura dos dados trocados devem permanecer os mesmos para garantir a compatibilidade retroativa.
*   **Critérios de Aceitação:**
    *   **1.3.4.1. URLs de Endpoint:**
        *   [ ] Todas as URLs de endpoint existentes (ex: `/process_url`, `/get_history`, `/delete_entry/<id>`, `/download_playlist/<id>`, `/download_transcription/<id>`, `/get_playlist_details/<id>`, `/get_transcription/<id>`) devem permanecer inalteradas.
    *   **1.3.4.2. Métodos HTTP:**
        *   [ ] Os métodos HTTP (GET, POST, DELETE) para cada endpoint existente devem permanecer os mesmos.
    *   **1.3.4.3. Estrutura JSON:**
        *   [ ] A estrutura JSON das requisições e respostas (nomes de campos, tipos de dados, aninhamento) para todos os endpoints existentes deve ser idêntica à anterior à refatoração.
    *   **1.3.4.4. Compatibilidade Frontend:**
        *   [ ] O frontend existente deve continuar funcionando sem a necessidade de alterações no seu código JavaScript após a refatoração do backend.
*   **Status:** Concluído (Requer verificação final após a conclusão de todos os sub-itens da Fase 5).

---

### **Checklist de Implementação Detalhado - Fases 6, 7 e 8**

Este documento fornece um checklist granular e exaustivo para a implementação das Fases 6, 7 e 8 do Sistema de Transcrição e Download do YouTube. As instruções são formuladas para serem literais, visando a execução precisa por parte dos desenvolvedores e a validação inequívoca pela equipe de testes.

-----

### **Fase 6: Modularização do Core do YouTube**

**Objetivo:** Refatorar o arquivo monolítico `youtube_handler.py`, desmembrando sua lógica em serviços coesos e com responsabilidades únicas, alinhando toda a arquitetura do backend a um padrão modular.

#### **1. RF-22: Serviço de Interação com YouTube (`YouTubeService`)**

  * **Backend (Desenvolvimento):**
      * [ ] Criar o arquivo `backend/services/youtube_service.py`.
      * [ ] Dentro de `youtube_service.py`, criar a classe `YouTubeService`.
      * [ ] Mover a função `_get_realistic_headers` de `youtube_handler.py` para `YouTubeService`.
      * [ ] Mover a função `_add_random_delay` de `youtube_handler.py` para `YouTubeService`.
      * [ ] Mover a função `_is_google_block` de `youtube_handler.py` para `YouTubeService`.
      * [ ] Mover a função `_get_video_metadata` de `youtube_handler.py` para `YouTubeService`.
      * [ ] Mover a função `get_playlist_info` de `youtube_handler.py` para `YouTubeService`.
      * [ ] Criar um novo método `get_raw_transcript_and_metadata(url)` em `YouTubeService`.
      * [ ] Mover para este novo método a lógica de `download_and_clean_transcript` que chama `YouTubeTranscriptApi` e o método de `fallback`.
      * [ ] Mover a função `download_subtitles_fallback` de `youtube_handler.py` para `YouTubeService`.
  * **Testes (QA):**
      * [ ] Verificar se o `YouTubeService` consegue obter metadados de um vídeo individual.
      * [ ] Verificar se o `YouTubeService` consegue obter a lista de vídeos de uma playlist.
      * [ ] Verificar se o método de `fallback` é acionado para um vídeo que sabidamente falha na API primária.
      * [ ] Confirmar que o serviço retorna a transcrição bruta (sem limpeza) e os metadados.

#### **2. RF-23: Serviço de Manipulação de Transcrições (`TranscriptionService`)**

  * **Backend (Desenvolvimento):**
      * [ ] Criar o arquivo `backend/services/transcription_service.py`.
      * [ ] Dentro de `transcription_service.py`, criar a classe `TranscriptionService`.
      * [ ] Mover a função `clean_subtitles` de `youtube_handler.py` para `TranscriptionService`.
      * [ ] Mover a função `split_transcript_into_chunks` de `youtube_handler.py` para `TranscriptionService`.
  * **Testes (QA):**
      * [ ] Testar o método `clean_subtitles` com uma string de legenda bruta (formato VTT/SRT) e verificar se os timestamps e tags são removidos.
      * [ ] Testar o método `split_transcript_into_chunks` com um texto longo e verificar se a lista de blocos é gerada corretamente, respeitando o limite de palavras.

#### **3. RF-24: Serviço de Gerenciamento de Arquivos (`FileService` - Hipotético, pois não foi solicitado, mas seria o próximo passo lógico)**

#### **4. RF-25: Refatoração do Orquestrador (`ProcessingService`)**

  * **Backend (Desenvolvimento):**
      * [ ] Modificar o `__init__` da classe `ProcessingService` para receber as instâncias dos novos serviços (`YouTubeService`, `TranscriptionService`, etc.).
      * [ ] Em `app.py`, instanciar os novos serviços e injetá-los no `ProcessingService` ao criá-lo.
      * [ ] Reescrever o método `process_video_task` para remover qualquer menção a `youtube_handler`.
      * [ ] Implementar a nova sequência de chamadas em `process_video_task`:
        1.  `youtube_service.get_raw_transcript_and_metadata()`
        2.  `transcription_service.clean_subtitles()`
        3.  `transcription_service.split_transcript_into_chunks()`
        4.  `youtube_handler.save_transcription_to_json()` (temporário até a criação de um `FileService`).
      * [ ] Garantir que os eventos `Socket.IO` (`video_progress`, `video_complete`, etc.) continuem sendo emitidos nos mesmos pontos do fluxo.
  * **Testes (QA):**
      * [ ] Processar um vídeo individual e verificar se a transcrição é gerada e salva corretamente, e se a UI é atualizada em tempo real.
      * [ ] Processar uma playlist e verificar se todos os vídeos são processados e se a UI reflete o progresso corretamente.
      * [ ] Verificar se o comportamento da aplicação para o usuário final permanece idêntico ao de antes da refatoração.

#### **5. Finalização da Fase**

  * **Backend (Desenvolvimento):**
      * [ ] Revisar todo o código e remover todas as chamadas remanescentes para `youtube_handler.py`.
      * [ ] Excluir o arquivo `backend/youtube_handler.py`.
  * **Testes (QA):**
      * [ ] Executar um teste de regressão completo, incluindo processamento de vídeo, playlist, visualização do histórico e exclusão, para garantir que a remoção do `youtube_handler` não introduziu efeitos colaterais.

-----

### **Fase 7: Aprimoramento da Arquitetura Modular**

**Objetivo:** Implementar novas funcionalidades de gerenciamento de histórico e processamento em lote, capitalizando sobre a nova arquitetura modular.

#### **1. RF-11: Busca Abrangente no Histórico**

  * **Backend (Desenvolvimento):**
      * [ ] Criar um novo endpoint `GET /search_history` em `backend/routes/history_routes.py`.
      * [ ] Garantir que o endpoint aceite os parâmetros de query: `q`, `start_date`, `end_date`, `duration`, `type`.
      * [ ] Implementar um novo método `search(...)` em `backend/services/history_service.py`.
      * [ ] Dentro de `search`, implementar a lógica de filtragem para o termo de pesquisa (`q`) no título.
      * [ ] Implementar a lógica de filtragem por intervalo de datas (`start_date`, `end_date`) comparando com o campo `created_at`.
      * [ ] Implementar a lógica de filtragem por duração (`duration`), considerando: `short` (\< 300s), `medium` (300-1200s), `long` (\> 1200s).
      * [ ] Implementar a lógica de filtragem por tipo de conteúdo (`type`: `video` ou `playlist`).
  * **Frontend (Desenvolvimento):**
      * [ ] Adicionar a estrutura HTML para a interface de busca avançada em `index.html` (campos de texto, seletores de data, dropdowns).
      * [ ] Em `main.js`, adicionar um event listener ao botão "Aplicar Filtros".
      * [ ] Implementar um mecanismo de *debounce* de 300ms no campo de texto da busca.
      * [ ] Criar uma função `searchHistory(filters)` (no futuro `api.js`) para montar a URL e chamar o endpoint `GET /search_history`.
      * [ ] Garantir que a função `loadHistory` seja chamada com os resultados da busca para renderizar a lista filtrada.
  * **Testes (QA):**
      * [ ] Testar a busca apenas com termo de texto e verificar se os resultados estão corretos.
      * [ ] Testar a busca apenas com filtro de data e verificar a precisão.
      * [ ] Testar a busca combinando múltiplos filtros (ex: playlists longas do último mês contendo a palavra "python").
      * [ ] Verificar se o *debounce* funciona, observando as requisições de rede no navegador.
      * [ ] Testar com um histórico grande (se possível, simulado) para avaliar o desempenho da busca.

#### **2. RF-15: Processamento de Múltiplas URLs**

  * **Backend (Desenvolvimento):**
      * [ ] Criar um novo endpoint `POST /process_urls` em `backend/routes/transcription_routes.py`.
      * [ ] Implementar a lógica para receber um array de URLs do corpo da requisição.
      * [ ] No backend, iterar sobre o array e, para cada URL, validar e iniciar o `ProcessingService` de forma sequencial.
      * [ ] Coletar o resultado de cada processamento (sucesso ou erro) e retornar um array de resultados no final.
  * **Frontend (Desenvolvimento):**
      * [ ] Adicionar uma `textarea` e um botão "Processar Múltiplas URLs" em `index.html`.
      * [ ] Em `main.js`, adicionar um event listener para o novo botão.
      * [ ] A função do listener deve ler a `textarea`, dividir o conteúdo por quebras de linha, limpar e filtrar as URLs.
      * [ ] Chamar o endpoint `POST /process_urls` enviando o array de URLs.
      * [ ] Criar uma função para renderizar o resumo dos resultados (ex: "3 URLs processadas com sucesso, 1 com erro") e os detalhes de cada uma.
  * **Testes (QA):**
      * [ ] Testar com uma lista de URLs válidas e verificar se todas são processadas e o histórico é atualizado.
      * [ ] Testar com uma lista mista (URLs válidas, inválidas, duplicadas) e verificar se apenas as válidas são processadas e se o feedback de erro para as inválidas é exibido corretamente.
      * [ ] Verificar se a UI é atualizada corretamente após a conclusão do lote.

#### **3. RNF-16: Identidade Visual do Navegador (Favicon)**

  * **Frontend (Desenvolvimento):**
      * [ ] Adicionar um arquivo `favicon.ico` ao diretório `frontend/static/` (ou `img/`).
      * [ ] Adicionar a tag `<link rel="icon" href="/static/favicon.ico">` no `<head>` do `index.html`.
  * **Testes (QA):**
      * [ ] Abrir a aplicação no navegador e verificar se o favicon aparece na aba da página.
      * [ ] Adicionar a página aos favoritos e verificar se o favicon é exibido.

-----

### **Fase 8: Refinamento de UX e Finalização**

**Objetivo:** Polir a aplicação, focando em temas, responsividade, feedback visual e acessibilidade para entregar uma experiência de usuário profissional.

#### **1. RF-16 / RNF-08: Temas de Interface (Claro/Escuro)**

  * **Frontend (Desenvolvimento):**
      * [ ] Em `style.css`, definir variáveis CSS para cores, fundos e bordas no seletor `:root`.
      * [ ] Criar um seletor `[data-theme="dark"]` em `style.css` que sobrescreve as variáveis para o tema escuro.
      * [ ] Refatorar todo o `style.css` para usar as novas variáveis em vez de cores fixas.
      * [ ] Em `main.js`, criar uma função `initTheme` para ser chamada no `DOMContentLoaded`.
      * [ ] `initTheme` deve:
        1.  Verificar se há um tema salvo no `localStorage`.
        2.  Se não houver, verificar a preferência do SO com `window.matchMedia`.
        3.  Aplicar o tema inicial definindo o atributo `data-theme` em `document.documentElement`.
      * [ ] Adicionar um botão de alternância de tema ao `index.html`.
      * [ ] Em `main.js`, adicionar um listener de clique a este botão que chame uma função `toggleTheme`.
      * [ ] `toggleTheme` deve:
        1.  Alternar o valor do atributo `data-theme` entre `light` e `dark`.
        2.  Salvar a nova preferência no `localStorage`.
        3.  Alternar o ícone do botão (lua/sol).
  * **Testes (QA):**
      * [ ] Verificar se a aplicação carrega o tema escuro por padrão se o SO estiver no modo escuro.
      * [ ] Clicar no botão de alternância e verificar se todos os elementos da UI mudam de cor suavemente.
      * [ ] Selecionar um tema, recarregar a página e verificar se a preferência foi mantida.
      * [ ] Alternar entre os temas e navegar pela aplicação, garantindo que todos os componentes (modais, notificações, etc.) respeitem o tema ativo.

#### **2. RF-17 / RNF-01: Responsividade Completa**

  * **Frontend (Desenvolvimento):**
      * [ ] Adicionar a tag `<meta name="viewport" content="width=device-width, initial-scale=1.0">` em `index.html`.
      * [ ] Em `style.css`, criar um bloco `@media (max-width: 768px)`.
      * [ ] Dentro do media query, aplicar estilos para:
        1.  Ocultar a `.sidebar` (ex: `position: fixed; left: -300px;`).
        2.  Fazer o `.main-content` ocupar 100% da largura.
        3.  Ajustar o tamanho de fontes e preenchimentos para melhor legibilidade.
      * [ ] Criar um botão "hambúrguer" para o menu móvel em `index.html` (ou via JS) e estilizá-lo para aparecer apenas no media query.
      * [ ] Em `main.js`, adicionar um listener ao botão hambúrguer que alterna uma classe (ex: `.active`) na `.sidebar`.
      * [ ] Em `style.css`, adicionar uma regra `.sidebar.active { left: 0; }` para exibir o menu.
  * **Testes (QA):**
      * [ ] Usar as ferramentas de desenvolvedor do navegador para simular diferentes tamanhos de tela (celular, tablet).
      * [ ] Verificar se a barra lateral desaparece e o botão de menu aparece abaixo de 768px de largura.
      * [ ] Testar a funcionalidade de abrir e fechar o menu lateral no modo móvel.
      * [ ] Garantir que todos os elementos interativos sejam grandes o suficiente para serem tocados facilmente.
      * [ ] Se possível, testar em um dispositivo móvel real.

#### **3. RF-18: Feedback Visual Consistente**

  * **Frontend (Desenvolvimento):**
      * [ ] Criar uma função reutilizável `showNotification(message, type, duration)` em `main.js`.
      * [ ] Esta função deve criar dinamicamente o HTML da notificação, adicioná-lo a um contêiner fixo na tela e removê-lo após a `duration`.
      * [ ] Estilizar as notificações em `style.css` com cores diferentes para `success`, `error`, e `info`, usando as variáveis de tema.
      * [ ] Refatorar todo o `main.js` para usar `showNotification` em vez de manipular o `statusMessage` diretamente.
      * [ ] Refatorar o modal de exclusão para ser gerado pela função `showConfirmationModal(message, onConfirmCallback)`, tornando-o reutilizável.
  * **Testes (QA):**
      * [ ] Acionar uma operação de sucesso (processar vídeo) e verificar se a notificação verde aparece e some.
      * [ ] Acionar um erro (URL inválida) e verificar a notificação vermelha.
      * [ ] Clicar para excluir um item e verificar se o modal de confirmação padronizado é exibido.
      * [ ] Garantir que as notificações e modais funcionem corretamente em ambos os temas (claro/escuro).

-----

### Checklist de Implementação e Testes - Fase 6: Documentação da Modularização do Arquivo do YouTube

#### 1. Requisitos Funcionais (RF)

##### RF-22: Modularização do `YouTubeHandler`

###### Desenvolvimento
* [ ] Criar arquivo `youtube_api_client.py` na pasta `src/services/`.
* [ ] Implementar a classe `YouTubeAPIClient` no arquivo `youtube_api_client.py` com os seguintes métodos:
    * [ ] `def __init__(self):` - Inicializar a classe.
    * [ ] `def get_video_info(video_id):` - Implementar lógica para obter informações do vídeo.
    * [ ] `def get_transcript(video_id):` - Implementar lógica para obter a transcrição do vídeo.
* [ ] Criar arquivo `transcript_processor.py` na pasta `src/services/`.
* [ ] Implementar a classe `TranscriptProcessor` no arquivo `transcript_processor.py` com os seguintes métodos:
    * [ ] `def __init__(self):` - Inicializar a classe.
    * [ ] `def clean_transcript(raw_transcript):` - Implementar lógica para limpar a transcrição.
* [ ] Criar arquivo `file_manager.py` na pasta `src/services/`.
* [ ] Implementar a classe `FileManager` no arquivo `file_manager.py` com os seguintes métodos:
    * [ ] `def __init__(self):` - Inicializar a classe.
    * [ ] `def save_transcript(video_id, transcript):` - Implementar lógica para salvar a transcrição em um arquivo.
* [ ] Criar arquivo `processing_service.py` na pasta `src/services/`.
* [ ] Implementar a classe `ProcessingService` no arquivo `processing_service.py` com o método:
    * [ ] `def process_video(video_id):` - Implementar lógica para orquestrar o processamento do vídeo.
* [ ] Atualizar o arquivo `history_service.py` para remover a lógica de gerenciamento de histórico do `YouTubeHandler`.
* [ ] Atualizar o arquivo `app.py` para incluir as novas classes e serviços.
* [ ] Atualizar o arquivo `download_routes.py` para utilizar os novos serviços.

###### Testes (QA)
* [ ] Testar a classe `YouTubeAPIClient`:
    * [ ] Validar que `get_video_info(video_id)` retorna informações corretas para um vídeo válido.
    * [ ] Validar que `get_transcript(video_id)` retorna a transcrição correta para um vídeo válido.
* [ ] Testar a classe `TranscriptProcessor`:
    * [ ] Validar que `clean_transcript(raw_transcript)` remove caracteres indesejados e formata a transcrição corretamente.
* [ ] Testar a classe `FileManager`:
    * [ ] Validar que `save_transcript(video_id, transcript)` salva a transcrição no formato correto e no local esperado.
* [ ] Testar a classe `ProcessingService`:
    * [ ] Validar que `process_video(video_id)` chama os métodos corretos na ordem correta e processa o vídeo como esperado.

#### 2. Requisitos Não Funcionais (RNF)

##### RNF-29: Coesão e Acoplamento

###### Desenvolvimento
* [ ] Revisar todas as classes criadas para garantir que cada uma tenha uma única responsabilidade.
* [ ] Remover dependências diretas de `utils` no `YouTubeHandler`.

###### Testes (QA)
* [ ] Validar que cada classe criada possui métodos que são coesos e que não há acoplamento excessivo entre as classes.
* [ ] Realizar uma análise de código para verificar a separação de responsabilidades.

##### RNF-30: Testabilidade Aprimorada

###### Desenvolvimento
* [ ] Implementar testes unitários para cada método nas classes `YouTubeAPIClient`, `TranscriptProcessor`, `FileManager` e `ProcessingService`.

###### Testes (QA)
* [ ] Executar os testes unitários implementados e garantir que todos passem sem falhas.
* [ ] Validar que a cobertura de testes atinge pelo menos 80% para cada classe.

#### 3. Instruções de Implementação Detalhadas

* [ ] Criar um diagrama de fluxo de dados que ilustre a interação entre `YouTubeAPIClient`, `TranscriptProcessor`, `FileManager` e `ProcessingService`.
* [ ] Documentar cada classe e método criado com comentários explicativos e exemplos de uso.

### Revisão Final
* [ ] Verificar se cada item do checklist é uma ação atômica e pode ser atribuída, executada e validada de forma independente.
* [ ] Garantir que não há ambiguidade nas instruções e que todos os nomes de arquivos, classes e métodos estão corretos e consistentes com a documentação.

---

### **Checklist de Implementação e Testes - Fase 7: Aprimoramento da Arquitetura Modular**  

#### **1. Requisitos Funcionais (RF)**  

##### **RF-23: Gerenciamento de Erros Aprimorado**  
✅ **Desenvolvimento**  
- [ ] Criar diretório `src/exceptions/` para centralizar exceções customizadas.  
- [ ] Implementar exceções personalizadas em `src/exceptions/custom_errors.py`:  
  - [ ] `class APIRequestError(Exception)` – Para erros de chamadas à API do YouTube.  
  - [ ] `class TranscriptProcessingError(Exception)` – Para falhas durante o processamento de transcrições.  
  - [ ] `class FileSaveError(Exception)` – Para problemas ao salvar arquivos.  
- [ ] Adicionar logs estruturados:  
  - [ ] Configurar `logging` em `src/config/logging_config.py`.  
  - [ ] Adicionar logs críticos em `YouTubeAPIClient`, `TranscriptProcessor` e `FileManager`.  
- [ ] Modificar `ProcessingService.process_video_task()` para capturar e tratar exceções.  

✅ **Testes (QA)**  
- [ ] Testar cenários de falha para cada exceção:  
  - [ ] Forçar `APIRequestError` simulando falhas na API do YouTube (e.g., vídeo privado).  
  - [ ] Forçar `TranscriptProcessingError` testando com transcrição malformada.  
  - [ ] Forçar `FileSaveError` simulando permissões incorretas no sistema de arquivos.  
- [ ] Verificar se os logs estão sendo registrados corretamente (`logs/app.log`).  

---  

##### **RF-24: Melhorias na Interface do Usuário**  
✅ **Desenvolvimento**  
- [ ] Adicionar **loaders** no frontend (`/static/js/ui.js`):  
  - [ ] Criar função `showLoader(containerId)` para exibir animação de carregamento.  
  - [ ] Criar função `hideLoader(containerId)` para ocultar após resposta da API.  
- [ ] Implementar feedback visual para erros (`/static/css/error.css`):  
  - [ ] Criar estilo `.error-toast` para exibir mensagens de erro temporárias.  
  - [ ] Integrar com `fetch()` em `main.js` para erros de API.  
- [ ] Garantir responsividade em telas menores (`/static/css/responsive.css`):  
  - [ ] Ajustar tabela de histórico para scroll horizontal em móveis.  
  - [ ] Redimensionar botões para melhor toque em dispositivos touch.  

✅ **Testes (QA)**  
- [ ] Testar UI em diferentes dispositivos (Chrome DevTools > Mobile View):  
  - [ ] Verificar se loaders aparecem/dissolvem corretamente.  
  - [ ] Simular erros e validar se `.error-toast` é exibido por 5 segundos.  
  - [ ] Testar tabela de histórico em resoluções < 768px.  

---  

##### **RF-25: Otimização de Desempenho**  
✅ **Desenvolvimento**  
- [ ] Adicionar **cache com Redis** em `src/cache/redis_client.py`:  
  - [ ] Configurar cliente Redis (`redis.Redis()`).  
  - [ ] Implementar decorator `@cache_response(ttl=3600)` para armazenar respostas da API.  
- [ ] Otimizar consultas ao histórico (`HistoryService.get_all()`):  
  - [ ] Adicionar índice `video_id` no banco de dados (SQL: `CREATE INDEX IF NOT EXISTS idx_video_id ON history(video_id);`).  

✅ **Testes (QA)**  
- [ ] Medir tempo de resposta antes/depois do cache:  
  - [ ] Chamar `YouTubeAPIClient.get_video_info()` duas vezes e comparar latência.  
  - [ ] Verificar se `redis-cli` mostra as keys em cache (`KEYS *`).  

---  

#### **2. Requisitos Não Funcionais (RNF)**  

##### **RNF-31: Desempenho**  
✅ **Desenvolvimento**  
- [ ] Configurar **Gzip** no Flask (`app.py`):  
  ```python
  from flask_compress import Compress
  Compress(app)
  ```
- [ ] Habilitar **HTTP/2** no servidor de produção (Nginx/Apache).  

✅ **Testes (QA)**  
- [ ] Usar Lighthouse (Chrome) para avaliar performance:  
  - [ ] Verificar se "First Contentful Paint" está abaixo de 1.5s.  
  - [ ] Validar compressão via `curl -I -H "Accept-Encoding: gzip" http://localhost:5000`.  

---  

##### **RNF-32: Usabilidade**  
✅ **Desenvolvimento**  
- [ ] Adicionar **tooltips** em botões complexos (`/static/js/tooltips.js`):  
  - [ ] Implementar `initTooltips()` usando `title` + CSS.  
- [ ] Traduzir mensagens de sistema para inglês/português (`src/locales/`).  

✅ **Testes (QA)**  
- [ ] Testar tooltips em todos os botões (`history.js`, `download.js`).  
- [ ] Verificar mudança de idioma no console: `localStorage.setItem("lang", "pt")`.  

---  

#### **3. Testes Automatizados (RF-26)**  
✅ **Desenvolvimento**  
- [ ] Criar `tests/integration/test_processing_flow.py`:  
  - [ ] Testar fluxo completo `video_id → API → transcript → saved file`.  
  - [ ] Mockar Redis para testes de cache.  
- [ ] Configurar **GitHub Actions** (`.github/workflows/tests.yml`):  
  - [ ] Executar testes unitários e de integração em PRs.  

✅ **Testes (QA)**  
- [ ] Rodar `pytest --cov=src/ --cov-report=term-missing` para validar cobertura ≥ 80%.  

---  

### **Revisão Final**  
✅ **Validações Gerais**  
- [ ] Todos os logs contêm timestamps e severity levels (`INFO`, `ERROR`).  
- [ ] Nenhum `print()` ou depuração hardcoded permanece no código.  
- [ ] README.md atualizado com instruções para cache/Redis.  

---  

**Notas:**  
- Itens marcados com ✅ exigem confirmação de dois revisores.  
- Priorizar tasks críticas (**Redis**, **Error Handling**, **UI Loaders**) antes de refinamentos.

-------

<SKIPPED_HTML_EDIT_MODE></SKIPPED_HTML_EDIT_MODE>
### **Checklist de Implementação e Testes - Fase 8: Refinamento de UX e Finalização (Antiga Fase 7)**

---

#### **1. Requisitos Funcionais (RF)**  

##### **RF-28: Sistema de Notificações**  
✅ **Desenvolvimento**  
- [ ] Criar componente `NotificationCenter` em `/static/js/notifications.js`:  
  - [ ] Implementar função `showNotification(type, message)` com tipos: `success`, `error`, `warning`.  
  - [ ] Adicionar estilos em `/static/css/notifications.css` para animações de entrada/saída.  
- [ ] Integrar notificações em ações críticas:  
  - [ ] Após download de transcrição (`success`).  
  - [ ] Em erros de API (`error`).  

✅ **Testes (QA)**  
- [ ] Forçar todos os tipos de notificação e verificar:  
  - [ ] Tempo de exibição (5s para `success`, 10s para `error`).  
  - [ ] Responsividade em mobile (ocupar no máximo 80% da largura).  

---

##### **RF-29: Loaders e Estados de Carregamento**  
✅ **Desenvolvimento**  
- [ ] Criar componentes reutilizáveis em `/static/components/loaders/`:  
  - [ ] `Spinner.js` (para ações rápidas <2s).  
  - [ ] `ProgressBar.js` (para processamentos longos, ex.: transcrição).  
- [ ] Atualizar `ProcessingService` para emitir eventos de progresso via Socket.IO.  

✅ **Testes (QA)**  
- [ ] Simular atrasos na API (ex.: `setTimeout` de 3s) e verificar:  
  - [ ] Se `ProgressBar` reflete o estágio atual (ex.: "Obtendo transcrição... 50%").  

---

##### **RF-30: Cache Estratégico**  
✅ **Desenvolvimento**  
- [ ] Adicionar cache para resultados de buscas no histórico (`HistoryService`):  
  - [ ] Implementar método `cache_search_query(query, results)` no Redis.  
- [ ] Invalidar cache após novas inserções (`TTL=1h`).  

✅ **Testes (QA)**  
- [ ] Executar 2 buscas idênticas e validar:  
  - [ ] Segunda consulta deve ser 50% mais rápida (medir com `console.time`).  

---

#### **2. Requisitos Não Funcionais (RNF)**  

##### **RNF-33: Performance Frontend**  
✅ **Desenvolvimento**  
- [ ] Otimizar bundles JavaScript:  
  - [ ] Configurar `Webpack` para code splitting (separar `vendor.js` e `app.js`).  
- [ ] Pré-carregar fontes críticas (`<link rel="preload">`).  

✅ **Testes (QA)**  
- [ ] Usar Lighthouse para auditar:  
  - [ ] "Reduce JavaScript execution time" deve ter score ≥90.  

---

##### **RNF-34: Acessibilidade**  
✅ **Desenvolvimento**  
- [ ] Adicionar atributos ARIA:  
  - [ ] `aria-live="polite"` em `NotificationCenter`.  
  - [ ] `aria-busy="true"` durante carregamentos.  
- [ ] Garantir contraste ≥4.5:1 em textos (`/static/css/contrast.css`).  

✅ **Testes (QA)**  
- [ ] Executar Axe DevTools e corrigir falhas prioritárias.  

---

##### **RNF-35: Monitoramento**  
✅ **Desenvolvimento**  
- [ ] Configurar Sentry para captura de erros no frontend (`/static/js/monitoring.js`):  
  - [ ] Inicializar com `Sentry.init({ dsn: ENV.SENTRY_DSN })`.  
- [ ] Adicionar logging de métricas no backend (`src/monitoring/prometheus.py`).  

✅ **Testes (QA)**  
- [ ] Forçar um erro no frontend e verificar se aparece no dashboard do Sentry.  

---

#### **3. Componentes Críticos**  

##### **HistoryList Component**  
✅ **Desenvolvimento**  
- [ ] Adicionar ordenação por data/alfabética em `/static/js/history.js`:  
  - [ ] Implementar botões `sort-by-date` e `sort-by-title`.  
- [ ] Paginação (10 itens por página).  

✅ **Testes (QA)**  
- [ ] Carregar 100 itens e verificar:  
  - [ ] Tempo de renderização <500ms.  

---

##### **VideoProcessor Component**  
✅ **Desenvolvimento**  
- [ ] Adicionar preview de vídeo ao inserir URL (`youtube.com/embed/ID`).  
- [ ] Validar formato de URL com regex em `main.js`:  
  ```javascript
  const YT_REGEX = /^(https?:\/\/)?(www\.)?youtube\.com\/watch\?v=([a-zA-Z0-9_-]{11})/;
  ```

✅ **Testes (QA)**  
- [ ] Testar URLs inválidas e verificar mensagem de erro.  

---

#### **4. Pré-Deploy**  
✅ **Validações Finais**  
- [ ] Testes E2E com Cypress (10 cenários críticos).  
- [ ] Verificar variáveis de ambiente em produção (`SENTRY_DSN`, `REDIS_URL`).  
- [ ] Gerar relatório de cobertura final (`pytest --cov-report html`).  

---

### **Notas para a Equipe**  
⚠️ **Prioridades:**  
1. Notificações e acessibilidade são obrigatórias para release.  
2. Performance deve ser validada em dispositivos low-end (ex.: Moto G4).  
3. Monitoramento só entra em produção após revisão de segurança.  

🔧 **Dicas:**  
- Use `localStorage.setItem('debug', 'true')` para ativar logs detalhados no frontend.  
- Commit messages devem referenciar RF/RNF (ex.: `[RF-28] Add notification system`).