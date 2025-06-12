'use client'

import { useState, useRef, useEffect } from 'react'
import axios from 'axios'
import { FiUpload, FiSend } from 'react-icons/fi'
import { useDropzone } from 'react-dropzone'

export default function Home() {
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [uploaded, setUploaded] = useState(false)
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState<{ role: 'user' | 'assistant', content: string }[]>([])
  const [isStreaming, setIsStreaming] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: { 'application/pdf': ['.pdf'] },
    maxFiles: 1,
    onDrop: accepted => setFile(accepted[0])
  })

  const scrollToBottom = () => messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })

  useEffect(() => { scrollToBottom() }, [messages])

  const handleUpload = async () => {
    if (!file) return
    setUploading(true)
    const formData = new FormData()
    formData.append('file', file)

    try {
      await axios.post('http://localhost:8000/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      setUploaded(true)
      setMessages([{ role: 'assistant', content: '✅ Resume uploaded! Ask me anything about it.' }])
    } catch {
      setMessages([{ role: 'assistant', content: '❌ Upload failed. Please try again.' }])
    } finally {
      setUploading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || !uploaded) return

    const userMessage = input.trim()
    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: userMessage }])
    setIsStreaming(true)

    try {
      const res = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMessage })
      })

      const reader = res.body?.getReader()
      const decoder = new TextDecoder()
      let assistantMessage = ''
      setMessages(prev => [...prev, { role: 'assistant', content: '' }])

      while (true) {
        const { done, value } = await reader!.read()
        if (done) break
        const chunk = decoder.decode(value)
        const lines = chunk.split('\n').filter(Boolean)

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const text = line.replace('data: ', '')
            assistantMessage += text
            setMessages(prev => {
              const updated = [...prev]
              updated[updated.length - 1].content = assistantMessage
              return updated
            })
          }
        }
      }
    } catch {
      setMessages(prev => [...prev, { role: 'assistant', content: '⚠️ Failed to fetch response.' }])
    } finally {
      setIsStreaming(false)
    }
  }

  return (
    <main className="min-h-screen bg-gradient-to-b from-gray-100 to-white px-4 py-8 md:px-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-center text-gray-800 mb-10">Resume Chat Assistant</h1>

        {!uploaded && (
          <section className="mb-10">
            <div
              {...getRootProps()}
              className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition duration-300 ${
                isDragActive ? 'border-blue-400 bg-blue-50' : 'border-gray-300 hover:border-blue-500 hover:bg-blue-50'
              }`}
            >
              <input {...getInputProps()} />
              <FiUpload className="mx-auto text-5xl mb-3 text-blue-400" />
              <p className="text-gray-600">
                {file ? file.name : isDragActive ? 'Drop your resume here...' : 'Drag and drop your PDF resume or click to upload.'}
              </p>
            </div>
            {file && (
              <button
                onClick={handleUpload}
                disabled={uploading}
                className="w-full mt-4 bg-blue-600 text-white py-3 rounded-xl text-lg hover:bg-blue-700 disabled:opacity-50"
              >
                {uploading ? 'Uploading...' : 'Upload Resume'}
              </button>
            )}
          </section>
        )}

        <section className="bg-white shadow-2xl rounded-2xl p-6 h-[600px] flex flex-col border border-gray-100">
          <div className="flex-1 overflow-y-auto space-y-4 pr-2">
            {messages.map((msg, i) => (
              <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`rounded-xl px-4 py-3 max-w-[80%] text-sm shadow ${
                  msg.role === 'user' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-800'
                }`}>
                  {msg.content}
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>

          <form onSubmit={handleSubmit} className="mt-4 flex gap-3">
            <input
              type="text"
              value={input}
              onChange={e => setInput(e.target.value)}
              disabled={!uploaded || isStreaming}
              placeholder="Ask your resume anything..."
              className="flex-1 border border-gray-300 rounded-xl px-4 py-2 shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
            />
            <button
              type="submit"
              disabled={!input.trim() || isStreaming}
              className="bg-blue-600 text-white px-5 py-2 rounded-xl hover:bg-blue-700 disabled:opacity-50"
            >
              <FiSend className="text-xl" />
            </button>
          </form>
        </section>
      </div>
    </main>
  )
}
