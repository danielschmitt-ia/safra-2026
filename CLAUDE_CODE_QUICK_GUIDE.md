# ⚡ Guia Rápido - Projeto Claude Code SAFRA 2026/27
## Setup em 5 Minutos

---

## 🎯 O que você vai fazer

```
✅ Instalar Claude Code Desktop (2 min)
✅ Preparar projeto (2 min)
✅ Fazer primeiro registro (1 min)
✅ Pronto para acompanhamento diário!
```

---

## 📦 Passo 1: Instalar Claude Code (2 minutos)

### **Windows**
1. Abra navegador → https://claude.com/download
2. Clique "Download Claude Code"
3. Execute instalador
4. Abra Command Prompt e confirme:
   ```bash
   claude-code --version
   ```

### **Mac**
1. Abra Safari/Chrome → https://claude.com/download
2. Clique "Download Claude Code for Mac"
3. Arraste para Applications
4. Abra Terminal e confirme:
   ```bash
   claude-code --version
   ```

### **Linux**
1. Abra Terminal:
   ```bash
   curl -fsSL https://download.claude.com/install.sh | bash
   claude-code --version
   ```

---

## 📂 Passo 2: Preparar Projeto (2 minutos)

### **Opção A: Quick Start (Recomendado)**

```bash
# 1. Abra Terminal/Prompt na pasta de trabalho
# Windows: Win+R → cmd
# Mac: Cmd+Space → Terminal
# Linux: Ctrl+Alt+T

# 2. Crie pasta do projeto
mkdir ~/safra-2026
cd ~/safra-2026

# 3. Copie arquivo principal
# (Copie o arquivo safra_2026_tracking.py para esta pasta)

# 4. Inicialize projeto
python safra_2026_tracking.py init

# Resultado esperado:
# 📁 Inicializando projeto SAFRA 2026/27...
# ✅ Projeto inicializado com sucesso!
```

### **Opção B: Clone do Git (Se usar Git)**

```bash
git clone https://seu-repo/safra-2026.git
cd safra-2026
python safra_2026_tracking.py init
```

---

## 📝 Passo 3: Primeiro Registro (1 minuto)

### **Registrar o preço de hoje**

```bash
# Sintaxe: python safra_2026_tracking.py log <preço>

python safra_2026_tracking.py log 125

# Resultado esperado:
# ✅ Dado registrado: R$ 125.00/saca - Cenário: base
```

### **Ver Status**

```bash
python safra_2026_tracking.py status

# Mostra:
# 🌾 SAFRA 2026/27 - STATUS DO PROJETO
# ================================================
# 📊 Informações Gerais:
#   • Versão: 1.0
#   • Localização: Luziânia, GO
#   • Área: 300 ha
#
# 💰 Dados de Preço:
#   • Preço atual: R$ 125.00/saca
#   • Break-even (IFAG): R$ 97.55/saca
#   • Margem de segurança: R$ 27.45/saca (22.0%)
#   • Cenário detectado: BASE
```

**Pronto! ✅ Seu projeto está funcionando!**

---

## 🔄 Rotina Diária (2 minutos por dia)

### **Toda manhã (06:00)**
```bash
python safra_2026_tracking.py status
```

### **Depois do fechamento Chicago (17:30)**
```bash
python safra_2026_tracking.py log 125.50 "Fechamento de hoje"
```

### **Quando preço salta (qualquer hora)**
```bash
python safra_2026_tracking.py compare
# → Sistema recomenda ação (hedge? proteção?)
```

### **Fim da semana**
```bash
python safra_2026_tracking.py export
# → Gera relatório completo
```

---

## 💡 Exemplos de Uso Prático

### **Exemplo 1: Monitoramento Normal**

**Segunda-feira, 12:00**
```bash
$ python safra_2026_tracking.py log 124.50
✅ Dado registrado: R$ 124.50/saca - Cenário: base
```

**Segunda-feira, 18:00 (Chicago fecha)**
```bash
$ python safra_2026_tracking.py log 126.00 "Chicago sobe com chuva na Argentina"
✅ Dado registrado: R$ 126.00/saca - Cenário: base
```

