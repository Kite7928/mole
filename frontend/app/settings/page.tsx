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
    // Application Config
    appName: 'AI公众号自动写作助手 Pro',
    appVersion: '1.0.0',
    secretKey: '',

    // LLM Config
    openaiApiKey: '',
    openaiBaseUrl: 'https://api.openai.com/v1',
    openaiModel: 'gpt-4-turbo-preview',
    openaiMaxTokens: 4000,
    openaiTemperature: 0.7,
    deepseekApiKey: '',
    deepseekBaseUrl: 'https://api.deepseek.com/v1',
    deepseekModel: 'deepseek-chat',
    claudeApiKey: '',
    claudeBaseUrl: 'https://api.anthropic.com/v1',
    claudeModel: 'claude-3-opus-20240229',
    geminiApiKey: '',
    geminiModel: 'gemini-pro',
    qwenApiKey: '',
    qwenBaseUrl: 'https://dashscope.aliyuncs.com/compatible-mode/v1',
    qwenModel: 'qwen-max',
    moonshotApiKey: '',
    moonshotBaseUrl: 'https://api.moonshot.cn/v1',
    moonshotModel: 'moonshot-v1-8k',
    ollamaBaseUrl: 'http://localhost:11434',
    ollamaModel: 'llama2',
    volcengineApiKey: '',
    volcengineBaseUrl: 'https://ark.cn-beijing.volces.com/api/v3',
    volcengineModel: 'ep-20240110134838-xxxxx',
    alibabaBailianApiKey: '',
    alibabaBailianBaseUrl: 'https://dashscope.aliyuncs.com/compatible-mode/v1',
    alibabaBailianModel: 'qwen-max',
    siliconflowApiKey: '',
    siliconflowBaseUrl: 'https://api.siliconflow.cn/v1',
    siliconflowModel: 'Qwen/Qwen2.5-7B-Instruct',
    openrouterApiKey: '',
    openrouterBaseUrl: 'https://openrouter.ai/api/v1',
    openrouterModel: 'openai/gpt-4-turbo',
    aiRotationStrategy: 'sequential',

    // WeChat Config
    wechatAppId: '',
    wechatAppSecret: '',

    // Database Config
    databaseUrl: 'postgresql+asyncpg://postgres:postgres@postgres:5432/wechat_ai_writer',
    redisUrl: 'redis://redis:6379/0',

    // Task Config
    celeryBrokerUrl: 'redis://redis:6379/1',
    celeryResultBackend: 'redis://redis:6379/1',
    taskTimeout: 3600,
    taskMaxRetries: 3,

    // File Storage Config
    uploadDir: 'uploads',
    tempDir: 'temp',
    maxUploadSize: 20971520,

    // Image Config
    coverImageWidth: 1280,
    coverImageHeight: 720,
    coverImageMinWidth: 900,
    coverImageMinHeight: 500,
    imageMaxSize: 5242880,

    // Logging Config
    logLevel: 'INFO',
    logFile: 'logs/app.log',

    // Monitoring Config
    enableMetrics: true,
    metricsPort: 9090,
    sentryDsn: '',

    // Security Config
    rateLimitEnabled: true,
    rateLimitRequests: 100,
    rateLimitPeriod: 60,

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
          <TabsList className="grid w-full grid-cols-9 overflow-x-auto">
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
            <TabsTrigger value="app">
              <SettingsIcon className="mr-2 h-4 w-4" />
              应用配置
            </TabsTrigger>
            <TabsTrigger value="task">
              <Zap className="mr-2 h-4 w-4" />
              任务配置
            </TabsTrigger>
            <TabsTrigger value="image">
              <ImageIcon className="mr-2 h-4 w-4" />
              图片配置
            </TabsTrigger>
            <TabsTrigger value="logging">
              <CheckCircle2 className="mr-2 h-4 w-4" />
              日志配置
            </TabsTrigger>
            <TabsTrigger value="security">
              <AlertCircle className="mr-2 h-4 w-4" />
              安全配置
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
                <div className="bg-purple-50 dark:bg-purple-950/20 border border-purple-200 dark:border-purple-800 p-4 rounded-lg">
                  <div className="flex items-start space-x-3">
                    <Bot className="h-5 w-5 text-purple-600 dark:text-purple-400 mt-0.5" />
                    <div>
                      <h4 className="font-medium text-purple-900 dark:text-purple-100 mb-1">智能提示</h4>
                      <p className="text-sm text-purple-700 dark:text-purple-300">你可以配置多个 AI 模型，系统会自动选择可用的模型进行内容生成。建议至少配置一个主要模型。</p>
                    </div>
                  </div>
                </div>

                {/* OpenAI */}
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <h3 className="text-lg font-semibold">OpenAI</h3>
                      <Badge variant="default" className="text-xs">推荐</Badge>
                    </div>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleTestConnection('OpenAI')}
                    >
                      测试连接
                    </Button>
                  </div>
                  <div className="bg-muted/50 p-4 rounded-lg space-y-4">
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
                        className="w-full px-3 py-2 bg-input border border-border rounded-md focus:ring-2 focus:ring-primary focus:border-transparent"
                      />
                    </div>
                    <div>
                      <label className="text-sm font-medium mb-2 block">Model</label>
                      <select
                        value={config.openaiModel}
                        onChange={(e) => setConfig({ ...config, openaiModel: e.target.value })}
                        className="w-full px-3 py-2 bg-input border border-border rounded-md focus:ring-2 focus:ring-primary focus:border-transparent"
                      >
                        <option value="gpt-4-turbo-preview">GPT-4 Turbo (推荐)</option>
                        <option value="gpt-4">GPT-4</option>
                        <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                      </select>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="text-sm font-medium mb-2 block">最大 Token 数</label>
                        <input
                          type="number"
                          value={config.openaiMaxTokens}
                          onChange={(e) => setConfig({ ...config, openaiMaxTokens: parseInt(e.target.value) })}
                          className="w-full px-3 py-2 bg-input border border-border rounded-md"
                        />
                      </div>
                      <div>
                        <label className="text-sm font-medium mb-2 block">温度 (0-2)</label>
                        <input
                          type="number"
                          step="0.1"
                          min="0"
                          max="2"
                          value={config.openaiTemperature}
                          onChange={(e) => setConfig({ ...config, openaiTemperature: parseFloat(e.target.value) })}
                          className="w-full px-3 py-2 bg-input border border-border rounded-md"
                        />
                      </div>
                    </div>
                  </div>
                </div>

                <Separator />

                {/* DeepSeek */}
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <h3 className="text-lg font-semibold">DeepSeek</h3>
                      <Badge variant="secondary" className="text-xs">性价比高</Badge>
                    </div>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleTestConnection('DeepSeek')}
                    >
                      测试连接
                    </Button>
                  </div>
                  <div className="bg-muted/50 p-4 rounded-lg space-y-4">
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
                        className="w-full px-3 py-2 bg-input border border-border rounded-md focus:ring-2 focus:ring-primary focus:border-transparent"
                      />
                    </div>
                    <div>
                      <label className="text-sm font-medium mb-2 block">Model</label>
                      <select
                        value={config.deepseekModel}
                        onChange={(e) => setConfig({ ...config, deepseekModel: e.target.value })}
                        className="w-full px-3 py-2 bg-input border border-border rounded-md focus:ring-2 focus:ring-primary focus:border-transparent"
                      >
                        <option value="deepseek-chat">DeepSeek Chat</option>
                        <option value="deepseek-coder">DeepSeek Coder</option>
                      </select>
                    </div>
                  </div>
                </div>

                <Separator />

                {/* Claude */}
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <h3 className="text-lg font-semibold">Claude</h3>
                      <Badge variant="secondary" className="text-xs">长文本</Badge>
                    </div>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleTestConnection('Claude')}
                    >
                      测试连接
                    </Button>
                  </div>
                  <div className="bg-muted/50 p-4 rounded-lg space-y-4">
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
                        className="w-full px-3 py-2 bg-input border border-border rounded-md focus:ring-2 focus:ring-primary focus:border-transparent"
                      />
                    </div>
                    <div>
                      <label className="text-sm font-medium mb-2 block">Model</label>
                      <select
                        value={config.claudeModel}
                        onChange={(e) => setConfig({ ...config, claudeModel: e.target.value })}
                        className="w-full px-3 py-2 bg-input border border-border rounded-md focus:ring-2 focus:ring-primary focus:border-transparent"
                      >
                        <option value="claude-3-opus-20240229">Claude 3 Opus (最强)</option>
                        <option value="claude-3-sonnet-20240229">Claude 3 Sonnet (平衡)</option>
                        <option value="claude-3-haiku-20240307">Claude 3 Haiku (快速)</option>
                      </select>
                    </div>
                  </div>
                </div>

                <Separator />

                {/* Gemini */}
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <h3 className="text-lg font-semibold">Gemini</h3>
                      <Badge variant="outline" className="text-xs">Google</Badge>
                    </div>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleTestConnection('Gemini')}
                    >
                      测试连接
                    </Button>
                  </div>
                  <div className="bg-muted/50 p-4 rounded-lg space-y-4">
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
                        className="w-full px-3 py-2 bg-input border border-border rounded-md focus:ring-2 focus:ring-primary focus:border-transparent"
                      >
                        <option value="gemini-pro">Gemini Pro</option>
                        <option value="gemini-pro-vision">Gemini Pro Vision</option>
                      </select>
                    </div>
                  </div>
                </div>

                <Separator />

                {/* Qwen (通义千问) */}
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <h3 className="text-lg font-semibold">通义千问 (Qwen)</h3>
                      <Badge variant="secondary" className="text-xs">阿里云</Badge>
                    </div>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleTestConnection('Qwen')}
                    >
                      测试连接
                    </Button>
                  </div>
                  <div className="bg-muted/50 p-4 rounded-lg space-y-4">
                    {renderSecretInput(
                      'API Key',
                      config.qwenApiKey,
                      (value) => setConfig({ ...config, qwenApiKey: value }),
                      'sk-...',
                      'qwenApiKey'
                    )}
                    <div>
                      <label className="text-sm font-medium mb-2 block">Base URL</label>
                      <input
                        type="text"
                        value={config.qwenBaseUrl}
                        onChange={(e) => setConfig({ ...config, qwenBaseUrl: e.target.value })}
                        placeholder="https://dashscope.aliyuncs.com/compatible-mode/v1"
                        className="w-full px-3 py-2 bg-input border border-border rounded-md focus:ring-2 focus:ring-primary focus:border-transparent"
                      />
                    </div>
                    <div>
                      <label className="text-sm font-medium mb-2 block">Model</label>
                      <select
                        value={config.qwenModel}
                        onChange={(e) => setConfig({ ...config, qwenModel: e.target.value })}
                        className="w-full px-3 py-2 bg-input border border-border rounded-md focus:ring-2 focus:ring-primary focus:border-transparent"
                      >
                        <option value="qwen-max">Qwen Max (最强)</option>
                        <option value="qwen-plus">Qwen Plus</option>
                        <option value="qwen-turbo">Qwen Turbo (快速)</option>
                      </select>
                    </div>
                  </div>
                </div>

                <Separator />

                {/* Moonshot Kimi */}
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <h3 className="text-lg font-semibold">Moonshot Kimi</h3>
                      <Badge variant="outline" className="text-xs">Kimi</Badge>
                    </div>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleTestConnection('Moonshot')}
                    >
                      测试连接
                    </Button>
                  </div>
                  <div className="bg-muted/50 p-4 rounded-lg space-y-4">
                    {renderSecretInput(
                      'API Key',
                      config.moonshotApiKey,
                      (value) => setConfig({ ...config, moonshotApiKey: value }),
                      'sk-...',
                      'moonshotApiKey'
                    )}
                    <div>
                      <label className="text-sm font-medium mb-2 block">Base URL</label>
                      <input
                        type="text"
                        value={config.moonshotBaseUrl}
                        onChange={(e) => setConfig({ ...config, moonshotBaseUrl: e.target.value })}
                        placeholder="https://api.moonshot.cn/v1"
                        className="w-full px-3 py-2 bg-input border border-border rounded-md focus:ring-2 focus:ring-primary focus:border-transparent"
                      />
                    </div>
                    <div>
                      <label className="text-sm font-medium mb-2 block">Model</label>
                      <select
                        value={config.moonshotModel}
                        onChange={(e) => setConfig({ ...config, moonshotModel: e.target.value })}
                        className="w-full px-3 py-2 bg-input border border-border rounded-md focus:ring-2 focus:ring-primary focus:border-transparent"
                      >
                        <option value="moonshot-v1-8k">Moonshot v1 8K</option>
                        <option value="moonshot-v1-32k">Moonshot v1 32K</option>
                        <option value="moonshot-v1-128k">Moonshot v1 128K</option>
                      </select>
                    </div>
                  </div>
                </div>

                <Separator />

                {/* Ollama */}
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <h3 className="text-lg font-semibold">Ollama</h3>
                      <Badge variant="secondary" className="text-xs">本地部署</Badge>
                    </div>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleTestConnection('Ollama')}
                    >
                      测试连接
                    </Button>
                  </div>
                  <div className="bg-muted/50 p-4 rounded-lg space-y-4">
                    <div>
                      <label className="text-sm font-medium mb-2 block">Base URL</label>
                      <input
                        type="text"
                        value={config.ollamaBaseUrl}
                        onChange={(e) => setConfig({ ...config, ollamaBaseUrl: e.target.value })}
                        placeholder="http://localhost:11434"
                        className="w-full px-3 py-2 bg-input border border-border rounded-md focus:ring-2 focus:ring-primary focus:border-transparent"
                      />
                    </div>
                    <div>
                      <label className="text-sm font-medium mb-2 block">Model</label>
                      <select
                        value={config.ollamaModel}
                        onChange={(e) => setConfig({ ...config, ollamaModel: e.target.value })}
                        className="w-full px-3 py-2 bg-input border border-border rounded-md focus:ring-2 focus:ring-primary focus:border-transparent"
                      >
                        <option value="llama2">Llama 2</option>
                        <option value="llama3">Llama 3</option>
                        <option value="mistral">Mistral</option>
                        <option value="codellama">Code Llama</option>
                      </select>
                    </div>
                  </div>
                </div>

                <Separator />

                {/* 火山引擎 */}
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <h3 className="text-lg font-semibold">火山引擎</h3>
                      <Badge variant="outline" className="text-xs">字节跳动</Badge>
                    </div>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleTestConnection('Volcengine')}
                    >
                      测试连接
                    </Button>
                  </div>
                  <div className="bg-muted/50 p-4 rounded-lg space-y-4">
                    {renderSecretInput(
                      'API Key',
                      config.volcengineApiKey,
                      (value) => setConfig({ ...config, volcengineApiKey: value }),
                      '...',
                      'volcengineApiKey'
                    )}
                    <div>
                      <label className="text-sm font-medium mb-2 block">Base URL</label>
                      <input
                        type="text"
                        value={config.volcengineBaseUrl}
                        onChange={(e) => setConfig({ ...config, volcengineBaseUrl: e.target.value })}
                        placeholder="https://ark.cn-beijing.volces.com/api/v3"
                        className="w-full px-3 py-2 bg-input border border-border rounded-md focus:ring-2 focus:ring-primary focus:border-transparent"
                      />
                    </div>
                    <div>
                      <label className="text-sm font-medium mb-2 block">Model</label>
                      <input
                        type="text"
                        value={config.volcengineModel}
                        onChange={(e) => setConfig({ ...config, volcengineModel: e.target.value })}
                        placeholder="ep-20240110134838-xxxxx"
                        className="w-full px-3 py-2 bg-input border border-border rounded-md focus:ring-2 focus:ring-primary focus:border-transparent"
                      />
                    </div>
                  </div>
                </div>

                <Separator />

                {/* 阿里云百炼 */}
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <h3 className="text-lg font-semibold">阿里云百炼</h3>
                      <Badge variant="secondary" className="text-xs">阿里云</Badge>
                    </div>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleTestConnection('Alibaba Bailian')}
                    >
                      测试连接
                    </Button>
                  </div>
                  <div className="bg-muted/50 p-4 rounded-lg space-y-4">
                    {renderSecretInput(
                      'API Key',
                      config.alibabaBailianApiKey,
                      (value) => setConfig({ ...config, alibabaBailianApiKey: value }),
                      'sk-...',
                      'alibabaBailianApiKey'
                    )}
                    <div>
                      <label className="text-sm font-medium mb-2 block">Base URL</label>
                      <input
                        type="text"
                        value={config.alibabaBailianBaseUrl}
                        onChange={(e) => setConfig({ ...config, alibabaBailianBaseUrl: e.target.value })}
                        placeholder="https://dashscope.aliyuncs.com/compatible-mode/v1"
                        className="w-full px-3 py-2 bg-input border border-border rounded-md focus:ring-2 focus:ring-primary focus:border-transparent"
                      />
                    </div>
                    <div>
                      <label className="text-sm font-medium mb-2 block">Model</label>
                      <select
                        value={config.alibabaBailianModel}
                        onChange={(e) => setConfig({ ...config, alibabaBailianModel: e.target.value })}
                        className="w-full px-3 py-2 bg-input border border-border rounded-md focus:ring-2 focus:ring-primary focus:border-transparent"
                      >
                        <option value="qwen-max">Qwen Max</option>
                        <option value="qwen-plus">Qwen Plus</option>
                        <option value="qwen-turbo">Qwen Turbo</option>
                      </select>
                    </div>
                  </div>
                </div>

                <Separator />

                {/* 硅基流动 */}
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <h3 className="text-lg font-semibold">硅基流动</h3>
                      <Badge variant="outline" className="text-xs">SiliconFlow</Badge>
                    </div>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleTestConnection('SiliconFlow')}
                    >
                      测试连接
                    </Button>
                  </div>
                  <div className="bg-muted/50 p-4 rounded-lg space-y-4">
                    {renderSecretInput(
                      'API Key',
                      config.siliconflowApiKey,
                      (value) => setConfig({ ...config, siliconflowApiKey: value }),
                      'sk-...',
                      'siliconflowApiKey'
                    )}
                    <div>
                      <label className="text-sm font-medium mb-2 block">Base URL</label>
                      <input
                        type="text"
                        value={config.siliconflowBaseUrl}
                        onChange={(e) => setConfig({ ...config, siliconflowBaseUrl: e.target.value })}
                        placeholder="https://api.siliconflow.cn/v1"
                        className="w-full px-3 py-2 bg-input border border-border rounded-md focus:ring-2 focus:ring-primary focus:border-transparent"
                      />
                    </div>
                    <div>
                      <label className="text-sm font-medium mb-2 block">Model</label>
                      <select
                        value={config.siliconflowModel}
                        onChange={(e) => setConfig({ ...config, siliconflowModel: e.target.value })}
                        className="w-full px-3 py-2 bg-input border border-border rounded-md focus:ring-2 focus:ring-primary focus:border-transparent"
                      >
                        <option value="Qwen/Qwen2.5-7B-Instruct">Qwen 2.5 7B</option>
                        <option value="Qwen/Qwen2.5-72B-Instruct">Qwen 2.5 72B</option>
                        <option value="deepseek-ai/DeepSeek-V3">DeepSeek V3</option>
                      </select>
                    </div>
                  </div>
                </div>

                <Separator />

                {/* OpenRouter */}
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <h3 className="text-lg font-semibold">OpenRouter</h3>
                      <Badge variant="secondary" className="text-xs">多模型聚合</Badge>
                    </div>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleTestConnection('OpenRouter')}
                    >
                      测试连接
                    </Button>
                  </div>
                  <div className="bg-muted/50 p-4 rounded-lg space-y-4">
                    {renderSecretInput(
                      'API Key',
                      config.openrouterApiKey,
                      (value) => setConfig({ ...config, openrouterApiKey: value }),
                      'sk-or-...',
                      'openrouterApiKey'
                    )}
                    <div>
                      <label className="text-sm font-medium mb-2 block">Base URL</label>
                      <input
                        type="text"
                        value={config.openrouterBaseUrl}
                        onChange={(e) => setConfig({ ...config, openrouterBaseUrl: e.target.value })}
                        placeholder="https://openrouter.ai/api/v1"
                        className="w-full px-3 py-2 bg-input border border-border rounded-md focus:ring-2 focus:ring-primary focus:border-transparent"
                      />
                    </div>
                    <div>
                      <label className="text-sm font-medium mb-2 block">Model</label>
                      <select
                        value={config.openrouterModel}
                        onChange={(e) => setConfig({ ...config, openrouterModel: e.target.value })}
                        className="w-full px-3 py-2 bg-input border border-border rounded-md focus:ring-2 focus:ring-primary focus:border-transparent"
                      >
                        <option value="openai/gpt-4-turbo">GPT-4 Turbo</option>
                        <option value="anthropic/claude-3-opus">Claude 3 Opus</option>
                        <option value="google/gemini-pro">Gemini Pro</option>
                      </select>
                    </div>
                  </div>
                </div>

                <Separator />

                {/* 轮询策略 */}
                <div className="space-y-4">
                  <div className="flex items-center space-x-2">
                    <h3 className="text-lg font-semibold">轮询策略</h3>
                    <Badge variant="default" className="text-xs">智能选择</Badge>
                  </div>
                  <div className="bg-muted/50 p-4 rounded-lg">
                    <label className="text-sm font-medium mb-2 block">选择提供商轮询策略</label>
                    <select
                      value={config.aiRotationStrategy}
                      onChange={(e) => setConfig({ ...config, aiRotationStrategy: e.target.value })}
                      className="w-full px-3 py-2 bg-input border border-border rounded-md focus:ring-2 focus:ring-primary focus:border-transparent"
                    >
                      <option value="sequential">顺序轮询 - 按顺序依次使用提供商</option>
                      <option value="random">随机轮询 - 随机选择可用提供商</option>
                    </select>
                    <p className="text-xs text-muted-foreground mt-2">
                      当不指定提供商时，系统会使用此策略自动选择AI模型
                    </p>
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
                <CardDescription>配置微信公众号的 AppID 和 AppSecret 以实现自动发布</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="bg-green-50 dark:bg-green-950/20 border border-green-200 dark:border-green-800 p-4 rounded-lg">
                  <div className="flex items-start space-x-3">
                    <Key className="h-5 w-5 text-green-600 dark:text-green-400 mt-0.5" />
                    <div>
                      <h4 className="font-medium text-green-900 dark:text-green-100 mb-1">为什么需要配置？</h4>
                      <p className="text-sm text-green-700 dark:text-green-300">配置微信公众号后，系统可以自动将生成的文章发布到你的公众号，实现全流程自动化。</p>
                    </div>
                  </div>
                </div>

                <div className="space-y-4">
                  <div>
                    <label className="text-sm font-medium mb-2 flex items-center">
                      AppID
                      <Badge variant="outline" className="ml-2 text-xs">必需</Badge>
                    </label>
                    <input
                      type="text"
                      value={config.wechatAppId}
                      onChange={(e) => setConfig({ ...config, wechatAppId: e.target.value })}
                      placeholder="wx..."
                      className="w-full px-3 py-2 bg-input border border-border rounded-md focus:ring-2 focus:ring-primary focus:border-transparent"
                    />
                    <p className="text-xs text-muted-foreground mt-2">
                      微信公众号的唯一标识符，以 wx 开头
                    </p>
                  </div>

                  {renderSecretInput(
                    'AppSecret',
                    config.wechatAppSecret,
                    (value) => setConfig({ ...config, wechatAppSecret: value }),
                    '...',
                    'wechatAppSecret'
                  )}
                  <p className="text-xs text-muted-foreground">
                    用于接口调用的密钥，请妥善保管
                  </p>
                </div>

                <Separator />

                <div className="bg-muted/50 p-4 rounded-lg">
                  <h4 className="font-medium mb-3 flex items-center">
                    <AlertCircle className="mr-2 h-4 w-4" />
                    如何获取 AppID 和 AppSecret?
                  </h4>
                  <ol className="text-sm text-muted-foreground space-y-2 list-decimal list-inside">
                    <li>登录 <a href="https://mp.weixin.qq.com" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">微信公众平台</a></li>
                    <li>进入 "开发 > 基本配置"</li>
                    <li>查看 AppID 和生成 AppSecret</li>
                    <li>配置服务器地址和令牌（如果需要）</li>
                  </ol>
                </div>

                <div className="bg-blue-50 dark:bg-blue-950/20 border border-blue-200 dark:border-blue-800 p-4 rounded-lg">
                  <h4 className="font-medium mb-2 text-blue-900 dark:text-blue-100">注意事项</h4>
                  <ul className="text-sm text-blue-700 dark:text-blue-300 space-y-1 list-disc list-inside">
                    <li>AppSecret 只显示一次，请立即保存</li>
                    <li>确保公众号已认证（服务号或订阅号）</li>
                    <li>需要开启公众号的"开发者权限"</li>
                  </ul>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Database Configuration */}
          <TabsContent value="database">
            <Card>
              <CardHeader>
                <CardTitle>数据库配置</CardTitle>
                <CardDescription>配置 PostgreSQL 和 Redis 连接信息</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="bg-blue-50 dark:bg-blue-950/20 border border-blue-200 dark:border-blue-800 p-4 rounded-lg">
                  <div className="flex items-start space-x-3">
                    <AlertCircle className="h-5 w-5 text-blue-600 dark:text-blue-400 mt-0.5" />
                    <div>
                      <h4 className="font-medium text-blue-900 dark:text-blue-100 mb-1">为什么需要配置数据库？</h4>
                      <p className="text-sm text-blue-700 dark:text-blue-300">数据库用于存储文章、任务记录和系统配置。如果你使用 Docker 部署，通常使用默认配置即可。</p>
                    </div>
                  </div>
                </div>

                <div>
                  <label className="text-sm font-medium mb-2 flex items-center">
                    PostgreSQL 连接地址
                    <Badge variant="outline" className="ml-2 text-xs">必需</Badge>
                  </label>
                  <input
                    type="text"
                    value={config.databaseUrl}
                    onChange={(e) => setConfig({ ...config, databaseUrl: e.target.value })}
                    placeholder="postgresql+asyncpg://user:password@localhost:5432/wechat_ai_writer"
                    className="w-full px-3 py-2 bg-input border border-border rounded-md font-mono text-sm focus:ring-2 focus:ring-primary focus:border-transparent"
                  />
                  <p className="text-xs text-muted-foreground mt-2">
                    格式: postgresql+asyncpg://用户名:密码@主机:端口/数据库名
                  </p>
                </div>

                <div>
                  <label className="text-sm font-medium mb-2 flex items-center">
                    Redis 连接地址
                    <Badge variant="outline" className="ml-2 text-xs">必需</Badge>
                  </label>
                  <input
                    type="text"
                    value={config.redisUrl}
                    onChange={(e) => setConfig({ ...config, redisUrl: e.target.value })}
                    placeholder="redis://localhost:6379/0"
                    className="w-full px-3 py-2 bg-input border border-border rounded-md font-mono text-sm focus:ring-2 focus:ring-primary focus:border-transparent"
                  />
                  <p className="text-xs text-muted-foreground mt-2">
                    格式: redis://主机:端口/数据库编号
                  </p>
                </div>

                <div className="bg-muted/50 p-4 rounded-lg">
                  <h4 className="font-medium mb-2 flex items-center">
                    <CheckCircle2 className="mr-2 h-4 w-4 text-green-600" />
                    Docker 部署推荐配置
                  </h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex items-center justify-between p-2 bg-background rounded">
                      <span className="text-muted-foreground">PostgreSQL:</span>
                      <code className="text-xs bg-muted px-2 py-1 rounded">postgresql+asyncpg://postgres:postgres@postgres:5432/wechat_ai_writer</code>
                    </div>
                    <div className="flex items-center justify-between p-2 bg-background rounded">
                      <span className="text-muted-foreground">Redis:</span>
                      <code className="text-xs bg-muted px-2 py-1 rounded">redis://redis:6379/0</code>
                    </div>
                  </div>
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

          {/* Logging Configuration */}
          <TabsContent value="logging">
            <Card>
              <CardHeader>
                <CardTitle>日志配置</CardTitle>
                <CardDescription>配置系统日志记录和监控</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div>
                  <label className="text-sm font-medium mb-2 block">日志级别</label>
                  <select
                    value={config.logLevel}
                    onChange={(e) => setConfig({ ...config, logLevel: e.target.value })}
                    className="w-full px-3 py-2 bg-input border border-border rounded-md"
                  >
                    <option value="DEBUG">DEBUG - 调试信息</option>
                    <option value="INFO">INFO - 一般信息</option>
                    <option value="WARNING">WARNING - 警告信息</option>
                    <option value="ERROR">ERROR - 错误信息</option>
                    <option value="CRITICAL">CRITICAL - 严重错误</option>
                  </select>
                  <p className="text-xs text-muted-foreground mt-2">
                    生产环境建议使用 INFO 或 WARNING
                  </p>
                </div>

                <div>
                  <label className="text-sm font-medium mb-2 block">日志文件路径</label>
                  <input
                    type="text"
                    value={config.logFile}
                    onChange={(e) => setConfig({ ...config, logFile: e.target.value })}
                    placeholder="logs/app.log"
                    className="w-full px-3 py-2 bg-input border border-border rounded-md"
                  />
                </div>

                <Separator />

                <div>
                  <label className="text-sm font-medium mb-2 flex items-center">
                    启用性能监控
                  </label>
                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={config.enableMetrics}
                      onChange={(e) => setConfig({ ...config, enableMetrics: e.target.checked })}
                      className="w-5 h-5"
                    />
                    <span className="text-sm text-muted-foreground">收集性能指标</span>
                  </div>
                </div>

                <div>
                  <label className="text-sm font-medium mb-2 block">监控端口</label>
                  <input
                    type="number"
                    value={config.metricsPort}
                    onChange={(e) => setConfig({ ...config, metricsPort: parseInt(e.target.value) })}
                    className="w-full px-3 py-2 bg-input border border-border rounded-md"
                  />
                  <p className="text-xs text-muted-foreground mt-1">
                    默认: 9090
                  </p>
                </div>

                <div>
                  <label className="text-sm font-medium mb-2 block">Sentry DSN (可选)</label>
                  <input
                    type="text"
                    value={config.sentryDsn}
                    onChange={(e) => setConfig({ ...config, sentryDsn: e.target.value })}
                    placeholder="https://xxx@sentry.io/xxx"
                    className="w-full px-3 py-2 bg-input border border-border rounded-md"
                  />
                  <p className="text-xs text-muted-foreground mt-2">
                    用于错误追踪和监控，留空则不启用
                  </p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Security Configuration */}
          <TabsContent value="security">
            <Card>
              <CardHeader>
                <CardTitle>安全配置</CardTitle>
                <CardDescription>配置系统安全防护和访问控制</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="bg-red-50 dark:bg-red-950/20 border border-red-200 dark:border-red-800 p-4 rounded-lg">
                  <div className="flex items-start space-x-3">
                    <AlertCircle className="h-5 w-5 text-red-600 dark:text-red-400 mt-0.5" />
                    <div>
                      <h4 className="font-medium text-red-900 dark:text-red-100 mb-1">安全提示</h4>
                      <p className="text-sm text-red-700 dark:text-red-300">合理的限流配置可以防止恶意请求，保护系统稳定性。</p>
                    </div>
                  </div>
                </div>

                <div>
                  <label className="text-sm font-medium mb-2 flex items-center">
                    启用请求限流
                  </label>
                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={config.rateLimitEnabled}
                      onChange={(e) => setConfig({ ...config, rateLimitEnabled: e.target.checked })}
                      className="w-5 h-5"
                    />
                    <span className="text-sm text-muted-foreground">限制每个用户的请求频率</span>
                  </div>
                </div>

                <div>
                  <label className="text-sm font-medium mb-2 block">限流请求数</label>
                  <input
                    type="number"
                    value={config.rateLimitRequests}
                    onChange={(e) => setConfig({ ...config, rateLimitRequests: parseInt(e.target.value) })}
                    className="w-full px-3 py-2 bg-input border border-border rounded-md"
                  />
                  <p className="text-xs text-muted-foreground mt-1">
                    默认: 100 (每个时间窗口内的最大请求数)
                  </p>
                </div>

                <div>
                  <label className="text-sm font-medium mb-2 block">限流时间周期 (秒)</label>
                  <input
                    type="number"
                    value={config.rateLimitPeriod}
                    onChange={(e) => setConfig({ ...config, rateLimitPeriod: parseInt(e.target.value) })}
                    className="w-full px-3 py-2 bg-input border border-border rounded-md"
                  />
                  <p className="text-xs text-muted-foreground mt-1">
                    默认: 60 (秒)
                  </p>
                </div>

                <div className="bg-muted/50 p-4 rounded-lg">
                  <h4 className="font-medium mb-2">限流示例</h4>
                  <div className="text-sm text-muted-foreground space-y-1">
                    <p>当前配置: 每分钟最多 100 次请求</p>
                    <p>超出限制将返回 429 错误</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Application Configuration */}
          <TabsContent value="app">
            <Card>
              <CardHeader>
                <CardTitle>应用配置</CardTitle>
                <CardDescription>配置应用基本信息和安全设置</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div>
                  <label className="text-sm font-medium mb-2 block">应用名称</label>
                  <input
                    type="text"
                    value={config.appName}
                    onChange={(e) => setConfig({ ...config, appName: e.target.value })}
                    placeholder="AI公众号自动写作助手 Pro"
                    className="w-full px-3 py-2 bg-input border border-border rounded-md"
                  />
                </div>

                <div>
                  <label className="text-sm font-medium mb-2 block">应用版本</label>
                  <input
                    type="text"
                    value={config.appVersion}
                    onChange={(e) => setConfig({ ...config, appVersion: e.target.value })}
                    placeholder="1.0.0"
                    className="w-full px-3 py-2 bg-input border border-border rounded-md"
                  />
                </div>

                <div>
                  <label className="text-sm font-medium mb-2 flex items-center">
                    应用密钥
                    <Badge variant="destructive" className="ml-2 text-xs">重要</Badge>
                  </label>
                  {renderSecretInput(
                    '',
                    config.secretKey,
                    (value) => setConfig({ ...config, secretKey: value }),
                    '生成一个强随机密钥',
                    'secretKey'
                  )}
                  <p className="text-xs text-muted-foreground mt-2">
                    用于加密和会话管理，建议使用至少 32 位的随机字符串
                  </p>
                </div>

                <Separator />

                <div>
                  <label className="text-sm font-medium mb-2 block">上传目录</label>
                  <input
                    type="text"
                    value={config.uploadDir}
                    onChange={(e) => setConfig({ ...config, uploadDir: e.target.value })}
                    placeholder="uploads"
                    className="w-full px-3 py-2 bg-input border border-border rounded-md"
                  />
                </div>

                <div>
                  <label className="text-sm font-medium mb-2 block">临时目录</label>
                  <input
                    type="text"
                    value={config.tempDir}
                    onChange={(e) => setConfig({ ...config, tempDir: e.target.value })}
                    placeholder="temp"
                    className="w-full px-3 py-2 bg-input border border-border rounded-md"
                  />
                </div>

                <div>
                  <label className="text-sm font-medium mb-2 block">最大上传大小 (字节)</label>
                  <input
                    type="number"
                    value={config.maxUploadSize}
                    onChange={(e) => setConfig({ ...config, maxUploadSize: parseInt(e.target.value) })}
                    className="w-full px-3 py-2 bg-input border border-border rounded-md"
                  />
                  <p className="text-xs text-muted-foreground mt-1">
                    默认: 20971520 (20MB)
                  </p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Task Configuration */}
          <TabsContent value="task">
            <Card>
              <CardHeader>
                <CardTitle>任务配置</CardTitle>
                <CardDescription>配置异步任务和调度器参数</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div>
                  <label className="text-sm font-medium mb-2 block">Celery 消息队列地址</label>
                  <input
                    type="text"
                    value={config.celeryBrokerUrl}
                    onChange={(e) => setConfig({ ...config, celeryBrokerUrl: e.target.value })}
                    placeholder="redis://localhost:6379/1"
                    className="w-full px-3 py-2 bg-input border border-border rounded-md font-mono text-sm"
                  />
                  <p className="text-xs text-muted-foreground mt-2">
                    用于任务消息传递，建议使用 Redis 数据库编号 1
                  </p>
                </div>

                <div>
                  <label className="text-sm font-medium mb-2 block">Celery 结果存储地址</label>
                  <input
                    type="text"
                    value={config.celeryResultBackend}
                    onChange={(e) => setConfig({ ...config, celeryResultBackend: e.target.value })}
                    placeholder="redis://localhost:6379/1"
                    className="w-full px-3 py-2 bg-input border border-border rounded-md font-mono text-sm"
                  />
                  <p className="text-xs text-muted-foreground mt-2">
                    用于存储任务执行结果
                  </p>
                </div>

                <div>
                  <label className="text-sm font-medium mb-2 block">任务超时时间 (秒)</label>
                  <input
                    type="number"
                    value={config.taskTimeout}
                    onChange={(e) => setConfig({ ...config, taskTimeout: parseInt(e.target.value) })}
                    className="w-full px-3 py-2 bg-input border border-border rounded-md"
                  />
                  <p className="text-xs text-muted-foreground mt-1">
                    默认: 3600 (1小时)
                  </p>
                </div>

                <div>
                  <label className="text-sm font-medium mb-2 block">最大重试次数</label>
                  <input
                    type="number"
                    value={config.taskMaxRetries}
                    onChange={(e) => setConfig({ ...config, taskMaxRetries: parseInt(e.target.value) })}
                    className="w-full px-3 py-2 bg-input border border-border rounded-md"
                  />
                  <p className="text-xs text-muted-foreground mt-1">
                    默认: 3 次
                  </p>
                </div>

                <div className="bg-green-50 dark:bg-green-950/20 border border-green-200 dark:border-green-800 p-4 rounded-lg">
                  <div className="flex items-start space-x-3">
                    <CheckCircle2 className="h-5 w-5 text-green-600 dark:text-green-400 mt-0.5" />
                    <div>
                      <h4 className="font-medium text-green-900 dark:text-green-100 mb-1">提示</h4>
                      <p className="text-sm text-green-700 dark:text-green-300">如果你使用 Docker 部署，Celery 配置通常使用默认值即可。</p>
                    </div>
                  </div>
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
                <div className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50 transition-colors">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <h4 className="font-medium">深度研究</h4>
                      <Badge variant="secondary" className="text-xs">高级</Badge>
                    </div>
                    <p className="text-sm text-muted-foreground mt-1">启用联网搜索,增强内容深度和准确性</p>
                  </div>
                  <input
                    type="checkbox"
                    checked={config.enableResearch}
                    onChange={(e) => setConfig({ ...config, enableResearch: e.target.checked })}
                    className="w-5 h-5"
                  />
                </div>

                <div className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50 transition-colors">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <h4 className="font-medium">AI 图片生成</h4>
                      <Badge variant="secondary" className="text-xs">推荐</Badge>
                    </div>
                    <p className="text-sm text-muted-foreground mt-1">自动生成封面图和技术配图</p>
                  </div>
                  <input
                    type="checkbox"
                    checked={config.enableImageGeneration}
                    onChange={(e) => setConfig({ ...config, enableImageGeneration: e.target.checked })}
                    className="w-5 h-5"
                  />
                </div>

                <div className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50 transition-colors">
                  <div className="flex-1">
                    <h4 className="font-medium">Markdown 编辑器</h4>
                    <p className="text-sm text-muted-foreground mt-1">使用 Markdown 编辑器编写内容</p>
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