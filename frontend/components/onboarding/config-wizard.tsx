'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { 
  ChevronRight, 
  ChevronLeft, 
  CheckCircle2, 
  Key, 
  MessageSquare, 
  Sparkles,
  AlertCircle,
  Eye,
  EyeOff,
  Save
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { API_URL } from '@/lib/api'

interface WizardStep {
  id: string
  title: string
  description: string
  icon: React.ReactNode
}

const steps: WizardStep[] = [
  {
    id: 'ai',
    title: '配置 AI 服务',
    description: '选择并配置你的 AI 提供商',
    icon: <Sparkles className="w-5 h-5" />
  },
  {
    id: 'wechat',
    title: '配置微信公众号',
    description: '绑定微信公众号实现一键发布',
    icon: <MessageSquare className="w-5 h-5" />
  },
  {
    id: 'complete',
    title: '完成配置',
    description: '开始你的 AI 写作之旅',
    icon: <CheckCircle2 className="w-5 h-5" />
  }
]

const DEV88_DEFAULT_MODEL = 'gpt-5-nano [渠道id:33][輸出3k上限]'

export function ConfigWizard() {
  const router = useRouter()
  const [currentStep, setCurrentStep] = useState(0)
  const [showWizard, setShowWizard] = useState(false)
  const [loading, setLoading] = useState(false)
  const [showSecrets, setShowSecrets] = useState<Record<string, boolean>>({})
  
  // 配置状态
  const [config, setConfig] = useState({
    aiProvider: 'openai',
    apiKey: '',
    baseUrl: 'https://api.dev88.tech/v1',
    model: DEV88_DEFAULT_MODEL,
    wechatAppId: '',
    wechatAppSecret: '',
  })

  useEffect(() => {
    // 检查是否需要显示向导
    const checkConfig = async () => {
      try {
        const response = await fetch(`${API_URL}/api/config`)
        if (response.ok) {
          const data = await response.json()
          const hasAI = !!(data.config?.api_key || data.config?.openai_api_key)
          const hasWechat = !!(data.config?.wechat_app_id && data.config?.wechat_app_secret)
          
          // 如果没有完整配置，显示向导
          if (!hasAI || !hasWechat) {
            setShowWizard(true)
            // 预填充已有配置
            setConfig(prev => ({
              ...prev,
              aiProvider: data.config?.ai_provider || 'openai',
              apiKey: data.config?.api_key || '',
              baseUrl: data.config?.base_url || prev.baseUrl,
              model: data.config?.model || prev.model,
              wechatAppId: data.config?.wechat_app_id || '',
              wechatAppSecret: data.config?.wechat_app_secret || '',
            }))
          }
        }
      } catch (error) {
        console.error('检查配置失败:', error)
      }
    }
    checkConfig()
  }, [])

  const toggleSecret = (key: string) => {
    setShowSecrets(prev => ({ ...prev, [key]: !prev[key] }))
  }

  const handleSave = async () => {
    setLoading(true)
    try {
      const payload: any = {
        ai_provider: config.aiProvider,
        api_key: config.apiKey,
        base_url: config.baseUrl,
        model: config.model,
        wechat_app_id: config.wechatAppId,
        wechat_app_secret: config.wechatAppSecret,
      }

      const response = await fetch(`${API_URL}/api/config`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })

      if (!response.ok) throw new Error('保存失败')
      
      // 进入下一步
      if (currentStep < steps.length - 1) {
        setCurrentStep(prev => prev + 1)
      }
    } catch (error) {
      console.error('保存配置失败:', error)
      alert('保存配置失败，请检查网络连接')
    } finally {
      setLoading(false)
    }
  }

  const handleSkip = () => {
    setShowWizard(false)
  }

  const handleComplete = () => {
    setShowWizard(false)
    router.push('/articles/create')
  }

  if (!showWizard) return null

  const progress = ((currentStep + 1) / steps.length) * 100

  return (
    <Card className="mb-8 border-blue-500/30 bg-gradient-to-r from-blue-500/10 to-purple-500/10">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-500/20 rounded-lg">
              {steps[currentStep].icon}
            </div>
            <div>
              <CardTitle className="text-lg">{steps[currentStep].title}</CardTitle>
              <CardDescription className="text-gray-400">
                {steps[currentStep].description}
              </CardDescription>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-500">
              步骤 {currentStep + 1}/{steps.length}
            </span>
            <button 
              onClick={handleSkip}
              className="p-2 hover:bg-white/10 rounded-lg transition-colors"
            >
              <AlertCircle className="w-4 h-4 text-gray-500" />
            </button>
          </div>
        </div>
        
        {/* 进度条 */}
        <div className="w-full bg-gray-700 rounded-full h-2 mt-4">
          <div 
            className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full transition-all duration-500"
            style={{ width: `${progress}%` }}
          />
        </div>
      </CardHeader>

      <CardContent>
        {/* 步骤 1: AI 配置 */}
        {currentStep === 0 && (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                AI 提供商
              </label>
              <select
                value={config.aiProvider}
                onChange={(e) => {
                  const provider = e.target.value
                  setConfig(prev => ({
                    ...prev,
                    aiProvider: provider,
                    baseUrl: provider === 'openai' 
                      ? 'https://api.dev88.tech/v1'
                      : provider === 'deepseek'
                      ? 'https://api.deepseek.com/v1'
                      : provider === 'gemini'
                      ? 'https://generativelanguage.googleapis.com'
                      : prev.baseUrl
                  }))
                }}
                className="w-full bg-[#1a1d29] border border-white/10 rounded-lg px-4 py-2.5 text-white focus:border-blue-500 focus:outline-none"
              >
                <option value="openai">OpenAI</option>
                <option value="deepseek">DeepSeek</option>
                <option value="gemini">Google Gemini</option>
                <option value="claude">Claude (Anthropic)</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                API Key
              </label>
              <div className="relative">
                <input
                  type={showSecrets.apiKey ? 'text' : 'password'}
                  value={config.apiKey}
                  onChange={(e) => setConfig(prev => ({ ...prev, apiKey: e.target.value }))}
                  placeholder={`输入你的 ${config.aiProvider} API Key`}
                  className="w-full bg-[#1a1d29] border border-white/10 rounded-lg px-4 py-2.5 text-white placeholder-gray-500 focus:border-blue-500 focus:outline-none pr-10"
                />
                <button
                  onClick={() => toggleSecret('apiKey')}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-white"
                >
                  {showSecrets.apiKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
              <p className="text-xs text-gray-500 mt-1">
                你的 API Key 将被安全存储，仅用于调用 AI 服务
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Base URL（可选）
              </label>
              <input
                type="text"
                value={config.baseUrl}
                onChange={(e) => setConfig(prev => ({ ...prev, baseUrl: e.target.value }))}
                placeholder="https://api.dev88.tech/v1"
                className="w-full bg-[#1a1d29] border border-white/10 rounded-lg px-4 py-2.5 text-white placeholder-gray-500 focus:border-blue-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                模型
              </label>
              <input
                type="text"
                value={config.model}
                onChange={(e) => setConfig(prev => ({ ...prev, model: e.target.value }))}
                placeholder={DEV88_DEFAULT_MODEL}
                className="w-full bg-[#1a1d29] border border-white/10 rounded-lg px-4 py-2.5 text-white placeholder-gray-500 focus:border-blue-500 focus:outline-none"
              />
            </div>
          </div>
        )}

        {/* 步骤 2: 微信配置 */}
        {currentStep === 1 && (
          <div className="space-y-4">
            <div className="p-4 bg-yellow-500/10 border border-yellow-500/30 rounded-lg">
              <div className="flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-yellow-400 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-sm text-yellow-200">
                    配置微信公众号需要先在微信公众平台获取 AppID 和 AppSecret。
                  </p>
                  <a 
                    href="https://mp.weixin.qq.com"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-blue-400 hover:underline mt-1 inline-block"
                  >
                    前往微信公众平台 →
                  </a>
                </div>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                AppID
              </label>
              <input
                type="text"
                value={config.wechatAppId}
                onChange={(e) => setConfig(prev => ({ ...prev, wechatAppId: e.target.value }))}
                placeholder="wx1234567890abcdef"
                className="w-full bg-[#1a1d29] border border-white/10 rounded-lg px-4 py-2.5 text-white placeholder-gray-500 focus:border-blue-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                AppSecret
              </label>
              <div className="relative">
                <input
                  type={showSecrets.wechatSecret ? 'text' : 'password'}
                  value={config.wechatAppSecret}
                  onChange={(e) => setConfig(prev => ({ ...prev, wechatAppSecret: e.target.value }))}
                  placeholder="输入你的 AppSecret"
                  className="w-full bg-[#1a1d29] border border-white/10 rounded-lg px-4 py-2.5 text-white placeholder-gray-500 focus:border-blue-500 focus:outline-none pr-10"
                />
                <button
                  onClick={() => toggleSecret('wechatSecret')}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-white"
                >
                  {showSecrets.wechatSecret ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* 步骤 3: 完成 */}
        {currentStep === 2 && (
          <div className="text-center py-8">
            <div className="w-20 h-20 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
              <CheckCircle2 className="w-10 h-10 text-green-400" />
            </div>
            <h3 className="text-xl font-semibold text-white mb-2">配置完成！</h3>
            <p className="text-gray-400 mb-6">
              你已完成所有必要配置，现在可以开始使用 AI 写作功能了
            </p>
            <div className="flex gap-3 justify-center">
              <Button
                variant="outline"
                onClick={() => setShowWizard(false)}
                className="border-white/10"
              >
                留在设置页
              </Button>
              <Button
                onClick={handleComplete}
                className="bg-blue-600 hover:bg-blue-700"
              >
                开始写作
                <ChevronRight className="w-4 h-4 ml-1" />
              </Button>
            </div>
          </div>
        )}

        {/* 底部按钮 */}
        {currentStep < 2 && (
          <div className="flex justify-between mt-6">
            <Button
              variant="outline"
              onClick={() => setCurrentStep(prev => Math.max(0, prev - 1))}
              disabled={currentStep === 0}
              className="border-white/10"
            >
              <ChevronLeft className="w-4 h-4 mr-1" />
              上一步
            </Button>
            
            <div className="flex gap-2">
              <Button
                variant="ghost"
                onClick={handleSkip}
                className="text-gray-500"
              >
                跳过
              </Button>
              <Button
                onClick={handleSave}
                disabled={loading || (currentStep === 0 && !config.apiKey)}
                className="bg-blue-600 hover:bg-blue-700"
              >
                {loading ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin mr-2" />
                    保存中...
                  </>
                ) : (
                  <>
                    <Save className="w-4 h-4 mr-2" />
                    {currentStep === steps.length - 2 ? '完成' : '下一步'}
                  </>
                )}
              </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
