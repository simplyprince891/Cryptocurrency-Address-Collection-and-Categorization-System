    
    def _calculate_behavioral_risk(self, tx_data: Optional[dict], reasoning: List[str]) -> float:
        """
        Calculate risk from transaction patterns and wallet behavior
        Uses FREE blockchain API data (Blockchain.com, Etherscan)
        
        Args:
            tx_data: Transaction statistics dict with:
                - tx_count: Number of transactions
                - wallet_age_days: Age in days
                - total_received: Total BTC/ETH received
                - total_sent: Total sent
                - balance: Current balance
        
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
        
        # Mixing pattern detection (many small transactions)
        if tx_count > 100:
            avg_tx_size = total_received / tx_count if tx_count > 0 else 0
            if avg_tx_size < 0.1:  # Average < 0.1 BTC/ETH
                risk += 25
                reasoning.append("⚠️ Mixing pattern detected (many small transactions)")
        
        # Dormant wallets that suddenly activate
        if wallet_age > 365:  # Old wallet
            last_tx_date = tx_data.get('last_tx_date')
            # If provided, check if recently reactivated
            # For now, skip this check without timestamp
            pass
        
        # Balance analysis
        balance = tx_data.get('balance', 0)
        total_sent = tx_data.get('total_sent', 0)
        
        # High throughput (received and sent a lot, low balance) = tumbler
        if total_received > 100 and total_sent > 100 and balance < 1:
            risk += 20
            reasoning.append("📉 High throughput with low balance - possible tumbler/mixer")
        
        # Empty wallet after high volume = exit scam pattern
        if total_received > 10 and balance < 0.01 and wallet_age < 180:
            risk += 15
            reasoning.append("⚠️ Emptied wallet after receiving funds - possible scam exit")
        
        return min(risk, 100.0)
