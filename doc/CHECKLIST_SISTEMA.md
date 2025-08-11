# Checklist de Status do Projeto: Sistema de Transcrição YouTube

Este documento reflete o estado atual de implementação do sistema, com base na análise do código-fonte e nos requisitos definidos na documentação do projeto.

**Legenda:**
- `[x]` - Completo
- `[/]` - Parcialmente Implementado
- `[ ]` - Não Iniciado
- `[+]` - Funcionalidade Adicional Implementada (Não prevista inicialmente no checklist)

---

## Requisitos Funcionais (RF)

- **[x] RF-01: Transcrição de Vídeos Individuais**
  - [cite_start]O sistema processa uma URL de vídeo do YouTube, extrai a transcrição e a limpa de metadados e timestamps[cite: 3, 48, 58].

- **[ ] RF-02: Download de Arquivos de Mídia (Vídeo/Áudio)**
  - O sistema está focado exclusivamente na transcrição. [cite_start]A funcionalidade para baixar os arquivos de vídeo ou áudio (`.mp4`, `.mp3`) não foi implementada[cite: 31, 38].

- **[x] RF-03: Download da Transcrição em TXT**
  - [cite_start]A rota `/download_transcription/<video_id>` gera e disponibiliza para download um arquivo `.txt` com a transcrição limpa e formatada[cite: 6, 9, 10, 11, 12].

- **[/] RF-04: Interface de Usuário e Visualização da Transcrição**
  - [cite_start]A interface exibe o título, a miniatura (thumbnail) e o conteúdo da transcrição para um único vídeo processado[cite: 104, 105, 115, 117].
  - [cite_start]*Comentário: A exibição principal está funcional, mas faltam funcionalidades da documentação, como a barra lateral para histórico de sessões e a alternância de temas (claro/escuro)[cite: 144, 146].*

- **[/] RF-05: Persistência de Dados e Histórico**
  - [cite_start]Cada transcrição é salva individualmente em um arquivo JSON no diretório `data/transcriptions`[cite: 21, 52].
  - [cite_start]*Comentário: O armazenamento individual está implementado, mas não existe um sistema de gerenciamento de histórico ou um índice que permita ao usuário navegar entre as transcrições processadas anteriormente na interface[cite: 144].*

- **[ ] RF-06: Processamento de Playlists**
  - A lógica atual trata apenas URLs de vídeos individuais. Não há implementação para extrair e processar múltiplos vídeos de uma URL de playlist.

- **[+] [+] Divisão da Transcrição em Blocos (Chunks)** `[x]`
  - [cite_start]Uma funcionalidade implementada que divide a transcrição final em blocos de aproximadamente 300 palavras para facilitar o manuseio e a exibição[cite: 5, 50].

---

## Requisitos Não Funcionais (RNF)

- **[/] RNF-01: Responsividade da Interface**
  - [cite_start]O layout utiliza um contêiner com largura máxima, o que oferece uma fluidez básica[cite: 69].
  - *Comentário: O design não é totalmente responsivo, faltando `media queries` para se adaptar a telas menores como tablets e dispositivos móveis.*

- **[x] RNF-02: Tratamento de Erros e Feedback ao Usuário**
  - [cite_start]O backend retorna mensagens de erro claras para URLs inválidas ou vídeos sem legendas[cite: 2, 4].
  - [cite_start]O frontend exibe essas mensagens de erro em uma área de status dedicada[cite: 92, 109, 114].

- **[x] RNF-03: Sanitização de Entradas e Nomes de Arquivos**
  - [cite_start]Nomes de arquivos são sanitizados para remover caracteres inválidos antes de salvar o JSON ou gerar o nome do arquivo TXT para download[cite: 10, 17, 51].
  - [cite_start]URLs do YouTube são validadas no backend usando expressões regulares[cite: 27].

- **[ ] RNF-04: Comunicação em Tempo Real**
  - A comunicação atual é baseada em requisições HTTP (`fetch`). [cite_start]Não há implementação de WebSockets (Socket.IO) para atualizações de progresso em tempo real[cite: 100, 274].
  - [cite_start]*Comentário: A implementação difere do requisito[cite: 149]. [cite_start]O frontend exibe um indicador de processamento (`spinner`), mas não uma barra de progresso real[cite: 115, 82].*

- **[+] [+] Mecanismo de Fallback para Extração de Legendas** `[x]`
  - [cite_start]O sistema primeiro tenta obter a transcrição através de uma API especializada (`youtube-transcript-api`) e, em caso de falha, utiliza um método de fallback mais robusto com `yt-dlp` para garantir maior chance de sucesso[cite: 56, 64].

- **[+] [+] Estratégia para Evitar Bloqueios** `[x]`
  - [cite_start]O `youtube_handler` utiliza `User-Agents` de navegadores reais e insere um delay aleatório entre as requisições no método de fallback para simular comportamento humano e reduzir o risco de bloqueios por parte do YouTube[cite: 22, 24, 25].