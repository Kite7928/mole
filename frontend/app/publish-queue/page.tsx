'use client'

import { useState, useEffect } from 'react'
import {
  Send,
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle,
  RefreshCw,
  Calendar,
  MoreVertical,
  Play,
  X,
  Filter,
  History,
  BarChart3,
  ChevronRight,
  ArrowRight
} from 'lucide-react'
import Link from 'next/link'
import { API_URL } from '@/lib/api'

// 状态配置
const statusConfig: Record<string, { label: string; color: string; icon: React.ReactNode }> = {
  pending: { label: '待发布', color: 'bg-slate-400', icon: <Clock className="w-4 h-4" /> },
  scheduled: { label: '已计划', color: 'bg-blue-500', icon: <Calendar className="w-4 h-4" /> },
  publishing: { label: '发布中', color: 'bg-amber-500', icon: <RefreshCw className="w-4 h-4 animate-spin" /> },
  published: { label: '已发布', color: 'bg-emerald-500', icon: <CheckCircle className="w-4 h-4" /> },
  failed: { label: '失败', color: 'bg-red-500', icon: <XCircle className="w-4 h-4" /> },
  cancelled: { label: '已取消', color: 'bg-slate-300', icon: <X className="w-4 h-4" /> }
}

interface QueueItem {
  id: number
  article_id: number
  article_title: string
  platform: string
  scheduled_time: string
  status: string
  created_at: string
  error_message?: string
}

interface QueueStats {
  total_pending: number
  scheduled_today: number
  scheduled_this_week: number
  failed_recent: number
  published_today: number
}

