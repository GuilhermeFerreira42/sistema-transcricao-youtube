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

### **2. Fase 6: Aprimoramento da Arquitetura Modular**

**2.1. Objetivo**

Implementar novas funcionalidades e otimizar recursos existentes, capitalizando sobre a arquitetura modular estabelecida na Fase 5 para expandir as capacidades de processamento e aprimorar as ferramentas de gerenciamento de histórico.

**2.2. Requisitos Funcionais (RF)**

**2.2.1. RF-11: Busca Abrangente no Histórico**

*   **Descrição:** O sistema deve permitir que o usuário busque transcrições no histórico usando múltiplos critérios, incluindo termos de pesquisa, período de data, duração do vídeo e tipo de conteúdo (vídeo individual ou playlist).
*   **Critérios de Aceitação:**
    *   **2.2.1.1. Endpoint de Busca (Backend):**
        *   [ ] Criar um novo endpoint `GET /search_history` em `backend/routes/history_routes.py`.
        *   [ ] Este endpoint deve aceitar parâmetros de query string para os critérios de busca: `q` (termo de pesquisa), `start_date` (ISO 8601), `end_date` (ISO 8601), `duration` (`short`, `medium`, `long`), `type` (`video`, `playlist`).
        *   [ ] O endpoint deve chamar um método de busca no `HistoryService` e retornar os resultados filtrados como um array JSON.
    *   **2.2.1.2. Lógica de Busca (HistoryService):**
        *   [ ] Implementar o método `search(self, query="", start_date=None, end_date=None, duration=None, content_type=None)` em `backend/services/history_service.py`.
        *   [ ] Este método deve carregar todas as entradas do histórico e aplicar os filtros sequencialmente.
        *   [ ] A filtragem por `query` deve ser case-insensitive e buscar no `title` e no `transcript` (se disponível no JSON do histórico ou carregado sob demanda).
        *   [ ] A filtragem por `start_date` e `end_date` deve comparar com o campo `created_at` da entrada.
        *   [ ] A filtragem por `duration` deve considerar: `short` (< 5 minutos / 300 segundos), `medium` (5-20 minutos / 300-1200 segundos), `long` (> 20 minutos / 1200 segundos). O campo `duration` deve ser adicionado aos metadados do vídeo no `history.json` durante o salvamento.
        *   [ ] A filtragem por `type` deve considerar o campo `type` (`video` ou `playlist`) da entrada.
        *   [ ] A busca deve ser otimizada para volumes moderados de dados (até 1000 entradas) sem a necessidade de um banco de dados relacional.
    *   **2.2.1.3. Interface de Busca (Frontend):**
        *   [ ] Adicionar uma interface de busca avançada na barra lateral do histórico (`frontend/static/js/ui.js`, `frontend/templates/index.html`).
        *   [ ] Incluir campos de input para termo de pesquisa, seletores de data (início/fim), um dropdown para duração e um dropdown para tipo de conteúdo.
        *   [ ] Implementar um mecanismo de "debounce" (300ms) para o campo de pesquisa textual para evitar requisições excessivas ao backend.
        *   [ ] Um botão "Aplicar Filtros" deve ser visível para aplicar os filtros de data, duração e tipo.
        *   [ ] Os resultados da busca devem ser renderizados na lista do histórico em tempo real.
    *   **2.2.1.4. Integração API (Frontend):**
        *   [ ] Adicionar um método `searchHistory(filters)` em `frontend/static/js/api.js` para chamar o novo endpoint `GET /search_history`.
*   **Status:** Não Iniciado.

**2.2.2. RF-12: Botão de Navegação "Voltar"**

