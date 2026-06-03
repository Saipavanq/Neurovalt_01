import { TIER_CLASSES, TIER_COLORS } from '../utils/tiers'

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
