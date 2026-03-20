import { useEffect, useRef, useState } from 'react'
import * as d3 from 'd3'
import { getAnalytics, getLifecycleData } from '../utils/api'
import { TIER_COLORS } from '../components/TierBadge'
import TierBadge from '../components/TierBadge'
import { Files, Brain, TrendingUp, Layers, Loader } from 'lucide-react'

// ── D3 Force Graph ──────────────────────────────────────
function ForceGraph({ nodes }) {
    const svgRef = useRef(null)

    useEffect(() => {
        if (!nodes?.length || !svgRef.current) return
        const el = svgRef.current
        const W = el.clientWidth || 700
        const H = 380

        d3.select(el).selectAll('*').remove()
        const svg = d3.select(el)
            .attr('viewBox', `0 0 ${W} ${H}`)
            .attr('width', W).attr('height', H)

        // Background
        svg.append('rect').attr('width', W).attr('height', H).attr('fill', 'transparent')

        const sim = d3.forceSimulation(nodes)
            .force('charge', d3.forceManyBody().strength(-60))
            .force('center', d3.forceCenter(W / 2, H / 2))
            .force('collision', d3.forceCollide().radius(d => d.r + 4))

        const g = svg.append('g')

        // Glow filter
        const defs = svg.append('defs')
        const filter = defs.append('filter').attr('id', 'glow')
        filter.append('feGaussianBlur').attr('stdDeviation', '3').attr('result', 'coloredBlur')
        const merge = filter.append('feMerge')
        merge.append('feMergeNode').attr('in', 'coloredBlur')
        merge.append('feMergeNode').attr('in', 'SourceGraphic')

        const node = g.selectAll('circle')
            .data(nodes)
            .enter().append('circle')
            .attr('r', d => d.r)
            .attr('fill', d => d.color + '33')
            .attr('stroke', d => d.color)
            .attr('stroke-width', 1.5)
            .attr('filter', 'url(#glow)')
            .style('cursor', 'pointer')

        const label = g.selectAll('text')
            .data(nodes)
            .enter().append('text')
            .text(d => d.filename.length > 12 ? d.filename.slice(0, 12) + '…' : d.filename)
            .attr('text-anchor', 'middle')
            .attr('dy', '0.35em')
            .attr('font-size', 9)
            .attr('fill', d => d.color)
            .style('pointer-events', 'none')

        // Tooltip
        const tooltip = d3.select('body').append('div')
            .style('position', 'absolute')
            .style('background', 'rgba(13,21,37,0.95)')
            .style('border', '1px solid rgba(0,212,255,0.3)')
            .style('border-radius', '8px')
            .style('padding', '8px 12px')
            .style('font-size', '12px')
            .style('color', '#f0f4ff')
            .style('pointer-events', 'none')
            .style('opacity', 0)
            .style('z-index', 9999)

        node
            .on('mouseover', (event, d) => {
                tooltip.transition().duration(100).style('opacity', 1)
                tooltip.html(`<b>${d.filename}</b><br/>Score: ${d.score.toFixed(3)}<br/>Tier: ${d.tier}<br/>Access: ${d.access_count}×`)
                    .style('left', (event.pageX + 12) + 'px')
                    .style('top', (event.pageY - 28) + 'px')
            })
            .on('mousemove', (event) => {
                tooltip.style('left', (event.pageX + 12) + 'px').style('top', (event.pageY - 28) + 'px')
            })
            .on('mouseout', () => tooltip.transition().duration(200).style('opacity', 0))

        sim.on('tick', () => {
            node.attr('cx', d => d.x).attr('cy', d => d.y)
            label.attr('x', d => d.x).attr('y', d => d.y)
        })

        return () => {
            sim.stop()
            tooltip.remove()
        }
    }, [nodes])

    return <svg ref={svgRef} style={{ width: '100%', height: 380 }} />
}

