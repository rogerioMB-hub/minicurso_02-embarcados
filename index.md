---
layout: default
title: Início
---

# UART com MicroPython — Do Eco ao Protocolo

![Banner do curso](./assets/banner.svg)

> **Mini Curso 02** — Estudo dirigido para alunos do Curso Técnico em Automação Industrial.  
> Plataforma: ESP32 com MicroPython · Simulador: [Wokwi](https://wokwi.com)  
> *Continuação de: Mini Curso 01 — Lógica Digital com ESP32*

---

## Sobre o curso

Este material é um **mini-curso de apoio ao estudo da comunicação serial baseada em UART**. Ele não pressupõe experiência prévia com protocolos de comunicação — apenas familiaridade com Python básico e, de preferência, com o Mini Curso 01.

O objetivo é conduzir o aluno desde o conceito mais simples possível — um byte que vai e volta — até a construção de um **mini-protocolo bidirecional completo**, com frame estruturado, verificação de integridade e retransmissão automática. Ao final, o aluno reconhecerá, nos protocolos industriais reais como Modbus e CANbus, os mesmos elementos que construiu com as próprias mãos.

---

## Linha de raciocínio do curso

A construção foi pensada para que **cada passo introduza exatamente um conceito novo**, sempre partindo do que já foi aprendido. Não há saltos — cada ideia é o alicerce da próxima.

O percurso segue quatro fases naturais:

**Fase 1 — Comunicação básica com o terminal**
O aluno começa com o mais simples: um byte enviado pelo terminal volta para o terminal. A partir daí, esse byte começa a ter significado — controla um LED, consulta um dicionário. O foco é entender o ciclo *receber → decidir → responder*.

**Fase 2 — Estrutura e robustez**
Bytes soltos dão lugar a mensagens estruturadas. O aluno aprende a acumular bytes em um buffer até receber um terminador, a organizar o comportamento do sistema em estados explícitos (máquina de estados), e a proteger o sistema contra mensagens incompletas com timeout e limite de buffer. Esses três mecanismos juntos formam a espinha dorsal de qualquer receptor serial profissional.

**Fase 3 — Comunicação entre periféricos**
A comunicação sai do terminal e passa a acontecer entre duas UARTs do mesmo ESP32, conectadas por fios reais. O aluno atribui papéis distintos às UARTs — controladora e periférica — e implementa o modelo de requisição e resposta usado pelo Modbus. Adiciona então um checksum XOR para detectar corrupção de dados em trânsito.

**Fase 4 — Protocolo completo**
Tudo se une em um mini-protocolo com frame estruturado (`$TIPO:PAYLOAD*XX#`), confirmação (ACK/NAK) e retransmissão automática. O código do protocolo é extraído para um módulo compartilhado — exatamente como se faz em projetos reais.

---

## Roteiro de aprendizado

### Fase 1 — PC ↔ Placa via Serial Monitor
*Um dispositivo, sem fios extras, feedback imediato.*

| Passo | Título | Conceito introduzido | Entregável |
|-------|--------|----------------------|------------|
| [1](./aulas/passo01-eco-serial) | Eco Serial | `uart.read()`, `uart.write()` | Bytes ecoados de volta ao terminal |
| [2](./aulas/passo02-led-uart) | Controle de LED | Decisão por char, `if/elif/else` | LED ligado/desligado por comando serial |
| [3](./aulas/passo03-dicionario) | Dicionário de comandos | `dict`, operador `in`, despacho por chave | Respostas por extenso via lookup table |

### Fase 2 — Estrutura e robustez
*Ainda um dispositivo, mas com comunicação estruturada e à prova de falhas.*

| Passo | Título | Conceito introduzido | Entregável |
|-------|--------|----------------------|------------|
| [4](./aulas/passo04-parsing) | Parsing com terminador | Buffer, terminador `'\n'`, `split()` | Comandos com argumento: `LED:L`, `MSG:texto` |
| [5](./aulas/passo05-maquina-estados) | Máquina de estados | FSM — IDLE / RECEBENDO / PROCESSANDO | Recepção robusta com estados explícitos |
| [6](./aulas/passo06-buffer-timeout) | Buffer e timeout | `ticks_ms()`, limite de buffer | Auto-recuperação sem reset manual |

### Fase 3 — Placa ↔ Placa (loopback)
*Duas UARTs no mesmo ESP32, fios cruzados, comunicação de hardware real.*

| Passo | Título | Conceito introduzido | Entregável |
|-------|--------|----------------------|------------|
| [7](./aulas/passo07-loopback) | Loopback físico | UART1 ↔ UART2, fios cruzados | Comunicação real entre duas UARTs |
| [8](./aulas/passo08-controladora-periferica) | Controladora–Periférica | Papéis assimétricos, leitura de sensor | Protocolo `REQ:SENSOR` / `DADO:SENSOR:VALOR` |
| [9](./aulas/passo09-checksum) | Checksum XOR | Integridade de dados, detecção de erros | Frame `PAYLOAD*XX` com verificação |

### Fase 4 — Protocolo completo
*Tudo junto: frame estruturado, ACK/NAK e retransmissão automática.*

| Passo | Título | Conceito introduzido | Entregável |
|-------|--------|----------------------|------------|
| [10](./aulas/passo10-protocolo) | Mini-protocolo completo | SOF/EOF, ACK/NAK, retransmissão, módulo compartilhado | Frame `$TIPO:PAYLOAD*XX#` com retransmissão automática |

---

## Simulação no Wokwi

Todos os passos incluem arquivos Wokwi prontos, disponíveis na pasta `wokwi/` de cada passo no repositório.

- **Fases 1 e 2** — 1 ESP32 com Serial Monitor, sem fios extras
- **Fases 3 e 4** — 1 ESP32 com loopback: fios externos entre GPIO4→GPIO16 e GPIO17→GPIO5

> **Por que dois arquivos de código nos passos 1 a 6?**  
> O `$serialMonitor` do Wokwi entrega bytes com latência de simulação, exigindo leitura bloqueante (`uart.read(1)`). Na placa real, o padrão correto é não bloqueante (`uart.any()`). Cada passo traz `main_wokwi.py` e `main_placa.py` com a explicação detalhada do motivo.

---

## Pré-requisitos

| Item | Detalhe |
|------|---------|
| Hardware | ESP32 DevKit C v4 — 1 placa |
| Firmware | MicroPython instalado |
| IDE | [Thonny](https://thonny.org) — para uso com placa física |
| Simulador | [Wokwi](https://wokwi.com) — para uso online, sem instalação |
| Conhecimento | Python básico: variáveis, `if/else`, `while`, funções |

> Recomendado: ter concluído o **Mini Curso 01 — Lógica Digital com ESP32** ou ter familiaridade com `machine.Pin` e `machine.UART`.

---

## Conexão com protocolos industriais reais

Ao concluir o Mini Curso 02, o aluno reconhecerá os seguintes elementos em protocolos como Modbus RTU, CANbus e HDLC:

| Conceito do curso | Equivalente industrial |
|-------------------|----------------------|
| Buffer + terminador `'\n'` | Delimitador de frame (Modbus: silêncio de 3,5 bits) |
| Máquina de estados | Base de toda implementação de protocolo |
| Timeout + limite de buffer | Recuperação de erros em TCP, Modbus |
| Controladora–Periférica | Mestre–Escravo Modbus RTU |
| Checksum XOR | CRC-16 do Modbus, CRC-32 do Ethernet |
| SOF / EOF | Flags de início/fim de frame do HDLC e PPP |
| ACK / NAK + retransmissão | Confirmação no XMODEM, TCP, Modbus |

---

## Repositório

```
git clone https://github.com/rogerioMB-hub/minicurso_02-embarcados.git
```

Contribuições e correções são bem-vindas via *Issues* ou *Pull Requests*.
