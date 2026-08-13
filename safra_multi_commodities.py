#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🌾 SAFRA 2026/27 - Monitoramento Multi-Commodity
===================================================================

Acompanha preço e (quando há histórico suficiente) previsão de ML para
várias culturas além da soja: milho, trigo, arroz, aveia, algodão,
canola, cana-de-açúcar (via proxy açúcar) e feijão.

⚠️ LIMITAÇÕES IMPORTANTES (leia antes de usar)

1. SEM PREÇO LOCAL EM R$: ao contrário do safra_ml_mvp.py (soja), este
   módulo NÃO prevê preço local em R$/saca. Não há acesso, neste
   ambiente, a uma fonte de preço local confiável (CEPEA/ESALQ está
   bloqueado pela política de rede daqui). O que é coletado e previsto
   é o preço do CONTRATO FUTURO INTERNACIONAL (CBOT/ICE) na unidade
   nativa dele — cents/bushel, cents/lb, USD/cwt ou CAD/tonelada,
   dependendo da commodity. Ver COMMODITIES abaixo para a unidade de
   cada uma.

2. SEM CONVERSÃO DE UNIDADE: bushel tem peso diferente por grão (soja
   60lb, milho 56lb, aveia 32lb, trigo 60lb), e algodão/açúcar são
   cents/lb, arroz USD/cwt, canola CAD/tonelada. Converter tudo para
   R$/saca exigiria fatores específicos por commodity que não foram
   validados aqui — por isso os valores ficam crus, na unidade nativa,
   com o rótulo de unidade sempre visível.

3. SEM HEDGE/MARGEM: este módulo não calcula recomendação de venda ou
   margem (isso existe só para soja, em safra_ml_mvp.py, calibrado com
   break-even próprio). Aqui é acompanhamento de mercado.

4. FEIJÃO NÃO TEM COLETA AUTOMÁTICA: não existe contrato futuro
   internacional líquido para feijão comum. Preço precisa ser
   registrado manualmente com --log.

5. Rede bloqueada neste ambiente de desenvolvimento (mesma limitação
   do safra_data_collector.py) — rode --test-conexoes localmente antes
   de confiar em --collect.

Uso:
    python safra_multi_commodities.py --collect                # coleta futuros + câmbio
    python safra_multi_commodities.py --log milho 620.5         # registro manual
    python safra_multi_commodities.py --status                  # resumo de preços
    python safra_multi_commodities.py --train milho             # treina modelo (ou "todas")
    python safra_multi_commodities.py --predict milho           # previsão + confiança
    python safra_multi_commodities.py --test-conexoes           # diagnóstico de rede
