import React from 'react';
import { Shield, AlertTriangle, AlertCircle, CheckCircle } from 'lucide-react';

export default function RiskCard({ riskLevel, riskScore, reasoning, transactionData }) {
    const getRiskColor = (level) => {
        switch (level) {
            case 'HIGH': return {
                bg: 'linear-gradient(135deg, rgba(239, 68, 68, 0.2) 0%, rgba(220, 38, 38, 0.1) 100%)',
                border: '#EF4444',
                icon: '#EF4444',
                text: 'Critical Risk',
                shadow: '0 0 30px rgba(239, 68, 68, 0.3)'
            };
            case 'MEDIUM': return {
                bg: 'linear-gradient(135deg, rgba(251, 191, 36, 0.2) 0%, rgba(245, 158, 11, 0.1) 100%)',
                border: '#F59E0B',
                icon: '#F59E0B',
                text: 'Medium Risk',
                shadow: '0 0 30px rgba(251, 191, 36, 0.3)'
            };
            case 'LOW': return {
                bg: 'linear-gradient(135deg, rgba(59, 130, 246, 0.2) 0%, rgba(37, 99, 235, 0.1) 100%)',
                border: '#3B82F6',
                icon: '#3B82F6',
                text: 'Low Risk',
                shadow: '0 0 30px rgba(59, 130, 246, 0.3)'
            };
            default: return {
                bg: 'linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(5, 150, 105, 0.1) 100%)',
                border: '#10B981',
                icon: '#10B981',
                text: 'Clean',
                shadow: '0 0 30px rgba(16, 185, 129, 0.3)'
            };
        }
    };

    const riskConfig = getRiskColor(riskLevel);
    const Icon = riskLevel === 'HIGH' ? AlertCircle : riskLevel === 'MEDIUM' ? AlertTriangle : Shield;

    return (
        <div className="glass-panel" style={{
            border: `2px solid ${riskConfig.border}`,
            background: riskConfig.bg,
            padding: '2rem',
            boxShadow: riskConfig.shadow,
            transition: 'all 0.3s ease'
        }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.5rem' }}>
                <Icon size={40} color={riskConfig.icon} />
                <div>
                    <div style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>
                        Risk Assessment
                    </div>
                    <div style={{ fontSize: '2rem', fontWeight: '800', color: riskConfig.icon }}>
                        {Math.round(riskScore)}/100
                    </div>
                    <div style={{ fontSize: '1.1rem', fontWeight: '600', color: riskConfig.icon }}>
                        {riskConfig.text}
                    </div>
                </div>
            </div>

            {reasoning && reasoning.length > 0 && (
                <div style={{ marginTop: '1.5rem', paddingTop: '1.5rem', borderTop: `1px solid ${riskConfig.border}` }}>
                    <div style={{ fontSize: '0.9rem', fontWeight: '600', marginBottom: '0.75rem', color: 'var(--text-primary)' }}>
                        Risk Factors:
                    </div>
                    <ul style={{ margin: 0, paddingLeft: '1.5rem', color: 'var(--text-secondary)' }}>
                        {reasoning.map((reason, idx) => (
                            <li key={idx} style={{ marginBottom: '0.5rem', fontSize: '0.95rem' }}>
                                {reason}
                            </li>
                        ))}
                    </ul>
                </div>
            )}

            {/* NEW: Transaction Metrics Display */}
            {transactionData && (
                <div style={{ marginTop: '1.5rem', paddingTop: '1.5rem', borderTop: `1px solid ${riskConfig.border}` }}>
                    <div style={{ fontSize: '0.9rem', fontWeight: '600', marginBottom: '0.75rem', color: 'var(--text-primary)' }}>
                        📊 Transaction Metrics:
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '0.75rem', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                        <div>
                            <strong>Transactions:</strong> {transactionData.tx_count?.toLocaleString() || 'N/A'}
                        </div>
                        <div>
                            <strong>Wallet Age:</strong> {transactionData.wallet_age_days ? `${transactionData.wallet_age_days} days` : 'N/A'}
                        </div>
                        <div>
                            <strong>Balance:</strong> {transactionData.balance?.toFixed(4) || 'N/A'}
                        </div>
                        <div>
                            <strong>Total Received:</strong> {transactionData.total_received?.toFixed(4) || 'N/A'}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
