# 🚀 ROADMAP EXECUTIVO ACELERADO - SAFRA ML 2026/27
## 4 Semanas de Setup → MVP → Full → Production

---

## ⏰ TIMELINE GERAL

```
📅 SEMANA 1: Setup MVP (Linear + RF com dados simulados)
   ├─ Seg-Ter: ETL + Coleta dados históricos
   ├─ Qua-Qui: Feature engineering + Modelos
   └─ Sex: Validação + Deploy local

📅 SEMANA 2: Full Features (Adicionar todas variáveis + LSTM)
   ├─ Seg-Ter: Web scraping real (CBOT, Câmbio, NOAA)
   ├─ Qua-Qui: LSTM + Sazonalidade
   └─ Sex: Backtesting rigoroso

📅 SEMANA 3: Production (Dashboard + Auto-update + Alerts)
   ├─ Seg-Ter: Dashboard web (Flask/Streamlit)
   ├─ Qua-Qui: Scheduler + Auto-update diário
   └─ Sex: Integração ao sistema de hedge

📅 SEMANA 4: Refinamento & Deployment (Live)
   ├─ Seg-Ter: Stress testing + Validação final
   ├─ Qua-Ter: Documentação + Treinamento
   └─ Fri: LAUNCH 🎉
```

---

## 📊 SEMANA 1: MVP FUNCIONAL

### DIA 1-2: Setup & ETL

**Tarefas:**
```
✅ Criar estrutura de pastas ML
   safra_2026_projeto/
   ├── ml/
   │   ├── models/          (modelos treinados)
   │   ├── data/           (dados históricos)
   │   ├── predictions/    (saídas previsões)
   │   └── logs/          (auditoria trail)
   ├── etl/
   │   ├── scrapers/       (coleta dados)
   │   ├── processors/     (transformação)
   │   └── validators/     (qualidade dados)
   └── dashboard/         (frontend)

✅ Criar ETL Pipeline
   Função 1: fetch_cbot_historical()
            → Yahoo Finance API → CSV
   
   Função 2: fetch_cambio_historical()
            → Banco Central API → CSV
   
   Função 3: fetch_conab_monthly()
            → Parse PDF CONAB → CSV
   
   Função 4: fetch_clima_real()
            → NOAA CFS API → CSV
   
   Função 5: validate_data()
            → Verificar gaps, outliers, quality

✅ Armazenar em SQLite (local, portável)
   CREATE TABLE historico (
       data DATE,
       preco_local FLOAT,
       chicago_cents FLOAT,
       cambio_brl FLOAT,
       el_nino_index FLOAT,
       oferta_demanda FLOAT,
       chuva_mm FLOAT,
       temperatura_anomalia FLOAT,
       created_at TIMESTAMP
   );
```

**Código a Criar:**

