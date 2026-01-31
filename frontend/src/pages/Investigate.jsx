import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Search, AlertTriangle, CheckCircle, Smartphone, Bitcoin, Globe } from 'lucide-react';
import RiskCard from '../components/RiskCard';
import ReportsList from '../components/ReportsList';
import { useSearchParams } from 'react-router-dom';

export default function Investigate() {
    const [searchParams] = useSearchParams();
    const [query, setQuery] = useState(searchParams.get('addr') || '');
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    // Auto-trigger scan if URL param exists
    useEffect(() => {
        const addrParam = searchParams.get('addr');
        if (addrParam) {
            setQuery(addrParam);
            triggerScan(addrParam);
        }
    }, [searchParams]);

    const triggerScan = async (address) => {
        setLoading(true);
        setError('');
        setResult(null);

        try {
            // Use new unified endpoint
            const res = await axios.post('/api/classify-address', { address: address });
            setResult(res.data);
        } catch (err) {
            setError(err.response?.data?.error || 'Failed to classify address. Please check the format and try again.');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleScan = (e) => {
        e.preventDefault();
        if (!query) return;
        triggerScan(query);
    };

    const getChainIcon = (chain) => {
        const icons = {
            'bitcoin': '₿',
            'ethereum': 'Ξ',
            'solana': 'S',
            'polygon': 'P',
            'bsc': 'B',
            'tron': 'T'
        };
        return icons[chain?.toLowerCase()] || '⚡';
    };

    return (
        <div className="animate-fade-in">
            <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
                <h1 style={{ fontSize: '2rem', marginBottom: '1rem' }}>Address Investigation</h1>
                <p style={{ color: 'var(--text-muted)', maxWidth: '600px', margin: '0 auto' }}>
                    Multi-source intelligence platform combining local dataset and Chainabuse threat data
                </p>
            </div>

            <div className="glass-panel" style={{ maxWidth: '700px', margin: '0 auto 3rem auto', padding: '2rem' }}>
                <form onSubmit={handleScan} style={{ display: 'flex', gap: '1rem' }}>
                    <input
                        type="text"
                        className="input-field"
                        placeholder="Enter Wallet Address (e.g., 0x123... or bc1...)"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                    />
                    <button type="submit" className="btn-primary" disabled={loading}>
                        {loading ? 'Analyzing...' : <><Search size={18} style={{ marginRight: '8px' }} /> Investigate</>}
                    </button>
                </form>
                {error && <div style={{ marginTop: '1rem', color: 'var(--danger)', padding: '1rem', background: 'rgba(239, 68, 68, 0.1)', borderRadius: '8px' }}>{error}</div>}
            </div>

            {result && (
                <div className="animate-fade-in" style={{ marginBottom: '3rem' }}>
                    {/* Header with chain and wallet type */}
                    <div style={{ maxWidth: '1200px', margin: '0 auto 2rem auto' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
                            <div style={{
                                width: '60px',
                                height: '60px',
                                borderRadius: '50%',
                                background: 'linear-gradient(135deg, var(--primary), var(--accent))',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                fontSize: '2rem',
                                fontWeight: '800'
                            }}>
                                {getChainIcon(result.chain)}
                            </div>
                            <div>
                                <div style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>Address Analysis</div>
                                <div style={{ fontSize: '1.2rem', fontFamily: 'monospace', fontWeight: '600', color: 'var(--accent)' }}>
                                    {result.address.substring(0, 16)}...{result.address.substring(result.address.length - 8)}
                                </div>
                                <div style={{ display: 'flex', gap: '0.75rem', marginTop: '0.5rem' }}>
                                    <span style={{
                                        padding: '4px 12px',
                                        background: 'var(--primary)',
                                        borderRadius: '6px',
                                        fontSize: '0.85rem',
                                        fontWeight: '600',
                                        textTransform: 'capitalize'
                                    }}>
                                        {result.chain}
                                    </span>
                                    {result.wallet_type && (
                                        <span style={{
                                            padding: '4px 12px',
                                            background: 'rgba(99, 102, 241, 0.2)',
                                            border: '1px solid var(--primary)',
                                            borderRadius: '6px',
                                            fontSize: '0.85rem'
                                        }}>
                                            {result.wallet_type}
                                        </span>
                                    )}
                                    {result.wallet_subtype && result.wallet_subtype.toLowerCase() !== 'unknown' && (
                                        <span style={{
                                            padding: '4px 12px',
                                            background: 'rgba(251, 191, 36, 0.2)',
                                            border: '1px solid var(--warning)',
                                            borderRadius: '6px',
                                            fontSize: '0.85rem',
                                            color: 'var(--warning)',
                                            textTransform: 'capitalize'
                                        }}>
                                            {result.wallet_subtype}
                                        </span>
                                    )}
                                </div>
                            </div>
                        </div>

                        {/* Investigation Results Grid */}
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.5fr', gap: '2rem' }}>
                            {/* Left Column */}
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                                <RiskCard
                                    riskLevel={result.risk_level}
                                    riskScore={result.risk_score}
                                    reasoning={result.risk_reasoning}
                                    transactionData={result.transaction_data}
                                />

                                {/* Data Sources */}
                                <div className="glass-panel" style={{ padding: '1.5rem' }}>
                                    <h3 style={{ marginTop: 0, marginBottom: '1rem', fontSize: '1.1rem' }}>Data Sources</h3>
                                    {result.sources.map((source, idx) => (
                                        <div key={idx} style={{
                                            display: 'flex',
                                            justifyContent: 'space-between',
                                            padding: '0.75rem',
                                            background: 'rgba(0,0,0,0.2)',
                                            borderRadius: '6px',
                                            marginBottom: '0.5rem'
                                        }}>
                                            <span>{source.name}</span>
                                            <span style={{
                                                color: source.status === 'checked' ? 'var(--success)' : 'var(--text-muted)',
                                                fontSize: '0.85rem'
                                            }}>
                                                {source.status === 'checked' ? '✓ Checked' : '• Not configured'}
                                            </span>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            {/* Right Column */}
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                                <ReportsList
                                    datasetReports={result.dataset_reports}
                                    chainabuseReports={result.chainabuse_reports}
                                />
                            </div>
                        </div>
                    </div>
                </div>
            )}

            <div className="glass-panel" style={{ maxWidth: '700px', margin: '0 auto', padding: '2rem', borderTop: '3px solid var(--accent)' }}>
                <h3 style={{ marginTop: 0, display: 'flex', alignItems: 'center', gap: '10px' }}><Smartphone size={20} /> Report Suspicious Address</h3>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '1rem' }}>
                    Found a scammer? Report it to the community database.
                </p>
                <ReportForm />
            </div>
        </div>
    );
}

function ReportForm() {
    const [addr, setAddr] = useState('');
    const [category, setCategory] = useState('Scam');
    const [desc, setDesc] = useState('');
    const [msg, setMsg] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await axios.post('/api/report', {
                address: addr,
                category: category,
                description: desc
            });
            setMsg('Report submitted successfully!');
            setAddr('');
            setDesc('');
        } catch (err) {
            setMsg('Error submitting report.');
        }
    };

    return (
        <form onSubmit={handleSubmit} style={{ display: 'grid', gap: '1rem' }}>
            <input className="input-field" placeholder="Wallet Address" value={addr} onChange={e => setAddr(e.target.value)} required />
            <select className="input-field" value={category} onChange={e => setCategory(e.target.value)}>
                <option value="Scam">Scam</option>
                <option value="Ransomware">Ransomware</option>
                <option value="Phishing">Phishing</option>
                <option value="Darknet Market">Darknet Market</option>
                <option value="Mixer">Mixer</option>
            </select>
            <textarea className="input-field" placeholder="Description / Source of Info" rows="3" value={desc} onChange={e => setDesc(e.target.value)}></textarea>
            <button className="btn-primary" style={{ justifySelf: 'start' }}>Submit Report</button>
            {msg && <span style={{ color: 'var(--accent)' }}>{msg}</span>}
        </form>
    );
}
