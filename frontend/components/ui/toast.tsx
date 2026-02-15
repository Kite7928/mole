'use client'

import { useState, useEffect } from 'react'
import { CheckCircle2, XCircle, AlertCircle, Info, X } from 'lucide-react'

export type ToastType = 'success' | 'error' | 'warning' | 'info'

export interface Toast {
  id: string
  type: ToastType
  message: string
  duration?: number
}

interface ToastProps {
  toast: Toast
  onClose: (id: string) => void
}

export function ToastItem({ toast, onClose }: ToastProps) {
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    // 动画进入
    setIsVisible(true)

    // 自动关闭
    const timer = setTimeout(() => {
      setIsVisible(false)
      setTimeout(() => onClose(toast.id), 300)
    }, toast.duration || 3000)

    return () => clearTimeout(timer)
  }, [toast.id, toast.duration, onClose])

  const icons = {
    success: <CheckCircle2 className="text-green-600" size={20} />,
    error: <XCircle className="text-red-600" size={20} />,
    warning: <AlertCircle className="text-orange-600" size={20} />,
    info: <Info className="text-blue-600" size={20} />,
  }

  const bgColors = {
    success: 'bg-green-50 border-green-200',
    error: 'bg-red-50 border-red-200',
    warning: 'bg-orange-50 border-orange-200',
    info: 'bg-blue-50 border-blue-200',
  }

  return (
    <div
      className={`
        flex items-center gap-3 p-4 rounded-lg border shadow-lg
        transition-all duration-300 transform
        ${bgColors[toast.type]}
        ${isVisible ? 'translate-x-0 opacity-100' : 'translate-x-full opacity-0'}
      `}
    >
      {icons[toast.type]}
      <p className="flex-1 text-sm font-medium text-gray-900">{toast.message}</p>
      <button
        onClick={() => onClose(toast.id)}
        className="p-1 hover:bg-black/5 rounded-lg transition-colors"
      >
        <X size={16} className="text-gray-600" />
      </button>
    </div>
  )
}

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([])

  const addToast = (type: ToastType, message: string, duration?: number) => {
    const id = Math.random().toString(36).substr(2, 9)
    setToasts((prev) => [...prev, { id, type, message, duration }])
  }

  const removeToast = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id))
  }

  // 将添加和删除方法挂载到 window 对象上，方便全局调用
  useEffect(() => {
    ;(window as any).toast = {
      success: (message: string, duration?: number) => addToast('success', message, duration),
      error: (message: string, duration?: number) => addToast('error', message, duration),
      warning: (message: string, duration?: number) => addToast('warning', message, duration),
      info: (message: string, duration?: number) => addToast('info', message, duration),
    }
  }, [])

  return (
    <>
      {children}
      <div className="fixed top-4 right-4 z-50 space-y-2">
        {toasts.map((toast) => (
          <ToastItem key={toast.id} toast={toast} onClose={removeToast} />
        ))}
      </div>
    </>
  )
}