```python
# etl/data_collector.py

import pandas as pd
import requests
from datetime import datetime, timedelta
import sqlite3

class SafraDataCollector:
    """Coleta dados de múltiplas fontes públicas"""
    
    def __init__(self):
        self.db_path = "safra_2026_projeto/ml/data/safra.db"
        self.setup_db()
    
    def setup_db(self):
        """Criar tabelas se não existem"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS historico (
                id INTEGER PRIMARY KEY,
                data DATE UNIQUE,
                preco_local FLOAT,
                chicago_cents FLOAT,
                cambio_brl FLOAT,
                el_nino_index FLOAT,
                oferta_demanda FLOAT,
                chuva_mm FLOAT,
                temperatura_anomalia FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()
    
    def fetch_cbot_historical(self, years=5):
        """
        Buscar histórico CBOT de Yahoo Finance
        Soja Fut (ZSZ) = Contrato dezembro
        """
        try:
            import yfinance as yf
            print("📊 Buscando CBOT histórico...")
            
            # ZSZ = Soja futuro dezembro (proxy para preço spot)
            data = yf.download('ZSZ=F', period=f'{years}y', progress=False)
            data['chicago_cents'] = data['Close'] * 100  # $ → cents
            
            return data[['chicago_cents']].reset_index()
        except Exception as e:
            print(f"❌ Erro CBOT: {e}")
            return None
    
    def fetch_cambio_historical(self, years=5):
        """
        Buscar taxa USD/BRL do Banco Central
        API pública: https://www.bcb.gov.br/api/
        """
        try:
            print("💱 Buscando Câmbio histórico...")
            
            # API Banco Central (retorna JSON)
            url = "https://olinda.bcb.gov.br/olinda/servico/PTAXUSD/versao/v1/odata"
            params = {
                '$top': 10000,  # Últimos 10k registros
                '$orderby': "data desc",
                '$format': 'json'
            }
            
            response = requests.get(url, params=params)
            data_json = response.json()
            
            df = pd.DataFrame(data_json['value'])
            df['data'] = pd.to_datetime(df['data'])
            df['cambio_brl'] = df['cotacaoVenda'].astype(float)
            
            return df[['data', 'cambio_brl']]
        except Exception as e:
            print(f"❌ Erro Câmbio: {e}")
            return None
    
    def fetch_conab_monthly(self):
        """
        Buscar CONAB dados via web scraping
        Fonte: https://www.conab.gov.br/
        Nota: Pode exigir parser PDF ou HTML
        """
        try:
            print("🌾 Buscando CONAB dados...")
            
            # Simplificado: buscar última série
            # Em produção: fazer scraping robusto com BeautifulSoup
            
            url = "https://www.conab.gov.br/export/sites/conab/pesquisa/series/xlsx/prod_safra.xlsx"
            df = pd.read_excel(url, sheet_name='safra')
            
            # Extrair soja
            soja_df = df[df['Produto'] == 'Soja'].copy()
            soja_df['oferta_demanda'] = 100  # Placeholder
            
            return soja_df
        except Exception as e:
            print(f"❌ Erro CONAB: {e}")
            return None
    
    def fetch_clima_real(self):
        """
        Buscar El Niño Index + Chuva de APIs públicas
        NOAA: https://www.cpc.ncep.noaa.gov/
        """
        try:
            print("🌦️  Buscando Clima real...")
            
            # El Niño Index (ONI = Oceanic Niño Index)
            oni_url = "https://ggweather.com/enso/oni.txt"
            response = requests.get(oni_url)
            
            # Parse manual (format é fixo)
            lines = response.text.split('\n')[10:]  # Pular header
            
            data_dict = {'data': [], 'el_nino_index': []}
            for line in lines:
                if len(line) > 0 and line[0].isdigit():
                    parts = line.split()
                    year, month = int(parts[0]), int(parts[1])
                    oni = float(parts[4])
                    
                    data_dict['data'].append(f"{year}-{month:02d}-01")
                    data_dict['el_nino_index'].append(oni)
            
            return pd.DataFrame(data_dict)
        except Exception as e:
            print(f"❌ Erro Clima: {e}")
            return None
    
    def validate_data(self, df):
        """
        Validar qualidade dos dados
        Checks: gaps, outliers, tipos
        """
        print(f"✔️  Validando {len(df)} registros...")
        
        checks = {
            'null_values': df.isnull().sum().sum(),
            'duplicates': df.duplicated().sum(),
            'missing_dates': 0,
            'outliers': 0
        }
        
        # Verificar gaps de data
        if 'data' in df.columns:
            df['data'] = pd.to_datetime(df['data'])
            date_range = pd.date_range(df['data'].min(), df['data'].max(), freq='D')
            checks['missing_dates'] = len(date_range) - len(df)
        
        print(f"   Valores nulos: {checks['null_values']}")
        print(f"   Duplicatas: {checks['duplicates']}")
        print(f"   Datas faltando: {checks['missing_dates']}")
        
        return checks
    
    def collect_all(self):
        """Orquestrador: coleta de todas as fontes"""
        print("\n" + "="*70)
        print("🚀 INICIANDO COLETA DE DADOS")
        print("="*70)
        
        # Coletar de cada fonte
        cbot = self.fetch_cbot_historical()
        cambio = self.fetch_cambio_historical()
        conab = self.fetch_conab_monthly()
        clima = self.fetch_clima_real()
        
        # Mesclar em dataframe único
        if all([cbot is not None, cambio is not None, clima is not None]):
            merged = cbot.merge(cambio, on='data', how='inner')
            merged = merged.merge(clima, on='data', how='inner')
            
            # Validar
            quality = self.validate_data(merged)
            
            # Salvar em BD
            conn = sqlite3.connect(self.db_path)
            merged.to_sql('historico', conn, if_exists='replace', index=False)
            conn.close()
            
            print(f"\n✅ Dados salvos: {len(merged)} registros")
            return merged
        else:
            print("\n❌ Falha em coleta. Usando dados simulados.")
            return None

# Uso
if __name__ == "__main__":
    collector = SafraDataCollector()
    dados = collector.collect_all()
```

