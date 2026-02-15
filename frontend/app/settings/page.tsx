'use client'

import { useState, useEffect } from 'react'
import {
  Save,
  Key,
  Bot,
  Settings as SettingsIcon,
  CheckCircle,
  Eye,
  EyeOff,
  Loader2,
  MessageCircle,
  Image as ImageIcon,
  Plus,
  Trash2,
  TestTube,
  Star,
  Wand2,
  RefreshCw
} from 'lucide-react'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
const DEV88_DEFAULT_MODEL = 'gpt-5-nano [渠道id:33][輸出3k上限]'

const normalizeOpenAIModel = (baseUrl: string, model: string) => {
  if (baseUrl.includes('api.dev88.tech') && model === 'gpt-5-nano') {
    return DEV88_DEFAULT_MODEL
  }
  return model
}

const defaultProviderTypes = [
  { type: 'pollinations', name: 'Pollinations.ai', description: '完全免费，无需API Key', requires_config: false, recommended: true },
  { type: 'pexels', name: 'Pexels', description: '免费高质量图库', requires_config: true, recommended: true },
  { type: 'tongyi_wanxiang', name: '通义万相', description: '阿里云AI绘画，支持中文', requires_config: true, recommended: true },
  { type: 'leonardo', name: 'Leonardo.ai', description: '每日150 tokens免费额度', requires_config: true, recommended: false },
  { type: 'stable_diffusion', name: 'Stable Diffusion', description: '开源模型', requires_config: true, recommended: false },
]

