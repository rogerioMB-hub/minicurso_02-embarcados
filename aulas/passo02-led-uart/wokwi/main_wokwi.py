# ============================================================
# Passo 2 — Controle de LED via UART
# Versão: SIMULAÇÃO WOKWI
# ============================================================
# Placa : ESP32 DevKit C v4  |  IDE: Wokwi
#
# DIFERENÇA EM RELAÇÃO À PLACA REAL:
#   Usamos input() para ler do $serialMonitor — confiável no Wokwi.
#   Na placa real (main_placa.py), usamos uart.any() + uart.read().
#
# Como usar: digite 'L' + Enter para ligar | 'D' + Enter para desligar
# ============================================================

from machine import Pin  # type: ignore[import]

led = Pin(2, Pin.OUT)

print("=" * 40)
print("  Passo 2 — Controle de LED  [Wokwi]")
print("=" * 40)
print("  'L' + Enter → Liga o LED")
print("  'D' + Enter → Desliga o LED")
print("=" * 40)

while True:
    entrada = input(">> ").strip().upper()   # lê e normaliza

    if entrada == 'L':
        led.value(1)
        print("LED ligado ✓")

    elif entrada == 'D':
        led.value(0)
        print("LED desligado ✓")

    elif entrada == '':
        pass   # ignora linha vazia

    else:
        print(f"Comando '{entrada}' desconhecido. Use L ou D.")
