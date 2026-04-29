---
layout: default
title: "Passo 4 — Parsing de Comandos com Terminador"
---

# Passo 4 — Parsing de Comandos com Terminador `\n`

> **Duração estimada:** 25 minutos  
> **Fase:** 2 de 4 — Estrutura e robustez

---

## Simulação e Código

### Arquivos do projeto Wokwi

| Arquivo | Descrição | Link |
|---------|-----------|------|
| `diagram.json` | Circuito no simulador | [abrir](https://github.com/rogerioMB-hub/minicurso_02-embarcados/blob/main/aulas/passo04-parsing/wokwi/diagram.json) |
| `wokwi.toml` | Configuração do projeto | [abrir](https://github.com/rogerioMB-hub/minicurso_02-embarcados/blob/main/aulas/passo04-parsing/wokwi/wokwi.toml) |
| `main_wokwi.py` | Código para o Wokwi | [abrir](https://github.com/rogerioMB-hub/minicurso_02-embarcados/blob/main/aulas/passo04-parsing/wokwi/main_wokwi.py) |
| `main_placa.py` | Código para ESP32 / Pico real | [abrir](https://github.com/rogerioMB-hub/minicurso_02-embarcados/blob/main/aulas/passo04-parsing/wokwi/main_placa.py) |

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
# Passo 4 — Parsing de Comandos com Terminador '
'
# Versão: SIMULAÇÃO WOKWI
# ============================================================
# Placa : ESP32 DevKit C v4  |  IDE: Wokwi
#
# uart.read(1) BLOQUEANTE — aguarda o byte.
# uart.any() não funciona aqui por latência do $serialMonitor.
# Veja main_placa.py para entender o motivo e a versão correta.
#
# Como usar: LED:L  LED:D  MSG:ola  + Enter
# ============================================================

from machine import UART, Pin  # type: ignore[import]

BAUD_RATE = 9600
LED_PIN   = 2

uart   = UART(1, baudrate=BAUD_RATE, tx=Pin(1), rx=Pin(3))
led    = Pin(LED_PIN, Pin.OUT)
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

def processar(linha):
    linha = linha.strip()
    if ':' not in linha:
        return "Formato inválido. Use COMANDO:ARGUMENTO"
    partes  = linha.split(':', 1)
    comando = partes[0].upper()
    if comando in comandos:
        return comandos[comando](partes[1])
    return f"Comando desconhecido: '{comando}'"

print("=" * 40)
print("  Passo 4 — Parsing  [Wokwi]")
print("=" * 40)
print("  Formato: COMANDO:ARGUMENTO + Enter")
print("  Exemplos: LED:L  LED:D  MSG:ola")
print("=" * 40)

while True:
    byte = uart.read(1)
    char = byte.decode()

    if char == '
':
        resposta = processar(buffer)
        uart.write(resposta + '
')
        print(f">> {resposta}")
        buffer = ''
    elif char != '':
        buffer += char
```

---

### `main_placa.py` — para ESP32 / Raspberry Pi Pico

```python
# ============================================================
# Passo 4 — Parsing de Comandos com Terminador '
'
# Versão: PLACA REAL (ESP32 / Raspberry Pi Pico)
# ============================================================
# Placa : ESP32 DevKit  ou  Raspberry Pi Pico  |  IDE: Thonny
#
# ------------------------------------
# Por que uart.any() na placa real?
# ------------------------------------
#   Padrão não bloqueante: o programa não trava enquanto
#   aguarda dados. Permite tarefas paralelas no loop.
#   Na placa real, o buffer é preenchido sem latência pelo
#   driver de hardware — uart.any() funciona corretamente.
#
# ------------------------------------
# Por que uart.any() NÃO funciona no Wokwi?
# ------------------------------------
#   O $serialMonitor tem latência na entrega dos bytes.
#   uart.any() consulta o buffer antes do byte chegar,
#   retorna 0 e o buffer nunca é preenchido — a mensagem
#   é perdida ou corrompida. Solução no Wokwi: uart.read(1)
#   bloqueante (veja main_wokwi.py).
# ============================================================

from machine import UART, Pin

BAUD_RATE = 9600
LED_PIN   = 2

uart   = UART(0, baudrate=BAUD_RATE)
led    = Pin(LED_PIN, Pin.OUT)
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

def processar(linha):
    linha = linha.strip()
    if ':' not in linha:
        return "Formato inválido. Use COMANDO:ARGUMENTO"
    partes  = linha.split(':', 1)
    comando = partes[0].upper()
    if comando in comandos:
        return comandos[comando](partes[1])
    return f"Comando desconhecido: '{comando}'"

print("=" * 40)
print("  Passo 4 — Parsing  [Placa]")
print("=" * 40)
print("  Formato: COMANDO:ARGUMENTO + Enter")
print("  Exemplos: LED:L  LED:D  MSG:ola")
print("=" * 40)

while True:
    if uart.any():
        byte = uart.read(1)
        char = byte.decode()

        if char == '
':
            resposta = processar(buffer)
            uart.write(resposta + '
')
            print(f">> {resposta}")
            buffer = ''
        elif char != '':
            buffer += char
    # aqui poderiam vir outras tarefas paralelas
```

---
## Objetivos

Ao final deste passo você será capaz de:

- Acumular bytes em um buffer até receber um terminador `'\n'`
- Separar COMANDO e ARGUMENTO com `split()`
- Entender por que o terminador é a convenção fundamental de qualquer protocolo serial

---

## 1. Conceito

Até aqui, cada byte recebido era um comando completo. Na prática, os comandos precisam de **argumentos**: `LED:L` para ligar, `LED:D` para desligar, `MSG:ola` para exibir texto.

O problema: a UART entrega bytes um de cada vez, sem saber onde começa ou termina uma mensagem. A solução é definir um **terminador** — um caractere especial que marca o fim da mensagem. Usamos `'\n'` (o Enter do teclado).

O programa acumula os bytes em um **buffer** até receber `'\n'`, e só então processa a mensagem completa:

```
Bytes chegando:  'L' 'E' 'D' ':' 'L' '\n'
Buffer:          "LED:L"
                              ↑
                         terminador → processa!
```

Formato adotado:
```
COMANDO:ARGUMENTO\n

Exemplos:
  LED:L\n    → liga o LED
  LED:D\n    → desliga o LED
  MSG:ola\n  → exibe "ola"
```

---

## 2. Circuito

ESP32 com Serial Monitor + LED externo no GPIO2.

```
esp:TX  → $serialMonitor:RX
esp:RX  → $serialMonitor:TX
esp:2   → resistor 330Ω → LED → GND
```

---

## 3. Código

```python
# ============================================================
# Passo 4 — Parsing de Comandos com Terminador '\n'
# ============================================================

from machine import UART, Pin

UART_ID   = 0
BAUD_RATE = 9600
LED_PIN   = 2

uart   = UART(UART_ID, baudrate=BAUD_RATE)
led    = Pin(LED_PIN, Pin.OUT)
buffer = ''    # acumula os bytes da mensagem atual

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

# Dicionário de comandos → funções
comandos = {
    'LED': cmd_led,
    'MSG': cmd_msg,
}

# --- função de parsing ---

def processar(linha):
    linha = linha.strip()          # remove espaços e '\r'
    if ':' not in linha:
        return "Formato inválido. Use COMANDO:ARGUMENTO"
    partes    = linha.split(':', 1)   # divide só no primeiro ':'
    comando   = partes[0].upper()
    argumento = partes[1]
    if comando in comandos:
        return comandos[comando](argumento)
    else:
        return f"Comando desconhecido: '{comando}'"

print("=" * 40)
print("  Passo 4 — Parsing de Comandos UART")
print("=" * 40)
print("  Formato: COMANDO:ARGUMENTO + Enter")
print("  Exemplos: LED:L  LED:D  MSG:ola")
print("=" * 40)

# --- loop principal ---

while True:
    if uart.any():
        byte = uart.read(1)
        char = byte.decode()

        if char == '\n':                   # terminador detectado
            resposta = processar(buffer)
            uart.write(resposta + '\n')
            print(f">> {resposta}")
            buffer = ''                    # limpa para próxima mensagem
        elif char != '\r':
            buffer += char                 # acumula no buffer
```

---

## 4. Experimento

Execute o código e responda:

**a)** Digite `LED:L` e pressione Enter. O que acontece?

> _______________________________________________

**b)** Digite `led:d` (minúsculas). O LED apaga? Por quê? (dica: veja `.upper()`)

> _______________________________________________

**c)** Envie `MSG:comunicação serial`. O que aparece no terminal?

> _______________________________________________

**d)** Envie apenas `LED` sem argumento (sem os dois-pontos). Qual a resposta? Por quê?

> _______________________________________________

**e)** Por que usamos `split(':', 1)` e não apenas `split(':')`? O que mudaria para o comando `MSG:hora:12:30`?

> _______________________________________________

---

## 5. Desafio

**Desafio 1:** adicione o comando `ECO:texto` que simplesmente devolve o argumento recebido:

```python
def cmd_eco(argumento):
    return f"ECO: {argumento}"

comandos['ECO'] = cmd_eco
```

**Desafio 2:** adicione o comando `PWM:valor` que ajusta o brilho de um LED com PWM (0 a 100):

```python
from machine import PWM

pwm = PWM(Pin(LED_PIN), freq=1000)

def cmd_pwm(argumento):
    try:
        nivel = int(argumento)         # converte string → inteiro
        if 0 <= nivel <= 100:
            duty = int(nivel / 100 * 65535)
            pwm.duty_u16(duty)
            return f"PWM: {nivel}%"
        else:
            return "Valor deve ser 0 a 100"
    except ValueError:
        return "Argumento inválido — use número inteiro"
```

> **Para pensar:** o `try/except` protege contra argumentos inválidos (ex: `PWM:abc`). Tratar erros de entrada é uma das responsabilidades de qualquer parser real.

---

## Resumo

- O buffer acumula bytes até o terminador `'\n'` — então a mensagem é processada inteira
- `split(':', 1)` divide exatamente no primeiro `:`, preservando `:` no argumento
- `.strip()` remove `'\r'` do Windows e espaços acidentais
- O dicionário de funções (tabela de despacho) escala sem alterar a lógica de parsing

---

*← [Passo 3](./passo03-dicionario.md) | Próximo → [Passo 5: Máquina de Estados](./passo05-maquina-estados.md)*
