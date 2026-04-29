# ============================================================
# Passo 3 — Dicionário de Comandos via UART
# Versão: PLACA REAL (ESP32 / Raspberry Pi Pico)
# ============================================================
# Placa : ESP32 DevKit  ou  Raspberry Pi Pico  |  IDE: Thonny
#
# ------------------------------------
# Por que uart.any() na placa real?
# ------------------------------------
#   uart.any() é não bloqueante: o loop continua rodando
#   mesmo sem dados disponíveis, liberando o processador
#   para outras tarefas. Na placa real o buffer é preenchido
#   pelo driver de hardware sem latência.
#
# ------------------------------------
# Por que uart.any() NÃO funciona no Wokwi?
# ------------------------------------
#   O $serialMonitor entrega bytes com latência. uart.any()
#   consulta o buffer antes do byte chegar — retorna 0 e o
#   byte é ignorado. Solução no Wokwi: uart.read(1) bloqueante
#   (veja main_wokwi.py).
# ============================================================

from machine import UART

BAUD_RATE = 9600
uart = UART(0, baudrate=BAUD_RATE)

digitos = {
    '1': 'um',    '2': 'dois',   '3': 'três',
    '4': 'quatro','5': 'cinco',  '6': 'seis',
    '7': 'sete',  '8': 'oito',   '9': 'nove',
}

print("=" * 40)
print("  Passo 3 — Dicionário via UART  [Placa]")
print("=" * 40)
print("  Envie um dígito de 1 a 9")
print("=" * 40)

while True:
    if uart.any():
        byte = uart.read(1)
        char = byte.decode()

        if char in digitos:
            resposta = digitos[char]
            uart.write(resposta + '\n')
            print(f"'{char}' → {resposta}")

        elif char not in ('\n', '\r'):
            uart.write("Caractere desconhecido\n")
            print(f"Desconhecido: {repr(char)}")