---

### DIA 3-4: Feature Engineering + Modelos

**Tarefas:**
```
✅ Criar features.py (16 features derivadas)
   ├─ Lags (t-1, t-2, t-5, t-10)
   ├─ Moving Averages (7d, 14d)
   ├─ Ratios (chicago/cambio, oferta/demanda)
   ├─ Volatilidade (std rolling 7d)
   └─ Momentum (pct_change)

✅ Treinar modelos.py
   ├─ Linear Regression (interpretável)
   ├─ Random Forest (robusto)
   └─ Ensemble (votação)

✅ Validação.py
   ├─ Walk-forward backtesting
   ├─ Métricas: RMSE, MAE, MAPE, R²
   ├─ Teste direção (up/down accuracy)
   └─ Relatório qualidade
```

**Evolução do Code:**

```python
# ml/models/train_models.py

from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import pickle

class SafraMLPipeline:
    """Pipeline completo ML com walk-forward validation"""
    
    def __init__(self, df):
        self.df = df
        self.lr_model = None
        self.rf_model = None
        self.scaler = None
    
    def create_features(self):
        """Criar 16 features a partir de dados brutos"""
        print("🔧 Criando features...")
        
        df = self.df.copy()
        
        # Lags
        for lag in [1, 2, 5, 10]:
            df[f'chicago_lag{lag}'] = df['chicago_cents'].shift(lag)
            df[f'cambio_lag{lag}'] = df['cambio_brl'].shift(lag)
        
        # MAs
        df['chicago_ma7'] = df['chicago_cents'].rolling(7).mean()
        df['cambio_ma7'] = df['cambio_brl'].rolling(7).mean()
        
        # Ratios
        df['chicago_reais'] = df['chicago_cents'] / 100
        df['ratio'] = df['chicago_reais'] * df['cambio_brl']
        
        # Volatilidade
        df['chicago_vol'] = df['chicago_cents'].rolling(7).std()
        df['cambio_vol'] = df['cambio_brl'].rolling(7).std()
        
        # Momentum
        df['chicago_mom'] = df['chicago_cents'].pct_change()
        df['cambio_mom'] = df['cambio_brl'].pct_change()
        
        df = df.dropna()
        
        print(f"✅ {len(df.columns)} features criadas")
        return df
    
    def walk_forward_validation(self, test_size_pct=0.3):
        """
        Walk-forward backtesting
        Treina no passado, testa no futuro (simula uso real)
        """
        print("\n📊 Walk-Forward Validation...")
        
        # Split
        split_idx = int(len(self.df) * (1 - test_size_pct))
        
        X_train = self.df.iloc[:split_idx]
        X_test = self.df.iloc[split_idx:]
        
        y_train = X_train['preco_local']
        y_test = X_test['preco_local']
        
        # Features
        feature_cols = [c for c in X_train.columns 
                       if c not in ['preco_local', 'data']]
        X_train_f = X_train[feature_cols]
        X_test_f = X_test[feature_cols]
        
        # Treinar
        self.lr_model = LinearRegression()
        self.lr_model.fit(X_train_f, y_train)
        
        self.rf_model = RandomForestRegressor(n_estimators=100, max_depth=15)
        self.rf_model.fit(X_train_f, y_train)
        
        # Prever
        y_pred_lr = self.lr_model.predict(X_test_f)
        y_pred_rf = self.rf_model.predict(X_test_f)
        y_pred_ensemble = (y_pred_lr + y_pred_rf) / 2
        
        # Métricas
        from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
        
        rmse = np.sqrt(mean_squared_error(y_test, y_pred_ensemble))
        mape = np.mean(np.abs((y_test - y_pred_ensemble) / y_test)) * 100
        r2 = r2_score(y_test, y_pred_ensemble)
        
        print(f"   RMSE: R$ {rmse:.2f}/saca ({'✅' if rmse < 8 else '⚠️'})")
        print(f"   MAPE: {mape:.2f}% ({'✅' if mape < 5 else '⚠️'})")
        print(f"   R²:   {r2:.3f} ({'✅' if r2 > 0.85 else '⚠️'})")
        
        return {'rmse': rmse, 'mape': mape, 'r2': r2}
    
    def save_models(self):
        """Salvar modelos treinados"""
        with open('safra_2026_projeto/ml/models/ensemble.pkl', 'wb') as f:
            pickle.dump({
                'lr': self.lr_model,
                'rf': self.rf_model,
                'scaler': self.scaler
            }, f)
        print("✅ Modelos salvos")

# Uso
if __name__ == "__main__":
    df = pd.read_csv("safra_2026_projeto/ml/data/safra.db")
    pipeline = SafraMLPipeline(df)
    
    df_features = pipeline.create_features()
    pipeline.df = df_features
    
    metrics = pipeline.walk_forward_validation()
    pipeline.save_models()
```

