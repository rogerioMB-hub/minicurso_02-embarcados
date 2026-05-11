# ============================================================
# Passo 5 — Máquina de Estados para Recepção UART
# Versão: SIMULAÇÃO WOKWI
# ============================================================
# Placa : ESP32 DevKit C v4  |  IDE: Wokwi
#
# DIFERENÇA EM RELAÇÃO À PLACA REAL:
#   input() entrega a linha completa de uma vez.
#   Para preservar o comportamento da máquina de estados,
#   iteramos sobre os caracteres da linha com 'for char in linha'
#   — simulando a chegada byte a byte, como na placa real.
#   Na placa real (main_placa.py), os bytes chegam via uart.read(1).
#
# Como usar: LED:L  LED:D  MSG:ola  + Enter
# Observe as transições de estado impressas no monitor.
# ============================================================

from machine import Pin  # type: ignore[import]

led = Pin(2, Pin.OUT)

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

comandos = {'LED': cmd_led, 'MSG': cmd_msg}

def processar(buf):
    linha = buf.strip()
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
    linha = input(">> ")      # lê linha completa do terminal
    linha += '\n'             # reinsere '\n' para acionar transição PROCESSANDO

    # itera caractere a caractere — simula chegada byte a byte
    for char in linha:

        if estado == IDLE:
            if char not in ('\n', '\r', ' '):
                buffer = char
                estado = RECEBENDO
                print(f"[{estado}]", end=' ')

        elif estado == RECEBENDO:
            if char == '\n':
                estado = PROCESSANDO
            elif char != '\r':
                buffer += char
            print(f"[{estado}]", end=' ')

        if estado == PROCESSANDO:
            resposta = processar(buffer)
            print(f"\n>> {resposta}")
            buffer = ''
            estado = IDLE
            print(f"[{estado}]", end=' ')

    print()   # quebra de linha ao final de cada entrada
