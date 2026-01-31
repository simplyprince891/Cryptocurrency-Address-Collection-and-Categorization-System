import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { ArrowRight, ShieldAlert, Activity, Search } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function Dashboard() {
    const [recent, setRecent] = useState([]);
    const [query, setQuery] = useState('');
    const navigate = useNavigate();

    useEffect(() => {
        axios.get('/api/recent')
            .then(res => setRecent(res.data))
            .catch(err => console.error(err));
    }, []);

    const handleSearch = (e) => {
        e.preventDefault();
        if (query) navigate(`/investigate?addr=${query}`);
    }

    return (
        <div className="animate-fade-in">
            {/* Hero Section */}
            <div style={{
                textAlign: 'center',
                padding: '4rem 1rem',
                background: 'radial-gradient(circle at center, rgba(99, 102, 241, 0.15) 0%, transparent 70%)'
            }}>
                <h1 style={{ fontSize: '3.5rem', fontWeight: '800', margin: '0 0 1.5rem 0', lineHeight: 1.1 }}>
                    Trusted <span style={{ color: 'var(--primary)' }}>Crypto Forensics</span><br /> & Scam Reporting
                </h1>
                <p style={{ fontSize: '1.2rem', color: 'var(--text-muted)', maxWidth: '700px', margin: '0 auto 2.5rem auto' }}>
                    The community-driven platform to track illicit fund movements, report scams, and visualize transaction networks using AI.
                </p>

                <form onSubmit={handleSearch} style={{ maxWidth: '600px', margin: '0 auto', position: 'relative' }}>
                    <Search color="var(--text-muted)" size={20} style={{ position: 'absolute', left: '15px', top: '50%', transform: 'translateY(-50%)' }} />
                    <input
                        type="text"
                        className="input-field"
                        style={{ paddingLeft: '45px', paddingRight: '120px', height: '55px', fontSize: '1.1rem', borderRadius: '30px', border: '1px solid var(--primary)' }}
                        placeholder="Check wallet address (0x...)"
                        value={query}
                        onChange={e => setQuery(e.target.value)}
                    />
                    <button className="btn-primary" style={{
                        position: 'absolute',
                        right: '5px',
                        top: '5px',
                        bottom: '5px',
                        borderRadius: '25px',
                        padding: '0 30px'
                    }}>
                        Search
                    </button>
                </form>
            </div>

            {/* Stats / Ticker */}
            <div className="container">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                    <h2 style={{ fontSize: '1.5rem', margin: 0 }}>Latest Reported Scams</h2>
                    <button className="btn-primary" onClick={() => navigate('/investigate')} style={{ background: 'var(--bg-card)', border: '1px solid var(--glass-border)', boxShadow: 'none' }}>Report a Scam</button>
                </div>

                <div className="glass-panel" style={{ padding: '0', overflow: 'hidden' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                        <thead style={{ background: 'rgba(0,0,0,0.2)' }}>
                            <tr>
                                <th style={{ padding: '1rem', color: 'var(--text-muted)' }}>Reported Address</th>
                                <th style={{ padding: '1rem', color: 'var(--text-muted)' }}>Category</th>
                                <th style={{ padding: '1rem', color: 'var(--text-muted)' }}>Label/Description</th>
                                <th style={{ padding: '1rem', color: 'var(--text-muted)' }}>Date</th>
                                <th style={{ padding: '1rem', color: 'var(--text-muted)' }}>Risk</th>
                            </tr>
                        </thead>
                        <tbody>
                            {recent.map(addr => (
                                <tr key={addr.id} style={{ borderBottom: '1px solid var(--glass-border)', cursor: 'pointer' }} onClick={() => navigate(`/investigate?addr=${addr.id}`)}>
                                    <td style={{ padding: '1rem', fontFamily: 'monospace', color: 'var(--accent)' }}>{addr.id.substring(0, 12)}...</td>
                                    <td style={{ padding: '1rem' }}>
                                        <span style={{
                                            padding: '4px 8px',
                                            borderRadius: '4px',
                                            fontSize: '0.8rem',
                                            background: addr.category === 'Personal Wallet' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(239, 68, 68, 0.2)',
                                            color: addr.category === 'Personal Wallet' ? 'var(--success)' : 'var(--danger)'
                                        }}>
                                            {addr.category}
                                        </span>
                                    </td>
                                    <td style={{ padding: '1rem', color: 'var(--text-muted)', fontSize: '0.9rem' }}>{addr.label || 'No description provided'}</td>
                                    <td style={{ padding: '1rem', color: 'var(--text-muted)', fontSize: '0.9rem' }}>{new Date(addr.last_updated).toLocaleDateString()}</td>
                                    <td style={{ padding: '1rem', fontWeight: 'bold', color: addr.risk_score > 50 ? 'var(--danger)' : 'var(--success)' }}>
                                        {Math.round(addr.risk_score)}/100
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}
