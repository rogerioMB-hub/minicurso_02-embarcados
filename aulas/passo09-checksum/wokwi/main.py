# ============================================================
# Passo 9 — Frame com Checksum XOR (simulação Wokwi)
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
#   Evolui o protocolo do passo 8 adicionando checksum XOR
#   em cada frame. Ambos os lados calculam e verificam.
#
# Formato do frame: PAYLOAD*XX\n
#   Exemplo: "REQ:TEMP*4A\n"
# ============================================================

from machine import UART, Pin  # type: ignore[import]
import time

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

INTERVALO_MS = 3000
TIMEOUT_MS   = 500
BUFFER_MAX   = 64
SENSORES     = ['TEMP', 'LUM']

# Contadores de diagnóstico
enviados  = 0
recebidos = 0
invalidos = 0

# ------------------------------------------------------------
# Funções de checksum (usadas por ambos os lados)
# ------------------------------------------------------------

def calcular_checksum(payload):
    """XOR acumulado de todos os bytes do payload."""
    resultado = 0
    for byte in payload.encode():
        resultado ^= byte
    return resultado

def montar_frame(payload):
    """Monta PAYLOAD*XX  (sem o \\n — adicionado na escrita)."""
    cs = calcular_checksum(payload)
    return f"{payload}*{cs:02X}"

def validar_frame(frame):
    """
    Valida frame no formato PAYLOAD*XX.
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
# Lógica da PERIFÉRICA
# ------------------------------------------------------------

buf_peri = ''

def peri_tick():
    """Lê UART2, valida checksum e responde com frame protegido."""
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
                if sensor in sensores:
                    payload_resp = f"DADO:{sensor}:{sensores[sensor]()}"
                else:
                    payload_resp = f"ERRO:SENSOR:{sensor}"
                resp = montar_frame(payload_resp)
                uart_peri.write(resp + '\n')
                print(f"  [PERI] '{payload}' → '{resp}'")
            else:
                resp = montar_frame("ERRO:FORMATO")
                uart_peri.write(resp + '\n')
        elif char != '\r':
            if len(buf_peri) < BUFFER_MAX:
                buf_peri += char

# ------------------------------------------------------------
# Lógica da CONTROLADORA
# ------------------------------------------------------------

def ctrl_requisitar(sensor):
    """Envia frame com checksum e aguarda resposta validada."""
    global enviados, recebidos, invalidos
    payload = f"REQ:{sensor}"
    frame   = montar_frame(payload)
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

# ------------------------------------------------------------
# Mensagem inicial
# ------------------------------------------------------------

print("=" * 44)
print("  Passo 9 — Checksum XOR (Loopback)")
print("=" * 44)
print("  UART1 (ctrl): TX=GPIO4  RX=GPIO5")
print("  UART2 (peri): TX=GPIO17 RX=GPIO16")
print("  Fio laranja : GPIO4  → GPIO16")
print("  Fio azul    : GPIO17 → GPIO5")
print(f"  Formato     : PAYLOAD*XX\\n")
print(f"  Sensores    : {', '.join(SENSORES)}")
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
        print(f"── Ciclo {ciclo} ─────────────────────────────")

        for sensor in SENSORES:
            nome, valor = ctrl_requisitar(sensor)
            if valor is not None:
                print(f"  [CTRL] ✓ [{nome}] = {valor}")
            else:
                print(f"  [CTRL] ✗ [{nome}] = FALHA")

        # Estatísticas a cada 5 ciclos
        if ciclo % 5 == 0:
            total = enviados if enviados > 0 else 1
            print(f"\n  Estatísticas:")
            print(f"    Enviados  : {enviados}")
            print(f"    Válidos   : {recebidos}")
            print(f"    Inválidos : {invalidos}")
            print(f"    Taxa OK   : {recebidos/total*100:.1f}%")

        print()
