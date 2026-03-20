export const TIER_CLASSES = {
    Active: 'tier-active',
    Contextual: 'tier-contextual',
    Archived: 'tier-archived',
    Dormant: 'tier-dormant',
}

export const TIER_COLORS = {
    Active: '#00ff88',
    Contextual: '#00d4ff',
    Archived: '#ff9500',
    Dormant: '#666688',
}

export const TIER_DOTS = {
    Active: '🟢',
    Contextual: '🔵',
    Archived: '🟠',
    Dormant: '⚫',
}

export default function TierBadge({ tier, size = 'sm' }) {
    const cls = TIER_CLASSES[tier] || 'tier-dormant'
    const style = size === 'lg'
        ? { fontSize: 13, padding: '5px 14px' }
        : {}
    return (
        <span className={`tier-badge ${cls}`} style={style}>
            <span style={{ width: 6, height: 6, borderRadius: '50%', background: TIER_COLORS[tier], display: 'inline-block' }} />
            {tier}
        </span>
    )
}
