'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import {
  BookOpen,
  Eye,
  Heart,
  Share2,
  MessageCircle,
  TrendingUp,
  Calendar,
  BarChart3,
  PieChart as PieChartIcon,
} from 'lucide-react'

interface OverviewStats {
  total_articles: number
  published_articles: number
  total_reads: number
  total_likes: number
  total_shares: number
  total_comments: number
  avg_read_count: number
  success_rate: number
}

interface DailyStats {
  date: string
  articles: number
  reads: number
  likes: number
  shares: number
}

interface ArticleRanking {
  id: number
  title: string
  read_count: number
  like_count: number
  share_count: number
  comment_count: number
  published_at: string
}

interface SourceStats {
  source: string
  count: number
  percentage: number
}

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']

export default function StatisticsPage() {
  const [overview, setOverview] = useState<OverviewStats | null>(null)
  const [dailyStats, setDailyStats] = useState<DailyStats[]>([])
  const [topArticles, setTopArticles] = useState<ArticleRanking[]>([])
  const [sourceStats, setSourceStats] = useState<SourceStats[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchStatistics()
  }, [])

  const fetchStatistics = async () => {
    try {
      setLoading(true)

      // Fetch overview stats
      const overviewRes = await fetch('http://localhost:8000/api/statistics/overview')
      const overviewData = await overviewRes.json()
      setOverview(overviewData)

      // Fetch daily stats
      const dailyRes = await fetch('http://localhost:8000/api/statistics/daily?days=30')
      const dailyData = await dailyRes.json()
      setDailyStats(dailyData)

      // Fetch top articles
      const topRes = await fetch('http://localhost:8000/api/statistics/top-articles?limit=10')
      const topData = await topRes.json()
      setTopArticles(topData)

      // Fetch source stats
      const sourceRes = await fetch('http://localhost:8000/api/statistics/sources')
      const sourceData = await sourceRes.json()
      setSourceStats(sourceData)

    } catch (error) {
      console.error('Error fetching statistics:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <BarChart3 className="mx-auto h-12 w-12 text-muted-foreground animate-pulse mb-4" />
          <p className="text-muted-foreground">加载统计数据...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary">
                <BarChart3 className="h-6 w-6 text-primary-foreground" />
              </div>
              <div>
                <h1 className="text-xl font-bold">数据统计</h1>
                <p className="text-sm text-muted-foreground">文章效果分析</p>
              </div>
            </div>
            <Button onClick={fetchStatistics} variant="outline">
              <Calendar className="mr-2 h-4 w-4" />
              刷新数据
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-6">
        {/* Overview Stats */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mb-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">总文章数</CardTitle>
              <BookOpen className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{overview?.total_articles || 0}</div>
              <p className="text-xs text-muted-foreground">
                已发布 {overview?.published_articles || 0} 篇
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">总阅读量</CardTitle>
              <Eye className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{overview?.total_reads || 0}</div>
              <p className="text-xs text-muted-foreground">
                平均 {overview?.avg_read_count || 0} 阅读/篇
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">总互动数</CardTitle>
              <Heart className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {((overview?.total_likes || 0) + (overview?.total_shares || 0) + (overview?.total_comments || 0))}
              </div>
              <p className="text-xs text-muted-foreground">
                ❤️ {overview?.total_likes || 0} · 🔄 {overview?.total_shares || 0} · 💬 {overview?.total_comments || 0}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">成功率</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{overview?.success_rate || 0}%</div>
              <p className="text-xs text-muted-foreground">
                文章发布成功率
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Charts */}
        <div className="grid gap-4 md:grid-cols-2 mb-6">
          {/* Daily Trends */}
          <Card>
            <CardHeader>
              <CardTitle>每日趋势</CardTitle>
              <CardDescription>近30天文章发布和阅读趋势</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={dailyStats}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="articles" stroke="#3b82f6" name="文章数" />
                  <Line type="monotone" dataKey="reads" stroke="#10b981" name="阅读量" />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Source Distribution */}
          <Card>
            <CardHeader>
              <CardTitle>来源分布</CardTitle>
              <CardDescription>文章来源统计</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={sourceStats}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ source, percentage }) => `${source}: ${percentage}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="count"
                  >
                    {sourceStats.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>

        {/* Top Articles */}
        <Card>
          <CardHeader>
            <CardTitle>热门文章排行</CardTitle>
            <CardDescription>按阅读量排序的前10篇文章</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {topArticles.map((article, index) => (
                <div key={article.id} className="flex items-start justify-between space-x-4 p-3 rounded-lg hover:bg-muted/50 transition-colors">
                  <div className="flex-1 space-y-1">
                    <div className="flex items-center space-x-2">
                      <Badge variant="secondary">#{index + 1}</Badge>
                      <p className="text-sm font-medium leading-none">{article.title}</p>
                    </div>
                    <div className="flex items-center space-x-4 text-xs text-muted-foreground">
                      <span className="flex items-center">
                        <Eye className="mr-1 h-3 w-3" />
                        {article.read_count}
                      </span>
                      <span className="flex items-center">
                        <Heart className="mr-1 h-3 w-3" />
                        {article.like_count}
                      </span>
                      <span className="flex items-center">
                        <Share2 className="mr-1 h-3 w-3" />
                        {article.share_count}
                      </span>
                      <span className="flex items-center">
                        <MessageCircle className="mr-1 h-3 w-3" />
                        {article.comment_count}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  )
}