---

### **Exemplo 2: Alerta de Preço Baixo**

**Quinta-feira, 15:00 (queda forte)**
```bash
$ python safra_2026_tracking.py log 112.00 "Queda! El Niño reduz"
✅ Dado registrado: R$ 112.00/saca - Cenário: pessimista

$ python safra_2026_tracking.py compare
📊 COMPARAÇÃO: PREVISÃO vs REALIDADE
...
🎯 Recomendação de Hedge:
  🛡️  COMPRAR PUT proteção (strike R$ 110)
  Motivo: Preço muito baixo, proteção crítica
```

**Você contacta corretora:**
```bash
# Depois de executar PUT:
$ python safra_2026_tracking.py log 112.00 "PUT comprado @ R$3.50"
✅ Dado registrado e histórico atualizado
```

---

### **Exemplo 3: Decisão Crítica de Hedge (MAI/2026)**

**Quinta-feira 15h, Preço = R$ 128**
```bash
$ python safra_2026_tracking.py compare

🎯 Recomendação de Hedge:
  ✅ VENDER 70-80% de futuro
  Motivo: Preço em nível bom, protege lucro
```

**Você executa no telefone com corretora:**
- Vende 70% futuro (13.020 sacas)
- Deixa 30% aberto (5.580 sacas)
- Custo: ~R$ 150.000

**Registra a ação:**
```bash
$ python safra_2026_tracking.py log 128 62 "HEDGE EXECUTADO: 70% futuro em R$127"
✅ Dado registrado com status de hedge
```

---

## 🎯 Checklists

### **Setup Inicial**
```
[ ] Baixar Claude Code Desktop
[ ] Confirmar instalação (claude-code --version)
[ ] Criar pasta safra-2026
[ ] Copiar safra_2026_tracking.py
[ ] Executar init (python safra_2026_tracking.py init)
[ ] Fazer primeiro log (python safra_2026_tracking.py log 125)
[ ] Verificar status (python safra_2026_tracking.py status)
```

### **Uso Diário**
```
[ ] Manhã: Verificar status
[ ] 17:30: Registrar preço fechamento Chicago
[ ] Se alerta: Executar compare + export
[ ] Sexta: Revisar análise semanal
[ ] Fim do mês: Gerar relatório consolidado
```

### **Antes da Colheita (AGO/2026)**
```
[ ] Revisar todos cenários
[ ] Confirmar produtividade esperada
[ ] Executar compare para decisão final
[ ] Gerar relatório pré-colheita
```

---

## 🎓 Entender os Dados

### **O que é cada cenário?**

```
🔴 PESSIMISTA (R$ 100-110/saca)
   └─ Produção recorde pressiona preço
   └─ Probabilidade: 30-35%
   └─ Ação: Comprar PUT proteção

🟢 BASE (R$ 122-128/saca)
   └─ Expectativa CONAB/CEAPA
   └─ Probabilidade: 50-55% ← MAIS PROVÁVEL
   └─ Ação: Vender 70% futuro

⭐ OTIMISTA (R$ 145-155/saca)
   └─ El Niño intensifica
   └─ Probabilidade: 15-20%
   └─ Ação: Deixar 70% aberto
```

### **Break-even significa?**

```
Break-even = R$ 97,55/saca

= Preço mínimo para não perder dinheiro
= Abaixo disso → prejuízo
= Acima disso → lucro

Seu preço atual: R$ 125/saca
Margem: R$ 125 - R$ 97,55 = R$ 27,45 ✅
```

### **Cenário detectado?**

```
Se preço está em R$ 112:
  → Cenário = PESSIMISTA
  → Ação = Comprar PUT

Se preço está em R$ 125:
  → Cenário = BASE
  → Ação = Vender 70% futuro

Se preço está em R$ 148:
  → Cenário = OTIMISTA
  → Ação = Deixar 70% aberto
```

---

## 🚀 Próximos Passos Opcionais

### **Para Gráficos (Opcional)**

