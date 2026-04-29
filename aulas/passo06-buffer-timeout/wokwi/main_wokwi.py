# ============================================================
# Passo 6 — Buffer e Timeout na Recepção UART
# Versão: SIMULAÇÃO WOKWI
# ============================================================
# Placa : ESP32 DevKit C v4  |  IDE: Wokwi
#
# uart.read(1) BLOQUEANTE — aguarda o byte.
# uart.any() não funciona aqui por latência do $serialMonitor.
# Veja main_placa.py para entender o motivo e a versão correta.
#
# NOTA SOBRE TIMEOUT NO WOKWI:
#   Como uart.read(1) é bloqueante, o timeout só é verificado
#   ENTRE bytes recebidos — não durante silêncio na linha.
#   Para testar o limite de buffer: envie string com >64 chars.
#   Para ver o timeout na placa real: veja main_placa.py.
#
# Como usar: LED:L  LED:D  MSG:ola  + Enter
# ============================================================

from machine import UART, Pin  # type: ignore[import]
import time

BAUD_RATE  = 9600
LED_PIN    = 2
TIMEOUT_MS = 2000
BUFFER_MAX = 64

uart = UART(1, baudrate=BAUD_RATE, tx=Pin(1), rx=Pin(3))
led  = Pin(LED_PIN, Pin.OUT)

IDLE        = 'IDLE'
RECEBENDO   = 'RECEBENDO'
PROCESSANDO = 'PROCESSANDO'

estado       = IDLE
buffer       = ''
tempo_inicio = 0

def cmd_led(arg):
    if arg == 'L':
        led.value(1); return "LED ligado"
    elif arg == 'D':
        led.value(0); return "LED desligado"
    return f"Argumento inválido: '{arg}'"

def cmd_msg(arg):
    print(f"[MSG] {arg}"); return f"Mensagem: {arg}"

comandos = { 'LED': cmd_led, 'MSG': cmd_msg }

def processar(buffer):
    linha = buffer.strip()
    if ':' not in linha: return "Formato inválido"
    partes  = linha.split(':', 1)
    comando = partes[0].upper()
    if comando in comandos: return comandos[comando](partes[1])
    return f"Comando desconhecido: '{comando}'"

def descartar(motivo):
    aviso = f"[DESCARTADO] {motivo}"
    uart.write(aviso + '\n'); print(aviso)
    return IDLE, '', 0

print("=" * 40)
print("  Passo 6 — Buffer e Timeout  [Wokwi]")
print("=" * 40)
print(f"  Timeout: {TIMEOUT_MS} ms | Buffer máx: {BUFFER_MAX} B")
print("  Formato: COMANDO:ARGUMENTO + Enter")
print("=" * 40)

while True:
    byte = uart.read(1)
    char = byte.decode()

    # Timeout verificado entre bytes (limitação do modo bloqueante)
    if estado == RECEBENDO:
        if time.ticks_diff(time.ticks_ms(), tempo_inicio) >= TIMEOUT_MS:
            estado, buffer, tempo_inicio = descartar(
                f"timeout {TIMEOUT_MS} ms — buffer: '{buffer}'"
            )

    if estado == IDLE:
        if char not in ('\n', '\r', ' '):
            buffer       = char
            tempo_inicio = time.ticks_ms()
            estado       = RECEBENDO
            print(f"[{estado}]", end=' ')

    elif estado == RECEBENDO:
        if char == '\n':
            estado = PROCESSANDO
        elif char == '\r':
            pass
        elif len(buffer) >= BUFFER_MAX:
            estado, buffer, tempo_inicio = descartar(
                f"buffer cheio ({BUFFER_MAX} bytes)"
            )
        else:
            buffer += char

    if estado == PROCESSANDO:
        resposta = processar(buffer)
        uart.write(resposta + '\n')
        print(f"\n>> {resposta}")
        buffer, tempo_inicio = '', 0
        estado = IDLE
        print(f"[{estado}]", end=' ')