export default function SettingsPage() {
  const [loading, setLoading] = useState(false)
  const [saved, setSaved] = useState(false)
  const [activeTab, setActiveTab] = useState('ai')
  const [showSecrets, setShowSecrets] = useState<Record<string, boolean>>({})

  const [config, setConfig] = useState({
    aiProvider: 'openai',
    deepseekApiKey: '',
    deepseekBaseUrl: 'https://api.deepseek.com/v1',
    deepseekModel: 'deepseek-chat',
    openaiApiKey: '',
    openaiBaseUrl: 'https://api.dev88.tech/v1',
    openaiModel: DEV88_DEFAULT_MODEL,
    geminiApiKey: '',
    geminiBaseUrl: 'https://generativelanguage.googleapis.com/v1beta',
    geminiModel: 'gemini-pro',
    wechatAppId: '',
    wechatAppSecret: '',
  })

  const [imageProviders, setImageProviders] = useState<any[]>([])
  const [providerTypes, setProviderTypes] = useState<any[]>(defaultProviderTypes)
  const [showAddProvider, setShowAddProvider] = useState(false)
  const [newProvider, setNewProvider] = useState({
    provider_type: 'pollinations',
    name: 'Pollinations.ai',
    api_key: '',
    is_default: false,
    default_width: 900,
    default_height: 500
  })

  useEffect(() => {
    loadConfig()
    loadImageProviders()
  }, [])

  const loadConfig = async () => {
    try {
      const [globalResponse, providersResponse] = await Promise.all([
        fetch(`${API_URL}/api/config`),
        fetch(`${API_URL}/api/config/providers`),
      ])

      if (globalResponse.ok) {
        const data = await globalResponse.json()
        if (data.config) {
          setConfig(prev => {
            const activeProvider = data.config.ai_provider || prev.aiProvider
            const nextConfig = {
              ...prev,
              aiProvider: activeProvider,
              wechatAppId: data.config.wechat_app_id || '',
              wechatAppSecret: data.config.wechat_app_secret || '',
            }

            if (activeProvider === 'deepseek') {
              nextConfig.deepseekApiKey = data.config.api_key || ''
              nextConfig.deepseekBaseUrl = data.config.base_url || prev.deepseekBaseUrl
              nextConfig.deepseekModel = data.config.model || prev.deepseekModel
            } else if (activeProvider === 'openai') {
              nextConfig.openaiApiKey = data.config.api_key || ''
              nextConfig.openaiBaseUrl = data.config.base_url || prev.openaiBaseUrl
              nextConfig.openaiModel = normalizeOpenAIModel(
                nextConfig.openaiBaseUrl,
                data.config.model || prev.openaiModel,
              )
            } else if (activeProvider === 'gemini') {
              nextConfig.geminiApiKey = data.config.api_key || ''
              nextConfig.geminiBaseUrl = data.config.base_url || prev.geminiBaseUrl
              nextConfig.geminiModel = data.config.model || prev.geminiModel
            }

            return nextConfig
          })
        }
      }

      if (providersResponse.ok) {
        const providerData = await providersResponse.json()
        if (providerData.success && Array.isArray(providerData.providers)) {
          const providerMap = Object.fromEntries(
            providerData.providers.map((item: any) => [item.provider, item])
          )

          setConfig(prev => ({
            ...prev,
            deepseekBaseUrl: providerMap.deepseek?.base_url || prev.deepseekBaseUrl,
            deepseekModel: providerMap.deepseek?.model || prev.deepseekModel,
            openaiBaseUrl: providerMap.openai?.base_url || prev.openaiBaseUrl,
            openaiModel: normalizeOpenAIModel(
              providerMap.openai?.base_url || prev.openaiBaseUrl,
              providerMap.openai?.model || prev.openaiModel,
            ),
            geminiBaseUrl: providerMap.gemini?.base_url || prev.geminiBaseUrl,
            geminiModel: providerMap.gemini?.model || prev.geminiModel,
          }))
        }
      }
    } catch (error) {
      console.error('加载配置失败:', error)
    }
  }

  const loadImageProviders = async () => {
    try {
      const localConfigs = localStorage.getItem('image_providers')
      if (localConfigs) setImageProviders(JSON.parse(localConfigs))
      
      const response = await fetch(`${API_URL}/api/image-providers/configs`)
      if (response.ok) {
        const data = await response.json()
        if (data.success && data.configs) {
          setImageProviders(data.configs)
          localStorage.setItem('image_providers', JSON.stringify(data.configs))
        }
      }
    } catch (error) {
      console.error('加载图片配置失败:', error)
    }
  }

  const handleAddProvider = async () => {
    setLoading(true)
    try {
      const providerType = providerTypes.find(p => p.type === newProvider.provider_type)
      const apiConfig = providerType?.requires_config ? { api_key: newProvider.api_key } : {}
      const width = newProvider.default_width || 900
      const height = newProvider.default_height || 500

      const response = await fetch(`${API_URL}/api/image-providers/configs`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          provider_type: newProvider.provider_type,
          name: newProvider.name || providerType?.name,
          api_config: apiConfig,
          default_params: { width, height },
          is_default: newProvider.is_default,
          priority: imageProviders.length
        }),
      })

      if (!response.ok && response.status === 404) {
        const localConfig = {
          id: Date.now(),
          provider_type: newProvider.provider_type,
          name: newProvider.name || providerType?.name,
          api_config: apiConfig,
          default_params: { width, height },
          is_default: newProvider.is_default,
          is_enabled: true,
          priority: imageProviders.length,
        }
        const updatedProviders = [...imageProviders, localConfig]
        setImageProviders(updatedProviders)
        localStorage.setItem('image_providers', JSON.stringify(updatedProviders))
        setShowAddProvider(false)
        setLoading(false)
        return
      }
      
      await loadImageProviders()
      setShowAddProvider(false)
    } catch (error) {
      alert('添加失败')
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteProvider = async (id: number) => {
    if (!confirm('确定删除？')) return
    setLoading(true)
    try {
      const response = await fetch(`${API_URL}/api/image-providers/configs/${id}`, { method: 'DELETE' })
      if (!response.ok && response.status === 404) {
        const updatedProviders = imageProviders.filter(p => p.id !== id)
        setImageProviders(updatedProviders)
        localStorage.setItem('image_providers', JSON.stringify(updatedProviders))
        setLoading(false)
        return
      }
      await loadImageProviders()
    } catch (error) {
      alert('删除失败')
    } finally {
      setLoading(false)
    }
  }

  const handleTestProvider = async (id: number) => {
    setLoading(true)
    try {
      const response = await fetch(`${API_URL}/api/image-providers/configs/${id}/test`, { method: 'POST' })
      if (!response.ok && response.status === 404) {
        const provider = imageProviders.find(p => p.id === id)
        alert(provider?.provider_type === 'pollinations' ? 'Pollinations 配置有效' : '配置已保存')
        setLoading(false)
        return
      }
      const result = await response.json()
      alert(result.success ? '测试成功' : `失败：${result.message}`)
    } catch (error) {
      alert('测试失败')
    } finally {
      setLoading(false)
    }
  }

  const handleSetDefault = async (id: number) => {
    setLoading(true)
    try {
      const response = await fetch(`${API_URL}/api/image-providers/configs/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ is_default: true }),
      })
      if (!response.ok && response.status === 404) {
        const updatedProviders = imageProviders.map(p => ({ ...p, is_default: p.id === id }))
        setImageProviders(updatedProviders)
        localStorage.setItem('image_providers', JSON.stringify(updatedProviders))
        setLoading(false)
        return
      }
      await loadImageProviders()
    } catch (error) {
      alert('设置失败')
    } finally {
      setLoading(false)
    }
  }

  const handleQuickSetup = async () => {
    setLoading(true)
    try {
      const response = await fetch(`${API_URL}/api/image-providers/quick-setup`, { method: 'POST' })
      if (!response.ok && response.status === 404) {
        const now = new Date().toISOString()
        const localConfigs = [
          { id: Date.now(), provider_type: 'pollinations', name: 'Pollinations.ai', api_config: {}, default_params: { width: 900, height: 500 }, is_default: true, is_enabled: true },
          { id: Date.now() + 1, provider_type: 'pexels', name: 'Pexels', api_config: { api_key: '' }, default_params: { width: 900, height: 500 }, is_default: false, is_enabled: true },
          { id: Date.now() + 2, provider_type: 'tongyi_wanxiang', name: '通义万相', api_config: { api_key: '' }, default_params: { width: 900, height: 500 }, is_default: false, is_enabled: true },
        ]
        setImageProviders(localConfigs)
        localStorage.setItem('image_providers', JSON.stringify(localConfigs))
        setLoading(false)
        return
      }
      await loadImageProviders()
    } catch (error) {
      alert('快速设置失败')
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    setLoading(true)
    try {
      const providerPayloads = [
        {
          provider: 'deepseek',
          api_key: config.deepseekApiKey.trim(),
          base_url: config.deepseekBaseUrl,
          model: config.deepseekModel,
        },
        {
          provider: 'openai',
          api_key: config.openaiApiKey.trim(),
          base_url: config.openaiBaseUrl,
          model: normalizeOpenAIModel(config.openaiBaseUrl, config.openaiModel),
        },
        {
          provider: 'gemini',
          api_key: config.geminiApiKey.trim(),
          base_url: config.geminiBaseUrl,
          model: config.geminiModel,
        },
      ]

      const providerSaveRequests = providerPayloads
        .filter(item => item.api_key)
        .map(item =>
          fetch(`${API_URL}/api/config/providers`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              provider: item.provider,
              api_key: item.api_key,
              base_url: item.base_url,
              model: item.model,
              is_enabled: true,
              is_default: false,
            }),
          })
        )

      const providerSaveResponses = await Promise.all(providerSaveRequests)
      const hasProviderSaveFailed = providerSaveResponses.some(item => !item.ok)
      if (hasProviderSaveFailed) {
        throw new Error('保存提供商配置失败')
      }

      const response = await fetch(`${API_URL}/api/config/providers/${config.aiProvider}/activate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          wechat_app_id: config.wechatAppId,
          wechat_app_secret: config.wechatAppSecret,
        }),
      })
      if (!response.ok) {
        const errorData = await response.json().catch(() => null)
        throw new Error(errorData?.detail || '保存失败')
      }

      setSaved(true)
      setTimeout(() => setSaved(false), 3000)
    } catch (error) {
      const message = error instanceof Error ? error.message : '保存配置失败'
      alert(message)
    } finally {
      setLoading(false)
    }
  }

  const handleTestConnection = async (provider: 'deepseek' | 'openai') => {
    setLoading(true)
    try {
      const providerLabel = provider === 'deepseek' ? 'DeepSeek' : 'OpenAI'
      const apiKey = provider === 'deepseek' ? config.deepseekApiKey : config.openaiApiKey
      if (!apiKey) {
        alert(`请先填写 ${providerLabel} 的 API Key`)
        return
      }
      const response = await fetch(`${API_URL}/api/config/test-api`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          api_key: apiKey,
          base_url: provider === 'deepseek' ? config.deepseekBaseUrl : config.openaiBaseUrl,
          model: provider === 'deepseek' ? config.deepseekModel : config.openaiModel,
        }),
      })
      const result = await response.json()
      alert(result.success ? `${providerLabel} 连接成功` : `连接失败：${result.message}`)
    } catch (error) {
      alert('连接测试失败')
    } finally {
      setLoading(false)
    }
  }

  const tabs = [
    { id: 'ai', name: 'AI 模型', icon: Bot },
    { id: 'image', name: '图片生成', icon: ImageIcon },
    { id: 'wechat', name: '微信公众号', icon: MessageCircle },
  ]

  const inputClasses = "w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 text-sm focus:outline-none focus:border-violet-400 focus:ring-2 focus:ring-violet-100 transition-all"

  return (
    <div className="min-h-screen bg-slate-50">
      {/* 头部 */}
      <div className="bg-white border-b border-slate-200 sticky top-0 z-30">
        <div className="max-w-4xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-slate-900 flex items-center justify-center">
                <SettingsIcon className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-lg font-semibold text-slate-900">系统设置</h1>
                <p className="text-xs text-slate-500">配置AI、图片和发布服务</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              {saved && (
                <span className="flex items-center gap-1 text-emerald-600 text-sm font-medium">
                  <CheckCircle className="w-4 h-4" />
                  已保存
                </span>
              )}
              <button
                onClick={handleSave}
                disabled={loading}
                className="flex items-center gap-2 px-4 py-2 rounded-xl bg-violet-500 text-white text-sm font-medium hover:bg-violet-600 disabled:opacity-50 transition-colors"
              >
                {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
                保存配置
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-6 py-6">
        {/* 标签页 */}
        <div className="flex gap-2 mb-6">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-colors ${
                activeTab === tab.id
                  ? 'bg-slate-900 text-white'
                  : 'bg-white text-slate-600 hover:bg-slate-100 border border-slate-200'
              }`}
            >
              <tab.icon className="w-4 h-4" />
              {tab.name}
            </button>
          ))}
        </div>

        {/* AI 模型配置 */}
        {activeTab === 'ai' && (
          <div className="space-y-4">
            <div className="bg-white rounded-2xl border border-slate-200 p-5">
              <label className="block text-xs text-slate-500 mb-1.5">默认文章生成提供商</label>
              <select
                value={config.aiProvider}
                onChange={(e) => setConfig({ ...config, aiProvider: e.target.value })}
                className={inputClasses}
              >
                <option value="openai">OpenAI（当前推荐）</option>
                <option value="deepseek">DeepSeek</option>
                <option value="gemini">Gemini</option>
              </select>
              <p className="text-xs text-slate-500 mt-2">
                保存时会同步写入各提供商配置；默认提供商用于文章生成的主链路。
              </p>
            </div>

            {/* DeepSeek */}
            <div className="bg-white rounded-2xl border border-slate-200 p-5">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 rounded-xl bg-orange-100 flex items-center justify-center">
                    <Bot className="w-4 h-4 text-orange-600" />
                  </div>
                  <div>
                    <h3 className="font-medium text-slate-900">DeepSeek</h3>
                    <p className="text-xs text-slate-500">性价比高，推荐使用</p>
                  </div>
                </div>
                <button
                  onClick={() => handleTestConnection('deepseek')}
                  disabled={loading}
                  className="px-3 py-1.5 rounded-lg bg-slate-100 text-slate-600 text-xs font-medium hover:bg-slate-200"
                >
                  测试连接
                </button>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-slate-500 mb-1.5">API Key</label>
                  <div className="relative">
                    <input
                      type={showSecrets.deepseek ? 'text' : 'password'}
                      value={config.deepseekApiKey}
                      onChange={(e) => setConfig({ ...config, deepseekApiKey: e.target.value })}
                      placeholder="sk-..."
                      className={inputClasses + " pr-10"}
                    />
                    <button
                      onClick={() => setShowSecrets(prev => ({ ...prev, deepseek: !prev.deepseek }))}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                    >
                      {showSecrets.deepseek ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  </div>
                </div>
                <div>
                  <label className="block text-xs text-slate-500 mb-1.5">Model</label>
                  <select value={config.deepseekModel} onChange={(e) => setConfig({ ...config, deepseekModel: e.target.value })} className={inputClasses}>
                    <option value="deepseek-chat">DeepSeek Chat</option>
                    <option value="deepseek-coder">DeepSeek Coder</option>
                  </select>
                </div>
                <div className="sm:col-span-2">
                  <label className="block text-xs text-slate-500 mb-1.5">Base URL</label>
                  <input type="text" value={config.deepseekBaseUrl} onChange={(e) => setConfig({ ...config, deepseekBaseUrl: e.target.value })} className={inputClasses} />
                </div>
              </div>
            </div>

            {/* OpenAI */}
            <div className="bg-white rounded-2xl border border-slate-200 p-5">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 rounded-xl bg-blue-100 flex items-center justify-center">
                    <Bot className="w-4 h-4 text-blue-600" />
                  </div>
                  <div>
                    <h3 className="font-medium text-slate-900">OpenAI</h3>
                    <p className="text-xs text-slate-500">GPT-4 系列</p>
                  </div>
                </div>
                <button onClick={() => handleTestConnection('openai')} disabled={loading} className="px-3 py-1.5 rounded-lg bg-slate-100 text-slate-600 text-xs font-medium hover:bg-slate-200">
                  测试连接
                </button>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-slate-500 mb-1.5">API Key</label>
                  <div className="relative">
                    <input type={showSecrets.openai ? 'text' : 'password'} value={config.openaiApiKey} onChange={(e) => setConfig({ ...config, openaiApiKey: e.target.value })} placeholder="sk-..." className={inputClasses + " pr-10"} />
                    <button onClick={() => setShowSecrets(prev => ({ ...prev, openai: !prev.openai }))} className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600">
                      {showSecrets.openai ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  </div>
                </div>
                <div>
                  <label className="block text-xs text-slate-500 mb-1.5">Model</label>
                  <select value={config.openaiModel} onChange={(e) => setConfig({ ...config, openaiModel: e.target.value })} className={inputClasses}>
                    <option value="gpt-5-nano [渠道id:33][輸出3k上限]">GPT-5 Nano（渠道33）</option>
                    <option value="gpt-5-nano">GPT-5 Nano（通用别名）</option>
                    <option value="claude-sonnet-4.5">Claude Sonnet 4.5</option>
                    <option value="moonshotai/kimi-k2-thinking">Kimi K2 Thinking</option>
                    <option value="gemini-2.5-flash">Gemini 2.5 Flash</option>
                    <option value="gpt-4-turbo-preview">GPT-4 Turbo</option>
                  </select>
                </div>
                <div className="sm:col-span-2">
                  <label className="block text-xs text-slate-500 mb-1.5">Base URL</label>
                  <input type="text" value={config.openaiBaseUrl} onChange={(e) => setConfig({ ...config, openaiBaseUrl: e.target.value })} className={inputClasses} />
                </div>
              </div>
            </div>

            {/* Gemini */}
            <div className="bg-white rounded-2xl border border-slate-200 p-5">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-9 h-9 rounded-xl bg-emerald-100 flex items-center justify-center">
                  <Bot className="w-4 h-4 text-emerald-600" />
                </div>
                <div>
                  <h3 className="font-medium text-slate-900">Gemini</h3>
                  <p className="text-xs text-slate-500">Google AI</p>
                </div>
              </div>
              <div>
                <label className="block text-xs text-slate-500 mb-1.5">API Key</label>
                <div className="relative">
                  <input type={showSecrets.gemini ? 'text' : 'password'} value={config.geminiApiKey} onChange={(e) => setConfig({ ...config, geminiApiKey: e.target.value })} placeholder="AIza..." className={inputClasses + " pr-10"} />
                  <button onClick={() => setShowSecrets(prev => ({ ...prev, gemini: !prev.gemini }))} className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600">
                    {showSecrets.gemini ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* 微信配置 */}
        {activeTab === 'wechat' && (
          <div className="bg-white rounded-2xl border border-slate-200 p-5">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-9 h-9 rounded-xl bg-green-100 flex items-center justify-center">
                <MessageCircle className="w-4 h-4 text-green-600" />
              </div>
              <div>
                <h3 className="font-medium text-slate-900">微信公众号</h3>
                <p className="text-xs text-slate-500">用于自动发布文章到公众号草稿箱</p>
              </div>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label className="block text-xs text-slate-500 mb-1.5">App ID</label>
                <input type="text" value={config.wechatAppId} onChange={(e) => setConfig({ ...config, wechatAppId: e.target.value })} placeholder="wx..." className={inputClasses} />
              </div>
              <div>
                <label className="block text-xs text-slate-500 mb-1.5">App Secret</label>
                <div className="relative">
                  <input type={showSecrets.wechat ? 'text' : 'password'} value={config.wechatAppSecret} onChange={(e) => setConfig({ ...config, wechatAppSecret: e.target.value })} placeholder="..." className={inputClasses + " pr-10"} />
                  <button onClick={() => setShowSecrets(prev => ({ ...prev, wechat: !prev.wechat }))} className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600">
                    {showSecrets.wechat ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>
            </div>
            <div className="mt-4 p-3 rounded-xl bg-green-50 text-sm text-green-700">
              配置后可直接发布文章到公众号草稿箱
            </div>
          </div>
        )}

        {/* 图片生成配置 */}
        {activeTab === 'image' && (
          <div className="space-y-4">
            <div className="bg-white rounded-2xl border border-slate-200 p-5">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 rounded-xl bg-purple-100 flex items-center justify-center">
                    <Wand2 className="w-4 h-4 text-purple-600" />
                  </div>
                  <div>
                    <h3 className="font-medium text-slate-900">图片生成配置</h3>
                    <p className="text-xs text-slate-500">配置AI图片生成服务</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {imageProviders.length === 0 && (
                    <button onClick={handleQuickSetup} disabled={loading} className="px-3 py-1.5 rounded-lg bg-purple-500 text-white text-xs font-medium hover:bg-purple-600">
                      快速设置
                    </button>
                  )}
                  <button onClick={() => setShowAddProvider(true)} className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-100 text-slate-700 text-xs font-medium hover:bg-slate-200">
                    <Plus className="w-3.5 h-3.5" />
                    添加
                  </button>
                </div>
              </div>

              {/* 提供商列表 */}
              {imageProviders.length === 0 ? (
                <div className="text-center py-8">
                  <ImageIcon className="w-10 h-10 text-slate-300 mx-auto mb-3" />
                  <p className="text-slate-500 text-sm mb-3">暂无图片生成配置</p>
                  <button onClick={handleQuickSetup} className="px-4 py-2 rounded-xl bg-purple-500 text-white text-sm font-medium hover:bg-purple-600">
                    快速设置
                  </button>
                </div>
              ) : (
                <div className="space-y-2">
                  {imageProviders.map((provider) => (
                    <div key={provider.id} className="flex items-center justify-between p-3 rounded-xl bg-slate-50">
                      <div className="flex items-center gap-3">
                        <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${provider.is_default ? 'bg-purple-100' : 'bg-slate-200'}`}>
                          <ImageIcon className={`w-4 h-4 ${provider.is_default ? 'text-purple-600' : 'text-slate-400'}`} />
                        </div>
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="font-medium text-slate-900 text-sm">{provider.name}</span>
                            {provider.is_default && <span className="px-1.5 py-0.5 rounded bg-yellow-100 text-yellow-700 text-xs">默认</span>}
                          </div>
                          <span className="text-xs text-slate-500">{provider.provider_type}</span>
                        </div>
                      </div>
                      <div className="flex items-center gap-1">
                        <button onClick={() => handleTestProvider(provider.id)} className="p-1.5 rounded-lg hover:bg-slate-200 text-slate-400 hover:text-slate-600">
                          <TestTube className="w-4 h-4" />
                        </button>
                        {!provider.is_default && (
                          <button onClick={() => handleSetDefault(provider.id)} className="p-1.5 rounded-lg hover:bg-yellow-50 text-slate-400 hover:text-yellow-600">
                            <Star className="w-4 h-4" />
                          </button>
                        )}
                        <button onClick={() => handleDeleteProvider(provider.id)} className="p-1.5 rounded-lg hover:bg-red-50 text-slate-400 hover:text-red-500">
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* 推荐配置 */}
            <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-2xl p-5">
              <h4 className="text-sm font-medium text-slate-900 mb-3">推荐配置</h4>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                {[
                  { name: 'Pollinations.ai', desc: '完全免费，无需Key', tags: ['推荐', '免费'] },
                  { name: '通义万相', desc: '阿里云，支持中文', tags: ['推荐', '中文'] },
                  { name: 'Pexels', desc: '免费高质量图库', tags: ['推荐', '真实图片'] },
                ].map((item, idx) => (
                  <div key={idx} className="bg-white rounded-xl p-3 border border-purple-100">
                    <div className="flex gap-1 mb-2">
                      {item.tags.map((tag, i) => (
                        <span key={i} className="px-1.5 py-0.5 rounded bg-emerald-50 text-emerald-600 text-xs">{tag}</span>
                      ))}
                    </div>
                    <h5 className="font-medium text-slate-900 text-sm">{item.name}</h5>
                    <p className="text-xs text-slate-500">{item.desc}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* 添加配置弹窗 */}
      {showAddProvider && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" onClick={() => setShowAddProvider(false)} />
          <div className="relative w-full max-w-md bg-white rounded-2xl p-5">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-slate-900">添加图片生成配置</h3>
              <button onClick={() => setShowAddProvider(false)} className="p-1.5 rounded-lg hover:bg-slate-100">
                <EyeOff className="w-4 h-4 text-slate-500" />
              </button>
            </div>

            <div className="space-y-3">
              <div>
                <label className="block text-xs text-slate-500 mb-1.5">提供商类型</label>
                <select
                  value={newProvider.provider_type}
                  onChange={(e) => {
                    const selectedType = providerTypes.find(p => p.type === e.target.value)
                    setNewProvider({ ...newProvider, provider_type: e.target.value, name: selectedType?.name || '' })
                  }}
                  className={inputClasses}
                >
                  {providerTypes.map((type) => (
                    <option key={type.type} value={type.type}>
                      {type.recommended ? '⭐ ' : ''}{type.name} {type.requires_config ? '' : '(免费)'}
                    </option>
                  ))}
                </select>
                <p className="mt-1 text-xs text-slate-500">{providerTypes.find(p => p.type === newProvider.provider_type)?.description}</p>
              </div>

              <div>
                <label className="block text-xs text-slate-500 mb-1.5">配置名称</label>
                <input type="text" value={newProvider.name} onChange={(e) => setNewProvider({ ...newProvider, name: e.target.value })} className={inputClasses} />
              </div>

              {providerTypes.find(p => p.type === newProvider.provider_type)?.requires_config && (
                <div>
                  <label className="block text-xs text-slate-500 mb-1.5">API Key</label>
                  <input type="password" value={newProvider.api_key} onChange={(e) => setNewProvider({ ...newProvider, api_key: e.target.value })} placeholder="sk-..." className={inputClasses} />
                </div>
              )}

              <div className="flex items-center gap-2">
                <input type="checkbox" id="is_default" checked={newProvider.is_default} onChange={(e) => setNewProvider({ ...newProvider, is_default: e.target.checked })} className="w-4 h-4 rounded border-slate-300" />
                <label htmlFor="is_default" className="text-sm text-slate-600">设为默认提供商</label>
              </div>

              <div className="flex justify-end gap-2 pt-3">
                <button onClick={() => setShowAddProvider(false)} className="px-4 py-2 rounded-xl bg-slate-100 text-slate-700 text-sm font-medium hover:bg-slate-200">取消</button>
                <button onClick={handleAddProvider} disabled={loading} className="px-4 py-2 rounded-xl bg-purple-500 text-white text-sm font-medium hover:bg-purple-600 disabled:opacity-50">
                  {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : '添加'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
