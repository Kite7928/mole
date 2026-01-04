'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Separator } from '@/components/ui/separator'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  ArrowLeft,
  Sparkles,
  Image as ImageIcon,
  Send,
  CheckCircle2,
  Loader2,
  Settings,
  BookOpen,
  Zap,
  TrendingUp,
} from 'lucide-react'
import { articlesApi, newsApi, wechatApi } from '@/lib/api'

export default function CreateArticlePage() {
  const router = useRouter()
  const [step, setStep] = useState<'topic' | 'title' | 'content' | 'images' | 'preview'>('topic')
  const [loading, setLoading] = useState(false)
  const [progress, setProgress] = useState(0)

  // Article data
  const [topic, setTopic] = useState('')
  const [source, setSource] = useState<'manual' | 'hot'>('manual')
  const [hotNews, setHotNews] = useState<any[]>([])
  const [selectedNews, setSelectedNews] = useState<any>(null)
  
  const [titles, setTitles] = useState<any[]>([])
  const [selectedTitle, setSelectedTitle] = useState('')
  
  const [content, setContent] = useState<any>(null)
  const [coverImage, setCoverImage] = useState<string>('')
  
  const [config, setConfig] = useState({
    style: 'professional',
    length: 'medium',
    enableResearch: false,
    generateCover: true,
    aiModel: '',
  })

  const fetchHotNews = async () => {
    setLoading(true)
    try {
      const data = await newsApi.getHotNews(10)
      setHotNews(data)
    } catch (error) {
      console.error('Failed to fetch hot news:', error)
    } finally {
      setLoading(false)
    }
  }

  const selectHotNews = (news: any) => {
    setSelectedNews(news)
    setTopic(news.title)
  }

  const generateTitles = async () => {
    setLoading(true)
    setProgress(10)
    try {
      const data = await articlesApi.generateTitles(topic, 5, config.aiModel)
      setTitles(data)
      setProgress(30)
    } catch (error) {
      console.error('Failed to generate titles:', error)
    } finally {
      setLoading(false)
    }
  }

  const generateContent = async () => {
    setLoading(true)
    setProgress(40)
    try {
      const data = await articlesApi.generateContent({
        topic,
        title: selectedTitle,
        style: config.style,
        length: config.length,
        enable_research: config.enableResearch,
        ai_model: config.aiModel,
      })
      setContent(data)
      setProgress(70)
      
      // Generate cover image
      if (config.generateCover) {
        const keywords = topic.slice(0, 50)
        setCoverImage(`https://image.pollinations.ai/prompt/${keywords}?width=1280&height=720&nologo=true`)
      }
      setProgress(80)
    } catch (error) {
      console.error('Failed to generate content:', error)
    } finally {
      setLoading(false)
    }
  }

  const createAndPublish = async () => {
    setLoading(true)
    setProgress(90)
    try {
      // Create article
      const article = await articlesApi.createArticle({
        topic,
        title: selectedTitle,
        source: source,
        style: config.style,
        length: config.length,
        enable_research: config.enableResearch,
        generate_cover: config.generateCover,
        ai_model: config.aiModel,
      })

      // Publish to WeChat
      const wechatData = await wechatApi.createDraft([{
        title: selectedTitle,
        author: 'AI Writer',
        digest: content?.summary,
        content: content?.content,
        thumb_media_id: coverImage,
      }])

      setProgress(100)
      
      setTimeout(() => {
        alert(`文章创建成功！草稿 ID: ${wechatData.media_id}`)
        router.push('/')
      }, 500)
    } catch (error) {
      console.error('Failed to create and publish:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleNext = async () => {
    setLoading(true)
    
    switch (step) {
      case 'topic':
        await generateTitles()
        setStep('title')
        break
      case 'title':
        if (!selectedTitle) {
          alert('请选择一个标题')
        } else {
          await generateContent()
          setStep('content')
        }
        break
      case 'content':
        setStep('images')
        break
      case 'images':
        await createAndPublish()
        break
    }
    
    setLoading(false)
  }

  const handleBack = () => {
    switch (step) {
      case 'title':
        setStep('topic')
        break
      case 'content':
        setStep('title')
        break
      case 'images':
        setStep('content')
        break
    }
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Button variant="ghost" size="sm" onClick={() => router.push('/')}>
                <ArrowLeft className="h-4 w-4" />
              </Button>
              <div>
                <h1 className="text-xl font-bold">创建文章</h1>
                <p className="text-sm text-muted-foreground">AI 智能写作助手</p>
              </div>
            </div>
            <Button variant="outline" size="sm">
              <Settings className="mr-2 h-4 w-4" />
              配置
            </Button>
          </div>
        </div>
      </header>

      {/* Progress */}
      <div className="border-b border-border">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step === 'topic' || step === 'title' || step === 'content' || step === 'images' ? 'bg-primary' : 'bg-muted'}`}>
                {step === 'topic' || step === 'title' || step === 'content' || step === 'images' ? <CheckCircle2 className="h-4 w-4 text-primary-foreground" /> : '1'}
              </div>
              <div className={`w-16 h-1 ${step === 'title' || step === 'content' || step === 'images' ? 'bg-primary' : 'bg-muted'}`} />
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step === 'title' || step === 'content' || step === 'images' ? 'bg-primary' : 'bg-muted'}`}>
                {step === 'title' || step === 'content' || step === 'images' ? <CheckCircle2 className="h-4 w-4 text-primary-foreground" /> : '2'}
              </div>
              <div className={`w-16 h-1 ${step === 'content' || step === 'images' ? 'bg-primary' : 'bg-muted'}`} />
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step === 'content' || step === 'images' ? 'bg-primary' : 'bg-muted'}`}>
                {step === 'content' || step === 'images' ? <CheckCircle2 className="h-4 w-4 text-primary-foreground" /> : '3'}
              </div>
              <div className={`w-16 h-1 ${step === 'images' ? 'bg-primary' : 'bg-muted'}`} />
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step === 'images' ? 'bg-primary' : 'bg-muted'}`}>
                {step === 'images' ? <CheckCircle2 className="h-4 w-4 text-primary-foreground" /> : '4'}
              </div>
            </div>
            {loading && <span className="text-sm text-muted-foreground">处理中... {progress}%</span>}
          </div>
          {loading && <Progress value={progress} />}
        </div>
      </div>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-6">
        <div className="grid gap-6 lg:grid-cols-3">
          {/* Left Panel - Steps */}
          <div className="lg:col-span-2">
            {step === 'topic' && (
              <Card>
                <CardHeader>
                  <CardTitle>步骤 1: 选择主题</CardTitle>
                  <CardDescription>选择文章主题或从热点中选择</CardDescription>
                </CardHeader>
                <CardContent>
                  <Tabs defaultValue="manual">
                    <TabsList className="grid w-full grid-cols-2">
                      <TabsTrigger value="manual" onClick={() => setSource('manual')}>
                        <BookOpen className="mr-2 h-4 w-4" />
                        手动输入
                      </TabsTrigger>
                      <TabsTrigger value="hot" onClick={() => { setSource('hot'); fetchHotNews() }}>
                        <TrendingUp className="mr-2 h-4 w-4" />
                        热点选择
                      </TabsTrigger>
                    </TabsList>

                    <TabsContent value="manual" className="space-y-4">
                      <div>
                        <label className="text-sm font-medium mb-2 block">文章主题</label>
                        <textarea
                          value={topic}
                          onChange={(e) => setTopic(e.target.value)}
                          placeholder="输入你想写的文章主题..."
                          className="w-full px-3 py-2 bg-input border border-border rounded-md min-h-[100px]"
                        />
                      </div>
                    </TabsContent>

                    <TabsContent value="hot" className="space-y-4">
                      {loading && hotNews.length === 0 ? (
                        <div className="text-center py-8">
                          <Loader2 className="mx-auto h-8 w-8 animate-spin text-muted-foreground mb-2" />
                          <p className="text-sm text-muted-foreground">正在加载热点...</p>
                        </div>
                      ) : (
                        <div className="space-y-3 max-h-[400px] overflow-y-auto">
                          {hotNews.map((news, index) => (
                            <div
                              key={index}
                              className={`p-4 rounded-lg border cursor-pointer transition-colors ${
                                selectedNews?.id === news.id ? 'border-primary bg-primary/10' : 'border-border hover:bg-muted/50'
                              }`}
                              onClick={() => selectHotNews(news)}
                            >
                              <div className="flex items-start justify-between">
                                <div className="flex-1">
                                  <h4 className="text-sm font-medium mb-1">{news.title}</h4>
                                  <div className="flex items-center space-x-2 text-xs text-muted-foreground">
                                    <span>{news.source_name}</span>
                                    <span>•</span>
                                    <Badge variant="secondary">热度 {news.hot_score.toFixed(1)}</Badge>
                                  </div>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </TabsContent>
                  </Tabs>

                  <div className="mt-6 space-y-4">
                    <Separator />
                    <div>
                      <label className="text-sm font-medium mb-2 block">写作风格</label>
                      <select
                        value={config.style}
                        onChange={(e) => setConfig({ ...config, style: e.target.value })}
                        className="w-full px-3 py-2 bg-input border border-border rounded-md"
                      >
                        <option value="professional">专业严谨</option>
                        <option value="casual">轻松幽默</option>
                        <option value="emotional">情感共鸣</option>
                        <option value="technical">技术分析</option>
                      </select>
                    </div>

                    <div>
                      <label className="text-sm font-medium mb-2 block">文章长度</label>
                      <select
                        value={config.length}
                        onChange={(e) => setConfig({ ...config, length: e.target.value })}
                        className="w-full px-3 py-2 bg-input border border-border rounded-md"
                      >
                        <option value="short">短篇 (800-1200字)</option>
                        <option value="medium">中篇 (1500-2500字)</option>
                        <option value="long">长篇 (3000-5000字)</option>
                      </select>
                    </div>

                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">深度研究</span>
                      <input
                        type="checkbox"
                        checked={config.enableResearch}
                        onChange={(e) => setConfig({ ...config, enableResearch: e.target.checked })}
                        className="w-4 h-4"
                      />
                    </div>

                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">生成封面图</span>
                      <input
                        type="checkbox"
                        checked={config.generateCover}
                        onChange={(e) => setConfig({ ...config, generateCover: e.target.checked })}
                        className="w-4 h-4"
                      />
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {step === 'title' && (
              <Card>
                <CardHeader>
                  <CardTitle>步骤 2: 选择标题</CardTitle>
                  <CardDescription>AI 为你生成了多个标题,选择一个最合适的</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {titles.map((item, index) => (
                      <div
                        key={index}
                        className={`p-4 rounded-lg border cursor-pointer transition-colors ${
                          selectedTitle === item.title ? 'border-primary bg-primary/10' : 'border-border hover:bg-muted/50'
                        }`}
                        onClick={() => setSelectedTitle(item.title)}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <h4 className="font-medium mb-2">{item.title}</h4>
                            <div className="flex items-center space-x-2">
                              <Badge variant="secondary">点击率 {Math.round(item.predicted_click_rate * 100)}%</Badge>
                              <Badge variant="outline">{item.emotion}</Badge>
                            </div>
                          </div>
                          {selectedTitle === item.title && (
                            <CheckCircle2 className="h-5 w-5 text-primary" />
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {step === 'content' && (
              <Card>
                <CardHeader>
                  <CardTitle>步骤 3: 文章内容</CardTitle>
                  <CardDescription>AI 生成的文章内容,你可以进行编辑</CardDescription>
                </CardHeader>
                <CardContent>
                  {content && (
                    <div className="space-y-4">
                      <div>
                        <h3 className="text-lg font-bold mb-2">{selectedTitle}</h3>
                        <p className="text-sm text-muted-foreground mb-4">{content.summary}</p>
                      </div>

                      <Separator />

                      <div>
                        <label className="text-sm font-medium mb-2 block">文章正文</label>
                        <textarea
                          value={content.content}
                          onChange={(e) => setContent({ ...content, content: e.target.value })}
                          className="w-full px-3 py-2 bg-input border border-border rounded-md min-h-[400px] font-mono text-sm"
                        />
                      </div>

                      <div className="flex items-center space-x-2">
                        <Badge variant="outline">质量评分: {Math.round((content.quality_score || 0) * 100)}%</Badge>
                        {content.tags && content.tags.map((tag: string, index: number) => (
                          <Badge key={index} variant="secondary">{tag}</Badge>
                        ))}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}

            {step === 'images' && (
              <Card>
                <CardHeader>
                  <CardTitle>步骤 4: 图片预览</CardTitle>
                  <CardDescription>封面图和配图预览</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {coverImage && (
                      <div>
                        <label className="text-sm font-medium mb-2 block">封面图</label>
                        <img
                          src={coverImage}
                          alt="封面图"
                          className="w-full rounded-lg border border-border"
                        />
                      </div>
                    )}

                    <div className="bg-muted/50 p-4 rounded-lg">
                      <h4 className="font-medium mb-2">文章信息</h4>
                      <div className="space-y-1 text-sm">
                        <p><span className="text-muted-foreground">标题:</span> {selectedTitle}</p>
                        <p><span className="text-muted-foreground">主题:</span> {topic}</p>
                        <p><span className="text-muted-foreground">字数:</span> {content?.content?.length || 0} 字</p>
                        <p><span className="text-muted-foreground">标签:</span> {content?.tags?.join(', ') || '无'}</p>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Right Panel - Actions */}
          <div className="lg:col-span-1">
            <Card>
              <CardHeader>
                <CardTitle>操作</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {step !== 'topic' && (
                  <Button
                    variant="outline"
                    className="w-full"
                    onClick={handleBack}
                    disabled={loading}
                  >
                    上一步
                  </Button>
                )}

                {step === 'topic' && (
                  <Button
                    className="w-full"
                    onClick={handleNext}
                    disabled={!topic || loading}
                  >
                    {loading ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        生成标题
                      </>
                    ) : (
                      <>
                        <Sparkles className="mr-2 h-4 w-4" />
                        生成标题
                      </>
                    )}
                  </Button>
                )}

                {step === 'title' && (
                  <Button
                    className="w-full"
                    onClick={handleNext}
                    disabled={!selectedTitle || loading}
                  >
                    {loading ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        生成内容
                      </>
                    ) : (
                      <>
                        <BookOpen className="mr-2 h-4 w-4" />
                        生成内容
                      </>
                    )}
                  </Button>
                )}

                {step === 'content' && (
                  <Button
                    className="w-full"
                    onClick={handleNext}
                    disabled={loading}
                  >
                    <ImageIcon className="mr-2 h-4 w-4" />
                    下一步
                  </Button>
                )}

                {step === 'images' && (
                  <Button
                    className="w-full"
                    onClick={handleNext}
                    disabled={loading}
                  >
                    {loading ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        创建并发布
                      </>
                    ) : (
                      <>
                        <Send className="mr-2 h-4 w-4" />
                        创建并发布
                      </>
                    )}
                  </Button>
                )}

                <Separator />

                <div className="space-y-2">
                  <h4 className="text-sm font-medium">当前配置</h4>
                  <div className="text-xs text-muted-foreground space-y-1">
                    <p>风格: {config.style}</p>
                    <p>长度: {config.length}</p>
                    <p>深度研究: {config.enableResearch ? '开启' : '关闭'}</p>
                    <p>生成封面: {config.generateCover ? '开启' : '关闭'}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  )
}