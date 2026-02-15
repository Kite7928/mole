/**
 * AI简单生成组件（备用方案）
 * 使用非流式API，更稳定可靠
 */

'use client'

import { useState } from 'react'
import {
  Sparkles,
  Loader2,
  CheckCircle,
  AlertCircle,
  FileText,
  Type,
  RefreshCw
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { API_URL } from '@/lib/api'

interface AISimpleGeneratorProps {
  topic: string
  title?: string
  style?: string
  model?: string
  onComplete?: (result: {
    title: string
    content: string
    summary: string
    wordCount: number
  }) => void
  onError?: (error: string) => void
}

export default function AISimpleGenerator({
  topic,
  title,
  style = 'professional',
  model,
  onComplete,
  onError,
}: AISimpleGeneratorProps) {
  const [isGenerating, setIsGenerating] = useState(false)
  const [progress, setProgress] = useState(0)
  const [generatedContent, setGeneratedContent] = useState('')
  const [generatedTitle, setGeneratedTitle] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [stage, setStage] = useState<'idle' | 'title' | 'content' | 'complete'>('idle')

  const handleGenerate = async () => {
    setIsGenerating(true)
    setError(null)
    setStage('title')
    setProgress(10)

    try {
      // 步骤1: 生成标题（如果没有提供）
      let finalTitle: string = title || ''
      if (!finalTitle) {
        setProgress(20)
        const titleRes = await fetch(`${API_URL}/api/ai/generate-titles`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            topic,
            count: 1,
            model
          })
        })

        if (!titleRes.ok) {
          throw new Error('生成标题失败')
        }

        const titles = await titleRes.json()
        if (titles && titles.length > 0) {
          finalTitle = titles[0].title
          setGeneratedTitle(finalTitle)
        } else {
          finalTitle = topic
          setGeneratedTitle(finalTitle)
        }
      } else {
        setGeneratedTitle(finalTitle)
      }

      // 步骤2: 生成内容
      setStage('content')
      setProgress(40)

      const contentRes = await fetch(`${API_URL}/api/ai/generate-content`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          topic,
          title: finalTitle,
          style,
          length: 'medium',
          model
        })
      })

      if (!contentRes.ok) {
        const errorData = await contentRes.json()
        throw new Error(errorData.detail || '生成内容失败')
      }

      setProgress(80)

      const result = await contentRes.json()
      
      setGeneratedContent(result.content)
      setProgress(100)
      setStage('complete')

      // 完成回调
      onComplete?.({
        title: finalTitle || topic,
        content: result.content,
        summary: result.summary,
        wordCount: result.word_count || result.content?.length || 0
      })

    } catch (err: any) {
      const errorMessage = err.message || '生成过程中发生错误'
      setError(errorMessage)
      onError?.(errorMessage)
    } finally {
      setIsGenerating(false)
    }
  }

  const handleRetry = () => {
    setError(null)
    setProgress(0)
    setStage('idle')
    setGeneratedContent('')
    handleGenerate()
  }

  // 获取状态显示
  const getStatusDisplay = () => {
    if (error) return { icon: <AlertCircle className="w-5 h-5 text-red-500" />, text: '生成失败', color: 'text-red-400' }
    if (stage === 'complete') return { icon: <CheckCircle className="w-5 h-5 text-green-500" />, text: '生成完成', color: 'text-green-400' }
    if (isGenerating && stage === 'title') return { icon: <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />, text: '正在生成标题...', color: 'text-blue-400' }
    if (isGenerating && stage === 'content') return { icon: <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />, text: '正在生成内容...', color: 'text-blue-400' }
    return { icon: <Sparkles className="w-5 h-5 text-purple-500" />, text: '准备就绪', color: 'text-gray-400' }
  }

  const status = getStatusDisplay()

  return (
    <Card className="art-card">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            {status.icon}
            <div>
              <CardTitle className="text-base font-medium text-foreground">
                AI 智能写作
              </CardTitle>
              <p className={`text-xs mt-0.5 ${status.color}`}>
                {status.text}
              </p>
            </div>
          </div>
          
          {isGenerating && (
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <Type className="w-3 h-3" />
              {Math.ceil((generatedContent?.length || 0) / 500)}分钟
            </div>
          )}
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* 进度条 */}
        {(isGenerating || stage === 'complete') && (
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="text-muted-foreground">生成进度</span>
              <span className="text-foreground">{progress}%</span>
            </div>
            <Progress value={progress} className="h-2" />
          </div>
        )}

        {/* 错误提示 */}
        {error && (
          <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
            <div className="flex items-center gap-2 text-red-400">
              <AlertCircle className="w-4 h-4" />
              <span className="text-sm">{error}</span>
            </div>
            <Button 
              size="sm" 
              variant="outline" 
              className="mt-2 w-full"
              onClick={handleRetry}
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              重试
            </Button>
          </div>
        )}

        {/* 生成的标题 */}
        {generatedTitle && (
          <div className="p-3 bg-primary/10 border border-primary/20 rounded-lg">
            <div className="flex items-center gap-2 mb-1">
              <FileText className="w-4 h-4 text-primary" />
              <span className="text-xs text-primary">生成标题</span>
            </div>
            <p className="font-medium text-foreground">{generatedTitle}</p>
          </div>
        )}

        {/* 内容预览 */}
        {generatedContent && (
          <div className="relative">
            <div className="h-64 overflow-y-auto p-4 bg-muted/50 rounded-lg border text-sm leading-relaxed">
              <div 
                className="prose prose-sm max-w-none dark:prose-invert"
                dangerouslySetInnerHTML={{ 
                  __html: generatedContent
                    .replace(/#{1,6}\s(.+)/g, '<h3 class="text-lg font-bold mt-4 mb-2">$1</h3>')
                    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
                    .replace(/\n/g, '<br />')
                }}
              />
            </div>
            
            {/* 字数统计 */}
            <div className="absolute bottom-2 right-2 px-2 py-1 bg-background/80 rounded text-xs text-muted-foreground">
              {generatedContent.length.toLocaleString()} 字
            </div>
          </div>
        )}

        {/* 开始生成按钮 */}
        {!isGenerating && stage === 'idle' && (
          <Button 
            className="w-full art-button-primary"
            onClick={handleGenerate}
          >
            <Sparkles className="w-4 h-4 mr-2" />
            开始生成
          </Button>
        )}

        {/* 重新生成按钮 */}
        {!isGenerating && stage === 'complete' && (
          <Button 
            variant="outline" 
            className="w-full"
            onClick={handleRetry}
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            重新生成
          </Button>
        )}
      </CardContent>
    </Card>
  )
}
