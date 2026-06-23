# 🚀 ConsultaNF - Guia de Deploy 24/7 + App Windows

## **Etapa 1: Deploy no Streamlit Cloud (Gratuito - 24/7)**

### 1. Preparar GitHub
```bash
# Navegue até a pasta do projeto
cd C:\Users\Laboratorio_1\Desktop\ConsultaNF

# Inicializar Git (se não tiver feito)
git init
git add .
git commit -m "ConsultaNF - Initial deploy"

# Criar repositório no GitHub (https://github.com/new)
# Depois execute:
git remote add origin https://github.com/SEU_USUARIO/consulta-nf.git
git branch -M main
git push -u origin main
```

### 2. Deploy Automático
1. Acesse: https://streamlit.io/cloud
2. Clique em **"New app"**
3. Conecte sua conta GitHub
4. Selecione:
   - Repository: `seu-usuario/consulta-nf`
   - Branch: `main`
   - Main file path: `app.py`
5. Clique **"Deploy"**

**Resultado:** Sua app estará em `https://seu-username-streamlit.streamlit.app` 🎉

---

## **Etapa 2: Criar App Windows para Facilitar Acesso**

### 1. Atualizar o link
Edite `app_launcher.py` e altere:
```python
APP_URL = "https://seu-username-streamlit.streamlit.app"  # SEU LINK DO DEPLOY
```

### 2. Gerar o executável
```bash
# Execute no terminal (dentro da pasta do projeto)
python gerar_exe.py
```

Isso criará: `dist/ConsultaNF.exe`

### 3. Testar o executável
```bash
# Execute o arquivo gerado
dist/ConsultaNF.exe
```

---

## **Etapa 3: Distribuir para Colegas**

### Opção A: Via Email/DropBox
- Envie o arquivo `dist/ConsultaNF.exe`
- Eles clicam 2x para abrir
- Interface amigável que abre a aplicação

### Opção B: Via Atalho no Desktop
```batch
# Criar arquivo: ConsultaNF.bat
@echo off
start "" "C:\Caminho\para\ConsultaNF.exe"
```

### Opção C: Via Link Direto
Compartilhe o link da aplicação:
```
https://seu-username-streamlit.streamlit.app
```

---

## **Checklist Final**

- [ ] GitHub configurado
- [ ] Repositório com código enviado
- [ ] Deploy no Streamlit Cloud ativado
- [ ] Link funcionando (acesse pelo navegador)
- [ ] `app_launcher.py` com link correto
- [ ] `ConsultaNF.exe` gerado
- [ ] Executável testado
- [ ] Colegas receberam acesso

---

## **Suporte**

### Problema: App não abre no navegador
- Verifique conexão com internet
- Verifique se o link está correto em `app_launcher.py`

### Problema: Streamlit diz "app is not available"
- Aguarde 2-3 minutos após o deploy
- Verifique se não há erros no código

### Problema: Executável não funciona em outro PC
- Certifique-se que o Windows Defender não bloqueou
- Peça para adicionar exceção de firewall

---

**Sua app agora funciona 24/7 sem você precisar deixar o PC ligado!** ✅
