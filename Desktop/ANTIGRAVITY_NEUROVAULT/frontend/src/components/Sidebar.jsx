import { NavLink, useLocation } from 'react-router-dom'
import {
    Brain, LayoutDashboard, Upload, Search,
    BarChart3, Zap, Github
} from 'lucide-react'

const NAV = [
    { path: '/', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/upload', label: 'Upload', icon: Upload },
    { path: '/search', label: 'Search', icon: Search },
    { path: '/analytics', label: 'Analytics', icon: BarChart3 },
]

export default function Sidebar() {
    return (
        <aside className="sidebar">
            {/* Logo */}
            <div style={{ padding: '24px 20px 16px', borderBottom: '1px solid var(--border)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <div style={{
                        width: 38, height: 38,
                        background: 'linear-gradient(135deg, var(--cyan), var(--purple))',
                        borderRadius: 10,
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                    }}>
                        <Brain size={20} color="#000" />
                    </div>
                    <div>
                        <div style={{ fontWeight: 800, fontSize: 16, color: 'var(--text-primary)' }}>NeuroVault</div>
                        <div style={{ fontSize: 10, color: 'var(--text-muted)', letterSpacing: '0.08em' }}>COGNITIVE AI</div>
                    </div>
                </div>
            </div>

            {/* Navigation */}
            <nav style={{ flex: 1, padding: '12px 0' }}>
                <div style={{ padding: '8px 16px 6px', fontSize: 10, color: 'var(--text-muted)', letterSpacing: '0.1em', textTransform: 'uppercase' }}>
                    Navigation
                </div>
                {NAV.map(({ path, label, icon: Icon }) => (
                    <NavLink
                        key={path}
                        to={path}
                        end={path === '/'}
                        className={({ isActive }) => `nav-item${isActive ? ' active' : ''}`}
                    >
                        <Icon size={16} />
                        {label}
                    </NavLink>
                ))}
            </nav>

            {/* Footer */}
            <div style={{ padding: '16px', borderTop: '1px solid var(--border)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '8px 8px' }}>
                    <Zap size={14} color="var(--cyan)" />
                    <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>all-MiniLM-L6-v2</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '4px 8px' }}>
                    <div style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--green)' }} />
                    <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>FAISS Index Active</span>
                </div>
            </div>
        </aside>
    )
}
