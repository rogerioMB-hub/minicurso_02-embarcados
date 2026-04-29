# ============================================================
# Passo 5 — Máquina de Estados para Recepção UART
# Versão: SIMULAÇÃO WOKWI
# ============================================================
# Placa : ESP32 DevKit C v4  |  IDE: Wokwi
#
# uart.read(1) BLOQUEANTE — aguarda o byte.
# uart.any() não funciona aqui por latência do $serialMonitor.
# Veja main_placa.py para entender o motivo e a versão correta.
#
# Como usar: LED:L  LED:D  MSG:ola  + Enter
# Observe as transições de estado impressas no monitor.
# ============================================================

from machine import UART, Pin  # type: ignore[import]

BAUD_RATE = 9600
LED_PIN   = 2

uart = UART(1, baudrate=BAUD_RATE, tx=Pin(1), rx=Pin(3))
led  = Pin(LED_PIN, Pin.OUT)

IDLE        = 'IDLE'
RECEBENDO   = 'RECEBENDO'
PROCESSANDO = 'PROCESSANDO'

estado = IDLE
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

def no_idle(char):
    return IDLE if char in ('\n', '\r', ' ') else RECEBENDO

def no_recebendo(char, buf):
    if char == '\n':   return PROCESSANDO, buf
    elif char == '\r': return RECEBENDO, buf
    else:              return RECEBENDO, buf + char

def processar(buffer):
    linha = buffer.strip()
    if ':' not in linha:
        return "Formato inválido. Use COMANDO:ARGUMENTO"
    partes  = linha.split(':', 1)
    comando = partes[0].upper()
    if comando in comandos:
        return comandos[comando](partes[1])
    return f"Comando desconhecido: '{comando}'"

print("=" * 40)
print("  Passo 5 — Máquina de Estados  [Wokwi]")
print("=" * 40)
print(f"  Estado inicial: {estado}")
print("  Formato: COMANDO:ARGUMENTO + Enter")
print("=" * 40)

while True:
    byte  = uart.read(1)
    char  = byte.decode()

    if estado == IDLE:
        proximo = no_idle(char)
        if proximo == RECEBENDO:
            buffer = char
        estado = proximo
        print(f"[{estado}]", end=' ')

    elif estado == RECEBENDO:
        proximo, buffer = no_recebendo(char, buffer)
        estado = proximo
        print(f"[{estado}]", end=' ')

    if estado == PROCESSANDO:
        resposta = processar(buffer)
        uart.write(resposta + '\n')
        print(f"\n>> {resposta}")
        buffer = ''
        estado = IDLE
        print(f"[{estado}]", end=' ')
