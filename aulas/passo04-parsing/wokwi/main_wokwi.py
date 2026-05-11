# ============================================================
# Passo 4 — Parsing de Comandos com Terminador '\n'
# Versão: SIMULAÇÃO WOKWI
# ============================================================
# Placa : ESP32 DevKit C v4  |  IDE: Wokwi
#
# DIFERENÇA EM RELAÇÃO À PLACA REAL:
#   input() já entrega a linha completa (sem '\n') — o parsing
#   é feito sobre a string retornada, sem montar buffer manualmente.
#   Na placa real (main_placa.py), os bytes chegam um a um e o
#   buffer é montado até receber '\n'.
#
# Como usar: LED:L  LED:D  MSG:ola  + Enter
# ============================================================

from machine import Pin  # type: ignore[import]

led = Pin(2, Pin.OUT)

print("=" * 40)
print("  Passo 4 — Parsing  [Wokwi]")
print("=" * 40)
print("  Formato: COMANDO:ARGUMENTO + Enter")
print("  Exemplos: LED:L  LED:D  MSG:ola")
print("=" * 40)

def cmd_led(arg):
    if arg == 'L':
        led.value(1)
        return "LED ligado"
    elif arg == 'D':
        led.value(0)
        return "LED desligado"
    return f"Argumento inválido: '{arg}'"

def cmd_msg(arg):
    print(f"[MSG] {arg}")
    return f"Mensagem recebida: {arg}"

comandos = {'LED': cmd_led, 'MSG': cmd_msg}

def processar(linha):
    linha = linha.strip()
    if not linha:
        return None
    if ':' not in linha:
        return "Formato inválido. Use COMANDO:ARGUMENTO"
    partes  = linha.split(':', 1)
    comando = partes[0].upper()
    if comando in comandos:
        return comandos[comando](partes[1])
    return f"Comando desconhecido: '{comando}'"

while True:
    linha    = input(">> ")         # input() já entrega a linha sem '\n'
    resposta = processar(linha)
    if resposta:
        print(f">> {resposta}")
