'use client'

import { useEffect, useState, useRef } from 'react'
import { ArrowRight, ArrowLeft, X } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface OnboardingStep {
  id: string
  target: string
  title: string
  content: string
  position?: 'top' | 'bottom' | 'left' | 'right'
}

interface OnboardingTooltipProps {
  step: OnboardingStep
  currentStep: number
  totalSteps: number
  onNext: () => void
  onPrev: () => void
  onSkip: () => void
}

export function OnboardingTooltip({ 
  step, 
  currentStep, 
  totalSteps, 
  onNext, 
  onPrev, 
  onSkip 
}: OnboardingTooltipProps) {
  const [position, setPosition] = useState({ top: 0, left: 0 })
  const [isVisible, setIsVisible] = useState(false)
  const tooltipRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const updatePosition = () => {
      const target = document.querySelector(step.target)
      if (!target) {
        // 如果目标元素不存在，显示在屏幕中央
        setPosition({
          top: window.innerHeight / 2 - 100,
          left: window.innerWidth / 2 - 150
        })
        return
      }

      const targetRect = target.getBoundingClientRect()
      const tooltipRect = tooltipRef.current?.getBoundingClientRect()
      const tooltipWidth = tooltipRect?.width || 320
      const tooltipHeight = tooltipRect?.height || 200

      let top = 0
      let left = 0

      switch (step.position || 'bottom') {
        case 'top':
          top = targetRect.top - tooltipHeight - 16
          left = targetRect.left + (targetRect.width - tooltipWidth) / 2
          break
        case 'bottom':
          top = targetRect.bottom + 16
          left = targetRect.left + (targetRect.width - tooltipWidth) / 2
          break
        case 'left':
          top = targetRect.top + (targetRect.height - tooltipHeight) / 2
          left = targetRect.left - tooltipWidth - 16
          break
        case 'right':
          top = targetRect.top + (targetRect.height - tooltipHeight) / 2
          left = targetRect.right + 16
          break
      }

      // 确保不超出视口
      top = Math.max(16, Math.min(top, window.innerHeight - tooltipHeight - 16))
      left = Math.max(16, Math.min(left, window.innerWidth - tooltipWidth - 16))

      setPosition({ top, left })
    }

    // 延迟显示以等待 DOM 更新
    const timer = setTimeout(() => {
      updatePosition()
      setIsVisible(true)
    }, 100)

    window.addEventListener('resize', updatePosition)
    return () => {
      clearTimeout(timer)
      window.removeEventListener('resize', updatePosition)
    }
  }, [step])

  // 高亮目标元素
  useEffect(() => {
    const target = document.querySelector(step.target)
    if (target) {
      (target as HTMLElement).style.position = 'relative'
      ;(target as HTMLElement).style.zIndex = '60'
      ;(target as HTMLElement).classList.add('onboarding-highlight')
    }

    return () => {
      if (target) {
        ;(target as HTMLElement).style.position = ''
        ;(target as HTMLElement).style.zIndex = ''
        ;(target as HTMLElement).classList.remove('onboarding-highlight')
      }
    }
  }, [step.target])

  return (
    <>
      {/* 遮罩层 */}
      <div className="fixed inset-0 z-40 bg-black/50" onClick={onSkip} />
      
      {/* 提示框 */}
      <div
        ref={tooltipRef}
        className={`fixed z-50 w-80 bg-[#1a1d29] border border-blue-500/30 rounded-xl shadow-2xl transition-all duration-300 ${
          isVisible ? 'opacity-100 scale-100' : 'opacity-0 scale-95'
        }`}
        style={{ top: position.top, left: position.left }}
      >
        {/* 头部 */}
        <div className="flex items-center justify-between p-4 border-b border-white/10">
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-500">
              步骤 {currentStep + 1}/{totalSteps}
            </span>
          </div>
          <button
            onClick={onSkip}
            className="p-1 rounded hover:bg-white/10 transition-colors"
          >
            <X className="w-4 h-4 text-gray-400" />
          </button>
        </div>

        {/* 内容 */}
        <div className="p-4">
          <h3 className="text-lg font-semibold text-white mb-2">{step.title}</h3>
          <p className="text-gray-400 text-sm leading-relaxed">{step.content}</p>
        </div>

        {/* 底部 */}
        <div className="flex items-center justify-between p-4 border-t border-white/10">
          <Button
            variant="ghost"
            size="sm"
            onClick={onSkip}
            className="text-gray-500 hover:text-white"
          >
            跳过
          </Button>
          
          <div className="flex gap-2">
            {currentStep > 0 && (
              <Button
                variant="outline"
                size="sm"
                onClick={onPrev}
                className="border-white/10"
              >
                <ArrowLeft className="w-4 h-4" />
              </Button>
            )}
            <Button
              size="sm"
              onClick={onNext}
              className="bg-blue-600 hover:bg-blue-700"
            >
              {currentStep === totalSteps - 1 ? '完成' : '下一步'}
              {currentStep < totalSteps - 1 && <ArrowRight className="w-4 h-4 ml-1" />}
            </Button>
          </div>
        </div>

        {/* 进度条 */}
        <div className="h-1 bg-white/10 rounded-b-xl overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-blue-500 to-purple-500 transition-all duration-300"
            style={{ width: `${((currentStep + 1) / totalSteps) * 100}%` }}
          />
        </div>
      </div>

      <style jsx global>{`
        .onboarding-highlight {
          box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.5);
          border-radius: 8px;
          animation: pulse-highlight 2s infinite;
        }
        
        @keyframes pulse-highlight {
          0%, 100% {
            box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.5);
          }
          50% {
            box-shadow: 0 0 0 8px rgba(59, 130, 246, 0.3);
          }
        }
      `}</style>
    </>
  )
}
