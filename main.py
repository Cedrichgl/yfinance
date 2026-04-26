
from fastapi import FastAPI
from routers import stock

app = FastAPI()

app.include_router(stock.router)