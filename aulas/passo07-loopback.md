---
layout: default
title: "Passo 7 — Loopback Físico entre UARTs"
---

# Passo 7 — Loopback Físico entre UARTs

> **Duração estimada:** 30 minutos  
> **Fase:** 3 de 4 — Placa ↔ Placa (loopback)

---

## Simulação e Código

### Arquivos do projeto Wokwi

| Arquivo | Descrição | Link |
|---------|-----------|------|
| `diagram.json` | Circuito no simulador | [abrir](https://github.com/rogerioMB-hub/minicurso_02-embarcados/blob/main/aulas/passo07-loopback/wokwi/diagram.json) |
| `wokwi.toml` | Configuração do projeto | [abrir](https://github.com/rogerioMB-hub/minicurso_02-embarcados/blob/main/aulas/passo07-loopback/wokwi/wokwi.toml) |
| `main.py` | Código principal | [abrir](https://github.com/rogerioMB-hub/minicurso_02-embarcados/blob/main/aulas/passo07-loopback/wokwi/main.py) |

> **Como usar:** copie o conteúdo de cada arquivo para as abas correspondentes em [wokwi.com/projects/new/micropython-esp32](https://wokwi.com/projects/new/micropython-esp32).

> **Loopback:** fios cruzados entre UART1 (GPIO4/5) e UART2 (GPIO16/17) já configurados no `diagram.json`. Nenhuma placa extra necessária.

---

### `main.py`

```python
# ============================================================
# Passo 07 — Loopback UART (simulação Wokwi)
#
# Simula a comunicação entre duas UARTs em um único ESP32.
# UART1 (transmissora) conectada à UART2 (receptora)
# por um fio virtual no diagrama.
#
# Equivalente ao loopback físico com duas placas, mas
# executado em um único ESP32 no simulador Wokwi.
#
# Conexão interna (fio no diagram.json):
#   GPIO 4  (TX1) → GPIO 16 (RX2)
#
# Periféricos:
#   GPIO 13 → botão (pull-up interno)
#   GPIO 2  → LED
#
# Protocolo:
#   b'\x01' → acende LED
#   b'\x00' → apaga LED
#
# Baud rate: 9600 bps
# ============================================================

from machine import UART, Pin  # type: ignore[import]
import time

# --- Configuração das UARTs ---
uart_tx = UART(1, baudrate=9600, tx=4,  rx=5)   # transmissora
uart_rx = UART(2, baudrate=9600, tx=17, rx=16)  # receptora

# --- Periféricos ---
botao = Pin(13, Pin.IN, Pin.PULL_UP)
led   = Pin(2,  Pin.OUT)
led.value(0)

# --- Estado anterior do botão (debounce por software) ---
estado_anterior = 1

print("Passo 07 — Loopback UART iniciado.")
print("Pressione o botão para acionar o LED.")

# --- Loop principal não bloqueante ---
while True:

    # TRANSMISSORA: detecta mudança no botão e envia byte
    estado_atual = botao.value()

    if estado_atual != estado_anterior:
        estado_anterior = estado_atual

        if estado_atual == 0:
            uart_tx.write(b'\x01')
            print("[TX] Enviou 0x01 (LIGAR)")
        else:
            uart_tx.write(b'\x00')
            print("[TX] Enviou 0x00 (DESLIGAR)")

    # RECEPTORA: lê byte recebido e controla o LED
    if uart_rx.any():
        dado = uart_rx.read(1)

        if dado == b'\x01':
            led.value(1)
            print("[RX] LED LIGADO")
        elif dado == b'\x00':
            led.value(0)
            print("[RX] LED DESLIGADO")

    time.sleep(0.02)
print("Hello, ESP32!")
```

---
## Objetivos

Ao final deste passo você será capaz de:

- Inicializar duas UARTs independentes no mesmo ESP32
- Conectar TX de uma UART ao RX da outra com fios reais
- Medir e exibir estatísticas de comunicação (mensagens enviadas, recebidas, erros)

---

## 1. Conceito

A partir deste passo, a comunicação sai do loop USB/terminal e passa a acontecer entre **periféricos de hardware reais** — as UARTs internas do ESP32.

Usamos **duas UARTs no mesmo ESP32** com os TXs e RXs cruzados por fios físicos. Isso reproduz fielmente o comportamento de duas placas comunicando-se, sem precisar de hardware extra.

```
UART1                          UART2
TX (GPIO4) ──laranja──────► RX (GPIO16)
RX (GPIO5) ◄──── azul──── TX (GPIO17)
```

> **Por que isso é importante?** A partir daqui, os bytes não passam mais pelo USB — eles percorrem o caminho elétrico real: saem de um pino, percorrem um fio e chegam a outro pino. Qualquer erro de configuração (baud rate, pinos trocados, GND ausente) impede a comunicação — exatamente como no hardware real.

---

## 2. Circuito

### Placa física (Thonny)

Conecte 2 fios diretamente na placa:

```
GPIO4  (TX1) ──► GPIO16 (RX2)    ← fio laranja
GPIO17 (TX2) ──► GPIO5  (RX1)    ← fio azul
```

> GND comum não é necessário aqui pois é o mesmo ESP32 — mas em duas placas separadas o GND é **obrigatório**.

### Simulação (Wokwi)

**Componentes:** ESP32 DevKit C v4 + LED + botão.

**Conexões no `diagram.json`:**

```json
[ "esp:TX",  "$serialMonitor:RX", "", [] ],
[ "esp:RX",  "$serialMonitor:TX", "", [] ],
[ "esp:4",   "esp:16",  "orange", [] ],
[ "esp:17",  "esp:5",   "blue",   [] ],
[ "esp:13",  "btn1:1.r","green",  [] ],
[ "esp:2",   "r1:2",    "green",  [] ]
```

---

## 3. Código

```python
# ============================================================
# Passo 7 — Loopback Físico entre UARTs
# ============================================================

from machine import UART, Pin
import time

BAUD_RATE = 9600

# UART1 — transmissora: TX=GPIO4 → GPIO16 (RX da UART2)
uart_tx = UART(1, baudrate=BAUD_RATE, tx=Pin(4),  rx=Pin(5))

# UART2 — receptora: TX=GPIO17 → GPIO5 (RX da UART1)
uart_rx = UART(2, baudrate=BAUD_RATE, tx=Pin(17), rx=Pin(16))

# Periféricos
botao = Pin(13, Pin.IN, Pin.PULL_UP)   # botão com pull-up interno
led   = Pin(2, Pin.OUT)

# Estatísticas
enviadas  = 0
recebidas = 0
erros     = 0

estado_botao_anterior = 1
numero_mensagem       = 0

print("=" * 40)
print("  Passo 7 — Loopback Físico")
print("=" * 40)
print("  UART1: TX=GPIO4  RX=GPIO5")
print("  UART2: TX=GPIO17 RX=GPIO16")
print("  Fio laranja: GPIO4  → GPIO16")
print("  Fio azul   : GPIO17 → GPIO5")
print("  Pressione o botão para enviar")
print("=" * 40)

while True:
    estado_botao = botao.value()

    # Detecta borda de descida (botão pressionado)
    if estado_botao == 0 and estado_botao_anterior == 1:
        numero_mensagem += 1
        mensagem = f"MSG:{numero_mensagem:03d}"
        uart_tx.write(mensagem + '\n')
        enviadas += 1
        print(f"[TX] Enviou: '{mensagem}'  (total: {enviadas})")

    estado_botao_anterior = estado_botao

    # Recepção não bloqueante
    if uart_rx.any():
        dado = uart_rx.readline()   # lê até '\n'
        if dado:
            texto = dado.decode().strip()
            recebidas += 1
            led.value(1)            # pisca LED ao receber

            # Verifica se a mensagem chegou íntegra
            if texto.startswith('MSG:'):
                print(f"[RX] Recebeu: '{texto}'  (total: {recebidas})")
            else:
                erros += 1
                print(f"[RX] Formato inesperado: '{texto}'  (erros: {erros})")

            time.sleep_ms(50)
            led.value(0)

    time.sleep_ms(20)
```

---

## 4. Experimento

**a)** Pressione o botão várias vezes. As mensagens aparecem no terminal na ordem correta?

> _______________________________________________

**b)** Desconecte um dos fios (laranja ou azul) durante a simulação. O que acontece com as mensagens?

> _______________________________________________

**c)** Altere o `baudrate` de uma das UARTs (ex: mude `uart_rx` para `19200`). O que acontece? Por quê?

> _______________________________________________

**d)** `uart_rx.readline()` é diferente de `uart_rx.read(1)`. O que cada um faz? Qual é mais adequado aqui?

