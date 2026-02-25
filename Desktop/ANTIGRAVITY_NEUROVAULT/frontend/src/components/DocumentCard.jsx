import { useState } from 'react'
import { File, FileText, Image, Trash2, ChevronDown, ChevronUp } from 'lucide-react'
import TierBadge from './TierBadge'
import ExplainPanel from './ExplainPanel'

function fileIcon(type) {
    if (type === 'pdf') return <FileText size={16} color="var(--red)" />
    if (['png', 'jpg', 'jpeg', 'tiff', 'bmp'].includes(type)) return <Image size={16} color="var(--purple)" />
    return <File size={16} color="var(--cyan)" />
}

function formatBytes(b) {
    if (b < 1024) return `${b} B`
    if (b < 1048576) return `${(b / 1024).toFixed(1)} KB`
    return `${(b / 1048576).toFixed(1)} MB`
}

export default function DocumentCard({ doc, onDelete, explanation }) {
    const [expanded, setExpanded] = useState(false)

    const scoreColor = doc.cognitive_score >= 0.75 ? '#00ff88'
        : doc.cognitive_score >= 0.50 ? '#00d4ff'
            : doc.cognitive_score >= 0.25 ? '#ff9500'
                : '#666688'

    return (
        <div className="result-card fade-in-up">
            <div className="result-card-header">
                <div style={{ display: 'flex', alignItems: 'flex-start', gap: 12, flex: 1, minWidth: 0 }}>
                    <div style={{
                        width: 36, height: 36, borderRadius: 8,
                        background: 'rgba(255,255,255,0.05)',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        flexShrink: 0,
                    }}>
                        {fileIcon(doc.file_type)}
                    </div>
                    <div style={{ minWidth: 0 }}>
                        <div style={{
                            fontWeight: 600, fontSize: 14, color: 'var(--text-primary)',
                            whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis',
                            maxWidth: 280,
                        }}>
                            {doc.filename}
                        </div>
                        <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>
                            {formatBytes(doc.file_size)} · {doc.chunk_count} chunks · {doc.access_count}× accessed
                        </div>
                    </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexShrink: 0 }}>
                    <TierBadge tier={doc.tier} />
                    <span style={{
                        fontFamily: "'JetBrains Mono', monospace",
                        fontSize: 18, fontWeight: 700, color: scoreColor,
                    }}>
                        {doc.cognitive_score.toFixed(3)}
                    </span>
                    {onDelete && (
                        <button className="btn-danger" onClick={() => onDelete(doc.id)}>
                            <Trash2 size={13} />
                        </button>
                    )}
                </div>
            </div>

            {doc.description && (
                <div style={{ padding: '0 20px 12px', fontSize: 13, color: 'var(--text-muted)' }}>
                    {doc.description}
                </div>
            )}

            {explanation && (
                <div style={{ padding: '0 16px 16px' }}>
                    <button
                        className="btn-ghost"
                        style={{ fontSize: 12, padding: '4px 12px', marginBottom: 10 }}
                        onClick={() => setExpanded(e => !e)}
                    >
                        {expanded ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
                        {expanded ? 'Hide' : 'Show'} AI Explanation
                    </button>
                    {expanded && <ExplainPanel breakdown={explanation} />}
                </div>
            )}
        </div>
    )
}
