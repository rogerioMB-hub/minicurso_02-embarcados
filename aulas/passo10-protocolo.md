---
layout: default
title: "Passo 10 — Mini-Protocolo Bidirecional Completo"
---

# Passo 10 — Mini-Protocolo Bidirecional Completo

> **Duração estimada:** 45 minutos  
> **Fase:** 4 de 4 — Protocolo completo

---

## Objetivos

Ao final deste passo você será capaz de:

- Estruturar um frame com SOF, tipo, payload, checksum e EOF
- Implementar ACK, NAK e retransmissão automática
- Organizar o protocolo em um **módulo compartilhado** (`protocolo.py`)
- Reconhecer os mesmos elementos em protocolos industriais reais

---

## 1. Conceito

Este passo reúne tudo que foi construído nos nove passos anteriores em um **mini-protocolo completo**:

### Estrutura do frame

```
$ TIPO : PAYLOAD * XX #
│  │      │        │  │
│  │      │        │  └── EOF  — fim de frame (fixo: '#')
│  │      │        └───── Checksum XOR em hex (2 dígitos)
│  │      └────────────── Payload da mensagem
│  └───────────────────── Tipo  — identifica a mensagem
└──────────────────────── SOF  — início de frame (fixo: '$')
```

### Tipos de frame

| Tipo | Direção | Significado |
|------|---------|-------------|
| `REQ` | ctrl → peri | Requisição de dado |
| `DAD` | peri → ctrl | Dado de resposta |
| `ACK` | qualquer | Confirmação |
| `NAK` | qualquer | Rejeição — aciona retransmissão |
| `ERR` | qualquer | Erro descritivo |

### Exemplos

```
"$REQ:TEMP*4A#"         ← controladora pede temperatura
"$DAD:TEMP:44.3*7F#"    ← periférica responde
"$NAK:CHECKSUM*XX#"     ← frame inválido → retransmite
```

### Retransmissão automática

Se a controladora receber `NAK` ou não receber resposta dentro do timeout, ela **retransmite automaticamente** até `MAX_TENTATIVAS` vezes.

> **Relação com o mundo real:** o frame `$TIPO:PAYLOAD*XX#` é estruturalmente equivalente ao frame Modbus RTU: endereço + função + dados + CRC. O SOF (`$`) equivale ao silêncio de 3,5 tempos de bit do Modbus. O NAK com retransmissão está presente no XMODEM, Modbus e TCP.

---

## 2. Circuito

Mesmo dos passos 7 a 9 — fios laranja e azul entre as UARTs.

---

## 3. Módulo compartilhado — `protocolo.py`

Grave este arquivo na placa (ou na pasta do projeto Wokwi) **antes** de rodar o `main.py`:

```python
# protocolo.py — módulo compartilhado do mini-protocolo UART

SOF = '$'   # Start of Frame
EOF = '#'   # End of Frame
SEP = ':'   # Separador de campos
CSP = '*'   # Separador de checksum

T_REQ = 'REQ'   # Requisição
T_DAD = 'DAD'   # Dado
T_ACK = 'ACK'   # Confirmação
T_NAK = 'NAK'   # Rejeição
T_ERR = 'ERR'   # Erro

TIPOS_VALIDOS  = (T_REQ, T_DAD, T_ACK, T_NAK, T_ERR)
BUFFER_MAX     = 80
MAX_TENTATIVAS = 3

def calcular_checksum(dados):
    resultado = 0
    for byte in dados.encode():
        resultado ^= byte
    return resultado

def montar_frame(tipo, payload):
    conteudo = f"{tipo}{SEP}{payload}"
    cs       = calcular_checksum(conteudo)
    return f"{SOF}{conteudo}{CSP}{cs:02X}{EOF}"

def validar_frame(frame):
    if not (frame.startswith(SOF) and frame.endswith(EOF)):
        return {'ok': False, 'erro': 'SOF/EOF ausente'}
    interior = frame[1:-1]
    if CSP not in interior:
        return {'ok': False, 'erro': 'Checksum ausente'}
    partes, cs_rec = interior.rsplit(CSP, 1), None
    conteudo       = interior.rsplit(CSP, 1)[0]
    cs_rec         = interior.rsplit(CSP, 1)[1]
    if len(cs_rec) != 2:
        return {'ok': False, 'erro': 'Checksum malformado'}
    try:
        cs_recv = int(cs_rec, 16)
        cs_calc = calcular_checksum(conteudo)
    except ValueError:
        return {'ok': False, 'erro': 'Checksum inválido'}
    if cs_calc != cs_recv:
        return {'ok': False, 'erro': f'Checksum diverge: {cs_calc:02X}≠{cs_rec}'}
    if SEP not in conteudo:
        return {'ok': False, 'erro': 'Tipo ausente'}
    tipo, payload = conteudo.split(SEP, 1)
    if tipo not in TIPOS_VALIDOS:
        return {'ok': False, 'erro': f'Tipo desconhecido: {tipo}'}
    return {'ok': True, 'tipo': tipo, 'payload': payload}

def frame_req(sensor):  return montar_frame(T_REQ, sensor)
def frame_dad(sensor, valor): return montar_frame(T_DAD, f"{sensor}{SEP}{valor}")
def frame_nak(motivo):  return montar_frame(T_NAK, motivo)
def frame_err(desc):    return montar_frame(T_ERR, desc)
def frame_ack(ref):     return montar_frame(T_ACK, ref)
```

