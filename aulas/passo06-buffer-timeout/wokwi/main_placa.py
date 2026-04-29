# ============================================================
# Passo 6 — Buffer e Timeout na Recepção UART
# Versão: PLACA REAL (ESP32 / Raspberry Pi Pico)
# ============================================================
# Placa : ESP32 DevKit  ou  Raspberry Pi Pico  |  IDE: Thonny
#
# ------------------------------------
# Por que uart.any() na placa real?
# ------------------------------------
#   Essencial para o timeout funcionar corretamente!
#   Com uart.any(), o loop roda continuamente — mesmo sem
#   bytes chegando, a verificação de timeout é executada
#   a cada iteração. Se o transmissor parar de enviar no
#   meio de uma mensagem, o timeout dispara normalmente.
#   Na placa real, o driver preenche o buffer sem latência.
#
# ------------------------------------
# Por que uart.any() NÃO funciona no Wokwi?
# ------------------------------------
#   O $serialMonitor tem latência na entrega dos bytes.
#   uart.any() retorna 0 prematuramente — bytes são perdidos.
#   No Wokwi, uart.read(1) bloqueante é a solução (main_wokwi.py),
#   mas isso impede o timeout de funcionar durante silêncio
#   na linha — limitação aceita apenas na simulação.
# ============================================================

from machine import UART, Pin
import time

BAUD_RATE  = 9600
LED_PIN    = 2
TIMEOUT_MS = 2000   # 2 s sem '\n' → descarta
BUFFER_MAX = 64

uart = UART(0, baudrate=BAUD_RATE)
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
print("  Passo 6 — Buffer e Timeout  [Placa]")
print("=" * 40)
print(f"  Timeout: {TIMEOUT_MS} ms | Buffer máx: {BUFFER_MAX} B")
print("  Formato: COMANDO:ARGUMENTO + Enter")
print("=" * 40)

while True:
    # Timeout funciona aqui mesmo sem bytes chegando —
    # o loop não está bloqueado, roda continuamente
    if estado == RECEBENDO:
        if time.ticks_diff(time.ticks_ms(), tempo_inicio) >= TIMEOUT_MS:
            estado, buffer, tempo_inicio = descartar(
                f"timeout {TIMEOUT_MS} ms — buffer: '{buffer}'"
            )

    if uart.any():
        byte = uart.read(1)
        char = byte.decode()

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
