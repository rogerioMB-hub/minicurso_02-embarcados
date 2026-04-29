---
layout: default
title: "Passo 6 — Buffer e Timeout na Recepção UART"
---

# Passo 6 — Buffer e Timeout na Recepção UART

> **Duração estimada:** 30 minutos  
> **Fase:** 2 de 4 — Estrutura e robustez

---

## Simulação e Código

### Arquivos do projeto Wokwi

| Arquivo | Descrição | Link |
|---------|-----------|------|
| `diagram.json` | Circuito no simulador | [abrir](https://github.com/rogerioMB-hub/minicurso_02-embarcados/blob/main/aulas/passo06-buffer-timeout/wokwi/diagram.json) |
| `wokwi.toml` | Configuração do projeto | [abrir](https://github.com/rogerioMB-hub/minicurso_02-embarcados/blob/main/aulas/passo06-buffer-timeout/wokwi/wokwi.toml) |
| `main_wokwi.py` | Código para o Wokwi | [abrir](https://github.com/rogerioMB-hub/minicurso_02-embarcados/blob/main/aulas/passo06-buffer-timeout/wokwi/main_wokwi.py) |
| `main_placa.py` | Código para ESP32 / Pico real | [abrir](https://github.com/rogerioMB-hub/minicurso_02-embarcados/blob/main/aulas/passo06-buffer-timeout/wokwi/main_placa.py) |

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
# Passo 6 — Buffer e Timeout na Recepção UART
# Versão: SIMULAÇÃO WOKWI
# ============================================================
# Placa : ESP32 DevKit C v4  |  IDE: Wokwi
#
# uart.read(1) BLOQUEANTE — aguarda o byte.
# uart.any() não funciona aqui por latência do $serialMonitor.
# Veja main_placa.py para entender o motivo e a versão correta.
#
# NOTA SOBRE TIMEOUT NO WOKWI:
#   Como uart.read(1) é bloqueante, o timeout só é verificado
#   ENTRE bytes recebidos — não durante silêncio na linha.
#   Para testar o limite de buffer: envie string com >64 chars.
#   Para ver o timeout na placa real: veja main_placa.py.
#
# Como usar: LED:L  LED:D  MSG:ola  + Enter
# ============================================================

from machine import UART, Pin  # type: ignore[import]
import time

BAUD_RATE  = 9600
LED_PIN    = 2
TIMEOUT_MS = 2000
BUFFER_MAX = 64

uart = UART(1, baudrate=BAUD_RATE, tx=Pin(1), rx=Pin(3))
led  = Pin(LED_PIN, Pin.OUT)

IDLE        = 'IDLE'
RECEBENDO   = 'RECEBENDO'
PROCESSANDO = 'PROCESSANDO'

estado       = IDLE
buffer       = ''
tempo_inicio = 0

def cmd_led(arg):
    if arg == 'L':
        led.value(1); return "LED ligado"
    elif arg == 'D':
        led.value(0); return "LED desligado"
    return f"Argumento inválido: '{arg}'"

def cmd_msg(arg):
    print(f"[MSG] {arg}"); return f"Mensagem: {arg}"

comandos = { 'LED': cmd_led, 'MSG': cmd_msg }

def processar(buffer):
    linha = buffer.strip()
    if ':' not in linha: return "Formato inválido"
    partes  = linha.split(':', 1)
    comando = partes[0].upper()
    if comando in comandos: return comandos[comando](partes[1])
    return f"Comando desconhecido: '{comando}'"

def descartar(motivo):
    aviso = f"[DESCARTADO] {motivo}"
    uart.write(aviso + '
'); print(aviso)
    return IDLE, '', 0

print("=" * 40)
print("  Passo 6 — Buffer e Timeout  [Wokwi]")
print("=" * 40)
print(f"  Timeout: {TIMEOUT_MS} ms | Buffer máx: {BUFFER_MAX} B")
print("  Formato: COMANDO:ARGUMENTO + Enter")
print("=" * 40)

while True:
    byte = uart.read(1)
    char = byte.decode()

    # Timeout verificado entre bytes (limitação do modo bloqueante)
    if estado == RECEBENDO:
        if time.ticks_diff(time.ticks_ms(), tempo_inicio) >= TIMEOUT_MS:
            estado, buffer, tempo_inicio = descartar(
                f"timeout {TIMEOUT_MS} ms — buffer: '{buffer}'"
            )

    if estado == IDLE:
        if char not in ('
', '', ' '):
            buffer       = char
            tempo_inicio = time.ticks_ms()
            estado       = RECEBENDO
            print(f"[{estado}]", end=' ')

    elif estado == RECEBENDO:
        if char == '
':
            estado = PROCESSANDO
        elif char == '':
            pass
        elif len(buffer) >= BUFFER_MAX:
            estado, buffer, tempo_inicio = descartar(
                f"buffer cheio ({BUFFER_MAX} bytes)"
            )
        else:
            buffer += char

    if estado == PROCESSANDO:
        resposta = processar(buffer)
        uart.write(resposta + '
')
        print(f"
>> {resposta}")
        buffer, tempo_inicio = '', 0
        estado = IDLE
        print(f"[{estado}]", end=' ')
```

---

### `main_placa.py` — para ESP32 / Raspberry Pi Pico

```python
# ============================================================
# Passo 6 — Buffer e Timeout na Recepção UART
# Versão: PLACA REAL (ESP32 / Raspberry Pi Pico)
# ============================================================
# Placa : ESP32 DevKit  ou  Raspberry Pi Pico  |  IDE: Thonny
#
# ------------------------------------
# Por que uart.any() na placa real?
# ------------------------------------
#   Essencial para o timeout funcionar corretamente!
#   Com uart.any(), o loop roda continuamente — mesmo sem
#   bytes chegando, a verificação de timeout é executada
#   a cada iteração. Se o transmissor parar de enviar no
#   meio de uma mensagem, o timeout dispara normalmente.
#   Na placa real, o driver preenche o buffer sem latência.
#
# ------------------------------------
# Por que uart.any() NÃO funciona no Wokwi?
# ------------------------------------
#   O $serialMonitor tem latência na entrega dos bytes.
#   uart.any() retorna 0 prematuramente — bytes são perdidos.
#   No Wokwi, uart.read(1) bloqueante é a solução (main_wokwi.py),
#   mas isso impede o timeout de funcionar durante silêncio
#   na linha — limitação aceita apenas na simulação.
# ============================================================

from machine import UART, Pin
import time

BAUD_RATE  = 9600
LED_PIN    = 2
TIMEOUT_MS = 2000   # 2 s sem '
' → descarta
BUFFER_MAX = 64

uart = UART(0, baudrate=BAUD_RATE)
led  = Pin(LED_PIN, Pin.OUT)

IDLE        = 'IDLE'
RECEBENDO   = 'RECEBENDO'
PROCESSANDO = 'PROCESSANDO'

estado       = IDLE
buffer       = ''
tempo_inicio = 0

def cmd_led(arg):
    if arg == 'L':
        led.value(1); return "LED ligado"
    elif arg == 'D':
        led.value(0); return "LED desligado"
    return f"Argumento inválido: '{arg}'"

def cmd_msg(arg):
    print(f"[MSG] {arg}"); return f"Mensagem: {arg}"

comandos = { 'LED': cmd_led, 'MSG': cmd_msg }

def processar(buffer):
    linha = buffer.strip()
    if ':' not in linha: return "Formato inválido"
    partes  = linha.split(':', 1)
    comando = partes[0].upper()
    if comando in comandos: return comandos[comando](partes[1])
    return f"Comando desconhecido: '{comando}'"

def descartar(motivo):
    aviso = f"[DESCARTADO] {motivo}"
    uart.write(aviso + '
'); print(aviso)
    return IDLE, '', 0

print("=" * 40)
print("  Passo 6 — Buffer e Timeout  [Placa]")
print("=" * 40)
print(f"  Timeout: {TIMEOUT_MS} ms | Buffer máx: {BUFFER_MAX} B")
print("  Formato: COMANDO:ARGUMENTO + Enter")
print("=" * 40)

while True:
    # Timeout funciona aqui mesmo sem bytes chegando —
    # o loop não está bloqueado, roda continuamente
    if estado == RECEBENDO:
        if time.ticks_diff(time.ticks_ms(), tempo_inicio) >= TIMEOUT_MS:
            estado, buffer, tempo_inicio = descartar(
                f"timeout {TIMEOUT_MS} ms — buffer: '{buffer}'"
            )

    if uart.any():
        byte = uart.read(1)
        char = byte.decode()

        if estado == IDLE:
            if char not in ('
', '', ' '):
                buffer       = char
                tempo_inicio = time.ticks_ms()
                estado       = RECEBENDO
                print(f"[{estado}]", end=' ')

        elif estado == RECEBENDO:
            if char == '
':
                estado = PROCESSANDO
            elif char == '':
                pass
            elif len(buffer) >= BUFFER_MAX:
                estado, buffer, tempo_inicio = descartar(
                    f"buffer cheio ({BUFFER_MAX} bytes)"
                )
            else:
                buffer += char

        if estado == PROCESSANDO:
            resposta = processar(buffer)
            uart.write(resposta + '
')
            print(f"
>> {resposta}")
            buffer, tempo_inicio = '', 0
            estado = IDLE
            print(f"[{estado}]", end=' ')
```

---
## Objetivos

Ao final deste passo você será capaz de:

- Detectar e recuperar de mensagens incompletas com **timeout**
- Proteger a memória RAM com **limite de buffer**
- Usar `time.ticks_ms()` e `time.ticks_diff()` para medir tempo em embarcados

---

## 1. Conceito

Em comunicação serial real, três coisas podem dar errado:

1. **O transmissor para no meio da mensagem** — o `'\n'` nunca chega
2. **O cabo é desconectado** durante a transmissão
3. **Ruído elétrico** insere bytes extras, enchendo o buffer

Os dois mecanismos deste passo protegem contra esses cenários:

### Timeout

O sistema marca o instante em que entra em `RECEBENDO`. Se passar `TIMEOUT_MS` milissegundos sem receber o `'\n'`, a mensagem parcial é descartada e o sistema volta ao `IDLE`:

```python
decorrido = time.ticks_diff(time.ticks_ms(), tempo_inicio)
if decorrido >= TIMEOUT_MS:
    # descarta e volta ao IDLE
```

> `ticks_diff()` em vez de subtração simples: `ticks_ms()` pode dar a volta em 0 após ~12 dias. `ticks_diff()` trata esse overflow corretamente.

### Limite de buffer

Se o buffer atingir `BUFFER_MAX` bytes sem o terminador, a mensagem é descartada. Microcontroladores têm RAM limitada — um buffer ilimitado pode travar o sistema.

---

## 2. Circuito

Mesmo do passo 5 — ESP32 com Serial Monitor e LED no GPIO2.

---

## 3. Código

```python
# ============================================================
# Passo 6 — Buffer e Timeout na Recepção UART
# ============================================================

from machine import UART, Pin
import time

UART_ID    = 0
BAUD_RATE  = 9600
LED_PIN    = 2
TIMEOUT_MS = 2000   # 2 s sem '\n' → descarta
BUFFER_MAX = 64     # máximo de bytes acumulados

uart = UART(UART_ID, baudrate=BAUD_RATE)
led  = Pin(LED_PIN, Pin.OUT)

IDLE        = 'IDLE'
RECEBENDO   = 'RECEBENDO'
PROCESSANDO = 'PROCESSANDO'

estado       = IDLE
buffer       = ''
tempo_inicio = 0   # instante em que RECEBENDO começou

def cmd_led(argumento):
    if argumento == 'L':
        led.value(1)
        return "LED ligado"
    elif argumento == 'D':
        led.value(0)
        return "LED desligado"
    return f"Argumento inválido: '{argumento}'"

def cmd_msg(argumento):
    print(f"[MSG] {argumento}")
    return f"Mensagem: {argumento}"

comandos = { 'LED': cmd_led, 'MSG': cmd_msg }

def processar(buffer):
    linha = buffer.strip()
    if ':' not in linha:
        return "Formato inválido"
    partes    = linha.split(':', 1)
    comando   = partes[0].upper()
    argumento = partes[1]
    if comando in comandos:
        return comandos[comando](argumento)
    return f"Comando desconhecido: '{comando}'"

def descartar(motivo):
    """Centraliza o reset: envia aviso e volta ao IDLE."""
    aviso = f"[DESCARTADO] {motivo}"
    uart.write(aviso + '\n')
    print(aviso)
    return IDLE, '', 0   # (estado, buffer, tempo_inicio)

print("=" * 40)
print("  Passo 6 — Buffer e Timeout UART")
print(f"  Timeout: {TIMEOUT_MS} ms | Buffer máx: {BUFFER_MAX} B")
print("  Formato: COMANDO:ARGUMENTO + Enter")
print("=" * 40)

while True:

    # Verificação de timeout — roda a CADA iteração,
    # mesmo quando não há bytes disponíveis
    if estado == RECEBENDO:
        decorrido = time.ticks_diff(time.ticks_ms(), tempo_inicio)
        if decorrido >= TIMEOUT_MS:
            estado, buffer, tempo_inicio = descartar(
                f"timeout de {TIMEOUT_MS} ms — buffer: '{buffer}'"
            )

    if uart.any():
        byte = uart.read(1)
        char = byte.decode()

        if estado == IDLE:
            if char not in ('\n', '\r', ' '):
                buffer       = char
                tempo_inicio = time.ticks_ms()   # inicia o cronômetro
                estado       = RECEBENDO
                print(f"[{estado}]", end=' ')

        elif estado == RECEBENDO:
            if char == '\n':
                estado = PROCESSANDO
            elif char == '\r':
                pass
            elif len(buffer) >= BUFFER_MAX:
                estado, buffer, tempo_inicio = descartar(
                    f"buffer cheio ({BUFFER_MAX} bytes)"
                )
            else:
                buffer += char

        if estado == PROCESSANDO:
            resposta = processar(buffer)
            uart.write(resposta + '\n')
            print(f"\n>> {resposta}")
            buffer       = ''
            tempo_inicio = 0
            estado       = IDLE
            print(f"[{estado}]", end=' ')
```

---

## 4. Experimento

**a)** Envie `LED:L` normalmente. O sistema funciona como antes?

> _______________________________________________

**b)** Para testar o timeout: envie apenas `LED` (sem `:L\n`) e aguarde 2 segundos. O que aparece?

> _______________________________________________

**c)** A verificação de timeout ocorre **antes** de ler novos bytes. Por que isso é necessário? O que aconteceria se ela ficasse dentro do `if uart.any()`?

> _______________________________________________

**d)** Por que `ticks_diff(ticks_ms(), t0)` é preferível a `ticks_ms() - t0`?

> _______________________________________________

---

## 5. Desafio

**Desafio:** adicione um comando `CFG:TIMEOUT:valor` que permite alterar o timeout em tempo real:

```python
def cmd_cfg(argumento):
    global TIMEOUT_MS
    partes = argumento.split(':', 1)
    if len(partes) == 2 and partes[0] == 'TIMEOUT':
        try:
            novo = int(partes[1])
            if 500 <= novo <= 10000:
                TIMEOUT_MS = novo
                return f"Timeout alterado para {novo} ms"
            return "Valor deve ser entre 500 e 10000 ms"
        except ValueError:
            return "Valor inválido"
    return "Subcomando desconhecido"

comandos['CFG'] = cmd_cfg
```

> **Para pensar:** sistemas industriais frequentemente permitem reconfiguração de parâmetros em tempo real via serial — sem reiniciar o equipamento. O comando `CFG` é o embrião desse mecanismo.

---

## Resumo

- O timeout garante que o sistema não fique travado em `RECEBENDO` para sempre
- O limite de buffer protege a RAM — crítico em microcontroladores com 256 KB ou menos
- `ticks_diff()` é a forma correta de medir tempo em MicroPython (trata overflow)
- A função `descartar()` centraliza o reset — evita repetir código em dois lugares

---

*← [Passo 5](./passo05-maquina-estados.md) | Próximo → [Passo 7: Loopback Físico](./passo07-loopback.md)*
