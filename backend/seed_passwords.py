# backend/seed_passwords.py

from app.db.session import SessionLocal
from app.models.entities import User
from app.core.security import hash_password

def seed():
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.email == "admin@telecom.com").first()
        subscriber = db.query(User).filter(User.email == "subscriber@telecom.com").first()

        if admin:
            admin.password_hash = hash_password("AdminPassword123!")
            print(f"Admin hash updated: {admin.password_hash[:35]}...")
        else:
            print("Admin user not found in database!")

        if subscriber:
            subscriber.password_hash = hash_password("UserPassword123!")
            print(f"Subscriber hash updated: {subscriber.password_hash[:35]}...")
        else:
            print("Subscriber user not found in database!")

        db.commit()
        print("Database password hashes updated successfully!")
    except Exception as e:
        db.rollback()
        print(f"Error during update: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed()