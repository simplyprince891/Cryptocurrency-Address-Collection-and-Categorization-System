import csv
import sys
from app import create_app
from models import db, Address
from datetime import datetime

def import_csv(file_path):
    app = create_app()
    with app.app_context():
        # Log database location for debugging
        db_path = app.config['SQLALCHEMY_DATABASE_URI']
        print(f"[INFO] Using database: {db_path}")
        print(f"[INFO] Importing from {file_path}...")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                # Read header to debug
                headers = reader.fieldnames
                print(f"[INFO] Detected columns: {headers}")
                
                count = 0
                updated_count = 0
                skipped_count = 0
                for row in reader:
                    # Normalize keys (handle potential case variants or BOM)
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
                    
                    if not addr_id:
                        skipped_count += 1
                        continue
                        
                    category = (
                        clean_row.get('category') or 
                        clean_row.get('type') or 
                        clean_row.get('classification') or
                        clean_row.get('abuse_type_other') or  # Added for user dataset
                        'Suspicious'
                    )
                    
                    label = (
                        clean_row.get('label') or 
                        clean_row.get('tag') or 
                        clean_row.get('name') or 
                        clean_row.get('description') or
                        clean_row.get('entity') or
                        clean_row.get('abuser')  # Added for user dataset
                    )

                    risk_str = (
                        clean_row.get('risk') or 
                        clean_row.get('score') or 
                        clean_row.get('risk_score') or 
                        clean_row.get('risk level')
                    )
                    
                    # Infer risk from category/abuse type if no explicit risk score
                    if not risk_str:
                        cat_lower = str(category).lower()
                        if any(x in cat_lower for x in ['ransomware', 'blackmail', 'extortion', 'stolen', 'hack', 'darknet']):
                            risk_score = 100.0
                        elif any(x in cat_lower for x in ['scam', 'fraud', 'phishing', 'theft']):
                            risk_score = 90.0
                        elif any(x in cat_lower for x in ['mixer', 'laundering']):
                            risk_score = 80.0
                        elif any(x in cat_lower for x in ['suspicious', 'unsafe']):
                            risk_score = 60.0
                        else:
                            risk_score = 50.0 # Default for unknown abuse types
                    else:
                        try:
                            # Handle strings like "High", "Critical"
                            if isinstance(risk_str, str) and not risk_str.replace('.','').isdigit():
                                if 'high' in risk_str.lower() or 'critical' in risk_str.lower():
                                    risk_score = 90.0
                                elif 'medium' in risk_str.lower():
                                    risk_score = 50.0
                                elif 'low' in risk_str.lower():
                                    risk_score = 10.0
                                else:
                                    risk_score = 50.0
                            else:
                                risk_score = float(risk_str)
                        except ValueError:
                            risk_score = 50.0

                    # Check if exists (deduplication)
                    existing = Address.query.get(addr_id)
                    if existing:
                        # Update existing record with new data
                        existing.label = label
                        existing.category = category
                        existing.risk_score = risk_score
                        existing.last_updated = datetime.utcnow()
                        updated_count += 1
                    else:
                        # Create new record
                        new_addr = Address(
                            id=addr_id,
                            label=label,
                            category=category,
                            risk_score=risk_score,
                            currency='ETH' if addr_id.startswith('0x') else 'BTC'
                        )
                        db.session.add(new_addr)
                    
                    count += 1
                    
                    # Commit in batches for better performance
                    if count % 500 == 0:
                        db.session.commit()
                        print(f"[PROGRESS] Processed {count} records (New: {count - updated_count}, Updated: {updated_count}, Skipped: {skipped_count})")
                        
                # Final commit
                db.session.commit()
                
                # Summary statistics
                new_count = count - updated_count
                print(f"\n[SUCCESS] Import completed:")
                print(f"  Total processed: {count}")
                print(f"  New addresses: {new_count}")
                print(f"  Updated addresses: {updated_count}")
                print(f"  Skipped (no address): {skipped_count}")
                
        except FileNotFoundError:
            print(f"[ERROR] File not found: {file_path}")
        except Exception as e:
            print(f"[ERROR] Import failed: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python import_data.py <path_to_csv>")
        print("Example: python import_data.py dataset.csv")
    else:
        import_csv(sys.argv[1])
