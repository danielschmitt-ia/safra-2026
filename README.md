# 🌾 SAFRA 2026/27

Acompanhamento diário de preços da soja e apoio à decisão de hedge para a safra 2026/27, com histórico versionado e recomendações automáticas baseadas em cenários de mercado (CONAB/CEPEA) e nos custos de produção (dados IFAG 2025/26).

## Como funciona

O sistema classifica cada preço registrado em um de três cenários e recomenda uma ação de hedge:

| Cenário | Faixa (R$/saca) | Probabilidade | Ação sugerida |
|---|---|---|---|
| 🔴 Pessimista | 100 – 110 | ~32% | Comprar PUT de proteção |
| 🟢 Base | 122 – 128 | ~53% | Vender 70–80% via futuro |
| ⭐ Otimista | 145 – 155 | ~15% | Manter posição aberta |

O break-even é calculado a partir dos custos de produção por hectare (defensivos, fertilizantes, sementes, mão de obra, operações, frete, seguro/juros, tributos, depreciação) divididos pela produtividade esperada.

## Uso rápido

Requer apenas Python 3.7+ (sem dependências externas).

```bash
python3 safra_2026_tracking.py init                              # inicializa o projeto
python3 safra_2026_tracking.py log <preço> [produtividade] [notas]  # registra o preço do dia
python3 safra_2026_tracking.py status                            # mostra status atual e margem
python3 safra_2026_tracking.py compare                           # compara previsão vs. realidade
python3 safra_2026_tracking.py export                            # gera relatório
python3 safra_2026_tracking.py version                           # versão do sistema
```

Exemplo:

```bash
python3 safra_2026_tracking.py log 125.50 62 "Fechamento Chicago"
```

Os dados são salvos localmente em `safra_2026_projeto/` (config, histórico em JSONL e logs diários) — nada é enviado a serviços externos, e esse diretório fica fora do controle de versão (veja `.gitignore`).

## Estrutura do repositório

| Arquivo | Descrição |
|---|---|
| `safra_2026_tracking.py` | Sistema principal de rastreamento e recomendação (CLI) |
| `PROJETO_CLAUDE_CODE_README.md` | Visão geral detalhada do projeto e casos de uso |
| `CLAUDE_CODE_QUICK_GUIDE.md` | Guia de início rápido |
| `GITHUB_SETUP_GUIDE.md` | Guia de configuração do repositório no GitHub |
| `CONTRIBUTING.md` | Como contribuir com o projeto |
| `LICENSE` | Licença MIT |

## Em desenvolvimento

Um MVP de Machine Learning (previsão de preço via Chicago/CBOT + câmbio + clima), um coletor automático de dados de mercado e monitoramento multi-commodity estão em revisão no PR [#1](https://github.com/danielschmitt-ia/safra-2026/pull/1).

## Licença

MIT — veja [LICENSE](LICENSE).
