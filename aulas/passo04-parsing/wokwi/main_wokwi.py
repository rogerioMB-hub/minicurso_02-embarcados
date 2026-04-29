# ============================================================
# Passo 4 — Parsing de Comandos com Terminador '\n'
# Versão: SIMULAÇÃO WOKWI
# ============================================================
# Placa : ESP32 DevKit C v4  |  IDE: Wokwi
#
# uart.read(1) BLOQUEANTE — aguarda o byte.
# uart.any() não funciona aqui por latência do $serialMonitor.
# Veja main_placa.py para entender o motivo e a versão correta.
#
# Como usar: LED:L  LED:D  MSG:ola  + Enter
# ============================================================

from machine import UART, Pin  # type: ignore[import]

BAUD_RATE = 9600
LED_PIN   = 2

uart   = UART(1, baudrate=BAUD_RATE, tx=Pin(1), rx=Pin(3))
led    = Pin(LED_PIN, Pin.OUT)
buffer = ''

def cmd_led(arg):
    if arg == 'L':
        led.value(1); return "LED ligado"
    elif arg == 'D':
        led.value(0); return "LED desligado"
    return f"Argumento inválido: '{arg}'"

def cmd_msg(arg):
    print(f"[MSG] {arg}"); return f"Mensagem: {arg}"

comandos = { 'LED': cmd_led, 'MSG': cmd_msg }

def processar(linha):
    linha = linha.strip()
    if ':' not in linha:
        return "Formato inválido. Use COMANDO:ARGUMENTO"
    partes  = linha.split(':', 1)
    comando = partes[0].upper()
    if comando in comandos:
        return comandos[comando](partes[1])
    return f"Comando desconhecido: '{comando}'"

print("=" * 40)
print("  Passo 4 — Parsing  [Wokwi]")
print("=" * 40)
print("  Formato: COMANDO:ARGUMENTO + Enter")
print("  Exemplos: LED:L  LED:D  MSG:ola")
print("=" * 40)

while True:
    byte = uart.read(1)
    char = byte.decode()

    if char == '\n':
        resposta = processar(buffer)
        uart.write(resposta + '\n')
        print(f">> {resposta}")
        buffer = ''
    elif char != '\r':
        buffer += char
