# ============================================================
# Passo 2 — Controle de LED via UART
# Versão: SIMULAÇÃO WOKWI
# ============================================================
# Placa : ESP32 DevKit C v4  |  IDE: Wokwi
#
# uart.read(1) BLOQUEANTE — aguarda o byte.
# uart.any() não funciona aqui por latência do $serialMonitor.
# Veja main_placa.py para entender o motivo e a versão correta
# para uso com hardware real.
#
# Como usar: 'L' + Enter → liga | 'D' + Enter → desliga
# ============================================================

from machine import UART, Pin  # type: ignore[import]

BAUD_RATE = 9600
LED_PIN   = 2

uart = UART(1, baudrate=BAUD_RATE, tx=Pin(1), rx=Pin(3))
led  = Pin(LED_PIN, Pin.OUT)

print("=" * 40)
print("  Passo 2 — Controle de LED  [Wokwi]")
print("=" * 40)
print("  'L' → Liga o LED | 'D' → Desliga o LED")
print("=" * 40)

while True:
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
