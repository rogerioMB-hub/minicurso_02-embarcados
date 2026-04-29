# Como publicar o Mini Curso 02 no GitHub Pages e Google Sites

Siga os mesmos passos do Mini Curso 01. Os passos são idênticos — apenas o nome do repositório muda.

---

## 1. Ajustar o `_config.yml`

Abra `_config.yml` e confirme que as URLs estão corretas:

```yaml
baseurl: "/minicurso_02-embarcados"
url: "https://rogerioMB-hub.github.io"
```

---

## 2. Criar o repositório e fazer push

```bash
git init
git add .
git commit -m "feat: mini curso 02 — UART com MicroPython"
git remote add origin https://github.com/rogerioMB-hub/minicurso_02-embarcados.git
git push -u origin main
```

---

## 3. Ativar o GitHub Pages

1. No repositório GitHub, clique em **Settings**
2. No menu lateral, clique em **Pages**
3. Em *Source*, selecione **Deploy from a branch**
4. Em *Branch*, selecione **main** e a pasta **/ (root)**
5. Clique em **Save**

Após 1 a 2 minutos, o site estará disponível em:

```
https://rogerioMB-hub.github.io/minicurso_02-embarcados
```

---

## 4. Incorporar no Google Sites

Mesmo procedimento do Mini Curso 01:

1. No Google Sites, abra a página do **Mini Curso 02**
2. No painel direito, clique em **Incorporar**
3. Cole a URL:
   ```
   https://rogerioMB-hub.github.io/minicurso_02-embarcados
   ```
4. Ajuste o tamanho do iframe

Para um botão de link direto:
- *Inserir → Botão → URL do GitHub Pages*

---

## 5. Atualizar o conteúdo

Qualquer alteração nos arquivos `.md` publicada via `git push` é refletida automaticamente no site em 1 a 2 minutos.
