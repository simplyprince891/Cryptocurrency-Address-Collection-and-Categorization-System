from flask import Blueprint, request, jsonify
from services.crypto_data import CryptoDataService
from services.address_classifier import get_classifier
from services.chainabuse import ChainabuseClient
from services.risk_engine import get_risk_engine
from models import db, Address
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()


api_bp = Blueprint('api', __name__)

@api_bp.route('/classify-address', methods=['POST'])
def classify_address():
    """
    Unified investigation endpoint
    
    Combines:
    - Chain detection and wallet classification
    - Local dataset lookup
    - Chainabuse API screening
    - Multi-source risk scoring
    """
    data = request.json
    address = data.get('address')
    
    if not address:
        return jsonify({"error": "No address provided"}), 400
    
    address = address.strip()
    
    try:
        # Initialize services with database session
        classifier = get_classifier()
        chainabuse_client = ChainabuseClient(db_session=db)
        risk_engine = get_risk_engine()
        
        # Step 1: Classify chain and wallet type
        print(f"[INFO] Classifying address: {address}")
        classification = classifier.classify(address)
        
        if not classification.is_valid:
            return jsonify({
                "error": "Invalid address format",
                "address": address
            }), 400
        
        # Step 2: Query local dataset
        print(f"[INFO] Querying local database...")
        db_address = Address.query.get(address)
        if not db_address:
            # Try case-insensitive
            db_address = Address.query.filter(Address.id.ilike(address)).first()
        
        dataset_info = None
        if db_address:
            dataset_info = {
                'category': db_address.category,
                'label': db_address.label,
                'risk_score': db_address.risk_score,
                'currency': db_address.currency
            }
        
        # Step 3: Query Chainabuse API (only if no local data)
        chainabuse_summary = None
        if db_address:
            # Local data exists - skip Chainabuse API to minimize calls
            print(f"[INFO] Local data found - skipping Chainabuse API (use cached if available)")
            # Still check cache for any previous Chainabuse data
            from models import ChainabuseCache
            cached_chainabuse = ChainabuseCache.query.get(address)
            if cached_chainabuse:
                chainabuse_summary = chainabuse_client._cached_to_summary(cached_chainabuse)
        else:
            # No local data - query Chainabuse
            print(f"[INFO] No local data - checking Chainabuse API...")
            chainabuse_summary = chainabuse_client.get_address_reports(address)
        
        chainabuse_info = None
        if chainabuse_summary:
            chainabuse_info = {
                'report_count': chainabuse_summary.report_count,
                'categories': chainabuse_summary.categories,
                'highest_confidence': chainabuse_summary.highest_confidence,
                'total_amount_lost': chainabuse_summary.total_amount_lost,
                'reports': [
                    {
                        'category': r.category,
                        'description': r.description,
                        'amount_lost': r.amount_lost,
                        'confidence': r.confidence
                    }
                    for r in chainabuse_summary.reports[:5]  # Limit to 5
                ]
            }
        
        # Step 4: Fetch transaction data from blockchain APIs (FREE)
        from services.blockchain_api import get_blockchain_service
        blockchain_service = get_blockchain_service()
        
        tx_data = None
        wallet_stats = blockchain_service.get_wallet_stats(address, classification.chain)
        if wallet_stats:
            tx_data = {
                'tx_count': wallet_stats.tx_count,
                'total_received': wallet_stats.total_received,
                'total_sent': wallet_stats.total_sent,
                'balance': wallet_stats.balance,
                'wallet_age_days': wallet_stats.wallet_age_days
            }
            print(f"[SUCCESS] TX data: {wallet_stats.tx_count} txs, {wallet_stats.wallet_age_days} days old")
        
        # Step 5: Calculate unified risk
        print(f"[INFO] Calculating risk score...")
        wallet_class_info = {
            'wallet_type': classification.wallet_type,
            'wallet_subtype': classification.wallet_subtype
        }
        
        risk_assessment = risk_engine.calculate_risk(
            address=address,
            dataset_info=dataset_info,
            chainabuse_info=chainabuse_info,
            wallet_classification=wallet_class_info,
            tx_data=tx_data  # NEW: Pass transaction data
        )
        
        # Step 5: Get transaction graph
        graph_data = CryptoDataService.get_address_graph(address)
        
        # Build comprehensive response
        result = {
            "address": address,
            "chain": classification.chain,
            "wallet_type": classification.wallet_type,
            "wallet_subtype": classification.wallet_subtype,
            "risk_level": risk_assessment.risk_level.value,
            "risk_score": risk_assessment.risk_score,
            "risk_reasoning": risk_assessment.reasoning,
            "dataset_reports": {
                "found": db_address is not None,
                "category": dataset_info['category'] if dataset_info else None,
                "label": dataset_info['label'] if dataset_info else None,
                "risk_score": dataset_info['risk_score'] if dataset_info else 0
            },
            "chainabuse_reports": chainabuse_info or {
                "report_count": 0,
                "categories": [],
                "reports": []
            },
            "transaction_graph": graph_data,
            "transaction_data": tx_data,  # NEW: Transaction metrics from blockchain APIs
            "sources": [
                {"name": "Local Dataset", "status": "checked"},
                {"name": "Chainabuse", "status": "checked" if chainabuse_client.is_configured() else "not_configured"},
                {"name": "Chain Classification", "status": "checked"}
            ]
        }
        
        print(f"[SUCCESS] Classification complete: {classification.chain}, Risk: {risk_assessment.risk_score}")
        
        return jsonify(result)
    
    except Exception as e:
        print(f"[ERROR] Classification failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Classification failed: {str(e)}"}), 500

