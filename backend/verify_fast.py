from app import create_app
from models import db, Address
import random

app = create_app()

with app.app_context():
    print("--- Verifying Imported Data ---")
    
    # Get total count
    count = Address.query.count()
    print(f"Total Addresses in DB: {count}")
    
    if count == 0:
        print("Database is empty!")
    else:
        # Fetch 5 sample addresses (limit/offset is slow for random, but fine for prototype)
        # We'll just grab the first 10 and pick 5 to show they aren't all the same
        print("\nSampling 5 random-ish addresses from DB...")
        
        # Get a few from the beginning
        rows = Address.query.limit(10).all()
        
        for r in rows[:5]:
            print(f"Address: {r.id}")
            print(f"  Category: {r.category}")
            print(f"  Risk Score: {r.risk_score}")
            print(f"  Label: {r.label}")
            print("-" * 30)
