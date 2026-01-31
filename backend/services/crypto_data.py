import random
from models import db, Address, Transaction
from datetime import datetime, timedelta

class CryptoDataService:
    """
    Service to handle interaction with Blockchain APIs (Mocked for Prototype)
    and performed basic analysis.
    """

    @staticmethod
    def inspect_address(address_id):
        """
        Check if address exists in DB. If not, 'fetch' it (mock) and analyze.
        """
        address_id = address_id.strip()
        
        # 1. Try exact match
        addr = Address.query.get(address_id)
        
        # 2. Try case-insensitive match (common issue with hex vs Base58)
        if not addr:
            addr = Address.query.filter(Address.id.ilike(address_id)).first()

        if not addr:
            addr = CryptoDataService._fetch_mock_address_data(address_id)
            db.session.add(addr)
            db.session.commit()
            
            # Generate mock transactions for this new address
            CryptoDataService._generate_mock_transactions(addr)
        
        return addr

    @staticmethod
    def _fetch_mock_address_data(address_id):
        """
        Simulate fetching data from an external API like Etherscan.
        """
        # ONLY mock specific demo addresses if needed, otherwise return Unknown
        
        category = "Unknown"
        risk_score = 0.0
        label = "Not found in database"

        # Keep these strictly for the "Demo" capability if the user wants to test it
        if address_id.startswith("0xBad"): 
            category = "Ransomware"
            risk_score = 95.0
            label = "WannaCry Related (Demo)"
        elif address_id.startswith("0xMix"):
            category = "Mixer"
            risk_score = 80.0
            label = "Tornado Cash (Demo)"
        elif address_id.startswith("0xEx"):
            category = "Exchange"
            risk_score = 5.0
            label = "Binance Hot Wallet (Demo)"
        
        # If it's a real address not in our DB, we shouldn't guess it's a "Personal Wallet"
        # We should flag it as unknown/clean for now.
        
        new_address = Address(
            id=address_id,
            currency="ETH" if address_id.startswith("0x") else "BTC",
            category=category,
            risk_score=risk_score,
            label=label
        )
        return new_address

    @staticmethod
    def _generate_mock_transactions(address):
        """
        Generate random mock transactions for the graph.
        """
        num_txs = random.randint(5, 15)
        for i in range(num_txs):
            is_incoming = random.choice([True, False])
            other_addr = f"0x{random.randint(100000, 999999)}abc"
            
            if is_incoming:
                sender = other_addr
                receiver = address.id
                # ensure sender 'address' stub exists for foreign key constraints locally
                # In a real app we might not strictly enforce FK for all external addrs or valid them
                # For this prototype we will just create the stub wallet if it doesn't exist
                CryptoDataService._ensure_stub_address(sender)
            else:
                sender = address.id
                receiver = other_addr
                CryptoDataService._ensure_stub_address(receiver)

            tx = Transaction(
                tx_hash=f"0x{random.randint(10000000, 99999999)}",
                sender_addr=sender,
                receiver_addr=receiver,
                amount=round(random.uniform(0.1, 10.0), 4),
                timestamp=datetime.utcnow() - timedelta(days=random.randint(0, 30))
            )
            db.session.add(tx)
        
        db.session.commit()

    @staticmethod
    def _ensure_stub_address(address_id):
        if not Address.query.get(address_id):
            stub = Address(id=address_id, category="Unknown")
            db.session.add(stub)
            # db.session.commit() # Commit handled by caller for meaningful batching usually

    @staticmethod
    def get_address_graph(address_id):
        """
        Build a node-link structure for the frontend graph.
        """
        addr = Address.query.get(address_id)
        if not addr:
            return None
        
        nodes = {}
        links = []

        # Add central node
        nodes[addr.id] = {"id": addr.id, "group": addr.category, "risk": addr.risk_score}

        # Process transactions (Incoming)
        for tx in addr.incoming_txs:
            sender = tx.sender
            nodes[sender.id] = {"id": sender.id, "group": sender.category, "risk": sender.risk_score}
            links.append({"source": sender.id, "target": addr.id, "amount": tx.amount, "hash": tx.tx_hash})

        # Process transactions (Outgoing)
        for tx in addr.outgoing_txs:
            receiver = tx.receiver
            nodes[receiver.id] = {"id": receiver.id, "group": receiver.category, "risk": receiver.risk_score}
            links.append({"source": addr.id, "target": receiver.id, "amount": tx.amount, "hash": tx.tx_hash})

        return {
            "nodes": list(nodes.values()),
            "links": links
        }
