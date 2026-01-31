import React, { useEffect, useRef } from 'react';
import ForceGraph2D from 'react-force-graph-2d';

const NetworkGraph = ({ data }) => {
    const wrapperRef = useRef();

    if (!data || !data.nodes || data.nodes.length === 0) {
        return <div className="glass-panel" style={{ height: '400px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#64748b' }}>No transaction data to display</div>;
    }

    return (
        <div ref={wrapperRef} className="glass-panel" style={{ height: '500px', overflow: 'hidden', padding: 0 }}>
            <ForceGraph2D
                width={wrapperRef.current ? wrapperRef.current.offsetWidth : 800}
                height={500}
                graphData={data}
                nodeLabel="id"
                nodeColor={node => {
                    if (node.risk > 80) return '#ef4444'; // Red for high risk
                    if (node.group === 'Exchange') return '#06b6d4'; // Blue for exchange
                    return '#10b981'; // Green for safe
                }}
                nodeRelSize={6}
                linkColor={() => 'rgba(255,255,255,0.2)'}
                linkDirectionalParticles={2}
                linkDirectionalParticleSpeed={d => d.value * 0.001}
                backgroundColor="#1e293b"
            />
        </div>
    );
};

export default NetworkGraph;
