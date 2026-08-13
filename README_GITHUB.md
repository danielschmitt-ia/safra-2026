# 🌾 SAFRA 2026/27 - Acompanhamento Diário com Claude Code

**Sistema profissional de rastreamento, análise de cenários e estratégia de hedge para safra 2026/27 com precisão contínua.**

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: Active](https://img.shields.io/badge/status-active-brightgreen.svg)](https://github.com)

---

## 🎯 O Que É?

Sistema de **acompanhamento diário + melhoria contínua de precisão** para a safra 2026/27 de soja em Luziânia, GO.

Integra:
- ✅ **3 cenários oficiais** (CONAB/CEAPA mai/2026)
- ✅ **Custos reais** (IFAG 2025/26: R$ 6.048/ha)
- ✅ **Detecção automática de cenários** (preço → ação)
- ✅ **Recomendações dinâmicas de hedge** (futuro + PUT)
- ✅ **Histórico auditável** (JSONL append-only)
- ✅ **Precisão melhorando em tempo real**

**Resultado esperado:** Lucro de **R$ 300k-976k** (conforme cenário), com risco gerenciado via hedge.

---

## 🚀 Quick Start

### 1. Clone o Repositório
```bash
git clone https://github.com/seu-usuario/safra-2026.git
cd safra-2026
```

### 2. Instale Python 3.7+
```bash
python --version  # Confirme: 3.7 ou superior
```

### 3. Inicialize o Projeto
```bash
python safra_2026_tracking.py init
# ✅ Cria pasta safra_2026_projeto/ com config.json
```

### 4. Registre Seu Primeiro Preço
```bash
python safra_2026_tracking.py log 125
# ✅ Dado registrado: R$ 125.00/saca - Cenário: base
```

### 5. Veja o Status
```bash
python safra_2026_tracking.py status
# Mostra: preço, cenário, margem, recomendação
```

**Pronto!** Seu sistema está funcionando.

---

## 📖 Documentação

| Arquivo | Finalidade |
|---------|-----------|
| [`CLAUDE_CODE_QUICK_GUIDE.md`](CLAUDE_CODE_QUICK_GUIDE.md) | ⚡ Setup 5 min + exemplos |
| [`CLAUDE_CODE_SETUP.md`](CLAUDE_CODE_SETUP.md) | 📚 Documentação técnica completa |
| [`SAFRA_2026_27_GUIA_ESTRATEGICO.md`](SAFRA_2026_27_GUIA_ESTRATEGICO.md) | 🎯 Estratégia de hedge + cenários |
| [`PROJETO_CLAUDE_CODE_README.md`](PROJETO_CLAUDE_CODE_README.md) | 🔍 Visão geral do projeto |

---

## 🔄 Comandos Disponíveis

```bash
# Inicializar (primeira vez)
python safra_2026_tracking.py init

# Registrar preço diário
python safra_2026_tracking.py log 125.50
python safra_2026_tracking.py log 123 62 "Queda leve em Chicago"

# Ver status do projeto
python safra_2026_tracking.py status

# Comparar com cenários + recomendação
python safra_2026_tracking.py compare

# Gerar relatório mensal
python safra_2026_tracking.py export

# Informações do projeto
python safra_2026_tracking.py version
```

---

## 📊 Cenários 2026/27

| Cenário | Faixa de Preço | Probabilidade | Lucro Esperado | Ação |
|---------|---|---|---|---|
| 🔴 Pessimista | R$ 100-110 | 30-35% | R$ 139k | Comprar PUT |
| 🟢 Base | R$ 122-128 | 50-55% | R$ 511k | Vender 70% futuro |
| ⭐ Otimista | R$ 145-155 | 15-20% | R$ 976k | Deixar 70% aberto |

**Break-even:** R$ 97,55/saca (dados IFAG 2025/26)

---

## 💾 Estrutura de Dados

O projeto cria esta estrutura:

```
safra_2026_projeto/
├── config.json              ← Configuração (versionada)
├── dados/
│   └── historico.jsonl      ← Todos os registros (append-only)
├── logs/
│   ├── 20260815.log
│   ├── 20260816.log
│   └── ...
└── relatorios/
    └── relatorio_20260831.txt
```

### config.json (exemplo)
```json
{
  "projeto": "SAFRA 2026/27",
  "area_ha": 300,
  "produtividade_esperada": 62,
  "precisao_atual": 87.5,
  "dados_atualizados_ate": "2026-08-15",
  "versoes": ["1.0"]
}
```

### historico.jsonl (cada linha é um registro)
```jsonl
{"data":"2026-08-15T17:30:00","preco_saca":125.00,"produtividade_sc_ha":62,"cenario":"base","notas":"Normal"}
{"data":"2026-08-16T17:30:00","preco_saca":123.50,"produtividade_sc_ha":62,"cenario":"base","notas":"Queda leve"}
```

---

## 🎯 Fluxo de Uso Diário

```
06:00 AM  → python safra_2026_tracking.py status
            └─ Ver status overnight

17:30 PM  → python safra_2026_tracking.py log <preço>
            └─ Registrar fechamento Chicago

Se alerta → python safra_2026_tracking.py compare
            └─ Análise + recomendação de ação

Sexta     → python safra_2026_tracking.py export
            └─ Gerar relatório semanal

Fim mês   → Revisar precisão + atualizar config.json
```

---

## 📈 Melhorias Futuras

### V1.1 (Setembro 2026)
- [ ] Gráficos automáticos (matplotlib)
- [ ] Exportação para Excel (openpyxl)
- [ ] Notificações automáticas (preço atinge limiares)

### V1.2 (Outubro 2026)
- [ ] API REST para acesso remoto
- [ ] Sincronização com Google Sheets
- [ ] Análise preditiva (machine learning)

### V2.0 (Novembro 2026)
- [ ] Dashboard web interativo
- [ ] Histórico multissafra (comparações)
- [ ] Leaderboard anônimo de precisão

---

## 🛠️ Desenvolvimento

### Clonar e Configurar

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/safra-2026.git
cd safra-2026

# Configure seu ambiente local
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate no Windows
pip install -r requirements_safra.txt  # opcional

# Teste o sistema
python safra_2026_tracking.py init
python safra_2026_tracking.py log 125
```

### Contribuir

1. **Fork** o repositório
2. **Crie branch** para sua feature: `git checkout -b feature/minha-feature`
3. **Commit** suas mudanças: `git commit -m '🌾 Add: minha feature'`
4. **Push** para a branch: `git push origin feature/minha-feature`
5. **Abra Pull Request**

Veja [`CONTRIBUTING.md`](CONTRIBUTING.md) para mais detalhes.

---

## 📄 Licença

Este projeto está licenciado sob a **MIT License** - veja [`LICENSE`](LICENSE) para detalhes.

---

## 📞 Suporte

### Problemas?

1. **Verificar logs:** `cat safra_2026_projeto/logs/$(date +%Y%m%d).log`
2. **Ver config:** `cat safra_2026_projeto/config.json`
3. **Consultar docs:** Ver `CLAUDE_CODE_SETUP.md`

### Perguntas?

- 💬 Abra uma [Issue](https://github.com/seu-usuario/safra-2026/issues)
- 💡 Sugira ideias em [Discussions](https://github.com/seu-usuario/safra-2026/discussions)
- 📧 Entre em contato: [seu-email@example.com](mailto:seu-email@example.com)

---

## 📊 Status do Projeto

```
[████████████████████████░░░░░] 85% Completo

✅ Core functionality
✅ CLI interface
✅ Data persistence
✅ Scenario detection
✅ Hedge recommendations
⏳ Web dashboard (V1.2)
⏳ ML predictions (V1.2)
⏳ Multi-year history (V2.0)
```

---

## 🙏 Agradecimentos

- **IFAG** - Custos reais 2025/26
- **CONAB/CEAPA** - Cenários oficiais 2026/27
- **IMEA** - Projeções oferta/demanda
- **Claude (Anthropic)** - Desenvolvimento do sistema

---

## 👤 Autor

**Daniel Schmitt**  
📍 Luziânia, Goiás, Brasil  
🌐 [LinkedIn](#) | 💻 [GitHub](https://github.com/seu-usuario)

---

## 📅 Changelog

### [1.0] - 2026-08-12

**Adicionado:**
- Sistema de rastreamento diário completo
- 3 cenários (pessimista/base/otimista)
- Detecção automática de cenários
- Recomendações de hedge
- CLI com 6 comandos
- Dados IFAG 2025/26 integrados
- Histórico auditável (JSONL)

**Planejado para V1.1:**
- Gráficos automáticos
- Exportação Excel
- Notificações

---

## 🌾 Visão

**Transformar dados em precisão. Transformar precisão em lucro.**

Este projeto prova que decisões agrícolas baseadas em dados + análise contínua + gestão de risco = sucesso.

Para 2026/27: **R$ 300k-976k** protegidos. Para o futuro: **benchmarks de precisão** que elevam toda a comunidade agrícola.

---

<div align="center">

**🌾 [Clone Agora](https://github.com/seu-usuario/safra-2026) | [Leia a Docs](CLAUDE_CODE_QUICK_GUIDE.md) | [Abra uma Issue](https://github.com/seu-usuario/safra-2026/issues)** 🌾

**Made with ❤️ in Luziânia, GO**

</div>
