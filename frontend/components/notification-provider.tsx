/**
 * WebSocket实时通知系统
 * 支持文章生成完成、发布成功等实时通知
 */

'use client'

import { createContext, useContext, useEffect, useState, useCallback, ReactNode } from 'react'
import { Bell, CheckCircle, AlertCircle, Info, X } from 'lucide-react'

// 通知类型
type NotificationType = 'success' | 'error' | 'info' | 'warning'

// 通知数据
interface Notification {
  id: string
  type: NotificationType
  title: string
  message: string
  timestamp: Date
  read: boolean
  action?: {
    label: string
    onClick: () => void
  }
}

// 上下文类型
interface NotificationContextType {
  notifications: Notification[]
  unreadCount: number
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp' | 'read'>) => void
  markAsRead: (id: string) => void
  markAllAsRead: () => void
  removeNotification: (id: string) => void
  clearAll: () => void
  isConnected: boolean
}

const NotificationContext = createContext<NotificationContextType | null>(null)

export function useNotifications() {
  const context = useContext(NotificationContext)
  if (!context) {
    throw new Error('useNotifications must be used within NotificationProvider')
  }
  return context
}

interface NotificationProviderProps {
  children: ReactNode
  wsUrl?: string
}

export function NotificationProvider({ 
  children, 
  wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws'
}: NotificationProviderProps) {
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [isConnected, setIsConnected] = useState(false)
  const [ws, setWs] = useState<WebSocket | null>(null)

  // 初始化WebSocket连接
  useEffect(() => {
    const connectWebSocket = () => {
      try {
        const socket = new WebSocket(wsUrl)

        socket.onopen = () => {
          console.log('WebSocket已连接')
          setIsConnected(true)
        }

        socket.onclose = () => {
          console.log('WebSocket已断开')
          setIsConnected(false)
          // 3秒后重连
          setTimeout(connectWebSocket, 3000)
        }

        socket.onerror = (error) => {
          console.error('WebSocket错误:', error)
          setIsConnected(false)
        }

        socket.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data)
            handleWebSocketMessage(data)
          } catch (error) {
            console.error('解析WebSocket消息失败:', error)
          }
        }

        setWs(socket)
      } catch (error) {
        console.error('WebSocket连接失败:', error)
        setIsConnected(false)
      }
    }

    connectWebSocket()

    return () => {
      if (ws) {
        ws.close()
      }
    }
  }, [wsUrl])

  // 处理WebSocket消息
  const handleWebSocketMessage = (data: any) => {
    switch (data.type) {
      case 'article_generated':
        addNotification({
          type: 'success',
          title: '文章生成完成',
          message: `文章"${data.title}"已成功生成`,
          action: {
            label: '查看',
            onClick: () => window.open(`/articles/create?id=${data.articleId}`, '_blank')
          }
        })
        break
      
      case 'publish_success':
        addNotification({
          type: 'success',
          title: '发布成功',
          message: `文章已发布到${data.platform}`,
        })
        break
      
      case 'publish_failed':
        addNotification({
          type: 'error',
          title: '发布失败',
          message: data.message || '发布过程中出现错误',
        })
        break
      
      case 'hotspot_updated':
        addNotification({
          type: 'info',
          title: '热点更新',
          message: `发现${data.count}条新的热门话题`,
        })
        break
      
      default:
        console.log('未知消息类型:', data.type)
    }
  }

  // 添加通知
  const addNotification = useCallback((notification: Omit<Notification, 'id' | 'timestamp' | 'read'>) => {
    const newNotification: Notification = {
      ...notification,
      id: Date.now().toString(),
      timestamp: new Date(),
      read: false
    }

    setNotifications(prev => [newNotification, ...prev])

    // 自动移除成功通知（5秒后）
    if (notification.type === 'success') {
      setTimeout(() => {
        removeNotification(newNotification.id)
      }, 5000)
    }
  }, [])

  // 标记为已读
  const markAsRead = useCallback((id: string) => {
    setNotifications(prev =>
      prev.map(n => n.id === id ? { ...n, read: true } : n)
    )
  }, [])

  // 标记全部已读
  const markAllAsRead = useCallback(() => {
    setNotifications(prev => prev.map(n => ({ ...n, read: true })))
  }, [])

  // 移除通知
  const removeNotification = useCallback((id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id))
  }, [])

  // 清空所有通知
  const clearAll = useCallback(() => {
    setNotifications([])
  }, [])

  // 未读数量
  const unreadCount = notifications.filter(n => !n.read).length

  return (
    <NotificationContext.Provider
      value={{
        notifications,
        unreadCount,
        addNotification,
        markAsRead,
        markAllAsRead,
        removeNotification,
        clearAll,
        isConnected
      }}
    >
      {children}
      <NotificationCenter />
    </NotificationContext.Provider>
  )
}