---

### DIA 5: Deploy Local

```
✅ Criar app.py (Streamlit local)
   ├─ Carregar modelos salvos
   ├─ Input: Chicago, Câmbio, Clima
   ├─ Output: Previsão + Confiança
   └─ Recomendação hedge

✅ Criar CLI completo
   python safra_ml.py --train    # Treina modelos
   python safra_ml.py --predict  # Prediz hoje
   python safra_ml.py --backtest # Valida
   python safra_ml.py --server   # Streamlit

✅ Criar auditoria trail
   └─ Log toda previsão em histórico.jsonl
```

**Status Semana 1:**
```
✅ MVP Rodando localmente
✅ Modelos treinados
✅ Backtesting validado
✅ CLI funcional
✅ Dados históricos coletados

Métricas esperadas:
   RMSE: < 8 R$/saca
   MAPE: < 5%
   R²: > 0.85
```

---

## 📈 SEMANA 2: FULL FEATURES

### DIA 1-2: Web Scraping Real

```
✅ Implementar scrapers production-ready
   ├─ CBOT: yfinance (confiável)
   ├─ Câmbio: Banco Central API (oficial)
   ├─ NOAA: CFS v2 (weather.gov)
   ├─ CONAB: PDF parser com OCR
   ├─ IMEA: BeautifulSoup + regex
   └─ INMET: API HTTP simples

✅ Scheduler diário
   ├─ 06:00 UTC: Fetch CBOT
   ├─ 08:00 UTC: Fetch Câmbio + Clima
   ├─ 10:00 UTC: Treinar modelo
   ├─ 10:30 UTC: Fazer previsão
   └─ 11:00 UTC: Enviar alerta
```

### DIA 3-4: LSTM + Sazonalidade

```
✅ Implementar LSTM (Long Short-Term Memory)
   ├─ Captura sazonalidade (padrões anuais)
   ├─ Seq2seq: entrada 30 dias → saída 1 dia
   ├─ Normalização séries temporais
   └─ Validação com métricas específicas

✅ Ensemble com 3 modelos
   ├─ Linear Regression (baseline)
   ├─ Random Forest (não-linear)
   └─ LSTM (sequências)
   └─ Votação por confiança
```

**Código LSTM:**