---

## 4. Código principal — `main.py`

```python
# ============================================================
# Passo 10 — Mini-Protocolo Completo (loopback no ESP32)
# ============================================================

from machine import UART, Pin
import time
import protocolo as proto

BAUD_RATE    = 9600
INTERVALO_MS = 4000
TIMEOUT_MS   = 500
SENSORES     = ['TEMP', 'LUM']

uart_ctrl = UART(1, baudrate=BAUD_RATE, tx=Pin(4),  rx=Pin(5))
uart_peri = UART(2, baudrate=BAUD_RATE, tx=Pin(17), rx=Pin(16))

stats = { 'enviados': 0, 'confirmados': 0, 'naks': 0,
          'timeouts': 0, 'retransmissoes': 0 }

# ── Sensores simulados ────────────────────────────────────

def ler_temperatura():
    return f"{44.0 + (time.ticks_ms() % 10000)/10000*5:.1f}"

def ler_luminosidade():
    return f"{(time.ticks_ms() % 60000)/600:.1f}"

sensores = { 'TEMP': ler_temperatura, 'LUM': ler_luminosidade }

# ── Periférica — máquina de estados não bloqueante ────────

peri_buf, peri_estado, peri_t0 = '', 'IDLE', 0

def peri_tick():
    global peri_buf, peri_estado, peri_t0
    if peri_estado == 'RECEBENDO':
        if time.ticks_diff(time.ticks_ms(), peri_t0) > 1000:
            peri_buf, peri_estado = '', 'IDLE'
    while uart_peri.any():
        char = uart_peri.read(1).decode()
        if peri_estado == 'IDLE':
            if char == proto.SOF:
                peri_buf, peri_t0, peri_estado = char, time.ticks_ms(), 'RECEBENDO'
        elif peri_estado == 'RECEBENDO':
            peri_buf += char
            if char == proto.EOF:
                resultado = proto.validar_frame(peri_buf)
                if not resultado['ok']:
                    uart_peri.write(proto.frame_nak(resultado['erro'][:20]))
                    print(f"  [PERI] NAK: {resultado['erro']}")
                elif resultado['tipo'] == proto.T_REQ:
                    sensor = resultado['payload'].upper()
                    resp = proto.frame_dad(sensor, sensores[sensor]()) \
                           if sensor in sensores else proto.frame_err(f"SENSOR:{sensor}")
                    uart_peri.write(resp)
                    print(f"  [PERI] DAD: '{peri_buf}' → '{resp}'")
                peri_buf, peri_estado = '', 'IDLE'
            elif len(peri_buf) > proto.BUFFER_MAX:
                uart_peri.write(proto.frame_nak('FRAME_LONGO'))
                peri_buf, peri_estado = '', 'IDLE'

# ── Controladora — aguarda frame completo ─────────────────

def ctrl_aguardar_frame():
    buf, cap = '', False
    t0 = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), t0) < TIMEOUT_MS:
        peri_tick()
        while uart_ctrl.any():
            char = uart_ctrl.read(1).decode()
            if char == proto.SOF:
                buf, cap = char, True
            elif cap:
                buf += char
                if char == proto.EOF:
                    return buf
                if len(buf) > proto.BUFFER_MAX:
                    buf, cap = '', False
    return None

def ctrl_requisitar(sensor):
    frame = proto.frame_req(sensor)
    for tentativa in range(1, proto.MAX_TENTATIVAS + 1):
        if tentativa > 1:
            stats['retransmissoes'] += 1
            print(f"  [CTRL] ↺ Tentativa {tentativa}/{proto.MAX_TENTATIVAS}")
        uart_ctrl.write(frame)
        stats['enviados'] += 1
        print(f"  [CTRL] → '{frame.strip()}'")
        frame_rec = ctrl_aguardar_frame()
        if frame_rec is None:
            stats['timeouts'] += 1
            print(f"  [CTRL] ✗ Timeout")
            continue
        resultado = proto.validar_frame(frame_rec)
        print(f"  [CTRL] ← '{frame_rec.strip()}'")
        if not resultado['ok']:
            print(f"  [CTRL] ✗ Inválido: {resultado['erro']}")
            continue
        if resultado['tipo'] == proto.T_NAK:
            stats['naks'] += 1
            print(f"  [CTRL] ✗ NAK: '{resultado['payload']}'")
            continue
        if resultado['tipo'] == proto.T_DAD:
            partes = resultado['payload'].split(proto.SEP, 1)
            if len(partes) == 2:
                stats['confirmados'] += 1
                return partes[1], tentativa
    return None, proto.MAX_TENTATIVAS

# ── Mensagem inicial ─────────────────────────────────────

print("=" * 44)
print("  Passo 10 — Mini-Protocolo Completo")
print("=" * 44)
print(f"  Frame: SOF='{proto.SOF}' EOF='{proto.EOF}' CSP='{proto.CSP}'")
print(f"  Max tentativas: {proto.MAX_TENTATIVAS}")
print("=" * 44)

# ── Loop principal ────────────────────────────────────────

ciclo, t_proximo = 0, time.ticks_ms()

while True:
    peri_tick()
    if time.ticks_diff(time.ticks_ms(), t_proximo) >= INTERVALO_MS:
        t_proximo = time.ticks_ms()
        ciclo += 1
        print(f"\n══ Ciclo {ciclo} {'═'*34}")
        for sensor in SENSORES:
            print(f"  Sensor: {sensor}")
            valor, tent = ctrl_requisitar(sensor)
            print(f"  {'✓' if valor else '✗'} [{sensor}] = "
                  f"{valor if valor else 'FALHA'} ({tent} tentativa(s))")
        if ciclo % 5 == 0:
            total = stats['enviados'] or 1
            print(f"\n  Estatísticas: enviados={stats['enviados']} "
                  f"confirmados={stats['confirmados']} "
                  f"taxa={stats['confirmados']/total*100:.1f}%")
```

