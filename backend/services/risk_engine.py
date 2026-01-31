"""
Unified Risk Engine

Combines multiple data sources to calculate comprehensive risk scores:
- Local dataset intelligence
- Chainabuse reports
- Wallet type classification
"""

from dataclasses import dataclass
from typing import Optional, List
from enum import Enum


class RiskLevel(Enum):
    """Risk level categories"""
    NONE = "NONE"  # 0-20
    LOW = "LOW"  # 21-50
    MEDIUM = "MEDIUM"  # 51-80
    HIGH = "HIGH"  # 81-100


@dataclass
class UnifiedRiskAssessment:
    """Complete risk assessment result"""
    address: str
    risk_score: float  # 0-100
    risk_level: RiskLevel
    reasoning: List[str]  # Human-readable reasons
    dataset_risk: float
    chainabuse_risk: float
    wallet_type_risk: float


class RiskEngine:
    """Calculate unified risk scores from multiple sources"""
    
    # Risk weights for different sources (UPDATED for free APIs)
    DATASET_WEIGHT = 0.45       # Local dataset (free)
    CHAINABUSE_WEIGHT = 0.15    # Chainabuse (bonus, but not primary)
    WALLET_TYPE_WEIGHT = 0.10   # Wallet classification (free)
    BEHAVIORAL_WEIGHT = 0.30    # Transaction behavior (free APIs) - NEW!
    
    # Category-based risk mappings
    HIGH_RISK_CATEGORIES = [
        'ransomware', 'blackmail', 'extortion', 'stolen', 'hack',
        'darknet', 'terrorism', 'child abuse', 'murder for hire',
        'sextortion', 'threatening', 'threat', 'kidnap', 'ransom'
    ]
    
    MEDIUM_HIGH_CATEGORIES = [
        'scam', 'fraud', 'phishing', 'theft', 'ponzi', 'pyramid'
    ]
    
    MEDIUM_CATEGORIES = [
        'mixer', 'tumbler', 'laundering', 'gambling', 'sanctions'
    ]
    
    def calculate_risk(
        self,
        address: str,
        dataset_info: Optional[dict] = None,
        chainabuse_info: Optional[dict] = None,
        wallet_classification: Optional[dict] = None,
        tx_data: Optional[dict] = None  # NEW: Transaction data from blockchain APIs
    ) -> UnifiedRiskAssessment:
        """
        Calculate unified risk score
        
        Args:
            address: The address being assessed
            dataset_info: Local dataset information (category, risk_score)
            chainabuse_info: Chainabuse report summary
            wallet_classification: Wallet type classification result
            
        Returns:
            UnifiedRiskAssessment with final score and reasoning
        """
        reasoning = []
        
        # Calculate individual risk components
        dataset_risk = self._calculate_dataset_risk(dataset_info, reasoning)
        chainabuse_risk = self._calculate_chainabuse_risk(chainabuse_info, reasoning)
        wallet_type_risk = self._calculate_wallet_type_risk(wallet_classification, reasoning)
        behavioral_risk = self._calculate_behavioral_risk(tx_data, reasoning)  # NEW
        
        # SMART WEIGHTING: Normalize weights based on available data sources
        # This ensures dataset threats are scored properly even without transaction data
        available_sources = []
        if dataset_risk > 0:
            available_sources.append(('dataset', dataset_risk, self.DATASET_WEIGHT))
        if chainabuse_risk > 0:
            available_sources.append(('chainabuse', chainabuse_risk, self.CHAINABUSE_WEIGHT))
        if wallet_type_risk > 0:
            available_sources.append(('wallet', wallet_type_risk, self.WALLET_TYPE_WEIGHT))
        if behavioral_risk > 0:
            available_sources.append(('behavioral', behavioral_risk, self.BEHAVIORAL_WEIGHT))
        
        # If we only have dataset data (no tx data), give it full weight
        if len(available_sources) == 1 and available_sources[0][0] == 'dataset':
            final_score = dataset_risk
            reasoning.insert(0, "⚠️ Risk based solely on dataset (no transaction data available)")
        else:
            # Weighted combination with normalization
            total_weight = sum(w for _, _, w in available_sources)
            final_score = sum(risk * (weight / total_weight) for _, risk, weight in available_sources)
        
        # Boost score if multiple sources agree on high risk
        if dataset_risk > 70 and behavioral_risk > 60:
            final_score = min(100, final_score * 1.15)
            reasoning.append("⚠️ Dataset and behavioral patterns both indicate high risk")
        elif dataset_risk > 70 and chainabuse_risk > 70:
            final_score = min(100, final_score * 1.2)
            reasoning.append("⚠️ Multiple sources confirm high risk")
        
        # Determine risk level
        risk_level = self._score_to_level(final_score)
        
        if not reasoning:
            reasoning.append("No significant risk indicators found")
        
        return UnifiedRiskAssessment(
            address=address,
            risk_score=round(final_score, 1),
            risk_level=risk_level,
            reasoning=reasoning,
            dataset_risk=dataset_risk,
            chainabuse_risk=chainabuse_risk,
            wallet_type_risk=wallet_type_risk
        )
    
    def _calculate_dataset_risk(self, dataset_info: Optional[dict], reasoning: List[str]) -> float:
        """Calculate risk from local dataset"""
        if not dataset_info:
            return 0.0
        
        # Get stored risk score
        risk_score = dataset_info.get('risk_score', 0.0)
        category = dataset_info.get('category', '').lower()
        label = dataset_info.get('label', '').lower()  # Also check label field
        
        # Combine category and label for comprehensive keyword matching
        combined_text = f"{category} {label}"
        
        # Check for critical threats in BOTH category and label
        if any(cat in combined_text for cat in self.HIGH_RISK_CATEGORIES):
            risk_score = 100.0  # Override to maximum for critical threats
            # Find which keyword matched
            matched = next((cat for cat in self.HIGH_RISK_CATEGORIES if cat in combined_text), 'critical threat')
            reasoning.append(f"🔴 Dataset: Identified as '{matched}' - CRITICAL RISK")
        
        elif any(cat in combined_text for cat in self.MEDIUM_HIGH_CATEGORIES):
            risk_score = max(risk_score, 90.0)  # Ensure minimum 90 for scams/fraud
            matched = next((cat in combined_text for cat in self.MEDIUM_HIGH_CATEGORIES if cat in combined_text), 'scam')
            reasoning.append(f"🟠 Dataset: Contains '{matched}' indicators - HIGH RISK")
        
        elif any(cat in combined_text for cat in self.MEDIUM_CATEGORIES):
            risk_score = max(risk_score, 75.0)
            reasoning.append(f"🟡 Dataset: {dataset_info.get('category', 'Suspicious')} activity detected")
        
        elif risk_score > 50:
            reasoning.append(f"⚠️ Dataset: Risk score {risk_score}/100")
        
        elif dataset_info.get('category') or dataset_info.get('label'):
            # Has data but no specific risk category
            risk_score = max(risk_score, 40.0)
            reasoning.append(f"⚠️ Dataset: Flagged as {dataset_info.get('category', 'Suspicious')}")
        
        return risk_score
    
    def _calculate_chainabuse_risk(self, chainabuse_info: Optional[dict], reasoning: List[str]) -> float:
        """Calculate risk from Chainabuse reports"""
        if not chainabuse_info or not chainabuse_info.get('report_count'):
            return 0.0
        
        report_count = chainabuse_info['report_count']
        confidence = chainabuse_info.get('highest_confidence', 0.5)
        categories = chainabuse_info.get('categories', [])
        
        # Base risk from report count
        if report_count >= 10:
            base_risk = 100.0
        elif report_count >= 5:
            base_risk = 90.0
        elif report_count >= 2:
            base_risk = 70.0
        else:
            base_risk = 50.0
        
        # Adjust by confidence
        risk_score = base_risk * confidence
        
        # Add reasoning
        if report_count > 0:
            cat_text = ', '.join(categories[:3]) if categories else 'abuse'
            reasoning.append(f"🚨 Chainabuse: {report_count} report(s) for {cat_text}")
        
        return risk_score
    
    def _calculate_wallet_type_risk(self, classification: Optional[dict], reasoning: List[str]) -> float:
        """Calculate risk from wallet type"""
        if not classification:
            return 0.0
        
        wallet_type = classification.get('wallet_type', '')
        wallet_subtype = classification.get('wallet_subtype', '')
        
        risk_score = 0.0
        
        # Contract-based risk
        if wallet_type == 'Contract':
            if wallet_subtype == 'mixer':
                risk_score = 80.0
                reasoning.append("⚠️ Identified as mixer contract")
            elif wallet_subtype in ['defi_protocol', 'bridge']:
                risk_score = 20.0
                # Don't add reasoning for legitimate protocols
        
        # Exchange wallets are generally lower risk
        elif wallet_subtype == 'exchange':
            risk_score = 10.0
            reasoning.append("ℹ️ Exchange wallet (typically lower risk)")
        
        return risk_score
    
    def _calculate_behavioral_risk(self, tx_data: Optional[dict], reasoning: List[str]) -> float:
        """
        Calculate risk from transaction patterns (FREE blockchain API data)
        
        Args:
            tx_data: Transaction stats (tx_count, wallet_age_days, total_received, etc.)
        
        Returns:
            Risk score 0-100
        """
        if not tx_data:
            return 0.0
        
        risk = 0.0
        
        # High transaction volume = potential mixer/tumbler
        tx_count = tx_data.get('tx_count', 0)
        if tx_count > 10000:
            risk += 40
            reasoning.append("🚨 Extremely high transaction volume (>10K txs) - likely mixer/exchange")
        elif tx_count > 5000:
            risk += 30
            reasoning.append("⚠️ Very high transaction volume (>5K txs)")
        elif tx_count > 1000:
            risk += 15
            reasoning.append("📊 High transaction volume (>1K txs)")
        
        # Young wallet with high value = potential fraud
        wallet_age = tx_data.get('wallet_age_days', 999)
        total_received = tx_data.get('total_received', 0)
        
        if wallet_age < 30 and total_received > 10:
            risk += 35
            reasoning.append("🔴 New wallet (<30 days) with high volume (>10 BTC/ETH) - RED FLAG")
        elif wallet_age < 90 and total_received > 50:
            risk += 25
            reasoning.append("⚠️ Recently created wallet with significant volume")
        
        # Mixing pattern (many small transactions)
        if tx_count > 100:
            avg_tx_size = total_received / tx_count if tx_count > 0 else 0
            if avg_tx_size < 0.1:
                risk += 25
                reasoning.append("⚠️ Mixing pattern detected (many small transactions)")
        
        # High throughput with low balance = tumbler
        balance = tx_data.get('balance', 0)
        total_sent = tx_data.get('total_sent', 0)
        
        if total_received > 100 and total_sent > 100 and balance < 1:
            risk += 20
            reasoning.append("📉 High throughput, low balance - possible tumbler/mixer")
        
        # Emptied wallet after receiving funds = exit scam
        if total_received > 10 and balance < 0.01 and wallet_age < 180:
            risk += 15
            reasoning.append("⚠️ Emptied wallet after receiving funds - exit scam pattern")
        
        return min(risk, 100.0)
    
    def _score_to_level(self, score: float) -> RiskLevel:
        """Convert numeric score to risk level"""
        if score >= 81:
            return RiskLevel.HIGH
        elif score >= 51:
            return RiskLevel.MEDIUM
        elif score >= 21:
            return RiskLevel.LOW
        else:
            return RiskLevel.NONE


# Singleton instance
_engine_instance = None


def get_risk_engine() -> RiskEngine:
    """Get singleton risk engine instance"""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = RiskEngine()
    return _engine_instance
