# ============================================================
# Passo 3 — Dicionário de Comandos via UART
# Versão: SIMULAÇÃO WOKWI
# ============================================================
# Placa : ESP32 DevKit C v4  |  IDE: Wokwi
#
# DIFERENÇA EM RELAÇÃO À PLACA REAL:
#   Usamos input() para ler do $serialMonitor — confiável no Wokwi.
#   Na placa real (main_placa.py), usamos uart.any() + uart.read().
#
# Como usar: envie um dígito de 1 a 9 + Enter
# ============================================================

print("=" * 40)
print("  Passo 3 — Dicionário  [Wokwi]")
print("=" * 40)
print("  Envie um dígito de 1 a 9 + Enter")
print("=" * 40)

digitos = {
    '1': 'um',    '2': 'dois',   '3': 'três',
    '4': 'quatro','5': 'cinco',  '6': 'seis',
    '7': 'sete',  '8': 'oito',   '9': 'nove',
}

while True:
    entrada = input(">> ").strip()

    if entrada == '':
        continue   # ignora linha vazia

    # trata apenas o primeiro caractere digitado
    char = entrada[0]

    if char in digitos:
        resposta = digitos[char]
        print(f"'{char}' → {resposta}")
    else:
        print(f"'{char}' não reconhecido. Use um dígito de 1 a 9.")
