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
