import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
from typing import Any, Dict

from database import db, create_document, get_documents
from schemas import Message, AnalyticsEvent, CheckoutSessionRequest

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Ascendia API running"}

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response: Dict[str, Any] = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = os.getenv("DATABASE_NAME") or "❌ Not Set"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"

    return response

# Contact form endpoint - stores messages to database
@app.post("/api/contact")
async def create_message(payload: Dict[str, Any]):
    try:
        message = Message(**payload)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())

    try:
        inserted_id = create_document("message", message)
        return {"status": "ok", "id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Analytics endpoint
@app.post("/api/analytics")
async def analytics_event(payload: Dict[str, Any]):
    try:
        event = AnalyticsEvent(**payload)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())

    try:
        inserted_id = create_document("analyticsevent", event)
        return {"status": "ok", "id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Stripe checkout session creation (mock-ready)
# If STRIPE_SECRET is provided, we create a real session; otherwise we return a mock URL
@app.post("/api/checkout")
async def create_checkout_session(payload: Dict[str, Any]):
    try:
        data = CheckoutSessionRequest(**payload)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())

    stripe_secret = os.getenv("STRIPE_SECRET")
    if not stripe_secret:
        # Mock mode
        return {
            "status": "mock",
            "checkout_url": f"{data.success_url}?mock_session=1",
        }

    try:
        import stripe
        stripe.api_key = stripe_secret
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": data.currency,
                        "product_data": {"name": data.course_name or "Ascendia Course"},
                        "unit_amount": data.amount_cents,
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=data.success_url,
            cancel_url=data.cancel_url,
        )
        return {"status": "ok", "id": session.id, "checkout_url": session.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
