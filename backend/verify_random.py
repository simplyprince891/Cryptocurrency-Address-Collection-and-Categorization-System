import csv
import random
from app import create_app
from models import db, Address

app = create_app()

def verify_samples():
    print("--- Verifying Random Dataset Samples ---")
    
    # 1. Pick 5 random rows from CSV
    samples = []
    try:
        with open('dataset.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            if not rows:
                print("Error: Dataset is empty.")
                return
            
            samples = random.sample(rows, 5)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    # 2. Check them in DB
    with app.app_context():
        success_count = 0
        for row in samples:
            # Replicate import logic for ID extraction
            clean_row = {k.strip().lower(): v.strip() for k, v in row.items() if k}
            addr_id = (
                clean_row.get('address') or 
                clean_row.get('wallet') or 
                clean_row.get('id') or 
                clean_row.get('wallet address') or
                clean_row.get('btc address') or
                clean_row.get('eth address') or
                clean_row.get('addr')
            )
            
            expected_category = clean_row.get('abuse_type_other') or 'Suspicious'
            
            print(f"\nChecking Address: {addr_id}")
            print(f"  Expected Category: {expected_category}")
            
            if not addr_id:
                print("  [SKIP] Could not extract address ID from row.")
                continue

            db_addr = Address.query.get(addr_id)
            if db_addr:
                print(f"  [FOUND] In DB.")
                print(f"  -> DB Category: {db_addr.category}")
                print(f"  -> DB Risk: {db_addr.risk_score}")
                success_count += 1
            else:
                # Try case insensitive
                db_addr = Address.query.filter(Address.id.ilike(addr_id)).first()
                if db_addr:
                    print(f"  [FOUND - Case Mismatch] In DB.")
                    print(f"  -> DB Category: {db_addr.category}")
                    success_count += 1
                else:
                    print(f"  [MISSING] Not found in DB!")

        print(f"\nSummary: {success_count}/5 addresses verified successfully.")

if __name__ == "__main__":
    verify_samples()