*   **Descrição:** O sistema deve fornecer um botão "Voltar para a Playlist" quando o usuário estiver visualizando uma transcrição individual que faz parte de uma playlist.
*   **Critérios de Aceitação:**
    *   **2.2.2.1. Exibição Condicional:**
        *   [ ] Quando a área central de visualização estiver exibindo uma transcrição de vídeo individual que possui um `playlist_id` associado (indicando que faz parte de uma playlist), um botão "Voltar para a Playlist" deve ser exibido.
        *   [ ] O botão deve ser posicionado de forma proeminente e consistente na interface (ex: próximo ao título do vídeo ou na barra de ações).
        *   [ ] O botão não deve ser exibido se o vídeo não pertencer a uma playlist ou se a visualização atual for de uma playlist completa.
    *   **2.2.2.2. Funcionalidade de Navegação:**
        *   [ ] Ao clicar no botão, o frontend deve carregar e exibir a visualização completa da playlist à qual o vídeo pertence.
        *   [ ] A navegação deve ser feita via JavaScript, sem recarregar a página completa, mantendo a experiência de Single Page Application (SPA).
*   **Status:** Não Iniciado.

**2.2.3. RF-13: Exibição do Link Original do Vídeo**

*   **Descrição:** O sistema deve exibir o link original do vídeo do YouTube na interface de visualização da transcrição, permitindo que o usuário acesse diretamente o vídeo no YouTube.
*   **Critérios de Aceitação:**
    *   **2.2.3.1. Link Visível:**
        *   [ ] O link completo do vídeo do YouTube deve ser exibido de forma clara e acessível na área central de visualização da transcrição.
    *   **2.2.3.2. Abertura em Nova Aba: ```markdown
        *   [ ] O link deve ser clicável e abrir o vídeo correspondente no YouTube em uma nova aba.
    *   **2.2.3.3. Links de Playlist (se aplicável):**
        *   [ ] Para vídeos que fazem parte de uma playlist, o link deve ser formatado para levar ao vídeo específico dentro do contexto da playlist (ex: `https://www.youtube.com/watch?v=VIDEO_ID&list=PLAYLIST_ID&index=VIDEO_INDEX`).
        *   [ ] O campo `playlist_index` deve ser adicionado aos metadados do vídeo no `history.json` durante o salvamento, se o vídeo for processado como parte de uma playlist.
*   **Status:** Não Iniciado.

**2.2.4. RF-14: Navegação para Página Inicial**

*   **Descrição:** O sistema deve fornecer um logotipo "Home" clicável no cabeçalho que leve o usuário de volta à página inicial do sistema (lista de histórico).
*   **Critérios de Aceitação:**
    *   **2.2.4.1. Elemento "Home":**
        *   [ ] Um logotipo ou texto "Home" (ex: "YouTube Transcriber") deve ser exibido no canto superior esquerdo do cabeçalho da aplicação.
        *   [ ] O elemento deve ser visualmente identificável como um botão ou link de navegação.
    *   **2.2.4.2. Funcionalidade de Navegação:**
        *   [ ] Ao clicar no elemento "Home", o frontend deve reinicializar a interface para o estado inicial, exibindo a lista completa do histórico e limpando a área de visualização central (ou exibindo uma mensagem de boas-vindas).
        *   [ ] A navegação deve ser feita via JavaScript, sem recarregar a página completa.
*   **Status:** Não Iniciado.

**2.2.5. RF-15: Processamento de Múltiplas URLs**

