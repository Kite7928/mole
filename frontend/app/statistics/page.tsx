'use client'

import { useState } from 'react'
import { 
  BarChart3, 
  TrendingUp, 
  Download, 
  RefreshCw,
  Calendar,
  Eye,
  Heart,
  Share2,
  ArrowUp,
  ArrowDown,
  Loader2,
  Sparkles
} from 'lucide-react'

export default function StatisticsPage() {
  const [selectedDays, setSelectedDays] = useState('7')
  const [selectedAccount, setSelectedAccount] = useState('all')
  const [isRefreshing, setIsRefreshing] = useState(false)

  const timeRanges = [
    { id: '1', name: '今天' },
    { id: '7', name: '最近7天' },
    { id: '30', name: '最近30天' },
    { id: '90', name: '最近90天' },
  ]

  const accounts = [
    { id: 'all', name: '全部公众号' },
    { id: 'tech', name: '科技前沿' },
    { id: 'ai', name: 'AI观察' },
  ]

  const [overviewStats, setOverviewStats] = useState({
    totalReadCount: 125680,
    totalLikeCount: 3456,
    totalShareCount: 1234,
    avgReadCount: 2513,
    growthRate: {
      read: 15.3,
      like: 12.5,
      share: 8.7,
    },
  })

  const [trendData, setTrendData] = useState({
    dates: ['1/3', '1/4', '1/5', '1/6', '1/7', '1/8', '1/9'],
    readCounts: [18000, 22000, 19500, 24000, 21000, 20000, 25680],
  })

  const [topArticles, setTopArticles] = useState([
    {
      id: 1,
      title: 'GPT-4o发布：AI推理能力的新突破',
      readCount: 25680,
      likeCount: 890,
      shareCount: 320,
      publishedAt: '2026-01-09 10:00',
    },
    {
      id: 2,
      title: 'DeepSeek-V3：开源模型的新里程碑',
      readCount: 18450,
      likeCount: 654,
      shareCount: 210,
      publishedAt: '2026-01-09 09:30',
    },
    {
      id: 3,
      title: 'Claude 3.5 Sonnet：长文本处理的王者',
      readCount: 15230,
      likeCount: 520,
      shareCount: 180,
      publishedAt: '2026-01-08 15:00',
    },
    {
      id: 4,
      title: 'Gemini Pro：谷歌AI的最新答卷',
      readCount: 12890,
      likeCount: 450,
      shareCount: 150,
      publishedAt: '2026-01-08 10:00',
    },
    {
      id: 5,
      title: '2024年AI大模型发展报告',
      readCount: 10560,
      likeCount: 380,
      shareCount: 120,
      publishedAt: '2026-01-07 14:00',
    },
  ])

  const [insights, setInsights] = useState([
    { type: 'positive', text: '本周阅读量比上周增长 15.3%' },
    { type: 'positive', text: '平均点赞率为 2.8%，高于行业平均 2.5%' },
    { type: 'warning', text: '分享率为 1.0%，建议增加引导分享的CTA' },
    { type: 'info', text: '最佳发布时间为 10:00-11:00' },
  ])

  const handleRefresh = async () => {
    setIsRefreshing(true)
    // 模拟刷新
    await new Promise(resolve => setTimeout(resolve, 2000))
    setIsRefreshing(false)
  }

  const handleExport = () => {
    // 导出数据
    console.log('Export data')
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">数据统计</h1>
          <p className="text-muted-foreground mt-1">查看文章表现和数据趋势</p>
        </div>
        <div className="flex items-center gap-2">
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
          <button
            onClick={handleExport}
            className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
          >
            <Download size={20} />
            导出数据
          </button>
        </div>
      </div>

      {/* Filters - 横向标签栏 */}
      <div className="flex flex-wrap items-center gap-4 bg-white/50 backdrop-blur-sm rounded-2xl p-4 border border-gray-200">
        <div className="flex items-center gap-2">
          <Calendar size={20} className="text-muted-foreground" />
          <span className="text-sm font-medium">时间范围:</span>
          <div className="flex gap-2">
            {timeRanges.map((range) => (
              <button
                key={range.id}
                onClick={() => setSelectedDays(range.id)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-300 ${
                  selectedDays === range.id
                    ? 'bg-gradient-to-r from-[#5a6e5c] to-[#4a5e4c] text-white shadow-lg'
                    : 'bg-white hover:bg-gray-100 text-gray-700 border border-gray-200'
                }`}
              >
                {range.name}
              </button>
            ))}
          </div>
        </div>

        <div className="flex items-center gap-2 ml-4">
          <span className="text-sm font-medium">公众号:</span>
          <div className="flex gap-2">
            {accounts.map((account) => (
              <button
                key={account.id}
                onClick={() => setSelectedAccount(account.id)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-300 ${
                  selectedAccount === account.id
                    ? 'bg-gradient-to-r from-[#5a6e5c] to-[#4a5e4c] text-white shadow-lg'
                    : 'bg-white hover:bg-gray-100 text-gray-700 border border-gray-200'
                }`}
              >
                {account.name}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Overview Stats - 放大的数据卡片，低饱和度渐变色 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
        <OverviewStatCard
          title="总阅读量"
          value={overviewStats.totalReadCount.toLocaleString()}
          icon={<Eye size={28} />}
          growth={overviewStats.growthRate.read}
          gradient="from-blue-100 to-blue-50"
          iconColor="text-blue-600"
          iconBg="bg-blue-100"
        />
        <OverviewStatCard
          title="总点赞数"
          value={overviewStats.totalLikeCount.toLocaleString()}
          icon={<Heart size={28} />}
          growth={overviewStats.growthRate.like}
          gradient="from-green-100 to-green-50"
          iconColor="text-green-600"
          iconBg="bg-green-100"
        />
        <OverviewStatCard
          title="总分享数"
          value={overviewStats.totalShareCount.toLocaleString()}
          icon={<Share2 size={28} />}
          growth={overviewStats.growthRate.share}
          gradient="from-purple-100 to-purple-50"
          iconColor="text-purple-600"
          iconBg="bg-purple-100"
        />
        <OverviewStatCard
          title="平均阅读量"
          value={overviewStats.avgReadCount.toLocaleString()}
          icon={<BarChart3 size={28} />}
          growth={12.8}
          gradient="from-orange-100 to-orange-50"
          iconColor="text-orange-600"
          iconBg="bg-orange-100"
        />
      </div>

      {/* Trend Chart - 加浅灰色网格底和动态趋势线，亮色标注峰值点 */}
      <div className="bg-white/80 backdrop-blur-sm rounded-2xl border border-gray-200 p-6 shadow-sm">
        <h2 className="text-xl font-semibold mb-6">阅读量趋势</h2>
        <div className="h-80 relative">
          {/* 网格背景 */}
          <div className="absolute inset-0 grid grid-rows-4 gap-0 pointer-events-none">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="border-b border-gray-200/50" />
            ))}
          </div>
          
          {/* 图表内容 */}
          <div className="relative h-full flex items-end justify-between gap-4 px-2">
            {trendData.readCounts.map((count, index) => {
              const maxCount = Math.max(...trendData.readCounts)
              const height = (count / maxCount) * 100
              const isPeak = count === maxCount
              
              return (
                <div key={index} className="flex-1 flex flex-col items-center gap-2 relative">
                  {/* 峰值标注 */}
                  {isPeak && (
                    <div className="absolute -top-12 left-1/2 -translate-x-1/2 flex flex-col items-center gap-1 z-10">
                      <Sparkles size={16} className="text-yellow-500" />
                      <span className="text-xs font-bold text-yellow-600 bg-yellow-100 px-2 py-1 rounded-full">
                        峰值
                      </span>
                    </div>
                  )}
                  
                  {/* 柱状图 */}
                  <div className="w-full bg-gray-100 rounded-t-lg relative group" style={{ height: '100%' }}>
                    <div
                      className={`absolute bottom-0 left-0 right-0 rounded-t-lg transition-all duration-500 ease-out ${
                        isPeak 
                          ? 'bg-gradient-to-t from-[#5a6e5c] to-[#7a9e8c] shadow-lg shadow-[#5a6e5c]/30' 
                          : 'bg-gradient-to-t from-[#5a6e5c]/80 to-[#7a9e8c]/60'
                      } group-hover:shadow-lg group-hover:shadow-[#5a6e5c]/20`}
                      style={{ height: `${height}%` }}
                    />
                    {/* 悬浮提示 */}
                    <div className="absolute -top-10 left-1/2 -translate-x-1/2 px-3 py-1.5 rounded-lg bg-gray-900 text-white text-xs font-medium opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap shadow-lg">
                      {count.toLocaleString()}
                    </div>
                  </div>
                  <span className="text-xs text-gray-600 font-medium">{trendData.dates[index]}</span>
                </div>
              )
            })}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Articles */}
        <div className="bg-white/80 backdrop-blur-sm rounded-2xl border border-gray-200 p-6 shadow-sm">
          <h2 className="text-xl font-semibold mb-6">文章排行</h2>
          <div className="space-y-3">
            {topArticles.map((article, index) => (
              <div
                key={article.id}
                className="flex items-start gap-4 p-4 rounded-xl bg-gradient-to-r from-gray-50 to-white hover:from-blue-50 hover:to-blue-50/50 transition-all duration-300 border border-transparent hover:border-blue-200 cursor-pointer group"
              >
                <div className={`flex-shrink-0 w-10 h-10 rounded-xl flex items-center justify-center font-bold text-lg ${
                  index === 0 ? 'bg-gradient-to-br from-yellow-400 to-orange-400 text-white' :
                  index === 1 ? 'bg-gradient-to-br from-gray-300 to-gray-400 text-white' :
                  index === 2 ? 'bg-gradient-to-br from-orange-300 to-orange-400 text-white' :
                  'bg-gray-100 text-gray-600'
                }`}>
                  {index + 1}
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold mb-2 truncate group-hover:text-[#5a6e5c] transition-colors">{article.title}</h3>
                  <div className="flex items-center gap-4 text-sm">
                    <span className="flex items-center gap-1 text-gray-600">
                      <Eye size={14} className="text-blue-500" />
                      {article.readCount.toLocaleString()}
                    </span>
                    <span className="flex items-center gap-1 text-gray-600">
                      <Heart size={14} className="text-red-500" />
                      {article.likeCount}
                    </span>
                    <span className="flex items-center gap-1 text-gray-600">
                      <Share2 size={14} className="text-purple-500" />
                      {article.shareCount}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Insights */}
        <div className="bg-white/80 backdrop-blur-sm rounded-2xl border border-gray-200 p-6 shadow-sm">
          <h2 className="text-xl font-semibold mb-6">数据分析</h2>
          <div className="space-y-3">
            {insights.map((insight, index) => (
              <div
                key={index}
                className={`flex items-start gap-3 p-4 rounded-xl transition-all duration-300 ${
                  insight.type === 'positive' ? 'bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 hover:shadow-md hover:shadow-green-500/10' :
                  insight.type === 'warning' ? 'bg-gradient-to-r from-yellow-50 to-amber-50 border border-yellow-200 hover:shadow-md hover:shadow-yellow-500/10' :
                  'bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 hover:shadow-md hover:shadow-blue-500/10'
                }`}
              >
                <div className={`flex-shrink-0 mt-0.5 ${
                  insight.type === 'positive' ? 'text-green-600' :
                  insight.type === 'warning' ? 'text-yellow-600' :
                  'text-blue-600'
                }`}>
                  {insight.type === 'positive' ? <ArrowUp size={20} /> :
                   insight.type === 'warning' ? <TrendingUp size={20} /> :
                   <BarChart3 size={20} />}
                </div>
                <p className="text-sm font-medium text-gray-700">{insight.text}</p>
              </div>
            ))}
          </div>

          {/* Best Publish Time */}
          <div className="mt-6 p-5 rounded-xl bg-gradient-to-br from-[#5a6e5c]/10 to-[#4a5e4c]/10 border border-[#5a6e5c]/20">
            <div className="flex items-center justify-between mb-3">
              <span className="text-sm font-semibold text-gray-700">最佳发布时间</span>
              <Calendar size={16} className="text-[#5a6e5c]" />
            </div>
            <div className="text-2xl font-bold bg-gradient-to-r from-[#5a6e5c] to-[#4a5e4c] bg-clip-text text-transparent">10:00 - 11:00</div>
            <p className="text-xs text-gray-600 mt-1.5">
              基于历史数据分析，该时间段发布的文章平均阅读量最高
            </p>
          </div>
        </div>
      </div>

      {/* Detailed Metrics */}
      <div className="bg-white/80 backdrop-blur-sm rounded-2xl border border-gray-200 p-6 shadow-sm">
        <h2 className="text-xl font-semibold mb-6">详细指标</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="space-y-4">
            <h3 className="font-semibold text-sm text-gray-700 flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-blue-500" />
              互动率
            </h3>
            <div className="space-y-3">
              <MetricRow label="点赞率" value="2.8%" trend="+0.3%" />
              <MetricRow label="分享率" value="1.0%" trend="-0.1%" />
              <MetricRow label="收藏率" value="0.8%" trend="+0.2%" />
            </div>
          </div>
          <div className="space-y-4">
            <h3 className="font-semibold text-sm text-gray-700 flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-green-500" />
              内容表现
            </h3>
            <div className="space-y-3">
              <MetricRow label="平均阅读时长" value="2.5min" trend="+0.3min" />
              <MetricRow label="完读率" value="65%" trend="+5%" />
              <MetricRow label="跳出率" value="35%" trend="-3%" />
            </div>
          </div>
          <div className="space-y-4">
            <h3 className="font-semibold text-sm text-gray-700 flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-purple-500" />
              用户增长
            </h3>
            <div className="space-y-3">
              <MetricRow label="新增关注" value="1,234" trend="+156" />
              <MetricRow label="取关人数" value="45" trend="-12" />
              <MetricRow label="净增长" value="1,189" trend="+168" />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function OverviewStatCard({
  title,
  value,
  icon,
  growth,
  gradient,
  iconColor,
  iconBg,
}: {
  title: string
  value: string
  icon: React.ReactNode
  growth: number
  gradient: string
  iconColor: string
  iconBg: string
}) {
  const isPositive = growth >= 0

  return (
    <div className={`bg-gradient-to-br ${gradient} rounded-2xl p-6 border border-gray-200 shadow-sm hover:shadow-lg hover:shadow-gray-500/10 transition-all duration-300 hover:-translate-y-1`}>
      <div className="flex items-start justify-between mb-4">
        <div className={`p-3 rounded-xl ${iconBg} ${iconColor}`}>
          {icon}
        </div>
        <span className={`flex items-center gap-1 text-sm font-semibold px-2.5 py-1 rounded-full ${
          isPositive ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
        }`}>
          {isPositive ? <ArrowUp size={14} /> : <ArrowDown size={14} />}
          {Math.abs(growth)}%
        </span>
      </div>
      <p className="text-3xl font-bold mb-1 text-gray-900">{value}</p>
      <p className="text-sm font-medium text-gray-600">{title}</p>
    </div>
  )
}

function MetricRow({
  label,
  value,
  trend,
}: {
  label: string
  value: string
  trend: string
}) {
  const isPositive = trend.startsWith('+')

  return (
    <div className="flex items-center justify-between p-3 rounded-lg bg-gray-50 hover:bg-gray-100 transition-colors">
      <span className="text-sm font-medium text-gray-700">{label}</span>
      <div className="flex items-center gap-2">
        <span className="font-bold text-gray-900">{value}</span>
        <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${
          isPositive ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
        }`}>
          {trend}
        </span>
      </div>
    </div>
  )
}