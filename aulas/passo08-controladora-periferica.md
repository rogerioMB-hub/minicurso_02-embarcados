---
layout: default
title: "Passo 8 — Modelo Controladora–Periférica"
---

# Passo 8 — Modelo Controladora–Periférica

> **Duração estimada:** 35 minutos  
> **Fase:** 3 de 4 — Placa ↔ Placa (loopback)

---

## Simulação e Código

### Arquivos do projeto Wokwi

| Arquivo | Descrição | Link |
|---------|-----------|------|
| `diagram.json` | Circuito no simulador | [abrir](https://github.com/rogerioMB-hub/minicurso_02-embarcados/blob/main/aulas/passo08-controladora-periferica/wokwi/diagram.json) |
| `wokwi.toml` | Configuração do projeto | [abrir](https://github.com/rogerioMB-hub/minicurso_02-embarcados/blob/main/aulas/passo08-controladora-periferica/wokwi/wokwi.toml) |
| `main.py` | Código principal | [abrir](https://github.com/rogerioMB-hub/minicurso_02-embarcados/blob/main/aulas/passo08-controladora-periferica/wokwi/main.py) |


> **Como usar:** copie o conteúdo de cada arquivo para as abas correspondentes em [wokwi.com/projects/new/micropython-esp32](https://wokwi.com/projects/new/micropython-esp32).

> **Loopback:** este passo usa UART1 e UART2 com fios cruzados no mesmo ESP32.
> Nenhuma placa extra é necessária — os fios já estão configurados no `diagram.json`.

---

### `main.py`

```python
# ============================================================
# Passo 8 — Modelo Controladora–Periférica (simulação Wokwi)
# ============================================================
# Placa : ESP32 DevKit C v4  —  1 único ESP32
# IDE   : Wokwi (https://wokwi.com)
#
# Topologia de loopback com fios externos reais:
#
#   UART1 faz o papel de CONTROLADORA
#   UART2 faz o papel de PERIFÉRICA
#
#   Fios no diagrama (pontes externas entre pinos):
#     GPIO 4  (TX1) ──laranja──► GPIO 16 (RX2)
#     GPIO 17 (TX2) ──azul────► GPIO 5  (RX1)
#
#   Serial Monitor (UART0):
#     esp:TX → $serialMonitor:RX
#     esp:RX → $serialMonitor:TX
#
# O que este programa faz:
#   A "controladora" (UART1) envia requisições de sensor.
#   A "periférica"   (UART2) recebe, processa e responde.
#   Tudo no mesmo ESP32 — sem placas extras.
#
# Protocolo:
#   Controladora envia : "REQ:SENSOR\n"
#   Periférica responde: "DADO:SENSOR:VALOR\n"
# ============================================================

from machine import UART, Pin  # type: ignore[import]
import time

# ------------------------------------------------------------
# Configuração das UARTs
# ------------------------------------------------------------

BAUD_RATE = 9600

# UART1 — papel: CONTROLADORA
# TX=GPIO4 → fio laranja → GPIO16 (RX2)
uart_ctrl = UART(1, baudrate=BAUD_RATE, tx=Pin(4), rx=Pin(5))

# UART2 — papel: PERIFÉRICA
# TX=GPIO17 → fio azul → GPIO5 (RX1)
uart_peri = UART(2, baudrate=BAUD_RATE, tx=Pin(17), rx=Pin(16))

# ------------------------------------------------------------
# Parâmetros
# ------------------------------------------------------------

INTERVALO_MS = 3000   # Intervalo entre ciclos de requisição
TIMEOUT_MS   = 500    # Timeout aguardando resposta da periférica
BUFFER_MAX   = 64
SENSORES     = ['TEMP', 'LUM']

# ------------------------------------------------------------
# Sensores simulados (papel da periférica)
# ------------------------------------------------------------

_ciclo_lum = 0   # Contador para variar luminosidade

def ler_temperatura():
    """
    Simula temperatura interna do chip.
    No ESP32 real, usaria esp32.raw_temperature().
    Aqui varia levemente com o tempo para demonstrar.
    """
    base = 45.0
    variacao = (time.ticks_ms() % 10000) / 10000 * 5
    return f"{base + variacao:.1f}"

def ler_luminosidade():
    """Simula luminosidade variando de 0 a 100%."""
    global _ciclo_lum
    _ciclo_lum = (_ciclo_lum + 1) % 101
    return f"{_ciclo_lum}"

sensores = {
    'TEMP': ler_temperatura,
    'LUM' : ler_luminosidade,
}

# ------------------------------------------------------------
# Lógica da PERIFÉRICA — processa uma linha recebida
# ------------------------------------------------------------

buf_peri = ''    # Buffer de recepção da periférica

def peri_tick():
    """
    Lê bytes da UART2 (periférica) byte a byte.
    Ao receber '\n', processa a requisição e responde.
    Não bloqueante — deve ser chamada a cada iteração do loop.
    """
    global buf_peri
    while uart_peri.any():
        char = uart_peri.read(1).decode()
        if char == '\n':
            linha = buf_peri.strip()
            buf_peri = ''
            if linha.startswith('REQ:'):
                sensor = linha[4:].upper()
                if sensor in sensores:
                    valor    = sensores[sensor]()
                    resposta = f"DADO:{sensor}:{valor}"
                else:
                    resposta = f"ERRO:SENSOR_DESCONHECIDO:{sensor}"
            else:
                resposta = "ERRO:FORMATO"
            uart_peri.write(resposta + '\n')
            print(f"  [PERI] '{linha}' → '{resposta}'")
        elif char != '\r':
            if len(buf_peri) < BUFFER_MAX:
                buf_peri += char

# ------------------------------------------------------------
# Lógica da CONTROLADORA — envia requisição e aguarda resposta
# ------------------------------------------------------------

def ctrl_requisitar(sensor):
    """
    Envia 'REQ:SENSOR\n' pela UART1 e aguarda resposta.
    Retorna (sensor, valor) ou (sensor, None) se timeout.
    """
    mensagem = f"REQ:{sensor}"
    uart_ctrl.write(mensagem + '\n')
    print(f"  [CTRL] → '{mensagem}'")

    buf  = ''
    t0   = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), t0) < TIMEOUT_MS:
        # A periférica também precisa rodar durante a espera
        peri_tick()

        while uart_ctrl.any():
            char = uart_ctrl.read(1).decode()
            if char == '\n':
                partes = buf.strip().split(':')
                if len(partes) == 3 and partes[0] == 'DADO':
                    return partes[1], partes[2]
                return sensor, None
            elif char != '\r':
                buf += char

    return sensor, None   # Timeout

# ------------------------------------------------------------
# Mensagem inicial
# ------------------------------------------------------------

print("=" * 44)
print("  Passo 8 — Controladora–Periférica (Loopback)")
print("=" * 44)
print("  UART1 (ctrl): TX=GPIO4  RX=GPIO5")
print("  UART2 (peri): TX=GPIO17 RX=GPIO16")
print("  Fio laranja : GPIO4  → GPIO16")
print("  Fio azul    : GPIO17 → GPIO5")
print(f"  Sensores    : {', '.join(SENSORES)}")
print("=" * 44)
print()

# ------------------------------------------------------------
# Loop principal
# ------------------------------------------------------------

ciclo = 0
t_proximo = time.ticks_ms()

while True:
    # Periférica escuta continuamente
    peri_tick()

    # Controladora envia requisições no intervalo definido
    if time.ticks_diff(time.ticks_ms(), t_proximo) >= INTERVALO_MS:
        t_proximo = time.ticks_ms()
        ciclo += 1
        print(f"── Ciclo {ciclo} ─────────────────────────────")

        for sensor in SENSORES:
            nome, valor = ctrl_requisitar(sensor)
            if valor is not None:
                print(f"  [CTRL] ✓ [{nome}] = {valor}")
            else:
                print(f"  [CTRL] ✗ [{nome}] = TIMEOUT")

        print()
```

---
## Objetivos

Ao final deste passo você será capaz de:

- Dar papéis assimétricos às duas UARTs: controladora e periférica
- Implementar o modelo de comunicação **requisição → resposta**
- Simular leituras de sensor e retorná-las em um protocolo de texto

---

## 1. Conceito

No passo 7, as duas UARTs eram simétricas. Agora elas ganham **papéis distintos**:

| | Controladora (UART1) | Periférica (UART2) |
|---|---|---|
| Quem inicia | **Sempre** a controladora | Nunca — só responde |
| O que faz | Envia requisições | Lê o sensor e responde |
| Analogia | Mestre Modbus | Escravo Modbus |

O protocolo deste passo:

```
Controladora          Periférica
────────────          ──────────
"REQ:TEMP\n"  ──────►
              ◄──────  "DADO:TEMP:45.3\n"

"REQ:LUM\n"   ──────►
              ◄──────  "DADO:LUM:72.1\n"
```

> **Conexão com o mundo real:** este é exatamente o modelo do **Modbus RTU** — o protocolo industrial mais usado no mundo. A controladora (mestre) requisita dados; a periférica (escravo) responde. Nenhuma periférica fala sem ser perguntada.

---

## 2. Circuito

Mesmo loopback do passo 7 — fios laranja e azul entre as UARTs.

```
GPIO4  (TX1) ──laranja──► GPIO16 (RX2)
GPIO17 (TX2) ──azul────► GPIO5  (RX1)
```

Wokwi: mesmo `diagram.json` do passo 7 (sem botão, sem LED externos obrigatórios).

---

## 3. Código

```python
# ============================================================
# Passo 8 — Controladora–Periférica (loopback no ESP32)
# ============================================================

from machine import UART, Pin
import time

BAUD_RATE    = 9600
INTERVALO_MS = 3000   # intervalo entre ciclos de requisição
TIMEOUT_MS   = 500    # timeout aguardando resposta
BUFFER_MAX   = 64
SENSORES     = ['TEMP', 'LUM']

# UART1 — CONTROLADORA: TX=GPIO4 → GPIO16
uart_ctrl = UART(1, baudrate=BAUD_RATE, tx=Pin(4),  rx=Pin(5))
# UART2 — PERIFÉRICA:   TX=GPIO17 → GPIO5
uart_peri = UART(2, baudrate=BAUD_RATE, tx=Pin(17), rx=Pin(16))

# ── Sensores simulados (papel da PERIFÉRICA) ──────────────

def ler_temperatura():
    """Simula temperatura variando entre 44 °C e 49 °C."""
    base = 44.0 + (time.ticks_ms() % 10000) / 10000 * 5
    return f"{base:.1f}"

def ler_luminosidade():
    """Simula luminosidade variando de 0 a 100%."""
    return f"{(time.ticks_ms() % 60000) / 600:.1f}"

sensores = { 'TEMP': ler_temperatura, 'LUM': ler_luminosidade }

# ── Lógica da PERIFÉRICA ──────────────────────────────────

buf_peri = ''

def peri_tick():
    """Lê UART2 byte a byte e responde quando a linha fica completa."""
    global buf_peri
    while uart_peri.any():
        char = uart_peri.read(1).decode()
        if char == '\n':
            linha = buf_peri.strip()
            buf_peri = ''
            if linha.startswith('REQ:'):
                sensor = linha[4:].upper()
                if sensor in sensores:
                    resposta = f"DADO:{sensor}:{sensores[sensor]()}"
                else:
                    resposta = f"ERRO:SENSOR_DESCONHECIDO:{sensor}"
            else:
                resposta = "ERRO:FORMATO"
            uart_peri.write(resposta + '\n')
            print(f"  [PERI] '{linha}' → '{resposta}'")
        elif char != '\r' and len(buf_peri) < BUFFER_MAX:
            buf_peri += char

# ── Lógica da CONTROLADORA ───────────────────────────────

def ctrl_requisitar(sensor):
    """Envia REQ e aguarda resposta DADO."""
    mensagem = f"REQ:{sensor}"
    uart_ctrl.write(mensagem + '\n')
    print(f"  [CTRL] → '{mensagem}'")

    buf = ''
    t0  = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), t0) < TIMEOUT_MS:
        peri_tick()   # periférica precisa rodar durante a espera!
        while uart_ctrl.any():
            char = uart_ctrl.read(1).decode()
            if char == '\n':
                partes = buf.strip().split(':')
                if len(partes) == 3 and partes[0] == 'DADO':
                    return partes[1], partes[2]
                return sensor, None
            elif char != '\r':
                buf += char
    return sensor, None   # timeout

# ── Mensagem inicial ─────────────────────────────────────

print("=" * 44)
print("  Passo 8 — Controladora–Periférica")
print("=" * 44)
print("  UART1 (ctrl): TX=GPIO4  RX=GPIO5")
print("  UART2 (peri): TX=GPIO17 RX=GPIO16")
print(f"  Intervalo: {INTERVALO_MS} ms | Timeout: {TIMEOUT_MS} ms")
print("=" * 44)

# ── Loop principal ────────────────────────────────────────

ciclo     = 0
t_proximo = time.ticks_ms()

while True:
    peri_tick()   # periférica escuta continuamente

    if time.ticks_diff(time.ticks_ms(), t_proximo) >= INTERVALO_MS:
        t_proximo = time.ticks_ms()
        ciclo += 1
        print(f"\n── Ciclo {ciclo} ─────────────────────────────")
        for sensor in SENSORES:
            nome, valor = ctrl_requisitar(sensor)
            status = f"✓ {valor}" if valor else "✗ TIMEOUT"
            print(f"  [{nome}] = {status}")
```

---

## 4. Experimento

**a)** Observe o ciclo completo no terminal: requisição → resposta. Quanto tempo leva cada ciclo?

> _______________________________________________

**b)** Mude `INTERVALO_MS` para `500`. O que acontece? O timeout de 500 ms cria algum problema?

> _______________________________________________

**c)** Adicione um sensor `'UMID'` que retorna um valor fixo `"65.0"`. Basta adicionar ao dicionário `sensores` — a lógica principal não muda. Teste com `REQ:UMID`.

> _______________________________________________

**d)** Por que `peri_tick()` é chamada dentro do loop de espera da controladora?

