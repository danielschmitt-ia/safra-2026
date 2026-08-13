#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🌐 SAFRA 2026/27 - Coletor de Dados de Mercado
===================================================================

ETL (Extract-Transform-Load) que busca dados públicos reais para
alimentar o pipeline de ML (safra_ml_mvp.py):
1. CBOT (soja Chicago) → Yahoo Finance
2. Câmbio USD/BRL → Banco Central do Brasil (PTAX)
3. El Niño (ONI) → NOAA / ggweather.com

⚠️ AVISO IMPORTANTE
Este ambiente de desenvolvimento tem a rede restrita por política
organizacional (bloqueia yahoo.com, bcb.gov.br etc.), então as funções
de rede abaixo NÃO puderam ser testadas contra os endpoints reais
aqui. A lógica foi escrita com o máximo de cuidado (corrigindo bugs
encontrados no roadmap original), mas rode `--test-conexoes` na sua
máquina antes de confiar em `--collect` em produção.

Uso:
    python safra_data_collector.py --test-conexoes  # Testa cada fonte isoladamente
    python safra_data_collector.py --collect        # Coleta tudo e salva no SQLite
    python safra_data_collector.py --status          # Mostra o que já está salvo
"""

import re
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests


class SafraDataCollector:
    """Coleta dados de mercado de fontes públicas (CBOT, câmbio, clima)"""

    # BCB limita o range de algumas consultas; buscamos ano a ano para
    # não depender de paginação nem estourar limites não documentados.
    BCB_PTAX_URL = (
        "https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/"
        "CotacaoDolarPeriodo(dataInicial=@dataInicial,dataFinalCotacao=@dataFinalCotacao)"
    )
    ONI_URL = "https://ggweather.com/enso/oni.txt"

    # Mapeia cada temporada trimestral (ONI) para o mês central, para dar
    # uma data única e comparável às outras séries diárias.
    SEASON_TO_MONTH = {
        "DJF": 1, "JFM": 2, "FMA": 3, "AMJ": 4, "MJJ": 5, "JJA": 6,
        "JAS": 7, "ASO": 8, "SON": 9, "OND": 10, "NDJ": 11,
    }

    def __init__(self, project_dir="safra_2026_projeto"):
        self.project_dir = Path(project_dir)
        self.data_dir = self.project_dir / "dados"
        self.logs_dir = self.project_dir / "logs"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        self.db_path = self.data_dir / "safra_mercado.db"
        self._setup_db()

        print("🌐 SAFRA Data Collector Inicializado")

    def _setup_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS chicago (
                data DATE PRIMARY KEY,
                chicago_cents FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS cambio (
                data DATE PRIMARY KEY,
                cambio_brl FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS clima (
                data DATE PRIMARY KEY,
                el_nino_index FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    # ============================================================================
    # FONTE 1: CBOT (Yahoo Finance)
    # ============================================================================

    def fetch_cbot_historical(self, years=5):
        """
        Busca histórico do futuro de soja (ZS=F) via yfinance.

        NOTA: soja no CBOT é cotada em cents/bushel diretamente — o Close
        retornado pelo Yahoo já vem nessa unidade, sem precisar multiplicar
        por 100 (o roadmap original fazia isso por engano).
        """
        try:
            import yfinance as yf
        except ImportError:
            print("❌ yfinance não instalado. Rode: pip install yfinance")
            return None

        try:
            print("📊 Buscando CBOT histórico (ZS=F)...")
            data = yf.download("ZS=F", period=f"{years}y", progress=False)

            if data is None or data.empty:
                print("❌ CBOT: resposta vazia do Yahoo Finance")
                return None

            close_col = "Close"
            if isinstance(data.columns, pd.MultiIndex):
                close = data["Close"].iloc[:, 0]
            else:
                close = data[close_col]

            df = pd.DataFrame({
                "data": pd.to_datetime(data.index).date,
                "chicago_cents": close.values,
            })
            return df.dropna()
        except Exception as e:
            print(f"❌ Erro CBOT: {e}")
            return None

    # ============================================================================
    # FONTE 2: Câmbio (Banco Central - PTAX)
    # ============================================================================

    def fetch_cambio_historical(self, years=5):
        """
        Busca cotação PTAX de fechamento (USD/BRL) via API do Banco Central,
        ano a ano (evita depender de paginação não documentada).
        """
        print("💱 Buscando Câmbio histórico (BCB PTAX)...")

        ano_atual = datetime.now().year
        frames = []

        for ano in range(ano_atual - years + 1, ano_atual + 1):
            data_inicial = f"01-01-{ano}"
            data_final = f"12-31-{ano}"
            params = {
                "@dataInicial": f"'{data_inicial}'",
                "@dataFinalCotacao": f"'{data_final}'",
                "$format": "json",
            }
            try:
                resp = requests.get(self.BCB_PTAX_URL, params=params, timeout=30)
                resp.raise_for_status()
                registros = resp.json().get("value", [])
                if not registros:
                    continue

                df_ano = pd.DataFrame(registros)
                df_ano["data"] = pd.to_datetime(df_ano["dataHoraCotacao"]).dt.date
                df_ano["cambio_brl"] = df_ano["cotacaoVenda"].astype(float)
                frames.append(df_ano[["data", "cambio_brl"]])
            except Exception as e:
                print(f"⚠️  Câmbio {ano}: falhou ({e}), pulando")
                continue

        if not frames:
            print("❌ Câmbio: nenhum dado coletado")
            return None

        df = pd.concat(frames, ignore_index=True)
        # Pode haver mais de uma cotação no mesmo dia; mantém a última.
        df = df.drop_duplicates(subset="data", keep="last").sort_values("data")
        return df

    # ============================================================================
    # FONTE 3: Clima (El Niño / ONI)
    # ============================================================================

    def fetch_clima_oni(self):
        """
        Busca o índice ONI (Oceanic Niño Index) histórico.

        A tabela publicada é "larga" (um ano por linha, uma coluna por
        temporada trimestral: DJF, JFM, ...), não "ano + mês" como o
        roadmap original assumia. O parser abaixo lê o cabeçalho para
        descobrir as colunas em vez de supor posições fixas, e ignora
        silenciosamente linhas que não conseguir interpretar.
        """
        try:
            print("🌦️  Buscando El Niño (ONI)...")
            resp = requests.get(self.ONI_URL, timeout=30)
            resp.raise_for_status()

            linhas = resp.text.splitlines()
            header_idx = None
            seasons = []
            for i, linha in enumerate(linhas):
                tokens = linha.split()
                candidatos = [t for t in tokens if t.upper() in self.SEASON_TO_MONTH]
                if len(candidatos) >= 6:  # header de verdade tem ~11-12 temporadas
                    header_idx = i
                    seasons = [t.upper() for t in tokens]
                    break

            if header_idx is None:
                print("❌ Clima: não encontrei o cabeçalho esperado no arquivo ONI")
                return None

            registros = {"data": [], "el_nino_index": []}
            for linha in linhas[header_idx + 1:]:
                tokens = linha.split()
                if not tokens or not re.fullmatch(r"\d{4}", tokens[0]):
                    continue
                ano = int(tokens[0])
                valores = tokens[1:]
                for season, valor in zip(seasons, valores):
                    mes = self.SEASON_TO_MONTH.get(season)
                    if mes is None:
                        continue
                    try:
                        oni = float(valor)
                    except ValueError:
                        continue
                    registros["data"].append(f"{ano}-{mes:02d}-01")
                    registros["el_nino_index"].append(oni)

            if not registros["data"]:
                print("❌ Clima: nenhuma linha de dados reconhecida")
                return None

            df = pd.DataFrame(registros)
            df["data"] = pd.to_datetime(df["data"]).dt.date
            return df.sort_values("data")
        except Exception as e:
            print(f"❌ Erro Clima: {e}")
            return None

    # ============================================================================
    # VALIDAÇÃO
    # ============================================================================

    def validate_data(self, df, nome):
        """Checagem básica de qualidade: nulos, duplicatas, faixa de datas"""
        if df is None or df.empty:
            print(f"⚠️  {nome}: sem dados para validar")
            return {"ok": False}

        nulos = df.isnull().sum().sum()
        duplicatas = df.duplicated(subset="data").sum()
        print(f"✔️  {nome}: {len(df)} registros | nulos={nulos} | duplicatas={duplicatas} "
              f"| {df['data'].min()} → {df['data'].max()}")
        return {"ok": True, "registros": len(df), "nulos": int(nulos), "duplicatas": int(duplicatas)}

    # ============================================================================
    # PERSISTÊNCIA
    # ============================================================================

    def _salvar(self, tabela, df):
        if df is None or df.empty:
            return 0
        conn = sqlite3.connect(self.db_path)
        cols = [c for c in df.columns if c != "created_at"]
        placeholders = ", ".join("?" for _ in cols)
        col_list = ", ".join(cols)
        rows = df[cols].itertuples(index=False, name=None)
        conn.executemany(
            f"INSERT OR REPLACE INTO {tabela} ({col_list}) VALUES ({placeholders})",
            [tuple(str(v) if i == 0 else v for i, v in enumerate(row)) for row in rows],
        )
        conn.commit()
        conn.close()
        return len(df)

    # ============================================================================
    # ORQUESTRAÇÃO
    # ============================================================================

    def testar_conexoes(self):
        """Faz uma checagem leve (poucos dias) de cada fonte, sem salvar nada."""
        print("\n" + "=" * 70)
        print("🔌 TESTE DE CONEXÕES")
        print("=" * 70)

        resultados = {}

        cbot = self.fetch_cbot_historical(years=1)
        resultados["cbot"] = self.validate_data(cbot, "CBOT")

        cambio = self.fetch_cambio_historical(years=1)
        resultados["cambio"] = self.validate_data(cambio, "Câmbio")

        clima = self.fetch_clima_oni()
        resultados["clima"] = self.validate_data(clima, "Clima (ONI)")

        print("\n📋 Resumo:")
        for fonte, r in resultados.items():
            status = "✅ OK" if r.get("ok") else "❌ FALHOU"
            print(f"   {fonte}: {status}")

        return resultados

    def collect_all(self, years=5):
        """Coleta todas as fontes e persiste no SQLite"""
        print("\n" + "=" * 70)
        print("🚀 INICIANDO COLETA DE DADOS")
        print("=" * 70)

        cbot = self.fetch_cbot_historical(years=years)
        self.validate_data(cbot, "CBOT")
        n_cbot = self._salvar("chicago", cbot)

        cambio = self.fetch_cambio_historical(years=years)
        self.validate_data(cambio, "Câmbio")
        n_cambio = self._salvar("cambio", cambio)

        clima = self.fetch_clima_oni()
        self.validate_data(clima, "Clima (ONI)")
        n_clima = self._salvar("clima", clima)

        print(f"\n✅ Salvos: {n_cbot} CBOT, {n_cambio} câmbio, {n_clima} clima")
        print(f"   Banco: {self.db_path}")

        if n_cbot == 0 and n_cambio == 0 and n_clima == 0:
            print("\n⚠️  Nenhuma fonte retornou dados. Rode --test-conexoes para diagnosticar.")

    def status(self):
        """Mostra o que já está salvo no banco local"""
        if not self.db_path.exists():
            print("📭 Nenhum dado coletado ainda. Rode --collect primeiro.")
            return

        conn = sqlite3.connect(self.db_path)
        for tabela in ["chicago", "cambio", "clima"]:
            cur = conn.execute(f"SELECT COUNT(*), MIN(data), MAX(data) FROM {tabela}")
            count, dmin, dmax = cur.fetchone()
            print(f"   {tabela}: {count} registros ({dmin or '-'} → {dmax or '-'})")
        conn.close()


def main():
    collector = SafraDataCollector()

    if len(sys.argv) < 2:
        print(__doc__)
        return

    comando = sys.argv[1].lower()

    if comando == "--test-conexoes":
        collector.testar_conexoes()
    elif comando == "--collect":
        collector.collect_all()
    elif comando == "--status":
        collector.status()
    else:
        print(f"Comando desconhecido: {comando}")
        print(__doc__)


if __name__ == "__main__":
    main()