---

## 5. Experimento

**a)** Observe a sequência completa no terminal: `REQ → DAD → confirmação`. Qual é o tempo médio de um ciclo?

> _______________________________________________

**b)** No `protocolo.py`, mude `MAX_TENTATIVAS` para `1`. O que muda no comportamento do sistema?

> _______________________________________________

**c)** Identifique no frame `$DAD:TEMP:44.3*7F#` cada campo:

| Campo | Valor |
|-------|-------|
| SOF | `$` |
| Tipo | ___ |
| Payload | ___ |
| Checksum | ___ |
| EOF | ___ |

**d)** Onde você identifica elementos equivalentes ao SOF/EOF, checksum e ACK/NAK no protocolo Modbus RTU?

> _______________________________________________

---

## 6. Desafio final

Adicione um **contador de sequência** ao frame: `$REQ:TEMP:001*XX#`. A periférica verifica se o número é igual ao esperado; se não for, responde com NAK e registra a lacuna:

```python
# Na controladora: adicione número de sequência ao payload
seq = 0
def ctrl_requisitar_com_seq(sensor):
    global seq
    seq += 1
    payload = f"{sensor}:{seq:03d}"
    frame   = proto.frame_req(payload)
    # ... resto igual
```

> **Parabéns — você concluiu o Mini Curso 02!**  
> Você partiu de um eco byte a byte e chegou a um mini-protocolo com frame estruturado, checksum, ACK/NAK e retransmissão automática — os mesmos elementos presentes em Modbus, CANbus, HDLC e TCP/IP.

---

## Resumo do passo e do curso

| Conceito | Passo onde aparece | Protocolo real equivalente |
|----------|-------------------|---------------------------|
| UART básica | 1 | Todos |
| Terminador `'\n'` | 4 | NMEA, AT commands |
| Máquina de estados | 5 | Toda implementação profissional |
| Timeout + limite de buffer | 6 | TCP, Modbus |
| Loopback físico | 7 | Teste de hardware |
| Controladora–Periférica | 8 | Modbus RTU |
| Checksum XOR / CRC | 9 | Modbus, CAN, Ethernet |
| SOF/EOF + ACK/NAK + retransmissão | 10 | HDLC, PPP, XMODEM |

---

*← [Passo 9](./passo09-checksum.md) | [Voltar ao início](../index.md)*
