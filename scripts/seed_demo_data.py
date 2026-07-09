import asyncio
import os
import random
import sys
from datetime import UTC, datetime, timedelta

# Add backend to PYTHONPATH so we can import app modules directly
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

import httpx
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings

API_BASE = "http://localhost:8000/api/v1"
EMAIL = "demo_api@sentinel.app"
PASSWORD = "Password123!"
FULL_NAME = "API Demo User"

# Realistic texts to generate predictions for
SPAM_TEXTS = [
    "URGENT: Your account has been suspended. Click here to verify your identity.",
    "You have won a $1000 Walmart gift card! Claim it now before it expires.",
    "Hot singles in your area want to meet you! Click the link below.",
    "Lose 10 pounds in 1 week with this miracle pill!",
    "Your package could not be delivered. Please pay the $2.99 shipping fee here.",
    "Congratulations! You've been selected for a free iPhone 15.",
    "Action Required: Update your billing information immediately to avoid service interruption.",
    "Get rich quick with this new cryptocurrency investment strategy.",
    "This is a final notice regarding your car's extended warranty.",
    "You have a pending refund of $450. Click here to claim your money.",
    "Dear customer, your bank account is compromised. Call 1-800-SPAM now."
]

HAM_TEXTS = [
    "Hey, are we still on for lunch tomorrow?",
    "Please review the attached quarterly report and let me know your thoughts.",
    "Don't forget to pick up milk on your way home.",
    "Can you send me the presentation slides from yesterday's meeting?",
    "I'll be about 10 minutes late, traffic is terrible.",
    "Happy birthday! Hope you have a great day.",
    "The project deadline has been extended to next Friday.",
    "Thanks for your help with the bug fix, it works perfectly now.",
    "Could we reschedule our 1-on-1 to Thursday afternoon?",
    "I have reviewed the PR. It looks good to me, feel free to merge.",
    "Let me know if you need anything else from my end."
]

async def seed_data():
    print(f"Connecting to API at {API_BASE}...")
    async with httpx.AsyncClient(base_url=API_BASE, timeout=30.0) as client:
        # 1. Register or Login
        print("Authenticating user...")
        register_resp = await client.post("/auth/register", json={
            "email": EMAIL,
            "password": PASSWORD,
            "full_name": FULL_NAME
        })
        
        if register_resp.status_code >= 400:
            print("User might already exist (or registration failed), attempting login...")
        else:
            print("Successfully registered demo user.")
            
        login_resp = await client.post("/auth/login", json={
            "email": EMAIL,
            "password": PASSWORD
        })
        
        if login_resp.status_code != 200:
            print(f"Failed to login: {login_resp.text}")
            return
            
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 2. Generate predictions
        num_predictions = random.randint(150, 300)
        print(f"Generating {num_predictions} predictions using the real API...")
        
        prediction_ids = []
        for i in range(num_predictions):
            is_spam = random.choice([True, False])
            text_val = random.choice(SPAM_TEXTS) if is_spam else random.choice(HAM_TEXTS)
            
            # Add some slight variation so they aren't all identical
            text_val += f" [Ref: {random.randint(1000, 9999)}]"
            
            msg_type = random.choice(["sms", "email", "text"])
            
            # Spoof IP to bypass IP-based rate limiting during demo seeding
            current_ip = f"192.168.1.{random.randint(1, 254)}"
            req_headers = {**headers, "X-Forwarded-For": current_ip}
            
            resp = await client.post("/predict", json={
                "text": text_val,
                "message_type": msg_type
            }, headers=req_headers)
            
            if resp.status_code == 200:
                data = resp.json()
                prediction_ids.append(data["prediction_id"])
            elif resp.status_code == 429:
                print("Rate limit hit, waiting 2 seconds...")
                await asyncio.sleep(2)
                # Retry once
                resp = await client.post("/predict", json={
                    "text": text_val,
                    "message_type": msg_type
                }, headers=req_headers)
                if resp.status_code == 200:
                    data = resp.json()
                    prediction_ids.append(data["prediction_id"])
            else:
                print(f"Warning: Failed to predict ({resp.status_code}): {resp.text}")
                
            if (i + 1) % 25 == 0:
                print(f"Created {i + 1}/{num_predictions} predictions...")
                
        print(f"Successfully created {len(prediction_ids)} predictions.")
        
        # 3. Backdate timestamps in DB
        if prediction_ids:
            print("Backdating timestamps in the database to span the last 30 days...")
            engine = create_async_engine(settings.DATABASE_URL)
            async with engine.begin() as conn:
                now = datetime.now(UTC)
                for pid in prediction_ids:
                    days_ago = random.uniform(0, 30)
                    random_date = now - timedelta(days=days_ago)
                    
                    await conn.execute(
                        text("UPDATE predictions SET created_at = :ts WHERE id = :id"),
                        {"ts": random_date, "id": pid}
                    )
            print("Successfully backdated timestamps.")
            
        print("Demo data generation complete!")

if __name__ == "__main__":
    asyncio.run(seed_data())
