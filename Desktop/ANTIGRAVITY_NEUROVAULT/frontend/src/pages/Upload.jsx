import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import toast from 'react-hot-toast'
import { uploadDocument, listDocuments, deleteDocument } from '../utils/api'
import { Upload as UploadIcon, FileText, CheckCircle, XCircle, Loader, Trash2, RefreshCw } from 'lucide-react'
import DocumentCard from '../components/DocumentCard'

function UploadZone({ onUpload }) {
    const [uploading, setUploading] = useState(false)
    const [desc, setDesc] = useState('')

    const onDrop = useCallback(async (acceptedFiles) => {
        if (!acceptedFiles.length) return
        setUploading(true)
        for (const file of acceptedFiles) {
            try {
                await uploadDocument(file, 'default_user', desc)
                toast.success(`✅ Uploaded: ${file.name}`, { style: { background: 'var(--bg-card)', color: 'var(--text-primary)' } })
            } catch (e) {
                toast.error(`❌ Failed: ${file.name}`)
            }
        }
        setUploading(false)
        onUpload?.()
    }, [desc, onUpload])

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: {
            'application/pdf': ['.pdf'],
            'text/plain': ['.txt', '.md'],
            'text/markdown': ['.md'],
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
            'image/png': ['.png'],
            'image/jpeg': ['.jpg', '.jpeg'],
        },
        multiple: true,
    })

    return (
        <div className="card">
            <div style={{ marginBottom: 16 }}>
                <label style={{ fontSize: 13, color: 'var(--text-muted)', display: 'block', marginBottom: 6 }}>
                    Document Description (optional)
                </label>
                <input
                    type="text"
                    value={desc}
                    onChange={e => setDesc(e.target.value)}
                    placeholder="e.g. Q4 financial report, research paper on NLP…"
                    style={{
                        width: '100%', background: 'var(--bg-surface)',
                        border: '1px solid var(--border)', borderRadius: 8,
                        padding: '8px 12px', fontSize: 14, color: 'var(--text-primary)',
                        outline: 'none', fontFamily: 'Inter, sans-serif',
                    }}
                />
            </div>

            <div {...getRootProps()} className={`dropzone${isDragActive ? ' active' : ''}`}>
                <input {...getInputProps()} />
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 16 }}>
                    {uploading
                        ? <Loader size={40} color="var(--cyan)" className="spin" />
                        : <UploadIcon size={40} color={isDragActive ? 'var(--cyan)' : 'var(--text-muted)'} />
                    }
                    <div>
                        <div style={{ fontWeight: 700, fontSize: 16, color: isDragActive ? 'var(--cyan)' : 'var(--text-primary)' }}>
                            {uploading ? 'Processing document…' : isDragActive ? 'Drop files here' : 'Drag & drop files here'}
                        </div>
                        <div style={{ fontSize: 13, color: 'var(--text-muted)', marginTop: 6 }}>
                            PDF, DOCX, TXT, MD, PNG, JPG supported
                        </div>
                        {!uploading && (
                            <div style={{ marginTop: 16 }}>
                                <span className="btn-primary" style={{ display: 'inline-flex' }}>
                                    <UploadIcon size={15} /> Browse Files
                                </span>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            <div style={{ marginTop: 16, display: 'flex', gap: 12, flexWrap: 'wrap' }}>
                {['PDF', 'DOCX', 'TXT / MD', 'PNG / JPG'].map(t => (
                    <span key={t} style={{
                        fontSize: 11, padding: '3px 10px', borderRadius: 20,
                        background: 'var(--bg-surface)', color: 'var(--text-muted)',
                        border: '1px solid var(--border)',
                    }}>{t}</span>
                ))}
            </div>
        </div>
    )
}

export default function Upload() {
    const [docs, setDocs] = useState([])
    const [loading, setLoading] = useState(false)

    const fetchDocs = async () => {
        setLoading(true)
        try {
            const res = await listDocuments()
            setDocs(res.data)
        } catch {
            toast.error('Failed to load documents')
        }
        setLoading(false)
    }

    const handleDelete = async (id) => {
        try {
            await deleteDocument(id)
            toast.success('Document deleted')
            fetchDocs()
        } catch {
            toast.error('Delete failed')
        }
    }

    return (
        <div className="page-container fade-in-up">
            <div style={{ marginBottom: 28 }}>
                <h1 className="page-title">Ingest Documents</h1>
                <p style={{ color: 'var(--text-muted)', marginTop: 6, fontSize: 14 }}>
                    Files are parsed, chunked, embedded (384-dim), and indexed into FAISS automatically
                </p>
            </div>

            <UploadZone onUpload={fetchDocs} />

            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', margin: '28px 0 16px' }}>
                <span style={{ fontWeight: 700, fontSize: 16 }}>Document Vault ({docs.length})</span>
                <button className="btn-ghost" onClick={fetchDocs}>
                    <RefreshCw size={14} className={loading ? 'spin' : ''} /> Refresh
                </button>
            </div>

            {docs.length === 0 && !loading && (
                <div className="card" style={{ textAlign: 'center', padding: 48, color: 'var(--text-muted)' }}>
                    <FileText size={40} style={{ margin: '0 auto 12px', opacity: 0.4 }} />
                    <div>No documents yet. Upload your first file above.</div>
                </div>
            )}

            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                {docs.map(doc => (
                    <DocumentCard key={doc.id} doc={doc} onDelete={handleDelete} />
                ))}
            </div>
        </div>
    )
}
