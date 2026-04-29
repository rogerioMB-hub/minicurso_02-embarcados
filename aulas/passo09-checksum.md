---
layout: default
title: "Passo 9 — Frame com Checksum XOR"
---

# Passo 9 — Frame com Checksum XOR

> **Duração estimada:** 35 minutos  
> **Fase:** 3 de 4 — Placa ↔ Placa (loopback)

---

## Objetivos

Ao final deste passo você será capaz de:

- Calcular um checksum XOR para detectar corrupção de dados
- Incluir e verificar o checksum em cada frame transmitido
- Entender a diferença entre **detectar** e **corrigir** erros

---

## 1. Conceito

No passo 8, um byte corrompido em trânsito seria processado silenciosamente — uma temperatura de `44.3` corrompida para `94.3` seria aceita sem questionamento.

O **checksum XOR** adiciona integridade: ambos os lados calculam o XOR de todos os bytes do payload. Se qualquer byte for alterado, o checksum diverge e o frame é descartado.

### Como funciona o XOR

```python
def calcular_checksum(payload):
    resultado = 0
    for byte in payload.encode():
        resultado ^= byte       # XOR acumulado
    return resultado

# Exemplo: "REQ:TEMP"
# R=0x52, E=0x45, Q=0x51, :=0x3A, T=0x54, E=0x45, M=0x4D, P=0x50
# XOR de todos = 0x4A
```

### Formato do frame

```
PAYLOAD*XX\n

Exemplos:
  "REQ:TEMP*4A\n"
  "DADO:TEMP:44.3*7F\n"
```

O `*` separa o payload do checksum de 2 dígitos hexadecimais. Na recepção, o receptor:
1. Divide no `*`
2. Recalcula o XOR do payload
3. Compara com o checksum recebido
4. Se divergir → descarta

> **Detectar vs. corrigir:** o XOR detecta erros, mas não consegue corrigi-los. Para correção, precisaríamos de CRC + retransmissão — que é exatamente o que implementaremos no passo 10.

---

## 2. Circuito

Mesmo do passo 8 — fios laranja e azul entre as UARTs.

---

## 3. Código

