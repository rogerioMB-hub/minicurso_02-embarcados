---
layout: default
title: "Passo 3 — Dicionário de Comandos"
---

# Passo 3 — Dicionário de Comandos

> **Duração estimada:** 20 minutos  
> **Fase:** 1 de 4 — PC ↔ Placa via Serial Monitor

---

## Objetivos

Ao final deste passo você será capaz de:

- Usar um dicionário Python como tabela de despacho de comandos
- Verificar a existência de uma chave com o operador `in`
- Entender por que dicionários escalam melhor que cadeias de `if/elif`

---

## 1. Conceito

No passo 2, cada novo comando exige um novo `elif`. Com 3 comandos isso é aceitável — com 10 ou 20, o código fica ilegível e propenso a erros.

A solução é usar um **dicionário como tabela de despacho**: a chave é o comando recebido, o valor é a resposta (ou uma função). O operador `in` verifica se o comando existe antes de acessá-lo:

```python
tabela = {
    '1': 'um',
    '2': 'dois',
    '9': 'nove',
}

if char in tabela:
    resposta = tabela[char]   # acesso seguro — chave garantida
else:
    resposta = "desconhecido"
```

> **Vantagem prática:** adicionar um novo comando significa adicionar **uma linha** ao dicionário — sem tocar na lógica principal.

---

## 2. Circuito

Mesmo do passo 1 — apenas ESP32 com Serial Monitor.

```
esp:TX → $serialMonitor:RX
esp:RX → $serialMonitor:TX
```

---

## 3. Código

```python
# ============================================================
# Passo 3 — Dicionário de Dígitos por Extenso via UART
# ============================================================

from machine import UART

UART_ID   = 0
BAUD_RATE = 9600

uart = UART(UART_ID, baudrate=BAUD_RATE)

# Dicionário: chave = caractere recebido, valor = resposta
# As chaves são STRINGS pois a UART entrega caracteres de texto
digitos = {
    '1': 'um',
    '2': 'dois',
    '3': 'três',
    '4': 'quatro',
    '5': 'cinco',
    '6': 'seis',
    '7': 'sete',
    '8': 'oito',
    '9': 'nove',
}

print("=" * 40)
print("  Passo 3 — Dicionário via UART")
print("=" * 40)
print(f"  UART{UART_ID} | {BAUD_RATE} bps")
print("  Envie um dígito de 1 a 9")
print("=" * 40)

while True:
    if uart.any():
        byte = uart.read(1)
        char = byte.decode()

        if char in digitos:               # a chave existe?
            resposta = digitos[char]      # acessa o valor
            uart.write(resposta + '\n')
            print(f"'{char}' → {resposta}")

        elif char not in ('\n', '\r'):
            uart.write("Caractere desconhecido\n")
            print(f"Desconhecido: {repr(char)}")
```

---

## 4. Experimento

Execute o código e responda:

**a)** Envie `5`. Qual a resposta? E `9`?

> _______________________________________________

**b)** Envie `0` (zero). O que acontece e por quê?

> _______________________________________________

**c)** Adicione a entrada `'0': 'zero'` ao dicionário e teste novamente. Quantas linhas de código você precisou alterar?

> _______________________________________________

**d)** O que aconteceria se você escrevesse `digitos[char]` sem verificar `if char in digitos` antes?

> _______________________________________________

---

## 5. Desafio

**Desafio 1:** transforme o dicionário em uma tabela de controle de LEDs. Cada dígito acende um padrão diferente de 4 LEDs (use GPIO 2, 4, 5, 18):

```python
from machine import UART, Pin

leds = [Pin(2,Pin.OUT), Pin(4,Pin.OUT), Pin(5,Pin.OUT), Pin(18,Pin.OUT)]

def aplicar(nibble):
    for i, led in enumerate(leds):
        led.value((nibble >> i) & 1)

padroes = {
    '1': 0b0001,   # só LED0
    '2': 0b0011,   # LED0 e LED1
    '3': 0b0111,   # LED0, 1 e 2
    '4': 0b1111,   # todos
    '0': 0b0000,   # apaga tudo
}
```

**Desafio 2:** use o dicionário para mapear letras a ações com funções:

```python
def ligar():  return "LED ligado"
def apagar(): return "LED apagado"

acoes = { 'L': ligar, 'D': apagar }

if char in acoes:
    resultado = acoes[char]()   # chama a função armazenada!
```

> **Para pensar:** dicionários com funções como valores são chamados de *tabelas de despacho*. Protocolos industriais reais usam esse padrão internamente.

---

## Resumo

- Um dicionário Python funciona como uma tabela de lookup: `O(1)`, sem `if/elif` aninhados
- O operador `in` verifica a chave com segurança antes do acesso
- Adicionar comandos = adicionar entradas ao dicionário, sem alterar a lógica principal
- No próximo passo, os comandos deixarão de ser caracteres únicos e passarão a ser **strings completas com argumentos**

---

*← [Passo 2](./passo02-led-uart.md) | Próximo → [Passo 4: Parsing com Terminador](./passo04-parsing.md)*
