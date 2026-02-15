/**
 * AI流式生成Hook
 * 支持SSE流式响应和打字机效果
 */

import { useState, useCallback, useRef, useEffect } from 'react'
import { API_URL } from '@/lib/api'

export interface StreamGenerationOptions {
  topic: string
  title?: string
  style?: string
  provider?: string
  model?: string
  temperature?: number
  maxTokens?: number
}

export interface GenerationProgress {
  type: 'start' | 'progress' | 'title' | 'content' | 'complete' | 'error'
  progress?: number
  message?: string
  title?: string
  chunk?: string
  content?: string
  data?: {
    title: string
    content: string
    summary: string
    word_count: number
    style: string
  }
  error?: string
}

export interface UseStreamGenerationReturn {
  isGenerating: boolean
  progress: GenerationProgress | null
  generatedContent: string
  generatedTitle: string
  error: string | null
  startGeneration: (options: StreamGenerationOptions) => void
  stopGeneration: () => void
  reset: () => void
}

export function useStreamGeneration(): UseStreamGenerationReturn {
  const [isGenerating, setIsGenerating] = useState(false)
  const [progress, setProgress] = useState<GenerationProgress | null>(null)
  const [generatedContent, setGeneratedContent] = useState('')
  const [generatedTitle, setGeneratedTitle] = useState('')
  const [error, setError] = useState<string | null>(null)
  
  const eventSourceRef = useRef<EventSource | null>(null)
  const abortControllerRef = useRef<AbortController | null>(null)

  const startGeneration = useCallback((options: StreamGenerationOptions) => {
    // 重置状态
    setIsGenerating(true)
    setProgress(null)
    setGeneratedContent('')
    setGeneratedTitle('')
    setError(null)

    // 创建AbortController用于取消请求
    abortControllerRef.current = new AbortController()

    // 使用fetch API而不是EventSource，以便支持POST请求
    const generate = async () => {
      try {
        const response = await fetch(`${API_URL}/api/ai-stream/stream-generate`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            topic: options.topic,
            title: options.title,
            style: options.style || 'professional',
            provider: options.provider,
            model: options.model,
            temperature: options.temperature || 0.7,
            max_tokens: options.maxTokens || 4000,
          }),
          signal: abortControllerRef.current?.signal,
        })

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }

        const reader = response.body?.getReader()
        const decoder = new TextDecoder()

        if (!reader) {
          throw new Error('No reader available')
        }

        let buffer = ''

        while (true) {
          const { done, value } = await reader.read()
          
          if (done) {
            break
          }

          // 解码收到的数据
          buffer += decoder.decode(value, { stream: true })

          // 处理SSE格式的数据
          const lines = buffer.split('\n\n')
          buffer = lines.pop() || '' // 保留不完整的部分

          for (const line of lines) {
            const trimmedLine = line.trim()
            if (!trimmedLine) continue

            // 解析SSE事件
            const eventLines = trimmedLine.split('\n')
            let eventType = 'message'
            let eventData = ''

            for (const eventLine of eventLines) {
              if (eventLine.startsWith('event:')) {
                eventType = eventLine.slice(6).trim()
              } else if (eventLine.startsWith('data:')) {
                eventData += eventLine.slice(5).trim()
              }
            }

            if (eventData) {
              try {
                const parsedData = JSON.parse(eventData)
                setProgress(parsedData)

                // 根据事件类型更新状态
                switch (parsedData.type) {
                  case 'title':
                    if (parsedData.title) {
                      setGeneratedTitle(parsedData.title)
                    }
                    break
                  case 'content':
                    if (parsedData.content) {
                      setGeneratedContent(parsedData.content)
                    }
                    break
                  case 'complete':
                    if (parsedData.data) {
                      setGeneratedTitle(parsedData.data.title)
                      setGeneratedContent(parsedData.data.content)
                    }
                    setIsGenerating(false)
                    break
                  case 'error':
                    setError(parsedData.error || '生成失败')
                    setIsGenerating(false)
                    break
                }
              } catch (e) {
                console.warn('Failed to parse SSE data:', eventData)
              }
            }
          }
        }
      } catch (err: any) {
        if (err.name === 'AbortError') {
          console.log('Generation aborted')
        } else {
          setError(err.message || '生成过程中发生错误')
          setIsGenerating(false)
        }
      }
    }

    generate()
  }, [])

  const stopGeneration = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
      abortControllerRef.current = null
    }
    setIsGenerating(false)
  }, [])

  const reset = useCallback(() => {
    stopGeneration()
    setProgress(null)
    setGeneratedContent('')
    setGeneratedTitle('')
    setError(null)
  }, [stopGeneration])

  // 清理
  useEffect(() => {
    return () => {
      stopGeneration()
    }
  }, [stopGeneration])

  return {
    isGenerating,
    progress,
    generatedContent,
    generatedTitle,
    error,
    startGeneration,
    stopGeneration,
    reset,
  }
}
