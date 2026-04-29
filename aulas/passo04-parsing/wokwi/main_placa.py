# ============================================================
# Passo 4 — Parsing de Comandos com Terminador '\n'
# Versão: PLACA REAL (ESP32 / Raspberry Pi Pico)
# ============================================================
# Placa : ESP32 DevKit  ou  Raspberry Pi Pico  |  IDE: Thonny
#
# ------------------------------------
# Por que uart.any() na placa real?
# ------------------------------------
#   Padrão não bloqueante: o programa não trava enquanto
#   aguarda dados. Permite tarefas paralelas no loop.
#   Na placa real, o buffer é preenchido sem latência pelo
#   driver de hardware — uart.any() funciona corretamente.
#
# ------------------------------------
# Por que uart.any() NÃO funciona no Wokwi?
# ------------------------------------
#   O $serialMonitor tem latência na entrega dos bytes.
#   uart.any() consulta o buffer antes do byte chegar,
#   retorna 0 e o buffer nunca é preenchido — a mensagem
#   é perdida ou corrompida. Solução no Wokwi: uart.read(1)
#   bloqueante (veja main_wokwi.py).
# ============================================================

from machine import UART, Pin

BAUD_RATE = 9600
LED_PIN   = 2

uart   = UART(0, baudrate=BAUD_RATE)
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
print("  Passo 4 — Parsing  [Placa]")
print("=" * 40)
print("  Formato: COMANDO:ARGUMENTO + Enter")
print("  Exemplos: LED:L  LED:D  MSG:ola")
print("=" * 40)

while True:
    if uart.any():
        byte = uart.read(1)
        char = byte.decode()

        if char == '\n':
            resposta = processar(buffer)
            uart.write(resposta + '\n')
            print(f">> {resposta}")
            buffer = ''
        elif char != '\r':
            buffer += char
    # aqui poderiam vir outras tarefas paralelas
