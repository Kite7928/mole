'use client'

import { useState, useEffect } from 'react'
import { 
  FileText, 
  TrendingUp, 
  Clock, 
  CheckCircle, 
  ArrowRight,
  Sparkles,
  Flame,
  BarChart3,
  Loader2,
  User,
  Calendar
} from 'lucide-react'
import Link from 'next/link'
import { useStore } from '@/lib/store'

export default function Dashboard() {
  const { statistics, articles, hotNews, refreshStatistics, refreshHotNews, addNotification, isLoading } = useStore()
  const [isRefreshing, setIsRefreshing] = useState(false)

  const handleRefresh = async () => {
    setIsRefreshing(true)
    try {
      await Promise.all([refreshStatistics(), refreshHotNews()])
      addNotification('数据已刷新', 'success')
    } catch (error) {
      addNotification('刷新失败', 'error')
    } finally {
      setIsRefreshing(false)
    }
  }

  const handleQuickAction = (action: string) => {
    addNotification(`正在前往${action}...`, 'info')
  }

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      published: { label: '已发布', className: 'bg-emerald-100 text-emerald-700 border-emerald-200 dark:bg-emerald-500/10 dark:text-emerald-400 dark:border-emerald-500/20' },
      draft: { label: '草稿', className: 'bg-amber-100 text-amber-700 border-amber-200 dark:bg-amber-500/10 dark:text-amber-400 dark:border-amber-500/20' },
      generating: { label: '生成中', className: 'bg-blue-100 text-blue-700 border-blue-200 dark:bg-blue-500/10 dark:text-blue-400 dark:border-blue-500/20' },
    }
    const config = statusConfig[status as keyof typeof statusConfig]
    return (
      <span className={`px-2.5 py-1 rounded-full text-xs font-semibold border ${config?.className}`}>
        {config?.label}
      </span>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold art-gradient-text">仪表板</h1>
          <p className="text-slate-600 dark:text-slate-400 mt-1">欢迎回来，开始今天的创作之旅</p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handleRefresh}
            disabled={isRefreshing}
            className="flex items-center gap-2 px-4 py-2 rounded-xl border border-slate-300 dark:border-slate-600 hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors text-slate-700 dark:text-slate-300 disabled:opacity-50"
          >
            {isRefreshing ? (
              <>
                <Loader2 size={20} className="animate-spin" />
                刷新中...
              </>
            ) : (
              <>
                <TrendingUp size={20} />
                刷新数据
              </>
            )}
          </button>
          <Link
            href="/articles/create"
            onClick={() => handleQuickAction('AI写作')}
            className="flex items-center justify-center gap-2 px-6 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl hover:shadow-lg hover:shadow-indigo-500/30 transition-all duration-300 font-medium"
          >
            <Sparkles size={20} />
            开始创作
          </Link>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="总文章数"
          value={statistics.totalArticles}
          icon={<FileText size={24} />}
          trend={`+${statistics.growthRate.read}%`}
          trendUp
          color="blue"
        />
        <StatCard
          title="今日发布"
          value={statistics.publishedToday}
          icon={<CheckCircle size={24} />}
          trend="+3"
          trendUp
          color="emerald"
        />
        <StatCard
          title="总阅读量"
          value={statistics.totalReads.toLocaleString()}
          icon={<TrendingUp size={24} />}
          trend={`+${statistics.growthRate.read}%`}
          trendUp
          color="purple"
        />
        <StatCard
          title="平均阅读时间"
          value={`${statistics.avgReadTime}min`}
          icon={<Clock size={24} />}
          trend="+0.5min"
          trendUp
          color="orange"
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Articles */}
        <div className="lg:col-span-2 bg-white/95 dark:bg-slate-800/95 backdrop-blur-xl rounded-2xl border border-slate-200 dark:border-slate-700 p-6 shadow-sm">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-slate-900 dark:text-white">最近文章</h2>
            <Link
              href="/articles"
              className="flex items-center gap-1 text-sm text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 dark:hover:text-indigo-300 transition-colors font-medium"
            >
              查看全部 <ArrowRight size={16} />
            </Link>
          </div>
          <div className="space-y-3">
            {articles.slice(0, 5).map((article) => (
              <div
                key={article.id}
                className="flex items-start gap-4 p-4 rounded-xl bg-slate-50 dark:bg-slate-700/50 hover:bg-slate-100 dark:hover:bg-slate-700 transition-all duration-300 border border-slate-200 dark:border-slate-600 hover:border-indigo-300 dark:hover:border-indigo-500/50 cursor-pointer group"
                onClick={() => {
                  addNotification(`查看文章: ${article.title}`, 'info')
                }}
              >
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-2">
                    {getStatusBadge(article.status)}
                    <span className="text-xs text-slate-500 dark:text-slate-400">
                      {article.publishedAt || article.createdAt}
                    </span>
                  </div>
                  <h3 className="font-medium mb-2 truncate text-slate-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">
                    {article.title}
                  </h3>
                  <div className="flex items-center gap-4 text-sm text-slate-600 dark:text-slate-400">
                    <span className="flex items-center gap-1">
                      <TrendingUp size={16} className="text-indigo-500" />
                      {article.readCount.toLocaleString()} 阅读
                    </span>
                    <span className="flex items-center gap-1">
                      <CheckCircle size={16} className="text-emerald-500" />
                      {article.likeCount} 点赞
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Hot News */}
        <div className="bg-white/95 dark:bg-slate-800/95 backdrop-blur-xl rounded-2xl border border-slate-200 dark:border-slate-700 p-6 shadow-sm">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-slate-900 dark:text-white">热点新闻</h2>
            <Link
              href="/hotspots"
              className="flex items-center gap-1 text-sm text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 dark:hover:text-indigo-300 transition-colors font-medium"
            >
              查看全部 <ArrowRight size={16} />
            </Link>
          </div>
          <div className="space-y-3">
            {hotNews.slice(0, 3).map((news) => (
              <div
                key={news.id}
                className="p-4 rounded-xl bg-slate-50 dark:bg-slate-700/50 hover:bg-slate-100 dark:hover:bg-slate-700 transition-all duration-300 border border-slate-200 dark:border-slate-600 hover:border-orange-300 dark:hover:border-orange-500/50 cursor-pointer group"
                onClick={() => {
                  addNotification(`查看热点: ${news.title}`, 'info')
                }}
              >
                <div className="flex items-center gap-2 mb-2">
                  <Flame size={16} className="text-orange-500" />
                  <span className="text-sm font-semibold text-orange-600 dark:text-orange-400">
                    热度: {news.hotScore}
                  </span>
                </div>
                <h3 className="font-medium mb-2 text-slate-900 dark:text-white group-hover:text-orange-600 dark:group-hover:text-orange-400 transition-colors line-clamp-2">
                  {news.title}
                </h3>
                <div className="flex items-center justify-between text-sm text-slate-500 dark:text-slate-400">
                  <span className="flex items-center gap-1">
                    <User size={14} />
                    {news.sourceName}
                  </span>
                  <span className="flex items-center gap-1">
                    <Calendar size={14} />
                    {news.publishedAt}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white/95 dark:bg-slate-800/95 backdrop-blur-xl rounded-2xl border border-slate-200 dark:border-slate-700 p-6 shadow-sm">
        <h2 className="text-xl font-semibold text-slate-900 dark:text-white mb-6">快捷操作</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <QuickActionCard
            title="创建新文章"
            description="使用AI快速生成高质量内容"
            icon={<Sparkles size={32} />}
            href="/articles/create"
            onClick={() => handleQuickAction('创建新文章')}
            color="indigo"
          />
          <QuickActionCard
            title="查看热点"
            description="实时监控科技圈热点话题"
            icon={<Flame size={32} />}
            href="/hotspots"
            onClick={() => handleQuickAction('查看热点')}
            color="orange"
          />
          <QuickActionCard
            title="数据统计"
            description="查看文章表现和数据趋势"
            icon={<BarChart3 size={32} />}
            href="/statistics"
            onClick={() => handleQuickAction('数据统计')}
            color="emerald"
          />
        </div>
      </div>
    </div>
  )
}

function StatCard({ 
  title, 
  value, 
  icon, 
  trend, 
  trendUp,
  color
}: { 
  title: string
  value: string | number
  icon: React.ReactNode
  trend: string
  trendUp: boolean
  color: 'blue' | 'emerald' | 'purple' | 'orange'
}) {
  const colorConfig = {
    blue: {
      bg: 'bg-blue-100 dark:bg-blue-500/10',
      text: 'text-blue-600 dark:text-blue-400',
      iconBg: 'bg-gradient-to-br from-blue-500/20 to-blue-600/20 dark:from-blue-500/10 dark:to-blue-600/10',
      iconText: 'text-blue-600 dark:text-blue-400'
    },
    emerald: {
      bg: 'bg-emerald-100 dark:bg-emerald-500/10',
      text: 'text-emerald-600 dark:text-emerald-400',
      iconBg: 'bg-gradient-to-br from-emerald-500/20 to-emerald-600/20 dark:from-emerald-500/10 dark:to-emerald-600/10',
      iconText: 'text-emerald-600 dark:text-emerald-400'
    },
    purple: {
      bg: 'bg-purple-100 dark:bg-purple-500/10',
      text: 'text-purple-600 dark:text-purple-400',
      iconBg: 'bg-gradient-to-br from-purple-500/20 to-purple-600/20 dark:from-purple-500/10 dark:to-purple-600/10',
      iconText: 'text-purple-600 dark:text-purple-400'
    },
    orange: {
      bg: 'bg-orange-100 dark:bg-orange-500/10',
      text: 'text-orange-600 dark:text-orange-400',
      iconBg: 'bg-gradient-to-br from-orange-500/20 to-orange-600/20 dark:from-orange-500/10 dark:to-orange-600/10',
      iconText: 'text-orange-600 dark:text-orange-400'
    }
  }

  const config = colorConfig[color]

  return (
    <div className="bg-white/95 dark:bg-slate-800/95 backdrop-blur-xl rounded-2xl p-5 border border-slate-200 dark:border-slate-700 shadow-sm hover:shadow-lg hover:shadow-indigo-500/10 transition-all duration-300 hover:-translate-y-1">
      <div className="flex items-start justify-between mb-4">
        <div className={`p-2.5 rounded-xl ${config.iconBg} ${config.iconText}`}>
          {icon}
        </div>
        <span className={`text-sm font-semibold px-2.5 py-1 rounded-full ${trendUp ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-400' : 'bg-red-100 text-red-700 dark:bg-red-500/10 dark:text-red-400'}`}>
          {trend}
        </span>
      </div>
      <p className="text-2xl font-bold mb-1 text-slate-900 dark:text-white">{value}</p>
      <p className="text-sm text-slate-600 dark:text-slate-400">{title}</p>
    </div>
  )
}

function QuickActionCard({
  title,
  description,
  icon,
  href,
  onClick,
  color
}: {
  title: string
  description: string
  icon: React.ReactNode
  href: string
  onClick: () => void
  color: 'indigo' | 'orange' | 'emerald'
}) {
  const colorConfig = {
    indigo: {
      bg: 'bg-indigo-100 dark:bg-indigo-500/10',
      text: 'text-indigo-600 dark:text-indigo-400',
      hoverBg: 'hover:from-indigo-500/30 hover:to-purple-500/30',
      hoverText: 'group-hover:text-indigo-700 dark:group-hover:text-indigo-300'
    },
    orange: {
      bg: 'bg-orange-100 dark:bg-orange-500/10',
      text: 'text-orange-600 dark:text-orange-400',
      hoverBg: 'hover:from-orange-500/30 hover:to-red-500/30',
      hoverText: 'group-hover:text-orange-700 dark:group-hover:text-orange-300'
    },
    emerald: {
      bg: 'bg-emerald-100 dark:bg-emerald-500/10',
      text: 'text-emerald-600 dark:text-emerald-400',
      hoverBg: 'hover:from-emerald-500/30 hover:to-teal-500/30',
      hoverText: 'group-hover:text-emerald-700 dark:group-hover:text-emerald-300'
    }
  }

  const config = colorConfig[color]

  return (
    <Link
      href={href}
      onClick={onClick}
      className="flex flex-col items-center gap-4 p-6 rounded-xl bg-slate-50 dark:bg-slate-700/50 hover:bg-slate-100 dark:hover:bg-slate-700 transition-all duration-300 border border-slate-200 dark:border-slate-600 hover:border-indigo-300 dark:hover:border-indigo-500/50 group"
    >
      <div className={`p-4 rounded-xl bg-gradient-to-br ${config.bg} ${config.text} transition-all duration-300 ${config.hoverBg}`}>
        {icon}
      </div>
      <div className="text-center">
        <h3 className="font-semibold mb-1 text-slate-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">
          {title}
        </h3>
        <p className="text-sm text-slate-600 dark:text-slate-400">{description}</p>
      </div>
    </Link>
  )
}