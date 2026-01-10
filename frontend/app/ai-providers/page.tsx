'use client'

import { useState, useEffect } from 'react'
import { 
  Bot, 
  Settings, 
  RefreshCw, 
  CheckCircle2, 
  XCircle, 
  Clock,
  Zap,
  Shuffle,
  ArrowRight,
  Activity,
  Cpu
} from 'lucide-react'

interface Provider {
  name: string
  display_name: string
  available: boolean
  default_model: string | null
}

interface ProvidersResponse {
  providers: Provider[]
  current_strategy: string
  enabled_providers: string[]
}

export default function AIProvidersPage() {
  const [providers, setProviders] = useState<Provider[]>([])
  const [currentStrategy, setCurrentStrategy] = useState<string>('sequential')
  const [loading, setLoading] = useState(true)
  const [testingProvider, setTestingProvider] = useState<string | null>(null)
  const [testResults, setTestResults] = useState<Record<string, any>>({})

  useEffect(() => {
    fetchProviders()
  }, [])

  const fetchProviders = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/ai/providers')
      const data: ProvidersResponse = await response.json()
      setProviders(data.providers)
      setCurrentStrategy(data.current_strategy)
    } catch (error) {
      console.error('Failed to fetch providers:', error)
    } finally {
      setLoading(false)
    }
  }

  const testProvider = async (providerName: string) => {
    setTestingProvider(providerName)
    try {
      const response = await fetch(`http://localhost:8000/api/ai/test-provider?provider=${providerName}`)
      const data = await response.json()
      setTestResults(prev => ({
        ...prev,
        [providerName]: data
      }))
    } catch (error) {
      setTestResults(prev => ({
        ...prev,
        [providerName]: { available: false, error: 'Connection error' }
      }))
    } finally {
      setTestingProvider(null)
    }
  }

  const setRotationStrategy = async (strategy: string) => {
    try {
      await fetch('http://localhost:8000/api/ai/rotation-strategy', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ strategy })
      })
      setCurrentStrategy(strategy)
    } catch (error) {
      console.error('Failed to set rotation strategy:', error)
    }
  }

  const getProviderIcon = (name: string) => {
    const icons: Record<string, any> = {
      openai: <Bot className="w-6 h-6" />,
      deepseek: <Zap className="w-6 h-6" />,
      claude: <Activity className="w-6 h-6" />,
      gemini: <Cpu className="w-6 h-6" />,
      qwen: <Bot className="w-6 h-6" />,
      moonshot: <Bot className="w-6 h-6" />,
      ollama: <Bot className="w-6 h-6" />,
      volcengine: <Zap className="w-6 h-6" />,
      alibaba_bailian: <Bot className="w-6 h-6" />,
      siliconflow: <Bot className="w-6 h-6" />,
      openrouter: <Bot className="w-6 h-6" />
    }
    return icons[name] || <Bot className="w-6 h-6" />
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-12 h-12 animate-spin text-indigo-600 mx-auto mb-4" />
          <p className="text-slate-600 dark:text-slate-400">加载中...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
      {/* Header */}
      <header className="bg-white/80 dark:bg-slate-800/80 backdrop-blur-xl border-b border-slate-200 dark:border-slate-700 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-600 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/30">
                <Bot className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
                  AI模型提供商管理
                </h1>
                <p className="text-sm text-slate-600 dark:text-slate-400">
                  统一管理多个AI模型提供商
                </p>
              </div>
            </div>
            <button
              onClick={fetchProviders}
              className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg transition-colors"
            >
              <RefreshCw size={18} />
              刷新
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* 轮询策略设置 */}
        <div className="mb-8 bg-white/95 dark:bg-slate-800/95 backdrop-blur-xl rounded-2xl p-6 border border-slate-200 dark:border-slate-700 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <Settings className="w-6 h-6 text-indigo-600" />
              <h2 className="text-lg font-semibold text-slate-900 dark:text-white">
                轮询策略
              </h2>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-sm text-slate-600 dark:text-slate-400">
                当前策略:
              </span>
              <span className="px-3 py-1 bg-indigo-100 dark:bg-indigo-500/20 text-indigo-600 dark:text-indigo-400 rounded-full text-sm font-medium">
                {currentStrategy === 'sequential' ? '顺序轮询' : '随机轮询'}
              </span>
            </div>
          </div>
          <div className="flex gap-3">
            <button
              onClick={() => setRotationStrategy('sequential')}
              disabled={currentStrategy === 'sequential'}
              className={`flex-1 flex items-center justify-center gap-2 px-6 py-3 rounded-xl transition-all ${
                currentStrategy === 'sequential'
                  ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-lg shadow-indigo-500/30'
                  : 'bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600'
              }`}
            >
              <Clock size={20} />
              <span className="font-medium">顺序轮询</span>
            </button>
            <button
              onClick={() => setRotationStrategy('random')}
              disabled={currentStrategy === 'random'}
              className={`flex-1 flex items-center justify-center gap-2 px-6 py-3 rounded-xl transition-all ${
                currentStrategy === 'random'
                  ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-lg shadow-indigo-500/30'
                  : 'bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600'
              }`}
            >
              <Shuffle size={20} />
              <span className="font-medium">随机轮询</span>
            </button>
          </div>
        </div>

        {/* 提供商列表 */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {providers.map((provider) => {
            const result = testResults[provider.name]
            return (
              <div
                key={provider.name}
                className="bg-white/95 dark:bg-slate-800/95 backdrop-blur-xl rounded-2xl p-6 border border-slate-200 dark:border-slate-700 shadow-sm hover:shadow-lg hover:shadow-indigo-500/10 transition-all duration-300 hover:-translate-y-1"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-500/20 to-purple-500/20 dark:from-indigo-500/10 dark:to-purple-500/10 flex items-center justify-center text-indigo-600 dark:text-indigo-400">
                      {getProviderIcon(provider.name)}
                    </div>
                    <div>
                      <h3 className="font-semibold text-slate-900 dark:text-white">
                        {provider.display_name}
                      </h3>
                      <p className="text-xs text-slate-500 dark:text-slate-400">
                        {provider.default_model || '未配置'}
                      </p>
                    </div>
                  </div>
                  {provider.available ? (
                    <CheckCircle2 className="w-5 h-5 text-green-500" />
                  ) : (
                    <XCircle className="w-5 h-5 text-red-500" />
                  )}
                </div>

                {result && (
                  <div className="mb-4 p-3 rounded-lg bg-slate-50 dark:bg-slate-700/50">
                    {result.available ? (
                      <div className="text-sm">
                        <p className="text-green-600 dark:text-green-400 font-medium mb-1">
                          ✓ 连接成功
                        </p>
                        <p className="text-slate-600 dark:text-slate-400 text-xs">
                          模型: {result.model}
                        </p>
                        <p className="text-slate-600 dark:text-slate-400 text-xs">
                          Token: {result.token_usage?.total_tokens || 0}
                        </p>
                      </div>
                    ) : (
                      <p className="text-sm text-red-600 dark:text-red-400">
                        ✗ {result.error || '连接失败'}
                      </p>
                    )}
                  </div>
                )}

                <div className="flex gap-2">
                  <button
                    onClick={() => testProvider(provider.name)}
                    disabled={testingProvider === provider.name || !provider.available}
                    className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-300 dark:disabled:bg-slate-600 text-white rounded-lg transition-colors text-sm font-medium"
                  >
                    {testingProvider === provider.name ? (
                      <RefreshCw size={16} className="animate-spin" />
                    ) : (
                      <Activity size={16} />
                    )}
                    测试
                  </button>
                  <button className="px-4 py-2 bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 dark:hover:bg-slate-600 text-slate-700 dark:text-slate-300 rounded-lg transition-colors">
                    <Settings size={16} />
                  </button>
                </div>
              </div>
            )
          })}
        </div>

        {/* 统计信息 */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white/95 dark:bg-slate-800/95 backdrop-blur-xl rounded-2xl p-6 border border-slate-200 dark:border-slate-700 shadow-sm">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-slate-600 dark:text-slate-400">
                可用提供商
              </span>
              <CheckCircle2 className="w-5 h-5 text-green-500" />
            </div>
            <p className="text-3xl font-bold text-slate-900 dark:text-white">
              {providers.filter(p => p.available).length}
            </p>
          </div>
          <div className="bg-white/95 dark:bg-slate-800/95 backdrop-blur-xl rounded-2xl p-6 border border-slate-200 dark:border-slate-700 shadow-sm">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-slate-600 dark:text-slate-400">
                总提供商数
              </span>
              <Bot className="w-5 h-5 text-indigo-600" />
            </div>
            <p className="text-3xl font-bold text-slate-900 dark:text-white">
              {providers.length}
            </p>
          </div>
          <div className="bg-white/95 dark:bg-slate-800/95 backdrop-blur-xl rounded-2xl p-6 border border-slate-200 dark:border-slate-700 shadow-sm">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-slate-600 dark:text-slate-400">
                轮询策略
              </span>
              <ArrowRight className="w-5 h-5 text-purple-600" />
            </div>
            <p className="text-3xl font-bold text-slate-900 dark:text-white">
              {currentStrategy === 'sequential' ? '顺序' : '随机'}
            </p>
          </div>
        </div>
      </main>
    </div>
  )
}