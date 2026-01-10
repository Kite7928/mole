'use client'

import { useState } from 'react'
import { Sun, Moon, X } from 'lucide-react'
import { useThemeStore } from '@/lib/theme-store'

export default function BrightnessControl() {
  const { theme, brightness, setBrightness, toggleTheme } = useThemeStore()
  const [isOpen, setIsOpen] = useState(false)

  const handleBrightnessChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newBrightness = parseInt(e.target.value)
    setBrightness(newBrightness)
  }

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="p-2.5 rounded-xl hover:bg-slate-200 dark:hover:bg-slate-800 transition-colors light:text-slate-700 dark:text-slate-300 light:hover:text-slate-900 dark:hover:text-white touch-friendly"
        title="亮度调节"
      >
        {theme === 'dark' ? <Sun size={22} /> : <Moon size={22} />}
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-72 light:bg-white dark:bg-slate-800 border light:border-slate-200 dark:border-slate-700 rounded-xl shadow-2xl z-50 p-4">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold light:text-slate-900 dark:text-white text-base">亮度调节</h3>
            <button
              onClick={() => setIsOpen(false)}
              className="p-1 hover:bg-slate-200 dark:hover:bg-slate-700 rounded-lg transition-colors"
            >
              <X size={18} className="light:text-slate-400 dark:text-slate-400" />
            </button>
          </div>

          {/* 主题切换 */}
          <div className="flex items-center justify-between mb-4 p-3 rounded-xl light:bg-green-50 dark:bg-slate-700">
            <span className="text-sm light:text-slate-700 dark:text-slate-300">主题模式</span>
            <button
              onClick={toggleTheme}
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-green-500 text-white hover:bg-green-600 transition-colors"
            >
              {theme === 'dark' ? (
                <>
                  <Moon size={16} />
                  <span className="text-sm">夜间</span>
                </>
              ) : (
                <>
                  <Sun size={16} />
                  <span className="text-sm">日间</span>
                </>
              )}
            </button>
          </div>

          {/* 亮度滑块 */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm light:text-slate-700 dark:text-slate-300">屏幕亮度</span>
              <span className="text-sm font-medium light:text-slate-900 dark:text-white">{brightness}%</span>
            </div>
            <div className="relative">
                      <input
                        type="range"
                        min="0"
                        max="100"
                        value={brightness}
                        onChange={handleBrightnessChange}
                        className="w-full h-2 light:bg-green-200 dark:bg-slate-600 rounded-lg appearance-none cursor-pointer accent-green-500"
                      />
                      <div className="absolute top-1/2 -translate-y-1/2 left-0 w-full h-1 light:bg-green-300 dark:bg-slate-500 rounded-lg pointer-events-none" />
                    </div>            <div className="flex items-center justify-between text-xs light:text-slate-400 dark:text-slate-400">
              <span>暗</span>
              <span>标准</span>
              <span>亮</span>
            </div>
          </div>

          {/* 快捷预设 */}
          <div className="grid grid-cols-3 gap-2 mt-4">
            <button
              onClick={() => setBrightness(30)}
              className={`px-3 py-2 rounded-lg text-xs font-medium transition-all ${
                brightness === 30
                  ? 'bg-green-500 text-white'
                  : 'light:bg-green-50 dark:bg-slate-700 light:text-green-700 dark:text-slate-300 hover:light:bg-green-100 dark:hover:bg-slate-600'
              }`}
            >
              30%
            </button>
            <button
              onClick={() => setBrightness(50)}
              className={`px-3 py-2 rounded-lg text-xs font-medium transition-all ${
                brightness === 50
                  ? 'bg-green-500 text-white'
                  : 'light:bg-green-50 dark:bg-slate-700 light:text-green-700 dark:text-slate-300 hover:light:bg-green-100 dark:hover:bg-slate-600'
              }`}
            >
              50%
            </button>
            <button
              onClick={() => setBrightness(70)}
              className={`px-3 py-2 rounded-lg text-xs font-medium transition-all ${
                brightness === 70
                  ? 'bg-green-500 text-white'
                  : 'light:bg-green-50 dark:bg-slate-700 light:text-green-700 dark:text-slate-300 hover:light:bg-green-100 dark:hover:bg-slate-600'
              }`}
            >
              70%
            </button>
          </div>
        </div>
      )}
    </div>
  )
}