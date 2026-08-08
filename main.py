from fastapi import FastAPI
from pytrends.request import TrendReq

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/trends/{keyword}")
def get_trends(keyword: str):
    pytrends = TrendReq(hl='fr-FR', tz=60)
    pytrends.build_payload([keyword], timeframe='today 3-m')
    data = pytrends.interest_over_time()
    if data.empty:
        return {"keyword": keyword, "trend_score": 0}
    return {"keyword": keyword, "trend_score": int(data[keyword].mean())}
