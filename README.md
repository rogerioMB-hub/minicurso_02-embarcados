# UART com MicroPython — Do Eco ao Protocolo

![Banner do curso](./assets/banner.svg)

**Mini Curso 02** do Curso Técnico em Automação Industrial.

Repositório didático de comunicação serial UART com MicroPython, organizado em 10 passos progressivos — cada um introduz exatamente um conceito novo, sempre partindo do que já foi aprendido.

Ao final, o aluno terá construído, passo a passo, um mini-protocolo de comunicação bidirecional completo com frame estruturado, checksum XOR, ACK/NAK e retransmissão automática.

## Site do curso

**[https://rogerioMB-hub.github.io/minicurso_02-embarcados](https://rogerioMB-hub.github.io/minicurso_02-embarcados)**

## Sequência de passos

### Fase 1 — PC ↔ Placa via Serial Monitor

| # | Título | Conceito introduzido | Entregável |
|---|--------|----------------------|------------|
| [1](./aulas/passo01-eco-serial.md) | Eco Serial | `uart.any()`, `read()`, `write()` | Bytes ecoados de volta ao terminal |
| [2](./aulas/passo02-led-uart.md) | Controle de LED | Decisão por char, `if/elif/else` | LED ligado/desligado por comando serial |
| [3](./aulas/passo03-dicionario.md) | Dicionário de comandos | `dict`, operador `in`, despacho por chave | Respostas por extenso via lookup table |

### Fase 2 — Estrutura e robustez

| # | Título | Conceito introduzido | Entregável |
|---|--------|----------------------|------------|
| [4](./aulas/passo04-parsing.md) | Parsing com terminador | Buffer, `'\n'`, `split()` | Comandos com argumento: `LED:L`, `MSG:texto` |
| [5](./aulas/passo05-maquina-estados.md) | Máquina de estados | FSM — IDLE / RECEBENDO / PROCESSANDO | Recepção robusta com estados explícitos |
| [6](./aulas/passo06-buffer-timeout.md) | Buffer e timeout | `ticks_ms()`, limite de buffer | Auto-recuperação sem reset manual |

### Fase 3 — Placa ↔ Placa (loopback)

| # | Título | Conceito introduzido | Entregável |
|---|--------|----------------------|------------|
| [7](./aulas/passo07-loopback.md) | Loopback físico | UART1 ↔ UART2, fios cruzados, estatísticas | Comunicação real entre UARTs |
| [8](./aulas/passo08-controladora-periferica.md) | Controladora–Periférica | Papéis assimétricos, leitura de sensor | Protocolo `REQ:SENSOR` / `DADO:SENSOR:VALOR` |
| [9](./aulas/passo09-checksum.md) | Checksum XOR | Integridade de dados, detecção de erros | Frame `PAYLOAD*XX` com verificação |

### Fase 4 — Protocolo completo

| # | Título | Conceito introduzido | Entregável |
|---|--------|----------------------|------------|
| [10](./aulas/passo10-protocolo.md) | Mini-protocolo completo | SOF/EOF, ACK/NAK, retransmissão, módulo compartilhado | Frame `$TIPO:PAYLOAD*XX#` com retransmissão automática |

---

## Estrutura

```
minicurso_02-embarcados/
├── index.md                          ← página inicial
├── _config.yml                       ← configuração Jekyll / GitHub Pages
├── COMO-PUBLICAR.md
├── assets/
│   └── banner.svg
└── aulas/
    ├── passo01-eco-serial.md
    ├── passo02-led-uart.md
    ├── passo03-dicionario.md
    ├── passo04-parsing.md
    ├── passo05-maquina-estados.md
    ├── passo06-buffer-timeout.md
    ├── passo07-loopback.md
    ├── passo08-controladora-periferica.md
    ├── passo09-checksum.md
    └── passo10-protocolo.md
```

## Pré-requisitos

- Python básico (variáveis, `if/else`, `while`, funções)
- Recomendado: Mini Curso 01 — Lógica Digital com ESP32

## Licença

MIT — livre para uso educacional e comercial com atribuição.
