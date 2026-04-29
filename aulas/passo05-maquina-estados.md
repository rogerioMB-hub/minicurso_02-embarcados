---
layout: default
title: "Passo 5 — Máquina de Estados para Recepção UART"
---

# Passo 5 — Máquina de Estados para Recepção UART

> **Duração estimada:** 30 minutos  
> **Fase:** 2 de 4 — Estrutura e robustez

---

## Simulação e Código

### Arquivos do projeto Wokwi

| Arquivo | Descrição | Link |
|---------|-----------|------|
| `diagram.json` | Circuito no simulador | [abrir](https://github.com/rogerioMB-hub/minicurso_02-embarcados/blob/main/aulas/passo05-maquina-estados/wokwi/diagram.json) |
| `wokwi.toml` | Configuração do projeto | [abrir](https://github.com/rogerioMB-hub/minicurso_02-embarcados/blob/main/aulas/passo05-maquina-estados/wokwi/wokwi.toml) |
| `main_wokwi.py` | Código para o Wokwi | [abrir](https://github.com/rogerioMB-hub/minicurso_02-embarcados/blob/main/aulas/passo05-maquina-estados/wokwi/main_wokwi.py) |
| `main_placa.py` | Código para ESP32 / Pico real | [abrir](https://github.com/rogerioMB-hub/minicurso_02-embarcados/blob/main/aulas/passo05-maquina-estados/wokwi/main_placa.py) |

> **Como usar:** copie o conteúdo de cada arquivo para as abas correspondentes em [wokwi.com/projects/new/micropython-esp32](https://wokwi.com/projects/new/micropython-esp32).

---

### ⚠️ Por que dois arquivos de código?

| | `main_wokwi.py` | `main_placa.py` |
|---|---|---|
| **Leitura UART** | `uart.read(1)` bloqueante | `if uart.any(): uart.read(1)` |
| **Comportamento** | Aguarda o byte chegar | Verifica e segue em frente |
| **Uso** | Wokwi (simulação) | ESP32 / Raspberry Pi Pico |

**Por que `uart.any()` não funciona no Wokwi?**
O `$serialMonitor` entrega bytes com latência de simulação. `uart.any()` consulta o buffer naquele instante — retorna `0` antes do byte chegar e o programa o ignora. Na placa real, o driver de hardware preenche o buffer imediatamente, sem latência.

---

### `main_wokwi.py` — para o Wokwi

```python
# ============================================================
# Passo 5 — Máquina de Estados para Recepção UART
# Versão: SIMULAÇÃO WOKWI
# ============================================================
# Placa : ESP32 DevKit C v4  |  IDE: Wokwi
#
# uart.read(1) BLOQUEANTE — aguarda o byte.
# uart.any() não funciona aqui por latência do $serialMonitor.
# Veja main_placa.py para entender o motivo e a versão correta.
#
# Como usar: LED:L  LED:D  MSG:ola  + Enter
# Observe as transições de estado impressas no monitor.
# ============================================================

from machine import UART, Pin  # type: ignore[import]

BAUD_RATE = 9600
LED_PIN   = 2

uart = UART(1, baudrate=BAUD_RATE, tx=Pin(1), rx=Pin(3))
led  = Pin(LED_PIN, Pin.OUT)

IDLE        = 'IDLE'
RECEBENDO   = 'RECEBENDO'
PROCESSANDO = 'PROCESSANDO'

estado = IDLE
buffer = ''

def cmd_led(arg):
    if arg == 'L':
        led.value(1); return "LED ligado"
    elif arg == 'D':
        led.value(0); return "LED desligado"
    return f"Argumento inválido: '{arg}'"

def cmd_msg(arg):
    print(f"[MSG] {arg}"); return f"Mensagem: {arg}"

comandos = { 'LED': cmd_led, 'MSG': cmd_msg }

def no_idle(char):
    return IDLE if char in ('
', '', ' ') else RECEBENDO

def no_recebendo(char, buf):
    if char == '
':   return PROCESSANDO, buf
    elif char == '': return RECEBENDO, buf
    else:              return RECEBENDO, buf + char

def processar(buffer):
    linha = buffer.strip()
    if ':' not in linha:
        return "Formato inválido. Use COMANDO:ARGUMENTO"
    partes  = linha.split(':', 1)
    comando = partes[0].upper()
    if comando in comandos:
        return comandos[comando](partes[1])
    return f"Comando desconhecido: '{comando}'"

print("=" * 40)
print("  Passo 5 — Máquina de Estados  [Wokwi]")
print("=" * 40)
print(f"  Estado inicial: {estado}")
print("  Formato: COMANDO:ARGUMENTO + Enter")
print("=" * 40)

while True:
    byte  = uart.read(1)
    char  = byte.decode()

    if estado == IDLE:
        proximo = no_idle(char)
        if proximo == RECEBENDO:
            buffer = char
        estado = proximo
        print(f"[{estado}]", end=' ')

    elif estado == RECEBENDO:
        proximo, buffer = no_recebendo(char, buffer)
        estado = proximo
        print(f"[{estado}]", end=' ')

    if estado == PROCESSANDO:
        resposta = processar(buffer)
        uart.write(resposta + '
')
        print(f"
>> {resposta}")
        buffer = ''
        estado = IDLE
        print(f"[{estado}]", end=' ')
```

---

### `main_placa.py` — para ESP32 / Raspberry Pi Pico

```python
# ============================================================
# Passo 5 — Máquina de Estados para Recepção UART
# Versão: PLACA REAL (ESP32 / Raspberry Pi Pico)
# ============================================================
# Placa : ESP32 DevKit  ou  Raspberry Pi Pico  |  IDE: Thonny
#
# ------------------------------------
# Por que uart.any() na placa real?
# ------------------------------------
#   Padrão não bloqueante essencial em FSMs: o sistema
#   permanece responsivo mesmo em estado IDLE, sem travar
#   aguardando dados. Na placa real, o driver de hardware
#   preenche o buffer sem latência.
#
# ------------------------------------
# Por que uart.any() NÃO funciona no Wokwi?
# ------------------------------------
#   O $serialMonitor tem latência na entrega dos bytes.
#   uart.any() retorna 0 antes do byte chegar — a transição
#   IDLE→RECEBENDO nunca acontece e o primeiro byte é perdido.
#   No Wokwi usamos uart.read(1) bloqueante (main_wokwi.py).
# ============================================================

from machine import UART, Pin

BAUD_RATE = 9600
LED_PIN   = 2

uart = UART(0, baudrate=BAUD_RATE)
led  = Pin(LED_PIN, Pin.OUT)

IDLE        = 'IDLE'
RECEBENDO   = 'RECEBENDO'
PROCESSANDO = 'PROCESSANDO'

estado = IDLE
buffer = ''

def cmd_led(arg):
    if arg == 'L':
        led.value(1); return "LED ligado"
    elif arg == 'D':
        led.value(0); return "LED desligado"
    return f"Argumento inválido: '{arg}'"

def cmd_msg(arg):
    print(f"[MSG] {arg}"); return f"Mensagem: {arg}"

comandos = { 'LED': cmd_led, 'MSG': cmd_msg }

def no_idle(char):
    return IDLE if char in ('
', '', ' ') else RECEBENDO

def no_recebendo(char, buf):
    if char == '
':   return PROCESSANDO, buf
    elif char == '': return RECEBENDO, buf
    else:              return RECEBENDO, buf + char

def processar(buffer):
    linha = buffer.strip()
    if ':' not in linha:
        return "Formato inválido. Use COMANDO:ARGUMENTO"
    partes  = linha.split(':', 1)
    comando = partes[0].upper()
    if comando in comandos:
        return comandos[comando](partes[1])
    return f"Comando desconhecido: '{comando}'"

print("=" * 40)
print("  Passo 5 — Máquina de Estados  [Placa]")
print("=" * 40)
print(f"  Estado inicial: {estado}")
print("  Formato: COMANDO:ARGUMENTO + Enter")
print("=" * 40)

while True:
    if uart.any():
        byte  = uart.read(1)
        char  = byte.decode()

        if estado == IDLE:
            proximo = no_idle(char)
            if proximo == RECEBENDO:
                buffer = char
            estado = proximo
            print(f"[{estado}]", end=' ')

        elif estado == RECEBENDO:
            proximo, buffer = no_recebendo(char, buffer)
            estado = proximo
            print(f"[{estado}]", end=' ')

        if estado == PROCESSANDO:
            resposta = processar(buffer)
            uart.write(resposta + '
')
            print(f"
>> {resposta}")
            buffer = ''
            estado = IDLE
            print(f"[{estado}]", end=' ')
    # aqui poderiam vir outras tarefas: ler sensor, timeout, etc.
```

---
## Objetivos

Ao final deste passo você será capaz de:

- Implementar uma Máquina de Estados Finitos (FSM) para recepção serial
- Tornar o comportamento do sistema explícito e previsível
- Entender por que FSMs são o padrão em implementações de protocolo profissional

---

## 1. Conceito

No passo 4, o buffer acumulava bytes sem critério. Se chegassem dados corrompidos ou fora de ordem, o sistema tentaria processar uma mensagem mal formada sem perceber.

A **Máquina de Estados** resolve isso tornando o comportamento **explícito**:

```
IDLE ──► RECEBENDO ──► PROCESSANDO ──► IDLE
  ↑                                      │
  └──────────────────────────────────────┘
```

| Estado | O que faz |
|--------|-----------|
| `IDLE` | Aguarda o primeiro byte válido da mensagem |
| `RECEBENDO` | Acumula bytes no buffer até o terminador `'\n'` |
| `PROCESSANDO` | Executa o comando e volta ao IDLE |

> **Por que isso importa?** Em `IDLE`, ruído na linha (bytes soltos, `'\r'`, espaços) é **ignorado** explicitamente — em vez de ser silenciosamente acumulado no buffer.

---

## 2. Circuito

Mesmo do passo 4 — ESP32 com Serial Monitor e LED no GPIO2.

---

## 3. Código

```python
# ============================================================
# Passo 5 — Máquina de Estados para Recepção UART
# ============================================================

from machine import UART, Pin

UART_ID   = 0
BAUD_RATE = 9600
LED_PIN   = 2

uart = UART(UART_ID, baudrate=BAUD_RATE)
led  = Pin(LED_PIN, Pin.OUT)

# --- Estados (constantes nomeadas — evita "números mágicos") ---
IDLE        = 'IDLE'
RECEBENDO   = 'RECEBENDO'
PROCESSANDO = 'PROCESSANDO'

estado = IDLE   # estado inicial
buffer = ''

# --- funções de comando ---

def cmd_led(argumento):
    if argumento == 'L':
        led.value(1)
        return "LED ligado"
    elif argumento == 'D':
        led.value(0)
        return "LED desligado"
    else:
        return f"Argumento inválido: '{argumento}'"

def cmd_msg(argumento):
    print(f"[MSG] {argumento}")
    return f"Mensagem: {argumento}"

comandos = { 'LED': cmd_led, 'MSG': cmd_msg }

# --- funções de estado ---

def no_idle(char):
    """IDLE: ignora ruído; qualquer byte útil inicia recepção."""
    if char in ('\n', '\r', ' '):
        return IDLE           # permanece IDLE
    else:
        return RECEBENDO      # inicia recepção com este byte

def no_recebendo(char, buf):
    """RECEBENDO: acumula até '\n'."""
    if char == '\n':
        return PROCESSANDO, buf
    elif char == '\r':
        return RECEBENDO, buf          # ignora '\r' (Windows)
    else:
        return RECEBENDO, buf + char   # acumula

def processar(buffer):
    """PROCESSANDO: interpreta e executa."""
    linha = buffer.strip()
    if ':' not in linha:
        return "Formato inválido. Use COMANDO:ARGUMENTO"
    partes    = linha.split(':', 1)
    comando   = partes[0].upper()
    argumento = partes[1]
    if comando in comandos:
        return comandos[comando](argumento)
    return f"Comando desconhecido: '{comando}'"

print("=" * 40)
print("  Passo 5 — Máquina de Estados UART")
print(f"  Estado inicial: {estado}")
print("  Formato: COMANDO:ARGUMENTO + Enter")
print("=" * 40)

# --- loop principal com transições de estado explícitas ---

while True:
    if uart.any():
        byte = uart.read(1)
        char = byte.decode()

        if estado == IDLE:
            proximo = no_idle(char)
            if proximo == RECEBENDO:
                buffer = char         # guarda o primeiro byte
            estado = proximo
            print(f"[{estado}]", end=' ')

        elif estado == RECEBENDO:
            proximo, buffer = no_recebendo(char, buffer)
            estado = proximo
            print(f"[{estado}]", end=' ')

        if estado == PROCESSANDO:
            resposta = processar(buffer)
            uart.write(resposta + '\n')
            print(f"\n>> {resposta}")
            buffer = ''
            estado = IDLE
            print(f"[{estado}]", end=' ')
```

---

## 4. Experimento

Execute o código e observe as transições de estado no terminal.

**a)** Envie `LED:L`. Quais estados aparecem na sequência?

> _______________________________________________

**b)** Envie apenas `\n` (uma linha vazia). O que acontece em IDLE? E em RECEBENDO?

> _______________________________________________

**c)** Compare com o passo 4: qual a diferença de comportamento ao receber um `'\r'` no início, antes de qualquer mensagem?

> _______________________________________________

**d)** Por que usar constantes nomeadas (`IDLE = 'IDLE'`) em vez de números (`0`, `1`, `2`)?

> _______________________________________________

---

## 5. Desafio

**Desafio:** adicione um quarto estado `ERRO` que o sistema entra quando recebe um caractere inválido (ex: bytes fora da faixa ASCII imprimível). No estado `ERRO`, o sistema descarta tudo até receber `'\n'`, depois volta ao IDLE:

```python
ERRO = 'ERRO'

# Em no_recebendo, adicione:
elif ord(char) < 32 and char not in ('\n', '\r'):
    return ERRO, ''   # byte de controle inesperado → vai para ERRO

# Adicione o tratamento do estado ERRO no loop:
elif estado == ERRO:
    if char == '\n':
        uart.write("Mensagem descartada — caractere inválido\n")
        estado = IDLE
```

> **Para pensar:** a capacidade de **se recuperar** de erros sem precisar de reset manual é uma das qualidades mais valorizadas em sistemas embarcados industriais.

---

## Resumo

- A FSM torna o comportamento explícito: cada estado define claramente o que aceita e o que ignora
- `IDLE` filtra ruído de linha antes de iniciar o buffer — o passo 4 não fazia isso
- As funções de transição (`no_idle`, `no_recebendo`) são testáveis independentemente do hardware
- Protocolos profissionais (Modbus, HDLC) implementam FSMs mais complexas, mas com o mesmo princípio

---

*← [Passo 4](./passo04-parsing.md) | Próximo → [Passo 6: Buffer e Timeout](./passo06-buffer-timeout.md)*