*   **Descrição:** O sistema deve permitir que o usuário insira múltiplas URLs do YouTube de uma vez para processamento em lote.
*   **Critérios de Aceitação:**
    *   **2.2.5.1. Interface de Entrada:**
        *   [ ] Adicionar uma área de texto (`textarea`) na interface principal onde o usuário pode inserir várias URLs, uma por linha.
        *   [ ] Um botão "Processar Múltiplas URLs" deve ser disponibilizado.
    *   **2.2.5.2. Validação Individual (Backend):**
        *   [ ] Criar um novo endpoint `POST /process_urls` em `backend/routes/transcription_routes.py` que aceita um array de URLs no corpo da requisição JSON.
        *   [ ] O backend deve validar cada URL individualmente usando as funções utilitárias existentes (ex: `extract_video_id`).
        *   [ ] Apenas as URLs válidas e únicas devem ser consideradas para processamento; URLs inválidas ou duplicadas devem ser ignoradas sem interromper o processo.
    *   **2.2.5.3. Processamento em Lote (Backend):**
        *   [ ] O `TranscriptionService` deve ser adaptado ou um novo método deve ser criado para orquestrar o processamento sequencial de cada URL válida.
        *   [ ] Para cada URL, o processo de transcrição (chamando `download_and_clean_transcript`) deve ser iniciado.
        *   [ ] O backend deve retornar um array de resultados, indicando o status (`success` ou `error`) e uma mensagem para cada URL processada.
    *   **2.2.5.4. Feedback ao Usuário (Frontend):**
        *   [ ] Durante o processamento em lote, o frontend deve exibir um feedback claro e detalhado para cada URL (ex: "Processando URL X...", "URL Y processada com sucesso", "Erro ao processar URL Z: [mensagem de erro]").
        *   [ ] Um resumo final do processo (ex: "X URLs processadas com sucesso, Y com erro") deve ser exibido.
        *   [ ] O histórico deve ser atualizado automaticamente após a conclusão do processamento em lote.
*   **Status:** Não Iniciado.

**2.3. Requisitos Não Funcionais (RNF)**

**2.3.1. RNF-15: Modularização do Código Frontend**

*   **Descrição:** O código frontend deve ser organizado em módulos especializados com responsabilidades claramente definidas, conforme iniciado na Fase 5.
*   **Critérios de Aceitação:**
    *   **2.3.1.1. Redução de `main.js`:**
        *   [ ] O arquivo `frontend/static/js/main.js` deve ser reduzido para apenas a lógica de inicialização do aplicativo.
    *   **2.3.1.2. Responsabilidade Única:**
        *   [ ] Cada módulo deve ter uma única responsabilidade bem definida, sem misturar lógicas.
    *   **2.3.1.3. Comunicação entre Módulos:**
        *   [ ] A comunicação entre módulos deve seguir padrões claramente definidos.
    *   **2.3.1.4. Execução Imediata:**
        *   [ ] Nenhum código deve ser executado imediatamente ao carregar um script de módulo (exceto definições de classes/funções e exportações).
*   **Status:** Parcialmente Implementado (Requer revisão e refinamento contínuos).

**2.3.2. RNF-16: Identidade Visual do Navegador (Favicon)**

*   **Descrição:** O sistema deve ter um favicon personalizado que identifique visualmente o aplicativo no navegador.
*   **Critérios de Aceitação:**
    *   **2.3.2.1. Arquivo Favicon:**
        *   [ ] Um arquivo `favicon.ico` deve ser adicionado ao diretório `frontend/static/img/`.
    *   **2.3.2.2. Referência HTML:**
        *   [ ] O favicon deve ser referenciado corretamente no `<head>` do `frontend/templates/index.html`.
    *   **2.3.2.3. Visibilidade:**
        *   [ ] O favicon deve ser visível e reconhecível nas abas do navegador, favoritos e atalhos em diferentes navegadores e sistemas operacionais.
    *   **2.3.2.4. Representação:**
        *   [ ] O favicon deve representar a identidade do aplicativo (transcrição de vídeos).
*   **Status:** Não Iniciado.

**2.3.3. RNF-25: Desempenho com Grandes Volumes de Dados**

*   **Descrição:** O sistema deve manter desempenho aceitável mesmo com grandes volumes de dados no histórico (1000+ entradas).
*   **Critérios de Aceitação:**
    *   **2.3.3.1. Busca no Histórico:**
        *   [ ] A busca no histórico deve retornar resultados em menos de 1 segundo com 1000 entradas.
    *   **2.3.3.2. Paginação/Virtualização (Frontend):**
        *   [ ] Para listas de histórico com mais de 50 entradas, o frontend deve implementar paginação ou virtualização de listas.
    *   **2.3.3.3. Carregamento Inicial:**
        *   [ ] O carregamento inicial do histórico não deve travar a interface do usuário.
    *   **2.3.3.4. Otimização de Memória (Backend):**
        *   [ ] O `HistoryService` deve otimizar o carregamento e manipulação do `history.json`.
