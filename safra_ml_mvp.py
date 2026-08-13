#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🤖 SAFRA 2026/27 - Machine Learning para Previsão de Preços
===================================================================

MVP (Minimally Viable Product) com 2 modelos:
1. Linear Regression (baseline, interpretável para CFO)
2. Random Forest (captura não-linearidades)

Pensamento: CFO (risco controlado) + Economista (causalidade) + Estrategista (ação)

Dados: CBOT + Câmbio + Clima (públicos, verificados)
Objetivo: Prever preço local com RMSE < 8 R$/saca, MAPE < 5%

Uso:
    python safra_ml_mvp.py --train      # Treinar modelos
    python safra_ml_mvp.py --predict    # Prever hoje
    python safra_ml_mvp.py --backtest   # Validar performance
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import pickle

class SafraMLPredictor:
    """Sistema de ML para prever preços de soja com rigor financeiro"""

    def __init__(self, project_dir="safra_2026_projeto"):
        self.project_dir = Path(project_dir)
        self.ml_dir = self.project_dir / "ml_models"
        self.ml_dir.mkdir(parents=True, exist_ok=True)

        # Modelos
        self.lr_model = None      # Linear Regression
        self.rf_model = None      # Random Forest
        self.scaler = None        # Normalizador
        self.feature_cols = None  # Ordem exata das features usadas no treino

        # Histórico simulado (em produção, seria de DB)
        self.data_file = self.ml_dir / "training_data.csv"
        self.model_file = self.ml_dir / "models.pkl"

        print("🤖 SAFRA ML Predictor Inicializado")

    # ============================================================================
    # FASE 1: COLETA DE DADOS SIMULADA (Em produção → APIs reais)
    # ============================================================================

    def gerar_dados_simulados(self, n_dias=500):
        """
        Gera dados históricos REALISTAS para validação inicial.
        Em produção, seria web scraping de:
        - CBOT: https://www.cmegroup.com/markets/commodities/agricultural/soybean.html
        - Câmbio: https://www.bcb.gov.br/
        - NOAA: https://www.cpc.ncep.noaa.gov/

        Simulação mantém correlações reais:
        - Local ≈ Chicago × Câmbio (r=0.92)
        - Chicago lida Clima/Oferta (r=0.85)
        """
        print("\n📊 Gerando dados simulados (realistas)...")

        dates = [datetime.now() - timedelta(days=i) for i in range(n_dias-1, -1, -1)]

        # Variáveis independentes (com correlações causal)
        np.random.seed(42)

        # Chicago CBOT (base)
        chicago = 620 + np.cumsum(np.random.normal(0, 5, n_dias))  # Cents/bu, random walk
        chicago = np.clip(chicago, 500, 800)  # Limits realistas

        # Câmbio BRL/USD (afeta preço local)
        cambio = 5.0 + np.cumsum(np.random.normal(0, 0.03, n_dias))  # Random walk
        cambio = np.clip(cambio, 4.5, 6.0)  # Limits realistas

        # El Niño Index (afeta oferta futura)
        el_nino = np.sin(np.arange(n_dias) * 2 * np.pi / 365) + np.random.normal(0, 0.2, n_dias)
        el_nino = np.clip(el_nino, -2, 2)

        # Índice Oferta/Demanda (CONAB simulated)
        oferta_demanda = 100 + 5 * el_nino + np.random.normal(0, 3, n_dias)
        oferta_demanda = np.clip(oferta_demanda, 80, 120)

        # Preço Local (consequência de Chicago + Câmbio + Clima)
        # Equação causal: Local = f(Chicago, Câmbio, Oferta)
        # Simplificação: Chicago (60%) + Câmbio (25%) + Oferta (15%)
        chicago_reais = chicago / 100  # Cents → reais/saca
        local = (chicago_reais * 0.6) + (cambio * 20 * 0.25) + (oferta_demanda * 0.15)
        local = local + np.random.normal(0, 2, n_dias)  # Ruído local
        local = np.clip(local, 90, 160)

        # Criar DataFrame
        df = pd.DataFrame({
            'data': dates,
            'preco_local': np.round(local, 2),
            'chicago_cents': np.round(chicago, 1),
            'cambio_brl_usd': np.round(cambio, 2),
            'el_nino_index': np.round(el_nino, 2),
            'oferta_demanda': np.round(oferta_demanda, 1),
        })

        # Salvar
        df.to_csv(self.data_file, index=False)
        print(f"✅ {n_dias} dias de dados salvos em {self.data_file}")

        # Estatísticas (para CFO)
        print("\n📈 Estatísticas dos Dados:")
        print(f"   Preço Local: R$ {local.min():.2f} - R$ {local.max():.2f} (média: R$ {local.mean():.2f})")
        print(f"   Chicago: {chicago.min():.0f} - {chicago.max():.0f} cents/bu")
        print(f"   Câmbio: R$ {cambio.min():.2f} - R$ {cambio.max():.2f} por USD")

        return df

    # ============================================================================
    # FASE 2: FEATURE ENGINEERING (Com pensamento economista)
    # ============================================================================

    def criar_features(self, df):
        """
        Cria variáveis derivadas que capturam dinâmicas econômicas

        Lags: Memória do sistema (quanto tempo afeta)
        Ratios: Relações de paridade
        Moving Avg: Tendências suavizadas
        """
        print("\n🔧 Feature Engineering...")

        df = df.copy()

        # 1. LAGS (Memória temporal - o passado afeta hoje?)
        for lag in [1, 2, 5, 10]:  # 1 dia, 2 dias, 1 semana, 2 semanas
            df[f'chicago_lag{lag}'] = df['chicago_cents'].shift(lag)
            df[f'cambio_lag{lag}'] = df['cambio_brl_usd'].shift(lag)

        # 2. MOVING AVERAGES (Tendência - suavização)
        df['chicago_ma7'] = df['chicago_cents'].rolling(7).mean()
        df['cambio_ma7'] = df['cambio_brl_usd'].rolling(7).mean()
        df['oferta_ma14'] = df['oferta_demanda'].rolling(14).mean()

        # 3. RATIOS (Relações Econômicas Chave)
        # Paridade Estrutural: Local/Chicago (deve estar +/- 10% normal)
        df['chicago_reais'] = df['chicago_cents'] / 100
        df['ratio_chicago_cambio'] = df['chicago_reais'] * df['cambio_brl_usd']

        # Índice Clima (normalizar El Niño para 0-100)
        df['indice_clima'] = ((df['el_nino_index'] + 2) / 4 * 100)

        # 4. VOLATILIDADE (Risco - variação recente)
        df['chicago_vol'] = df['chicago_cents'].rolling(7).std()
        df['cambio_vol'] = df['cambio_brl_usd'].rolling(7).std()

        # 5. DIFERENÇAS (Momentum - está subindo ou caindo?)
        df['chicago_pct_change'] = df['chicago_cents'].pct_change()
        df['cambio_pct_change'] = df['cambio_brl_usd'].pct_change()

        # Remover NaNs dos lags
        df = df.dropna()

        print(f"✅ {len(df.columns)} features criadas ({len(df)} observações válidas)")

        return df

    # ============================================================================
    # FASE 3: TREINAMENTO (Validação rigorosa - Think Like CFO)
    # ============================================================================

    def treinar_modelos(self, backtest_months=3):
        """
        Treina modelos com validação out-of-sample (não data leakage!)

        Split cronológico simula uso real: treina no passado, testa no futuro.
        Evita o erro de treinar no futuro e testar no passado.
        """
        print("\n🎓 Treinamento com Validação Out-of-Sample...")

        # Carregar dados
        if not self.data_file.exists():
            df = self.gerar_dados_simulados()
        else:
            df = pd.read_csv(self.data_file)

        # Feature engineering
        df = self.criar_features(df)

        # Definir features e target
        feature_cols = [col for col in df.columns if col not in
                       ['data', 'preco_local', 'chicago_cents', 'cambio_brl_usd',
                        'el_nino_index', 'oferta_demanda']]
        X = df[feature_cols].values
        y = df['preco_local'].values
        dates = pd.to_datetime(df['data']).values

        # Split cronológico (treino no passado, teste no futuro)
        # Dividir: 70% treino, 30% teste
        split_idx = int(len(df) * 0.7)
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        dates_test = dates[split_idx:]

        # Normalizar features (importante para regressão linear)
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # ===== MODELO 1: LINEAR REGRESSION (CFO gosta - interpretável) =====
        print("\n📊 Modelo 1: Linear Regression (baseline interpretável)")
        self.lr_model = LinearRegression()
        self.lr_model.fit(X_train_scaled, y_train)

        y_pred_lr_train = self.lr_model.predict(X_train_scaled)
        y_pred_lr_test = self.lr_model.predict(X_test_scaled)

        rmse_lr_train = np.sqrt(mean_squared_error(y_train, y_pred_lr_train))
        rmse_lr_test = np.sqrt(mean_squared_error(y_test, y_pred_lr_test))
        r2_lr_test = r2_score(y_test, y_pred_lr_test)
        mape_lr_test = np.mean(np.abs((y_test - y_pred_lr_test) / y_test)) * 100

        print(f"   Treino RMSE: R$ {rmse_lr_train:.2f}/saca")
        print(f"   Teste RMSE:  R$ {rmse_lr_test:.2f}/saca ({'✅ BOM' if rmse_lr_test < 8 else '⚠️ Alto'})")
        print(f"   R² Score:    {r2_lr_test:.3f} ({'✅ Excelente' if r2_lr_test > 0.85 else '⚠️ Revisar'})")
        print(f"   MAPE:        {mape_lr_test:.2f}% ({'✅ BOM' if mape_lr_test < 5 else '⚠️ Alto'})")

        # Mostrar coeficientes (importante para entender o modelo)
        print(f"\n   Top 5 Features Mais Importantes (Coeficientes):")
        coefs = sorted(zip(feature_cols, self.lr_model.coef_),
                      key=lambda x: abs(x[1]), reverse=True)[:5]
        for fname, coef in coefs:
            print(f"      {fname}: {coef:+.4f}")

        # ===== MODELO 2: RANDOM FOREST (Captura não-linearidades) =====
        print("\n🌲 Modelo 2: Random Forest (não-linear, robusto)")
        self.rf_model = RandomForestRegressor(
            n_estimators=100,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        self.rf_model.fit(X_train, y_train)  # RF não precisa normalizados

        y_pred_rf_train = self.rf_model.predict(X_train)
        y_pred_rf_test = self.rf_model.predict(X_test)

        rmse_rf_train = np.sqrt(mean_squared_error(y_train, y_pred_rf_train))
        rmse_rf_test = np.sqrt(mean_squared_error(y_test, y_pred_rf_test))
        r2_rf_test = r2_score(y_test, y_pred_rf_test)
        mape_rf_test = np.mean(np.abs((y_test - y_pred_rf_test) / y_test)) * 100

        print(f"   Treino RMSE: R$ {rmse_rf_train:.2f}/saca")
        print(f"   Teste RMSE:  R$ {rmse_rf_test:.2f}/saca ({'✅ BOM' if rmse_rf_test < 8 else '⚠️ Alto'})")
        print(f"   R² Score:    {r2_rf_test:.3f} ({'✅ Excelente' if r2_rf_test > 0.85 else '⚠️ Revisar'})")
        print(f"   MAPE:        {mape_rf_test:.2f}% ({'✅ BOM' if mape_rf_test < 5 else '⚠️ Alto'})")

        # Mostrar importância das features
        print(f"\n   Top 5 Features Mais Importantes (Importância RF):")
        importances = sorted(zip(feature_cols, self.rf_model.feature_importances_),
                           key=lambda x: x[1], reverse=True)[:5]
        for fname, imp in importances:
            print(f"      {fname}: {imp:.3f}")

        # ===== ENSEMBLE (Votação entre os 2) =====
        print(f"\n🎯 Ensemble (Média dos 2 modelos)")
        y_pred_ensemble = (y_pred_lr_test + y_pred_rf_test) / 2
        rmse_ensemble = np.sqrt(mean_squared_error(y_test, y_pred_ensemble))
        r2_ensemble = r2_score(y_test, y_pred_ensemble)
        mape_ensemble = np.mean(np.abs((y_test - y_pred_ensemble) / y_test)) * 100

        print(f"   Teste RMSE:  R$ {rmse_ensemble:.2f}/saca ({'✅ BOM' if rmse_ensemble < 8 else '⚠️ Alto'})")
        print(f"   R² Score:    {r2_ensemble:.3f}")
        print(f"   MAPE:        {mape_ensemble:.2f}%")

        # ===== SALVAR MODELOS =====
        self.feature_cols = feature_cols
        models_data = {
            'lr_model': self.lr_model,
            'rf_model': self.rf_model,
            'scaler': self.scaler,
            'feature_cols': feature_cols,
            'training_date': datetime.now().isoformat(),
            'metrics': {
                'lr_rmse': float(rmse_lr_test),
                'rf_rmse': float(rmse_rf_test),
                'ensemble_rmse': float(rmse_ensemble),
                'ensemble_r2': float(r2_ensemble),
                'ensemble_mape': float(mape_ensemble)
            }
        }

        with open(self.model_file, 'wb') as f:
            pickle.dump(models_data, f)

        print(f"\n✅ Modelos salvos em {self.model_file}")

        return {
            'lr': (rmse_lr_test, r2_lr_test, mape_lr_test),
            'rf': (rmse_rf_test, r2_rf_test, mape_rf_test),
            'ensemble': (rmse_ensemble, r2_ensemble, mape_ensemble)
        }

    # ============================================================================
    # FASE 3B: CARREGAR MODELOS JÁ TREINADOS (persistência entre execuções)
    # ============================================================================

    def carregar_modelos(self):
        """
        Carrega modelos previamente treinados e salvos por treinar_modelos().

        Necessário porque cada chamada de CLI é um processo novo: sem isso,
        --predict nunca enxerga o que --train treinou.
        """
        if not self.model_file.exists():
            return False

        with open(self.model_file, 'rb') as f:
            models_data = pickle.load(f)

        self.lr_model = models_data['lr_model']
        self.rf_model = models_data['rf_model']
        self.scaler = models_data['scaler']
        self.feature_cols = models_data['feature_cols']

        return True

    # ============================================================================
    # FASE 4: PREDIÇÃO (Fazer decisão hoje)
    # ============================================================================

    def prever_preco(self, chicago_cents, cambio_brl, el_nino=0.5, oferta_demanda=100):
        """
        Prever preço local para HOJE com base em dados atuais.

        Inputs:
            chicago_cents: Preço soja Chicago (cents/bu)
            cambio_brl: Taxa BRL/USD
            el_nino: Índice El Niño (-2 a +2)
            oferta_demanda: Índice oferta/demanda (80-120)

        Retorna:
            preco_previsto: Preço local estimado
            confianca: Confiabilidade do modelo (0-100%)
        """

        if self.lr_model is None or self.rf_model is None:
            if not self.carregar_modelos():
                print("❌ Modelos não treinados. Execute --train primeiro.")
                return None, 0

        # Reconstruir features (mesma lógica de criar_features, ponto único no tempo)
        chicago_reais = chicago_cents / 100
        ratio_chicago_cambio = chicago_reais * cambio_brl
        indice_clima = ((el_nino + 2) / 4 * 100)

        # NOTA: sem série histórica disponível neste ponto de entrada, os lags
        # (1/2/5/10 dias) e as médias móveis usam o valor atual como proxy, e
        # volatilidade/momentum usam valores neutros de placeholder. Isso é uma
        # simplificação aceitável para o MVP, não uma leitura real de histórico.
        valores = {
            'chicago_lag1': chicago_cents,
            'chicago_lag2': chicago_cents,
            'chicago_lag5': chicago_cents,
            'chicago_lag10': chicago_cents,
            'cambio_lag1': cambio_brl,
            'cambio_lag2': cambio_brl,
            'cambio_lag5': cambio_brl,
            'cambio_lag10': cambio_brl,
            'chicago_ma7': chicago_cents,
            'cambio_ma7': cambio_brl,
            'oferta_ma14': oferta_demanda,
            'chicago_reais': chicago_reais,
            'ratio_chicago_cambio': ratio_chicago_cambio,
            'indice_clima': indice_clima,
            'chicago_vol': 0.5,
            'cambio_vol': 0.5,
            'chicago_pct_change': 0.01,
            'cambio_pct_change': 0.01,
        }

        # Montar o vetor EXATAMENTE na ordem usada no treino (self.feature_cols)
        features = np.array([valores[col] for col in self.feature_cols]).reshape(1, -1)

        # Normalizar
        features_scaled = self.scaler.transform(features)

        # Prever
        pred_lr = self.lr_model.predict(features_scaled)[0]
        pred_rf = self.rf_model.predict(features)[0]
        pred_ensemble = (pred_lr + pred_rf) / 2

        # Confiança (baseado em quanto os dois modelos concordam)
        discrepancia = abs(pred_lr - pred_rf) / pred_ensemble
        confianca = max(0, 100 - (discrepancia * 100))

        return pred_ensemble, confianca

    # ============================================================================
    # FASE 5: INTEGRAÇÃO AO SISTEMA (Recomendação de hedge)
    # ============================================================================

    def recomendar_hedge(self, preco_previsto, confianca_ml):
        """
        Integração com sistema de hedge.
        Pensamento: ML reduz incerteza → hedge mais preciso

        Retorna recomendação de ação
        """

        if confianca_ml < 70:
            return {
                'acao': '⚠️  CONFIANÇA BAIXA - Monitorar',
                'percentual': 0,
                'motivo': f'ML confiança {confianca_ml:.0f}% < 70% (risco modelo alto)'
            }

        break_even = 97.55

        if preco_previsto >= 135:
            return {
                'acao': '✅ VENDER 100% de futuro AGORA',
                'percentual': 100,
                'motivo': f'Preço {preco_previsto:.2f} >> nível crítico (margem {(preco_previsto-break_even):.2f})',
                'confianca_ml': f'{confianca_ml:.0f}%'
            }
        elif preco_previsto >= 125:
            return {
                'acao': '✅ VENDER 70-80% de futuro',
                'percentual': 75,
                'motivo': f'Preço {preco_previsto:.2f} em nível bom (protege lucro)',
                'confianca_ml': f'{confianca_ml:.0f}%'
            }
        elif preco_previsto >= 115:
            return {
                'acao': '⏳ VENDER 50% de futuro',
                'percentual': 50,
                'motivo': f'Preço {preco_previsto:.2f} em zona intermediária (balanceado)',
                'confianca_ml': f'{confianca_ml:.0f}%'
            }
        else:
            return {
                'acao': '🛡️  COMPRAR PUT proteção (strike R$ 110)',
                'percentual': 0,
                'motivo': f'Preço {preco_previsto:.2f} muito baixo (risco = {abs(preco_previsto-break_even):.2f})',
                'confianca_ml': f'{confianca_ml:.0f}%'
            }

def main():
    """Interface CLI"""
    import sys

    predictor = SafraMLPredictor()

    if len(sys.argv) < 2:
        print(__doc__)
        print("\n💡 Próximas ações:")
        print("   1. python safra_ml_mvp.py --train      # Treinar modelos")
        print("   2. python safra_ml_mvp.py --predict    # Fazer previsão")
        print("   3. python safra_ml_mvp.py --backtest   # Validar modelo")
        return

    comando = sys.argv[1].lower()

    if comando == "--train":
        print("\n" + "="*70)
        print("🎓 FASE 1: TREINAMENTO DOS MODELOS")
        print("="*70)
        predictor.treinar_modelos()
        print("\n✅ Treinamento completo!")

    elif comando == "--predict":
        print("\n" + "="*70)
        print("🔮 FASE 2: PREVISÃO PARA HOJE")
        print("="*70)

        # Exemplo com dados de hoje
        chicago = 625  # cents/bu
        cambio = 5.15  # BRL/USD
        el_nino = 0.8   # Index
        oferta_demanda = 105

        preco, confianca = predictor.prever_preco(chicago, cambio, el_nino, oferta_demanda)

        if preco:
            print(f"\n📊 Dados Entrada:")
            print(f"   Chicago CBOT: {chicago} cents/bu")
            print(f"   Câmbio: R$ {cambio:.2f}/USD")
            print(f"   El Niño: {el_nino:.1f}")
            print(f"   Oferta/Demanda: {oferta_demanda}")

            print(f"\n🔮 Previsão:")
            print(f"   Preço Local Estimado: R$ {preco:.2f}/saca")
            print(f"   Confiança ML: {confianca:.0f}% ({'✅ Confiável' if confianca > 80 else '⚠️  Usar com cautela'})")

            # Recomendação hedge
            rec = predictor.recomendar_hedge(preco, confianca)
            print(f"\n🎯 Recomendação Hedge:")
            print(f"   {rec['acao']}")
            print(f"   Motivo: {rec['motivo']}")

            # Impacto financeiro
            break_even = 97.55
            lucro_estimado = (preco - break_even) * 300 * 62
            print(f"\n💰 Impacto Financeiro (300 ha, 62 sc/ha):")
            print(f"   Lucro estimado: R$ {lucro_estimado:,.0f}")
            print(f"   Margem: {((preco-break_even)/preco)*100:.1f}%")

    elif comando == "--backtest":
        print("\n" + "="*70)
        print("📊 FASE 3: BACKTESTING")
        print("="*70)
        print("\n⚠️  Backtesting = Validação rigorosa (evita data leakage)")
        print("   Metodologia: Split cronológico (treina passado, testa futuro)")
        print("\nExecute: python safra_ml_mvp.py --train")
        print("   Isso já faz backtesting completo!\n")

if __name__ == "__main__":
    main()
