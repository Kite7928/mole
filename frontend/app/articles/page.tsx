'use client'

import { useState } from 'react'
import { 
  FileText, 
  Plus, 
  Search, 
  Filter,
  MoreVertical,
  Eye,
  Edit,
  Trash2,
  CheckCircle,
  Clock,
  TrendingUp,
  Calendar,
  ArrowRight,
  GripVertical,
  ChevronDown,
  ChevronUp,
  Move,
  Archive,
  Copy,
  Share2
} from 'lucide-react'
import Link from 'next/link'

export default function ArticlesPage() {
  const [selectedStatus, setSelectedStatus] = useState('all')
  const [selectedSource, setSelectedSource] = useState('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [expandedStats, setExpandedStats] = useState(true)
  const [selectedArticles, setSelectedArticles] = useState<number[]>([])
  const [batchMode, setBatchMode] = useState(false)

  const statuses = [
    { id: 'all', name: '全部状态', count: 5 },
    { id: 'published', name: '已发布', count: 3 },
    { id: 'draft', name: '草稿', count: 1 },
    { id: 'generating', name: '生成中', count: 1 },
  ]

  const sources = [
    { id: 'all', name: '全部来源' },
    { id: 'ai_hotspot', name: 'AI热点' },
    { id: 'baidu_search', name: '百度搜索' },
    { id: 'manual', name: '手动创建' },
  ]

  const [articles, setArticles] = useState([
    {
      id: 1,
      title: 'GPT-4o发布：AI推理能力的新突破',
      status: 'published',
      source: 'ai_hotspot',
      sourceName: 'AI热点',
      aiModel: 'GPT-4',
      coverImage: 'https://via.placeholder.com/200x150',
      readCount: 25680,
      likeCount: 890,
      shareCount: 320,
      qualityScore: 87,
      predictedClickRate: 85,
      createdAt: '2026-01-09 10:00',
      publishedAt: '2026-01-09 10:00',
      tags: ['AI', 'GPT-4', '技术'],
    },
    {
      id: 2,
      title: 'DeepSeek-V3：开源模型的新里程碑',
      status: 'published',
      source: 'ai_hotspot',
      sourceName: 'AI热点',
      aiModel: 'GPT-4',
      coverImage: 'https://via.placeholder.com/200x150',
      readCount: 18450,
      likeCount: 654,
      shareCount: 210,
      qualityScore: 82,
      predictedClickRate: 78,
      createdAt: '2026-01-09 09:30',
      publishedAt: '2026-01-09 09:30',
      tags: ['AI', 'DeepSeek', '开源'],
    },
    {
      id: 3,
      title: 'Claude 3.5 Sonnet：长文本处理的王者',
      status: 'draft',
      source: 'baidu_search',
      sourceName: '百度搜索',
      aiModel: 'Claude 3.5',
      coverImage: 'https://via.placeholder.com/200x150',
      readCount: 0,
      likeCount: 0,
      shareCount: 0,
      qualityScore: 85,
      predictedClickRate: 72,
      createdAt: '2026-01-09 08:00',
      publishedAt: null,
      tags: ['AI', 'Claude', '长文本'],
    },
    {
      id: 4,
      title: 'Gemini Pro：谷歌AI的最新答卷',
      status: 'generating',
      source: 'manual',
      sourceName: '手动创建',
      aiModel: 'Gemini Pro',
      coverImage: null,
      readCount: 0,
      likeCount: 0,
      shareCount: 0,
      qualityScore: 0,
      predictedClickRate: 68,
      createdAt: '2026-01-09 07:30',
      publishedAt: null,
      tags: ['AI', 'Gemini', 'Google'],
    },
    {
      id: 5,
      title: '2024年AI大模型发展报告',
      status: 'published',
      source: 'ai_hotspot',
      sourceName: 'AI热点',
      aiModel: 'GPT-4',
      coverImage: 'https://via.placeholder.com/200x150',
      readCount: 10560,
      likeCount: 380,
      shareCount: 120,
      qualityScore: 90,
      predictedClickRate: 65,
      createdAt: '2026-01-08 15:00',
      publishedAt: '2026-01-08 15:00',
      tags: ['AI', '报告', '趋势'],
    },
  ])

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      published: { label: '已发布', className: 'bg-green-100 text-green-700 border-green-200' },
      draft: { label: '草稿', className: 'bg-yellow-100 text-yellow-700 border-yellow-200' },
      generating: { label: '生成中', className: 'bg-blue-100 text-blue-700 border-blue-200' },
    }
    const config = statusConfig[status as keyof typeof statusConfig]
    return (
      <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${config?.className}`}>
        {config?.label}
      </span>
    )
  }

  const getQualityScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-600'
    if (score >= 80) return 'text-blue-600'
    if (score >= 70) return 'text-yellow-600'
    return 'text-gray-500'
  }

  const handleSelectAll = () => {
    if (selectedArticles.length === articles.length) {
      setSelectedArticles([])
    } else {
      setSelectedArticles(articles.map(a => a.id))
    }
  }

  const handleSelectArticle = (id: number) => {
    if (selectedArticles.includes(id)) {
      setSelectedArticles(selectedArticles.filter(a => a !== id))
    } else {
      setSelectedArticles([...selectedArticles, id])
    }
  }

  const handleBatchDelete = () => {
    console.log('Batch delete:', selectedArticles)
    setSelectedArticles([])
    setBatchMode(false)
  }

  const handleBatchPublish = () => {
    console.log('Batch publish:', selectedArticles)
    setSelectedArticles([])
    setBatchMode(false)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">文章管理</h1>
          <p className="text-muted-foreground mt-1">管理和发布您的文章内容</p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setBatchMode(!batchMode)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg border transition-colors ${
              batchMode 
                ? 'bg-[#5a6e5c] text-white border-[#5a6e5c]' 
                : 'border-gray-300 text-gray-700 hover:bg-gray-100'
            }`}
          >
            <Archive size={20} />
            批量操作
          </button>
          <Link
            href="/articles/create"
            className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-[#5a6e5c] to-[#4a5e4c] text-white rounded-xl hover:shadow-lg hover:shadow-[#5a6e5c]/30 transition-all duration-300 font-medium"
          >
            <Plus size={20} />
            创建文章
          </Link>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-4 bg-white/50 backdrop-blur-sm rounded-2xl p-4 border border-gray-200">
        {/* Status Filter */}
        <div className="flex items-center gap-2">
          <Filter size={20} className="text-muted-foreground" />
          <span className="text-sm font-medium">状态:</span>
          <div className="flex gap-2">
            {statuses.map((status) => (
              <button
                key={status.id}
                onClick={() => setSelectedStatus(status.id)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-300 ${
                  selectedStatus === status.id
                    ? 'bg-gradient-to-r from-[#5a6e5c] to-[#4a5e4c] text-white shadow-lg'
                    : 'bg-white hover:bg-gray-100 text-gray-700 border border-gray-200'
                }`}
              >
                {status.name}
                {status.count > 0 && (
                  <span className="ml-1.5 px-2 py-0.5 rounded-full bg-gray-200 text-gray-700 text-xs">
                    {status.count}
                  </span>
                )}
              </button>
            ))}
          </div>
        </div>

        {/* Source Filter */}
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium">来源:</span>
          <div className="flex gap-2">
            {sources.map((source) => (
              <button
                key={source.id}
                onClick={() => setSelectedSource(source.id)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-300 ${
                  selectedSource === source.id
                    ? 'bg-gradient-to-r from-[#5a6e5c] to-[#4a5e4c] text-white shadow-lg'
                    : 'bg-white hover:bg-gray-100 text-gray-700 border border-gray-200'
                }`}
              >
                {source.name}
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
          placeholder="搜索文章标题、标签..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full pl-12 pr-4 py-3 rounded-xl bg-white/80 backdrop-blur-sm border border-gray-200 focus:outline-none focus:ring-2 focus:ring-[#5a6e5c] focus:border-transparent transition-all"
        />
      </div>

      {/* Collapsible Stats */}
      <div className="bg-white/80 backdrop-blur-sm rounded-2xl border border-gray-200 overflow-hidden">
        <button
          onClick={() => setExpandedStats(!expandedStats)}
          className="w-full flex items-center justify-between px-6 py-4 hover:bg-gray-50 transition-colors"
        >
          <div className="flex items-center gap-3">
            <FileText size={20} className="text-[#5a6e5c]" />
            <span className="font-semibold text-gray-900">统计概览</span>
            <span className="text-sm text-gray-500">共 {articles.length} 篇文章</span>
          </div>
          {expandedStats ? <ChevronUp size={20} className="text-gray-500" /> : <ChevronDown size={20} className="text-gray-500" />}
        </button>
        
        {expandedStats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 px-6 pb-6">
            <StatCard
              title="总文章数"
              value={articles.length}
              icon={<FileText size={24} />}
              color="from-blue-500 to-blue-600"
              bg="bg-blue-100"
              textColor="text-blue-600"
              onClick={() => setSelectedStatus('all')}
            />
            <StatCard
              title="已发布"
              value={articles.filter(a => a.status === 'published').length}
              icon={<CheckCircle size={24} />}
              color="from-green-500 to-green-600"
              bg="bg-green-100"
              textColor="text-green-600"
              onClick={() => setSelectedStatus('published')}
            />
            <StatCard
              title="草稿"
              value={articles.filter(a => a.status === 'draft').length}
              icon={<Clock size={24} />}
              color="from-yellow-500 to-yellow-600"
              bg="bg-yellow-100"
              textColor="text-yellow-600"
              onClick={() => setSelectedStatus('draft')}
            />
            <StatCard
              title="总阅读量"
              value={articles.reduce((sum, a) => sum + a.readCount, 0).toLocaleString()}
              icon={<TrendingUp size={24} />}
              color="from-purple-500 to-purple-600"
              bg="bg-purple-100"
              textColor="text-purple-600"
              onClick={() => {}}
            />
          </div>
        )}
      </div>

      {/* Batch Actions */}
      {batchMode && selectedArticles.length > 0 && (
        <div className="bg-gradient-to-r from-[#5a6e5c] to-[#4a5e4c] text-white rounded-xl px-6 py-4 flex items-center justify-between shadow-lg">
          <div className="flex items-center gap-3">
            <span className="font-medium">已选择 {selectedArticles.length} 篇文章</span>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={handleBatchPublish}
              className="flex items-center gap-2 px-4 py-2 bg-white text-[#5a6e5c] rounded-lg hover:bg-gray-100 transition-colors font-medium"
            >
              <CheckCircle size={18} />
              批量发布
            </button>
            <button
              onClick={handleBatchDelete}
              className="flex items-center gap-2 px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors font-medium"
            >
              <Trash2 size={18} />
              批量删除
            </button>
            <button
              onClick={() => setSelectedArticles([])}
              className="flex items-center gap-2 px-4 py-2 bg-white/20 text-white rounded-lg hover:bg-white/30 transition-colors"
            >
              取消选择
            </button>
          </div>
        </div>
      )}

      {/* Articles List */}
      <div className="space-y-3">
        {articles.map((article, index) => (
          <div
            key={article.id}
            className="bg-white/90 backdrop-blur-sm rounded-xl border border-gray-200 p-4 hover:shadow-lg hover:shadow-gray-500/10 transition-all duration-300 hover:border-[#5a6e5c]/30 group"
          >
            <div className="flex items-start gap-4">
              {/* Drag Handle */}
              <div className="flex items-center gap-2 pt-1">
                {batchMode && (
                  <input
                    type="checkbox"
                    checked={selectedArticles.includes(article.id)}
                    onChange={() => handleSelectArticle(article.id)}
                    className="w-4 h-4 rounded border-gray-300 text-[#5a6e5c] focus:ring-[#5a6e5c]"
                  />
                )}
                <button className="p-1 hover:bg-gray-100 rounded transition-colors cursor-grab">
                  <GripVertical size={20} className="text-gray-400" />
                </button>
              </div>

              {/* Thumbnail */}
              <div className="w-32 h-20 rounded-lg overflow-hidden flex-shrink-0 bg-gradient-to-br from-gray-100 to-gray-200">
                {article.coverImage ? (
                  <img
                    src={article.coverImage}
                    alt={article.title}
                    className="w-full h-full object-cover hover:scale-105 transition-transform duration-300"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-gray-400">
                    <FileText size={32} />
                  </div>
                )}
              </div>

              {/* Content */}
              <div className="flex-1 min-w-0">
                {/* Title Row */}
                <div className="flex items-start gap-3 mb-2">
                  <h3 className="text-lg font-semibold text-gray-900 flex-1 line-clamp-1 group-hover:text-[#5a6e5c] transition-colors">
                    {article.title}
                  </h3>
                  {getStatusBadge(article.status)}
                </div>

                {/* Tags */}
                <div className="flex items-center gap-2 mb-2">
                  {article.tags.map((tag, index) => (
                    <span
                      key={index}
                      className="px-2.5 py-1 rounded-full bg-[#5a6e5c]/10 text-[#5a6e5c] text-xs font-medium"
                    >
                      {tag}
                    </span>
                  ))}
                  <span className="text-xs text-gray-500">• {article.sourceName}</span>
                  <span className="text-xs text-gray-500">• {article.aiModel}</span>
                </div>

                {/* Stats Row */}
                <div className="flex items-center gap-6 text-sm">
                  <div className="flex items-center gap-1.5">
                    <Eye size={16} className="text-gray-400" />
                    <span className="font-medium text-gray-900">{article.readCount.toLocaleString()}</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <CheckCircle size={16} className="text-gray-400" />
                    <span className="font-medium text-gray-900">{article.likeCount}</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <Share2 size={16} className="text-gray-400" />
                    <span className="font-medium text-gray-900">{article.shareCount}</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <span className={`font-semibold ${getQualityScoreColor(article.qualityScore)}`}>
                      {article.qualityScore}
                    </span>
                    <span className="text-xs text-gray-500">质量分</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <span className="font-semibold text-yellow-600">
                      {article.predictedClickRate}%
                    </span>
                    <span className="text-xs text-gray-500">预测点击率</span>
                  </div>
                </div>
              </div>

              {/* Time */}
              <div className="flex flex-col items-end gap-1 text-sm text-gray-500">
                <div className="flex items-center gap-1.5">
                  <Calendar size={16} />
                  {article.createdAt}
                </div>
                {article.publishedAt && (
                  <div className="flex items-center gap-1.5 text-xs">
                    <Clock size={14} />
                    发布于 {article.publishedAt}
                  </div>
                )}
              </div>

              {/* Actions - Hover */}
              <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <button className="p-2 rounded-lg hover:bg-gray-100 text-gray-600 hover:text-[#5a6e5c] transition-colors" title="预览">
                  <Eye size={18} />
                </button>
                <button className="p-2 rounded-lg hover:bg-gray-100 text-gray-600 hover:text-[#5a6e5c] transition-colors" title="编辑">
                  <Edit size={18} />
                </button>
                <button className="p-2 rounded-lg hover:bg-gray-100 text-gray-600 hover:text-[#5a6e5c] transition-colors" title="复制">
                  <Copy size={18} />
                </button>
                <button className="p-2 rounded-lg hover:bg-red-100 text-gray-600 hover:text-red-600 transition-colors" title="删除">
                  <Trash2 size={18} />
                </button>
                <button className="p-2 rounded-lg hover:bg-gray-100 text-gray-600 hover:text-[#5a6e5c] transition-colors" title="更多">
                  <MoreVertical size={18} />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between">
        <div className="text-sm text-gray-600">
          显示 1-{articles.length} 条，共 {articles.length} 条
        </div>
        <div className="flex items-center gap-2">
          <button className="px-4 py-2 rounded-lg border border-gray-200 hover:bg-gray-100 transition-colors text-sm disabled:opacity-50 font-medium">
            上一页
          </button>
          <button className="px-4 py-2 rounded-lg bg-gradient-to-r from-[#5a6e5c] to-[#4a5e4c] text-white text-sm font-medium">
            1
          </button>
          <button className="px-4 py-2 rounded-lg border border-gray-200 hover:bg-gray-100 transition-colors text-sm">
            2
          </button>
          <button className="px-4 py-2 rounded-lg border border-gray-200 hover:bg-gray-100 transition-colors text-sm">
            3
          </button>
          <button className="px-4 py-2 rounded-lg border border-gray-200 hover:bg-gray-100 transition-colors text-sm">
            下一页 <ArrowRight size={14} className="inline ml-1" />
          </button>
        </div>
      </div>
    </div>
  )
}

function StatCard({ 
  title, 
  value, 
  icon,
  color,
  bg,
  textColor,
  onClick
}: { 
  title: string
  value: string | number
  icon: React.ReactNode
  color: string
  bg: string
  textColor: string
  onClick: () => void
}) {
  return (
    <button
      onClick={onClick}
      className={`w-full p-4 rounded-xl bg-gradient-to-br ${bg} hover:shadow-lg hover:shadow-gray-500/10 transition-all duration-300 hover:-translate-y-1 text-left`}
    >
      <div className="flex items-center gap-3">
        <div className={`p-2.5 rounded-lg bg-gradient-to-br ${color} text-white`}>
          {icon}
        </div>
        <div>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
          <p className={`text-sm font-medium ${textColor}`}>{title}</p>
        </div>
      </div>
    </button>
  )
}