> _______________________________________________

---

## 5. Desafio

**Desafio:** adicione um mecanismo de **número de sequência com verificação**. A transmissora envia `MSG:NNN` e a receptora verifica se `NNN` é igual ao esperado. Se não for (simulando uma perda de mensagem), incrementa um contador de `perdas`:

```python
esperado = 1

# Na recepção:
if texto.startswith('MSG:'):
    num_recebido = int(texto[4:])
    if num_recebido != esperado:
        perdas = num_recebido - esperado
        print(f"[ALERTA] {perdas} mensagem(ns) perdida(s)!")
    esperado = num_recebido + 1
```

> **Para pensar:** números de sequência são usados em TCP, Modbus e praticamente todo protocolo confiável. A detecção de lacunas é o primeiro passo para a retransmissão — que implementaremos no passo 10.

---

## Resumo

- Duas UARTs no mesmo ESP32 com pinos cruzados reproduzem fielmente a comunicação entre placas
- Baud rates devem ser **idênticos** nos dois lados — qualquer divergência corrompe os dados
- `uart.readline()` aguarda o `'\n'` — mais prático que acumular byte a byte para mensagens simples
- O LED de feedback e as estatísticas são ferramentas de diagnóstico que você usará em projetos reais

---

*← [Passo 6](./passo06-buffer-timeout.md) | Próximo → [Passo 8: Controladora–Periférica](./passo08-controladora-periferica.md)*
