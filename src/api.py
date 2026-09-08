from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import jwt
import datetime

from pipeline import build_pipeline
from database import init_db, init_users_table, create_user, verify_user
from market_overview import get_market_snapshot
from market_movers import get_movers
from news_agent import get_curated_news

app = FastAPI(title="Quantis API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = "change-this-to-something-random-and-secret"

init_db()
init_users_table()


class SignupRequest(BaseModel):
    name: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class AnalyzeRequest(BaseModel):
    ticker: str
    market: str


def create_token(email: str, name: str) -> str:
    payload = {
        "email": email,
        "name": name,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def verify_token(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.post("/api/signup")
def signup(req: SignupRequest):
    success, message = create_user(req.email, req.name, req.password)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message}


@app.post("/api/login")
def login(req: LoginRequest):
    success, result = verify_user(req.email, req.password)
    if not success:
        raise HTTPException(status_code=401, detail=result)
    token = create_token(req.email, result)
    return {"token": token, "name": result}


@app.get("/api/market-snapshot")
def market_snapshot():
    return get_market_snapshot()


@app.get("/api/market-movers")
def market_movers(market: str = "US"):
    gainers, losers = get_movers(market)
    return {"gainers": gainers, "losers": losers}


@app.get("/api/news")
def news():
    return get_curated_news()


@app.post("/api/analyze")
def analyze(req: AnalyzeRequest, user=Depends(verify_token)):
    ticker = req.ticker.strip().upper()
    if req.market == "India" and not ticker.endswith(".NS"):
        ticker = f"{ticker}.NS"

    pipeline_app = build_pipeline()
    result = pipeline_app.invoke({"ticker": ticker})

    if result.get("error"):
        raise HTTPException(status_code=400, detail=result["error"])

    return {
        "ticker": ticker,
        "currency": "₹" if req.market == "India" else "$",
        **result,
    }


@app.get("/api/price-history/{ticker}")
def price_history(ticker: str):
    from database import load_data
    df = load_data(ticker)
    if df.empty:
        raise HTTPException(status_code=404, detail="No data found for this ticker")
    return df.to_dict(orient="records")