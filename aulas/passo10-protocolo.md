---
layout: default
title: "Passo 10 — Mini-Protocolo Bidirecional Completo"
---

# Passo 10 — Mini-Protocolo Bidirecional Completo

> **Duração estimada:** 45 minutos  
> **Fase:** 4 de 4 — Protocolo completo

---

## Simulação e Código

### Arquivos do projeto Wokwi

| Arquivo | Descrição | Link |
|---------|-----------|------|
| `diagram.json` | Circuito no simulador | [abrir](https://github.com/rogerioMB-hub/minicurso_02-embarcados/blob/main/aulas/passo10-protocolo/wokwi/diagram.json) |
| `wokwi.toml` | Configuração do projeto | [abrir](https://github.com/rogerioMB-hub/minicurso_02-embarcados/blob/main/aulas/passo10-protocolo/wokwi/wokwi.toml) |
| `main.py` | Código principal | [abrir](https://github.com/rogerioMB-hub/minicurso_02-embarcados/blob/main/aulas/passo10-protocolo/wokwi/main.py) |
| `protocolo.py` | Módulo compartilhado do protocolo | [abrir](https://github.com/rogerioMB-hub/minicurso_02-embarcados/blob/main/aulas/passo10-protocolo/wokwi/protocolo.py) |

> **Como usar:** copie os quatro arquivos para as abas correspondentes no Wokwi.
> O `protocolo.py` deve ser adicionado como arquivo extra clicando em **+** ao lado das abas.

> **Loopback:** fios cruzados entre UART1 e UART2 já configurados no `diagram.json`.

---

### `protocolo.py` — módulo compartilhado

```python
# ============================================================
# protocolo.py — Módulo compartilhado do mini-protocolo UART
# ============================================================
# Compatível com: Raspberry Pi Pico e ESP32
# IDE: Thonny
#
# Este módulo deve ser gravado em AMBAS as placas.
# Ele centraliza toda a lógica do protocolo, garantindo
# que controladora e periférica falem exatamente a mesma
# linguagem.
#
# Estrutura do frame:
#
#   $ TIPO : PAYLOAD * XX #
#   │  │      │        │  │
#   │  │      │        │  └── EOF  — fim de frame (fixo: '#')
#   │  │      │        └───── Checksum XOR em hex (2 dígitos)
#   │  │      └────────────── Payload — conteúdo da mensagem
#   │  └───────────────────── Tipo — identifica a mensagem
#   └──────────────────────── SOF  — início de frame (fixo: '$')
#
# Tipos de frame definidos:
#   REQ  → Requisição de dado (controladora → periférica)
#   DAD  → Dado de resposta   (periférica → controladora)
#   ACK  → Confirmação        (qualquer direção)
#   NAK  → Rejeição           (qualquer direção)
#   ERR  → Erro descritivo    (qualquer direção)
#
# Exemplos de frames completos:
#   "$REQ:TEMP*XX#"
#   "$DAD:TEMP:24.3*XX#"
#   "$ACK:REQ:TEMP*XX#"
#   "$NAK:CHECKSUM*XX#"
#   "$ERR:SENSOR_DESCONHECIDO*XX#"
#
# Onde XX é o checksum XOR em hexadecimal.
# ============================================================

# ------------------------------------------------------------
# Constantes do protocolo
# ------------------------------------------------------------

SOF = '$'    # Start of Frame
EOF = '#'    # End of Frame
SEP = ':'    # Separador de campos
CSP = '*'    # Separador de checksum

# Tipos de frame
T_REQ = 'REQ'    # Requisição
T_DAD = 'DAD'    # Dado
T_ACK = 'ACK'    # Confirmação (acknowledge)
T_NAK = 'NAK'    # Rejeição    (negative acknowledge)
T_ERR = 'ERR'    # Erro

TIPOS_VALIDOS = (T_REQ, T_DAD, T_ACK, T_NAK, T_ERR)

# Limites
BUFFER_MAX   = 80    # Tamanho máximo do frame completo
MAX_TENTATIVAS = 3   # Tentativas de retransmissão

# ------------------------------------------------------------
# Funções de checksum
# ------------------------------------------------------------

def calcular_checksum(dados):
    """
    Calcula o checksum XOR de todos os bytes da string 'dados'.
    Retorna inteiro 0–255.
    """
    resultado = 0
    for byte in dados.encode():
        resultado ^= byte
    return resultado


# ------------------------------------------------------------
# Funções de montagem e validação de frame
# ------------------------------------------------------------

def montar_frame(tipo, payload):
    """
    Monta um frame completo no formato: $TIPO:PAYLOAD*XX#
    O checksum cobre o conteúdo entre SOF e CSP: "TIPO:PAYLOAD"
    """
    conteudo = f"{tipo}{SEP}{payload}"
    cs       = calcular_checksum(conteudo)
    return f"{SOF}{conteudo}{CSP}{cs:02X}{EOF}"


def validar_frame(frame):
    """
    Valida e desempacota um frame recebido.

    Retorna um dicionário com:
      {'ok': True,  'tipo': ..., 'payload': ...}  — frame íntegro
      {'ok': False, 'erro': ...}                  — frame inválido

    Verificações realizadas (em ordem):
      1. Presença de SOF e EOF
      2. Presença do separador de checksum
      3. Tamanho do campo checksum (exatamente 2 hex digits)
      4. Validade dos hex digits
      5. Correspondência do checksum calculado vs recebido
      6. Tipo de frame reconhecido
    """
    # 1. SOF e EOF
    if not (frame.startswith(SOF) and frame.endswith(EOF)):
        return {'ok': False, 'erro': 'SOF/EOF ausente'}

    interior = frame[1:-1]          # Remove '$' e '#'

    # 2. Separador de checksum
    if CSP not in interior:
        return {'ok': False, 'erro': 'Separador de checksum ausente'}

    partes   = interior.rsplit(CSP, 1)
    conteudo = partes[0]            # "TIPO:PAYLOAD"
    cs_rec   = partes[1]            # "XX"

    # 3. Tamanho do checksum
    if len(cs_rec) != 2:
        return {'ok': False, 'erro': 'Checksum malformado'}

    # 4. Validade dos hex digits
    try:
        cs_recebido  = int(cs_rec, 16)
        cs_calculado = calcular_checksum(conteudo)
    except ValueError:
        return {'ok': False, 'erro': 'Checksum contém caracteres inválidos'}

    # 5. Comparação de checksum
    if cs_calculado != cs_recebido:
        return {'ok': False, 'erro': f'Checksum diverge: calc={cs_calculado:02X} rec={cs_rec}'}

    # 6. Tipo de frame
    if SEP not in conteudo:
        return {'ok': False, 'erro': 'Separador de tipo ausente'}

    partes2 = conteudo.split(SEP, 1)
    tipo    = partes2[0]
    payload = partes2[1]

    if tipo not in TIPOS_VALIDOS:
        return {'ok': False, 'erro': f'Tipo desconhecido: {tipo}'}

    return {'ok': True, 'tipo': tipo, 'payload': payload}


# ------------------------------------------------------------
# Frames prontos (atalhos para os mais usados)
# ------------------------------------------------------------

def frame_ack(referencia):
    """Monta um ACK referenciando o payload recebido."""
    return montar_frame(T_ACK, referencia)


def frame_nak(motivo):
    """Monta um NAK com o motivo da rejeição."""
    return montar_frame(T_NAK, motivo)


def frame_err(descricao):
    """Monta um ERR com descrição do problema."""
    return montar_frame(T_ERR, descricao)


def frame_req(sensor):
    """Monta uma requisição de sensor."""
    return montar_frame(T_REQ, sensor)


def frame_dad(sensor, valor):
    """Monta uma resposta de dado."""
    return montar_frame(T_DAD, f"{sensor}{SEP}{valor}")
```

---

### `main.py`

```python
# ============================================================
# Passo 10 — Mini-Protocolo Completo (simulação Wokwi)
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
#   Serial Monitor (UART0): esp:TX / esp:RX
#
# O que este programa faz:
#   Frame estruturado com SOF/EOF, tipo, payload, checksum XOR,
#   ACK/NAK e retransmissão automática — tudo em loopback.
#
# Estrutura do frame: $TIPO:PAYLOAD*XX#
#   SOF=$  EOF=#  CSP=*  SEP=:
#   Exemplos:
#     "$REQ:TEMP*4A#"
#     "$DAD:TEMP:45.3*7F#"
#     "$NAK:CHECKSUM*XX#"
#
# ATENÇÃO: protocolo.py deve estar na mesma pasta que main.py
# ============================================================

from machine import UART, Pin  # type: ignore[import]
import time
import protocolo as proto

# ------------------------------------------------------------
# Configuração das UARTs
# ------------------------------------------------------------

BAUD_RATE = 9600

# UART1 — CONTROLADORA: TX=GPIO4 → GPIO16 (RX2)
uart_ctrl = UART(1, baudrate=BAUD_RATE, tx=Pin(4), rx=Pin(5))

# UART2 — PERIFÉRICA: TX=GPIO17 → GPIO5 (RX1)
uart_peri = UART(2, baudrate=BAUD_RATE, tx=Pin(17), rx=Pin(16))

# ------------------------------------------------------------
# Parâmetros
# ------------------------------------------------------------

INTERVALO_MS   = 4000
TIMEOUT_MS     = 500
MAX_TENTATIVAS = proto.MAX_TENTATIVAS
SENSORES       = ['TEMP', 'LUM']

stats = {
    'enviados'      : 0,
    'confirmados'   : 0,
    'nak_recebidos' : 0,
    'timeouts'      : 0,
    'retransmissoes': 0,
}

# ------------------------------------------------------------
# Sensores simulados (papel da periférica)
# ------------------------------------------------------------

def ler_temperatura():
    base = 45.0
    variacao = (time.ticks_ms() % 10000) / 10000 * 5
    return f"{base + variacao:.1f}"

def ler_luminosidade():
    t = time.ticks_ms() % 60000
    return f"{round(t / 60000 * 100, 1)}"

sensores = {
    'TEMP': ler_temperatura,
    'LUM' : ler_luminosidade,
}

# ------------------------------------------------------------
# Lógica da PERIFÉRICA — máquina de estados não bloqueante
# ------------------------------------------------------------

peri_estado = 'IDLE'
peri_buf    = ''
peri_t0     = 0
PERI_NAK    = 0
PERI_DAD    = 0

def peri_tick():
    """
    Lê UART2 byte a byte. Ao capturar um frame completo
    ($...#), valida checksum e responde com DAD ou NAK.
    Não bloqueante.
    """
    global peri_estado, peri_buf, peri_t0, PERI_NAK, PERI_DAD

    # Timeout de segurança
    if peri_estado == 'RECEBENDO':
        if time.ticks_diff(time.ticks_ms(), peri_t0) > 1000:
            peri_estado, peri_buf = 'IDLE', ''

    while uart_peri.any():
        char = uart_peri.read(1).decode()

        if peri_estado == 'IDLE':
            if char == proto.SOF:
                peri_buf    = char
                peri_t0     = time.ticks_ms()
                peri_estado = 'RECEBENDO'

        elif peri_estado == 'RECEBENDO':
            peri_buf += char
            if char == proto.EOF:
                # Frame completo — processa
                resultado = proto.validar_frame(peri_buf)
                if not resultado['ok']:
                    PERI_NAK += 1
                    resp = proto.frame_nak(resultado['erro'][:20])
                    uart_peri.write(resp)
                    print(f"  [PERI] NAK #{PERI_NAK}: {resultado['erro']}")
                elif resultado['tipo'] == proto.T_REQ:
                    sensor = resultado['payload'].strip().upper()
                    if sensor in sensores:
                        resp = proto.frame_dad(sensor, sensores[sensor]())
                    else:
                        resp = proto.frame_err(f"SENSOR:{sensor}")
                    uart_peri.write(resp)
                    PERI_DAD += 1
                    print(f"  [PERI] DAD #{PERI_DAD:03d}: '{peri_buf}' → '{resp}'")
                else:
                    resp = proto.frame_err('TIPO_INESPERADO')
                    uart_peri.write(resp)
                peri_buf, peri_estado = '', 'IDLE'

            elif len(peri_buf) > proto.BUFFER_MAX:
                PERI_NAK += 1
                uart_peri.write(proto.frame_nak('FRAME_LONGO'))
                peri_buf, peri_estado = '', 'IDLE'

# ------------------------------------------------------------
# Lógica da CONTROLADORA — envia com retransmissão
# ------------------------------------------------------------

def ctrl_aguardar_frame():
    """Lê UART1 até capturar frame completo ($...#) ou timeout."""
    buf        = ''
    capturando = False
    t0         = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), t0) < TIMEOUT_MS:
        peri_tick()   # Periférica roda durante a espera
        while uart_ctrl.any():
            char = uart_ctrl.read(1).decode()
            if char == proto.SOF:
                buf        = char
                capturando = True
            elif capturando:
                buf += char
                if char == proto.EOF:
                    return buf
                if len(buf) > proto.BUFFER_MAX:
                    buf, capturando = '', False
    return None

def ctrl_requisitar(sensor):
    """Envia REQ com retransmissão automática em caso de NAK/timeout."""
    frame = proto.frame_req(sensor)

    for tentativa in range(1, MAX_TENTATIVAS + 1):
        if tentativa > 1:
            stats['retransmissoes'] += 1
            print(f"  [CTRL] ↺ Retransmissão {tentativa}/{MAX_TENTATIVAS}")

        uart_ctrl.write(frame)
        stats['enviados'] += 1
        print(f"  [CTRL] → [{tentativa}] '{frame.strip()}'")

        frame_rec = ctrl_aguardar_frame()

        if frame_rec is None:
            stats['timeouts'] += 1
            print(f"  [CTRL] ✗ Timeout")
            continue

        resultado = proto.validar_frame(frame_rec)
        print(f"  [CTRL] ← '{frame_rec.strip()}'")

        if not resultado['ok']:
            print(f"  [CTRL] ✗ Frame inválido: {resultado['erro']}")
            continue

        tipo    = resultado['tipo']
        payload = resultado['payload']

        if tipo == proto.T_NAK:
            stats['nak_recebidos'] += 1
            print(f"  [CTRL] ✗ NAK: '{payload}'")
            continue

        if tipo == proto.T_DAD:
            partes = payload.split(proto.SEP, 1)
            if len(partes) == 2:
                stats['confirmados'] += 1
                return partes[1], tentativa

        if tipo == proto.T_ERR:
            print(f"  [CTRL] ✗ ERR: '{payload}'")
            return None, tentativa

    return None, MAX_TENTATIVAS

# ------------------------------------------------------------
# Mensagem inicial
# ------------------------------------------------------------

print("=" * 44)
print("  Passo 10 — Mini-Protocolo (Loopback)")
print("=" * 44)
print("  UART1 (ctrl): TX=GPIO4  RX=GPIO5")
print("  UART2 (peri): TX=GPIO17 RX=GPIO16")
print("  Fio laranja : GPIO4  → GPIO16")
print("  Fio azul    : GPIO17 → GPIO5")
print(f"  Frame: SOF='{proto.SOF}' EOF='{proto.EOF}' CSP='{proto.CSP}'")
print(f"  Max tentativas: {MAX_TENTATIVAS}")
print(f"  Sensores: {', '.join(SENSORES)}")
print("=" * 44)
print()

# ------------------------------------------------------------
# Loop principal
# ------------------------------------------------------------

ciclo     = 0
t_proximo = time.ticks_ms()

while True:
    peri_tick()

    if time.ticks_diff(time.ticks_ms(), t_proximo) >= INTERVALO_MS:
        t_proximo = time.ticks_ms()
        ciclo += 1
        print(f"══ Ciclo {ciclo} {'═' * 34}")

        for sensor in SENSORES:
            print(f"  Sensor: {sensor}")
            valor, tentativas = ctrl_requisitar(sensor)
            if valor is not None:
                print(f"  [CTRL] ✓ [{sensor}] = {valor}  ({tentativas} tentativa(s))")
            else:
                print(f"  [CTRL] ✗ [{sensor}] = FALHA após {MAX_TENTATIVAS} tentativas")

        if ciclo % 5 == 0:
            total = stats['enviados'] if stats['enviados'] > 0 else 1
            taxa  = stats['confirmados'] / total * 100
            print(f"\n  ── Estatísticas ──────────────────────")
            for chave, val in stats.items():
                print(f"    {chave:<16}: {val}")
            print(f"    {'taxa OK':<16}: {taxa:.1f}%")

        print()
```

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
