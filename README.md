# Capafy Money Maker — SkillMarket API

A monetized AI skill listed on [skillmarket.space](https://skillmarket.space).

## How it works

Uses the **x402 payment protocol** on Solana. Each invocation costs **$0.01 USDC**.

## Invoke

```bash
# Without payment → returns 402 + payment instructions
curl https://your-app.onrender.com/api/capafy-money-maker?q=data+analysis

# With payment → returns results
curl -H "X-Payment: <solana_tx_sig>" \
  "https://your-app.onrender.com/api/capafy-money-maker?q=data+analysis"
```

## Deploy to Render

1. Fork this repo
2. Connect to [render.com](https://render.com)
3. Set env var `CAPAFY_ACCESS_TOKEN`