"""

import sqlite3
import sys
from datetime import datetime, date
from pathlib import Path

import numpy as np
import pandas as pd
import pickle

from safra_data_collector import SafraDataCollector

# Ticker=None => sem futuro internacional líquido, só entrada manual (--log)
COMMODITIES = {
    "soja":        {"nome": "Soja",              "ticker": "ZS=F", "unidade": "cents/bushel", "fonte": "CBOT"},
    "milho":       {"nome": "Milho",              "ticker": "ZC=F", "unidade": "cents/bushel", "fonte": "CBOT"},
    "trigo":       {"nome": "Trigo",              "ticker": "ZW=F", "unidade": "cents/bushel", "fonte": "CBOT"},
    "aveia":       {"nome": "Aveia",              "ticker": "ZO=F", "unidade": "cents/bushel", "fonte": "CBOT"},
    "arroz":       {"nome": "Arroz",              "ticker": "ZR=F", "unidade": "USD/cwt",      "fonte": "CBOT"},
    "algodao":     {"nome": "Algodão",            "ticker": "CT=F", "unidade": "cents/lb",     "fonte": "ICE"},
    "canola":      {"nome": "Canola",             "ticker": "RS=F", "unidade": "CAD/tonelada", "fonte": "ICE Canada"},
    "cana_acucar": {"nome": "Cana-de-açúcar (proxy: Açúcar #11)", "ticker": "SB=F", "unidade": "cents/lb", "fonte": "ICE"},
    "feijao":      {"nome": "Feijão",             "ticker": None,   "unidade": "R$/saca 60kg", "fonte": "manual"},
}


class SafraMultiCollector:
    """Coleta e acompanha preços de várias commodities"""

    def __init__(self, project_dir="safra_2026_projeto"):
        self.project_dir = Path(project_dir)
        self.data_dir = self.project_dir / "dados"
        self.ml_dir = self.project_dir / "ml_models"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.ml_dir.mkdir(parents=True, exist_ok=True)

        # Reaproveita a coleta de câmbio já validada em safra_data_collector.py,
        # e usa o MESMO banco (safra_mercado.db) para que a tabela 'cambio'
        # fique visível às consultas do SafraMultiML abaixo.
        self._base_collector = SafraDataCollector(project_dir=str(self.project_dir))
        self.db_path = self._base_collector.db_path
        self._setup_db()

        print("🌾 SAFRA Multi-Commodity Inicializado")

    def _setup_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS precos_futuros (
                commodity TEXT,
                data DATE,
                preco FLOAT,
                unidade TEXT,
                fonte TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (commodity, data)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS precos_manuais (
                commodity TEXT,
                data DATE,
                preco FLOAT,
                unidade TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (commodity, data)
            )
        """)
        conn.commit()
        conn.close()

    # ============================================================================
    # COLETA
    # ============================================================================

    def fetch_futuro(self, commodity_key, years=5):
        """Busca histórico do contrato futuro de uma commodity via yfinance.

        Retorna preço BRUTO, na unidade nativa do contrato (ver COMMODITIES)
        — nenhuma conversão de unidade é aplicada.
        """
        info = COMMODITIES.get(commodity_key)
        if info is None:
            print(f"❌ Commodity desconhecida: {commodity_key}")
            return None
        if info["ticker"] is None:
            print(f"⚠️  {info['nome']}: sem futuro internacional, use --log")
            return None

        try:
            import yfinance as yf
        except ImportError:
            print("❌ yfinance não instalado. Rode: pip install yfinance")
            return None

        try:
            print(f"📊 Buscando {info['nome']} ({info['ticker']})...")
            data = yf.download(info["ticker"], period=f"{years}y", progress=False)

            if data is None or data.empty:
                print(f"❌ {info['nome']}: resposta vazia")
                return None

            if isinstance(data.columns, pd.MultiIndex):
                close = data["Close"].iloc[:, 0]
            else:
                close = data["Close"]

            df = pd.DataFrame({
                "data": pd.to_datetime(data.index).date,
                "preco": close.values,
            })
            return df.dropna()
        except Exception as e:
            print(f"❌ Erro {info['nome']}: {e}")
            return None

    def validate_data(self, df, nome):
        if df is None or df.empty:
            print(f"⚠️  {nome}: sem dados para validar")
            return False
        nulos = df.isnull().sum().sum()
        duplicatas = df.duplicated(subset="data").sum()
        print(f"✔️  {nome}: {len(df)} registros | nulos={nulos} | duplicatas={duplicatas} "
              f"| {df['data'].min()} → {df['data'].max()}")
        return True

    def _salvar_futuro(self, commodity_key, df):
        if df is None or df.empty:
            return 0
        info = COMMODITIES[commodity_key]
        conn = sqlite3.connect(self.db_path)
        rows = [
            (commodity_key, str(row.data), float(row.preco), info["unidade"], info["fonte"])
            for row in df.itertuples(index=False)
        ]
        conn.executemany(
            "INSERT OR REPLACE INTO precos_futuros (commodity, data, preco, unidade, fonte) "
            "VALUES (?, ?, ?, ?, ?)",
            rows,
        )
        conn.commit()
        conn.close()
        return len(rows)

    def collect_all(self, years=5):
        """Coleta todas as commodities com ticker configurado + câmbio (compartilhado)"""
        print("\n" + "=" * 70)
        print("🚀 COLETA MULTI-COMMODITY")
        print("=" * 70)

        cambio = self._base_collector.fetch_cambio_historical(years=years)
        self._base_collector.validate_data(cambio, "Câmbio")
        self._base_collector._salvar("cambio", cambio)

        totais = {}
        for key, info in COMMODITIES.items():
            if info["ticker"] is None:
                continue
            df = self.fetch_futuro(key, years=years)
            self.validate_data(df, info["nome"])
            totais[key] = self._salvar_futuro(key, df)

        print("\n📋 Resumo da coleta:")
        for key, n in totais.items():
            status = "✅" if n > 0 else "❌"
            print(f"   {status} {COMMODITIES[key]['nome']}: {n} registros")

        if all(n == 0 for n in totais.values()):
            print("\n⚠️  Nenhuma fonte retornou dados. Rode --test-conexoes para diagnosticar.")

    def log_manual(self, commodity_key, preco, data_str=None):
        """Registra preço manualmente (essencial para feijão, opcional para as demais)"""
        if commodity_key not in COMMODITIES:
            print(f"❌ Commodity desconhecida: {commodity_key}")
            print(f"   Opções: {', '.join(COMMODITIES.keys())}")
            return False

        info = COMMODITIES[commodity_key]
        data_str = data_str or date.today().isoformat()

        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "INSERT OR REPLACE INTO precos_manuais (commodity, data, preco, unidade) VALUES (?, ?, ?, ?)",
            (commodity_key, data_str, float(preco), info["unidade"]),
        )
        conn.commit()
        conn.close()
        print(f"✅ {info['nome']}: {preco} {info['unidade']} registrado em {data_str}")
        return True

    def status(self):
        """Resumo: último preço e variação de cada commodity acompanhada"""
        if not self.db_path.exists():
            print("📭 Nenhum dado ainda. Rode --collect ou --log primeiro.")
            return

        conn = sqlite3.connect(self.db_path)
        print("\n" + "=" * 70)
        print("📊 STATUS MULTI-COMMODITY")
        print("=" * 70)

        for key, info in COMMODITIES.items():
            fontes = []
            cur = conn.execute(
                "SELECT data, preco FROM precos_futuros WHERE commodity = ? ORDER BY data DESC LIMIT 2",
                (key,),
            )
            futuros = cur.fetchall()
            cur = conn.execute(
                "SELECT data, preco FROM precos_manuais WHERE commodity = ? ORDER BY data DESC LIMIT 2",
                (key,),
            )
            manuais = cur.fetchall()

            pontos = sorted(list(futuros) + list(manuais), key=lambda r: r[0], reverse=True)

            if not pontos:
                print(f"   {info['nome']}: sem dados")
                continue

            ultimo_data, ultimo_preco = pontos[0]
            linha = f"   {info['nome']}: {ultimo_preco:.2f} {info['unidade']} ({ultimo_data})"
            if len(pontos) > 1:
                anterior = pontos[1][1]
                variacao = ((ultimo_preco - anterior) / anterior) * 100 if anterior else 0
                seta = "↑" if variacao > 0 else ("↓" if variacao < 0 else "→")
                linha += f"  {seta} {variacao:+.2f}%"
            print(linha)

        conn.close()

    def testar_conexoes(self):
        print("\n" + "=" * 70)
        print("🔌 TESTE DE CONEXÕES (multi-commodity)")
        print("=" * 70)
        resultados = {}
        for key, info in COMMODITIES.items():
            if info["ticker"] is None:
                continue
            df = self.fetch_futuro(key, years=1)
            resultados[key] = self.validate_data(df, info["nome"])

        print("\n📋 Resumo:")
        for key, ok in resultados.items():
            print(f"   {COMMODITIES[key]['nome']}: {'✅ OK' if ok else '❌ FALHOU'}")
        return resultados


