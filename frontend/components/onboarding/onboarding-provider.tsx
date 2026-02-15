'use client'

import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { OnboardingModal } from './onboarding-modal'
import { OnboardingTooltip } from './onboarding-tooltip'

interface OnboardingStep {
  id: string
  target: string
  title: string
  content: string
  position?: 'top' | 'bottom' | 'left' | 'right'
}

interface OnboardingContextType {
  startOnboarding: (steps: OnboardingStep[]) => void
  stopOnboarding: () => void
  isActive: boolean
  currentStep: number
  totalSteps: number
  nextStep: () => void
  prevStep: () => void
  skipOnboarding: () => void
}

const OnboardingContext = createContext<OnboardingContextType | undefined>(undefined)

export function useOnboarding() {
  const context = useContext(OnboardingContext)
  if (!context) {
    throw new Error('useOnboarding must be used within OnboardingProvider')
  }
  return context
}

interface OnboardingProviderProps {
  children: ReactNode
}

export function OnboardingProvider({ children }: OnboardingProviderProps) {
  const [isActive, setIsActive] = useState(false)
  const [steps, setSteps] = useState<OnboardingStep[]>([])
  const [currentStep, setCurrentStep] = useState(0)
  const [showModal, setShowModal] = useState(false)

  useEffect(() => {
    // 检查是否是首次访问
    const hasCompletedOnboarding = localStorage.getItem('gzh_onboarding_completed')
    const hasVisited = localStorage.getItem('gzh_has_visited')
    
    if (!hasCompletedOnboarding && !hasVisited) {
      // 延迟显示，等待页面完全加载
      const timer = setTimeout(() => {
        setShowModal(true)
      }, 1000)
      return () => clearTimeout(timer)
    }
  }, [])

  const startOnboarding = (newSteps: OnboardingStep[]) => {
    setSteps(newSteps)
    setCurrentStep(0)
    setIsActive(true)
  }

  const stopOnboarding = () => {
    setIsActive(false)
    setSteps([])
    setCurrentStep(0)
    localStorage.setItem('gzh_onboarding_completed', 'true')
  }

  const skipOnboarding = () => {
    stopOnboarding()
    localStorage.setItem('gzh_onboarding_completed', 'true')
  }

  const nextStep = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(prev => prev + 1)
    } else {
      stopOnboarding()
    }
  }

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(prev => prev - 1)
    }
  }

  const handleStartFromModal = () => {
    setShowModal(false)
    // 定义默认的新手引导步骤
    const defaultSteps: OnboardingStep[] = [
      {
        id: 'sidebar',
        target: '[data-tour="sidebar"]',
        title: '导航菜单',
        content: '这里可以访问所有功能：AI写作、热点监控、文章管理等',
        position: 'right'
      },
      {
        id: 'ai-writing',
        target: '[data-tour="ai-writing"]',
        title: 'AI 写作',
        content: '点击这里开始使用 AI 生成文章，支持多种写作风格',
        position: 'bottom'
      },
      {
        id: 'hotspots',
        target: '[data-tour="hotspots"]',
        title: '热点监控',
        content: '查看各平台热门话题，获取创作灵感',
        position: 'bottom'
      },
      {
        id: 'settings',
        target: '[data-tour="settings"]',
        title: '系统设置',
        content: '配置 AI API Key 和微信公众号，启用自动发布功能',
        position: 'top'
      }
    ]
    startOnboarding(defaultSteps)
  }

  return (
    <OnboardingContext.Provider value={{
      startOnboarding,
      stopOnboarding,
      isActive,
      currentStep,
      totalSteps: steps.length,
      nextStep,
      prevStep,
      skipOnboarding
    }}>
      {children}
      
      {/* 引导模态框 */}
      <OnboardingModal 
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        onStart={handleStartFromModal}
      />
      
      {/* 步骤提示 */}
      {isActive && steps[currentStep] && (
        <OnboardingTooltip
          step={steps[currentStep]}
          currentStep={currentStep}
          totalSteps={steps.length}
          onNext={nextStep}
          onPrev={prevStep}
          onSkip={skipOnboarding}
        />
      )}
    </OnboardingContext.Provider>
  )
}
