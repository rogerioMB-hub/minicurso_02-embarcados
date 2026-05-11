# ============================================================
# Passo 1 — Eco Serial via UART
# Versão: SIMULAÇÃO WOKWI
# ============================================================
# Placa : ESP32 DevKit C v4
# IDE   : Wokwi (https://wokwi.com)
#
# DIFERENÇA EM RELAÇÃO À PLACA REAL:
#   No Wokwi, uart.any() não funciona com UART0 ($serialMonitor)
#   pois os bytes chegam com latência de simulação.
#   Solução: input() lê diretamente do terminal, linha a linha,
#   de forma confiável. Na placa real, use main_placa.py.
#
# Como usar:
#   1. Clique em "Play"
#   2. Abra o Serial Monitor
#   3. Digite qualquer texto e pressione Enter
#   4. O texto será ecoado de volta, byte a byte
# ============================================================

# Nota: no Wokwi não importamos UART para comunicar com o
# terminal — usamos input() que lê do $serialMonitor diretamente.

print("=" * 40)
print("  Passo 1 — Eco Serial  [Wokwi]")
print("=" * 40)
print("  Digite algo e pressione Enter.")
print("=" * 40)

while True:
    linha = input(">> ")           # lê uma linha do Serial Monitor

    print(f"Eco: {linha}")         # ecoa o texto de volta
    print("-" * 30)

    # exibe cada byte individualmente — conecta com o Mini Curso 01
    for i, char in enumerate(linha):
        codigo = ord(char)         # valor inteiro do caractere
        print(f"  [{i}] '{char}'  dec={codigo}  hex=0x{codigo:02X}  bin=0b{codigo:08b}")
