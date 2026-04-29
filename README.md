# UART com MicroPython — Do Eco ao Protocolo

![Banner do curso](./assets/banner.svg)

**Mini Curso 02** do Curso Técnico em Automação Industrial.

Repositório didático de comunicação serial UART com MicroPython, organizado em 10 passos progressivos — cada um introduz exatamente um conceito novo, sempre partindo do que já foi aprendido.

Ao final, o aluno terá construído, passo a passo, um mini-protocolo de comunicação bidirecional completo com frame estruturado, checksum XOR, ACK/NAK e retransmissão automática.

## Site do curso

**[https://rogerioMB-hub.github.io/minicurso_02-embarcados](https://rogerioMB-hub.github.io/minicurso_02-embarcados)**

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
  **[https://rogerioMB-hub.github.io/minicurso_01-embarcados](https://rogerioMB-hub.github.io/minicurso_01-embarcados)**

## Licença

MIT — livre para uso educacional e comercial com atribuição.
