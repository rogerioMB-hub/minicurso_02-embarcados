# ============================================================
# Passo 1 — Eco Serial via UART
# Versão: SIMULAÇÃO WOKWI
# ============================================================
# Placa : ESP32 DevKit C v4
# IDE   : Wokwi (https://wokwi.com)
#
# DIFERENÇA EM RELAÇÃO À PLACA REAL:
#   Este arquivo usa uart.read(1) de forma BLOQUEANTE —
#   o programa aguarda até um byte chegar antes de continuar.
#
#   Por que não usamos uart.any() aqui?
#   No Wokwi, o $serialMonitor entrega bytes com uma pequena
#   latência. uart.any() é não bloqueante e consulta o buffer
#   instantaneamente — nesse intervalo o buffer ainda está
#   vazio, então retorna 0 e o byte é "perdido" pelo programa.
#   uart.read(1) sem verificação prévia bloqueia e aguarda
#   o byte chegar, resolvendo o problema.
#
#   Na placa real (Thonny), uart.any() funciona corretamente.
#   Veja main_placa.py para a versão com uart.any().
#
# Como usar:
#   1. Clique em "Play"
#   2. Abra o Serial Monitor
#   3. Digite qualquer texto e pressione Enter
#   4. O texto será ecoado de volta
# ============================================================

from machine import UART, Pin  # type: ignore[import]

BAUD_RATE = 9600
uart = UART(1, baudrate=BAUD_RATE, tx=Pin(1), rx=Pin(3))

print("=" * 40)
print("  Passo 1 — Eco Serial UART  [Wokwi]")
print("=" * 40)
print(f"  UART1 | TX=GPIO1 | RX=GPIO3 | {BAUD_RATE} bps")
print("  Digite algo no Serial Monitor...")
print("=" * 40)

while True:
    byte = uart.read(1)      # bloqueante — aguarda o byte chegar
    uart.write(byte)         # ecoa de volta
    print(byte.decode(), end="")
