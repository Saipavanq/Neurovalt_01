import { useEffect, useRef, useState } from 'react'
import * as d3 from 'd3'
import { getLifecycleData, getTierSummary } from '../utils/api'
import { TIER_COLORS } from '../components/TierBadge'
import { Layers, Loader } from 'lucide-react'

// ── D3 Tier Bar Chart ──────────────────────────────────────
function TierBarChart({ tiers }) {
    const svgRef = useRef(null)
    useEffect(() => {
        if (!tiers || !svgRef.current) return
        const el = svgRef.current
        const W = el.clientWidth || 600
        const H = 220
        const margin = { top: 20, right: 20, bottom: 40, left: 40 }
        const iW = W - margin.left - margin.right
        const iH = H - margin.top - margin.bottom

        d3.select(el).selectAll('*').remove()
        const svg = d3.select(el).attr('viewBox', `0 0 ${W} ${H}`).attr('width', W).attr('height', H)
        const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`)

        const tierNames = Object.keys(tiers)
        const counts = tierNames.map(t => tiers[t].count)

        const x = d3.scaleBand().domain(tierNames).range([0, iW]).padding(0.35)
        const y = d3.scaleLinear().domain([0, Math.max(...counts, 1)]).nice().range([iH, 0])

        // Axis
        g.append('g').attr('transform', `translate(0,${iH})`)
            .call(d3.axisBottom(x).tickSize(0))
            .select('.domain').remove()
        g.selectAll('.tick text').style('fill', '#888').style('font-size', '12px')

        g.append('g').call(d3.axisLeft(y).ticks(5).tickSize(-iW))
            .call(ax => ax.select('.domain').remove())
            .call(ax => ax.selectAll('line').attr('stroke', 'rgba(255,255,255,0.05)'))
            .call(ax => ax.selectAll('text').style('fill', '#888').style('font-size', '10px'))

        // Bars
        g.selectAll('.bar')
            .data(tierNames)
            .enter().append('rect')
            .attr('class', 'bar')
            .attr('x', d => x(d))
            .attr('y', iH)
            .attr('width', x.bandwidth())
            .attr('height', 0)
            .attr('rx', 6)
            .attr('fill', d => TIER_COLORS[d] || '#888')
            .attr('opacity', 0.8)
            .transition().duration(700).ease(d3.easeBackOut)
            .attr('y', d => y(tiers[d].count))
            .attr('height', d => iH - y(tiers[d].count))

        // Labels
        g.selectAll('.label')
            .data(tierNames)
            .enter().append('text')
            .attr('x', d => x(d) + x.bandwidth() / 2)
            .attr('y', d => y(tiers[d].count) - 6)
            .attr('text-anchor', 'middle')
            .attr('font-size', 13)
            .attr('font-weight', 700)
            .attr('fill', d => TIER_COLORS[d] || '#888')
            .text(d => tiers[d].count)

    }, [tiers])
    return <svg ref={svgRef} style={{ width: '100%' }} />
}

// ── D3 Score Histogram ──────────────────────────────────────
function ScoreHistogram({ histogram }) {
    const svgRef = useRef(null)
    useEffect(() => {
        if (!histogram || !svgRef.current) return
        const el = svgRef.current
        const W = el.clientWidth || 600
        const H = 200
        const margin = { top: 16, right: 16, bottom: 40, left: 40 }
        const iW = W - margin.left - margin.right
        const iH = H - margin.top - margin.bottom

        d3.select(el).selectAll('*').remove()
        const svg = d3.select(el).attr('viewBox', `0 0 ${W} ${H}`).attr('width', W).attr('height', H)
        const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`)

        const maxCount = Math.max(...histogram.map(d => d.count), 1)
        const x = d3.scaleBand().domain(histogram.map(d => d.range)).range([0, iW]).padding(0.1)
        const y = d3.scaleLinear().domain([0, maxCount]).nice().range([iH, 0])
        const colorScale = d3.scaleLinear().domain([0, iW]).range(['#666688', '#00ff88'])

        g.append('g').attr('transform', `translate(0,${iH})`)
            .call(d3.axisBottom(x).tickSize(0))
            .select('.domain').remove()
        g.selectAll('.tick text').style('fill', '#666').style('font-size', '9px')

        g.append('g').call(d3.axisLeft(y).ticks(4).tickSize(-iW))
            .call(ax => ax.select('.domain').remove())
            .call(ax => ax.selectAll('line').attr('stroke', 'rgba(255,255,255,0.04)'))
            .call(ax => ax.selectAll('text').style('fill', '#888').style('font-size', '10px'))

        g.selectAll('.bar')
            .data(histogram)
            .enter().append('rect')
            .attr('x', d => x(d.range))
            .attr('y', iH)
            .attr('width', x.bandwidth())
            .attr('height', 0)
            .attr('rx', 4)
            .attr('fill', (_, i) => colorScale(i * (iW / histogram.length)))
            .attr('opacity', 0.85)
            .transition().duration(600)
            .attr('y', d => y(d.count))
            .attr('height', d => iH - y(d.count))
    }, [histogram])
    return <svg ref={svgRef} style={{ width: '100%' }} />
}

