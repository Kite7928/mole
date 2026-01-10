'use client'

import { useState } from 'react'
import { Search, Bell, User, Sun, Moon, X } from 'lucide-react'
import { useStore } from '@/lib/store'
import { useThemeStore } from '@/lib/theme-store'

export default function Header() {
  const { notifications, removeNotification } = useStore()
  const { theme, toggleTheme } = useThemeStore()
  const [showNotifications, setShowNotifications] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (searchQuery.trim()) {
      window.location.href = `/articles?search=${encodeURIComponent(searchQuery)}`
    }
  }

  return (
    <header 
      className="h-16 border-b flex items-center justify-between px-4 lg:px-6 transition-all duration-300"
      style={{
        background: 'linear-gradient(90deg, rgba(99, 102, 241, 0.08) 0%, rgba(139, 92, 246, 0.08) 100%)',
        backdropFilter: 'blur(20px)',
        borderColor: 'rgba(99, 102, 241, 0.1)'
      }}
    >
      {/* 搜索框 */}
      <form onSubmit={handleSearch} className="flex-1 max-w-md mx-4 lg:mx-0">
        <div className="relative">
          <Search size={20} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 dark:text-slate-500" />
          <input
            type="text"
            placeholder="搜索文章、热点..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-white/80 dark:bg-slate-700/80 border border-slate-300 dark:border-slate-600 focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition-all text-slate-800 dark:text-slate-200 placeholder-slate-500 dark:placeholder-slate-500"
          />
        </div>
      </form>

      {/* 右侧操作区 */}
      <div className="flex items-center gap-3">
        {/* 主题切换 */}
        <button
          onClick={toggleTheme}
          className="p-2.5 rounded-xl hover:bg-white/50 dark:hover:bg-slate-700 transition-colors text-slate-700 dark:text-slate-300 touch-friendly"
          title={theme === 'dark' ? '切换到日间模式' : '切换到夜间模式'}
        >
          {theme === 'dark' ? <Sun size={22} /> : <Moon size={22} />}
        </button>

        {/* 通知 */}
        <div className="relative">
          <button
            onClick={() => setShowNotifications(!showNotifications)}
            className="p-2.5 rounded-xl hover:bg-white/50 dark:hover:bg-slate-700 transition-colors text-slate-700 dark:text-slate-300 touch-friendly"
          >
            <Bell size={22} />
            {notifications.length > 0 && (
              <span className="absolute top-1 right-1 w-5 h-5 bg-gradient-to-r from-indigo-600 to-purple-600 text-white text-xs rounded-full flex items-center justify-center font-bold shadow-lg shadow-indigo-500/30">
                {notifications.length}
              </span>
            )}
          </button>

          {/* 通知下拉 */}
          {showNotifications && (
            <div className="absolute right-0 mt-2 w-80 bg-white/95 dark:bg-slate-800/95 backdrop-blur-xl border border-slate-200 dark:border-slate-700 rounded-xl shadow-xl z-50 overflow-hidden">
              <div className="p-3 border-b border-slate-200 dark:border-slate-700 flex items-center justify-between">
                <h3 className="font-semibold text-slate-900 dark:text-white text-base">通知</h3>
                <button
                  onClick={() => setShowNotifications(false)}
                  className="p-1 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors"
                >
                  <X size={18} className="text-slate-400 dark:text-slate-500" />
                </button>
              </div>
              <div className="max-h-96 overflow-y-auto">
                {notifications.length === 0 ? (
                  <div className="p-6 text-center text-slate-400 dark:text-slate-500">
                    <p className="text-sm">暂无通知</p>
                  </div>
                ) : (
                  notifications.map((notification) => (
                    <div
                      key={notification.id}
                      className={`p-4 border-b border-slate-200/50 dark:border-slate-700/50 ${
                        notification.type === 'success' ? 'bg-emerald-50/50 dark:bg-emerald-500/10' :
                        notification.type === 'error' ? 'bg-red-50/50 dark:bg-red-500/10' :
                        notification.type === 'warning' ? 'bg-amber-50/50 dark:bg-amber-500/10' :
                        'bg-blue-50/50 dark:bg-blue-500/10'
                      }`}
                    >
                      <div className="flex items-start justify-between gap-3">
                        <div className="flex-1">
                          <p className="text-sm text-slate-900 dark:text-white font-medium">{notification.message}</p>
                          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                            {new Date(notification.timestamp).toLocaleString('zh-CN')}
                          </p>
                        </div>
                        <button
                          onClick={() => removeNotification(notification.id)}
                          className="p-1 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors flex-shrink-0"
                        >
                          <X size={16} className="text-slate-400 dark:text-slate-500" />
                        </button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>

        {/* 用户头像 */}
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-600 to-purple-600 flex items-center justify-center text-white font-bold shadow-lg shadow-indigo-500/30">
          U
        </div>
      </div>
    </header>
  )
}