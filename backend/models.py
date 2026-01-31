from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Address(db.Model):
    __tablename__ = 'addresses'
    id = db.Column(db.String(64), primary_key=True)  # The wallet address
    currency = db.Column(db.String(10), default='ETH')
    risk_score = db.Column(db.Float, default=0.0)
    category = db.Column(db.String(50), default='Unknown')
    label = db.Column(db.String(100), nullable=True)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Transaction analytics (from blockchain APIs)
    tx_count = db.Column(db.Integer, default=0)
    total_received_btc = db.Column(db.Float, default=0.0)
    total_sent_btc = db.Column(db.Float, default=0.0)
    wallet_balance = db.Column(db.Float, default=0.0)
    first_tx_date = db.Column(db.DateTime, nullable=True)
    last_tx_date = db.Column(db.DateTime, nullable=True)
    wallet_age_days = db.Column(db.Integer, default=0)
    
    # Behavioral flags
    is_mixer_pattern = db.Column(db.Boolean, default=False)
    is_high_volume = db.Column(db.Boolean, default=False)
    
    # Relationships
    outgoing_txs = db.relationship('Transaction', foreign_keys='Transaction.sender_addr', backref='sender', lazy=True)
    incoming_txs = db.relationship('Transaction', foreign_keys='Transaction.receiver_addr', backref='receiver', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'currency': self.currency,
            'risk_score': self.risk_score,
            'category': self.category,
            'label': self.label,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }

class Transaction(db.Model):
    __tablename__ = 'transactions'
    tx_hash = db.Column(db.String(64), primary_key=True)
    sender_addr = db.Column(db.String(64), db.ForeignKey('addresses.id'), nullable=False)
    receiver_addr = db.Column(db.String(64), db.ForeignKey('addresses.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'tx_hash': self.tx_hash,
            'sender': self.sender_addr,
            'receiver': self.receiver_addr,
            'amount': self.amount,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }


class ChainabuseCache(db.Model):
    """Permanent cache for Chainabuse API responses"""
    __tablename__ = 'chainabuse_cache'
    address = db.Column(db.String(64), primary_key=True)
    report_count = db.Column(db.Integer, default=0)
    categories = db.Column(db.Text)  # JSON string
    reports_data = db.Column(db.Text)  # JSON string
    highest_confidence = db.Column(db.Float, default=0.0)
    total_amount_lost = db.Column(db.Float, default=0.0)
    cached_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        import json
        return {
            'address': self.address,
            'report_count': self.report_count,
            'categories': json.loads(self.categories) if self.categories else [],
            'reports': json.loads(self.reports_data) if self.reports_data else [],
            'highest_confidence': self.highest_confidence,
            'total_amount_lost': self.total_amount_lost,
            'cached_at': self.cached_at.isoformat() if self.cached_at else None
        }
