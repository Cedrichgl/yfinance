#ingestion dans la base de données
import sys
sys.path.append(".")

from services.data import df
from database import SessionLocal
import pandas as pd
from models.stock import Stock

db = SessionLocal()

# Aplatir le MultiIndex des colonnes
df_flat = df.copy()
df_flat.columns = [col if col == 'Date' else f"{col[0]}_{col[1]}" for col in df_flat.columns]
df_flat = df_flat.drop(columns=[col for col in df_flat.columns if col.startswith("Adj")])
print(df_flat.columns.tolist())  # ← ici
print(df_flat.head(2))

tickers = ["MSFT", "AAPL", "ABNB", "GOOGL"]

for ticker in tickers:
    for _, row in df_flat.iterrows():
        if pd.isna(row[f"Close_{ticker}"]):
            continue
        record = Stock(
            ticker=ticker,
            date=row["Date_"].date(),
            open=row[f"Open_{ticker}"],
            high=row[f"High_{ticker}"],
            low=row[f"Low_{ticker}"],
            close=row[f"Close_{ticker}"],
            volume=int(row[f"Volume_{ticker}"]),
        )
        db.merge(record)

db.commit()
db.close()
print("Ingestion terminée")