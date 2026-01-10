'use client'

import { useState } from 'react'
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
  ExternalLink
} from 'lucide-react'
import Link from 'next/link'

export default function HotspotsPage() {
  const [selectedPlatform, setSelectedPlatform] = useState('all')
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [selectedTime, setSelectedTime] = useState('24h')
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const [showCluster, setShowCluster] = useState(false)

  const platforms = [
    { id: 'all', name: '全部' },
    { id: 'ithome', name: 'IT之家' },
    { id: '36kr', name: '36氪' },
    { id: 'baidu', name: '百度' },
    { id: 'zhihu', name: '知乎' },
    { id: 'weibo', name: '微博' },
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

  const [hotNews, setHotNews] = useState([
    {
      id: 1,
      title: 'GPT-4o发布：AI推理能力的新突破',
      summary: 'OpenAI今日正式发布GPT-4o，在推理能力上实现重大突破，多项基准测试超越前代模型。',
      source: 'ithome',
      sourceName: 'IT之家',
      sourceLogo: '🏠',
      url: 'https://ithome.com/xxx',
      hotScore: 95,
      publishedAt: '2小时前',
      imageUrl: 'https://via.placeholder.com/400x300',
      category: 'ai',
      tags: ['AI', 'GPT-4', 'OpenAI'],
    },
    {
      id: 2,
      title: 'DeepSeek-V3：开源模型的新里程碑',
      summary: 'DeepSeek今日发布V3版本，性能媲美GPT-4，开源社区反响热烈。',
      source: '36kr',
      sourceName: '36氪',
      sourceLogo: '🚀',
      url: 'https://36kr.com/xxx',
      hotScore: 88,
      publishedAt: '3小时前',
      imageUrl: 'https://via.placeholder.com/400x300',
      category: 'ai',
      tags: ['AI', 'DeepSeek', '开源'],
    },
    {
      id: 3,
      title: 'Claude 3.5 Sonnet：长文本处理的王者',
      summary: 'Anthropic发布Claude 3.5 Sonnet，支持20万token上下文，长文本处理能力显著提升。',
      source: 'zhihu',
      sourceName: '知乎',
      sourceLogo: '📚',
      url: 'https://zhihu.com/xxx',
      hotScore: 82,
      publishedAt: '5小时前',
      imageUrl: 'https://via.placeholder.com/400x300',
      category: 'ai',
      tags: ['AI', 'Claude', '长文本'],
    },
    {
      id: 4,
      title: 'Gemini Pro：谷歌AI的最新答卷',
      summary: 'Google发布Gemini Pro，多模态能力显著提升，在图像和视频理解方面表现优异。',
      source: 'baidu',
      sourceName: '百度',
      sourceLogo: '🔍',
      url: 'https://baidu.com/xxx',
      hotScore: 75,
      publishedAt: '6小时前',
      imageUrl: 'https://via.placeholder.com/400x300',
      category: 'ai',
      tags: ['AI', 'Gemini', 'Google'],
    },
    {
      id: 5,
      title: '2024年AI大模型发展报告',
      summary: '知名机构发布2024年AI大模型发展报告，深度分析行业趋势和未来展望。',
      source: 'weibo',
      sourceName: '微博',
      sourceLogo: '📱',
      url: 'https://weibo.com/xxx',
      hotScore: 68,
      publishedAt: '8小时前',
      imageUrl: 'https://via.placeholder.com/400x300',
      category: 'ai',
      tags: ['AI', '报告', '趋势'],
    },
    {
      id: 6,
      title: 'AI芯片战争升级：英伟达vsAMD',
      summary: 'AI芯片市场竞争加剧，英伟达和AMD纷纷推出新一代产品，性能对比引发热议。',
      source: 'ithome',
      sourceName: 'IT之家',
      sourceLogo: '🏠',
      url: 'https://ithome.com/xxx',
      hotScore: 72,
      publishedAt: '10小时前',
      imageUrl: 'https://via.placeholder.com/400x300',
      category: 'tech',
      tags: ['芯片', '英伟达', 'AMD'],
    },
  ])

  const handleRefresh = async () => {
    setIsRefreshing(true)
    // 模拟刷新
    await new Promise(resolve => setTimeout(resolve, 2000))
    setIsRefreshing(false)
  }

  const handleCluster = () => {
    setShowCluster(true)
    // 热点聚类逻辑
    console.log('Clustering hotspots')
    setTimeout(() => setShowCluster(false), 2000)
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
            {/* Image */}
            <div className="w-full h-48 rounded-xl overflow-hidden bg-gradient-to-br from-gray-100 to-gray-200 mb-4">
              <img
                src={news.imageUrl}
                alt={news.title}
                className="w-full h-full object-cover hover:scale-105 transition-transform duration-300"
              />
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

            {/* Quick Action - 关联创作 */}
            <Link
              href="/articles/create"
              className="mt-4 w-full flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-[#5a6e5c] to-[#4a5e4c] text-white rounded-xl font-medium hover:shadow-lg hover:shadow-[#5a6e5c]/30 transition-all duration-300"
            >
              <Sparkles size={18} />
              关联创作
            </Link>
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
    </div>
  )
}