'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import {
  Sparkles,
  TrendingUp,
  FileText,
  ArrowRight,
  Plus,
  Clock,
  CheckCircle,
  Zap,
  Target,
  Layers,
  ChevronRight,
  Flame,
  Eye,
  BarChart2,
  PenTool,
  Send,
  Award
} from 'lucide-react'
import Link from 'next/link'
import { API_URL } from '@/lib/api'

interface Article {
  id: number
  title: string
  status: string
  created_at: string
  view_count: number
}

interface Stats {
  total: number
  published: number
  draft: number
}

interface Hotspot {
  title: string
  source: string
  heat: number
}

export default function HomePage() {
  const router = useRouter()
  const [recentArticles, setRecentArticles] = useState<Article[]>([])
  const [stats, setStats] = useState<Stats>({ total: 0, published: 0, draft: 0 })
  const [loading, setLoading] = useState(true)
  const [hotspots, setHotspots] = useState<Hotspot[]>([])
  const [hasCompletedSetup, setHasCompletedSetup] = useState(false)

  useEffect(() => {
    loadAllData()
  }, [])

  const loadAllData = async () => {
    setLoading(true)
    try {
      await Promise.allSettled([
        fetchDashboardData(),
        checkSetupStatus(),
        fetchHotspots()
      ])
    } catch (error) {
      console.error('加载数据失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchDashboardData = async () => {
    try {
      const response = await fetch(`${API_URL}/api/articles?limit=5`)
      if (response.ok) {
        const data = await response.json()
        const articles = data.articles || data || []
        setRecentArticles(articles)
        setStats({
          total: articles.length,
          published: articles.filter((a: Article) => a.status === 'published').length,
          draft: articles.filter((a: Article) => a.status === 'draft').length
        })
      }
    } catch (error) {
      console.error('获取数据失败:', error)
    }
  }

  const checkSetupStatus = async () => {
    try {
      const configRes = await fetch(`${API_URL}/api/config`)
      if (configRes.ok) {
        const config = await configRes.json()
        const hasAI = !!(config.api_key)
        setHasCompletedSetup(hasAI)
      }
    } catch (error) {
      console.error('检查配置失败:', error)
    }
  }

  const fetchHotspots = async () => {
    try {
      const response = await fetch(`${API_URL}/api/hotspots?limit=5`)
      if (response.ok) {
        const data = await response.json()
        setHotspots(data.items || [])
      }
    } catch (error) {
      console.error('获取热点失败:', error)
    }
  }

  const formatDate = (dateStr: string) => {
    if (!dateStr) return '刚刚'
    const date = new Date(dateStr)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const hours = Math.floor(diff / (1000 * 60 * 60))
    const days = Math.floor(hours / 24)

    if (hours < 1) return '刚刚'
    if (hours < 24) return `${hours}小时前`
    if (days < 7) return `${days}天前`
    return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
  }

  const totalReads = recentArticles.reduce((sum, a) => sum + (a.view_count || 0), 0)

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-violet-500 to-purple-600 animate-pulse" />
          <p className="text-slate-400 text-sm">加载中...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-50">
      {/* 顶部Hero区 */}
      <div className="bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-6 py-8">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-6">
            <div className="space-y-2">
              <p className="text-sm font-medium text-violet-500">AI 内容创作平台</p>
              <h1 className="text-3xl md:text-4xl font-semibold text-slate-900">
                让创作更简单
              </h1>
              <p className="text-slate-500">
                已创作 {stats.total} 篇内容 · 热点追踪 · 一键多平台发布
              </p>
            </div>
            
            <div className="flex items-center gap-3">
              <Link
                href="/hotspots"
                className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-slate-100 text-slate-700 font-medium hover:bg-slate-200 transition-colors"
              >
                <Flame className="w-4 h-4 text-orange-500" />
                热点选题
              </Link>
              <Link
                href="/articles/create"
                className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-violet-500 to-purple-600 text-white font-medium shadow-lg shadow-purple-500/20 hover:shadow-xl transition-all"
              >
                <Sparkles className="w-4 h-4" />
                AI 创作
              </Link>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-6 space-y-6">
        {/* 配置提示 */}
        {!hasCompletedSetup && (
          <div className="bg-gradient-to-r from-violet-500 to-purple-600 rounded-2xl p-5 flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 rounded-xl bg-white/20 flex items-center justify-center">
                <Zap className="w-5 h-5 text-white" />
              </div>
              <div className="text-white">
                <p className="font-medium">完成 AI 配置，开启智能创作</p>
                <p className="text-sm text-white/80">配置 API 密钥即可使用 AI 写作功能</p>
              </div>
            </div>
            <button
              onClick={() => router.push('/settings')}
              className="flex items-center gap-1 px-4 py-2 rounded-xl bg-white text-violet-600 font-medium hover:bg-white/90 transition-colors"
            >
              去配置 <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        )}

        {/* 核心数据指标 */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          <div className="bg-white rounded-xl p-4 border border-slate-200">
            <div className="flex items-center gap-2 text-slate-500 text-sm mb-1">
              <Layers className="w-4 h-4" />
              总作品
            </div>
            <p className="text-2xl font-semibold text-slate-900">{stats.total}</p>
          </div>
          <div className="bg-white rounded-xl p-4 border border-slate-200">
            <div className="flex items-center gap-2 text-emerald-600 text-sm mb-1">
              <Send className="w-4 h-4" />
              已发布
            </div>
            <p className="text-2xl font-semibold text-emerald-600">{stats.published}</p>
          </div>
          <div className="bg-white rounded-xl p-4 border border-slate-200">
            <div className="flex items-center gap-2 text-amber-600 text-sm mb-1">
              <PenTool className="w-4 h-4" />
              草稿
            </div>
            <p className="text-2xl font-semibold text-amber-600">{stats.draft}</p>
          </div>
          <div className="bg-white rounded-xl p-4 border border-slate-200">
            <div className="flex items-center gap-2 text-blue-600 text-sm mb-1">
              <Eye className="w-4 h-4" />
              总阅读
            </div>
            <p className="text-2xl font-semibold text-blue-600">{(totalReads / 1000).toFixed(1)}k</p>
          </div>
          <div className="bg-white rounded-xl p-4 border border-slate-200">
            <div className="flex items-center gap-2 text-violet-600 text-sm mb-1">
              <Target className="w-4 h-4" />
              发布率
            </div>
            <p className="text-2xl font-semibold text-violet-600">
              {stats.total > 0 ? Math.round((stats.published / stats.total) * 100) : 0}%
            </p>
          </div>
        </div>

        {/* 快捷操作 */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {[
            { icon: Sparkles, label: 'AI 写作', desc: '智能创作', href: '/articles/create', gradient: 'from-violet-500 to-purple-600' },
            { icon: Flame, label: '热点选题', desc: '实时追踪', href: '/hotspots', gradient: 'from-orange-500 to-red-500' },
            { icon: FileText, label: '文章管理', desc: '内容中心', href: '/articles', gradient: 'from-blue-500 to-cyan-500' },
            { icon: Target, label: '系统设置', desc: '配置管理', href: '/settings', gradient: 'from-slate-600 to-slate-800' },
          ].map((action, idx) => (
            <Link
              key={idx}
              href={action.href}
              className="group bg-white rounded-xl p-4 border border-slate-200 hover:border-violet-200 hover:shadow-lg transition-all duration-200"
            >
              <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${action.gradient} flex items-center justify-center mb-3 group-hover:scale-110 transition-transform`}>
                <action.icon className="w-5 h-5 text-white" />
              </div>
              <p className="font-medium text-slate-900">{action.label}</p>
              <p className="text-xs text-slate-500">{action.desc}</p>
            </Link>
          ))}
        </div>

        {/* 主内容区：文章 + 热点 */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* 最近文章 */}
          <div className="lg:col-span-2 bg-white rounded-2xl border border-slate-200 overflow-hidden">
            <div className="px-5 py-4 border-b border-slate-100 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-blue-50 flex items-center justify-center">
                  <FileText className="w-4 h-4 text-blue-500" />
                </div>
                <div>
                  <h2 className="font-medium text-slate-900">最近创作</h2>
                  <p className="text-xs text-slate-500">{recentArticles.length} 篇文章</p>
                </div>
              </div>
              <Link
                href="/articles/create"
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-900 text-white text-sm font-medium hover:bg-slate-800 transition-colors"
              >
                <Plus className="w-3.5 h-3.5" />
                新建
              </Link>
            </div>

            <div className="divide-y divide-slate-100">
              {recentArticles.length === 0 ? (
                <div className="px-5 py-12 text-center">
                  <div className="w-14 h-14 rounded-2xl bg-slate-100 flex items-center justify-center mx-auto mb-4">
                    <FileText className="w-7 h-7 text-slate-300" />
                  </div>
                  <p className="text-slate-500 font-medium mb-1">还没有文章</p>
                  <p className="text-sm text-slate-400 mb-4">开始创作第一篇文章</p>
                  <button
                    onClick={() => router.push('/articles/create')}
                    className="px-4 py-2 rounded-xl bg-violet-500 text-white text-sm font-medium hover:bg-violet-600 transition-colors"
                  >
                    开始创作
                  </button>
                </div>
              ) : (
                recentArticles.slice(0, 5).map((article) => (
                  <div
                    key={article.id}
                    onClick={() => router.push(`/articles/create?editId=${article.id}`)}
                    className="px-5 py-3 flex items-center justify-between hover:bg-slate-50 transition-colors cursor-pointer group"
                  >
                    <div className="flex-1 min-w-0">
                      <h4 className="font-medium text-slate-900 truncate group-hover:text-violet-600 transition-colors">
                        {article.title}
                      </h4>
                      <div className="flex items-center gap-3 mt-1 text-xs text-slate-500">
                        <span>{formatDate(article.created_at)}</span>
                        <span className={`px-2 py-0.5 rounded-md text-xs font-medium ${
                          article.status === 'published' 
                            ? 'bg-emerald-50 text-emerald-600' 
                            : 'bg-amber-50 text-amber-600'
                        }`}>
                          {article.status === 'published' ? '已发布' : '草稿'}
                        </span>
                        <span className="flex items-center gap-1">
                          <Eye className="w-3 h-3" />
                          {article.view_count || 0}
                        </span>
                      </div>
                    </div>
                    <ChevronRight className="w-4 h-4 text-slate-300 group-hover:text-slate-500 transition-colors" />
                  </div>
                ))
              )}
            </div>

            {recentArticles.length > 0 && (
              <div className="px-5 py-3 border-t border-slate-100">
                <Link
                  href="/articles"
                  className="flex items-center justify-center gap-1 text-sm text-violet-600 font-medium hover:text-violet-700"
                >
                  查看全部文章 <ChevronRight className="w-4 h-4" />
                </Link>
              </div>
            )}
          </div>

          {/* 热点推荐 */}
          <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden">
            <div className="px-5 py-4 border-b border-slate-100 flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-orange-50 flex items-center justify-center">
                <Flame className="w-4 h-4 text-orange-500" />
              </div>
              <div>
                <h2 className="font-medium text-slate-900">今日热点</h2>
                <p className="text-xs text-slate-500">实时追踪</p>
              </div>
            </div>

            <div className="p-3 space-y-2">
              {hotspots.length === 0 ? (
                <div className="py-8 text-center">
                  <p className="text-slate-400 text-sm">暂无热点数据</p>
                </div>
              ) : (
                hotspots.slice(0, 5).map((hotspot, idx) => (
                  <div
                    key={idx}
                    onClick={() => router.push('/articles/create')}
                    className="p-3 rounded-xl bg-slate-50 hover:bg-slate-100 transition-colors cursor-pointer group"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <p className="text-sm font-medium text-slate-700 line-clamp-2 group-hover:text-violet-600 transition-colors">
                        {hotspot.title}
                      </p>
                      <span className="flex items-center gap-0.5 text-xs font-semibold text-orange-500 whitespace-nowrap">
                        <Flame className="w-3 h-3" />
                        {hotspot.heat}
                      </span>
                    </div>
                    <p className="text-xs text-slate-400 mt-1">{hotspot.source}</p>
                  </div>
                ))
              )}
            </div>

            <div className="px-5 py-3 border-t border-slate-100">
              <Link
                href="/hotspots"
                className="flex items-center justify-center gap-1 text-sm text-violet-600 font-medium hover:text-violet-700"
              >
                查看全部热点 <ChevronRight className="w-4 h-4" />
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}