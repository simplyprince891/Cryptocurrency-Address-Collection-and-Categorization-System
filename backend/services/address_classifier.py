"""
Address Classification Service

Provides chain detection and wallet type classification for cryptocurrency addresses.
Supports: Bitcoin, Ethereum, Polygon, BSC, Solana, Tron, and other EVM chains.
"""

import re
from dataclasses import dataclass
from typing import Optional, Tuple
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


@dataclass
class AddressClassificationResult:
    """Result of address classification"""
    address: str
    chain: str
    is_valid: bool
    wallet_type: Optional[str] = None  # 'EOA', 'Contract', 'Unknown'
    wallet_subtype: Optional[str] = None  # 'Exchange', 'Mixer', 'Protocol', etc.
    confidence: float = 1.0


class AddressClassifier:
    """Classifies cryptocurrency addresses by chain and type"""
    
    # Chain detection patterns
    CHAIN_PATTERNS = {
        'bitcoin': r'^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$|^bc1[a-z0-9]{39,59}$',
        'ethereum': r'^0x[a-fA-F0-9]{40}$',
        'solana': r'^[1-9A-HJ-NP-Za-km-z]{32,44}$',
        'tron': r'^T[A-Za-z1-9]{33}$',
    }
    
    # EVM chains share Ethereum address format
    EVM_CHAINS = ['ethereum', 'polygon', 'bsc', 'arbitrum', 'optimism', 'avalanche']
    
    # Known contract patterns (heuristics)
    KNOWN_PATTERNS = {
        'mixer': ['tornado', 'mixer', 'tumbler', 'blender'],
        'exchange': ['binance', 'coinbase', 'kraken', 'bitfinex', 'huobi'],
        'bridge': ['bridge', 'portal', 'wormhole', 'multichain'],
        'defi_protocol': ['uniswap', 'aave', 'compound', 'curve', 'sushiswap']
    }
    
    # Default RPC endpoints (can be overridden)
    DEFAULT_RPC_ENDPOINTS = {
        'ethereum': 'https://eth.llamarpc.com',
        'polygon': 'https://polygon-rpc.com',
        'bsc': 'https://bsc-dataseed.binance.org/',
        'arbitrum': 'https://arb1.arbitrum.io/rpc',
        'optimism': 'https://mainnet.optimism.io',
    }
    
    def __init__(self, rpc_endpoints: Optional[dict] = None):
        """
        Initialize classifier
        
        Args:
            rpc_endpoints: Custom RPC endpoints for EVM chains
        """
        self.rpc_endpoints = rpc_endpoints or self.DEFAULT_RPC_ENDPOINTS
        
        # Setup HTTP session with retries
        self.session = requests.Session()
        retry_strategy = Retry(
            total=2,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def classify(self, address: str, label: Optional[str] = None) -> AddressClassificationResult:
        """
        Classify a cryptocurrency address
        
        Args:
            address: The address to classify
            label: Optional label/description for heuristic classification
            
        Returns:
            AddressClassificationResult with chain, type, and confidence
        """
        address = address.strip()
        
        # Step 1: Detect chain
        chain, is_valid = self._detect_chain(address)
        
        if not is_valid:
            return AddressClassificationResult(
                address=address,
                chain='unknown',
                is_valid=False,
                confidence=0.0
            )
        
        # Step 2: Classify wallet type (for EVM chains)
        wallet_type = 'Unknown'
        if chain in self.EVM_CHAINS:
            wallet_type = self._classify_evm_address(address, chain)
        
        # Step 3: Apply heuristic classification (based on label)
        wallet_subtype = None
        if label:
            wallet_subtype = self._apply_heuristics(label)
        
        return AddressClassificationResult(
            address=address,
            chain=chain,
            is_valid=True,
            wallet_type=wallet_type,
            wallet_subtype=wallet_subtype,
            confidence=0.9 if wallet_type != 'Unknown' else 0.5
        )
    
    def _detect_chain(self, address: str) -> Tuple[str, bool]:
        """
        Detect blockchain network from address format
        
        Returns:
            (chain_name, is_valid)
        """
        # Check each pattern
        for chain, pattern in self.CHAIN_PATTERNS.items():
            if re.match(pattern, address):
                return (chain, True)
        
        # Check if it looks like an EVM address but didn't match ethereum
        # (could be another EVM chain)
        if re.match(self.CHAIN_PATTERNS['ethereum'], address):
            return ('ethereum', True)
        
        return ('unknown', False)
    
    def _classify_evm_address(self, address: str, chain: str) -> str:
        """
        Classify EVM address as EOA or Contract
        
        Uses eth_getCode RPC call:
        - Empty (0x or 0x0) = EOA (Externally Owned Account)
        - Non-empty = Smart Contract
        
        Returns:
            'EOA', 'Contract', or 'Unknown' if RPC fails
        """
        rpc_url = self.rpc_endpoints.get(chain)
        if not rpc_url:
            return 'Unknown'
        
        try:
            payload = {
                "jsonrpc": "2.0",
                "method": "eth_getCode",
                "params": [address, "latest"],
                "id": 1
            }
            
            response = self.session.post(
                rpc_url,
                json=payload,
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                code = result.get('result', '0x')
                
                # Empty code = EOA, non-empty = Contract
                if code in ['0x', '0x0', '']:
                    return 'EOA'
                else:
                    return 'Contract'
        
        except Exception as e:
            print(f"[WARNING] RPC call failed for {chain}: {str(e)}")
        
        return 'Unknown'
    
    def _apply_heuristics(self, label: str) -> Optional[str]:
        """
        Apply heuristic classification based on label/description
        
        Returns:
            Wallet subtype if pattern matches, else None
        """
        label_lower = label.lower()
        
        for subtype, keywords in self.KNOWN_PATTERNS.items():
            if any(keyword in label_lower for keyword in keywords):
                return subtype
        
        return None


# Singleton instance
_classifier_instance = None


def get_classifier() -> AddressClassifier:
    """Get singleton classifier instance"""
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = AddressClassifier()
    return _classifier_instance