@api_bp.route('/scan', methods=['POST'])

def scan_address():
    data = request.json
    address_id = data.get('address')
    
    if not address_id:
        return jsonify({"error": "No address provided"}), 400
        
    address_id = address_id.strip() # Sanitize input

    try:
        # Inspect (fetch + analyze)
        addr = CryptoDataService.inspect_address(address_id)
        return jsonify({
            "message": "Scan complete",
            "data": addr.to_dict()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/address/<address_id>', methods=['GET'])
def get_address_details(address_id):
    addr = Address.query.get(address_id)
    if not addr:
        return jsonify({"error": "Address not found"}), 404
    
    # Get graph data
    graph_data = CryptoDataService.get_address_graph(address_id)
    
    return jsonify({
        "details": addr.to_dict(),
        "graph": graph_data
    })

@api_bp.route('/recent', methods=['GET'])
def get_recent_scans():
    # 1. First trying to get recently UPDATED addresses (live reports)
    recent_addresses = Address.query.order_by(Address.last_updated.desc()).limit(10).all()
    
    # 2. If we have few results (e.g. fresh import), grab some high-risk ones to show value
    if len(recent_addresses) < 5:
        high_risk = Address.query.filter(Address.risk_score > 80).limit(10).all()
        # Merge lists, avoiding duplicates
        existing_ids = {a.id for a in recent_addresses}
        for hr in high_risk:
            if hr.id not in existing_ids:
                recent_addresses.append(hr)
    
    return jsonify([a.to_dict() for a in recent_addresses])

@api_bp.route('/report', methods=['POST'])
def report_address():
    data = request.json
    address_id = data.get('address')
    category = data.get('category', 'Suspicious')
    description = data.get('description')
    
    if not address_id:
        return jsonify({"error": "No address provided"}), 400
        
    # Check if exists
    addr = Address.query.get(address_id)
    if addr:
        # Update existing
        addr.category = category
        addr.risk_score = min(addr.risk_score + 20, 100) # Increase risk
        if description: 
            addr.label = description
        addr.last_updated = datetime.utcnow()
    else:
        # Create new
        addr = Address(
            id=address_id,
            category=category,
            risk_score=75.0, # Default high risk for user reports
            label=description,
            currency='ETH' if address_id.startswith('0x') else 'BTC'
        )
        db.session.add(addr)
    
    db.session.commit()
    return jsonify({"message": "Report submitted successfully", "data": addr.to_dict()})
