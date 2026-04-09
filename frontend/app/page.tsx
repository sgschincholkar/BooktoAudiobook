'use client'

import { useState, useCallback, useEffect } from 'react'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const VOICES = [
  { id: 'EXAVITQu4vr4xnSDxMaL', name: 'Sarah (Female, American)' },
  { id: 'TX3LPaxmHKxFdv7VOQHJ', name: 'Liam (Male, Neutral)' },
  { id: 'XB0fDUnXU5powFXDhCwa', name: 'Charlotte (Female, British)' },
  { id: 'nPczCjzI2devNBz1zQrb', name: 'Brian (Male, Deep)' },
  { id: 'onwK4e9ZLuTAKqWW03F9', name: 'Daniel (Male, British)' },
]

interface Chapter {
  title: string
  status: 'pending' | 'processing' | 'done' | 'error'
  progress?: number
  word_count?: number
}

interface JobStatus {
  status: 'pending' | 'processing' | 'completed' | 'error'
  chapters: Chapter[]
  error?: string
}

export default function Home() {
  const [file, setFile] = useState<File | null>(null)
  const [voiceId, setVoiceId] = useState<string>(VOICES[0].id)
  const [jobId, setJobId] = useState<string | null>(null)
  const [chapters, setChapters] = useState<Chapter[]>([])
  const [jobStatus, setJobStatus] = useState<JobStatus | null>(null)
  const [isDragging, setIsDragging] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)

  const getHelpfulError = (message: string): string => {
    const lower = message.toLowerCase()
    if (
      lower.includes('no extractable text') ||
      lower.includes('scanned pdf') ||
      lower.includes('ocr')
    ) {
      return 'This file appears to be a scanned/image PDF with no selectable text. Run OCR first, then upload again.'
    }
    return message
  }

  const isOcrRelatedError = (message: string | null): boolean => {
    if (!message) return false
    const lower = message.toLowerCase()
    return (
      lower.includes('no extractable text') ||
      lower.includes('scanned pdf') ||
      lower.includes('ocr') ||
      lower.includes('scanned/image pdf')
    )
  }

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const validateFile = (file: File): boolean => {
    const validTypes = [
      'application/pdf',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    ]

    if (!validTypes.includes(file.type)) {
      setError('Only PDF and DOCX files are supported')
      return false
    }

    const maxSize = 50 * 1024 * 1024 // 50MB
    if (file.size > maxSize) {
      setError('File size must be under 50MB')
      return false
    }

    return true
  }

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    setError(null)

    const droppedFile = e.dataTransfer.files[0]
    if (droppedFile && validateFile(droppedFile)) {
      setFile(droppedFile)
    }
  }, [])

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    setError(null)
    const selectedFile = e.target.files?.[0]
    if (selectedFile && validateFile(selectedFile)) {
      setFile(selectedFile)
    }
  }

  const handleUpload = async () => {
    if (!file) return

    setError(null)
    setIsGenerating(true)

    try {
      const formData = new FormData()
      formData.append('file', file)

      const uploadRes = await fetch(`${API_URL}/upload`, {
        method: 'POST',
        body: formData,
      })

      if (!uploadRes.ok) {
        const errorData = await uploadRes.json()
        throw new Error(getHelpfulError(errorData.detail || 'Upload failed'))
      }

      const uploadData = await uploadRes.json()
      setJobId(uploadData.job_id)
      setChapters(uploadData.chapters.map((ch: Chapter) => ({ ...ch, status: 'pending' })))

      const generateRes = await fetch(`${API_URL}/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          job_id: uploadData.job_id,
          voice_id: voiceId,
        }),
      })

      if (!generateRes.ok) {
        const errorData = await generateRes.json()
        throw new Error(getHelpfulError(errorData.detail || 'Generation failed'))
      }
    } catch (err) {
      setError(err instanceof Error ? getHelpfulError(err.message) : 'An error occurred')
      setIsGenerating(false)
    }
  }

  useEffect(() => {
    if (!jobId || !isGenerating) return

    const pollInterval = setInterval(async () => {
      try {
        const res = await fetch(`${API_URL}/status/${jobId}`)
        if (!res.ok) throw new Error('Status check failed')

        const data: JobStatus = await res.json()
        setJobStatus(data)
        setChapters(data.chapters)

        if (data.status === 'completed' || data.status === 'error') {
          setIsGenerating(false)
          clearInterval(pollInterval)
          if (data.status === 'error') {
            setError(getHelpfulError(data.error || 'Generation failed'))
          }
        }
      } catch (err) {
        console.error('Poll error:', err)
      }
    }, 2000)

    return () => clearInterval(pollInterval)
  }, [jobId, isGenerating])

  const handleDownload = async () => {
    if (!jobId) return

    try {
      const res = await fetch(`${API_URL}/download/${jobId}`)
      if (!res.ok) throw new Error('Download failed')

      const blob = await res.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `audiobook_${jobId}.zip`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Download failed')
    }
  }

  return (
    <main className="min-h-screen p-8 max-w-4xl mx-auto">
      <h1 className="text-4xl font-bold mb-2">Book to Audiobook</h1>
      <p className="text-gray-600 dark:text-gray-400 mb-8">
        Convert your books into professional audiobooks with AI voices
      </p>

      {error && (
        <div className="mb-6 p-4 bg-red-100 dark:bg-red-900/30 border border-red-400 dark:border-red-600 rounded-lg text-red-700 dark:text-red-300">
          <p>{error}</p>
          {isOcrRelatedError(error) && (
            <a
              href="https://ocrmypdf.readthedocs.io/en/latest/introduction.html"
              target="_blank"
              rel="noreferrer"
              className="inline-block mt-2 underline text-red-800 dark:text-red-200 hover:opacity-90"
            >
              How to OCR this PDF (free)
            </a>
          )}
        </div>
      )}

      <div
        className={`border-2 border-dashed rounded-lg p-12 mb-6 text-center transition-colors ${
          isDragging
            ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
            : 'border-gray-300 dark:border-gray-700'
        }`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <input
          type="file"
          accept=".pdf,.docx"
          onChange={handleFileSelect}
          className="hidden"
          id="file-upload"
          disabled={isGenerating}
        />
        <label
          htmlFor="file-upload"
          className="cursor-pointer text-gray-700 dark:text-gray-300"
        >
          {file ? (
            <div>
              <p className="text-lg font-semibold">{file.name}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
                {(file.size / 1024 / 1024).toFixed(2)} MB
              </p>
            </div>
          ) : (
            <div>
              <p className="text-lg mb-2">Drag and drop your book here</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                or click to browse (PDF or DOCX, max 50MB)
              </p>
            </div>
          )}
        </label>
      </div>

      <div className="mb-6">
        <label htmlFor="voice" className="block text-sm font-medium mb-2">
          Select Voice
        </label>
        <select
          id="voice"
          value={voiceId}
          onChange={(e) => setVoiceId(e.target.value)}
          disabled={isGenerating}
          className="w-full p-3 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800"
        >
          {VOICES.map((voice) => (
            <option key={voice.id} value={voice.id}>
              {voice.name}
            </option>
          ))}
        </select>
      </div>

      <button
        onClick={handleUpload}
        disabled={!file || isGenerating}
        className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white font-semibold py-3 px-6 rounded-lg transition-colors mb-8"
      >
        {isGenerating ? 'Generating...' : 'Generate Audiobook'}
      </button>

      {chapters.length > 0 && (
        <div className="mb-6">
          <h2 className="text-2xl font-bold mb-4">Progress</h2>
          <div className="space-y-3">
            {chapters.map((chapter, idx) => (
              <div
                key={idx}
                className="p-4 border border-gray-300 dark:border-gray-700 rounded-lg"
              >
                <div className="flex justify-between items-center mb-2">
                  <h3 className="font-semibold">{chapter.title}</h3>
                  <span
                    className={`px-3 py-1 rounded-full text-sm ${
                      chapter.status === 'done'
                        ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300'
                        : chapter.status === 'processing'
                        ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300'
                        : chapter.status === 'error'
                        ? 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300'
                        : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300'
                    }`}
                  >
                    {chapter.status}
                  </span>
                </div>
                {chapter.word_count && (
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    {chapter.word_count.toLocaleString()} words
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {jobStatus?.status === 'completed' && (
        <button
          onClick={handleDownload}
          className="w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors"
        >
          Download ZIP
        </button>
      )}
    </main>
  )
}
