---
layout: default
title: "Passo 1 — Eco Serial via UART"
---

# Passo 1 — Eco Serial via UART

> **Duração estimada:** 20 minutos  
> **Fase:** 1 de 4 — PC ↔ Placa via Serial Monitor

---

## Simulação e Código

### Arquivos do projeto Wokwi

| Arquivo | Descrição | Link |
|---------|-----------|------|
| `diagram.json` | Circuito no simulador | [abrir](https://github.com/rogerioMB-hub/minicurso_02-embarcados/blob/main/aulas/passo01-eco-serial/wokwi/diagram.json) |
| `wokwi.toml` | Configuração do projeto | [abrir](https://github.com/rogerioMB-hub/minicurso_02-embarcados/blob/main/aulas/passo01-eco-serial/wokwi/wokwi.toml) |
| `main_wokwi.py` | Código para o Wokwi | [abrir](https://github.com/rogerioMB-hub/minicurso_02-embarcados/blob/main/aulas/passo01-eco-serial/wokwi/main_wokwi.py) |
| `main_placa.py` | Código para ESP32 / Pico real | [abrir](https://github.com/rogerioMB-hub/minicurso_02-embarcados/blob/main/aulas/passo01-eco-serial/wokwi/main_placa.py) |

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
# Passo 1 — Eco Serial via UART
# Versão: SIMULAÇÃO WOKWI
# ============================================================
# Placa : ESP32 DevKit C v4
# IDE   : Wokwi (https://wokwi.com)
#
# DIFERENÇA EM RELAÇÃO À PLACA REAL:
#   Este arquivo usa uart.read(1) de forma BLOQUEANTE —
#   o programa aguarda até um byte chegar antes de continuar.
#
#   Por que não usamos uart.any() aqui?
#   No Wokwi, o $serialMonitor entrega bytes com uma pequena
#   latência. uart.any() é não bloqueante e consulta o buffer
#   instantaneamente — nesse intervalo o buffer ainda está
#   vazio, então retorna 0 e o byte é "perdido" pelo programa.
#   uart.read(1) sem verificação prévia bloqueia e aguarda
#   o byte chegar, resolvendo o problema.
#
#   Na placa real (Thonny), uart.any() funciona corretamente.
#   Veja main_placa.py para a versão com uart.any().
#
# Como usar:
#   1. Clique em "Play"
#   2. Abra o Serial Monitor
#   3. Digite qualquer texto e pressione Enter
#   4. O texto será ecoado de volta
# ============================================================

from machine import UART, Pin  # type: ignore[import]

BAUD_RATE = 9600
uart = UART(1, baudrate=BAUD_RATE, tx=Pin(1), rx=Pin(3))

print("=" * 40)
print("  Passo 1 — Eco Serial UART  [Wokwi]")
print("=" * 40)
print(f"  UART1 | TX=GPIO1 | RX=GPIO3 | {BAUD_RATE} bps")
print("  Digite algo no Serial Monitor...")
print("=" * 40)

while True:
    byte = uart.read(1)      # bloqueante — aguarda o byte chegar
    uart.write(byte)         # ecoa de volta
    print(byte.decode(), end="")
```

---

### `main_placa.py` — para ESP32 / Raspberry Pi Pico

```python
# ============================================================
# Passo 1 — Eco Serial via UART
# Versão: PLACA REAL (ESP32 / Raspberry Pi Pico)
# ============================================================
# Placa : ESP32 DevKit  ou  Raspberry Pi Pico
# IDE   : Thonny
#
# DIFERENÇA EM RELAÇÃO AO WOKWI:
#   Esta versão usa o padrão não bloqueante uart.any() +
#   uart.read(1), que é o correto para uso em hardware real.
#
# ------------------------------------
# Por que uart.any() na placa real?
# ------------------------------------
#   uart.any() consulta quantos bytes estão disponíveis no
#   buffer de recepção da UART naquele instante, SEM bloquear
#   o programa. Se não houver bytes, o loop continua rodando
#   normalmente — permitindo que outras tarefas sejam feitas
#   enquanto se aguarda dados (ex: piscar LED, ler sensor).
#
#   Na placa real, o driver de hardware da UART preenche o
#   buffer imediatamente ao receber cada byte. uart.any()
#   enxerga esse buffer sem latência — por isso funciona.
#
# ------------------------------------
# Por que uart.any() NÃO funciona no Wokwi?
# ------------------------------------
#   No Wokwi, o $serialMonitor simula a entrada do usuário
#   com uma pequena latência. uart.any() consulta o buffer
#   antes que o byte simulado chegue — retorna 0 e o byte
#   é ignorado. Por isso, no Wokwi usamos uart.read(1)
#   bloqueante (veja main_wokwi.py).
#
# ------------------------------------
# Configuração de pinos
# ------------------------------------
#   ESP32  : UART0 usa GPIO1 (TX) e GPIO3 (RX) — cabo USB
#   Pico W : UART0 usa GPIO0 (TX) e GPIO1 (RX)
#            ajuste UART_ID e pinos conforme sua placa
# ============================================================

from machine import UART, Pin

# --- Configuração -------------------------------------------
# ESP32:
UART_ID  = 0
TX_PIN   = 1    # GPIO1  (não é necessário declarar no ESP32
RX_PIN   = 3    # GPIO3   quando UART_ID=0, mas fica explícito)

# Raspberry Pi Pico — descomente e ajuste se necessário:
# UART_ID = 0
# TX_PIN  = 0   # GPIO0
# RX_PIN  = 1   # GPIO1

BAUD_RATE = 9600
uart = UART(UART_ID, baudrate=BAUD_RATE)

print("=" * 40)
print("  Passo 1 — Eco Serial UART  [Placa]")
print("=" * 40)
print(f"  UART{UART_ID} | {BAUD_RATE} bps")
print("  Digite algo no Shell do Thonny...")
print("=" * 40)

# --- Loop principal (não bloqueante) ------------------------
while True:
    if uart.any():           # há bytes disponíveis no buffer?
        byte = uart.read(1)  # lê 1 byte — não bloqueia
        uart.write(byte)     # ecoa de volta
        print(byte.decode(), end="")
    # aqui poderiam vir outras tarefas: ler sensor, piscar LED, etc.
```

---
## Objetivos

Ao final deste passo você será capaz de:

- Inicializar uma UART em MicroPython
- Verificar se há bytes disponíveis com `uart.any()`
- Ler e reenviar bytes com `uart.read()` e `uart.write()`
- Entender que a UART transmite exatamente os bytes que você enviar

---

## 1. Conceito

A UART (*Universal Asynchronous Receiver-Transmitter*) é o protocolo serial mais simples do mundo embarcado. Ela transmite bytes bit a bit, a uma velocidade configurável chamada **baud rate**.

No ESP32, a UART0 está conectada ao cabo USB — o mesmo que alimenta a placa. Isso significa que o que você digitar no Shell do Thonny (ou no Serial Monitor do Wokwi) chega diretamente ao seu programa como bytes.

| Conceito | Significado |
|----------|-------------|
| `UART(0, baudrate=9600)` | Inicializa UART0 a 9600 bits/segundo |
| `uart.any()` | Retorna o número de bytes disponíveis para leitura |
| `uart.read(1)` | Lê exatamente 1 byte — retorna `bytes` |
| `uart.write(byte)` | Envia bytes de volta pela UART |

> **Por que não bloqueante?** `uart.any()` verifica sem esperar. Se não houver dados, o programa continua seu loop. Isso é essencial em embarcados — um `while uart.any()` bloquearia o sistema inteiro enquanto aguarda.

---

## 2. Circuito

### Placa física (Thonny)

Nenhum fio extra necessário. A UART0 já está conectada ao USB.

```
ESP32 ──── cabo USB ──── PC
                         └── Shell do Thonny (entrada/saída)
```

### Simulação (Wokwi)

**Componentes:** apenas 1 ESP32 DevKit C v4.

**Conexões no `diagram.json`:**

```json
[ "esp:TX", "$serialMonitor:RX", "", [] ],
[ "esp:RX", "$serialMonitor:TX", "", [] ]
```

---

## 3. Código

```python
# ============================================================
# Passo 1 — Eco Serial via UART
# ============================================================
# Compatível com: ESP32 · Raspberry Pi Pico
# IDE: Thonny  |  Simulador: Wokwi
# ============================================================

from machine import UART

UART_ID   = 0       # UART0 → conectada ao USB/Serial Monitor
BAUD_RATE = 9600

uart = UART(UART_ID, baudrate=BAUD_RATE)

print("=" * 40)
print("  Passo 1 — Eco Serial UART")
print("=" * 40)
print(f"  UART{UART_ID} | {BAUD_RATE} bps")
print("  Digite algo no terminal...")
print("=" * 40)

while True:
    if uart.any():               # Há byte(s) disponível(is)?
        byte = uart.read(1)      # Lê exatamente 1 byte
        uart.write(byte)         # Ecoa o mesmo byte de volta
        print(byte.decode(), end="")  # Exibe no Shell
```

**O que cada parte faz:**

| Linha | Explicação |
|-------|------------|
| `UART(0, baudrate=9600)` | Inicializa UART0 com 9600 bps |
| `uart.any()` | Retorna `True` se houver bytes prontos |
| `uart.read(1)` | Lê 1 byte — retorna objeto `bytes` |
| `uart.write(byte)` | Reenvia o mesmo byte pela UART |

---

## 4. Experimento

Execute o código e responda:

**a)** Digite a letra `A` no terminal. O que aparece de volta?

> _______________________________________________

**b)** Digite `123`. Os dígitos aparecem juntos ou um de cada vez? Por quê?

> _______________________________________________

**c)** `uart.read(1)` retorna um objeto do tipo `bytes`. Para exibir no `print()`, usamos `.decode()`. O que acontece se você remover o `.decode()` e tentar imprimir diretamente?

> _______________________________________________

**d)** O loop verifica `uart.any()` a cada iteração. Se não houver dados disponíveis, o que o programa faz?

> _______________________________________________

---

## 5. Desafio

Modifique o código para que cada byte recebido seja exibido **em três formatos** — caractere, decimal e hexadecimal:

```python
# Exemplo de saída esperada ao receber 'A':
# Char: A  |  Dec: 65  |  Hex: 0x41

byte = uart.read(1)
char = byte.decode()
dec  = byte[0]        # acessa o valor inteiro do primeiro byte
hex_ = hex(byte[0])   # converte para hexadecimal

print(f"Char: {char}  |  Dec: {dec}  |  Hex: {hex_}")
uart.write(byte)
```

> **Para pensar:** `byte[0]` retorna um inteiro entre 0 e 255. Esse é exatamente o byte transmitido pela UART. Você já trabalhou com esses valores no Mini Curso 01 — são os mesmos bits!

---

## Resumo

- A UART recebe bytes do terminal e os disponibiliza via `uart.any()` / `uart.read()`
- `uart.write()` envia bytes de volta — qualquer objeto `bytes` ou `str` é aceito
- O padrão não bloqueante (`if uart.any()`) é a base de todo código UART em embarcados
- Um byte é um inteiro de 0 a 255 — os mesmos valores manipulados com bitwise

---

*Próximo passo → [Passo 2: Controle de LED via UART](./passo02-led-uart.md)*