// ── Dashboard Page ──────────────────────────────────────
export default function Dashboard() {
    const [data, setData] = useState(null)
    const [lifecycle, setLifecycle] = useState(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        Promise.all([getAnalytics(), getLifecycleData()])
            .then(([a, l]) => {
                setData(a.data)
                setLifecycle(l.data)
            })
            .catch(() => { })
            .finally(() => setLoading(false))
    }, [])

    const graphNodes = lifecycle?.nodes?.map(n => ({
        ...n,
        r: 8 + n.score * 20,
        color: TIER_COLORS[n.tier] || '#888',
    })) || []

    if (loading) return (
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: 400, gap: 12, color: 'var(--text-muted)' }}>
            <Loader size={20} className="spin" /> Loading intelligence...
        </div>
    )

    const tiers = data?.tier_distribution || []

    return (
        <div className="page-container fade-in-up">
            {/* Header */}
            <div style={{ marginBottom: 32 }}>
                <h1 className="page-title">Cognitive Dashboard</h1>
                <p style={{ color: 'var(--text-muted)', marginTop: 6, fontSize: 14 }}>
                    Real-time intelligence layer — semantic memory, lifecycle states & cognitive scoring
                </p>
            </div>

            {/* Stats Grid */}
            <div className="stats-grid" style={{ marginBottom: 28 }}>
                <div className="stat-card">
                    <Files size={20} color="var(--cyan)" />
                    <div className="stat-value">{data?.total_documents ?? 0}</div>
                    <div className="stat-label">Total Documents</div>
                </div>
                <div className="stat-card">
                    <Brain size={20} color="var(--purple)" />
                    <div className="stat-value">{data?.avg_cognitive_score?.toFixed(3) ?? '0.000'}</div>
                    <div className="stat-label">Avg Cognitive Score</div>
                </div>
                {tiers.map(t => (
                    <div className="stat-card" key={t.tier}>
                        <div style={{ width: 8, height: 8, borderRadius: '50%', background: t.color }} />
                        <div className="stat-value" style={{ fontSize: 26, color: t.color }}>{t.count}</div>
                        <div className="stat-label">{t.tier} Tier</div>
                    </div>
                ))}
            </div>

            {/* Force Graph */}
            <div className="card" style={{ marginBottom: 24 }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
                    <div>
                        <div style={{ fontWeight: 700, marginBottom: 2 }}>Memory Constellation</div>
                        <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                            Node size = cognitive score · Color = lifecycle tier
                        </div>
                    </div>
                    <div style={{ display: 'flex', gap: 10 }}>
                        {Object.entries(TIER_COLORS).map(([t, c]) => (
                            <div key={t} style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
                                <div style={{ width: 8, height: 8, borderRadius: '50%', background: c }} />
                                <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>{t}</span>
                            </div>
                        ))}
                    </div>
                </div>
                {graphNodes.length > 0
                    ? <ForceGraph nodes={graphNodes} />
                    : (
                        <div style={{ height: 200, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)', fontSize: 14 }}>
                            No documents yet — upload files to see your memory constellation
                        </div>
                    )
                }
            </div>

            {/* Top Documents */}
            {data?.top_documents?.length > 0 && (
                <div className="card">
                    <div style={{ fontWeight: 700, marginBottom: 16 }}>Top Cognitive Documents</div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                        {data.top_documents.slice(0, 5).map((doc, i) => (
                            <div key={doc.id} style={{
                                display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                                padding: '10px 14px', background: 'var(--bg-surface)', borderRadius: 10,
                                border: '1px solid var(--border)',
                            }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                                    <span style={{ fontSize: 12, color: 'var(--text-muted)', width: 20 }}>#{i + 1}</span>
                                    <div>
                                        <div style={{ fontSize: 13, fontWeight: 600 }}>{doc.filename}</div>
                                        <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>{doc.access_count}× accessed</div>
                                    </div>
                                </div>
                                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                                    <TierBadge tier={doc.tier} />
                                    <span style={{ fontFamily: 'monospace', fontWeight: 700, color: 'var(--cyan)' }}>
                                        {doc.cognitive_score.toFixed(3)}
                                    </span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    )
}