*   **Status:** Não Iniciado.

**2.3.4. RNF-26: Feedback Visual para Operações em Lote**

*   **Descrição:** O sistema deve fornecer feedback claro e detalhado durante operações de processamento em lote.
*   **Critérios de Aceitação:**
    *   **2.3.4.1. Progresso Individual:**
        *   [ ] Durante o processamento de múltiplas URLs, o usuário deve ver o progresso de cada URL individualmente.
    *   **2.3.4.2. Status Visual:**
        *   [ ] O sistema deve indicar visualmente quais URLs foram processadas com sucesso e quais falharam.
    *   **2.3.4.3. Resumo Final:**
        *   [ ] Um resumo deve ser exibido ao final do processamento em lote.
    *   **2.3.4.4. Cancelamento:**
        *   [ ] O usuário deve poder cancelar o processamento em lote a qualquer momento.
*   **Status:** Não Iniciado.

---

### **3. Fase 7: Refinamento de UX e Finalização**

**3.1. Objetivo**

Refinar a aparência visual do sistema, garantir que ele seja totalmente acessível em diferentes dispositivos e implementar a personalização de temas, entregando uma experiência de usuário coesa e profissional.

**3.2. Requisitos Funcionais (RF)**

**3.2.1. RF-16: Temas de Interface**

*   **Descrição:** O sistema deve oferecer opção de tema claro e escuro.
*   **Critérios de Aceitação:**
    *   **3.2.1.1. Botão de Alternância:**
        *   [ ] Deve haver um botão de alternância de tema visível e clicável no cabeçalho da aplicação.
    *   **3.2.1.2. Persistência da Preferência:**
        *   [ ] A preferência de tema do usuário deve ser salva no `localStorage`.
    *   **3.2.1.3. Aplicação Consistente:**
        *   [ ] Todos os elementos da interface devem respeitar o tema selecionado.
    *   **3.2.1.4. Detecção de Preferência do Sistema:**
        *   [ ] O sistema deve detectar a preferência de tema do sistema operacional do usuário.
    *   **3.2.1.5. Transição Suave:**
        *   [ ] A transição entre temas deve ser suave.
*   **Status:** Não Iniciado.

**3.2.2. RF-17: Responsividade Completa**

*   **Descrição:** A interface do sistema deve se adaptar fluidamente a diferentes larguras de tela.
*   **Critérios de Aceitação:**
    *   **3.2.2.1. Barra Lateral em Mobile:**
        *   [ ] A barra lateral deve estar oculta por padrão em telas menores.
        *   [ ] Um ícone de menu "hambúrguer" deve ser visível.
    *   **3.2.2.2. Conteúdo Principal Responsivo:**
        *   [ ] O conteúdo principal deve se ajustar automaticamente.
    *   **3.2.2.3. Elementos Tocáveis:**
        *   [ ] Todos os elementos interativos devem ter um tamanho mínimo de 44x44px.
    *   **3.2.2.4. Testes em Dispositivos Reais:**
        *   [ ] A interface deve ser testada em dispositivos reais.
*   **Status:** Parcialmente Implementado.

**3.2.3. RF-18: Feedback Visual Consistente**

*   **Descrição:** O sistema deve exibir modais ou notificações visualmente consistentes.
*   **Critérios de Aceitação:**
    *   **3.2.3.1. Componente Padronizado:**
        *   [ ] Todas as mensagens de sucesso, erro e confirmação devem usar um componente de UI padronizado.
    *   **3.2.3.2. Tempo de Exibição:**
        *   [ ] Mensagens de sucesso devem desaparecer após 3 segundos.
        *   [ ] Mensagens de erro devem desaparecer após 5 segundos.
    *   **3.2.3.3. Paleta de Cores:**
        *   [ ] As cores do componente de feedback devem seguir uma paleta consistente.
    *   **3.2.3.4. Acessibilidade:**
        *   [ ] O componente deve ser acessível via teclado e compatível com leitores de tela.
    *   **3.2.3.5. Fechamento Manual:**
        *   [ ] O usuário deve poder fechar manualmente notificações.
