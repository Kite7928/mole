'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Sparkles, X, ArrowRight, CheckCircle2, PenLine, Zap } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Checkbox } from '@/components/ui/checkbox'

interface OnboardingModalProps {
  isOpen: boolean
  onClose: () => void
  onStart: () => void
}

export function OnboardingModal({ isOpen, onClose, onStart }: OnboardingModalProps) {
  const router = useRouter()
  const [dontShowAgain, setDontShowAgain] = useState(false)

  if (!isOpen) return null

  const features = [
    {
      icon: '✨',
      title: 'AI 智能写作',
      description: '输入主题，3分钟生成高质量文章'
    },
    {
      icon: '🔥',
      title: '热点追踪',
      description: '实时监控全网热点，抓住流量风口'
    },
    {
      icon: '📱',
      title: '一键发布',
      description: '微信公众号自动排版发布'
    },
    {
      icon: '🎨',
      title: '爆款风格',
      description: '10+种写作风格，轻松写出10w+'
    }
  ]

  const handleClose = () => {
    if (dontShowAgain) {
      localStorage.setItem('gzh_onboarding_completed', 'true')
    }
    localStorage.setItem('gzh_has_visited', 'true')
    onClose()
  }

  const handleQuickStart = () => {
    if (dontShowAgain) {
      localStorage.setItem('gzh_onboarding_completed', 'true')
    }
    localStorage.setItem('gzh_has_visited', 'true')
    onClose()
    router.push('/articles/create')
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm">
      <Card className="w-full max-w-2xl mx-4 bg-[#1a1d29] border-white/10">
        <CardHeader className="text-center pb-2">
          <button
            onClick={handleClose}
            className="absolute top-4 right-4 p-2 rounded-lg hover:bg-white/10 transition-colors"
          >
            <X className="w-5 h-5 text-gray-400" />
          </button>
          
          <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg shadow-blue-500/20">
            <Sparkles className="w-10 h-10 text-white" />
          </div>
          
          <CardTitle className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
            欢迎使用 AI 写作助手
          </CardTitle>
          <CardDescription className="text-gray-400 text-lg mt-2">
            专为自媒体创作者打造，让 AI 成为你的内容合伙人
          </CardDescription>
        </CardHeader>
        
        <CardContent>
          <div className="grid grid-cols-2 gap-4 mb-6">
            {features.map((feature, index) => (
              <div 
                key={index}
                className="p-4 rounded-xl bg-white/5 border border-white/10 hover:border-blue-500/30 hover:bg-white/[0.07] transition-all cursor-pointer group"
              >
                <div className="text-3xl mb-2 group-hover:scale-110 transition-transform">{feature.icon}</div>
                <h3 className="font-semibold text-white mb-1">{feature.title}</h3>
                <p className="text-sm text-gray-500">{feature.description}</p>
              </div>
            ))}
          </div>

          {/* 快速入口 */}
          <div className="mb-6 p-4 rounded-xl bg-gradient-to-r from-blue-500/10 to-purple-500/10 border border-blue-500/20">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-blue-500/20 flex items-center justify-center">
                  <Zap className="w-5 h-5 text-blue-400" />
                </div>
                <div>
                  <h4 className="font-medium text-white">想直接开始写作？</h4>
                  <p className="text-sm text-gray-500">跳过引导，立即进入创作模式</p>
                </div>
              </div>
              <Button
                className="bg-blue-600 hover:bg-blue-700"
                onClick={handleQuickStart}
              >
                <PenLine className="w-4 h-4 mr-2" />
                立即写作
              </Button>
            </div>
          </div>

          <div className="flex gap-3">
            <Button
              variant="outline"
              className="flex-1 border-white/10 hover:bg-white/5"
              onClick={handleClose}
            >
              稍后再说
            </Button>
            <Button
              className="flex-1 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
              onClick={onStart}
            >
              开始引导
              <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          </div>

          {/* 不再显示选项 */}
          <div className="mt-4 flex items-center justify-center gap-2">
            <Checkbox
              id="dontShowAgain"
              checked={dontShowAgain}
              onCheckedChange={(checked) => setDontShowAgain(checked as boolean)}
              className="border-gray-600 data-[state=checked]:bg-blue-600"
            />
            <label 
              htmlFor="dontShowAgain" 
              className="text-sm text-gray-500 cursor-pointer hover:text-gray-400"
            >
              不再显示此引导（可在设置中重新开启）
            </label>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
