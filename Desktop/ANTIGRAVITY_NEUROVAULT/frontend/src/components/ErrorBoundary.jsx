import { Component } from 'react'

export default class ErrorBoundary extends Component {
    constructor(props) {
        super(props)
        this.state = { error: null }
    }

    static getDerivedStateFromError(error) {
        return { error }
    }

    componentDidCatch(error, info) {
        console.error('ErrorBoundary caught:', error, info)
    }

    render() {
        if (this.state.error) {
            return (
                <div style={{
                    display: 'flex', flexDirection: 'column', alignItems: 'center',
                    justifyContent: 'center', height: '100vh', gap: 16,
                    padding: 40, textAlign: 'center',
                    background: 'var(--bg-app)', color: 'var(--text-primary)',
                }}>
                    <div style={{
                        width: 48, height: 48, borderRadius: '50%',
                        background: 'rgba(255,0,0,0.1)', border: '1px solid rgba(255,0,0,0.3)',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        fontSize: 24,
                    }}>!</div>
                    <h2 style={{ margin: 0 }}>Something went wrong</h2>
                    <p style={{ color: 'var(--text-muted)', maxWidth: 400, fontSize: 13 }}>
                        {this.state.error.message}
                    </p>
                    <button className="btn-primary" onClick={() => window.location.reload()}>
                        Reload Page
                    </button>
                </div>
            )
        }
        return this.props.children
    }
}