```python
# ============================================================
# Passo 9 — Frame com Checksum XOR (loopback no ESP32)
# ============================================================

from machine import UART, Pin
import time

BAUD_RATE    = 9600
INTERVALO_MS = 3000
TIMEOUT_MS   = 500
BUFFER_MAX   = 64
SENSORES     = ['TEMP', 'LUM']

uart_ctrl = UART(1, baudrate=BAUD_RATE, tx=Pin(4),  rx=Pin(5))
uart_peri = UART(2, baudrate=BAUD_RATE, tx=Pin(17), rx=Pin(16))

enviados  = 0
recebidos = 0
invalidos = 0

# ── Checksum (usado por ambos os lados) ───────────────────

def calcular_checksum(payload):
    resultado = 0
    for byte in payload.encode():
        resultado ^= byte
    return resultado

def montar_frame(payload):
    """Monta PAYLOAD*XX  (sem o \\n)."""
    cs = calcular_checksum(payload)
    return f"{payload}*{cs:02X}"

def validar_frame(frame):
    """
    Valida PAYLOAD*XX.
    Retorna (payload, True) se íntegro, (None, False) se inválido.
    """
    if '*' not in frame:
        return None, False
    partes  = frame.rsplit('*', 1)
    payload = partes[0]
    cs_rec  = partes[1]
    if len(cs_rec) != 2:
        return None, False
    try:
        cs_calc = calcular_checksum(payload)
        cs_recv = int(cs_rec, 16)
    except ValueError:
        return None, False
    return (payload, True) if cs_calc == cs_recv else (payload, False)

# ── Sensores simulados ────────────────────────────────────

def ler_temperatura():
    return f"{44.0 + (time.ticks_ms() % 10000)/10000*5:.1f}"

def ler_luminosidade():
    return f"{(time.ticks_ms() % 60000)/600:.1f}"

sensores = { 'TEMP': ler_temperatura, 'LUM': ler_luminosidade }

# ── Lógica da PERIFÉRICA ──────────────────────────────────

buf_peri = ''

def peri_tick():
    global buf_peri, invalidos
    while uart_peri.any():
        char = uart_peri.read(1).decode()
        if char == '\n':
            frame_rec = buf_peri.strip()
            buf_peri  = ''
            payload, valido = validar_frame(frame_rec)
            if not valido:
                invalidos += 1
                resp = montar_frame("ERRO:CHECKSUM")
                uart_peri.write(resp + '\n')
                print(f"  [PERI] ✗ checksum inválido: '{frame_rec}'")
            elif payload.startswith('REQ:'):
                sensor = payload[4:].upper()
                p_resp = f"DADO:{sensor}:{sensores[sensor]()}" if sensor in sensores \
                         else f"ERRO:SENSOR:{sensor}"
                resp = montar_frame(p_resp)
                uart_peri.write(resp + '\n')
                print(f"  [PERI] '{payload}' → '{resp}'")
            else:
                uart_peri.write(montar_frame("ERRO:FORMATO") + '\n')
        elif char != '\r' and len(buf_peri) < BUFFER_MAX:
            buf_peri += char

# ── Lógica da CONTROLADORA ───────────────────────────────

def ctrl_requisitar(sensor):
    global enviados, recebidos, invalidos
    frame = montar_frame(f"REQ:{sensor}")
    uart_ctrl.write(frame + '\n')
    enviados += 1
    print(f"  [CTRL] → '{frame}'")

    buf = ''
    t0  = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), t0) < TIMEOUT_MS:
        peri_tick()
        while uart_ctrl.any():
            char = uart_ctrl.read(1).decode()
            if char == '\n':
                payload_rec, valido = validar_frame(buf.strip())
                if not valido:
                    invalidos += 1
                    print(f"  [CTRL] ✗ checksum inválido na resposta")
                    return sensor, None
                recebidos += 1
                partes = payload_rec.split(':')
                if len(partes) == 3 and partes[0] == 'DADO':
                    return partes[1], partes[2]
                return sensor, None
            elif char != '\r':
                buf += char
    return sensor, None

# ── Mensagem inicial ─────────────────────────────────────

print("=" * 44)
print("  Passo 9 — Checksum XOR (loopback)")
print("=" * 44)
print("  Formato: PAYLOAD*XX\\n")
print(f"  Intervalo: {INTERVALO_MS} ms | Timeout: {TIMEOUT_MS} ms")
print("=" * 44)

# ── Loop principal ────────────────────────────────────────

ciclo     = 0
t_proximo = time.ticks_ms()

while True:
    peri_tick()
    if time.ticks_diff(time.ticks_ms(), t_proximo) >= INTERVALO_MS:
        t_proximo = time.ticks_ms()
        ciclo += 1
        print(f"\n── Ciclo {ciclo} ─────────────────────────────")
        for sensor in SENSORES:
            nome, valor = ctrl_requisitar(sensor)
            print(f"  [{nome}] = {'✓ ' + valor if valor else '✗ FALHA'}")
        if ciclo % 5 == 0:
            total = enviados or 1
            print(f"\n  Enviados: {enviados} | Válidos: {recebidos} "
                  f"| Inválidos: {invalidos} | Taxa: {recebidos/total*100:.1f}%")
```

---

## 4. Experimento

**a)** Calcule manualmente o checksum XOR de `"REQ:TEMP"`:

| Char | ASCII (hex) | XOR acumulado |
|------|-------------|---------------|
| R | 0x52 | 0x52 |
| E | 0x45 | ___ |
| Q | 0x51 | ___ |
| : | 0x3A | ___ |
| T | 0x54 | ___ |
| E | 0x45 | ___ |
| M | 0x4D | ___ |
| P | 0x50 | ___ |

> O resultado deve coincidir com o que o programa exibe.

**b)** Altere um único caractere do frame recebido antes de validar. O checksum detecta a alteração?

> _______________________________________________

**c)** O XOR consegue detectar se **dois bytes** forem trocados entre si (ex: posição 3 e 7 são trocadas)? Por quê?

> _______________________________________________

---

## 5. Desafio

Implemente **CRC-8** no lugar do XOR. O CRC-8 é mais robusto pois detecta erros em rajada:

```python
def calcular_crc8(payload, poly=0x07):
    """CRC-8 com polinômio 0x07 (padrão SMBUS)."""
    crc = 0x00
    for byte in payload.encode():
        crc ^= byte
        for _ in range(8):
            if crc & 0x80:
                crc = (crc << 1) ^ poly
            else:
                crc <<= 1
            crc &= 0xFF   # mantém 8 bits
    return crc
```

> **Para pensar:** o Modbus RTU usa CRC-16 exatamente neste papel. A ideia é idêntica à que você acabou de implementar — apenas o algoritmo é mais robusto.

---

## Resumo

- O XOR acumulado de todos os bytes do payload é o checksum mais simples possível
- `rsplit('*', 1)` divide no **último** `*` — seguro se o payload contiver `*`
- Checksum detecta erros mas não corrige — para correção, a solução é **retransmissão**
- O próximo passo implementa ACK/NAK e retransmissão automática

---

*← [Passo 8](./passo08-controladora-periferica.md) | Próximo → [Passo 10: Mini-Protocolo Completo](./passo10-protocolo.md)*
