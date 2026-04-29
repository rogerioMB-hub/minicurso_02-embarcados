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
