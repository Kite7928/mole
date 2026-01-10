'use client'

import { useStore } from '@/lib/store'
import { 
  CheckCircle, 
  XCircle, 
  Info, 
  AlertTriangle, 
  X 
} from 'lucide-react'
import { useEffect } from 'react'

export default function Notifications() {
  const { notifications, removeNotification } = useStore()

  useEffect(() => {
    // 自动移除通知
    notifications.forEach(notification => {
      const timer = setTimeout(() => {
        removeNotification(notification.id)
      }, 5000)
      return () => clearTimeout(timer)
    })
  }, [notifications, removeNotification])

  const getIcon = (type: string) => {
    switch (type) {
      case 'success':
        return <CheckCircle size={20} className="text-green-400" />
      case 'error':
        return <XCircle size={20} className="text-red-400" />
      case 'warning':
        return <AlertTriangle size={20} className="text-yellow-400" />
      default:
        return <Info size={20} className="text-blue-400" />
    }
  }

  const getBgColor = (type: string) => {
    switch (type) {
      case 'success':
        return 'bg-green-500/10 border-green-500/30'
      case 'error':
        return 'bg-red-500/10 border-red-500/30'
      case 'warning':
        return 'bg-yellow-500/10 border-yellow-500/30'
      default:
        return 'bg-blue-500/10 border-blue-500/30'
    }
  }

  return (
    <div className="fixed top-4 right-4 z-50 space-y-2 max-w-sm w-full">
      {notifications.map((notification) => (
        <div
          key={notification.id}
          className={`
            flex items-start gap-3 p-4 rounded-xl border backdrop-blur-sm
            animate-in slide-in-from-right-full
            ${getBgColor(notification.type)}
          `}
        >
          <div className="flex-shrink-0 mt-0.5">
            {getIcon(notification.type)}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm text-white">{notification.message}</p>
          </div>
          <button
            onClick={() => removeNotification(notification.id)}
            className="flex-shrink-0 p-1 rounded hover:bg-white/10 transition-colors"
          >
            <X size={16} className="text-white/60" />
          </button>
        </div>
      ))}
    </div>
  )
}