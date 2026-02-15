'use client'

import { useEffect, useState } from 'react'
import { X, Check, Loader2, Globe, FileText, Send } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { API_URL } from '@/lib/api'

interface Platform {
  id: string
  name: string
  icon: string
  enabled: boolean
  configured: boolean
  implemented: boolean
  ready: boolean
  reason?: string
  status?: 'idle' | 'loading' | 'success' | 'error'
  error?: string
  detail?: string
}

interface BackendPlatform {
  type: string
  name: string
  icon: string
  configured: boolean
  implemented: boolean
  ready: boolean
  reason?: string
}

interface MultiplatformPublishDialogProps {
  isOpen: boolean
  onClose: () => void
  articleId: number
  articleTitle: string
}

export default function MultiplatformPublishDialog({
  isOpen,
  onClose,
  articleId,
  articleTitle
}: MultiplatformPublishDialogProps) {
  const [platforms, setPlatforms] = useState<Platform[]>([])
  const [isLoadingPlatforms, setIsLoadingPlatforms] = useState(false)
  const [platformsError, setPlatformsError] = useState('')
  const [isPublishing, setIsPublishing] = useState(false)
  const [publishResults, setPublishResults] = useState<Record<string, any>>({})

  useEffect(() => {
    if (!isOpen) return
    void fetchPlatforms()
  }, [isOpen])

  const fetchPlatforms = async () => {
    setIsLoadingPlatforms(true)
    setPlatformsError('')
    try {
      const response = await fetch(`${API_URL}/api/multiplatform/platforms`)
      const data = await response.json().catch(() => ({}))
      if (!response.ok || !data.success || !Array.isArray(data.platforms)) {
        throw new Error(data?.detail || data?.message || '获取平台列表失败')
      }

      const normalizedPlatforms: Platform[] = data.platforms.map((item: BackendPlatform) => {
        const isReady = !!item.ready
        return {
          id: item.type,
          name: item.name,
          icon: item.icon,
          enabled: isReady && item.type === 'wechat',
          configured: !!item.configured,
          implemented: !!item.implemented,
          ready: isReady,
          reason: item.reason || '',
        }
      })

      setPlatforms(normalizedPlatforms)
    } catch (error) {
      const message = error instanceof Error ? error.message : '获取平台状态失败'
      setPlatformsError(message)
      setPlatforms([])
    } finally {
      setIsLoadingPlatforms(false)
    }
  }

  const handlePlatformToggle = (platformId: string) => {
    setPlatforms(platforms.map(p => {
      if (p.id !== platformId) return p
      if (!p.ready) return p
      return { ...p, enabled: !p.enabled }
    }))
  }

  const handlePublish = async () => {
    const enabledPlatforms = platforms.filter(p => p.enabled)
    if (enabledPlatforms.length === 0) {
      alert('请至少选择一个平台')
      return
    }

    setIsPublishing(true)
    setPlatforms(platforms.map(p => ({ ...p, status: 'idle' })))
    setPublishResults({})

    try {
      // 微信单平台：优先走专用草稿接口，兼容性更好
      if (enabledPlatforms.length === 1 && enabledPlatforms[0].id === 'wechat') {
        const response = await fetch(`${API_URL}/api/wechat/publish-draft/${articleId}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
        })

        const data = await response.json().catch(() => ({}))
        if (!response.ok || !data.success) {
          const errorMessage = data?.detail?.message || data?.detail || data?.message || '发布失败'
          const traceId = data?.detail?.trace_id || data?.trace_id
          const finalMessage = traceId ? `${errorMessage}（追踪ID: ${traceId}）` : String(errorMessage)
          setPlatforms(platforms.map(p =>
            p.id === 'wechat'
              ? { ...p, status: 'error' as const, error: finalMessage }
              : { ...p, status: 'idle' as const }
          ))
          alert(`发布失败：${finalMessage}`)
          return
        }

        setPlatforms(platforms.map(p =>
          p.id === 'wechat'
            ? {
              ...p,
              status: 'success' as const,
              error: undefined,
              detail: [
                `封面: ${data?.cover_source || 'unknown'}`,
                `排版: ${data?.format_engine || 'unknown'}`,
                `正文图片: ${data?.image_rewrite?.replaced ?? 0}/${data?.image_rewrite?.total ?? 0}`,
                data?.trace_id ? `追踪ID: ${data.trace_id}` : null,
              ].filter(Boolean).join(' ｜ '),
            }
            : { ...p, status: 'idle' as const }
        ))
        setPublishResults({ wechat: data })
        alert('已成功发送到微信公众号草稿箱')
        onClose()
        return
      }

      // 调用多平台发布API
      const response = await fetch(`${API_URL}/api/multiplatform/publish`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          article_id: articleId,
          platforms: enabledPlatforms.map(p => p.id)
        })
      })

      const data = await response.json().catch(() => ({}))
      if (!response.ok) {
        const detail = data?.detail?.message || data?.detail || data?.message || '发布失败'
        const traceId = data?.detail?.trace_id || data?.trace_id
        throw new Error(traceId ? `${String(detail)}（追踪ID: ${traceId}）` : String(detail))
      }

      // 更新平台状态
      if (data.results) {
        const newPlatforms = platforms.map(p => {
          const result = data.results.find((r: any) => r.platform === p.id)
          const status: Platform['status'] = result
            ? (result.success ? 'success' : 'error')
            : 'idle'
          return {
            ...p,
            status,
            error: result ? (result.error || result.message) : undefined
          }
        })
        setPlatforms(newPlatforms)
        setPublishResults(data.results)

        const failed = data.results.filter((r: any) => !r.success)
        if (failed.length > 0) {
          const failMsg = failed
            .map((r: any) => `${r.platform}: ${r.error || r.message || '失败'}`)
            .join('\n')
          alert(`部分平台发布失败：\n${failMsg}`)
          return
        }
      }

      alert('发布完成！')
      onClose()

    } catch (error) {
      console.error('发布失败:', error)
      const message = error instanceof Error ? error.message : '发布失败，请重试'
      alert(message)
      setPlatforms(platforms.map(p => ({ ...p, status: 'error' as const, error: message })))
    } finally {
      setIsPublishing(false)
    }
  }

  const getStatusIcon = (status?: Platform['status']) => {
    switch (status) {
      case 'loading':
        return <Loader2 className="w-4 h-4 animate-spin" />
      case 'success':
        return <Check className="w-4 h-4 text-green-500" />
      case 'error':
        return <X className="w-4 h-4 text-red-500" />
      default:
        return null
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-[#1A1D24] rounded-2xl w-full max-w-lg border border-gray-800 shadow-2xl">
        {/* 头部 */}
        <div className="flex items-center justify-between p-6 border-b border-gray-800">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-purple-500/20 flex items-center justify-center">
              <Globe className="w-5 h-5 text-purple-400" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">多平台发布</h2>
              <p className="text-sm text-gray-400">{articleTitle}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-gray-400" />
          </button>
        </div>

        {/* 平台列表 */}
        <div className="p-6 space-y-3">
          <p className="text-sm text-gray-400 mb-4">选择要发布的平台：</p>

          {isLoadingPlatforms && (
            <div className="rounded-xl border border-gray-700 bg-gray-800/40 px-4 py-3 text-sm text-gray-300 flex items-center gap-2">
              <Loader2 className="w-4 h-4 animate-spin" />
              正在获取平台状态...
            </div>
          )}

          {!isLoadingPlatforms && platformsError && (
            <div className="rounded-xl border border-red-700/50 bg-red-900/20 px-4 py-3 text-sm text-red-300">
              {platformsError}
            </div>
          )}

          {platforms.map((platform) => (
            <div
              key={platform.id}
              className={`flex items-center justify-between p-4 rounded-xl border transition-all ${
                !platform.ready
                  ? 'bg-gray-900/50 border-gray-700/40 opacity-80'
                  : platform.enabled
                  ? 'bg-purple-500/10 border-purple-500/30'
                  : 'bg-gray-800/50 border-gray-700'
              }`}
            >
              <div className="flex items-center gap-3">
                <span className="text-2xl">{platform.icon}</span>
                <div>
                  <h3 className="font-semibold text-white">{platform.name}</h3>
                  {!platform.ready && platform.reason && (
                    <p className="text-xs text-amber-300">{platform.reason}</p>
                  )}
                  {platform.error && (
                    <p className="text-xs text-red-400">{platform.error}</p>
                  )}
                  {platform.detail && platform.status === 'success' && (
                    <p className="text-xs text-green-400">{platform.detail}</p>
                  )}
                </div>
              </div>

              <div className="flex items-center gap-3">
                {getStatusIcon(platform.status)}
                <button
                  onClick={() => !isPublishing && platform.ready && handlePlatformToggle(platform.id)}
                  disabled={isPublishing || !platform.ready}
                  className={`relative w-12 h-6 rounded-full transition-colors ${
                    platform.enabled ? 'bg-purple-500' : 'bg-gray-700'
                  } ${isPublishing || !platform.ready ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
                >
                  <div
                    className={`absolute top-1 w-4 h-4 rounded-full bg-white transition-transform ${
                      platform.enabled ? 'left-7' : 'left-1'
                    }`}
                  />
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* 底部按钮 */}
        <div className="flex items-center justify-end gap-3 p-6 border-t border-gray-800">
          <Button
            variant="outline"
            onClick={onClose}
            disabled={isPublishing}
            className="bg-transparent border-gray-700 text-gray-300 hover:bg-gray-800"
          >
            取消
          </Button>
          <Button
            onClick={handlePublish}
            disabled={isPublishing || platforms.filter(p => p.enabled).length === 0}
            className="bg-purple-600 hover:bg-purple-700 text-white flex items-center gap-2"
          >
            {isPublishing ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                发布中...
              </>
            ) : (
              <>
                <Send className="w-4 h-4" />
                发布到 {platforms.filter(p => p.enabled).length} 个平台
              </>
            )}
          </Button>
        </div>
      </div>
    </div>
  )
}
