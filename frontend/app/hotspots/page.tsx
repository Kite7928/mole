'use client'

import { useState, useEffect } from 'react'
import { 
  Flame, 
  RefreshCw, 
  Search, 
  Filter,
  Clock,
  TrendingUp,
  Bookmark,
  Sparkles,
  Loader2,
  Grid3x3,
  List,
  Tag,
  Link as LinkIcon,
  ExternalLink,
  Wand2,
  X
} from 'lucide-react'
import Link from 'next/link'
import { API_URL } from '@/lib/api'

// 热点新闻类型定义
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
  const [selectedPlatform, setSelectedPlatform] = useState('all')
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [selectedTime, setSelectedTime] = useState('24h')
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const [showCluster, setShowCluster] = useState(false)

  // 大纲生成相关状态
  const [showOutlineModal, setShowOutlineModal] = useState(false)
  const [isGeneratingOutline, setIsGeneratingOutline] = useState(false)
  const [generatedOutlines, setGeneratedOutlines] = useState<any[]>([])
  const [selectedNewsForOutline, setSelectedNewsForOutline] = useState<any>(null)

  // 热点详情相关状态
  const [showDetailModal, setShowDetailModal] = useState(false)
  const [selectedNewsForDetail, setSelectedNewsForDetail] = useState<any>(null)
  const [isGeneratingArticle, setIsGeneratingArticle] = useState(false)

  // 预警订阅相关状态
  const [showSubscriptionModal, setShowSubscriptionModal] = useState(false)
  const [subscriptions, setSubscriptions] = useState<any[]>([])

  // 竞品对比相关状态
  const [showCompetitorModal, setShowCompetitorModal] = useState(false)
  const [competitorAccounts, setCompetitorAccounts] = useState<string[]>([''])
  const [competitorAnalysis, setCompetitorAnalysis] = useState<any>(null)

  // 页面加载时获取新闻数据
  useEffect(() => {
    fetchNews()
  }, [selectedPlatform])

  const fetchNews = async () => {
    try {
      const response = await fetch(`${API_URL}/api/news?limit=50`)
      const data = await response.json()
      if (data.items && data.items.length > 0) {
        // 处理数据，添加缺失的字段
        const processedNews = data.items
          .filter((item: any) => {
            // 根据选择的平台筛选
            if (selectedPlatform === 'all') return true
            return item.source === selectedPlatform
          })
          .map((item: any) => ({
            id: item.id,
            title: item.title,
            summary: item.summary?.replace(/<[^>]*>/g, '').substring(0, 200) || item.title,
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
          }))
        setHotNews(processedNews)
      }
    } catch (error) {
      console.error('获取新闻失败:', error)
    }
  }

  // 获取来源图标
  const getSourceLogo = (source: string) => {
    const logos: Record<string, string> = {
      'ithome': '🏠',
      '36kr': '🚀',
      'baidu': '🔍',
      'zhihu': '📚',
      'weibo': '📱'
    }
    return logos[source] || '📰'
  }

  // 格式化发布时间
  const formatPublishedAt = (publishedAt: string) => {
    if (!publishedAt) return '刚刚'
    const now = new Date()
    const published = new Date(publishedAt)
    const diff = Math.floor((now.getTime() - published.getTime()) / 1000 / 60) // 分钟
    
    if (diff < 60) return `${diff}分钟前`
    if (diff < 1440) return `${Math.floor(diff / 60)}小时前`
    return `${Math.floor(diff / 1440)}天前`
  }

  const platforms = [
    { id: 'all', name: '全部' },
    { id: 'ithome', name: 'IT之家' },
    { id: 'baidu', name: '百度资讯' },
  ]

  const categories = [
    { id: 'all', name: '全部' },
    { id: 'ai', name: 'AI' },
    { id: 'tech', name: '科技' },
    { id: 'startup', name: '创业' },
    { id: 'product', name: '产品' },
  ]

  const timeRanges = [
    { id: '1h', name: '1小时' },
    { id: '6h', name: '6小时' },
    { id: '24h', name: '24小时' },
    { id: '7d', name: '7天' },
  ]

  const [hotNews, setHotNews] = useState<HotNewsItem[]>([])

  const handleRefresh = async () => {
    setIsRefreshing(true)
    try {
      // 根据当前选择的平台刷新新闻
      const source = selectedPlatform === 'all' ? 'ithome' : selectedPlatform
      
      const response = await fetch(`${API_URL}/api/news/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ source: source, limit: 20 })
      })
      const data = await response.json()
      if (data.success) {
        // 刷新成功后重新获取新闻列表
        await fetchNews()
      }
    } catch (error) {
      console.error('刷新失败:', error)
    } finally {
      setIsRefreshing(false)
    }
  }

  const handleCluster = () => {
    setShowCluster(true)
    // 热点聚类逻辑
    console.log('Clustering hotspots')
    setTimeout(() => setShowCluster(false), 2000)
  }

  const handleGenerateOutline = async (news: any) => {
    setSelectedNewsForOutline(news)
    setShowOutlineModal(true)
    setIsGeneratingOutline(true)
    setGeneratedOutlines([])
    
    try {
      const response = await fetch(`${API_URL}/api/articles/generate-outlines`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          topic: news.title,
          source_url: news.url
        })
      })
      const data = await response.json()
      
      if (data.success && data.outlines) {
        setGeneratedOutlines(data.outlines)
      } else {
        alert(data.error || '生成大纲失败')
      }
    } catch (error) {
      console.error('生成大纲失败:', error)
      alert('生成大纲失败，请检查AI配置')
    } finally {
      setIsGeneratingOutline(false)
    }
  }

  const getHotScoreBorder = (score: number) => {
    if (score >= 90) return 'border-red-400 shadow-red-400/20'
    if (score >= 80) return 'border-orange-400 shadow-orange-400/20'
    if (score >= 70) return 'border-yellow-400 shadow-yellow-400/20'
    return 'border-gray-300 shadow-gray-300/20'
  }

  const getHotScoreGradient = (score: number) => {
    if (score >= 90) return 'from-red-500 to-orange-500'
    if (score >= 80) return 'from-orange-500 to-yellow-500'
    if (score >= 70) return 'from-yellow-500 to-green-500'
    return 'from-gray-400 to-gray-500'
  }

  // 处理生成完整文章
  const handleGenerateFullArticle = async (outline: any) => {
    if (!selectedNewsForOutline) return
    
    setIsGeneratingArticle(true)
    try {
      const response = await fetch(`${API_URL}/api/articles`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: outline.title,
          content: outline.points.map((p: string) => `## ${p}\n`).join('\n'),
          summary: outline.angle,
          source_topic: selectedNewsForOutline.title,
          source_url: selectedNewsForOutline.url,
          status: 'draft',
          tags: selectedNewsForOutline.tags,
          generate_cover_image: true
        })
      })
      const data = await response.json()
      
      if (data.id) {
        alert('文章创建成功！正在跳转到编辑页面...')
        window.location.href = `/articles/create?id=${data.id}`
      } else {
        alert('文章创建失败')
      }
    } catch (error) {
      console.error('生成文章失败:', error)
      alert('生成文章失败，请稍后重试')
    } finally {
      setIsGeneratingArticle(false)
    }
  }

  // 处理显示热点详情
  const handleShowDetail = (news: any) => {
    setSelectedNewsForDetail(news)
    setShowDetailModal(true)
  }

  // 处理添加订阅
  const handleAddSubscription = (keyword: string, threshold: number) => {
    const newSubscription = {
      id: Date.now(),
      keyword,
      threshold,
      createdAt: new Date().toISOString()
    }
    setSubscriptions([...subscriptions, newSubscription])
    alert(`已添加订阅：${keyword}（热度阈值：${threshold}）`)
    setShowSubscriptionModal(false)
  }

  // 处理竞品分析
  const handleCompetitorAnalysis = async () => {
    if (!selectedNewsForDetail) return
    
    const validAccounts = competitorAccounts.filter(acc => acc.trim())
    if (validAccounts.length === 0) {
      alert('请输入至少一个竞品账号')
      return
    }

    try {
      // 模拟竞品分析
      const mockAnalysis = {
        overlapScore: 65,
        competitorTopics: [
          { title: 'AI大模型应用', hotScore: 85 },
          { title: '新能源汽车', hotScore: 78 },
          { title: '智能硬件', hotScore: 72 }
        ],
        ourTopics: [
          { title: selectedNewsForDetail.title, hotScore: selectedNewsForDetail.hotScore },
          { title: 'AI写作助手', hotScore: 75 },
          { title: '内容创作', hotScore: 68 }
        ]
      }
      setCompetitorAnalysis(mockAnalysis)
    } catch (error) {
      console.error('竞品分析失败:', error)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">热点监控</h1>
          <p className="text-muted-foreground mt-1">实时监控科技圈热点话题</p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handleCluster}
            className="flex items-center gap-2 px-4 py-2 rounded-lg border border-[#5a6e5c] text-[#5a6e5c] hover:bg-[#5a6e5c] hover:text-white transition-colors"
          >
            <Grid3x3 size={20} />
            热点聚类
          </button>
          <button
            onClick={handleRefresh}
            disabled={isRefreshing}
            className="flex items-center gap-2 px-4 py-2 rounded-lg border border-border hover:bg-secondary transition-colors disabled:opacity-50"
          >
            {isRefreshing ? (
              <>
                <Loader2 size={20} className="animate-spin" />
                刷新中...
              </>
            ) : (
              <>
                <RefreshCw size={20} />
                刷新
              </>
            )}
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-4 bg-white/50 backdrop-blur-sm rounded-2xl p-4 border border-gray-200">
        {/* Platform Filter */}
        <div className="flex items-center gap-2">
          <Filter size={20} className="text-muted-foreground" />
          <span className="text-sm font-medium">平台:</span>
          <div className="flex gap-2">
            {platforms.map((platform) => (
              <button
                key={platform.id}
                onClick={() => setSelectedPlatform(platform.id)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-300 ${
                  selectedPlatform === platform.id
                    ? 'bg-gradient-to-r from-[#5a6e5c] to-[#4a5e4c] text-white shadow-lg'
                    : 'bg-white hover:bg-gray-100 text-gray-700 border border-gray-200'
                }`}
              >
                {platform.name}
              </button>
            ))}
          </div>
        </div>

        {/* Category Filter */}
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium">分类:</span>
          <div className="flex gap-2">
            {categories.map((category) => (
              <button
                key={category.id}
                onClick={() => setSelectedCategory(category.id)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-300 ${
                  selectedCategory === category.id
                    ? 'bg-gradient-to-r from-[#5a6e5c] to-[#4a5e4c] text-white shadow-lg'
                    : 'bg-white hover:bg-gray-100 text-gray-700 border border-gray-200'
                }`}
              >
                {category.name}
              </button>
            ))}
          </div>
        </div>

        {/* Time Filter */}
        <div className="flex items-center gap-2">
          <Clock size={20} className="text-muted-foreground" />
          <span className="text-sm font-medium">时间:</span>
          <div className="flex gap-2">
            {timeRanges.map((range) => (
              <button
                key={range.id}
                onClick={() => setSelectedTime(range.id)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-300 ${
                  selectedTime === range.id
                    ? 'bg-gradient-to-r from-[#5a6e5c] to-[#4a5e4c] text-white shadow-lg'
                    : 'bg-white hover:bg-gray-100 text-gray-700 border border-gray-200'
                }`}
              >
                {range.name}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-muted-foreground" size={20} />
        <input
          type="text"
          placeholder="搜索热点新闻..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full pl-12 pr-4 py-3 rounded-xl bg-white/80 backdrop-blur-sm border border-gray-200 focus:outline-none focus:ring-2 focus:ring-[#5a6e5c] focus:border-transparent transition-all"
        />
      </div>

      {/* View Mode Toggle */}
      <div className="flex items-center justify-end gap-2">
        <button
          onClick={() => setViewMode('grid')}
          className={`p-2 rounded-lg transition-colors ${
            viewMode === 'grid' ? 'bg-[#5a6e5c] text-white' : 'bg-white hover:bg-gray-100 text-gray-700'
          }`}
        >
          <Grid3x3 size={20} />
        </button>
        <button
          onClick={() => setViewMode('list')}
          className={`p-2 rounded-lg transition-colors ${
            viewMode === 'list' ? 'bg-[#5a6e5c] text-white' : 'bg-white hover:bg-gray-100 text-gray-700'
          }`}
        >
          <List size={20} />
        </button>
      </div>

      {/* Cluster Animation */}
      {showCluster && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center">
          <div className="bg-white rounded-2xl p-8 shadow-2xl">
            <div className="flex items-center gap-4">
              <Loader2 size={32} className="animate-spin text-[#5a6e5c]" />
              <div>
                <h3 className="text-lg font-semibold">正在聚类热点...</h3>
                <p className="text-sm text-gray-600">自动归类相似主题</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Hot News Grid */}
      <div className={`grid gap-5 ${
        viewMode === 'grid' ? 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3' : 'grid-cols-1'
      }`}>
        {hotNews.map((news) => (
          <div
            key={news.id}
            className={`bg-white/90 backdrop-blur-sm rounded-2xl p-5 border-2 ${getHotScoreBorder(news.hotScore)} shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-1`}
          >
            {/* Image - 使用CSS渐变背景 */}
            <div className="w-full h-48 rounded-xl overflow-hidden bg-gradient-to-br from-[#5a6e5c] to-[#4a5e4c] mb-4 flex items-center justify-center relative group">
              <div className="absolute inset-0 bg-gradient-to-br from-purple-500/20 to-blue-500/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
              <div className="relative z-10 text-center p-4">
                <div className="text-4xl mb-2">{news.sourceLogo}</div>
                <p className="text-white/90 text-sm font-medium line-clamp-2">{news.title}</p>
              </div>
            </div>

            {/* Hot Score Badge */}
            <div className="flex items-center gap-2 mb-3">
              <div className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-gradient-to-r ${getHotScoreGradient(news.hotScore)} text-white shadow-md`}>
                <Flame size={16} />
                <span className="text-sm font-bold">{news.hotScore}</span>
              </div>
              <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-gray-100 text-gray-700">
                <span className="text-lg">{news.sourceLogo}</span>
                <span className="text-sm font-medium">{news.sourceName}</span>
              </div>
            </div>

            {/* Title */}
            <h3 className="text-lg font-bold mb-2 line-clamp-2 hover:text-[#5a6e5c] cursor-pointer transition-colors">
              {news.title}
            </h3>

            {/* Summary */}
            <p className="text-sm text-gray-600 mb-3 line-clamp-2">
              {news.summary}
            </p>

            {/* Tags */}
            <div className="flex flex-wrap gap-2 mb-3">
              {news.tags.map((tag, index) => (
                <span
                  key={index}
                  className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-[#5a6e5c]/10 text-[#5a6e5c] text-xs font-medium"
                >
                  <Tag size={12} />
                  {tag}
                </span>
              ))}
            </div>

            {/* Footer */}
            <div className="flex items-center justify-between pt-3 border-t border-gray-200">
              <div className="flex items-center gap-1.5 text-xs text-gray-500">
                <Clock size={14} />
                {news.publishedAt}
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => handleShowDetail(news)}
                  className="p-2 rounded-lg hover:bg-gray-100 text-gray-600 hover:text-[#5a6e5c] transition-colors"
                  title="查看详情"
                >
                  <TrendingUp size={18} />
                </button>
                <a
                  href={news.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="p-2 rounded-lg hover:bg-gray-100 text-gray-600 hover:text-[#5a6e5c] transition-colors"
                  title="查看原文"
                >
                  <ExternalLink size={18} />
                </a>
                <button
                  className="p-2 rounded-lg hover:bg-gray-100 text-gray-600 hover:text-[#5a6e5c] transition-colors"
                  title="收藏"
                >
                  <Bookmark size={18} />
                </button>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="mt-4 space-y-2">
              <button
                onClick={() => handleGenerateOutline(news)}
                className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-purple-500 to-purple-600 text-white rounded-xl font-medium hover:shadow-lg hover:shadow-purple-500/30 transition-all duration-300"
              >
                <Wand2 size={18} />
                AI生成大纲
              </button>
              <Link
                href="/articles/create"
                className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-[#5a6e5c] to-[#4a5e4c] text-white rounded-xl font-medium hover:shadow-lg hover:shadow-[#5a6e5c]/30 transition-all duration-300"
              >
                <Sparkles size={18} />
                关联创作
              </Link>
            </div>
          </div>
        ))}
      </div>

      {/* Load More */}
      <div className="text-center">
        <button className="flex items-center justify-center gap-2 px-8 py-4 rounded-xl bg-white/80 backdrop-blur-sm border border-gray-200 hover:bg-gray-50 hover:border-[#5a6e5c] transition-all duration-300 font-medium">
          加载更多
          <TrendingUp size={20} className="text-[#5a6e5c]" />
        </button>
      </div>

      {/* 大纲生成弹窗 */}
      {showOutlineModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[80vh] overflow-hidden">
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b">
              <div>
                <h3 className="text-xl font-bold">AI生成3种差异化大纲</h3>
                <p className="text-sm text-gray-600 mt-1">主题：{selectedNewsForOutline?.title}</p>
              </div>
              <button
                onClick={() => setShowOutlineModal(false)}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <X size={20} />
              </button>
            </div>

            {/* Content */}
            <div className="p-6 overflow-y-auto max-h-[60vh]">
              {isGeneratingOutline ? (
                <div className="flex flex-col items-center justify-center py-12">
                  <Loader2 size={32} className="animate-spin text-[#5a6e5c]" />
                  <p className="mt-4 text-gray-600">正在生成大纲...</p>
                </div>
              ) : generatedOutlines.length > 0 ? (
                <div className="space-y-4">
                  {generatedOutlines.map((outline, index) => (
                    <div key={index} className="border-2 rounded-xl p-5 hover:border-[#5a6e5c] transition-colors">
                      <div className="flex items-start justify-between mb-3">
                        <div>
                          <h4 className="font-bold text-lg text-[#5a6e5c]">{outline.angle}</h4>
                          <p className="text-sm text-gray-600 mt-1">建议标题：{outline.title}</p>
                        </div>
                        <div className="bg-[#5a6e5c]/10 text-[#5a6e5c] px-3 py-1 rounded-full text-sm">
                          大纲 {index + 1}
                        </div>
                      </div>
                      <ul className="space-y-2 ml-4">
                        {outline.points.map((point: string, pIndex: number) => (
                          <li key={pIndex} className="flex items-start gap-2">
                            <div className="w-2 h-2 rounded-full bg-[#5a6e5c] mt-2 flex-shrink-0" />
                            <span className="text-gray-700">{point}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12 text-gray-500">
                  <p>暂无大纲数据</p>
                </div>
              )}
            </div>

            {/* Footer */}
            <div className="flex justify-end gap-3 p-6 border-t bg-gray-50">
              <button
                onClick={() => setShowOutlineModal(false)}
                className="px-6 py-2 rounded-lg border border-gray-300 hover:bg-gray-100 transition-colors"
              >
                关闭
              </button>
              {generatedOutlines.length > 0 && (
                <Link
                  href="/articles/create"
                  className="px-6 py-2 rounded-lg bg-gradient-to-r from-[#5a6e5c] to-[#4a5e4c] text-white hover:shadow-lg transition-all"
                >
                  使用此大纲创建文章
                </Link>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}