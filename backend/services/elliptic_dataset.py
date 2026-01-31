"""
Elliptic Dataset Integration Service

Provides lookup and risk assessment for Bitcoin transactions
based on the Elliptic dataset (200K+ labeled transactions).

Dataset: https://www.kaggle.com/datasets/ellipticco/elliptic-data-set
- Classes: illicit (1), licit (2), unknown (3/unlabeled)
- Features: 166 behavioral features per transaction
- Edgelist: Transaction graph connections
"""

import pandas as pd
import os
from typing import Optional, Dict
from dataclasses import dataclass


@dataclass
class EllipticResult:
    """Elliptic dataset lookup result"""
    tx_id: str
    classification: str  # "illicit", "licit", or "unknown"
    risk_score: float  # 0-100
    confidence: float  # 0-1
    has_features: bool


class EllipticDatasetService:
    """
    Service for querying Elliptic dataset
    
    Loads data lazily to avoid memory issues (689MB features file)
    """
    
    def __init__(self, data_dir: str = "."):
        self.data_dir = data_dir
        self.classes_file = os.path.join(data_dir, "elliptic_txs_classes.csv")
        self.features_file = os.path.join(data_dir, "elliptic_txs_features.csv")
        self.edgelist_file = os.path.join(data_dir, "elliptic_txs_edgelist.csv")
        
        # Lazy loading - only load when needed
        self._classes_df = None
        self._feature_index = None
        
        print(f"[INFO] Elliptic dataset service initialized")
        self._check_files()
    
    def _check_files(self):
        """Check if dataset files exist"""
        if not os.path.exists(self.classes_file):
            print(f"[WARNING] Elliptic classes file not found: {self.classes_file}")
            return False
        if not os.path.exists(self.features_file):
            print(f"[WARNING] Elliptic features file not found: {self.features_file}")
            return False
        print(f"[SUCCESS] Elliptic dataset files found")
        return True
    
    def _load_classes(self):
        """Load transaction classes (small file, ~3MB)"""
        if self._classes_df is None:
            print("[INFO] Loading Elliptic classes (one-time load)...")
            try:
                # File format: txId,class
                self._classes_df = pd.read_csv(self.classes_file, header=None, names=['txId', 'class'])
                self._classes_df.set_index('txId', inplace=True)
                print(f"[SUCCESS] Loaded {len(self._classes_df)} transaction labels")
            except Exception as e:
                print(f"[ERROR] Failed to load Elliptic classes: {e}")
                self._classes_df = pd.DataFrame()
        
        return self._classes_df
    
    def lookup_transaction(self, tx_id: str) -> Optional[EllipticResult]:
        """
        Look up a Bitcoin transaction in the Elliptic dataset
        
        Args:
            tx_id: Transaction ID (as string or int)
        
        Returns:
            EllipticResult or None if not found
        """
        # Load classes
        classes_df = self._load_classes()
        if classes_df.empty:
            return None
        
        # Try to find transaction
        try:
            tx_id_int = int(tx_id) if isinstance(tx_id, str) and tx_id.isdigit() else tx_id
        except:
            return None
        
        if tx_id_int not in classes_df.index:
            return None
        
        # Get classification
        class_label = classes_df.loc[tx_id_int, 'class']
        
        if class_label == '1' or class_label == 1:
            classification = "illicit"
            risk_score = 95.0  # High risk
            confidence = 0.9
        elif class_label == '2' or class_label == 2:
            classification = "licit"
            risk_score = 5.0  # Very low risk
            confidence = 0.9
        else:
            classification = "unknown"
            risk_score = 50.0  # Neutral
            confidence = 0.3
        
        return EllipticResult(
            tx_id=str(tx_id_int),
            classification=classification,
            risk_score=risk_score,
            confidence=confidence,
            has_features=True  # All transactions in classes have features
        )
    
    def get_stats(self) -> Dict:
        """Get dataset statistics"""
        classes_df = self._load_classes()
        if classes_df.empty:
            return {}
        
        stats = {
            'total_transactions': len(classes_df),
            'illicit_count': len(classes_df[classes_df['class'].isin([1, '1'])]),
            'licit_count': len(classes_df[classes_df['class'].isin([2, '2'])]),
            'unknown_count': len(classes_df[~classes_df['class'].isin([1, '1', 2, '2'])])
        }
        
        return stats


# Singleton instance
_elliptic_service = None


def get_elliptic_service() -> EllipticDatasetService:
    """Get singleton Elliptic dataset service"""
    global _elliptic_service
    if _elliptic_service is None:
        _elliptic_service = EllipticDatasetService()
    return _elliptic_service


# Quick test
if __name__ == "__main__":
    service = get_elliptic_service()
    stats = service.get_stats()
    print(f"\nElliptic Dataset Stats:")
    print(f"  Total: {stats.get('total_transactions', 0):,}")
    print(f"  Illicit: {stats.get('illicit_count', 0):,}")
    print(f"  Licit: {stats.get('licit_count', 0):,}")
    print(f"  Unknown: {stats.get('unknown_count', 0):,}")
