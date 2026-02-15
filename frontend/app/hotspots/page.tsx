'use client'

import { useState, useEffect } from 'react'
import { 
  Flame, 
  RefreshCw, 
  Search, 
  Clock,
  Sparkles,
  Loader2,
  Grid3x3,
  List,
  ExternalLink,
  Wand2,
  X,
  ChevronRight,
  Layers,
  Newspaper,
  Check,
  ArrowRight,
  PenTool,
  FileText,
  Send
} from 'lucide-react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { API_URL } from '@/lib/api'

interface HotNewsItem {
  id: number
  title: string
  summary: string
  url: string
  source: string
  sourceName: string
  sourceLogo: string
  hotScore: number
  publishedAt: string
  imageUrl: string
  category: string
  tags: string[]
  created_at: string
}

export default function HotspotsPage() {
  const router = useRouter()
  const [selectedPlatform, setSelectedPlatform] = useState('all')
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const [platforms, setPlatforms] = useState<{id: string, name: string}[]>([{ id: 'all', name: '全部' }])
  const [platformsLoading, setPlatformsLoading] = useState(true)
  const [hotNews, setHotNews] = useState<HotNewsItem[]>([])
  const [newsLoading, setNewsLoading] = useState(true)
  const [refreshStatus, setRefreshStatus] = useState<{
    type: 'success' | 'warning' | 'error'
    message: string
  } | null>(null)
  
  // 一键创作相关状态
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [creatingNews, setCreatingNews] = useState<HotNewsItem | null>(null)
  const [createStep, setCreateStep] = useState<'options' | 'creating' | 'success'>('options')
  const [createProgress, setCreateProgress] = useState(0)
  const [createStyle, setCreateStyle] = useState('professional')
  const [createAudience, setCreateAudience] = useState<'general' | 'creator' | 'professional'>('creator')
  const [createGoal, setCreateGoal] = useState<'insight' | 'growth' | 'conversion'>('insight')
  const [createEvidenceLevel, setCreateEvidenceLevel] = useState(4)
  const [createStyleCard, setCreateStyleCard] = useState(true)
  const [createdArticle, setCreatedArticle] = useState<any>(null)
  
  // AI大纲相关状态
  const [showOutlineModal, setShowOutlineModal] = useState(false)
  const [isGeneratingOutline, setIsGeneratingOutline] = useState(false)
  const [generatedOutlines, setGeneratedOutlines] = useState<any[]>([])
  const [selectedNewsForOutline, setSelectedNewsForOutline] = useState<any>(null)

  useEffect(() => {
    fetchNews()
  }, [selectedPlatform])

  useEffect(() => {
    fetchPlatforms()
  }, [])

  const fetchWithTimeout = async (url: string, options: RequestInit = {}, timeout = 10000) => {
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), timeout)
    try {
      const response = await fetch(url, { ...options, signal: controller.signal })
      clearTimeout(timeoutId)
      return response
    } catch (error) {
      clearTimeout(timeoutId)
      throw error
    }
  }

  const fetchPlatforms = async () => {
    try {
      setPlatformsLoading(true)
      const response = await fetchWithTimeout(`${API_URL}/api/news/sources`, {}, 15000)
      const data = await response.json()
      if (data.success && data.sources) {
        setPlatforms([
          { id: 'all', name: '全部' },
          ...data.sources.map((s: any) => ({ id: s.value, name: s.name }))
        ])
      }
    } catch (error) {
      setPlatforms([
        { id: 'all', name: '全部' },
        { id: 'ithome', name: 'IT之家' },
        { id: 'kr36', name: '36氪' },
        { id: 'sspai', name: '少数派' },
        { id: 'huxiu', name: '虎嗅' },
        { id: 'infoq', name: 'InfoQ' },
        { id: 'oschina', name: '开源中国' },
      ])
    } finally {
      setPlatformsLoading(false)
    }
  }

  const fetchNews = async () => {
    try {
      setNewsLoading(true)
      const params = new URLSearchParams({ limit: '50' })
      if (selectedPlatform !== 'all') {
        params.set('source', selectedPlatform)
      }

      const response = await fetchWithTimeout(`${API_URL}/api/news?${params.toString()}`, {}, 20000)
      const data = await response.json()
      const newsItems = Array.isArray(data) ? data : (data.items || [])
      if (newsItems.length > 0) {
        setHotNews(newsItems.map((item: any) => ({
          id: item.id,
          title: item.title,
          summary: item.summary?.replace(/<[^>]*>/g, '').substring(0, 150) || item.title,
          url: item.url,
          source: item.source,
          sourceName: item.source_name || item.source,
          sourceLogo: getSourceLogo(item.source),
          hotScore: Math.round(item.hot_score || 0),
          publishedAt: formatPublishedAt(item.published_at),
          imageUrl: '',
          category: 'tech',
          tags: ['热点'],
          created_at: item.created_at
        })))
      } else {
        setHotNews([])
      }
    } catch (error) {
      setHotNews([])
    } finally {
      setNewsLoading(false)
    }
  }

  const getSourceLogo = (source: string) => {
    const logos: Record<string, string> = {
      'ithome': '🏠', 'baidu': '🔍', 'kr36': '🚀', 'sspai': '⚡',
      'huxiu': '🐯', 'tmpost': '💎', 'infoq': '📡', 'juejin': '🔧',
      'zhihu_daily': '📚', 'oschina': '🌐', 'zhihu': '📖', 'weibo': '📱'
    }
    return logos[source] || '📰'
  }

  const formatPublishedAt = (publishedAt: string) => {
    if (!publishedAt) return '刚刚'
    const now = new Date()
    const published = new Date(publishedAt)
    const diff = Math.floor((now.getTime() - published.getTime()) / 1000 / 60)
    if (diff < 1) return '刚刚'
    if (diff < 60) return `${diff}分钟前`
    if (diff < 1440) return `${Math.floor(diff / 60)}小时前`
    return `${Math.floor(diff / 1440)}天前`
  }

  const handleRefresh = async () => {
    setIsRefreshing(true)
    setRefreshStatus(null)
    try {
      const refreshSource = selectedPlatform === 'all' ? 'all' : selectedPlatform

      const response = await fetchWithTimeout(`${API_URL}/api/news/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ source: refreshSource, limit: 10 })
      }, 30000)

      const data = await response.json().catch(() => ({}))
      if (!response.ok || data?.success === false) {
        throw new Error(data?.detail || data?.message || '刷新失败，请稍后重试')
      }

      if (data?.fallback === 'cache') {
        setRefreshStatus({
          type: 'warning',
          message: data?.message || '本次抓取未命中新数据，已保留历史缓存'
        })
      } else {
        setRefreshStatus({
          type: 'success',
          message: data?.message || '热点刷新成功'
        })
      }

      await fetchNews()
    } catch (error: any) {
      setRefreshStatus({
        type: 'error',
        message: error?.message || '刷新失败，请检查网络后重试'
      })
    } finally {
      setIsRefreshing(false)
    }
  }

  const handleGenerateOutline = async (news: any) => {
    setSelectedNewsForOutline(news)
    setShowOutlineModal(true)
    setIsGeneratingOutline(true)
    setGeneratedOutlines([])
    try {
      const response = await fetchWithTimeout(`${API_URL}/api/articles/generate-outlines`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic: news.title, source_url: news.url })
      }, 60000)
      const data = await response.json()
      if (data.success && data.outlines) setGeneratedOutlines(data.outlines)
    } catch (error) {
      console.error('生成大纲失败:', error)
    } finally {
      setIsGeneratingOutline(false)
    }
  }

  // 打开一键创作弹窗
  const openCreateModal = (news: HotNewsItem) => {
    setCreatingNews(news)
    setCreateStep('options')
    setCreateProgress(0)
    setCreatedArticle(null)
    setShowCreateModal(true)
  }

  // 执行一键创作
  const executeQuickCreate = async () => {
    if (!creatingNews) return
    
    setCreateStep('creating')
    setCreateProgress(10)
    
    try {
      // 步骤1：创建文章草稿 - 增加超时时间到120秒
      setCreateProgress(15)
      
      // 使用普通 fetch，不设置超时限制（AI生成需要较长时间）
      const controller = new AbortController()
      const createResponse = await fetch(
        `${API_URL}/api/news/${creatingNews.id}/create-article`,
        { 
          method: 'POST', 
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            style: createStyle,
            audience: createAudience,
            goal: createGoal,
            evidence_level: createEvidenceLevel,
            style_card: createStyleCard,
          }),
          signal: controller.signal
        }
      )
      
      setCreateProgress(30)
      const createData = await createResponse.json()
      
      if (!createData.success || !createData.article) {
        throw new Error(createData.message || '创建文章失败')
      }
      
      setCreatedArticle(createData.article)
      setCreateProgress(100)
      
      // 延迟显示成功状态
      setTimeout(() => {
        setCreateStep('success')
      }, 500)
      
    } catch (error: any) {
      // 如果是超时错误，给出更友好的提示
      if (error.name === 'AbortError') {
        alert('创作超时，AI正在处理中，请稍后在文章管理中查看')
      } else {
        alert('创作失败: ' + (error.message || '请稍后重试'))
      }
      setShowCreateModal(false)
      setCreateStep('options')
    }
  }

  // 跳转到编辑页面
  const goToEdit = () => {
    if (createdArticle?.id) {
      router.push(`/articles/create?article_id=${createdArticle.id}`)
    }
    setShowCreateModal(false)
  }

  const selectedPlatformName = platforms.find((platform) => platform.id === selectedPlatform)?.name

  const filteredNews = hotNews.filter(news => {
    const matchesSearch = !searchQuery || 
      news.title.toLowerCase().includes(searchQuery.toLowerCase())

    if (selectedPlatform === 'all') {
      return matchesSearch
    }

    const matchesPlatform =
      news.source === selectedPlatform ||
      (!!selectedPlatformName && news.sourceName === selectedPlatformName)

    return matchesSearch && matchesPlatform
  })

  // 公众号创作者专属写作风格
  const createStyles = [
    { id: 'hot', name: '爆款吸睛', icon: '🔥', desc: '高点击率', highlight: true },
    { id: 'dry', name: '干货清单', icon: '📋', desc: '收藏价值' },
    { id: 'story', name: '故事叙述', icon: '📖', desc: '引人入胜' },
    { id: 'emotion', name: '情感共鸣', icon: '💝', desc: '引发互动' },
    { id: 'professional', name: '专业深度', icon: '📊', desc: '权威背书' },
    { id: 'casual', name: '轻松解读', icon: '💬', desc: '通俗易懂' },
  ]

  return (
    <div className="min-h-screen bg-slate-50">
      {/* 头部 */}
      <div className="bg-white border-b border-slate-200 sticky top-0 z-30">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-orange-500 to-red-500 flex items-center justify-center">
                <Flame className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-semibold text-slate-900">热点选题</h1>
                <p className="text-sm text-slate-500">实时追踪科技热点，一键AI创作</p>
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              <span className="hidden sm:inline-flex px-3 py-1.5 rounded-lg bg-slate-100 text-xs text-slate-600">
                已接入 {Math.max(platforms.length - 1, 0)} 个来源
              </span>
              <Link
                href="/settings/rss-sources"
                className="flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-100 text-slate-700 text-sm font-medium hover:bg-slate-200 transition-colors"
              >
                <Layers className="w-4 h-4" />
                自定义源
              </Link>
              <button
                onClick={handleRefresh}
                disabled={isRefreshing}
                className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-orange-500 to-red-500 text-white text-sm font-medium hover:opacity-90 transition-opacity disabled:opacity-50"
              >
                {isRefreshing ? <Loader2 className="w-4 h-4 animate-spin" /> : <RefreshCw className="w-4 h-4" />}
                {isRefreshing ? '刷新中' : '刷新热点'}
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-6 space-y-6">
        {refreshStatus && (
          <div className={`rounded-xl border px-4 py-3 text-sm ${
            refreshStatus.type === 'success'
              ? 'border-emerald-200 bg-emerald-50 text-emerald-700'
              : refreshStatus.type === 'warning'
              ? 'border-amber-200 bg-amber-50 text-amber-700'
              : 'border-red-200 bg-red-50 text-red-700'
          }`}>
            {refreshStatus.message}
          </div>
        )}

        {/* 搜索和筛选 */}
        <div className="flex flex-col md:flex-row gap-4">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              type="text"
              placeholder="搜索热点话题..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-white border border-slate-200 text-sm focus:outline-none focus:border-violet-400 focus:ring-2 focus:ring-violet-100"
            />
          </div>

          <div className="flex items-center gap-3">
            <div className="flex bg-white border border-slate-200 rounded-xl p-1 gap-1 overflow-x-auto max-w-full">
              {platformsLoading ? (
                <div className="px-3 py-1.5 text-sm text-slate-400">加载中...</div>
              ) : (
                platforms.map((platform) => (
                  <button
                    key={platform.id}
                    onClick={() => setSelectedPlatform(platform.id)}
                    className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                      selectedPlatform === platform.id
                        ? 'bg-violet-500 text-white'
                        : 'text-slate-600 hover:bg-slate-100'
                    }`}
                  >
                    {platform.name}
                  </button>
                ))
              )}
            </div>

            <div className="flex bg-white border border-slate-200 rounded-xl p-1">
              <button
                onClick={() => setViewMode('grid')}
                className={`p-1.5 rounded-lg ${viewMode === 'grid' ? 'bg-slate-100' : ''}`}
              >
                <Grid3x3 className="w-4 h-4 text-slate-600" />
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`p-1.5 rounded-lg ${viewMode === 'list' ? 'bg-slate-100' : ''}`}
              >
                <List className="w-4 h-4 text-slate-600" />
              </button>
            </div>
          </div>
        </div>

        {/* 统计 */}
        <div className="flex items-center gap-4 text-sm">
          <span className="text-slate-500">
            共 <span className="font-semibold text-slate-900">{filteredNews.length}</span> 条热点
          </span>
          <span className="text-slate-300">|</span>
          <span className="text-slate-500">
            高热 <span className="font-semibold text-orange-500">{filteredNews.filter(n => n.hotScore >= 80).length}</span> 条
          </span>
        </div>

        {/* 内容区 */}
        {newsLoading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="w-8 h-8 animate-spin text-violet-500" />
          </div>
        ) : filteredNews.length === 0 ? (
          <div className="text-center py-16 bg-white rounded-2xl border border-slate-200">
            <Newspaper className="w-12 h-12 text-slate-300 mx-auto mb-4" />
            <p className="text-slate-500 font-medium">暂无热点</p>
            <p className="text-sm text-slate-400 mt-1">点击刷新获取最新热点</p>
          </div>
        ) : (
          <div className={`grid gap-4 ${viewMode === 'grid' ? 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3' : 'grid-cols-1'}`}>
            {filteredNews.map((news, index) => {
              const isHot = news.hotScore >= 80
              
              return (
                <div
                  key={news.id}
                  className="group bg-white rounded-2xl border border-slate-200 hover:border-violet-200 hover:shadow-lg transition-all overflow-hidden"
                >
                  <div className={`h-1 ${isHot ? 'bg-gradient-to-r from-orange-500 to-red-500' : 'bg-slate-200'}`} />
                  
                  <div className="p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-2">
                        <span className="text-lg">{news.sourceLogo}</span>
                        <span className="text-sm text-slate-500">{news.sourceName}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-slate-400">{news.publishedAt}</span>
                        {isHot && (
                          <span className="flex items-center gap-1 px-2 py-0.5 rounded-full bg-orange-50 text-orange-600 text-xs font-medium">
                            <Flame className="w-3 h-3" />
                            {news.hotScore}
                          </span>
                        )}
                      </div>
                    </div>

                    <h3 className="font-medium text-slate-900 mb-2 line-clamp-2 group-hover:text-violet-600 transition-colors">
                      {news.title}
                    </h3>

                    <p className="text-sm text-slate-500 mb-4 line-clamp-2">{news.summary}</p>

                    <div className="flex gap-2">
                      <button
                        onClick={() => openCreateModal(news)}
                        className="flex-1 flex items-center justify-center gap-2 px-3 py-2.5 rounded-xl bg-gradient-to-r from-violet-500 to-purple-600 text-white text-sm font-medium hover:opacity-90 transition-opacity"
                      >
                        <Sparkles className="w-4 h-4" />
                        一键创作
                      </button>
                      <button
                        onClick={() => handleGenerateOutline(news)}
                        className="px-3 py-2.5 rounded-xl bg-slate-100 text-slate-700 text-sm font-medium hover:bg-slate-200 transition-colors"
                      >
                        <Wand2 className="w-4 h-4" />
                      </button>
                      <a
                        href={news.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="p-2.5 rounded-xl bg-slate-100 text-slate-500 hover:bg-slate-200 hover:text-slate-700 transition-colors"
                      >
                        <ExternalLink className="w-4 h-4" />
                      </a>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>

      {/* 一键创作弹窗 */}
      {showCreateModal && creatingNews && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" onClick={() => createStep !== 'creating' && setShowCreateModal(false)} />
          <div className="relative w-full max-w-md bg-white rounded-2xl shadow-2xl overflow-hidden">
            
            {/* 选项步骤 */}
            {createStep === 'options' && (
              <>
                <div className="px-6 py-5 border-b border-slate-100">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center">
                      <Sparkles className="w-5 h-5 text-white" />
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-slate-900">AI 一键创作</h3>
                      <p className="text-sm text-slate-500">选择创作风格</p>
                    </div>
                  </div>
                </div>

                <div className="px-6 py-5">
                  {/* 热点标题 */}
                  <div className="mb-5 p-3 rounded-xl bg-slate-50">
                    <p className="text-xs text-slate-500 mb-1">创作主题</p>
                    <p className="font-medium text-slate-900 text-sm line-clamp-2">{creatingNews.title}</p>
                  </div>

                  {/* 风格选择 */}
                  <div className="mb-5">
                    <label className="text-sm font-medium text-slate-700 mb-3 block">写作风格</label>
                    <div className="grid grid-cols-2 gap-2">
                      {createStyles.map((style) => (
                        <button
                          key={style.id}
                          onClick={() => setCreateStyle(style.id)}
                          className={`relative p-3 rounded-xl border-2 text-left transition-all ${
                            createStyle === style.id 
                              ? 'border-violet-500 bg-violet-50' 
                              : 'border-slate-100 hover:border-slate-200'
                          }`}
                        >
                          {style.highlight && (
                            <span className="absolute -top-2 -right-2 px-2 py-0.5 rounded-full bg-orange-500 text-white text-xs font-medium">
                              推荐
                            </span>
                          )}
                          <div className="flex items-center gap-2 mb-1">
                            <span className="text-xl">{style.icon}</span>
                            <span className="text-sm font-medium text-slate-900">{style.name}</span>
                          </div>
                          <div className="text-xs text-slate-400">{style.desc}</div>
                        </button>
                      ))}
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-3 mb-5">
                    <div>
                      <label className="text-sm font-medium text-slate-700 mb-2 block">目标受众</label>
                      <select
                        value={createAudience}
                        onChange={(e) => setCreateAudience(e.target.value as 'general' | 'creator' | 'professional')}
                        className="w-full px-3 py-2 rounded-xl border border-slate-200 text-sm text-slate-700 bg-white"
                      >
                        <option value="general">大众读者</option>
                        <option value="creator">自媒体创作者</option>
                        <option value="professional">行业从业者</option>
                      </select>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-slate-700 mb-2 block">内容目标</label>
                      <select
                        value={createGoal}
                        onChange={(e) => setCreateGoal(e.target.value as 'insight' | 'growth' | 'conversion')}
                        className="w-full px-3 py-2 rounded-xl border border-slate-200 text-sm text-slate-700 bg-white"
                      >
                        <option value="insight">洞察输出</option>
                        <option value="growth">互动增长</option>
                        <option value="conversion">行动转化</option>
                      </select>
                    </div>
                  </div>

                  <div className="mb-5">
                    <div className="flex items-center justify-between mb-2">
                      <label className="text-sm font-medium text-slate-700">证据强度</label>
                      <span className="text-xs text-slate-500">{createEvidenceLevel}/5</span>
                    </div>
                    <input
                      type="range"
                      min={1}
                      max={5}
                      value={createEvidenceLevel}
                      onChange={(e) => setCreateEvidenceLevel(Number(e.target.value))}
                      className="w-full"
                    />
                    <label className="mt-2 flex items-center gap-2 text-sm text-slate-600">
                      <input
                        type="checkbox"
                        checked={createStyleCard}
                        onChange={(e) => setCreateStyleCard(e.target.checked)}
                        className="rounded border-slate-300"
                      />
                      启用风格卡（强化结构与表达）
                    </label>
                  </div>

                  {/* 提示 */}
                  <div className="p-3 rounded-xl bg-violet-50 text-sm text-violet-700">
                    <p>AI 将自动为您：</p>
                    <ul className="mt-2 space-y-1 text-xs">
                      <li className="flex items-center gap-2">
                        <Check className="w-3 h-3" />
                        生成吸引人的标题
                      </li>
                      <li className="flex items-center gap-2">
                        <Check className="w-3 h-3" />
                        创作完整文章内容
                      </li>
                      <li className="flex items-center gap-2">
                        <Check className="w-3 h-3" />
                        自动生成封面图片
                      </li>
                    </ul>
                  </div>
                </div>

                <div className="flex gap-3 px-6 py-4 border-t border-slate-100 bg-slate-50">
                  <button
                    onClick={() => setShowCreateModal(false)}
                    className="flex-1 px-4 py-2.5 rounded-xl bg-white border border-slate-200 text-slate-700 font-medium hover:bg-slate-100"
                  >
                    取消
                  </button>
                  <button
                    onClick={executeQuickCreate}
                    className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-violet-500 to-purple-600 text-white font-medium hover:opacity-90"
                  >
                    <Sparkles className="w-4 h-4" />
                    开始创作
                  </button>
                </div>
              </>
            )}

            {/* 创作中步骤 */}
            {createStep === 'creating' && (
              <div className="px-6 py-10">
                <div className="text-center">
                  <div className="relative w-20 h-20 mx-auto mb-6">
                    <div className="absolute inset-0 rounded-full border-4 border-slate-100" />
                    <div 
                      className="absolute inset-0 rounded-full border-4 border-violet-500 transition-all duration-500"
                      style={{ 
                        clipPath: `polygon(50% 0%, 100% 0%, 100% 100%, 50% 100%, 50% ${100 - createProgress}%, ${50 + createProgress/2}% ${100 - createProgress}%, ${50 - createProgress/2}% ${100 - createProgress}%)`
                      }}
                    />
                    <div className="absolute inset-0 flex items-center justify-center">
                      <span className="text-lg font-bold text-violet-600">{createProgress}%</span>
                    </div>
                  </div>
                  
                  <h3 className="text-lg font-semibold text-slate-900 mb-2">
                    AI 正在创作中...
                  </h3>
                  <p className="text-sm text-slate-500">
                    {createProgress < 30 && '正在分析热点内容...'}
                    {createProgress >= 30 && createProgress < 60 && '正在构思文章结构...'}
                    {createProgress >= 60 && createProgress < 90 && '正在生成正文内容...'}
                    {createProgress >= 90 && '正在优化排版格式...'}
                  </p>
                </div>

                {/* 进度步骤 */}
                <div className="mt-8 space-y-3">
                  {[
                    { label: '分析热点', progress: 25 },
                    { label: '生成标题', progress: 50 },
                    { label: '创作内容', progress: 75 },
                    { label: '生成封面', progress: 100 },
                  ].map((step, idx) => (
                    <div key={idx} className="flex items-center gap-3">
                      <div className={`w-6 h-6 rounded-full flex items-center justify-center ${
                        createProgress >= step.progress 
                          ? 'bg-violet-500 text-white' 
                          : 'bg-slate-100 text-slate-400'
                      }`}>
                        {createProgress >= step.progress ? (
                          <Check className="w-3 h-3" />
                        ) : (
                          <span className="text-xs">{idx + 1}</span>
                        )}
                      </div>
                      <span className={`text-sm ${
                        createProgress >= step.progress ? 'text-slate-900' : 'text-slate-400'
                      }`}>
                        {step.label}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* 成功步骤 */}
            {createStep === 'success' && (
              <div className="px-6 py-8">
                <div className="text-center">
                  <div className="w-16 h-16 rounded-full bg-emerald-100 flex items-center justify-center mx-auto mb-4">
                    <Check className="w-8 h-8 text-emerald-600" />
                  </div>
                  <h3 className="text-xl font-semibold text-slate-900 mb-2">创作完成！</h3>
                  <p className="text-sm text-slate-500 mb-6">文章已生成，您可以继续编辑或直接发布</p>
                  
                  {createdArticle && (
                    <div className="p-4 rounded-xl bg-slate-50 text-left mb-6">
                      <div className="flex items-center gap-2 mb-2">
                        <FileText className="w-4 h-4 text-slate-400" />
                        <span className="text-sm font-medium text-slate-900 line-clamp-1">
                          {createdArticle.title || creatingNews.title}
                        </span>
                      </div>
                      <div className="flex items-center gap-4 text-xs text-slate-500">
                        <span className="flex items-center gap-1">
                          <PenTool className="w-3 h-3" />
                          {createdArticle.word_count || '约1000'} 字
                        </span>
                        <span className="flex items-center gap-1">
                          <Sparkles className="w-3 h-3" />
                          AI 创作
                        </span>
                      </div>
                    </div>
                  )}
                </div>

                <div className="flex flex-col gap-2">
                  <button
                    onClick={goToEdit}
                    className="flex items-center justify-center gap-2 px-4 py-3 rounded-xl bg-gradient-to-r from-violet-500 to-purple-600 text-white font-medium hover:opacity-90"
                  >
                    <PenTool className="w-4 h-4" />
                    继续编辑
                    <ArrowRight className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => setShowCreateModal(false)}
                    className="px-4 py-2.5 rounded-xl bg-slate-100 text-slate-700 font-medium hover:bg-slate-200"
                  >
                    留在当前页
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* AI大纲弹窗 */}
      {showOutlineModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" onClick={() => setShowOutlineModal(false)} />
          <div className="relative w-full max-w-2xl bg-white rounded-2xl shadow-2xl overflow-hidden">
            <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-orange-400 to-pink-500 flex items-center justify-center">
                  <Wand2 className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-slate-900">AI 智能大纲</h3>
                  <p className="text-sm text-slate-500">基于热点生成创作大纲</p>
                </div>
              </div>
              <button onClick={() => setShowOutlineModal(false)} className="p-2 rounded-lg hover:bg-slate-100">
                <X className="w-5 h-5 text-slate-500" />
              </button>
            </div>

            <div className="px-6 py-6 max-h-[60vh] overflow-y-auto">
              {selectedNewsForOutline && (
                <div className="mb-4 p-3 rounded-xl bg-slate-50">
                  <p className="text-xs text-slate-500 mb-1">参考热点</p>
                  <p className="font-medium text-slate-900 text-sm">{selectedNewsForOutline.title}</p>
                </div>
              )}

              {isGeneratingOutline ? (
                <div className="flex flex-col items-center py-12">
                  <Loader2 className="w-8 h-8 animate-spin text-violet-500 mb-4" />
                  <p className="text-slate-600 font-medium">AI 正在构思大纲...</p>
                </div>
              ) : generatedOutlines.length > 0 ? (
                <div className="space-y-3">
                  {generatedOutlines.map((outline, index) => (
                    <div key={index} className="p-4 rounded-xl bg-slate-50 hover:bg-violet-50 border border-transparent hover:border-violet-200 cursor-pointer transition-all">
                      <div className="flex items-center gap-3 mb-2">
                        <span className="w-6 h-6 rounded-lg bg-violet-500 text-white text-xs font-semibold flex items-center justify-center">
                          {index + 1}
                        </span>
                        <h4 className="font-medium text-slate-900">{outline.angle}</h4>
                      </div>
                      <p className="text-sm text-slate-600 mb-2 ml-9">{outline.title}</p>
                      <ul className="space-y-1 ml-9">
                        {outline.points?.slice(0, 3).map((point: string, pIndex: number) => (
                          <li key={pIndex} className="flex items-start gap-2 text-sm text-slate-500">
                            <div className="w-1 h-1 rounded-full bg-violet-400 mt-2 flex-shrink-0" />
                            {point}
                          </li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12">
                  <Sparkles className="w-10 h-10 text-slate-300 mx-auto mb-4" />
                  <p className="text-slate-500">生成中...</p>
                </div>
              )}
            </div>

            <div className="flex justify-end gap-3 px-6 py-4 border-t border-slate-100 bg-slate-50">
              <button
                onClick={() => setShowOutlineModal(false)}
                className="px-4 py-2 rounded-xl text-slate-600 hover:bg-slate-200 font-medium"
              >
                取消
              </button>
              {generatedOutlines.length > 0 && (
                <Link
                  href="/articles/create"
                  className="flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-900 text-white font-medium hover:bg-slate-800"
                >
                  使用此大纲
                  <ArrowRight className="w-4 h-4" />
                </Link>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
