#ingestion
import yfinance as yf
import pandas as pd
from datetime import datetime,timedelta


date_de_debut = datetime(2020, 1, 1)
date_de_fin = datetime(2024, 12, 31)

actions = ["MSFT", "AAPL", "ABNB", "GOOGL"]

df = yf.download(actions, date_de_debut, date_de_fin)
df = df.reset_index()

