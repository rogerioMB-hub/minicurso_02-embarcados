---
layout: default
title: "Passo 6 — Buffer e Timeout na Recepção UART"
---

# Passo 6 — Buffer e Timeout na Recepção UART

> **Duração estimada:** 30 minutos
> **Fase:** 2 de 4 — Estrutura e robustez

---

## Simulação e Código

> **O código completo está disponível nos arquivos abaixo.** Copie cada um para a aba correspondente no Wokwi antes de iniciar o experimento.

| Arquivo | Descrição | Link |
|---------|-----------|------|
| `diagram.json` | Circuito no simulador | [abrir](https://github.com/rogerioMB-hub/minicurso_02-embarcados/blob/main/aulas/passo06-buffer-timeout/wokwi/diagram.json) |
| `wokwi.toml` | Configuração do projeto | [abrir](https://github.com/rogerioMB-hub/minicurso_02-embarcados/blob/main/aulas/passo06-buffer-timeout/wokwi/wokwi.toml) |
| `main_wokwi.py` | Código para o Wokwi | [abrir](https://github.com/rogerioMB-hub/minicurso_02-embarcados/blob/main/aulas/passo06-buffer-timeout/wokwi/main_wokwi.py) |
| `main_placa.py` | Código para ESP32 real (Thonny) | [abrir](https://github.com/rogerioMB-hub/minicurso_02-embarcados/blob/main/aulas/passo06-buffer-timeout/wokwi/main_placa.py) |

### ⚠️ Por que dois arquivos de código?

| | `main_wokwi.py` | `main_placa.py` |
|---|---|---|
| **Leitura do terminal** | `input()` + iteração char a char | `if uart.any(): uart.read(1)` |
| **Timeout** | Apenas limite de buffer testável | Timeout real funciona (loop não bloqueante) |
| **Uso** | Wokwi (simulação) | ESP32 com Thonny |

> **Por que `uart.any()` não funciona no Wokwi?**
> O `$serialMonitor` entrega bytes com latência — `uart.any()` retorna `0` antes do byte chegar.
> No Wokwi usamos `input()`. Uma consequência importante: **o timeout real não é simulável no Wokwi** — como `input()` bloqueia até o Enter, não há "silêncio na linha". Use a placa real para testar o timeout.

---

## Objetivos

Ao final deste passo você será capaz de:

- Detectar e recuperar de mensagens incompletas com **timeout**
- Proteger a memória RAM com **limite de buffer**
- Usar `time.ticks_ms()` e `time.ticks_diff()` para medir tempo em embarcados

---

## 1. Conceito

Em comunicação serial real, três coisas podem dar errado:

1. **O transmissor para no meio da mensagem** — o `'\n'` nunca chega
2. **O cabo é desconectado** durante a transmissão
3. **Ruído elétrico** insere bytes extras, enchendo o buffer

Os dois mecanismos deste passo protegem contra esses cenários:

### Timeout

O sistema marca o instante em que entra em `RECEBENDO`. Se passar `TIMEOUT_MS` milissegundos sem receber o `'\n'`, a mensagem parcial é descartada e o sistema volta ao `IDLE`:

```python
decorrido = time.ticks_diff(time.ticks_ms(), tempo_inicio)
if decorrido >= TIMEOUT_MS:
    # descarta e volta ao IDLE
```

> `ticks_diff()` em vez de subtração simples: `ticks_ms()` pode dar a volta em 0 após ~12 dias. `ticks_diff()` trata esse overflow corretamente.

### Limite de buffer

Se o buffer atingir `BUFFER_MAX` bytes sem o terminador, a mensagem é descartada. Microcontroladores têm RAM limitada — um buffer ilimitado pode travar o sistema.

---

## 2. Circuito

Mesmo do passo 5 — ESP32 com Serial Monitor e LED no GPIO2.

---

## 3. Código

> O código completo está nos arquivos linkados acima (`main_wokwi.py` e `main_placa.py`).
> Abaixo estão os trechos essenciais para leitura e compreensão.

Verificação de timeout — roda a cada iteração, mesmo sem bytes chegando:

```python
# Este bloco fica FORA do if uart.any() — essencial para o timeout funcionar
if estado == RECEBENDO:
    decorrido = time.ticks_diff(time.ticks_ms(), tempo_inicio)
    if decorrido >= TIMEOUT_MS:
        estado, buffer, tempo_inicio = descartar(
            f"timeout de {TIMEOUT_MS} ms — buffer: '{buffer}'"
        )
```

Verificação de limite de buffer — dentro do estado RECEBENDO:

```python
elif len(buffer) >= BUFFER_MAX:
    estado, buffer, tempo_inicio = descartar(
        f"buffer cheio ({BUFFER_MAX} bytes)"
    )
```

Função de reset centralizada:

```python
def descartar(motivo):
    """Centraliza o reset: envia aviso e volta ao IDLE."""
    aviso = f"[DESCARTADO] {motivo}"
    uart.write(aviso + '\n')
    print(aviso)
    return IDLE, '', 0   # (estado, buffer, tempo_inicio)
```

---

## 4. Experimento

**a)** Envie `LED:L` normalmente. O sistema funciona como antes?

> _______________________________________________

**b)** Para testar o timeout na placa real: envie apenas `LED` (sem `:L\n`) e aguarde 2 segundos. O que aparece?

> _______________________________________________

**c)** A verificação de timeout ocorre **antes** de ler novos bytes. Por que isso é necessário? O que aconteceria se ela ficasse dentro do `if uart.any()`?

> _______________________________________________

**d)** Por que `ticks_diff(ticks_ms(), t0)` é preferível a `ticks_ms() - t0`?

> _______________________________________________

---

## 5. Desafio

**Desafio:** adicione um comando `CFG:TIMEOUT:valor` que permite alterar o timeout em tempo real:

```python
def cmd_cfg(argumento):
    global TIMEOUT_MS
    partes = argumento.split(':', 1)
    if len(partes) == 2 and partes[0] == 'TIMEOUT':
        try:
            novo = int(partes[1])
            if 500 <= novo <= 10000:
                TIMEOUT_MS = novo
                return f"Timeout alterado para {novo} ms"
            return "Valor deve ser entre 500 e 10000 ms"
        except ValueError:
            return "Valor inválido"
    return "Subcomando desconhecido"

comandos['CFG'] = cmd_cfg
```

> **Para pensar:** sistemas industriais frequentemente permitem reconfiguração de parâmetros em tempo real via serial — sem reiniciar o equipamento. O comando `CFG` é o embrião desse mecanismo.

---

## Resumo

- O timeout garante que o sistema não fique travado em `RECEBENDO` para sempre
- O limite de buffer protege a RAM — crítico em microcontroladores com memória limitada
- `ticks_diff()` é a forma correta de medir tempo em MicroPython (trata overflow)
- A função `descartar()` centraliza o reset — evita repetir código em dois lugares
- O timeout só funciona corretamente na placa real — no Wokwi, teste apenas o limite de buffer

---

*← [Passo 5](./passo05-maquina-estados.md) | Próximo → [Passo 7: Loopback Físico](./passo07-loopback.md)*