class SafraMultiML:
    """Previsão de ML do preço do CONTRATO FUTURO (não preço local) de uma commodity"""

    def __init__(self, commodity_key, project_dir="safra_2026_projeto"):
        if commodity_key not in COMMODITIES:
            raise ValueError(f"Commodity desconhecida: {commodity_key}")

        self.commodity_key = commodity_key
        self.info = COMMODITIES[commodity_key]
        self.project_dir = Path(project_dir)
        # Mesmo banco usado por SafraMultiCollector (compartilha a tabela 'cambio')
        self.db_path = self.project_dir / "dados" / "safra_mercado.db"
        self.ml_dir = self.project_dir / "ml_models"
        self.ml_dir.mkdir(parents=True, exist_ok=True)
        self.model_file = self.ml_dir / f"{commodity_key}_models.pkl"

        self.lr_model = None
        self.rf_model = None
        self.scaler = None
        self.feature_cols = None

    def _carregar_serie(self):
        """Carrega a série de preço (futuro se houver, senão manual) + câmbio"""
        if not self.db_path.exists():
            return None

        conn = sqlite3.connect(self.db_path)
        if self.info["ticker"] is not None:
            df = pd.read_sql(
                "SELECT data, preco FROM precos_futuros WHERE commodity = ? ORDER BY data",
                conn, params=(self.commodity_key,),
            )
        else:
            df = pd.read_sql(
                "SELECT data, preco FROM precos_manuais WHERE commodity = ? ORDER BY data",
                conn, params=(self.commodity_key,),
            )
        cambio = pd.read_sql("SELECT data, cambio_brl FROM cambio ORDER BY data", conn)
        conn.close()

        if df.empty:
            return None

        df["data"] = pd.to_datetime(df["data"])
        cambio["data"] = pd.to_datetime(cambio["data"])
        df = df.merge(cambio, on="data", how="left")
        df["cambio_brl"] = df["cambio_brl"].ffill()
        return df.dropna(subset=["preco"])

    def _criar_features(self, df):
        df = df.copy()
        for lag in [1, 2, 5, 10]:
            df[f"preco_lag{lag}"] = df["preco"].shift(lag)
            df[f"cambio_lag{lag}"] = df["cambio_brl"].shift(lag)
        df["preco_ma7"] = df["preco"].rolling(7).mean()
        df["cambio_ma7"] = df["cambio_brl"].rolling(7).mean()
        df["preco_vol7"] = df["preco"].rolling(7).std()
        df["cambio_vol7"] = df["cambio_brl"].rolling(7).std()
        df["preco_pct_change"] = df["preco"].pct_change()
        df["cambio_pct_change"] = df["cambio_brl"].pct_change()
        return df.dropna()

    def treinar(self):
        from sklearn.linear_model import LinearRegression
        from sklearn.ensemble import RandomForestRegressor
        from sklearn.preprocessing import StandardScaler
        from sklearn.metrics import mean_squared_error, r2_score

        print(f"\n🎓 Treinando modelo: {self.info['nome']} ({self.info['unidade']})")

        df = self._carregar_serie()
        if df is None or len(df) < 60:
            print(f"❌ Dados insuficientes para {self.info['nome']} "
                  f"(precisa de pelo menos ~60 pontos; use --collect ou --log)")
            return None

        df = self._criar_features(df)
        if len(df) < 20:
            print(f"❌ Após feature engineering, poucos pontos válidos para {self.info['nome']}")
            return None

        feature_cols = [c for c in df.columns if c not in ["data", "preco", "cambio_brl"]]
        X = df[feature_cols].values
        y = df["preco"].values

        split_idx = max(int(len(df) * 0.7), 1)
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]

        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)

        self.lr_model = LinearRegression()
        self.lr_model.fit(X_train_scaled, y_train)

        self.rf_model = RandomForestRegressor(n_estimators=100, max_depth=15, random_state=42, n_jobs=-1)
        self.rf_model.fit(X_train, y_train)

        metrics = {}
        if len(X_test) > 0:
            X_test_scaled = self.scaler.transform(X_test)
            pred_ensemble = (self.lr_model.predict(X_test_scaled) + self.rf_model.predict(X_test)) / 2
            rmse = np.sqrt(mean_squared_error(y_test, pred_ensemble))
            mape = np.mean(np.abs((y_test - pred_ensemble) / y_test)) * 100
            r2 = r2_score(y_test, pred_ensemble) if len(y_test) > 1 else float("nan")
            metrics = {"rmse": float(rmse), "mape": float(mape), "r2": float(r2)}
            print(f"   Teste RMSE: {rmse:.2f} {self.info['unidade']}")
            print(f"   Teste MAPE: {mape:.2f}%")
        else:
            print("   ⚠️  Poucos dados para separar conjunto de teste — só treino, sem validação")

        self.feature_cols = feature_cols
        with open(self.model_file, "wb") as f:
            pickle.dump({
                "lr_model": self.lr_model,
                "rf_model": self.rf_model,
                "scaler": self.scaler,
                "feature_cols": feature_cols,
                "metrics": metrics,
                "training_date": datetime.now().isoformat(),
            }, f)
        print(f"✅ Modelo salvo em {self.model_file}")
        return metrics

    def carregar_modelo(self):
        if not self.model_file.exists():
            return False
        with open(self.model_file, "rb") as f:
            models_data = pickle.load(f)
        self.lr_model = models_data["lr_model"]
        self.rf_model = models_data["rf_model"]
        self.scaler = models_data["scaler"]
        self.feature_cols = models_data["feature_cols"]
        return True

    def prever(self):
        """Prevê o próximo ponto de preço a partir do histórico mais recente salvo."""
        if self.lr_model is None or self.rf_model is None:
            if not self.carregar_modelo():
                print(f"❌ {self.info['nome']}: modelo não treinado. Rode --train {self.commodity_key}")
                return None, 0

        df = self._carregar_serie()
        if df is None or len(df) < 11:
            print(f"❌ {self.info['nome']}: histórico insuficiente para montar features de previsão")
            return None, 0

        df_feat = self._criar_features(df)
        if df_feat.empty:
            print(f"❌ {self.info['nome']}: sem linha válida após feature engineering")
            return None, 0

        ultima_linha = df_feat.iloc[[-1]]
        features = ultima_linha[self.feature_cols].values

        features_scaled = self.scaler.transform(features)
        pred_lr = self.lr_model.predict(features_scaled)[0]
        pred_rf = self.rf_model.predict(features)[0]
        pred_ensemble = (pred_lr + pred_rf) / 2

        discrepancia = abs(pred_lr - pred_rf) / pred_ensemble if pred_ensemble else 1
        confianca = max(0, 100 - (discrepancia * 100))

        return pred_ensemble, confianca


