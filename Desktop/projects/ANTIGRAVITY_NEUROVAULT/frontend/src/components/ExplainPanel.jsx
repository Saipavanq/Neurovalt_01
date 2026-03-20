import { useEffect, useRef } from 'react'
import { TIER_COLORS } from './TierBadge'
import TierBadge from './TierBadge'
import { Info } from 'lucide-react'

function ScoreBar({ label, value, color, weight }) {
    return (
        <div className="score-bar-row">
            <span className="score-bar-label">{label}</span>
            <div className="score-bar-bg">
                <div
                    className="score-bar-fill"
                    style={{ width: `${Math.round(value * 100)}%`, background: color }}
                />
            </div>
            <span className="score-bar-val">{(value * 100).toFixed(0)}%</span>
        </div>
    )
}

export default function ExplainPanel({ breakdown }) {
    if (!breakdown) return null

    const {
        final_score,
        semantic_similarity,
        semantic_percentage,
        recency_score,
        recency_label,
        access_score,
        access_label,
        tier,
        explanation,
    } = breakdown

    const tierColor = TIER_COLORS[tier] || '#888'
    const scoreColor = final_score >= 0.75 ? '#00ff88'
        : final_score >= 0.50 ? '#00d4ff'
            : final_score >= 0.25 ? '#ff9500'
                : '#666688'

    return (
        <div style={{
            background: 'rgba(0,212,255,0.04)',
            border: '1px solid rgba(0,212,255,0.15)',
            borderRadius: 12,
            padding: '16px 20px',
            display: 'flex',
            flexDirection: 'column',
            gap: 14,
        }}>
            {/* Header */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <Info size={14} color="var(--cyan)" />
                    <span style={{ fontSize: 12, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.07em', fontWeight: 600 }}>
                        AI Explanation
                    </span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                    <TierBadge tier={tier} />
                    <span style={{ fontSize: 22, fontWeight: 800, color: scoreColor, fontFamily: "'JetBrains Mono', monospace" }}>
                        {final_score.toFixed(3)}
                    </span>
                </div>
            </div>

            {/* Score breakdown bars */}
            <div className="score-bar-wrap">
                <ScoreBar label="Semantic" value={semantic_similarity} color="#a855f7" />
                <ScoreBar label="Recency" value={recency_score} color="#00d4ff" />
                <ScoreBar label="Access Freq" value={access_score} color="#00ff88" />
            </div>

            {/* Labels */}
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                <span style={{
                    fontSize: 11, padding: '3px 10px', borderRadius: 20,
                    background: 'rgba(168,85,247,0.12)', color: '#a855f7',
                    border: '1px solid rgba(168,85,247,0.25)',
                }}>
                    {semantic_percentage}% semantic match
                </span>
                <span style={{
                    fontSize: 11, padding: '3px 10px', borderRadius: 20,
                    background: 'rgba(0,212,255,0.1)', color: 'var(--cyan)',
                    border: '1px solid rgba(0,212,255,0.25)',
                }}>
                    {recency_label}
                </span>
                <span style={{
                    fontSize: 11, padding: '3px 10px', borderRadius: 20,
                    background: 'rgba(0,255,136,0.1)', color: 'var(--green)',
                    border: '1px solid rgba(0,255,136,0.25)',
                }}>
                    {access_label}
                </span>
            </div>

            {/* Explanation text */}
            <p style={{ fontSize: 12, color: 'var(--text-muted)', lineHeight: 1.6 }}>
                {explanation}
            </p>
        </div>
    )
}
