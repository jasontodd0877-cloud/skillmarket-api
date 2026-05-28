from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import httpx, os, json
from datetime import datetime

app = FastAPI(title="Capafy Money Maker Skill API", version="1.0.0")

WALLET = "HhUQSph7Q5cM6C7EgwVuozp39ErZUud1E5CCdaYuRm26"
PRICE_USDC = 0.01
CAPAFY_API = "https://api.capafy.ai"
CAPAFY_TOKEN = os.getenv("CAPAFY_ACCESS_TOKEN", "")

# ─── Health ────────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {
        "skill": "Capafy Money Maker",
        "status": "live",
        "wallet": WALLET,
        "invoke": "/api/capafy-money-maker",
        "price": f"${PRICE_USDC} USDC per invocation"
    }

@app.get("/health")
def health():
    return {"status": "ok", "ts": datetime.utcnow().isoformat()}

# ─── x402 Payment Helper ───────────────────────────────────────────────────
def payment_required_response():
    return JSONResponse(
        status_code=402,
        content={
            "error": "Payment Required",
            "protocol": "x402",
            "price": f"${PRICE_USDC} USDC",
            "wallet": WALLET,
            "chain": "solana",
            "instructions": f"Send {PRICE_USDC} USDC to {WALLET} on Solana mainnet, then retry with header: X-Payment: <tx_signature>",
            "payTo": WALLET,
        }
    )

# ─── Core Skill Logic ──────────────────────────────────────────────────────
async def run_skill(query: str) -> dict:
    results = []
    error = None

    try:
        headers = {}
        if CAPAFY_TOKEN:
            headers["Authorization"] = f"Bearer {CAPAFY_TOKEN}"

        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                f"{CAPAFY_API}/agent/agents/search",
                json={"query": query, "page": 1, "pageSize": 5},
                headers=headers
            )
            if resp.status_code == 200:
                data = resp.json().get("data", {})
                items = data.get("list", []) if isinstance(data, dict) else []
                for item in items:
                    results.append({
                        "name": item.get("name", ""),
                        "description": item.get("desc", ""),
                        "rating": item.get("rating"),
                        "billing": item.get("billingMode", ""),
                        "agent_id": item.get("agentId", ""),
                        "url": f"https://capafy.ai/agent/{item.get('agentId','')}",
                    })
    except Exception as e:
        error = str(e)

    return {
        "skill": "Capafy Money Maker",
        "query": query,
        "results": results,
        "count": len(results),
        "error": error,
        "powered_by": "skillmarket.space",
        "wallet": WALLET,
        "ts": datetime.utcnow().isoformat()
    }

# ─── Skill Endpoint ────────────────────────────────────────────────────────
@app.get("/api/capafy-money-maker")
@app.post("/api/capafy-money-maker")
async def invoke_skill(request: Request, q: str = "AI automation agent"):
    # Check x402 payment header
    payment = request.headers.get("X-Payment") or request.headers.get("x-payment")

    if not payment:
        return payment_required_response()

    # Payment present → run the skill
    result = await run_skill(q)
    result["payment_tx"] = payment
    return JSONResponse(content=result)

# ─── Generic invoke endpoint (SkillMarket format) ──────────────────────────
@app.api_route("/api/{skill_id}", methods=["GET", "POST"])
async def invoke_any(skill_id: str, request: Request, q: str = "AI agent"):
    payment = request.headers.get("X-Payment") or request.headers.get("x-payment")
    if not payment:
        return payment_required_response()
    result = await run_skill(q)
    result["skill_id"] = skill_id
    result["payment_tx"] = payment
    return JSONResponse(content=result)
