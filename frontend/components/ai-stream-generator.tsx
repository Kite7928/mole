/**
 * AI流式生成组件
 * 支持打字机效果和实时进度显示
 */

'use client'

import { useState, useEffect, useRef } from 'react'
import {
  Sparkles,
  Loader2,
  Pause,
  Play,
  Square,
  CheckCircle,
  AlertCircle,
  Clock,
  Type,
  FileText,
  Zap
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { useStreamGeneration, StreamGenerationOptions } from '@/hooks/useStreamGeneration'

interface AIStreamGeneratorProps {
  topic: string
  title?: string
  style?: string
  provider?: string
  model?: string
  onComplete?: (result: {
    title: string
    content: string
    summary: string
    wordCount: number
  }) => void
  onError?: (error: string) => void
}

export default function AIStreamGenerator({
  topic,
  title,
  style = 'professional',
  provider,
  model,
  onComplete,
  onError,
}: AIStreamGeneratorProps) {
  const {
    isGenerating,
    progress,
    generatedContent,
    generatedTitle,
    error,
    startGeneration,
    stopGeneration,
  } = useStreamGeneration()

  const [isPaused, setIsPaused] = useState(false)
  const [displayedContent, setDisplayedContent] = useState('')
  const [typingSpeed, setTypingSpeed] = useState(30) // 毫秒/字符
  const contentRef = useRef<HTMLDivElement>(null)
  const typingTimeoutRef = useRef<NodeJS.Timeout | null>(null)

  // 打字机效果
  useEffect(() => {
    if (!isGenerating || !generatedContent) return

    const targetContent = generatedContent
    let currentIndex = displayedContent.length

    const typeNextChar = () => {
      if (currentIndex < targetContent.length && !isPaused) {
        const nextChunk = targetContent.slice(currentIndex, currentIndex + 3) // 每次显示3个字符
        setDisplayedContent(targetContent.slice(0, currentIndex + 3))
        currentIndex += 3

        // 自动滚动到底部
        if (contentRef.current) {
          contentRef.current.scrollTop = contentRef.current.scrollHeight
        }

        // 动态调整打字速度
        const char = nextChunk[nextChunk.length - 1]
        const delay = char === '。' || char === '！' || char === '？' 
          ? typingSpeed * 5 // 句末停顿
          : char === '，' || char === '；'
          ? typingSpeed * 2 // 逗号短停
          : typingSpeed

        typingTimeoutRef.current = setTimeout(typeNextChar, delay)
      }
    }

    typeNextChar()

    return () => {
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current)
      }
    }
  }, [generatedContent, isGenerating, isPaused, typingSpeed])

  // 完成回调
  useEffect(() => {
    if (progress?.type === 'complete' && progress.data) {
      onComplete?.({
        title: progress.data.title,
        content: progress.data.content,
        summary: progress.data.summary,
        wordCount: progress.data.word_count,
      })
    }
  }, [progress, onComplete])

  // 错误回调
  useEffect(() => {
    if (error) {
      onError?.(error)
    }
  }, [error, onError])

  // 开始生成
  const handleStart = () => {
    setDisplayedContent('')
    startGeneration({
      topic,
      title,
      style,
      provider,
      model,
    })
  }

  // 暂停/继续
  const handlePauseToggle = () => {
    setIsPaused(!isPaused)
  }

  // 停止生成
  const handleStop = () => {
    stopGeneration()
    setIsPaused(false)
  }

  // 获取进度百分比
  const getProgressPercentage = () => {
    if (!progress) return 0
    if (progress.type === 'complete') return 100
    return progress.progress || 0
  }

  // 获取状态图标
  const getStatusIcon = () => {
    if (error) return <AlertCircle className="w-5 h-5 text-red-500" />
    if (progress?.type === 'complete') return <CheckCircle className="w-5 h-5 text-green-500" />
    if (isPaused) return <Pause className="w-5 h-5 text-yellow-500" />
    if (isGenerating) return <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />
    return <Sparkles className="w-5 h-5 text-purple-500" />
  }

  // 获取状态文本
  const getStatusText = () => {
    if (error) return '生成失败'
    if (progress?.type === 'complete') return '生成完成'
    if (isPaused) return '已暂停'
    if (isGenerating) return progress?.message || '生成中...'
    return '准备就绪'
  }

  // 渲染Markdown内容
  const renderContent = (content: string) => {
    // 简单的Markdown渲染
    return content
      .replace(/#{1,6}\s(.+)/g, '<h3 class="text-lg font-bold mt-4 mb-2">$1</h3>')
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.+?)\*/g, '<em>$1</em>')
      .replace(/```[\s\S]*?```/g, '<pre class="bg-gray-800 p-2 rounded my-2 overflow-x-auto"><code>$&</code></pre>')
      .replace(/`(.+?)`/g, '<code class="bg-gray-800 px-1 rounded">$1</code>')
      .replace(/\n/g, '<br />')
  }

  return (
    <Card className="bg-[#1A1D24] border-gray-800">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            {getStatusIcon()}
            <div>
              <CardTitle className="text-base font-medium text-white">
                AI 智能写作
              </CardTitle>
              <p className="text-xs text-gray-500 mt-0.5">
                {getStatusText()}
              </p>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            {isGenerating && (
              <>
                <Badge variant="outline" className="border-gray-700 text-gray-400">
                  <Clock className="w-3 h-3 mr-1" />
                  {Math.ceil((generatedContent?.length || 0) / 500)}分钟
                </Badge>
                <Badge variant="outline" className="border-gray-700 text-gray-400">
                  <Type className="w-3 h-3 mr-1" />
                  {(generatedContent?.length || 0).toLocaleString()}字
                </Badge>
              </>
            )}
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* 进度条 */}
        {(isGenerating || progress?.type === 'complete') && (
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="text-gray-500">生成进度</span>
              <span className="text-gray-400">{getProgressPercentage()}%</span>
            </div>
            <Progress 
              value={getProgressPercentage()} 
              className="h-2 bg-gray-800"
            />
          </div>
        )}

        {/* 生成的标题 */}
        {generatedTitle && (
          <div className="p-3 bg-blue-500/10 border border-blue-500/20 rounded-lg">
            <div className="flex items-center gap-2 mb-1">
              <FileText className="w-4 h-4 text-blue-400" />
              <span className="text-xs text-blue-400">生成标题</span>
            </div>
            <p className="text-white font-medium">{generatedTitle}</p>
          </div>
        )}

        {/* 内容预览区 */}
        {(isGenerating || displayedContent) && (
          <div className="relative">
            <div 
              ref={contentRef}
              className="h-64 overflow-y-auto p-4 bg-gray-900/50 rounded-lg border border-gray-800 text-sm leading-relaxed text-gray-300"
              dangerouslySetInnerHTML={{ __html: renderContent(displayedContent) }}
            />
            
            {/* 打字机光标 */}
            {isGenerating && !isPaused && (
              <span className="absolute bottom-4 right-4 w-2 h-5 bg-blue-500 animate-pulse" />
            )}
          </div>
        )}

        {/* 控制按钮 */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {!isGenerating && !displayedContent && (
              <Button
                onClick={handleStart}
                className="bg-blue-600 hover:bg-blue-700 text-white"
              >
                <Sparkles className="w-4 h-4 mr-2" />
                开始生成
              </Button>
            )}

            {isGenerating && (
              <>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handlePauseToggle}
                  className="border-gray-700 text-gray-300 hover:bg-gray-800"
                >
                  {isPaused ? (
                    <><Play className="w-4 h-4 mr-1" /> 继续</>
                  ) : (
                    <><Pause className="w-4 h-4 mr-1" /> 暂停</>
                  )}
                </Button>
                
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleStop}
                  className="border-red-700/50 text-red-400 hover:bg-red-900/20"
                >
                  <Square className="w-4 h-4 mr-1" />
                  停止
                </Button>
              </>
            )}
          </div>

          {/* 打字速度控制 */}
          {isGenerating && (
            <div className="flex items-center gap-2">
              <Zap className="w-4 h-4 text-gray-500" />
              <input
                type="range"
                min="10"
                max="100"
                value={110 - typingSpeed}
                onChange={(e) => setTypingSpeed(110 - parseInt(e.target.value))}
                className="w-24 h-1 bg-gray-700 rounded-lg appearance-none cursor-pointer"
              />
              <span className="text-xs text-gray-500 w-12">
                {typingSpeed < 30 ? '快' : typingSpeed > 70 ? '慢' : '中'}
              </span>
            </div>
          )}
        </div>

        {/* 错误提示 */}
        {error && (
          <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg flex items-center gap-2 text-red-400 text-sm">
            <AlertCircle className="w-4 h-4" />
            {error}
          </div>
        )}

        {/* 完成提示 */}
        {progress?.type === 'complete' && (
          <div className="p-3 bg-green-500/10 border border-green-500/20 rounded-lg flex items-center gap-2 text-green-400 text-sm">
            <CheckCircle className="w-4 h-4" />
            文章生成完成！共 {progress.data?.word_count} 字
          </div>
        )}
      </CardContent>
    </Card>
  )
}
