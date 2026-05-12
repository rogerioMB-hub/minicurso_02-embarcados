---
layout: default
title: "Passo 4 — Parsing de Comandos com Terminador"
---

# Passo 4 — Parsing de Comandos com Terminador `\n`

> **Duração estimada:** 25 minutos
> **Fase:** 2 de 4 — Estrutura e robustez

---

## Simulação e Código

> **O código completo está disponível nos arquivos abaixo.** Copie cada um para a aba correspondente no Wokwi antes de iniciar o experimento.

| Arquivo | Descrição | Link |
|---------|-----------|------|
| `diagram.json` | Circuito no simulador | [abrir](https://github.com/rogerioMB-hub/minicurso_02-embarcados/blob/main/aulas/passo04-parsing/wokwi/diagram.json) |
| `wokwi.toml` | Configuração do projeto | [abrir](https://github.com/rogerioMB-hub/minicurso_02-embarcados/blob/main/aulas/passo04-parsing/wokwi/wokwi.toml) |
| `main_wokwi.py` | Código para o Wokwi | [abrir](https://github.com/rogerioMB-hub/minicurso_02-embarcados/blob/main/aulas/passo04-parsing/wokwi/main_wokwi.py) |
| `main_placa.py` | Código para ESP32 real (Thonny) | [abrir](https://github.com/rogerioMB-hub/minicurso_02-embarcados/blob/main/aulas/passo04-parsing/wokwi/main_placa.py) |

### ⚠️ Por que dois arquivos de código?

| | `main_wokwi.py` | `main_placa.py` |
|---|---|---|
| **Leitura do terminal** | `input()` — entrega a linha pronta, sem montar buffer | `if uart.any(): uart.read(1)` + buffer até `'\n'` |
| **Comportamento** | Aguarda a linha completa (bloqueante) | Verifica byte a byte sem bloquear |
| **Uso** | Wokwi (simulação) | ESP32 com Thonny |

> **Por que `uart.any()` não funciona no Wokwi?**
> O `$serialMonitor` entrega bytes com latência de simulação — `uart.any()` retorna `0` antes do byte chegar.
> No Wokwi usamos `input()`, que entrega a linha completa de uma vez, simplificando também o parsing.
> Na placa real com Thonny, `uart.any()` funciona corretamente e os bytes são acumulados no buffer manualmente.

---

## Objetivos

Ao final deste passo você será capaz de:

- Acumular bytes em um buffer até receber um terminador `'\n'`
- Separar COMANDO e ARGUMENTO com `split()`
- Entender por que o terminador é a convenção fundamental de qualquer protocolo serial

---

## 1. Conceito

### O que é parsing?

**Parsing** é o processo de analisar um texto (ou sequência de bytes) para extrair informações estruturadas dele. O nome vem do inglês *to parse* — analisar, decompor.

Você já faz parsing intuitivamente quando lê um endereço como `Rua das Flores, 123 — Sala 4`: automaticamente identifica que `Rua das Flores` é o logradouro, `123` é o número e `Sala 4` é o complemento. Um programa precisa fazer o mesmo de forma explícita.

Em comunicação serial, parsing significa **receber uma sequência de bytes e identificar o que cada parte significa**:

```
Bytes recebidos:   L E D : L \n
                   ─────   ─   ─
                  comando  arg  fim
```

O parser lê os bytes, encontra o separador `:`, e sabe que tudo antes é o comando e tudo depois é o argumento. O `\n` sinaliza que a mensagem acabou.

> **Analogia:** um parser serial faz o mesmo que você faz ao ler um e-mail — identifica remetente, assunto e corpo separando cada parte pelo formato esperado. Se o formato mudar (ex: sem assunto), o parser precisa tratar isso como erro.

---

Até aqui, cada byte recebido era um comando completo. Na prática, os comandos precisam de **argumentos**: `LED:L` para ligar, `LED:D` para desligar, `MSG:ola` para exibir texto.

O problema: a UART entrega bytes um de cada vez, sem saber onde começa ou termina uma mensagem. A solução é definir um **terminador** — um caractere especial que marca o fim da mensagem. Usamos `'\n'` (o Enter do teclado).

O programa acumula os bytes em um **buffer** até receber `'\n'`, e só então processa a mensagem completa:

```
Bytes chegando:  'L' 'E' 'D' ':' 'L' '\n'
Buffer:          "LED:L"
                              ↑
                         terminador → processa!
```

Formato adotado:
```
COMANDO:ARGUMENTO\n

Exemplos:
  LED:L\n    → liga o LED
  LED:D\n    → desliga o LED
  MSG:ola\n  → exibe "ola"
```

---

## 2. Circuito

ESP32 com Serial Monitor + LED externo no GPIO2.

Link wokwi: < https://wokwi.com/projects/463769094749642753 >

```
esp:TX  → $serialMonitor:RX
esp:RX  → $serialMonitor:TX
esp:2   → resistor 330Ω → LED → GND
```

---

## 3. Código

> O código completo está nos arquivos linkados acima (`main_wokwi.py` e `main_placa.py`).
> Abaixo estão os trechos essenciais para leitura e compreensão.

Trecho central — buffer + parsing (versão placa real):

```python
buffer = ''    # acumula os bytes da mensagem atual

while True:
    if uart.any():
        byte = uart.read(1)
        char = byte.decode()

        if char == '\n':                   # terminador detectado
            resposta = processar(buffer)
            uart.write(resposta + '\n')
            buffer = ''                    # limpa para próxima mensagem
        elif char != '\r':
            buffer += char                 # acumula no buffer
```

Função de parsing — separa COMANDO e ARGUMENTO:

```python
def processar(linha):
    linha = linha.strip()          # remove espaços e '\r'
    if ':' not in linha:
        return "Formato inválido. Use COMANDO:ARGUMENTO"
    partes    = linha.split(':', 1)   # divide só no primeiro ':'
    comando   = partes[0].upper()
    argumento = partes[1]
    if comando in comandos:
        return comandos[comando](argumento)
    return f"Comando desconhecido: '{comando}'"
```

---

## 4. Experimento

Execute o código e responda:

**a)** Digite `LED:L` e pressione Enter. O que acontece?

> _______________________________________________

**b)** Digite `led:d` (minúsculas). O LED apaga? Por quê? (dica: veja `.upper()`)

> _______________________________________________

**c)** Envie `MSG:comunicação serial`. O que aparece no terminal?

> _______________________________________________

**d)** Envie apenas `LED` sem argumento (sem os dois-pontos). Qual a resposta? Por quê?

