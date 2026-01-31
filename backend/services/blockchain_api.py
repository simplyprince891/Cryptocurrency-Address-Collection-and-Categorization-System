"""
Blockchain Data API Service

Fetches transaction data from free public APIs:
- Blockchain.com for Bitcoin
- Etherscan for Ethereum
- BscScan for BSC
- Polygonscan for Polygon

No API keys required for basic Bitcoin data.
Etherscan requires free API key (5 req/sec).
"""

import os
import requests
from datetime import datetime
from typing import Optional, Dict
from dataclasses import dataclass


@dataclass
class WalletStats:
    """Wallet transaction statistics"""
    tx_count: int
    total_received: float
    total_sent: float
    balance: float
    first_tx_date: Optional[datetime]
    last_tx_date: Optional[datetime]
    wallet_age_days: int


class BlockchainDataService:
    """Fetch transaction data from blockchain APIs"""
    
    # API endpoints (all FREE)
    BLOCKCHAIN_INFO_API = "https://blockchain.info"
    ETHERSCAN_API = "https://api.etherscan.io/v2/api"  # Updated to V2
    BSCSCAN_API = "https://api.bscscan.com/api"
    POLYGONSCAN_API = "https://api.polygonscan.com/api"
    
    def __init__(self):
        # Load API keys from environment (free tier keys)
        self.etherscan_key = os.getenv('ETHERSCAN_API_KEY', 'YourApiKeyToken')
        self.bscscan_key = os.getenv('BSCSCAN_API_KEY', 'YourApiKeyToken')
        self.polygonscan_key = os.getenv('POLYGONSCAN_API_KEY', 'YourApiKeyToken')
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'CryptoInvestigator/1.0'
        })
    
    def get_wallet_stats(self, address: str, chain: str) -> Optional[WalletStats]:
        """
        Get wallet statistics based on chain
        
        Args:
            address: Wallet address
            chain: blockchain (bitcoin, ethereum, bsc, polygon, etc.)
        
        Returns:
            WalletStats or None if unavailable
        """
        chain_lower = chain.lower()
        
        if chain_lower == 'bitcoin':
            return self._get_bitcoin_stats(address)
        elif chain_lower in ['ethereum', 'evm']:
            return self._get_ethereum_stats(address)
        elif chain_lower == 'bsc':
            return self._get_bsc_stats(address)
        elif chain_lower == 'polygon':
            return self._get_polygon_stats(address)
        else:
            print(f"[INFO] Chain '{chain}' not supported for transaction data yet")
            return None
    
    def _get_bitcoin_stats(self, address: str) -> Optional[WalletStats]:
        """Get Bitcoin wallet stats from Blockchain.com (FREE, no key needed)"""
        try:
            print(f"[INFO] Fetching Bitcoin transaction data for {address[:16]}...")
            response = self.session.get(
                f"{self.BLOCKCHAIN_INFO_API}/rawaddr/{address}?limit=0",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Calculate wallet age
                first_tx = data.get('first_tx')
                last_tx = data.get('last_tx')
                wallet_age_days = 0
                
                if first_tx:
                    first_date = datetime.fromtimestamp(first_tx)
                    wallet_age_days = (datetime.now() - first_date).days
                
                stats = WalletStats(
                    tx_count=data.get('n_tx', 0),
                    total_received=data.get('total_received', 0) / 100000000,  # Satoshi to BTC
                    total_sent=data.get('total_sent', 0) / 100000000,
                    balance=data.get('final_balance', 0) / 100000000,
                    first_tx_date=datetime.fromtimestamp(first_tx) if first_tx else None,
                    last_tx_date=datetime.fromtimestamp(last_tx) if last_tx else None,
                    wallet_age_days=wallet_age_days
                )
                
                print(f"[SUCCESS] Bitcoin: {stats.tx_count} txs, {stats.wallet_age_days} days old")
                return stats
            
            elif response.status_code == 404:
                print(f"[INFO] No Bitcoin transactions found for address")
                return None
            else:
                print(f"[WARNING] Blockchain.com API error: {response.status_code}")
                return None
        
        except Exception as e:
            print(f"[ERROR] Bitcoin API failed: {str(e)}")
            return None
    
    def _get_ethereum_stats(self, address: str) -> Optional[WalletStats]:
        """Get Ethereum wallet stats from Etherscan (FREE tier: 5 req/sec)"""
        try:
            print(f"[INFO] Fetching Ethereum transaction data for {address[:16]}...")
            
            # Get normal transactions
            response = self.session.get(
                self.ETHERSCAN_API,
                params={
                    'chainid': '1',  # Ethereum mainnet (required for V2)
                    'module': 'account',
                    'action': 'txlist',
                    'address': address,
                    'startblock': 0,
                    'endblock': 99999999,
                    'page': 1,
                    'offset': 10000,  # Max 10k txs
                    'sort': 'asc',
                    'apikey': self.etherscan_key
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for API errors
                if data.get('status') == '0':
                    error_msg = data.get('message', 'Unknown error')
                    error_result = data.get('result', '')
                    print(f"[ERROR] Etherscan API error: {error_msg}")
                    print(f"[ERROR] Etherscan details: {error_result}")
                    if 'invalid api key' in error_msg.lower() or 'invalid api key' in str(error_result).lower():
                        print(f"[ERROR] Your ETHERSCAN_API_KEY appears to be invalid")
                    elif 'rate limit' in error_msg.lower():
                        print(f"[WARNING] Etherscan rate limit exceeded")
                    return None
                
                if data.get('status') == '1' and data.get('result'):
                    txs = data['result']
                    
                    # Handle case where result is not a list
                    if not isinstance(txs, list):
                        print(f"[ERROR] Unexpected Etherscan response format: {type(txs)}")
                        return None
                    
                    if len(txs) == 0:
                        print(f"[INFO] No Ethereum transactions found")
                        return None
                    
                    # Calculate totals
                    total_received = 0.0
                    total_sent = 0.0
                    
                    for tx in txs:
                        value_eth = int(tx.get('value', 0)) / 1e18  # Wei to ETH
                        if tx['to'].lower() == address.lower():
                            total_received += value_eth
                        if tx['from'].lower() == address.lower():
                            total_sent += value_eth
                    
                    # Get balance
                    balance_response = self.session.get(
                        self.ETHERSCAN_API,
                        params={
                            'chainid': '1',  # Ethereum mainnet (required for V2)
                            'module': 'account',
                            'action': 'balance',
                            'address': address,
                            'tag': 'latest',
                            'apikey': self.etherscan_key
                        },
                        timeout=5
                    )
                    
                    balance = 0.0
                    if balance_response.status_code == 200:
                        balance_data = balance_response.json()
                        if balance_data.get('status') == '1':
                            balance = int(balance_data['result']) / 1e18
                    
                    # Calculate wallet age
                    first_tx_timestamp = int(txs[0]['timeStamp'])
                    last_tx_timestamp = int(txs[-1]['timeStamp'])
                    first_date = datetime.fromtimestamp(first_tx_timestamp)
                    last_date = datetime.fromtimestamp(last_tx_timestamp)
                    wallet_age_days = (datetime.now() - first_date).days
                    
                    stats = WalletStats(
                        tx_count=len(txs),
                        total_received=total_received,
                        total_sent=total_sent,
                        balance=balance,
                        first_tx_date=first_date,
                        last_tx_date=last_date,
                        wallet_age_days=wallet_age_days
                    )
                    
                    print(f"[SUCCESS] Ethereum: {stats.tx_count} txs, {stats.wallet_age_days} days old")
                    return stats
                else:
                    print(f"[INFO] No Ethereum transactions found")
                    return None
            else:
                print(f"[WARNING] Etherscan API error: {response.status_code}")
                return None
        
        except Exception as e:
            print(f"[ERROR] Ethereum API failed: {str(e)}")
            return None
    
    def _get_bsc_stats(self, address: str) -> Optional[WalletStats]:
        """Get BSC wallet stats from BscScan (same API as Etherscan)"""
        # Almost identical to Etherscan, just different endpoint
        # Implementation similar to _get_ethereum_stats but with BSCSCAN_API
        print(f"[INFO] BSC transaction data not fully implemented yet")
        return None
    
    def _get_polygon_stats(self, address: str) -> Optional[WalletStats]:
        """Get Polygon wallet stats from Polygonscan"""
        print(f"[INFO] Polygon transaction data not fully implemented yet")
        return None


# Singleton instance
_blockchain_service = None


def get_blockchain_service() -> BlockchainDataService:
    """Get singleton blockchain data service"""
    global _blockchain_service
    if _blockchain_service is None:
        _blockchain_service = BlockchainDataService()
    return _blockchain_service
