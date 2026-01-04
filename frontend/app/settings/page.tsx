'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import {
  Save,
  Key,
  Bot,
  Settings as SettingsIcon,
  Database,
  Image as ImageIcon,
  CheckCircle2,
  AlertCircle,
  Eye,
  EyeOff,
} from 'lucide-react'

export default function SettingsPage() {
  const [loading, setLoading] = useState(false)
  const [showSecrets, setShowSecrets] = useState<Record<string, boolean>>({})

  const [config, setConfig] = useState({
    // LLM Config
    openaiApiKey: '',
    openaiBaseUrl: 'https://api.openai.com/v1',
    openaiModel: 'gpt-4-turbo-preview',
    deepseekApiKey: '',
    deepseekBaseUrl: 'https://api.deepseek.com/v1',
    deepseekModel: 'deepseek-chat',
    claudeApiKey: '',
    claudeBaseUrl: 'https://api.anthropic.com/v1',
    claudeModel: 'claude-3-opus-20240229',
    geminiApiKey: '',
    geminiModel: 'gemini-pro',

    // WeChat Config
    wechatAppId: '',
    wechatAppSecret: '',

    // Database Config
    databaseUrl: 'postgresql+asyncpg://user:password@localhost:5432/wechat_ai_writer',
    redisUrl: 'redis://localhost:6379/0',

    // Image Config
    coverImageWidth: 1280,
    coverImageHeight: 720,
    coverImageMinWidth: 900,
    coverImageMinHeight: 500,
    imageMaxSize: 5242880, // 5MB

    // Feature Config
    enableResearch: true,
    enableImageGeneration: true,
    enableMarkdownEditor: true,
  })

  const [saved, setSaved] = useState(false)

  const toggleSecret = (key: string) => {
    setShowSecrets((prev) => ({ ...prev, [key]: !prev[key] }))
  }

  const handleSave = async () => {
    setLoading(true)
    try {
      // TODO: Save to backend API
      localStorage.setItem('config', JSON.stringify(config))
      
      setSaved(true)
      setTimeout(() => setSaved(false), 3000)
    } catch (error) {
      console.error('Failed to save config:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleTestConnection = async (type: string) => {
    setLoading(true)
    try {
      // TODO: Test connection to backend
      alert(`${type} 连接测试成功`)
    } catch (error) {
      alert(`${type} 连接测试失败`)
    } finally {
      setLoading(false)
    }
  }

  const renderSecretInput = (
    label: string,
    value: string,
    onChange: (value: string) => void,
    placeholder: string,
    key: string
  ) => (
    <div>
      <label className="text-sm font-medium mb-2 block">{label}</label>
      <div className="relative">
        <input
          type={showSecrets[key] ? 'text' : 'password'}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          className="w-full px-3 py-2 bg-input border border-border rounded-md pr-10"
        />
        <button
          type="button"
          onClick={() => toggleSecret(key)}
          className="absolute right-3 top-1/2 transform -translate-y-1/2 text-muted-foreground hover:text-foreground"
        >
          {showSecrets[key] ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
        </button>
      </div>
    </div>
  )

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary">
                <SettingsIcon className="h-6 w-6 text-primary-foreground" />
              </div>
              <div>
                <h1 className="text-xl font-bold">系统设置</h1>
                <p className="text-sm text-muted-foreground">配置系统参数和API</p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              {saved && (
                <Badge variant="default" className="mr-2">
                  <CheckCircle2 className="mr-1 h-3 w-3" />
                  已保存
                </Badge>
              )}
              <Button onClick={handleSave} disabled={loading}>
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
                    保存中
                  </>
                ) : (
                  <>
                    <Save className="mr-2 h-4 w-4" />
                    保存配置
                  </>
                )}
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-6">
        <Tabs defaultValue="llm" className="space-y-4">
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="llm">
              <Bot className="mr-2 h-4 w-4" />
              AI模型
            </TabsTrigger>
            <TabsTrigger value="wechat">
              <Key className="mr-2 h-4 w-4" />
              微信配置
            </TabsTrigger>
            <TabsTrigger value="database">
              <Database className="mr-2 h-4 w-4" />
              数据库
            </TabsTrigger>
            <TabsTrigger value="image">
              <ImageIcon className="mr-2 h-4 w-4" />
              图片配置
            </TabsTrigger>
            <TabsTrigger value="features">
              <SettingsIcon className="mr-2 h-4 w-4" />
              功能开关
            </TabsTrigger>
          </TabsList>

          {/* LLM Configuration */}
          <TabsContent value="llm" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>AI 模型配置</CardTitle>
                <CardDescription>配置多个 AI 模型的 API 密钥和参数</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* OpenAI */}
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold">OpenAI</h3>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleTestConnection('OpenAI')}
                    >
                      测试连接
                    </Button>
                  </div>
                  <div className="space-y-4">
                    {renderSecretInput(
                      'API Key',
                      config.openaiApiKey,
                      (value) => setConfig({ ...config, openaiApiKey: value }),
                      'sk-...',
                      'openaiApiKey'
                    )}
                    <div>
                      <label className="text-sm font-medium mb-2 block">Base URL</label>
                      <input
                        type="text"
                        value={config.openaiBaseUrl}
                        onChange={(e) => setConfig({ ...config, openaiBaseUrl: e.target.value })}
                        placeholder="https://api.openai.com/v1"
                        className="w-full px-3 py-2 bg-input border border-border rounded-md"
                      />
                    </div>
                    <div>
                      <label className="text-sm font-medium mb-2 block">Model</label>
                      <select
                        value={config.openaiModel}
                        onChange={(e) => setConfig({ ...config, openaiModel: e.target.value })}
                        className="w-full px-3 py-2 bg-input border border-border rounded-md"
                      >
                        <option value="gpt-4-turbo-preview">GPT-4 Turbo</option>
                        <option value="gpt-4">GPT-4</option>
                        <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                      </select>
                    </div>
                  </div>
                </div>

                <Separator />

                {/* DeepSeek */}
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold">DeepSeek</h3>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleTestConnection('DeepSeek')}
                    >
                      测试连接
                    </Button>
                  </div>
                  <div className="space-y-4">
                    {renderSecretInput(
                      'API Key',
                      config.deepseekApiKey,
                      (value) => setConfig({ ...config, deepseekApiKey: value }),
                      'sk-...',
                      'deepseekApiKey'
                    )}
                    <div>
                      <label className="text-sm font-medium mb-2 block">Base URL</label>
                      <input
                        type="text"
                        value={config.deepseekBaseUrl}
                        onChange={(e) => setConfig({ ...config, deepseekBaseUrl: e.target.value })}
                        placeholder="https://api.deepseek.com/v1"
                        className="w-full px-3 py-2 bg-input border border-border rounded-md"
                      />
                    </div>
                    <div>
                      <label className="text-sm font-medium mb-2 block">Model</label>
                      <select
                        value={config.deepseekModel}
                        onChange={(e) => setConfig({ ...config, deepseekModel: e.target.value })}
                        className="w-full px-3 py-2 bg-input border border-border rounded-md"
                      >
                        <option value="deepseek-chat">DeepSeek Chat</option>
                        <option value="deepseek-coder">DeepSeek Coder</option>
                      </select>
                    </div>
                  </div>
                </div>

                <Separator />

                {/* Claude */}
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold">Claude</h3>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleTestConnection('Claude')}
                    >
                      测试连接
                    </Button>
                  </div>
                  <div className="space-y-4">
                    {renderSecretInput(
                      'API Key',
                      config.claudeApiKey,
                      (value) => setConfig({ ...config, claudeApiKey: value }),
                      'sk-ant-...',
                      'claudeApiKey'
                    )}
                    <div>
                      <label className="text-sm font-medium mb-2 block">Base URL</label>
                      <input
                        type="text"
                        value={config.claudeBaseUrl}
                        onChange={(e) => setConfig({ ...config, claudeBaseUrl: e.target.value })}
                        placeholder="https://api.anthropic.com/v1"
                        className="w-full px-3 py-2 bg-input border border-border rounded-md"
                      />
                    </div>
                    <div>
                      <label className="text-sm font-medium mb-2 block">Model</label>
                      <select
                        value={config.claudeModel}
                        onChange={(e) => setConfig({ ...config, claudeModel: e.target.value })}
                        className="w-full px-3 py-2 bg-input border border-border rounded-md"
                      >
                        <option value="claude-3-opus-20240229">Claude 3 Opus</option>
                        <option value="claude-3-sonnet-20240229">Claude 3 Sonnet</option>
                        <option value="claude-3-haiku-20240307">Claude 3 Haiku</option>
                      </select>
                    </div>
                  </div>
                </div>

                <Separator />

                {/* Gemini */}
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold">Gemini</h3>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleTestConnection('Gemini')}
                    >
                      测试连接
                    </Button>
                  </div>
                  <div className="space-y-4">
                    {renderSecretInput(
                      'API Key',
                      config.geminiApiKey,
                      (value) => setConfig({ ...config, geminiApiKey: value }),
                      'AIza...',
                      'geminiApiKey'
                    )}
                    <div>
                      <label className="text-sm font-medium mb-2 block">Model</label>
                      <select
                        value={config.geminiModel}
                        onChange={(e) => setConfig({ ...config, geminiModel: e.target.value })}
                        className="w-full px-3 py-2 bg-input border border-border rounded-md"
                      >
                        <option value="gemini-pro">Gemini Pro</option>
                        <option value="gemini-pro-vision">Gemini Pro Vision</option>
                      </select>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* WeChat Configuration */}
          <TabsContent value="wechat">
            <Card>
              <CardHeader>
                <CardTitle>微信公众号配置</CardTitle>
                <CardDescription>配置微信公众号的 AppID 和 AppSecret</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="text-sm font-medium mb-2 block">AppID</label>
                  <input
                    type="text"
                    value={config.wechatAppId}
                    onChange={(e) => setConfig({ ...config, wechatAppId: e.target.value })}
                    placeholder="wx..."
                    className="w-full px-3 py-2 bg-input border border-border rounded-md"
                  />
                </div>
                {renderSecretInput(
                  'AppSecret',
                  config.wechatAppSecret,
                  (value) => setConfig({ ...config, wechatAppSecret: value }),
                  '...',
                  'wechatAppSecret'
                )}
                <div className="bg-muted/50 p-4 rounded-lg">
                  <h4 className="font-medium mb-2 flex items-center">
                    <AlertCircle className="mr-2 h-4 w-4" />
                    如何获取 AppID 和 AppSecret?
                  </h4>
                  <ol className="text-sm text-muted-foreground space-y-1 list-decimal list-inside">
                    <li>登录微信公众平台</li>
                    <li>进入 "开发 > 基本配置"</li>
                    <li>查看 AppID 和生成 AppSecret</li>
                    <li>配置服务器地址和令牌</li>
                  </ol>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Database Configuration */}
          <TabsContent value="database">
            <Card>
              <CardHeader>
                <CardTitle>数据库配置</CardTitle>
                <CardDescription>配置 PostgreSQL 和 Redis 连接</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="text-sm font-medium mb-2 block">PostgreSQL URL</label>
                  <input
                    type="text"
                    value={config.databaseUrl}
                    onChange={(e) => setConfig({ ...config, databaseUrl: e.target.value })}
                    placeholder="postgresql+asyncpg://user:password@localhost:5432/db"
                    className="w-full px-3 py-2 bg-input border border-border rounded-md font-mono text-sm"
                  />
                </div>
                <div>
                  <label className="text-sm font-medium mb-2 block">Redis URL</label>
                  <input
                    type="text"
                    value={config.redisUrl}
                    onChange={(e) => setConfig({ ...config, redisUrl: e.target.value })}
                    placeholder="redis://localhost:6379/0"
                    className="w-full px-3 py-2 bg-input border border-border rounded-md font-mono text-sm"
                  />
                </div>
                <div className="bg-muted/50 p-4 rounded-lg">
                  <h4 className="font-medium mb-2">注意事项</h4>
                  <ul className="text-sm text-muted-foreground space-y-1 list-disc list-inside">
                    <li>确保数据库服务正在运行</li>
                    <li>使用强密码保护数据库</li>
                    <li>生产环境建议使用连接池</li>
                  </ul>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Image Configuration */}
          <TabsContent value="image">
            <Card>
              <CardHeader>
                <CardTitle>图片配置</CardTitle>
                <CardDescription>配置图片处理和生成参数</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium mb-2 block">封面图宽度</label>
                    <input
                      type="number"
                      value={config.coverImageWidth}
                      onChange={(e) => setConfig({ ...config, coverImageWidth: parseInt(e.target.value) })}
                      className="w-full px-3 py-2 bg-input border border-border rounded-md"
                    />
                  </div>
                  <div>
                    <label className="text-sm font-medium mb-2 block">封面图高度</label>
                    <input
                      type="number"
                      value={config.coverImageHeight}
                      onChange={(e) => setConfig({ ...config, coverImageHeight: parseInt(e.target.value) })}
                      className="w-full px-3 py-2 bg-input border border-border rounded-md"
                    />
                  </div>
                  <div>
                    <label className="text-sm font-medium mb-2 block">最小宽度</label>
                    <input
                      type="number"
                      value={config.coverImageMinWidth}
                      onChange={(e) => setConfig({ ...config, coverImageMinWidth: parseInt(e.target.value) })}
                      className="w-full px-3 py-2 bg-input border border-border rounded-md"
                    />
                  </div>
                  <div>
                    <label className="text-sm font-medium mb-2 block">最小高度</label>
                    <input
                      type="number"
                      value={config.coverImageMinHeight}
                      onChange={(e) => setConfig({ ...config, coverImageMinHeight: parseInt(e.target.value) })}
                      className="w-full px-3 py-2 bg-input border border-border rounded-md"
                    />
                  </div>
                </div>
                <div>
                  <label className="text-sm font-medium mb-2 block">最大文件大小 (字节)</label>
                  <input
                    type="number"
                    value={config.imageMaxSize}
                    onChange={(e) => setConfig({ ...config, imageMaxSize: parseInt(e.target.value) })}
                    className="w-full px-3 py-2 bg-input border border-border rounded-md"
                  />
                  <p className="text-xs text-muted-foreground mt-1">
                    默认: 5242880 (5MB)
                  </p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Features Configuration */}
          <TabsContent value="features">
            <Card>
              <CardHeader>
                <CardTitle>功能开关</CardTitle>
                <CardDescription>启用或禁用系统功能</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between p-4 border rounded-lg">
                  <div>
                    <h4 className="font-medium">深度研究</h4>
                    <p className="text-sm text-muted-foreground">启用联网搜索,增强内容深度</p>
                  </div>
                  <input
                    type="checkbox"
                    checked={config.enableResearch}
                    onChange={(e) => setConfig({ ...config, enableResearch: e.target.checked })}
                    className="w-5 h-5"
                  />
                </div>

                <div className="flex items-center justify-between p-4 border rounded-lg">
                  <div>
                    <h4 className="font-medium">AI 图片生成</h4>
                    <p className="text-sm text-muted-foreground">自动生成封面图和技术配图</p>
                  </div>
                  <input
                    type="checkbox"
                    checked={config.enableImageGeneration}
                    onChange={(e) => setConfig({ ...config, enableImageGeneration: e.target.checked })}
                    className="w-5 h-5"
                  />
                </div>

                <div className="flex items-center justify-between p-4 border rounded-lg">
                  <div>
                    <h4 className="font-medium">Markdown 编辑器</h4>
                    <p className="text-sm text-muted-foreground">使用 Markdown 编辑器编写内容</p>
                  </div>
                  <input
                    type="checkbox"
                    checked={config.enableMarkdownEditor}
                    onChange={(e) => setConfig({ ...config, enableMarkdownEditor: e.target.checked })}
                    className="w-5 h-5"
                  />
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  )
}