// 通知中心组件
function NotificationCenter() {
  const { 
    notifications, 
    unreadCount, 
    markAsRead, 
    markAllAsRead, 
    removeNotification,
    isConnected 
  } = useNotifications()
  const [isOpen, setIsOpen] = useState(false)

  return (
    <div className="fixed top-4 right-4 z-50">
      {/* 通知按钮 */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 bg-white rounded-full shadow-lg hover:shadow-xl transition-shadow"
      >
        <Bell className="w-6 h-6 text-gray-600" />
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
            {unreadCount > 99 ? '99+' : unreadCount}
          </span>
        )}
        {/* 连接状态指示器 */}
        <span 
          className={`absolute bottom-0 right-0 w-3 h-3 rounded-full border-2 border-white ${
            isConnected ? 'bg-green-500' : 'bg-red-500'
          }`}
        />
      </button>

      {/* 通知面板 */}
      {isOpen && (
        <div className="absolute top-full right-0 mt-2 w-80 bg-white rounded-lg shadow-xl border border-gray-200 max-h-96 overflow-hidden">
          {/* 头部 */}
          <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200">
            <h3 className="font-medium text-gray-900">通知中心</h3>
            <div className="flex items-center gap-2">
              {unreadCount > 0 && (
                <button
                  onClick={markAllAsRead}
                  className="text-xs text-blue-600 hover:text-blue-700"
                >
                  全部已读
                </button>
              )}
              <button
                onClick={() => setIsOpen(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* 通知列表 */}
          <div className="max-h-80 overflow-y-auto">
            {notifications.length === 0 ? (
              <div className="p-8 text-center text-gray-500">
                <Bell className="w-12 h-12 mx-auto mb-2 text-gray-300" />
                <p>暂无通知</p>
              </div>
            ) : (
              notifications.map(notification => (
                <div
                  key={notification.id}
                  className={`p-4 border-b border-gray-100 hover:bg-gray-50 transition-colors ${
                    !notification.read ? 'bg-blue-50/50' : ''
                  }`}
                  onClick={() => markAsRead(notification.id)}
                >
                  <div className="flex items-start gap-3">
                    {getNotificationIcon(notification.type)}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-2">
                        <h4 className="font-medium text-gray-900 text-sm">
                          {notification.title}
                        </h4>
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            removeNotification(notification.id)
                          }}
                          className="text-gray-400 hover:text-gray-600"
                        >
                          <X className="w-3 h-3" />
                        </button>
                      </div>
                      <p className="text-sm text-gray-600 mt-1">
                        {notification.message}
                      </p>
                      <div className="flex items-center justify-between mt-2">
                        <span className="text-xs text-gray-400">
                          {formatTime(notification.timestamp)}
                        </span>
                        {notification.action && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              notification.action?.onClick()
                            }}
                            className="text-xs text-blue-600 hover:text-blue-700 font-medium"
                          >
                            {notification.action.label}
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  )
}

// 获取通知图标
function getNotificationIcon(type: NotificationType) {
  switch (type) {
    case 'success':
      return <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0" />
    case 'error':
      return <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
    case 'warning':
      return <AlertCircle className="w-5 h-5 text-yellow-500 flex-shrink-0" />
    case 'info':
    default:
      return <Info className="w-5 h-5 text-blue-500 flex-shrink-0" />
  }
}

// 格式化时间
function formatTime(date: Date): string {
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 30) return `${days}天前`
  return date.toLocaleDateString('zh-CN')
}