```bash
# Instalar matplotlib
pip install matplotlib

# Depois, no Claude Code, criar:
# novo arquivo → grafico_precos.py

# (Claude Code vai oferecer sugerir!)
```

### **Para Excel (Opcional)**

```bash
# Instalar openpyxl
pip install openpyxl

# Depois criar:
# novo arquivo → exportar_excel.py
```

### **Usar Claude Code para Melhorias**

```bash
# Abrir projeto no Claude Code:
claude-code .

# Ou:
# 1. Abra Claude Code Desktop
# 2. File → Open Folder
# 3. Selecione safra-2026
# 4. Use Claude Code para:
#    - Editar config.json
#    - Criar novos scripts
#    - Adicionar gráficos
#    - Exportar para Excel
```

---

## 🆘 Troubleshooting Rápido

### **Erro: "Comando não encontrado"**
```bash
# Verifique Python instalado
python --version

# Ou use python3:
python3 safra_2026_tracking.py status
```

### **Erro: "Arquivo não encontrado"**
```bash
# Verifique pasta atual
pwd (Mac/Linux)
cd (Windows)

# Confirme arquivo está lá:
ls safra_2026_tracking.py (Mac/Linux)
dir safra_2026_tracking.py (Windows)
```

### **Erro: "Permission denied"**
```bash
# Mac/Linux:
chmod +x safra_2026_tracking.py
python safra_2026_tracking.py status

# Windows:
# (Não aplicável, tente executar como admin)
```

### **Histórico desapareceu**
```bash
# Backup em: safra_2026_projeto/dados/historico.jsonl
# É append-only (nunca sobrescreve)
# Se apagado, recupere do backup!

# Previne:
cp -r safra_2026_projeto safra_2026_projeto.backup
```

---

## 📊 Visualizar Dados em Excel (Bônus)

### **Exportar Histórico para Excel**

```python
# Criar arquivo: safra_to_excel.py

import json
from openpyxl import Workbook
from pathlib import Path

def exportar_excel():
    dados = []
    history_file = Path("safra_2026_projeto/dados/historico.jsonl")
    
    with open(history_file, 'r') as f:
        for line in f:
            dados.append(json.loads(line))
    
    wb = Workbook()
    ws = wb.active
    
    # Cabeçalhos
    ws['A1'] = 'Data'
    ws['B1'] = 'Preço (R$/saca)'
    ws['C1'] = 'Produtividade (sc/ha)'
    ws['D1'] = 'Cenário'
    ws['E1'] = 'Notas'
    
    # Dados
    for i, d in enumerate(dados, start=2):
        ws[f'A{i}'] = d['data']
        ws[f'B{i}'] = d['preco_saca']
        ws[f'C{i}'] = d['produtividade_sc_ha']
        ws[f'D{i}'] = d['cenario_detectado']
        ws[f'E{i}'] = d['notas']
    
    wb.save('safra_historico.xlsx')
    print("✅ Exportado: safra_historico.xlsx")

if __name__ == "__main__":
    exportar_excel()
```

**Executar:**
```bash
pip install openpyxl
python safra_to_excel.py
# ✅ Exportado: safra_historico.xlsx
```

---

## ✨ Sucesso!

**Você agora tem:**
- ✅ Sistema de rastreamento diário
- ✅ Detecção automática de cenários
- ✅ Recomendações dinâmicas de hedge
- ✅ Histórico versionado
- ✅ Precisão em tempo real

**Próximo passo:**
1. Use HOJE mesmo
2. Registre preço de agora
3. Veja status
4. MAI/2026 → Execute hedge conforme recomendação

---

## 📞 Dúvidas?

1. Leia: `CLAUDE_CODE_SETUP.md` (completo)
2. Verifique: `SAFRA_2026_27_GUIA_ESTRATEGICO.md` (estratégia)
3. Teste: `python safra_2026_tracking.py version`

---

**Versão:** 1.0 - Quick Guide  
**Data:** Agosto 2026  
**Próxima versão:** Setembro 2026 com gráficos automáticos

🌾 **5 minutos de setup. 6 meses de precisão. R$ 300k+ de lucro protegido.** 🌾
