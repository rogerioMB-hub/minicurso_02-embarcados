# ============================================================
# Passo 1 — Eco Serial via UART
# Versão: PLACA REAL (ESP32 / Raspberry Pi Pico)
# ============================================================
# Placa : ESP32 DevKit  ou  Raspberry Pi Pico
# IDE   : Thonny
#
# DIFERENÇA EM RELAÇÃO AO WOKWI:
#   Esta versão usa o padrão não bloqueante uart.any() +
#   uart.read(1), que é o correto para uso em hardware real.
#
# ------------------------------------
# Por que uart.any() na placa real?
# ------------------------------------
#   uart.any() consulta quantos bytes estão disponíveis no
#   buffer de recepção da UART naquele instante, SEM bloquear
#   o programa. Se não houver bytes, o loop continua rodando
#   normalmente — permitindo que outras tarefas sejam feitas
#   enquanto se aguarda dados (ex: piscar LED, ler sensor).
#
#   Na placa real, o driver de hardware da UART preenche o
#   buffer imediatamente ao receber cada byte. uart.any()
#   enxerga esse buffer sem latência — por isso funciona.
#
# ------------------------------------
# Por que uart.any() NÃO funciona no Wokwi?
# ------------------------------------
#   No Wokwi, o $serialMonitor simula a entrada do usuário
#   com uma pequena latência. uart.any() consulta o buffer
#   antes que o byte simulado chegue — retorna 0 e o byte
#   é ignorado. Por isso, no Wokwi usamos uart.read(1)
#   bloqueante (veja main_wokwi.py).
#
# ------------------------------------
# Configuração de pinos
# ------------------------------------
#   ESP32  : UART0 usa GPIO1 (TX) e GPIO3 (RX) — cabo USB
#   Pico W : UART0 usa GPIO0 (TX) e GPIO1 (RX)
#            ajuste UART_ID e pinos conforme sua placa
# ============================================================

from machine import UART, Pin

# --- Configuração -------------------------------------------
# ESP32:
UART_ID  = 0
TX_PIN   = 1    # GPIO1  (não é necessário declarar no ESP32
RX_PIN   = 3    # GPIO3   quando UART_ID=0, mas fica explícito)

# Raspberry Pi Pico — descomente e ajuste se necessário:
# UART_ID = 0
# TX_PIN  = 0   # GPIO0
# RX_PIN  = 1   # GPIO1

BAUD_RATE = 9600
uart = UART(UART_ID, baudrate=BAUD_RATE)

print("=" * 40)
print("  Passo 1 — Eco Serial UART  [Placa]")
print("=" * 40)
print(f"  UART{UART_ID} | {BAUD_RATE} bps")
print("  Digite algo no Shell do Thonny...")
print("=" * 40)

# --- Loop principal (não bloqueante) ------------------------
while True:
    if uart.any():           # há bytes disponíveis no buffer?
        byte = uart.read(1)  # lê 1 byte — não bloqueia
        uart.write(byte)     # ecoa de volta
        print(byte.decode(), end="")
    # aqui poderiam vir outras tarefas: ler sensor, piscar LED, etc.
