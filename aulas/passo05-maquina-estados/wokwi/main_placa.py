# ============================================================
# Passo 5 — Máquina de Estados para Recepção UART
# Versão: PLACA REAL (ESP32 / Raspberry Pi Pico)
# ============================================================
# Placa : ESP32 DevKit  ou  Raspberry Pi Pico  |  IDE: Thonny
#
# ------------------------------------
# Por que uart.any() na placa real?
# ------------------------------------
#   Padrão não bloqueante essencial em FSMs: o sistema
#   permanece responsivo mesmo em estado IDLE, sem travar
#   aguardando dados. Na placa real, o driver de hardware
#   preenche o buffer sem latência.
#
# ------------------------------------
# Por que uart.any() NÃO funciona no Wokwi?
# ------------------------------------
#   O $serialMonitor tem latência na entrega dos bytes.
#   uart.any() retorna 0 antes do byte chegar — a transição
#   IDLE→RECEBENDO nunca acontece e o primeiro byte é perdido.
#   No Wokwi usamos uart.read(1) bloqueante (main_wokwi.py).
# ============================================================

from machine import UART, Pin

BAUD_RATE = 9600
LED_PIN   = 2

uart = UART(0, baudrate=BAUD_RATE)
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
print("  Passo 5 — Máquina de Estados  [Placa]")
print("=" * 40)
print(f"  Estado inicial: {estado}")
print("  Formato: COMANDO:ARGUMENTO + Enter")
print("=" * 40)

while True:
    if uart.any():
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
    # aqui poderiam vir outras tarefas: ler sensor, timeout, etc.