export default function PublishQueuePage() {
  const [activeTab, setActiveTab] = useState<'queue' | 'history'>('queue')
  const [queueItems, setQueueItems] = useState<QueueItem[]>([])
  const [historyItems, setHistoryItems] = useState<any[]>([])
  const [stats, setStats] = useState<QueueStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [processingId, setProcessingId] = useState<number | null>(null)

  useEffect(() => {
    fetchData()
    const interval = setInterval(fetchData, 30000) // 30秒刷新
    return () => clearInterval(interval)
  }, [activeTab])

  const fetchData = async () => {
    try {
      // 获取统计
      const statsRes = await fetch(`${API_URL}/api/publish-queue/queue/stats`)
      if (statsRes.ok) {
        setStats(await statsRes.json())
      }

      // 获取队列或历史
      if (activeTab === 'queue') {
        const queueRes = await fetch(`${API_URL}/api/publish-queue/queue`)
        if (queueRes.ok) {
          setQueueItems(await queueRes.json())
        }
      } else {
        const historyRes = await fetch(`${API_URL}/api/publish-queue/history?limit=50`)
        if (historyRes.ok) {
          const data = await historyRes.json()
          setHistoryItems(data.items)
        }
      }
    } catch (error) {
      console.error('获取数据失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCancel = async (id: number) => {
    if (!confirm('确定要取消这个发布计划吗？')) return
    
    try {
      const response = await fetch(`${API_URL}/api/publish-queue/queue/${id}/cancel`, {
        method: 'POST'
      })
      
      if (response.ok) {
        fetchData()
      } else {
        alert('取消失败')
      }
    } catch (error) {
      console.error('取消失败:', error)
      alert('取消失败')
    }
  }

  const handlePublishNow = async (id: number) => {
    if (!confirm('确定要立即发布这篇文章吗？')) return
    
    setProcessingId(id)
    try {
      const response = await fetch(`${API_URL}/api/publish-queue/queue/${id}/publish-now`, {
        method: 'POST'
      })
      
      if (response.ok) {
        fetchData()
      } else {
        alert('发布失败')
      }
    } catch (error) {
      console.error('发布失败:', error)
      alert('发布失败')
    } finally {
      setProcessingId(null)
    }
  }

  const handleProcessScheduled = async () => {
    try {
      const response = await fetch(`${API_URL}/api/publish-queue/queue/process`, {
        method: 'POST'
      })
      
      if (response.ok) {
        const result = await response.json()
        alert(result.message)
        fetchData()
      }
    } catch (error) {
      console.error('处理失败:', error)
    }
  }

  const formatTime = (timeStr: string) => {
    if (!timeStr) return '-'
    const date = new Date(timeStr)
    return date.toLocaleString('zh-CN', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const isOverdue = (timeStr: string) => {
    if (!timeStr) return false
    return new Date(timeStr) < new Date()
  }

  return (
    <div className="min-h-screen bg-slate-50">
      {/* 头部 */}
      <div className="bg-white border-b border-slate-200 sticky top-0 z-30">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center">
                <Send className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-semibold text-slate-900">发布队列</h1>
                <p className="text-sm text-slate-500">管理文章发布计划和历史</p>
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              <button
                onClick={handleProcessScheduled}
                className="flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-100 text-slate-700 text-sm font-medium hover:bg-slate-200 transition-colors"
              >
                <RefreshCw className="w-4 h-4" />
                处理到期任务
              </button>
              <Link
                href="/articles"
                className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-violet-500 to-purple-600 text-white text-sm font-medium hover:opacity-90 transition-opacity"
              >
                <Send className="w-4 h-4" />
                发布文章
              </Link>
            </div>
          </div>

          {/* Tab切换 */}
          <div className="flex gap-2 mt-6">
            <button
              onClick={() => setActiveTab('queue')}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all ${
                activeTab === 'queue'
                  ? 'bg-violet-500 text-white'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              <Clock className="w-4 h-4" />
              发布队列
              {stats && stats.total_pending > 0 && (
                <span className="px-2 py-0.5 rounded-full bg-white/20 text-xs">
                  {stats.total_pending}
                </span>
              )}
            </button>
            <button
              onClick={() => setActiveTab('history')}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all ${
                activeTab === 'history'
                  ? 'bg-violet-500 text-white'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              <History className="w-4 h-4" />
              发布历史
            </button>
          </div>
        </div>
      </div>

      {/* 统计卡片 */}
      {stats && (
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            <div className="bg-white rounded-2xl p-4 border border-slate-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-2xl font-bold text-slate-900">{stats.total_pending}</p>
                  <p className="text-sm text-slate-500">待发布</p>
                </div>
                <div className="w-10 h-10 rounded-xl bg-slate-100 flex items-center justify-center">
                  <Clock className="w-5 h-5 text-slate-500" />
                </div>
              </div>
            </div>
            <div className="bg-white rounded-2xl p-4 border border-slate-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-2xl font-bold text-blue-600">{stats.scheduled_today}</p>
                  <p className="text-sm text-slate-500">今日计划</p>
                </div>
                <div className="w-10 h-10 rounded-xl bg-blue-50 flex items-center justify-center">
                  <Calendar className="w-5 h-5 text-blue-500" />
                </div>
              </div>
            </div>
            <div className="bg-white rounded-2xl p-4 border border-slate-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-2xl font-bold text-violet-600">{stats.scheduled_this_week}</p>
                  <p className="text-sm text-slate-500">本周计划</p>
                </div>
                <div className="w-10 h-10 rounded-xl bg-violet-50 flex items-center justify-center">
                  <BarChart3 className="w-5 h-5 text-violet-500" />
                </div>
              </div>
            </div>
            <div className="bg-white rounded-2xl p-4 border border-slate-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-2xl font-bold text-emerald-600">{stats.published_today}</p>
                  <p className="text-sm text-slate-500">今日已发</p>
                </div>
                <div className="w-10 h-10 rounded-xl bg-emerald-50 flex items-center justify-center">
                  <CheckCircle className="w-5 h-5 text-emerald-500" />
                </div>
              </div>
            </div>
            <div className="bg-white rounded-2xl p-4 border border-slate-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-2xl font-bold text-red-600">{stats.failed_recent}</p>
                  <p className="text-sm text-slate-500">近7天失败</p>
                </div>
                <div className="w-10 h-10 rounded-xl bg-red-50 flex items-center justify-center">
                  <AlertCircle className="w-5 h-5 text-red-500" />
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 主内容 */}
      <div className="max-w-7xl mx-auto px-6 pb-6">
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="w-8 h-8 border-2 border-violet-500 border-t-transparent rounded-full animate-spin" />
          </div>
        ) : activeTab === 'queue' ? (
          <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden">
            {queueItems.length === 0 ? (
              <div className="py-20 text-center text-slate-400">
                <Clock className="w-16 h-16 mx-auto mb-4 opacity-30" />
                <p className="mb-4">暂无发布计划</p>
                <Link
                  href="/articles"
                  className="px-4 py-2 bg-violet-500 text-white rounded-xl text-sm hover:bg-violet-600 transition-colors"
                >
                  去发布文章
                </Link>
              </div>
            ) : (
              <div className="divide-y divide-slate-100">
                {queueItems.map(item => {
                  const status = statusConfig[item.status] || statusConfig.pending
                  const StatusIcon = () => status.icon
                  
                  return (
                    <div
                      key={item.id}
                      className="p-4 flex items-center gap-4 hover:bg-slate-50 transition-colors"
                    >
                      <div className={`w-10 h-10 rounded-xl flex items-center justify-center text-white ${status.color}`}>
                        <StatusIcon />
                      </div>
                      
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-3">
                          <h4 className="font-medium text-slate-900 truncate">
                            {item.article_title}
                          </h4>
                          <span className={`px-2 py-0.5 rounded-full text-xs text-white ${status.color}`}>
                            {status.label}
                          </span>
                          {isOverdue(item.scheduled_time) && item.status === 'scheduled' && (
                            <span className="px-2 py-0.5 rounded-full text-xs bg-red-100 text-red-600">
                              已过期
                            </span>
                          )}
                        </div>
                        <div className="flex items-center gap-4 text-sm text-slate-500 mt-1">
                          <span className="capitalize">{item.platform}</span>
                          {item.scheduled_time && (
                            <span className="flex items-center gap-1">
                              <Clock className="w-3 h-3" />
                              计划时间: {formatTime(item.scheduled_time)}
                            </span>
                          )}
                          {item.error_message && (
                            <span className="text-red-500 truncate max-w-xs">
                              错误: {item.error_message}
                            </span>
                          )}
                        </div>
                      </div>
                      
                      <div className="flex items-center gap-2">
                        {(item.status === 'pending' || item.status === 'scheduled') && (
                          <>
                            <button
                              onClick={() => handlePublishNow(item.id)}
                              disabled={processingId === item.id}
                              className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-violet-100 text-violet-600 text-sm font-medium hover:bg-violet-200 disabled:opacity-50 transition-colors"
                            >
                              {processingId === item.id ? (
                                <RefreshCw className="w-4 h-4 animate-spin" />
                              ) : (
                                <Play className="w-4 h-4" />
                              )}
                              立即发布
                            </button>
                            <button
                              onClick={() => handleCancel(item.id)}
                              className="p-2 rounded-lg hover:bg-red-50 text-slate-400 hover:text-red-500 transition-colors"
                            >
                              <X className="w-4 h-4" />
                            </button>
                          </>
                        )}
                        {item.status === 'failed' && (
                          <button
                            onClick={() => handlePublishNow(item.id)}
                            disabled={processingId === item.id}
                            className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-amber-100 text-amber-600 text-sm font-medium hover:bg-amber-200 disabled:opacity-50 transition-colors"
                          >
                            <RefreshCw className={`w-4 h-4 ${processingId === item.id ? 'animate-spin' : ''}`} />
                            重试
                          </button>
                        )}
                      </div>
                    </div>
                  )
                })}
              </div>
            )}
          </div>
        ) : (
          <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden">
            {historyItems.length === 0 ? (
              <div className="py-20 text-center text-slate-400">
                <History className="w-16 h-16 mx-auto mb-4 opacity-30" />
                <p>暂无发布历史</p>
              </div>
            ) : (
              <div className="divide-y divide-slate-100">
                {historyItems.map(item => {
                  const status = statusConfig[item.status] || statusConfig.pending
                  
                  return (
                    <div
                      key={item.id}
                      className="p-4 flex items-center gap-4 hover:bg-slate-50 transition-colors"
                    >
                      <div className={`w-2 h-12 rounded-full ${status.color}`} />
                      
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-3">
                          <h4 className="font-medium text-slate-900">{item.article_title}</h4>
                          <span className={`px-2 py-0.5 rounded-full text-xs text-white ${status.color}`}>
                            {status.label}
                          </span>
                        </div>
                        <div className="flex items-center gap-4 text-sm text-slate-500 mt-1">
                          <span className="capitalize">{item.platform}</span>
                          {item.published_at && (
                            <span>发布时间: {formatTime(item.published_at)}</span>
                          )}
                          {item.error_message && (
                            <span className="text-red-500">{item.error_message}</span>
                          )}
                        </div>
                      </div>
                      
                      <Link
                        href={`/articles/create?editId=${item.article_id}`}
                        className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-slate-400 hover:text-violet-600 hover:bg-violet-50 transition-colors"
                      >
                        查看
                        <ChevronRight className="w-4 h-4" />
                      </Link>
                    </div>
                  )
                })}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
