from app import create_app
from models import db, Address

app = create_app()

with app.app_context():
    print("--- Database Diagnostics ---")
    
    # Check total count
    count = Address.query.count()
    print(f"Total Addresses in DB: {count}")
    
    # Check for the specific problem address
    problem_addr = '17HBG3fuchS7Kwsb5hb62nPi9r7J6m2coG'
    addr = Address.query.get(problem_addr)
    if addr:
        print(f"[FOUND] {problem_addr}: Category={addr.category}, Risk={addr.risk_score}")
    else:
        print(f"[MISSING] {problem_addr} not found in DB.")
        
        # Try finding similar
        similar = Address.query.filter(Address.id.ilike(f"%{problem_addr[:5]}%")).all()
        if similar:
            print(f"Found {len(similar)} similar addresses starting with {problem_addr[:5]}...")
            for s in similar:
                print(f" - {s.id}")
        else:
            print("No similar addresses found.")

    # Check recent entries
    print("\n--- Top 5 Recent Entries ---")
    recent = Address.query.order_by(Address.last_updated.desc()).limit(5).all()
    for r in recent:
        print(f"{r.id} | {r.category} | {r.risk_score}")
