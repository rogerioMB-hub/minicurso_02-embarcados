# ============================================================
# Passo 2 — Controle de LED via UART
# Versão: PLACA REAL (ESP32 / Raspberry Pi Pico)
# ============================================================
# Placa : ESP32 DevKit  ou  Raspberry Pi Pico  |  IDE: Thonny
#
# ------------------------------------
# Por que uart.any() na placa real?
# ------------------------------------
#   uart.any() é não bloqueante: consulta o buffer da UART
#   sem travar o programa. Se não houver bytes, o loop
#   continua — permitindo tarefas paralelas (ex: ler sensor).
#   Na placa real, o driver de hardware preenche o buffer
#   imediatamente ao receber cada byte, sem latência.
#
# ------------------------------------
# Por que uart.any() NÃO funciona no Wokwi?
# ------------------------------------
#   O $serialMonitor do Wokwi tem latência na entrega dos
#   bytes. uart.any() consulta o buffer antes do byte chegar
#   e retorna 0 — o byte é perdido. No Wokwi usamos
#   uart.read(1) bloqueante (veja main_wokwi.py).
# ============================================================

from machine import UART, Pin

BAUD_RATE = 9600
LED_PIN   = 2     # ESP32: GPIO2 (LED onboard) | Pico: use 25

uart = UART(0, baudrate=BAUD_RATE)
led  = Pin(LED_PIN, Pin.OUT)

print("=" * 40)
print("  Passo 2 — Controle de LED  [Placa]")
print("=" * 40)
print("  'L' → Liga o LED | 'D' → Desliga o LED")
print("=" * 40)

while True:
    if uart.any():
        byte = uart.read(1)
        char = byte.decode()

        if char == 'L':
            led.value(1)
            uart.write("LED ligado\n")
            print("LED ligado")

        elif char == 'D':
            led.value(0)
            uart.write("LED desligado\n")
            print("LED desligado")

        elif char not in ('\n', '\r'):
            uart.write("Caractere desconhecido\n")
            print(f"Desconhecido: {repr(char)}")
    # aqui poderiam vir outras tarefas paralelas
