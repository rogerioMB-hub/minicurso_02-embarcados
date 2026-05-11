---
layout: default
title: "Passo 1 — Eco Serial via UART"
---

# Passo 1 — Eco Serial via UART

> **Duração estimada:** 20 minutos
> **Fase:** 1 de 4 — PC ↔ Placa via Serial Monitor

---

## Simulação e Código

> **O código completo está disponível nos arquivos abaixo.** Copie cada um para a aba correspondente no Wokwi antes de iniciar o experimento.

| Arquivo | Descrição | Link |
|---------|-----------|------|
| `diagram.json` | Circuito no simulador | [abrir](https://github.com/rogerioMB-hub/minicurso_02-embarcados/blob/main/aulas/passo01-eco-serial/wokwi/diagram.json) |
| `wokwi.toml` | Configuração do projeto | [abrir](https://github.com/rogerioMB-hub/minicurso_02-embarcados/blob/main/aulas/passo01-eco-serial/wokwi/wokwi.toml) |
| `main_wokwi.py` | Código para o Wokwi | [abrir](https://github.com/rogerioMB-hub/minicurso_02-embarcados/blob/main/aulas/passo01-eco-serial/wokwi/main_wokwi.py) |
| `main_placa.py` | Código para ESP32 real (Thonny) | [abrir](https://github.com/rogerioMB-hub/minicurso_02-embarcados/blob/main/aulas/passo01-eco-serial/wokwi/main_placa.py) |

### ⚠️ Por que dois arquivos de código?

| | `main_wokwi.py` | `main_placa.py` |
|---|---|---|
| **Leitura do terminal** | `input()` — lê linha do $serialMonitor | `if uart.any(): uart.read(1)` |
| **Comportamento** | Aguarda a linha completa (bloqueante) | Verifica byte a byte sem bloquear |
| **Uso** | Wokwi (simulação) | ESP32 com Thonny |

> **Por que `uart.any()` não funciona no Wokwi?**
> O `$serialMonitor` entrega bytes com latência de simulação. `uart.any()` consulta o buffer naquele instante — retorna `0` antes do byte chegar e o programa o ignora.
> Por isso, no Wokwi usamos `input()`, que lê diretamente do terminal de forma confiável.
> Na placa real com Thonny, o driver de hardware preenche o buffer imediatamente — `uart.any()` funciona corretamente.

---

## Objetivos

Ao final deste passo você será capaz de:

- Inicializar uma UART em MicroPython
- Verificar se há bytes disponíveis com `uart.any()`
- Ler e reenviar bytes com `uart.read()` e `uart.write()`
- Entender que a UART transmite exatamente os bytes que você enviar

---

## 1. Conceito

A UART (*Universal Asynchronous Receiver-Transmitter*) é o protocolo serial mais simples do mundo embarcado. Ela transmite bytes bit a bit, a uma velocidade configurável chamada **baud rate**.

No ESP32, a UART0 está conectada ao cabo USB — o mesmo que alimenta a placa. Isso significa que o que você digitar no Shell do Thonny (ou no Serial Monitor do Wokwi) chega diretamente ao seu programa como bytes.

| Conceito | Significado |
|----------|-------------|
| `UART(0, baudrate=9600)` | Inicializa UART0 a 9600 bits/segundo |
| `uart.any()` | Retorna o número de bytes disponíveis para leitura |
| `uart.read(1)` | Lê exatamente 1 byte — retorna `bytes` |
| `uart.write(byte)` | Envia bytes de volta pela UART |

> **Por que não bloqueante?** `uart.any()` verifica sem esperar. Se não houver dados, o programa continua seu loop. Isso é essencial em embarcados — um loop bloqueado não consegue executar outras tarefas enquanto aguarda.

---

## 2. Circuito

### Placa física (Thonny)

Nenhum fio extra necessário. A UART0 já está conectada ao USB.

```
ESP32 ──── cabo USB ──── PC
                         └── Shell do Thonny (entrada/saída)
```

### Simulação (Wokwi)

**Componentes:** apenas 1 ESP32 DevKit C v4. Link: <https://wokwi.com/projects/463768207297676289>

**Conexões no `diagram.json`:**

```json
[ "esp:TX", "$serialMonitor:RX", "", [] ],
[ "esp:RX", "$serialMonitor:TX", "", [] ]
```

---

## 3. Código

> O código completo está nos arquivos linkados acima (`main_wokwi.py` e `main_placa.py`).
> Abaixo estão os trechos essenciais comentados para leitura e compreensão.

Trecho central — leitura e eco de um byte (versão placa real):

```python
while True:
    if uart.any():               # há byte(s) disponível(is)?
        byte = uart.read(1)      # lê exatamente 1 byte
        uart.write(byte)         # ecoa o mesmo byte de volta
        print(byte.decode(), end="")  # exibe no Shell
```

**O que cada parte faz:**

| Linha | Explicação |
|-------|------------|
| `uart.any()` | Retorna `True` se houver bytes prontos — sem bloquear |
| `uart.read(1)` | Lê 1 byte — retorna objeto `bytes` |
| `uart.write(byte)` | Reenvia o mesmo byte pela UART |
| `byte.decode()` | Converte `bytes` → `str` para exibir no terminal |

---

## 4. Experimento

Execute o código e responda:

**a)** Digite a letra `A` no terminal. O que aparece de volta?

> _______________________________________________

**b)** Digite `123`. Os dígitos aparecem juntos ou um de cada vez? Por quê?

> _______________________________________________

**c)** `uart.read(1)` retorna um objeto do tipo `bytes`. Para exibir no `print()`, usamos `.decode()`. O que acontece se você remover o `.decode()` e tentar imprimir diretamente?

> _______________________________________________

**d)** O loop verifica `uart.any()` a cada iteração. Se não houver dados disponíveis, o que o programa faz?

> _______________________________________________

---

## 5. Desafio

Modifique o código para que cada byte recebido seja exibido **em três formatos** — caractere, decimal e hexadecimal:

```python
# Exemplo de saída esperada ao receber 'A':
# Char: A  |  Dec: 65  |  Hex: 0x41

byte = uart.read(1)
char = byte.decode()
dec  = byte[0]        # acessa o valor inteiro do primeiro byte
hex_ = hex(byte[0])   # converte para hexadecimal

print(f"Char: {char}  |  Dec: {dec}  |  Hex: {hex_}")
uart.write(byte)
```

> **Para pensar:** `byte[0]` retorna um inteiro entre 0 e 255. Esse é exatamente o byte transmitido pela UART. Você já trabalhou com esses valores no Mini Curso 01 — são os mesmos bits!

---

## Resumo

- A UART recebe bytes do terminal e os disponibiliza via `uart.any()` / `uart.read()`
- `uart.write()` envia bytes de volta — qualquer objeto `bytes` é aceito
- O padrão não bloqueante (`if uart.any()`) é a base de todo código UART em embarcados
- Um byte é um inteiro de 0 a 255 — os mesmos valores manipulados com bitwise

---

*Próximo passo → [Passo 2: Controle de LED via UART](./passo02-led-uart.md)*