*   **Status:** Parcialmente Implementado.

**3.3. Requisitos Não Funcionais (RNF)**

**3.3.1. RNF-01: Responsividade da Interface**

*   **Descrição:** A interface deve ser responsiva e funcionar em diferentes tamanhos de tela.
*   **Critérios de Aceitação:**
    *   [ ] O layout deve se adaptar fluidamente.
    *   [ ] Elementos de interface devem ajustar seu tamanho.
    *   [ ] Testes em múltiplos dispositivos e navegadores.
    *   [ ] Desempenho aceitável em diferentes resoluções.
*   **Status:** Parcialmente Implementado.

**3.3.2. RNF-06: Usabilidade Básica**

*   **Descrição:** O sistema deve oferecer uma experiência de usuário intuitiva.
*   **Critérios de Aceitação:**
    *   [ ] Interface limpa e organizada.
    *   [ ] Fluxo de trabalho lógico e previsível.
    *   [ ] Feedback visual adequado.
    *   [ ] Documentação de ajuda acessível.
*   **Status:** Parcialmente Implementado.

**3.3.3. RNF-07: Comportamento da Rolagem**

*   **Descrição:** O sistema deve gerenciar a rolagem da conversa de forma inteligente.
*   **Critérios de Aceitação:**
    *   [ ] Rolagem automática para baixo quando próxima ao final.
    *   [ ] Botão "Ir para o Final" quando o usuário estiver rolando para cima.
    *   [ ] Não forçar rolagem para baixo se o usuário estiver lendo mensagens antigas.
*   **Status:** Concluído.

**3.3.4. RNF-08: Temas de Interface**

*   **Descrição:** O sistema deve oferecer opção de tema claro e escuro.
*   **Critérios de Aceitação:**
    *   [ ] Botão de alternância visível.
    *   [ ] Preferência salva no localStorage.
    *   [ ] Detecção automática da preferência do sistema.
    *   [ ] Transição suave entre temas.
*   **Status:** Não Iniciado.

**3.3.5. RNF-27: Consistência Visual**

*   **Descrição:** O sistema deve ter um design visual consistente.
*   **Critérios de Aceitação:**
    *   [ ] Componentes reutilizáveis devem ter estilo consistente.
    *   [ ] Não deve haver estilos "hardcoded".
    *   [ ] Tipografia deve seguir uma hierarquia clara.
    *   [ ] Estados de interação devem ser consistentes.
*   **Status:** Parcialmente Implementado.

**3.3.6. RNF-28: Acessibilidade (A11y)**

*   **Descrição:** O sistema deve seguir padrões básicos de acessibilidade.
*   **Critérios de Aceitação:**
    *   [ ] Contraste adequado entre texto e fundo.
    *   [ ] Todos os elementos interativos devem ser acessíveis via teclado.
    *   [ ] Uso adequado de ARIA labels.
    *   [ ] Estrutura semântica HTML correta.
*   **Status:** Não Iniciado.

---

### **Checklist de Conclusão de Fases**

**Fase 5: Modularização Estrutural**
*   [ ] Todos os requisitos funcionais (RF) implementados.
*   [ ] Todos os requisitos não funcionais (RNF) implementados.
*   [ ] Código revisado e testado.
*   [ ] Documentação atualizada.

**Fase 6: Aprimoramento da Arquitetura Modular**
*   [ ] Todos os requisitos funcionais (RF) implementados.
*   [ ] Todos os requisitos não funcionais (RNF) implementados.
*   [ ] Código revisado e testado.
*   [ ] Documentação atualizada.

**Fase 7: Refinamento de UX e Finalização**
*   [ ] Todos os requisitos funcionais (RF) implementados.
*   [ ] Todos os requisitos não funcionais (RNF) implementados.
*   [ ] Código revisado e testado.
*   [ ] Documentação atualizada.