from fastapi import FastAPI
from pytrends.request import TrendReq
from playwright.async_api import async_playwright

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


@app.get("/aliexpress-search")
async def search_aliexpress(query: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        url = f"https://www.aliexpress.com/wholesale?SearchText={query}"
        results = []
        try:
            await page.goto(url, timeout=30000)
            await page.wait_for_timeout(3000)
            items = await page.query_selector_all("a[href*='/item/']")
            seen_titles = set()
            for item in items[:30]:
                title = await item.get_attribute("title")
                href = await item.get_attribute("href")
                if title and title not in seen_titles:
                    seen_titles.add(title)
                    results.append({"title": title, "url": href})
                if len(results) >= 10:
                    break
        except Exception:
            results = []
        finally:
            await browser.close()
        return {"source": "aliexpress", "query": query, "count": len(results), "items": results}


@app.get("/tiktok-trends")
async def get_tiktok_trends():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        results = []
        try:
            await page.goto(
                "https://ads.tiktok.com/business/creativecenter/inspiration/popular/hashtag/pc/fr",
                timeout=30000
            )
            await page.wait_for_timeout(4000)
            cards = await page.query_selector_all(".CardPc_container")
            for card in cards[:20]:
                text = await card.inner_text()
                results.append(text)
        except Exception:
            results = []
        finally:
            await browser.close()
        return {"source": "tiktok", "count": len(results), "raw_items": results}
