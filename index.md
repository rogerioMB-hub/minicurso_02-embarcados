---
layout: default
title: Início
---

# UART com MicroPython — Do Eco ao Protocolo

![Banner do curso](./assets/banner.svg)

> **Mini Curso 02** para o **Curso Técnico em Automação Industrial**  
> Plataforma: ESP32 com MicroPython · Simulador: [Wokwi](https://wokwi.com)  
> *Continuação de: Sistemas Embarcados — Lógica Digital com ESP32 (Mini Curso 01)*

---

## Sobre o curso

Este material parte do zero na comunicação serial e conduz o aluno — passo a passo — até a construção de um **mini-protocolo bidirecional completo** com frame estruturado, checksum XOR e retransmissão automática.

Cada passo introduz **exatamente um conceito novo**, sempre partindo do que já foi aprendido. Ao final, o aluno terá construído, com as próprias mãos, o mesmo mecanismo presente em protocolos industriais reais como **Modbus** e **CANbus**.

---

## Roteiro de aprendizado

### Fase 1 — PC ↔ Placa via Serial Monitor
*Um dispositivo, sem fios extras, feedback imediato.*

| Passo | Título | Conceito introduzido |
|-------|--------|----------------------|
| [1](./aulas/passo01-eco-serial) | Eco Serial | `uart.any()`, `read()`, `write()` |
| [2](./aulas/passo02-led-uart) | Controle de LED | Decisão por char, `if/elif/else` |
| [3](./aulas/passo03-dicionario) | Dicionário de comandos | `dict`, operador `in`, despacho por chave |

### Fase 2 — Estrutura e robustez
*Ainda um dispositivo, mas com comunicação estruturada e à prova de falhas.*

| Passo | Título | Conceito introduzido |
|-------|--------|----------------------|
| [4](./aulas/passo04-parsing) | Parsing com terminador | Buffer, terminador `'\n'`, `split()` |
| [5](./aulas/passo05-maquina-estados) | Máquina de estados | FSM — IDLE / RECEBENDO / PROCESSANDO |
| [6](./aulas/passo06-buffer-timeout) | Buffer e timeout | `ticks_ms()`, limite de buffer, auto-recuperação |

### Fase 3 — Placa ↔ Placa (loopback)
*Duas UARTs no mesmo ESP32, fios cruzados, comunicação de hardware real.*

| Passo | Título | Conceito introduzido |
|-------|--------|----------------------|
| [7](./aulas/passo07-loopback) | Loopback físico | UART1 ↔ UART2, GND, estatísticas |
| [8](./aulas/passo08-controladora-periferica) | Controladora–Periférica | Papéis assimétricos, leitura de sensor |
| [9](./aulas/passo09-checksum) | Checksum XOR | Integridade de dados, detecção de erros |

### Fase 4 — Protocolo completo
*Tudo junto: frame estruturado, ACK/NAK e retransmissão automática.*

| Passo | Título | Conceito introduzido |
|-------|--------|----------------------|
| [10](./aulas/passo10-protocolo) | Mini-protocolo | SOF/EOF, tipos de frame, retransmissão, módulo compartilhado |

---

## Simulação no Wokwi

Todos os passos incluem um projeto Wokwi pronto para uso:

- **Fase 1 e 2** — 1 ESP32 com Serial Monitor (sem fios extras)
- **Fase 3 e 4** — 1 ESP32 com loopback: fios externos entre GPIO4→GPIO16 e GPIO17→GPIO5

> Os arquivos `diagram.json`, `main.py` e `wokwi.toml` de cada passo estão disponíveis no repositório GitHub.

---

## Pré-requisitos

| Item | Detalhe |
|------|---------|
| Hardware | ESP32 (1 placa) |
| Firmware | MicroPython instalado |
| IDE | [Thonny](https://thonny.org) — para uso com placa física |
| Simulador | [Wokwi](https://wokwi.com) — para uso online |
| Conhecimento | Python básico: variáveis, `if/else`, `while`, funções |

> Recomendado: ter concluído o **Mini Curso 01 — Lógica Digital com ESP32** ou ter familiaridade com `machine.Pin` e `machine.UART`.

---

## Relação com protocolos do mundo real

| Conceito aprendido | Onde aparece |
|--------------------|-------------|
| Frame com SOF/EOF | HDLC, PPP, Modbus RTU |
| Checksum / CRC | Modbus, CAN bus, NMEA 0183 |
| ACK / NAK | Modbus, XMODEM, HTTP/1.1 |
| Controladora–Periférica | Modbus, I²C, SPI |
| Máquina de estados | Toda implementação de protocolo profissional |

---

## Repositório

```
git clone https://github.com/rogerioMB-hub/minicurso-uart.git
```

Contribuições e correções são bem-vindas via *Issues* ou *Pull Requests*.
