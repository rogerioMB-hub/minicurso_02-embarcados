---
layout: default
title: "Passo 1 — Eco Serial via UART"
---

# Passo 1 — Eco Serial via UART

> **Duração estimada:** 20 minutos  
> **Fase:** 1 de 4 — PC ↔ Placa via Serial Monitor

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
