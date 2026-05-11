# ============================================================
# Passo 6 — Buffer e Timeout na Recepção UART
# Versão: SIMULAÇÃO WOKWI
# ============================================================
# Placa : ESP32 DevKit C v4  |  IDE: Wokwi
#
# DIFERENÇA EM RELAÇÃO À PLACA REAL:
#   input() entrega a linha completa — timeout real não é
#   simulável (não há silêncio entre bytes). O limite de
#   buffer, porém, pode ser testado normalmente.
#   Para ver o timeout em ação, use main_placa.py com hardware real.
#
# O que pode ser testado aqui:
#   - Limite de buffer: envie string com mais de BUFFER_MAX caracteres
#   - Parsing e controle de LED normalmente
#
# Como usar: LED:L  LED:D  MSG:ola  + Enter
# ============================================================

from machine import Pin  # type: ignore[import]

led = Pin(2, Pin.OUT)

BUFFER_MAX = 64

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
    if ':' not in linha: return "Formato inválido"
    partes  = linha.split(':', 1)
    comando = partes[0].upper()
    if comando in comandos: return comandos[comando](partes[1])
    return f"Comando desconhecido: '{comando}'"

def descartar(motivo):
    aviso = f"[DESCARTADO] {motivo}"
    print(aviso)
    return IDLE, ''

print("=" * 40)
print("  Passo 6 — Buffer e Timeout  [Wokwi]")
print("=" * 40)
print(f"  Buffer máx: {BUFFER_MAX} B")
print("  Timeout: não simulável — use placa real")
print("  Formato: COMANDO:ARGUMENTO + Enter")
print("=" * 40)

while True:
    linha = input(">> ")
    linha += '\n'   # reinsere terminador para máquina de estados

    for char in linha:

        if estado == IDLE:
            if char not in ('\n', '\r', ' '):
                buffer = char
                estado = RECEBENDO
                print(f"[{estado}]", end=' ')

        elif estado == RECEBENDO:
            if char == '\n':
                estado = PROCESSANDO
            elif char == '\r':
                pass
            elif len(buffer) >= BUFFER_MAX:
                estado, buffer = descartar(
                    f"buffer cheio ({BUFFER_MAX} bytes) — entrada descartada"
                )
            else:
                buffer += char

        if estado == PROCESSANDO:
            resposta = processar(buffer)
            print(f"\n>> {resposta}")
            buffer = ''
            estado = IDLE
            print(f"[{estado}]", end=' ')

    print()
