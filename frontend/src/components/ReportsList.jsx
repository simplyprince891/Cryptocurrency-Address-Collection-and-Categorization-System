import React from 'react';
import { FileText, ExternalLink } from 'lucide-react';

export default function ReportsList({ datasetReports, chainabuseReports }) {
    const hasDatasetReports = datasetReports && datasetReports.found;
    const hasChainabuseReports = chainabuseReports && chainabuseReports.report_count > 0;

    if (!hasDatasetReports && !hasChainabuseReports) {
        return (
            <div className="glass-panel" style={{ textAlign: 'center', padding: '3rem' }}>
                <FileText size={48} color="var(--text-muted)" style={{ opacity: 0.5, marginBottom: '1rem' }} />
                <div style={{ color: 'var(--text-muted)', fontSize: '1.1rem' }}>
                    No abuse reports found for this address
                </div>
            </div>
        );
    }

    return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            {/* Dataset Reports */}
            {hasDatasetReports && (
                <div className="glass-panel" style={{
                    borderLeft: '4px solid var(--accent)',
                    background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.05) 0%, rgba(0,0,0,0.2) 100%)'
                }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem' }}>
                        <FileText size={22} color="var(--accent)" />
                        <h3 style={{ margin: 0, fontSize: '1.3rem', fontWeight: '700' }}>Local Dataset</h3>
                    </div>

                    <div style={{ display: 'grid', gap: '1rem' }}>
                        {/* Category */}
                        <div style={{
                            padding: '1rem',
                            background: 'rgba(99, 102, 241, 0.1)',
                            borderRadius: '10px',
                            border: '1px solid rgba(99, 102, 241, 0.3)'
                        }}>
                            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.4rem', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Category</div>
                            <div style={{ fontWeight: '700', fontSize: '1.1rem', color: 'var(--accent)' }}>{datasetReports.category}</div>
                        </div>

                        {/* Label/Description */}
                        {datasetReports.label && (
                            <div style={{
                                padding: '1rem',
                                background: 'rgba(0,0,0,0.3)',
                                borderRadius: '10px',
                                border: '1px solid rgba(255,255,255,0.1)'
                            }}>
                                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.4rem', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Description</div>
                                <div style={{ lineHeight: '1.6', color: 'var(--text-secondary)' }}>{datasetReports.label}</div>
                            </div>
                        )}

                        {/* Risk Score */}
                        <div style={{
                            padding: '1rem',
                            background: datasetReports.risk_score > 70
                                ? 'linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(220, 38, 38, 0.05) 100%)'
                                : 'linear-gradient(135deg, rgba(251, 191, 36, 0.15) 0%, rgba(245, 158, 11, 0.05) 100%)',
                            borderRadius: '10px',
                            border: `1px solid ${datasetReports.risk_score > 70 ? 'rgba(239, 68, 68, 0.4)' : 'rgba(251, 191, 36, 0.4)'}`
                        }}>
                            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.4rem', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Dataset Risk Score</div>
                            <div style={{
                                fontWeight: '800',
                                fontSize: '1.4rem',
                                color: datasetReports.risk_score > 70 ? '#EF4444' : '#F59E0B'
                            }}>
                                {Math.round(datasetReports.risk_score)}/100
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Chainabuse Reports */}
            {hasChainabuseReports && (
                <div className="glass-panel">
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <FileText size={20} color="var(--accent)" />
                            <h3 style={{ margin: 0, fontSize: '1.2rem' }}>Chainabuse Reports</h3>
                        </div>
                        <span style={{
                            padding: '4px 12px',
                            background: 'var(--primary)',
                            borderRadius: '12px',
                            fontSize: '0.85rem',
                            fontWeight: '600'
                        }}>
                            {chainabuseReports.report_count} {chainabuseReports.report_count === 1 ? 'Report' : 'Reports'}
                        </span>
                    </div>

                    {chainabuseReports.categories.length > 0 && (
                        <div style={{ marginBottom: '1rem' }}>
                            <div style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
                                Categories:
                            </div>
                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                                {chainabuseReports.categories.map((cat, idx) => (
                                    <span key={idx} style={{
                                        padding: '6px 12px',
                                        background: 'rgba(239, 68, 68, 0.2)',
                                        border: '1px solid rgba(239, 68, 68, 0.3)',
                                        borderRadius: '6px',
                                        fontSize: '0.85rem',
                                        color: 'var(--danger)'
                                    }}>
                                        {cat}
                                    </span>
                                ))}
                            </div>
                        </div>
                    )}

                    {chainabuseReports.reports && chainabuseReports.reports.length > 0 && (
                        <div style={{ marginTop: '1.5rem' }}>
                            <div style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginBottom: '0.75rem' }}>
                                Recent Reports:
                            </div>
                            {chainabuseReports.reports.map((report, idx) => (
                                <div key={idx} style={{
                                    padding: '1rem',
                                    background: 'rgba(0,0,0,0.2)',
                                    borderRadius: '8px',
                                    marginBottom: '0.75rem'
                                }}>
                                    <div style={{ fontWeight: '600', color: 'var(--danger)', marginBottom: '0.5rem' }}>
                                        {report.category}
                                    </div>
                                    <div style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                                        {report.description}
                                    </div>
                                    {report.amount_lost > 0 && (
                                        <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>
                                            Reported Loss: ${report.amount_lost.toLocaleString()}
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