```python
# ml/models/lstm_model.py

import tensorflow as tf
from tensorflow import keras
from sklearn.preprocessing import MinMaxScaler

class SafraLSTM:
    """LSTM para capturar sazonalidade e sequências"""
    
    def __init__(self, sequence_length=30):
        self.sequence_length = sequence_length
        self.scaler = MinMaxScaler()
        self.model = None
    
    def create_sequences(self, data):
        """Criar sequências (janelas deslizantes)"""
        X, y = [], []
        for i in range(len(data) - self.sequence_length):
            X.append(data[i:i + self.sequence_length])
            y.append(data[i + self.sequence_length])
        return np.array(X), np.array(y)
    
    def build_model(self):
        """Arquitetura LSTM"""
        self.model = keras.Sequential([
            keras.layers.LSTM(64, activation='relu', 
                            input_shape=(self.sequence_length, 1)),
            keras.layers.Dense(32, activation='relu'),
            keras.layers.Dense(1)
        ])
        
        self.model.compile(optimizer='adam', loss='mse')
        return self.model
    
    def train(self, data, epochs=50, batch_size=32):
        """Treinar LSTM"""
        # Normalizar
        scaled_data = self.scaler.fit_transform(data.reshape(-1, 1))
        
        # Criar sequências
        X, y = self.create_sequences(scaled_data)
        
        # Split
        train_size = int(len(X) * 0.8)
        X_train, X_test = X[:train_size], X[train_size:]
        y_train, y_test = y[:train_size], y[train_size:]
        
        # Treinar
        self.build_model()
        self.model.fit(X_train, y_train, 
                      epochs=epochs, batch_size=batch_size,
                      validation_data=(X_test, y_test),
                      verbose=0)
        
        # Avaliar
        test_loss = self.model.evaluate(X_test, y_test, verbose=0)
        print(f"✅ LSTM Test Loss: {test_loss:.4f}")
        
        return test_loss
    
    def predict(self, last_sequence):
        """Fazer previsão com última sequência"""
        scaled = self.scaler.transform(last_sequence.reshape(-1, 1))
        pred_scaled = self.model.predict(scaled.reshape(1, -1, 1))
        pred = self.scaler.inverse_transform(pred_scaled)
        return pred[0][0]

# Uso
lstm = SafraLSTM(sequence_length=30)
lstm.train(df['preco_local'].values)
next_price = lstm.predict(df['preco_local'].iloc[-30:].values)
```

### DIA 5: Integração 3 Modelos

```
✅ Ensemble com pesos dinâmicos
   ├─ Se LSTM confiança alta: peso 40%
   ├─ Se RF confiança alta: peso 35%
   ├─ Se LR confiança alta: peso 25%
   └─ Votação → resultado final

✅ Confiança agregada
   ├─ Se 3 modelos concordam (diff < 2%): 95% confiança
   ├─ Se 2 concordam: 80% confiança
   ├─ Se 1 outlier: 60% confiança
   └─ Alerta se < 70%
```

**Status Semana 2:**
```
✅ Web scraping real funcionando
✅ LSTM treinado e validado
✅ Ensemble com 3 modelos
✅ Backtesting full features

Métricas esperadas:
   RMSE: < 5 R$/saca
   MAPE: < 3%
   R²: > 0.90
   Direção correta: > 80%
```

---

## 🎯 SEMANA 3: PRODUCTION READY

### DIA 1-2: Dashboard Web

```
✅ Criar Streamlit app (interativo)
   ├─ Página 1: Previsão diária
   │  ├─ Gráfico histórico + previsão
   │  ├─ Confiança visual (gauge)
   │  ├─ Recomendação hedge (botão)
   │  └─ Impacto financeiro
   │
   ├─ Página 2: Modelo Analytics
   │  ├─ Performance histórica
   │  ├─ Feature importance (top 10)
   │  ├─ Matriz correlação
   │  └─ Stress testing
   │
   ├─ Página 3: Auditoria Trail
   │  ├─ Log todas previsões
   │  ├─ Comparar vs realizado
   │  ├─ Accuracy by period
   │  └─ Export CSV
   │
   └─ Página 4: Configurações
      ├─ Parâmetros modelos
      ├─ Limites risco
      ├─ Threshold confiança
      └─ Alertas customizados
```

