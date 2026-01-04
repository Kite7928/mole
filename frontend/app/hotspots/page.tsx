'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Separator } from '@/components/ui/separator'
import {
  TrendingUp,
  RefreshCw,
  ArrowRight,
  Clock,
  Flame,
  Zap,
  Filter,
  Search,
  BookOpen,
} from 'lucide-react'
import { newsApi } from '@/lib/api'

export default function HotspotsPage() {
  const [activeTab, setActiveTab] = useState('all')
  const [loading, setLoading] = useState(false)
  const [hotNews, setHotNews] = useState<any[]>([])
  const [filteredNews, setFilteredNews] = useState<any[]>([])
  const [searchQuery, setSearchQuery] = useState('')

  useEffect(() => {
    fetchHotNews()
  }, [])

  useEffect(() => {
    filterNews()
  }, [hotNews, searchQuery, activeTab])

  const fetchHotNews = async () => {
    setLoading(true)
    try {
      const data = await newsApi.getHotNews(50)
      setHotNews(data)
    } catch (error) {
      console.error('Failed to fetch hot news:', error)
    } finally {
      setLoading(false)
    }
  }

  const filterNews = () => {
    let filtered = [...hotNews]

    // Filter by tab
    if (activeTab !== 'all') {
      filtered = filtered.filter((news) => news.source === activeTab)
    }

    // Filter by search
    if (searchQuery) {
      filtered = filtered.filter((news) =>
        news.title.toLowerCase().includes(searchQuery.toLowerCase())
      )
    }

    setFilteredNews(filtered)
  }

  const getSourceColor = (source: string) => {
    const colors: Record<string, string> = {
      'ITHOME': 'bg-blue-500',
      'KR36': 'bg-purple-500',
      'BAIDU': 'bg-red-500',
      'ZHIHU': 'bg-blue-600',
      'WEIBO': 'bg-orange-500',
    }
    return colors[source] || 'bg-gray-500'
  }

  const getHotScoreColor = (score: number) => {
    if (score >= 90) return 'text-red-500'
    if (score >= 70) return 'text-orange-500'
    if (score >= 50) return 'text-yellow-500'
    return 'text-gray-500'
  }

  const formatTime = (date: Date) => {
    const now = new Date()
    const diff = now.getTime() - new Date(date).getTime()
    const minutes = Math.floor(diff / 60000)
    const hours = Math.floor(diff / 3600000)
    const days = Math.floor(diff / 86400000)

    if (days > 0) return `${days}天前`
    if (hours > 0) return `${hours}小时前`
    if (minutes > 0) return `${minutes}分钟前`
    return '刚刚'
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary">
                <TrendingUp className="h-6 w-6 text-primary-foreground" />
              </div>
              <div>
                <h1 className="text-xl font-bold">热点监控</h1>
                <p className="text-sm text-muted-foreground">实时监控各大平台热点</p>
              </div>
            </div>
            <Button onClick={fetchHotNews} disabled={loading}>
              {loading ? (
                <>
                  <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                  刷新中
                </>
              ) : (
                <>
                  <RefreshCw className="mr-2 h-4 w-4" />
                  刷新
                </>
              )}
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-6">
        {/* Stats */}
        <div className="grid gap-4 md:grid-cols-4 mb-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">总热点数</CardTitle>
              <Flame className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{hotNews.length}</div>
              <p className="text-xs text-muted-foreground">实时更新</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">超热点</CardTitle>
              <Zap className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {hotNews.filter((n) => n.hot_score >= 90).length}
              </div>
              <p className="text-xs text-muted-foreground">热度 ≥ 90</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">IT之家</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {hotNews.filter((n) => n.source === 'ITHOME').length}
              </div>
              <p className="text-xs text-muted-foreground">科技热点</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">36氪</CardTitle>
              <BookOpen className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {hotNews.filter((n) => n.source === 'KR36').length}
              </div>
              <p className="text-xs text-muted-foreground">商业热点</p>
            </CardContent>
          </Card>
        </div>

        {/* Search and Filter */}
        <Card className="mb-6">
          <CardContent className="pt-6">
            <div className="flex items-center space-x-4">
              <div className="flex-1">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <input
                    type="text"
                    placeholder="搜索热点..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 bg-input border border-border rounded-md"
                  />
                </div>
              </div>
              <Button variant="outline">
                <Filter className="mr-2 h-4 w-4" />
                筛选
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Hot News List */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
          <TabsList className="grid w-full grid-cols-6">
            <TabsTrigger value="all">全部</TabsTrigger>
            <TabsTrigger value="ITHOME">IT之家</TabsTrigger>
            <TabsTrigger value="KR36">36氪</TabsTrigger>
            <TabsTrigger value="BAIDU">百度</TabsTrigger>
            <TabsTrigger value="ZHIHU">知乎</TabsTrigger>
            <TabsTrigger value="WEIBO">微博</TabsTrigger>
          </TabsList>

          <TabsContent value={activeTab} className="space-y-4">
            {loading && hotNews.length === 0 ? (
              <Card>
                <CardContent className="py-12">
                  <div className="text-center">
                    <RefreshCw className="mx-auto h-8 w-8 animate-spin text-muted-foreground mb-2" />
                    <p className="text-sm text-muted-foreground">正在加载热点...</p>
                  </div>
                </CardContent>
              </Card>
            ) : filteredNews.length === 0 ? (
              <Card>
                <CardContent className="py-12">
                  <div className="text-center">
                    <Search className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                    <h3 className="text-lg font-semibold mb-2">没有找到热点</h3>
                    <p className="text-muted-foreground">尝试调整搜索条件或刷新数据</p>
                  </div>
                </CardContent>
              </Card>
            ) : (
              <div className="space-y-3">
                {filteredNews.map((news, index) => (
                  <Card key={index} className="hover:border-primary transition-colors">
                    <CardContent className="p-4">
                      <div className="flex items-start justify-between">
                        <div className="flex-1 space-y-2">
                          <div className="flex items-start space-x-3">
                            <div className="flex-shrink-0">
                              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${getSourceColor(news.source)} text-white text-xs font-bold`}>
                                {index + 1}
                              </div>
                            </div>
                            <div className="flex-1">
                              <h3 className="font-medium leading-relaxed mb-2">{news.title}</h3>
                              {news.summary && (
                                <p className="text-sm text-muted-foreground line-clamp-2">{news.summary}</p>
                              )}
                              <div className="flex items-center space-x-3 mt-2">
                                <Badge variant="secondary" className="text-xs">
                                  {news.source_name}
                                </Badge>
                                {news.published_at && (
                                  <span className="text-xs text-muted-foreground flex items-center">
                                    <Clock className="h-3 w-3 mr-1" />
                                    {formatTime(news.published_at)}
                                  </span>
                                )}
                              </div>
                            </div>
                          </div>
                        </div>
                        <div className="flex flex-col items-end space-y-2 ml-4">
                          <div className={`text-2xl font-bold ${getHotScoreColor(news.hot_score)}`}>
                            {news.hot_score.toFixed(1)}
                          </div>
                          <span className="text-xs text-muted-foreground">热度</span>
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => window.open(news.url, '_blank')}
                          >
                            <ArrowRight className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </TabsContent>
        </Tabs>
      </main>
    </div>
  )
}