def _print_ajuda():
    print(__doc__)
    print("Commodities configuradas:")
    for key, info in COMMODITIES.items():
        fonte = info["fonte"] if info["ticker"] else "manual (--log)"
        print(f"   {key:12s} {info['nome']:35s} [{info['unidade']}] via {fonte}")


def main():
    collector = SafraMultiCollector()

    if len(sys.argv) < 2:
        _print_ajuda()
        return

    comando = sys.argv[1].lower()

    if comando == "--collect":
        collector.collect_all()
    elif comando == "--status":
        collector.status()
    elif comando == "--test-conexoes":
        collector.testar_conexoes()
    elif comando == "--log":
        if len(sys.argv) < 4:
            print("Uso: python safra_multi_commodities.py --log <commodity> <preco> [YYYY-MM-DD]")
            return
        commodity_key, preco = sys.argv[2], sys.argv[3]
        data_str = sys.argv[4] if len(sys.argv) > 4 else None
        collector.log_manual(commodity_key, float(preco), data_str)
    elif comando == "--train":
        if len(sys.argv) < 3:
            print("Uso: python safra_multi_commodities.py --train <commodity|todas>")
            return
        alvo = sys.argv[2]
        alvos = COMMODITIES.keys() if alvo == "todas" else [alvo]
        for key in alvos:
            if key not in COMMODITIES:
                print(f"❌ Commodity desconhecida: {key}")
                continue
            SafraMultiML(key).treinar()
    elif comando == "--predict":
        if len(sys.argv) < 3:
            print("Uso: python safra_multi_commodities.py --predict <commodity>")
            return
        key = sys.argv[2]
        if key not in COMMODITIES:
            print(f"❌ Commodity desconhecida: {key}")
            return
        ml = SafraMultiML(key)
        preco, confianca = ml.prever()
        if preco is not None:
            info = COMMODITIES[key]
            print(f"\n🔮 {info['nome']}: previsão {preco:.2f} {info['unidade']} "
                  f"(confiança {confianca:.0f}%)")
    else:
        print(f"Comando desconhecido: {comando}\n")
        _print_ajuda()


if __name__ == "__main__":
    main()