> _______________________________________________

---

## 5. Desafio

Transforme o protocolo em **binário**: em vez de texto `"REQ:TEMP\n"`, envie um único byte de requisição e receba 2 bytes de resposta:

```python
# Protocolo binário simples:
# Requisição: 1 byte  → 0x01=TEMP  0x02=LUM
# Resposta:   2 bytes → valor inteiro big-endian (0–9999 = 0,0–99,99 °C)

# Enviando:
uart_ctrl.write(bytes([0x01]))   # requisita TEMP

# Recebendo:
dado = uart_peri.read(2)
if dado and len(dado) == 2:
    valor = (dado[0] << 8) | dado[1]   # big-endian → inteiro
    temp  = valor / 100
    print(f"TEMP: {temp:.2f} °C")
```

> **Para pensar:** protocolos binários são mais compactos e rápidos que protocolos de texto — mas mais difíceis de depurar. O Modbus RTU usa exatamente este modelo: bytes de requisição e resposta com campos de comprimento fixo.

---

## Resumo

- O modelo controladora–periférica define quem fala e quando — elimina colisões
- A periférica nunca inicia comunicação: só responde a requisições
- Adicionar um sensor novo = adicionar uma entrada ao dicionário — zero mudanças na lógica
- `peri_tick()` não bloqueante permite que controladora e periférica rodem no mesmo loop

---

*← [Passo 7](./passo07-loopback.md) | Próximo → [Passo 9: Checksum XOR](./passo09-checksum.md)*
