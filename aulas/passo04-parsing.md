---
layout: default
title: "Passo 4 — Parsing de Comandos com Terminador"
---

# Passo 4 — Parsing de Comandos com Terminador `\n`

> **Duração estimada:** 25 minutos  
> **Fase:** 2 de 4 — Estrutura e robustez

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
