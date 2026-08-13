# Guia de Contribuição - SAFRA 2026/27

Obrigado por considerar contribuir para o projeto SAFRA 2026/27! 🌾

Neste documento você encontrará tudo que precisa saber para colaborar efetivamente.

---

## 💡 Tipos de Contribuição

### 🐛 Relatar Bugs

Se você encontrou um bug, abra uma [Issue](https://github.com/seu-usuario/safra-2026/issues) com:

- **Título descritivo:** "Bug: comando log não registra notas"
- **Descrição:** O que esperava acontecer vs. o que aconteceu
- **Passos para reproduzir:**
  ```bash
  python safra_2026_tracking.py log 125 62 "nota teste"
  python safra_2026_tracking.py status
  # Nota não aparece no histórico
  ```
- **Ambiente:** Python version, SO, etc.
- **Logs:** Cole output do comando que falhou

**Exemplo:**
```
Bug: Log ignora notas com espaços

Descrição: Quando registro preço com notas contendo espaços, 
a nota não é salva.

Passos:
1. python safra_2026_tracking.py log 125 62 "Queda em Chicago"
2. python safra_2026_tracking.py status
3. Nota não aparece

Esperado: "Queda em Chicago" deveria aparecer no histórico
Obtido: Notas vazias no histórico

Ambiente: Python 3.9, macOS 12
```

### 💬 Sugerir Melhorias

Para sugerir features, abra uma [Discussion](https://github.com/seu-usuario/safra-2026/discussions):

- **Título:** "Feature: gráficos de evolução de preço"
- **Descrição:** Por que isso ajudaria
- **Exemplos:** Como seria usado
- **Alternativas:** Outras soluções consideradas

**Exemplo:**
```
Feature: Exportar histórico para CSV

Por quê: Seria útil analisar dados em Excel/Python

Como seria usado:
$ python safra_2026_tracking.py export-csv
# Cria: safra_historico_20260815.csv

Benefícios:
- Integração com ferramentas de análise
- Compartilhamento de dados
- Backup adicional

Alternativas consideradas:
- JSON export (já fazemos append-only)
- Google Sheets sync (seria mais complexo)
```

### 📚 Melhorar Documentação

Documentação ruim é um bug! Você pode:

- Corrigir typos
- Esclarecer instruções confusas
- Adicionar exemplos
- Traduzir para outro idioma

Faça isso diretamente em uma Pull Request.

### ✨ Escrever Código

Quer adicionar features? Ótimo!

---

## 🚀 Como Contribuir com Código

### 1. Fork do Repositório

```bash
# No site GitHub, clique "Fork"
# Depois clone seu fork:
git clone https://github.com/seu-usuario/safra-2026.git
cd safra-2026
```

### 2. Criar Branch

```bash
# Sempre crie uma branch para sua feature
git checkout -b feature/minha-feature

# Naming: feature/*, bugfix/*, docs/*
```

### 3. Fazer Mudanças

```bash
# Edite os arquivos necessários
# Teste suas mudanças:
python safra_2026_tracking.py init
python safra_2026_tracking.py log 125
python safra_2026_tracking.py status
```

### 4. Commit com Mensagens Claras

```bash
# Mensagens em Português, emoji + ação
git commit -m "🌾 Add: comando export para CSV"
git commit -m "🐛 Fix: log ignora notas com espaços"
git commit -m "📚 Docs: melhorar guia quick-start"

# Emojis comuns:
# 🌾 = Feature principal
# 🐛 = Bug fix
# 📚 = Documentação
# 🔧 = Refatoração
# ⚡ = Performance
# 🧪 = Testes
# 🎨 = Formatação
```

### 5. Push e Pull Request

```bash
# Push para seu fork
git push origin feature/minha-feature

# No site GitHub, clique "Create Pull Request"
```

### 6. PR Description

Descreva o que você fez:

```markdown
## O que esta PR faz

Adiciona comando `export-csv` para exportar histórico

## Por quê

Usuários precisam analisar dados em Excel

## Como testar

1. python safra_2026_tracking.py log 125
2. python safra_2026_tracking.py export-csv
3. Verificar arquivo safra_historico_*.csv

## Checklist

- [x] Testes passam
- [x] Código segue o estilo do projeto
- [x] Documentação atualizada
- [x] Sem dependências novas desnecessárias
```

---

## 📋 Padrões de Código

### Estilo Python

```python
# ✅ BOM
def calcular_lucro(receita, custo):
    """Calcula lucro bruto em reais."""
    return receita - custo

cenario = tracker._detectar_cenario(preco_atual)

# ❌ RUIM
def calc_luc(r,c):
    return r-c

CENARIO = tracker._DETECTAR_CENARIO()  # MAIÚSCULAS em função
```

### Convenções

- **Funções públicas:** `minha_funcao()`
- **Funções privadas:** `_minha_funcao()`
- **Constantes:** `MINHA_CONSTANTE = 100`
- **Documentstrings:** Explicar o quê, não o como

```python
def log_dado_diario(self, preco_atual, produtividade=62, notas=""):
    """
    Registra dado de preço e produtividade no histórico.
    
    Args:
        preco_atual: Preço da saca em R$
        produtividade: Produtividade esperada (sc/ha)
        notas: Observações sobre o mercado (opcional)
        
    Returns:
        None. Salva em historico.jsonl
        
    Raises:
        FileNotFoundError: Se projeto não foi inicializado
    """
    # Implementation
    pass
```

### Nomes Significativos

```python
# ✅ BOM
custo_total_ha = 6048.01
break_even_saca = 97.55
cenario_detectado = "base"

# ❌ RUIM
ct = 6048.01
be = 97.55
c = "base"
```

---

## 🧪 Testes

Toda feature nova precisa de testes:

```python
# test_safra.py
def test_detectar_cenario():
    tracker = SafraTracker()
    assert tracker._detectar_cenario(105) == "pessimista"
    assert tracker._detectar_cenario(125) == "base"
    assert tracker._detectar_cenario(150) == "otimista"

def test_calcula_precisao():
    # Testar cálculo de precisão
    pass

def test_log_com_notas():
    # Testar se notas com espaços são salvas
    pass
```

Rodar testes:
```bash
python -m pytest test_safra.py -v
```

---

## 📖 Documentação

Ao adicionar features, atualize:

- **README.md:** Se é uma feature visível
- **Docstrings:** No código Python
- **CLAUDE_CODE_SETUP.md:** Se afeta fluxo de uso
- **CHANGELOG.md:** Na seção [Unreleased]

**Template de docstring:**

```python
def nova_funcao(param1, param2):
    """
    Uma linha explicando o que faz.
    
    Descrição mais longa se necessário.
    
    Args:
        param1: Explicação
        param2: Explicação
        
    Returns:
        Tipo e descrição do retorno
        
    Example:
        >>> nova_funcao(100, "teste")
        "Resultado"
    """
```

---

## 🔄 Processo de Review

Seu PR será revisado por:

1. **Testes automatizados** (GitHub Actions)
2. **Analista de código** (se houver)
3. **Teste manual** (se for feature importante)

Pedidos de mudança? Sem problemas! É normal.

```
Você: Enviar PR com mudança
  ↓
Revisor: Pedir ajustes
  ↓
Você: Fazer commits adicionais
  ↓
Revisor: Aprovar
  ↓
Você: Celebrar! 🎉
```

---

## ⚡ Quick Checklist Antes de Enviar PR

```bash
# 1. Código segue padrões?
python -m black safra_2026_tracking.py

# 2. Testes passam?
python -m pytest test_safra.py -v

# 3. Sem imports não usados?
python -m flake8 safra_2026_tracking.py

# 4. Documentação atualizada?
grep -r "sua-funcao" *.md  # Documentou?

# 5. Commit messages claras?
git log --oneline -5
# Devem ter emoji + ação clara

# 6. Branch está atualizado?
git fetch origin
git rebase origin/main
git push origin feature/minha-feature -f
```

---

## 📞 Perguntas?

- 💬 Abra uma [Discussion](https://github.com/seu-usuario/safra-2026/discussions)
- 💡 Comente em uma [Issue](https://github.com/seu-usuario/safra-2026/issues)
- 📧 Email: seu-email@example.com

---

## 🎯 Áreas que Precisam Ajuda

### Bugs Conhecidos
- [ ] Log ignora notas com caracteres especiais
- [ ] Precisão não reseta mensal

### Features Planejadas
- [ ] Gráficos matplotlib
- [ ] Exportação Excel
- [ ] Notificações automáticas
- [ ] API REST

### Documentação
- [ ] Guia em Espanhol
- [ ] Vídeo tutorial
- [ ] FAQ mais completo

---

## 🏆 Reconhecimento

Todo contribuidor é reconhecido em:
- README.md (seção Contributors)
- CHANGELOG.md
- Releases notes

Obrigado por melhorar este projeto! 🌾

---

**Comunidade SAFRA 2026/27**  
*Transformando precisão em lucro agrícola*
