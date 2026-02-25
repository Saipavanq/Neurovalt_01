import { useState, useCallback, useRef } from 'react'
import { semanticSearch, recordAccess } from '../utils/api'
import { Search as SearchIcon, Loader, Zap, Filter } from 'lucide-react'
import TierBadge from '../components/TierBadge'
import ExplainPanel from '../components/ExplainPanel'
import toast from 'react-hot-toast'

const TIERS = ['All', 'Active', 'Contextual', 'Archived', 'Dormant']

function ResultCard({ result, rank }) {
    const [showExplain, setShowExplain] = useState(false)

    const scoreColor = result.final_score >= 0.75 ? '#00ff88'
        : result.final_score >= 0.50 ? '#00d4ff'
            : result.final_score >= 0.25 ? '#ff9500' : '#666688'

    return (
        <div className="result-card fade-in-up" style={{ animationDelay: `${rank * 0.06}s` }}>
            <div className="result-card-header">
                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                    <span style={{
                        width: 28, height: 28, borderRadius: '50%',
                        background: `${scoreColor}22`, border: `1px solid ${scoreColor}55`,
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        fontSize: 12, fontWeight: 700, color: scoreColor, flexShrink: 0,
                    }}>
                        {rank}
                    </span>
                    <div>
                        <div style={{ fontWeight: 600, fontSize: 14 }}>{result.filename}</div>
                        <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>
                            {result.file_type.toUpperCase()} · Query time applied
                        </div>
                    </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                    <TierBadge tier={result.tier} />
                    <span style={{
                        fontSize: 20, fontWeight: 800, color: scoreColor,
                        fontFamily: "'JetBrains Mono', monospace",
                    }}>
                        {result.final_score.toFixed(3)}
                    </span>
                </div>
            </div>

            <div className="result-card-body" style={{ paddingTop: 12 }}>
                {/* Score mini bars */}
                <div style={{ display: 'flex', gap: 8, marginBottom: 14, flexWrap: 'wrap' }}>
                    {[
                        { label: 'Semantic', pct: result.breakdown.semantic_percentage, color: '#a855f7' },
                        { label: 'Recency', val: result.breakdown.recency_score, color: '#00d4ff' },
                        { label: 'Access', val: result.breakdown.access_score, color: '#00ff88' },
                    ].map(({ label, pct, val, color }) => (
                        <div key={label} style={{
                            display: 'flex', alignItems: 'center', gap: 6,
                            padding: '4px 10px', borderRadius: 20,
                            background: `${color}11`, border: `1px solid ${color}33`,
                        }}>
                            <div style={{ width: 6, height: 6, borderRadius: '50%', background: color }} />
                            <span style={{ fontSize: 11, color }}>{label}: {pct ?? Math.round((val || 0) * 100)}%</span>
                        </div>
                    ))}
                </div>

                {/* Snippet */}
                {result.content_snippet && (
                    <p style={{ fontSize: 13, color: 'var(--text-muted)', lineHeight: 1.7, marginBottom: 14 }}>
                        "{result.content_snippet}"
                    </p>
                )}

                {/* Explain toggle */}
                <button
                    className="btn-ghost"
                    style={{ fontSize: 12, padding: '5px 14px' }}
                    onClick={() => setShowExplain(v => !v)}
                >
                    <Zap size={12} />
                    {showExplain ? 'Hide' : 'Show'} AI Explanation
                </button>

                {showExplain && (
                    <div style={{ marginTop: 12 }}>
                        <ExplainPanel breakdown={result.breakdown} />
                    </div>
                )}
            </div>
        </div>
    )
}

export default function Search() {
    const [query, setQuery] = useState('')
    const [results, setResults] = useState(null)
    const [loading, setLoading] = useState(false)
    const [tier, setTier] = useState('All')
    const [k, setK] = useState(5)
    const [queryTime, setQueryTime] = useState(null)
    const inputRef = useRef()

    const handleSearch = async (e) => {
        e?.preventDefault()
        if (!query.trim()) return
        setLoading(true)
        setResults(null)
        try {
            const res = await semanticSearch(
                query, 'default_user', k, 0, tier === 'All' ? null : tier
            )
            setResults(res.data)
            setQueryTime(res.data.query_time_ms)
        } catch {
            toast.error('Search failed — is the backend running?')
        }
        setLoading(false)
    }

    return (
        <div className="page-container fade-in-up">
            <div style={{ marginBottom: 28 }}>
                <h1 className="page-title">Semantic Search</h1>
                <p style={{ color: 'var(--text-muted)', marginTop: 6, fontSize: 14 }}>
                    Natural language queries · FAISS vector similarity · Cognitive re-ranking · Explainable results
                </p>
            </div>

            {/* Search form */}
            <form onSubmit={handleSearch} style={{ marginBottom: 20 }}>
                <div className="search-input-wrap" style={{ marginBottom: 14 }}>
                    <SearchIcon size={18} className="search-icon" />
                    <input
                        ref={inputRef}
                        type="text"
                        className="search-input"
                        placeholder="Search by concept, idea, or context…"
                        value={query}
                        onChange={e => setQuery(e.target.value)}
                    />
                </div>

                <div style={{ display: 'flex', gap: 12, alignItems: 'center', flexWrap: 'wrap' }}>
                    {/* Tier filter */}
                    <div style={{ display: 'flex', gap: 6 }}>
                        {TIERS.map(t => (
                            <button
                                key={t}
                                type="button"
                                onClick={() => setTier(t)}
                                className="btn-ghost"
                                style={{
                                    padding: '5px 12px', fontSize: 12,
                                    background: tier === t ? 'var(--cyan-dim)' : 'transparent',
                                    color: tier === t ? 'var(--cyan)' : 'var(--text-muted)',
                                    borderColor: tier === t ? 'var(--cyan)' : 'var(--border)',
                                }}
                            >
                                {t}
                            </button>
                        ))}
                    </div>

                    {/* K selector */}
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>Top</span>
                        {[3, 5, 10].map(n => (
                            <button
                                key={n}
                                type="button"
                                className="btn-ghost"
                                style={{
                                    padding: '4px 10px', fontSize: 12,
                                    background: k === n ? 'var(--cyan-dim)' : 'transparent',
                                    color: k === n ? 'var(--cyan)' : 'var(--text-muted)',
                                    borderColor: k === n ? 'var(--cyan)' : 'var(--border)',
                                }}
                                onClick={() => setK(n)}
                            >
                                {n}
                            </button>
                        ))}
                    </div>

                    <button type="submit" className="btn-primary" disabled={loading}>
                        {loading ? <Loader size={15} className="spin" /> : <SearchIcon size={15} />}
                        {loading ? 'Searching…' : 'Search'}
                    </button>
                </div>
            </form>

            {/* Query info */}
            {results && (
                <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 20, display: 'flex', gap: 16 }}>
                    <span>✦ {results.total_results} results for <em>"{results.query}"</em></span>
                    {queryTime && <span>⏱ {queryTime}ms</span>}
                </div>
            )}

            {/* Results */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
                {results?.results?.map(r => (
                    <ResultCard key={r.document_id} result={r} rank={r.rank} />
                ))}

                {results?.total_results === 0 && (
                    <div className="card" style={{ textAlign: 'center', padding: 48, color: 'var(--text-muted)' }}>
                        <SearchIcon size={40} style={{ margin: '0 auto 12px', opacity: 0.3 }} />
                        <div>No results found. Try uploading more documents or a different query.</div>
                    </div>
                )}
            </div>
        </div>
    )
}