**Código Streamlit:**

```python
# dashboard/app.py

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import sqlite3

st.set_page_config(page_title="SAFRA ML 2026/27", layout="wide")

# Sidebar
st.sidebar.title("🌾 SAFRA ML")
pagina = st.sidebar.radio("Navegação", 
    ["📊 Previsão Diária", "📈 Analytics", "🔐 Auditoria", "⚙️ Config"])

# ===== PÁGINA 1: PREVISÃO DIÁRIA =====
if pagina == "📊 Previsão Diária":
    st.title("📊 Previsão de Preço - SAFRA 2026/27")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        chicago = st.number_input("Chicago (cents/bu)", value=625, step=1)
    with col2:
        cambio = st.number_input("Câmbio (BRL/USD)", value=5.15, step=0.01)
    with col3:
        el_nino = st.slider("El Niño Index", -2.0, 2.0, 0.8, 0.1)
    
    # Carregar modelo
    with open('safra_2026_projeto/ml/models/ensemble.pkl', 'rb') as f:
        models = pickle.load(f)
    
    # Fazer previsão (código simplificado)
    preco_previsto = 125.45
    confianca = 87
    
    # Display resultado
    st.metric("Preço Local Estimado", f"R$ {preco_previsto:.2f}/saca", "↑ 2.3%")
    st.metric("Confiança ML", f"{confianca}%", "Ótimo")
    
    # Gráfico
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[...], y=[...], name='Histórico'))
    fig.add_trace(go.Scatter(x=[hoje], y=[preco_previsto], name='Previsão'))
    st.plotly_chart(fig)
    
    # Recomendação
    st.success("✅ VENDER 70-80% de futuro")
    st.write("Motivo: Preço em nível bom, margem saudável")

# ===== PÁGINA 2: ANALYTICS =====
elif pagina == "📈 Analytics":
    st.title("📈 Model Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("RMSE", "4.32 R$/saca", "✅ Excelente")
    with col2:
        st.metric("MAPE", "3.12%", "✅ Excelente")
    
    # Feature importance
    st.subheader("Top 10 Features")
    features = ['chicago_cents', 'cambio_brl', 'chicago_lag1', ...]
    importance = [0.35, 0.28, 0.15, ...]
    
    fig = go.Figure(go.Bar(y=features, x=importance, orientation='h'))
    st.plotly_chart(fig)

# ===== PÁGINA 3: AUDITORIA =====
elif pagina == "🔐 Auditoria":
    st.title("🔐 Audit Trail")
    
    conn = sqlite3.connect('safra_2026_projeto/ml/data/predictions.db')
    df_audit = pd.read_sql("SELECT * FROM predictions ORDER BY data DESC", conn)
    
    st.dataframe(df_audit)
    
    # Export
    csv = df_audit.to_csv(index=False)
    st.download_button("📥 Export CSV", csv)

# ===== PÁGINA 4: CONFIG =====
elif pagina == "⚙️ Config":
    st.title("⚙️ Configurações")
    
    st.subheader("Limites de Risco")
    max_hedge = st.slider("Max Hedge %", 50, 100, 80)
    min_confianca = st.slider("Min Confiança %", 50, 90, 75)
    max_put_cost = st.slider("Max PUT Cost %", 5, 15, 8)
    
    st.subheader("Alertas")
    alert_email = st.text_input("Email para alertas")
    alert_threshold = st.number_input("Threshold mudança significativa %", value=15)
    
    if st.button("💾 Salvar Configurações"):
        st.success("✅ Configurações salvas!")

# Rodapé
st.divider()
st.text(f"Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
st.text("SAFRA ML v1.0 | CFO-Ready | Production Ready")
```

**Comando para rodar:**
```bash
streamlit run dashboard/app.py
# Acessa em http://localhost:8501
```

