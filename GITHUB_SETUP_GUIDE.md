# 🚀 Guia: Criar Repositório GitHub - SAFRA 2026/27

Instruções completas para colocar seu projeto no GitHub.

---

## 📋 Pré-Requisitos

- ✅ Conta GitHub (crie em https://github.com/join se não tiver)
- ✅ Git instalado (`git --version`)
- ✅ Pasta do projeto com todos os arquivos

---

## 🔑 Passo 1: Configurar Git Localmente

### Windows/Mac/Linux

```bash
# Configure seu nome e email
git config --global user.name "Seu Nome"
git config --global user.email "seu-email@example.com"

# Verifique a configuração
git config --global user.name
git config --global user.email
```

**Ou execute o script:**

```bash
bash setup_github.sh "seu-username" "seu-email@example.com"
```

---

## 📂 Passo 2: Inicializar Repositório Local

Dentro da pasta `safra-2026`:

```bash
# Inicializar Git
git init

# Adicionar todos os arquivos
git add .

# Criar commit inicial
git commit -m "🌾 Initial commit: SAFRA 2026/27"

# Criar branch main (GitHub padrão)
git branch -M main
```

**Verificar:**
```bash
git log --oneline
# Deve mostrar seu commit
```

---

## 🌐 Passo 3: Criar Repositório no GitHub

### Via Web

1. **Abra:** https://github.com/new
2. **Preencha:**
   - Repository name: `safra-2026`
   - Description: `SAFRA 2026/27 - Daily tracking + Hedge Strategy`
   - Visibility: **Public** (para compartilhar)
   - ❌ NÃO inicialize com README (já temos!)
   - ❌ NÃO adicione .gitignore (já temos!)
   - ❌ NÃO adicione licença (já temos!)

3. **Clique:** "Create repository"

4. **Você verá:**
```
Quick setup — if you've done this kind of thing before

Get started by creating a new file or uploading an existing file. 
We recommend every repository include a README, LICENSE, and .gitignore.

…or push an existing repository from the command line

git remote add origin https://github.com/seu-usuario/safra-2026.git
git branch -M main
git push -u origin main
```

---

## 🔗 Passo 4: Conectar Local ao GitHub

Use a URL que o GitHub forneceu:

```bash
# Adicionar remoto origin
git remote add origin https://github.com/seu-usuario/safra-2026.git

# Verificar
git remote -v
# Deve mostrar:
# origin  https://github.com/seu-usuario/safra-2026.git (fetch)
# origin  https://github.com/seu-usuario/safra-2026.git (push)
```

---

## 📤 Passo 5: Fazer Upload (Push)

```bash
# Push para GitHub
git push -u origin main

# Primeira vez pode pedir autenticação:
# - Username: seu-username-github
# - Password: seu-PAT-token (ver abaixo)
```

### ✅ Se funcionar:
```
Counting objects: 42, done.
Delta compression using up to 8 threads.
Compressing objects: 100% (38/38), done.
Writing objects: 100% (42/42), 156.23 KiB | 5.40 MiB/s, done.
Total 42 (delta 15), reused 0 (delta 0)
remote: Resolving deltas: 100% (15/15), done.
To https://github.com/seu-usuario/safra-2026.git
 * [new branch]      main -> main
Branch 'main' set up to track remote branch 'main' from 'origin'.
```

### ❌ Erro de Autenticação?

GitHub não aceita mais senha simples. Use Personal Access Token:

#### Criar PAT (Personal Access Token)

1. **Vá para:** https://github.com/settings/tokens
2. **Clique:** "Generate new token (classic)"
3. **Configure:**
   - Note: `SAFRA 2026 Git Push`
   - Expiration: `90 days`
   - Scopes: marque apenas `repo` ✅
4. **Clique:** "Generate token"
5. **Copie:** O token (mostra apenas 1 vez!)

#### Usar o PAT

```bash
# Quando pedir password, cole o token
git push -u origin main

# Ou configure para salvar (não recomendado):
# Mac/Linux:
# ~/.netrc com seu token

# Windows:
# Credential Manager: adicione token GitHub
```

---

## ✨ Passo 6: Verificar no GitHub

1. **Abra:** https://github.com/seu-usuario/safra-2026
2. **Você deve ver:**
   - ✅ Todos os arquivos uploadados
   - ✅ README.md renderizado
   - ✅ Histórico de commits
   - ✅ Badges de linguagem (Python)

---

## 🔧 Passo 7: Configurar Segurança (Opcional mas Recomendado)

### Proteger Branch Main

1. **Vá para:** Settings → Branches
2. **Branch protection rules** → "Add rule"
3. **Configure:**
   - Pattern: `main`
   - ✅ Require pull request reviews before merging (mínimo 1)
   - ✅ Require status checks to pass
   - ✅ Dismiss stale pull request approvals
4. **Save**

### Habilitar GitHub Actions

1. **Vá para:** Actions
2. **Clique:** "New workflow"
3. **Escolha:** "Python application"
4. **Configure** para rodar testes automaticamente

---

## 📝 Passo 8: Adicionar Badges no README

Adicione no início do README.md:

```markdown
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub Stars](https://img.shields.io/github/stars/seu-usuario/safra-2026.svg)](https://github.com/seu-usuario/safra-2026)
[![GitHub Issues](https://img.shields.io/github/issues/seu-usuario/safra-2026.svg)](https://github.com/seu-usuario/safra-2026/issues)
```

Depois faça push novamente:

```bash
git add README.md
git commit -m "📚 Add: GitHub badges"
git push
```

---

## 🔄 Próximas Vezes (Fluxo de Trabalho)

Depois que o repositório está criado:

```bash
# 1. Fazer mudanças nos arquivos
# ... edite seus arquivos ...

# 2. Verificar status
git status

# 3. Adicionar mudanças
git add .

# 4. Commit
git commit -m "🌾 [tipo]: descrição"

# 5. Push para GitHub
git push

# Pronto! Mudanças aparecem em https://github.com/seu-usuario/safra-2026
```

---

## 🎯 Exemplo Completo (Começo ao Fim)

```bash
# 1. Clonar seu repositório (em outro computador)
git clone https://github.com/seu-usuario/safra-2026.git
cd safra-2026

# 2. Criar branch para feature
git checkout -b feature/export-csv

# 3. Fazer mudanças
# ... editar arquivos ...

# 4. Commit e push
git add .
git commit -m "🌾 Add: command export-csv"
git push origin feature/export-csv

# 5. No GitHub: abrir Pull Request
# - Clique "Compare & pull request"
# - Escreva descrição
# - Clique "Create pull request"

# 6. Reviewer aprova, você faz merge no GitHub
# - Clique "Merge pull request"

# 7. Atualizar seu local
git checkout main
git pull
```

---

## 📊 Checklist Final

```
✅ Git configurado localmente
✅ Repositório inicializado (git init)
✅ Repositório criado no GitHub
✅ Remote origin adicionado
✅ Push para GitHub bem-sucedido
✅ Arquivos visíveis no GitHub
✅ README.md renderizado
✅ PAT criado e funcionando
✅ Branch main protegida (opcional)
✅ Badges adicionadas (opcional)
```

---

## 🆘 Troubleshooting

### Erro: "remote origin already exists"

```bash
# Remover remote anterior
git remote remove origin

# Adicionar novamente
git remote add origin https://github.com/seu-usuario/safra-2026.git
```

### Erro: "Authentication failed"

```bash
# Usar PAT em vez de senha
# Gerar em: https://github.com/settings/tokens
# Use como password

# Ou configurar SSH:
ssh-keygen -t ed25519 -C "seu-email@example.com"
# Adicionar chave em GitHub → Settings → SSH Keys
# Usar URL SSH em vez de HTTPS:
git remote set-url origin git@github.com:seu-usuario/safra-2026.git
```

### Erro: "Cannot push to protected branch"

```bash
# Você criou branch errado
# Solução: criar branch feature + pull request
git checkout -b feature/sua-mudanca
git push origin feature/sua-mudanca
# Abrir PR no GitHub para fazer merge
```

### Histórico muito grande?

```bash
# Ver tamanho
git count-objects -v

# Limpar cache local
git gc --aggressive
```

---

## 📚 Recursos Adicionais

- [GitHub Docs](https://docs.github.com)
- [Git Cheat Sheet](https://education.github.com/git-cheat-sheet-education.pdf)
- [Pro Git Book](https://git-scm.com/book/pt-BR/v2)

---

## 🎉 Pronto!

Seu repositório GitHub está online! 🚀

**Próximos passos:**
1. ✅ Compartilhe com colegas
2. ✅ Configure integração contínua
3. ✅ Abra issues para bugs/features
4. ✅ Convide colaboradores

---

**Dúvidas?** Abra uma Issue em:  
https://github.com/seu-usuario/safra-2026/issues

🌾 **Transformando precisão em código, código em lucro.** 🌾