// ── Analytics Page ──────────────────────────────────────────
export default function Analytics() {
    const [tiers, setTiers] = useState(null)
    const [lifecycle, setLifecycle] = useState(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        Promise.all([getTierSummary(), getLifecycleData()])
            .then(([t, l]) => { setTiers(t.data); setLifecycle(l.data) })
            .catch(() => { })
            .finally(() => setLoading(false))
    }, [])

    if (loading) return (
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: 400, gap: 12, color: 'var(--text-muted)' }}>
            <Loader size={20} className="spin" /> Loading analytics…
        </div>
    )

    return (
        <div className="page-container fade-in-up">
            <div style={{ marginBottom: 28 }}>
                <h1 className="page-title">Lifecycle Analytics</h1>
                <p style={{ color: 'var(--text-muted)', marginTop: 6, fontSize: 14 }}>
                    Memory tier distribution, cognitive score histogram, and lifecycle state transitions
                </p>
            </div>

            {/* Tier summary cards */}
            {tiers && (
                <div className="stats-grid" style={{ marginBottom: 24 }}>
                    {Object.entries(tiers).map(([tier, stats]) => (
                        <div key={tier} className="stat-card" style={{ borderColor: stats.color + '33' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                                <div style={{ width: 8, height: 8, borderRadius: '50%', background: stats.color }} />
                                <span style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>{tier}</span>
                            </div>
                            <div className="stat-value" style={{ fontSize: 28, color: stats.color }}>{stats.count}</div>
                            <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                                Avg score: <span style={{ color: stats.color }}>{stats.avg_score.toFixed(3)}</span>
                            </div>
                            <div className="progress-bar-wrap">
                                <div className="progress-bar-fill" style={{ width: `${stats.avg_score * 100}%`, background: stats.color }} />
                            </div>
                            <div style={{ fontSize: 10, color: 'var(--text-muted)', lineHeight: 1.5 }}>{stats.description}</div>
                        </div>
                    ))}
                </div>
            )}

            {/* Bar chart */}
            <div className="card" style={{ marginBottom: 24 }}>
                <div style={{ fontWeight: 700, marginBottom: 4 }}>Documents per Tier</div>
                <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 16 }}>
                    Lifecycle tier distribution across the vault
                </div>
                {tiers
                    ? <TierBarChart tiers={tiers} />
                    : <div style={{ height: 220, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>No data</div>
                }
            </div>

            {/* Histogram */}
            <div className="card">
                <div style={{ fontWeight: 700, marginBottom: 4 }}>Cognitive Score Distribution</div>
                <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 16 }}>
                    Score ranges from 0.0 (Dormant) to 1.0 (Active) — color gradient reflects lifecycle progression
                </div>
                {lifecycle?.histogram
                    ? <ScoreHistogram histogram={lifecycle.histogram} />
                    : <div style={{ height: 200, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>
                        Upload documents to see score distribution
                    </div>
                }

                {/* Threshold legend */}
                {lifecycle?.tier_thresholds && (
                    <div style={{ display: 'flex', gap: 20, marginTop: 16, paddingTop: 16, borderTop: '1px solid var(--border)' }}>
                        {[
                            { label: 'Active ≥ 0.75', color: '#00ff88' },
                            { label: 'Contextual ≥ 0.50', color: '#00d4ff' },
                            { label: 'Archived ≥ 0.25', color: '#ff9500' },
                            { label: 'Dormant < 0.25', color: '#666688' },
                        ].map(({ label, color }) => (
                            <div key={label} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                                <div style={{ width: 10, height: 10, borderRadius: 2, background: color }} />
                                <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>{label}</span>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    )
}