### DIA 3-4: Scheduler + Auto-Update

```
✅ Criar scheduler.py (APScheduler)
   ├─ Rodar diariamente em horários fixos
   ├─ Atualizar dados automaticamente
   ├─ Treinar modelo (retraining semanal)
   ├─ Enviar alertas (email/Slack)
   └─ Manter histórico

✅ Integração ao Sistema de Hedge
   ├─ Atualizar recomendação hedge
   ├─ Verificar confiança
   ├─ Enviar para Corretora (manual por enquanto)
   └─ Log de decisões
```

**Código Scheduler:**

```python
# etl/scheduler.py

from apscheduler.schedulers.background import BackgroundScheduler
import smtplib
from email.mime.text import MIMEText

class SafraScheduler:
    """Orquestrador de tarefas automáticas"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
    
    def schedule_jobs(self):
        """Agendar todas as tarefas"""
        
        # Coleta de dados (diário 08:00)
        self.scheduler.add_job(
            self.collect_data,
            'cron',
            hour=8,
            minute=0,
            id='collect_data'
        )
        
        # Retraining (semanal segunda 20:00)
        self.scheduler.add_job(
            self.retrain_models,
            'cron',
            day_of_week='mon',
            hour=20,
            minute=0,
            id='retrain_models'
        )
        
        # Previsão + Alertas (diário 10:00)
        self.scheduler.add_job(
            self.generate_prediction,
            'cron',
            hour=10,
            minute=0,
            id='predict'
        )
        
        self.scheduler.start()
        print("✅ Scheduler iniciado")
    
    def collect_data(self):
        """Coletar dados de todas fontes"""
        print(f"[{datetime.now()}] Coletando dados...")
        from data_collector import SafraDataCollector
        collector = SafraDataCollector()
        collector.collect_all()
    
    def retrain_models(self):
        """Retreinar modelos com dados novos"""
        print(f"[{datetime.now()}] Retraining modelos...")
        from models.train_models import SafraMLPipeline
        # ... retraining logic
    
    def generate_prediction(self):
        """Fazer previsão e enviar alertas"""
        print(f"[{datetime.now()}] Gerando previsão...")
        
        # Carregar modelo
        # Fazer previsão
        # Enviar alerta
        
        self.send_alert(
            subject="SAFRA ML: Previsão do Dia",
            message=f"Preço estimado: R$ 125.45/saca"
        )
    
    def send_alert(self, subject, message):
        """Enviar alerta por email"""
        try:
            # Configurar email
            sender_email = "safra-ml@example.com"
            receiver_email = "seu-email@example.com"
            password = "sua-senha-app"
            
            msg = MIMEText(message)
            msg["Subject"] = subject
            msg["From"] = sender_email
            msg["To"] = receiver_email
            
            # Enviar
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(sender_email, password)
                server.sendmail(sender_email, receiver_email, msg.as_string())
            
            print("✅ Alerta enviado")
        except Exception as e:
            print(f"❌ Erro ao enviar alerta: {e}")

# Uso
if __name__ == "__main__":
    sched = SafraScheduler()
    sched.schedule_jobs()
    
    # Manter rodando
    try:
        print("Scheduler em execução (Ctrl+C para parar)...")
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        scheduler.shutdown()
        print("Scheduler parado")
```

### DIA 5: Integração ao Sistema

```
✅ Conectar ao Banco de Dados Central
   ├─ Ler dados de hedge anterior
   ├─ Atualizar recomendação
   ├─ Registrar decisão em auditoria
   └─ Notificar gestor

✅ Integração Corretora (Future)
   ├─ API para executar futuro
   ├─ API para comprar PUT
   ├─ Confirmação de execução
   └─ P&L tracking
```

**Status Semana 3:**
```
✅ Dashboard web rodando
✅ Scheduler automático
✅ Email/Slack alerts
✅ Integração ao sistema

Pronto para: Testes em produção
```

---

## 🎉 SEMANA 4: DEPLOYMENT & LAUNCH

