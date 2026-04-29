---
layout: default
title: "Passo 2 — Controle de LED via UART"
---

# Passo 2 — Controle de LED via UART

> **Duração estimada:** 20 minutos  
> **Fase:** 1 de 4 — PC ↔ Placa via Serial Monitor

---

## Objetivos

Ao final deste passo você será capaz de:

- Decodificar um byte recebido para tomar decisões com `if/elif/else`
- Controlar um periférico (LED) a partir de um comando serial
- Enviar respostas de volta ao terminal

---

## 1. Conceito

No passo anterior o programa apenas devolvia o que recebia. Agora ele vai **interpretar** o byte recebido e tomar uma decisão:

- `'L'` → liga o LED
- `'D'` → desliga o LED
- qualquer outro → informa erro

Isso é a base de qualquer sistema de comando por serial: **receber → decodificar → agir → responder**.

> **Conexão com o Mini Curso 01:** controlar um LED com `Pin.value()` é exatamente o que fizemos na Aula 1. A diferença é que agora o comando vem pela UART em vez de um botão físico.

---

## 2. Circuito

### Placa física (Thonny)

O LED onboard do ESP32 está no **GPIO2** — nenhum componente extra necessário para o teste básico.

```
ESP32 GPIO2 ──► LED onboard (interno)
ESP32       ──── cabo USB ──── PC (Shell do Thonny)
```

Para LED externo:
```
ESP32 GPIO2 ──► Resistor 330Ω ──► LED (+) ──► GND
```

### Simulação (Wokwi)

**Componentes:** ESP32 DevKit C v4 + LED + Resistor 330Ω.

**Conexões:**

```
esp:TX  → $serialMonitor:RX
esp:RX  → $serialMonitor:TX
esp:2   → r1:2   (resistor 330Ω)
r1:1    → led1:A (anodo do LED)
led1:C  → esp:GND.2
```

---

## 3. Código

```python
# ============================================================
# Passo 2 — Controle de LED via UART
# ============================================================

from machine import UART, Pin

UART_ID   = 0
BAUD_RATE = 9600
LED_PIN   = 2      # GPIO2 — LED onboard ESP32 (ou externo)
                   # Pico: use 25 (LED onboard)

uart = UART(UART_ID, baudrate=BAUD_RATE)
led  = Pin(LED_PIN, Pin.OUT)

print("=" * 40)
print("  Passo 2 — Controle de LED via UART")
print("=" * 40)
print(f"  UART{UART_ID} | {BAUD_RATE} bps | LED: GPIO{LED_PIN}")
print("  Comandos: 'L' = ligar | 'D' = desligar")
print("=" * 40)

while True:
    if uart.any():
        byte = uart.read(1)
        char = byte.decode()         # converte bytes → string

        if char == 'L':
            led.value(1)
            uart.write("LED ligado\n")
            print("LED ligado")

        elif char == 'D':
            led.value(0)
            uart.write("LED desligado\n")
            print("LED desligado")

        elif char not in ('\n', '\r'):   # ignora Enter
            uart.write("Comando desconhecido\n")
            print(f"Desconhecido: {repr(char)}")
```

---

## 4. Experimento

Execute o código e responda:

**a)** Envie `L` pelo terminal. O LED acende? O terminal recebe a confirmação?

> _______________________________________________

**b)** Envie `l` (minúsculo). O que acontece? Por quê?

> _______________________________________________

**c)** O código usa `elif char not in ('\n', '\r')` para ignorar o Enter. Por que é necessário ignorar esses caracteres?

> _______________________________________________

**d)** `byte.decode()` converte `bytes` em `str`. Qual seria o valor de `byte[0]` ao receber `'L'`? (dica: tabela ASCII)

> _______________________________________________

---

## 5. Desafio

**Desafio 1:** adicione o comando `'T'` que **alterna** o estado do LED (se estiver ligado, apaga; se apagado, liga) usando o operador XOR que você aprendeu no Mini Curso 01:

```python
elif char == 'T':
    estado = led.value()
    led.value(estado ^ 1)    # XOR com 1 inverte o bit
    uart.write(f"LED alternado → {'ligado' if led.value() else 'desligado'}\n")
```

**Desafio 2:** adicione o comando `'S'` que retorna o **estado atual** do LED sem modificá-lo:

```python
elif char == 'S':
    estado = "ligado" if led.value() else "desligado"
    uart.write(f"Estado atual: {estado}\n")
```

> **Para pensar:** `led.value() ^ 1` usa XOR para inverter um bit — exatamente o operador `~` em lógica digital, aplicado diretamente ao hardware.

---

## Resumo

- `.decode()` converte o objeto `bytes` da UART em `str` Python
- `if/elif/else` é suficiente para um protocolo simples de 2 a 3 comandos
- Para protocolos com muitos comandos, existe uma solução mais elegante — veremos no próximo passo
- `uart.write()` envia a resposta de volta: o terminal exibe tanto o eco quanto a confirmação

---

*← [Passo 1](./passo01-eco-serial.md) | Próximo → [Passo 3: Dicionário de Comandos](./passo03-dicionario.md)*
