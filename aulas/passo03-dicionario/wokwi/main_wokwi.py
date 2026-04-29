# ============================================================
# Passo 3 — Dicionário de Comandos via UART
# Versão: SIMULAÇÃO WOKWI
# ============================================================
# Placa : ESP32 DevKit C v4  |  IDE: Wokwi
#
# uart.read(1) BLOQUEANTE — aguarda o byte.
# uart.any() não funciona aqui por latência do $serialMonitor.
# Veja main_placa.py para entender o motivo e a versão correta.
#
# Como usar: envie um dígito de 1 a 9 + Enter
# ============================================================

from machine import UART, Pin  # type: ignore[import]

BAUD_RATE = 9600
uart = UART(1, baudrate=BAUD_RATE, tx=Pin(1), rx=Pin(3))

digitos = {
    '1': 'um',    '2': 'dois',   '3': 'três',
    '4': 'quatro','5': 'cinco',  '6': 'seis',
    '7': 'sete',  '8': 'oito',   '9': 'nove',
}

print("=" * 40)
print("  Passo 3 — Dicionário via UART  [Wokwi]")
print("=" * 40)
print("  Envie um dígito de 1 a 9")
print("=" * 40)

while True:
    byte = uart.read(1)
    char = byte.decode()

    if char in digitos:
        resposta = digitos[char]
        uart.write(resposta + '\n')
        print(f"'{char}' → {resposta}")

    elif char not in ('\n', '\r'):
        uart.write("Caractere desconhecido\n")
        print(f"Desconhecido: {repr(char)}")