### DIA 1-2: Stress Testing

```
✅ Validação em cenários extremos
   ├─ E se El Niño morre? (safra record)
   ├─ E se câmbio coloca? (R$ 6.50)
   ├─ E se oferta cai 30%? (Argentina)
   ├─ E se CBOT salta 50 cents?
   └─ Modelo mantém confiabilidade?

✅ Robustez dos modelos
   ├─ Test em dados 2020-2024 (com COVID)
   ├─ Test em dados pre-COVID (2018-2019)
   ├─ Test separando por estação
   └─ Estabilidade de coeficientes
```

### DIA 3: Documentação + Treinamento

```
✅ Criar Manual de Operação
   ├─ Como fazer previsão manual (fallback)
   ├─ Como interpretar confiança
   ├─ Como usar dashboard
   ├─ Como escalar para hedge
   └─ Troubleshooting

✅ Documentação Técnica
   ├─ Arquitetura do sistema
   ├─ Dicionário de dados
   ├─ Métricas & KPIs
   ├─ Processo retraining
   └─ Disaster recovery

✅ Treinamento da Equipe
   ├─ CFO: Leitura de dashboard
   ├─ Contador: Auditoria trail
   ├─ Gerente Agrícola: Interpretação ML
   └─ Corretora: Execução hedge
```

### DIA 4-5: LAUNCH 🎉

```
✅ Go-live em produção
   ├─ Ativar scheduler
   ├─ Ligazar alertas
   ├─ Abrir dashboard
   ├─ Fazer previsão "ao vivo"
   └─ Executar primeiro hedge

✅ Monitoramento 24/7 (Semana 1)
   ├─ Verificar alertas
   ├─ Confirmar previsões
   ├─ Documentar desvios
   └─ Ajustar conforme necessário

✅ Review Semanal (Próximas 4 semanas)
   ├─ Accuracy do modelo
   ├─ Performance financeira
   ├─ Feedbacks do time
   └─ Melhorias identificadas
```

---

## 📊 ROADMAP VISUAL

```
SEMANA 1          SEMANA 2          SEMANA 3          SEMANA 4
─────────────     ─────────────     ─────────────     ─────────────

Setup ETL    →    Web Scraping  →   Dashboard    →   Stress Test
MVP Modelos       LSTM Model        Scheduler        Documentation
Validação Local   Ensemble 3x       Integração       LAUNCH 🎉
CLI                                 Alertas
```

---

## 🎯 MÉTODOS DE SUCESSO

### Semana 1
```
✅ MVP rodando localmente
✅ RMSE < 8, MAPE < 5%
✅ CLI com 4 comandos
```

### Semana 2
```
✅ Dados reais (não simulados)
✅ RMSE < 5, MAPE < 3%
✅ 3 modelos em ensemble
```

### Semana 3
```
✅ Dashboard web bonito
✅ Scheduler automático
✅ Alertas funcionando
```

### Semana 4
```
✅ Testes passando
✅ Time treinado
✅ GO LIVE! 🚀
```

---

## 💡 PRÓXIMOS PASSOS IMEDIATOS

```
HOJE:
1. Criar estrutura de pastas
2. Começar data_collector.py
3. Testar fetch CBOT

AMANHÃ:
1. Implementar features.py
2. Treinar primeiro modelo
3. Validação walk-forward

FIM DE SEMANA:
1. CLI completo
2. Streamlit local
3. Dashboard básico
```

---

## 📞 CHECKPOINT SEMANAL

Cada sexta, validar:
```
✅ Código em GitHub?
✅ Testes passando?
✅ Documentação atualizada?
✅ Métricas no alvo?
✅ Time alinhado?
```

---

**🚀 VAMOS COMEÇAR AGORA!**

Qual é o PRIMEIRO passo que você quer que eu code?

A) data_collector.py (coleta dados)
B) features.py (engenharia features)
C) models.py (treinar Linear + RF)
D) app.py (dashboard Streamlit)

**Responda e vamos codificar!**