> _______________________________________________

**e)** Por que usamos `split(':', 1)` e não apenas `split(':')`? O que mudaria para o comando `MSG:hora:12:30`?

> _______________________________________________

---

## 5. Desafio

**Desafio 1:** adicione o comando `ECO:texto` que simplesmente devolve o argumento recebido:

```python
def cmd_eco(argumento):
    return f"ECO: {argumento}"

comandos['ECO'] = cmd_eco
```

**Desafio 2:** adicione o comando `PWM:valor` que ajusta o brilho de um LED com PWM (0 a 100):

```python
from machine import PWM

pwm = PWM(Pin(LED_PIN), freq=1000)

def cmd_pwm(argumento):
    try:
        nivel = int(argumento)
        if 0 <= nivel <= 100:
            duty = int(nivel / 100 * 65535)
            pwm.duty_u16(duty)
            return f"PWM: {nivel}%"
        return "Valor deve ser 0 a 100"
    except ValueError:
        return "Argumento inválido — use número inteiro"
```

> **Para pensar:** o `try/except` protege contra argumentos inválidos (ex: `PWM:abc`). Tratar erros de entrada é uma das responsabilidades de qualquer parser real.

---

## Resumo

- O buffer acumula bytes até o terminador `'\n'` — então a mensagem é processada inteira
- `split(':', 1)` divide exatamente no primeiro `:`, preservando `:` no argumento
- `.strip()` remove `'\r'` do Windows e espaços acidentais
- O dicionário de funções (tabela de despacho) escala sem alterar a lógica de parsing

---

*← [Passo 3](./passo03-dicionario.md) | Próximo → [Passo 5: Máquina de Estados](./passo05-maquina-estados.md)*
