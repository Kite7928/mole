'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Separator } from '@/components/ui/separator'
import {
  BookOpen,
  Zap,
  TrendingUp,
  Clock,
  CheckCircle2,
  AlertCircle,
  Settings,
  Plus,
  ArrowRight,
  Sparkles,
  BarChart3,
  Calendar,
  Users,
  Eye,
  Heart,
  Share2,
} from 'lucide-react'

export default function DashboardPage() {
  const [activeTab, setActiveTab] = useState('overview')

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary">
                <BookOpen className="h-6 w-6 text-primary-foreground" />
              </div>
              <div>
                <h1 className="text-xl font-bold">AI公众号自动写作助手 Pro</h1>
                <p className="text-sm text-muted-foreground">智能内容生成与发布系统</p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <Button variant="outline" size="sm" asChild>
                <a href="/settings">
                  <Settings className="mr-2 h-4 w-4" />
                  设置
                </a>
              </Button>
              <Button size="sm" asChild>
                <a href="/articles/create">
                  <Plus className="mr-2 h-4 w-4" />
                  新建文章
                </a>
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-6">
        {/* Quick Stats */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mb-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">今日发布</CardTitle>
              <BookOpen className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">24</div>
              <p className="text-xs text-muted-foreground">+12% 较昨日</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">总阅读量</CardTitle>
              <Eye className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">12.5K</div>
              <p className="text-xs text-muted-foreground">+8% 较昨日</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">收藏数</CardTitle>
              <Heart className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">890</div>
              <p className="text-xs text-muted-foreground">+15% 较昨日</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">成功率</CardTitle>
              <CheckCircle2 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">95%</div>
              <p className="text-xs text-muted-foreground">稳定运行</p>
            </CardContent>
          </Card>
        </div>

        {/* Main Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="overview">仪表板</TabsTrigger>
            <TabsTrigger value="articles">文章</TabsTrigger>
            <TabsTrigger value="hotspots" asChild>
                <a href="/hotspots">热点</a>
              </TabsTrigger>
            <TabsTrigger value="statistics">统计</TabsTrigger>
            <TabsTrigger value="settings" asChild>
                <a href="/settings">设置</a>
              </TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2">
              {/* Quick Actions */}
              <Card>
                <CardHeader>
                  <CardTitle>快速操作</CardTitle>
                  <CardDescription>常用功能快捷入口</CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  <Button className="w-full justify-start" variant="default" asChild>
                    <a href="/articles/create">
                      <Zap className="mr-2 h-4 w-4" />
                      一键生成文章
                    </a>
                  </Button>
                  <Button className="w-full justify-start" variant="outline" asChild>
                    <a href="/hotspots">
                      <TrendingUp className="mr-2 h-4 w-4" />
                      查看热点趋势
                    </a>
                  </Button>
                  <Button className="w-full justify-start" variant="outline">
                    <Calendar className="mr-2 h-4 w-4" />
                    定时任务管理
                  </Button>
                  <Button className="w-full justify-start" variant="outline" asChild>
                    <a href="/statistics">
                      <BarChart3 className="mr-2 h-4 w-4" />
                      数据统计分析
                    </a>
                  </Button>
                </CardContent>
              </Card>

              {/* Real-time Tasks */}
              <Card>
                <CardHeader>
                  <CardTitle>实时任务</CardTitle>
                  <CardDescription>正在进行的任务</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="flex items-center">
                        <Sparkles className="mr-2 h-4 w-4 text-primary" />
                        正在生成文章
                      </span>
                      <span className="text-muted-foreground">45%</span>
                    </div>
                    <Progress value={45} />
                  </div>

                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="flex items-center">
                        <Eye className="mr-2 h-4 w-4 text-blue-500" />
                        上传封面图
                      </span>
                      <span className="text-muted-foreground">78%</span>
                    </div>
                    <Progress value={78} />
                  </div>

                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="flex items-center">
                        <Clock className="mr-2 h-4 w-4 text-orange-500" />
                        待发布任务
                      </span>
                      <Badge variant="secondary">3篇</Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Hot Topics */}
            <Card>
              <CardHeader>
                <CardTitle>最新热点</CardTitle>
                <CardDescription>实时更新的AI科技热点</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {[
                    {
                      title: '研究发现：YouTube向新用户展示的视频中超20%是"AI垃圾内容"',
                      source: 'IT之家',
                      time: '10分钟前',
                      hot: 9.8
                    },
                    {
                      title: '马斯克预测：AI和机器人将彻底消除贫困与饥饿',
                      source: '36氪',
                      time: '25分钟前',
                      hot: 8.5
                    },
                    {
                      title: '苹果Vision Pro降价30%，销量激增',
                      source: 'IT之家',
                      time: '1小时前',
                      hot: 7.2
                    },
                  ].map((item, index) => (
                    <div key={index} className="flex items-start justify-between space-x-4 p-3 rounded-lg hover:bg-muted/50 transition-colors">
                      <div className="flex-1 space-y-1">
                        <p className="text-sm font-medium leading-none">{item.title}</p>
                        <div className="flex items-center space-x-2 text-xs text-muted-foreground">
                          <span>{item.source}</span>
                          <span>•</span>
                          <span>{item.time}</span>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge variant="secondary">热度 {item.hot}</Badge>
                        <Button size="sm" variant="ghost" asChild>
                          <a href="/hotspots">
                            <ArrowRight className="h-4 w-4" />
                          </a>
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Articles Tab */}
          <TabsContent value="articles">
            <Card>
              <CardHeader>
                <CardTitle>文章管理</CardTitle>
                <CardDescription>管理和查看所有生成的文章</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center py-12">
                  <BookOpen className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                  <h3 className="text-lg font-semibold mb-2">暂无文章</h3>
                  <p className="text-muted-foreground mb-4">开始创建你的第一篇文章吧</p>
                  <Button asChild>
                    <a href="/articles/create">
                      <Plus className="mr-2 h-4 w-4" />
                      创建文章
                    </a>
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Hotspots Tab */}
          <TabsContent value="hotspots">
            <Card>
              <CardHeader>
                <CardTitle>热点监控</CardTitle>
                <CardDescription>实时监控各大平台热点</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center py-12">
                  <TrendingUp className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                  <h3 className="text-lg font-semibold mb-2">热点加载中</h3>
                  <p className="text-muted-foreground mb-4">正在获取最新热点信息...</p>
                  <Button asChild>
                    <a href="/hotspots">
                      <TrendingUp className="mr-2 h-4 w-4" />
                      查看所有热点
                    </a>
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Statistics Tab */}
          <TabsContent value="statistics">
            <Card>
              <CardHeader>
                <CardTitle>数据统计</CardTitle>
                <CardDescription>查看详细的数据分析</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center py-12">
                  <BarChart3 className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                  <h3 className="text-lg font-semibold mb-2">统计数据</h3>
                  <p className="text-muted-foreground">数据统计功能即将上线</p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Settings Tab */}
          <TabsContent value="settings">
            <Card>
              <CardHeader>
                <CardTitle>系统设置</CardTitle>
                <CardDescription>配置系统参数和API</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center py-12">
                  <Settings className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                  <h3 className="text-lg font-semibold mb-2">系统设置</h3>
                  <p className="text-muted-foreground mb-4">配置 AI 模型、微信公众号等参数</p>
                  <Button asChild>
                    <a href="/settings">
                      <Settings className="mr-2 h-4 w-4" />
                      打开设置页面
                    </a>
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  )
}