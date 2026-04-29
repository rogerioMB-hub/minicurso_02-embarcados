---
layout: default
title: "Passo 8 — Modelo Controladora–Periférica"
---

# Passo 8 — Modelo Controladora–Periférica

> **Duração estimada:** 35 minutos  
> **Fase:** 3 de 4 — Placa ↔ Placa (loopback)

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
