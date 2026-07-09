import asyncio
import random
import uuid
from datetime import datetime, timedelta, UTC
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import settings
from app.core.security import hash_password
from app.models.user import User
from app.models.prediction import Prediction
from app.models.model_version import ModelVersion

async def seed():
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        # Create a demo user
        user_id = uuid.uuid4()
        demo_user = User(
            id=user_id,
            email="demo@sentinel.app",
            full_name="Demo User",
            hashed_password=hash_password("password123"),
            role="user",
            is_active=True
        )
        session.add(demo_user)
        
        # Create a model version
        mv_id = uuid.uuid4()
        from datetime import date
        mv = ModelVersion(
            id=mv_id,
            version="1.0.0",
            algorithm="Logistic Regression",
            training_date=date(2026, 6, 1),
            training_samples=10000,
            accuracy=0.985,
            precision_spam=0.975,
            recall_spam=0.990,
            f1_spam=0.982,
            model_file_path="sentinel_v1.0.0.joblib",
            is_active=True
        )
        session.add(mv)

        spam_texts = [
            "URGENT: Your account has been suspended. Click here to verify your identity.",
            "You have won a $1000 Walmart gift card! Claim it now before it expires.",
            "Hot singles in your area want to meet you! Click the link below.",
            "Lose 10 pounds in 1 week with this miracle pill!",
            "Your package could not be delivered. Please pay the $2.99 shipping fee here.",
            "Congratulations! You've been selected for a free iPhone 15.",
            "Action Required: Update your billing information immediately to avoid service interruption.",
            "Get rich quick with this new cryptocurrency investment strategy."
        ]

        ham_texts = [
            "Hey, are we still on for lunch tomorrow?",
            "Please review the attached quarterly report and let me know your thoughts.",
            "Don't forget to pick up milk on your way home.",
            "Can you send me the presentation slides from yesterday's meeting?",
            "I'll be about 10 minutes late, traffic is terrible.",
            "Happy birthday! Hope you have a great day.",
            "The project deadline has been extended to next Friday.",
            "Thanks for your help with the bug fix, it works perfectly now."
        ]

        message_types = ["sms", "email", "text"]
        
        predictions = []
        now = datetime.now(UTC)
        
        # Generate 200 predictions over the last 30 days
        for i in range(200):
            is_spam = random.choice([True, False])
            
            if is_spam:
                text = random.choice(spam_texts)
                verdict = "SPAM"
                confidence = round(random.uniform(0.75, 0.99), 4)
                risk_level = "HIGH" if confidence > 0.9 else "MEDIUM"
                suspicious_tokens = [
                    {"token": "urgent", "weight": 0.8},
                    {"token": "click", "weight": 0.6},
                    {"token": "here", "weight": 0.4}
                ]
            else:
                text = random.choice(ham_texts)
                verdict = "HAM"
                confidence = round(random.uniform(0.75, 0.99), 4)
                risk_level = "LOW"
                suspicious_tokens = [
                    {"token": "lunch", "weight": 0.1},
                    {"token": "report", "weight": 0.05}
                ]

            days_ago = random.uniform(0, 30)
            created_at = now - timedelta(days=days_ago)
            
            p = Prediction(
                id=uuid.uuid4(),
                user_id=user_id,
                model_version_id=mv_id,
                original_text=text,
                processed_text=text.lower(),
                message_type=random.choice(message_types),
                verdict=verdict,
                confidence=confidence,
                risk_level=risk_level,
                explanation=f"The message was classified as {verdict} with {confidence*100:.2f}% confidence.",
                suspicious_tokens=suspicious_tokens,
                created_at=created_at
            )
            predictions.append(p)
            
        session.add_all(predictions)
        await session.commit()
        print(f"Successfully seeded {len(predictions)} predictions for user {demo_user.email}")

if __name__ == "__main__":
    asyncio.run(seed())
