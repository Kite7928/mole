'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import {
  Calendar,
  ChevronLeft,
  ChevronRight,
  Plus,
  Clock,
  CheckCircle,
  X,
  Filter,
  LayoutGrid,
  List,
  CalendarDays,
  MoreVertical,
  Edit2,
  Trash2,
  ExternalLink,
  Bell,
  Repeat
} from 'lucide-react'
import Link from 'next/link'
import { API_URL } from '@/lib/api'

// 类型定义
interface Schedule {
  id: number
  article_id?: number
  title: string
  description?: string
  scheduled_date: string
  scheduled_time: string
  status: 'draft' | 'scheduled' | 'published' | 'cancelled'
  platform: string
  remind_before: number
  is_reminded: boolean
  article_title?: string
}

interface ScheduleOverview {
  week_scheduled: number
  total_pending: number
  today_scheduled: number
}

const platformColors: Record<string, string> = {
  wechat: 'bg-emerald-500',
  weibo: 'bg-red-500',
  zhihu: 'bg-blue-500',
  xiaohongshu: 'bg-rose-500',
  douyin: 'bg-slate-900',
  bilibili: 'bg-pink-500',
  multi: 'bg-violet-500'
}

const platformNames: Record<string, string> = {
  wechat: '微信',
  weibo: '微博',
  zhihu: '知乎',
  xiaohongshu: '小红书',
  douyin: '抖音',
  bilibili: 'B站',
  multi: '多平台'
}

const statusColors: Record<string, string> = {
  draft: 'bg-slate-400',
  scheduled: 'bg-violet-500',
  published: 'bg-emerald-500',
  cancelled: 'bg-red-400'
}

const statusLabels: Record<string, string> = {
  draft: '草稿',
  scheduled: '已排期',
  published: '已发布',
  cancelled: '已取消'
}

export default function ContentCalendarPage() {
  const router = useRouter()
  const [viewMode, setViewMode] = useState<'month' | 'week' | 'list'>('month')
  const [currentDate, setCurrentDate] = useState(new Date())
  const [schedules, setSchedules] = useState<Schedule[]>([])
  const [overview, setOverview] = useState<ScheduleOverview | null>(null)
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [editingSchedule, setEditingSchedule] = useState<Schedule | null>(null)
  const [selectedDate, setSelectedDate] = useState<string | null>(null)

  // 表单状态
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    scheduled_date: '',
    scheduled_time: '08:00',
    platform: 'wechat',
    remind_before: 30
  })

  useEffect(() => {
    fetchData()
  }, [currentDate, viewMode])

  const fetchData = async () => {
    setLoading(true)
    try {
      // 计算日期范围
      let startDate: Date, endDate: Date
      
      if (viewMode === 'month') {
        startDate = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1)
        endDate = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0)
      } else if (viewMode === 'week') {
        const day = currentDate.getDay()
        const diff = currentDate.getDate() - day + (day === 0 ? -6 : 1)
        startDate = new Date(currentDate.setDate(diff))
        endDate = new Date(startDate)
        endDate.setDate(endDate.getDate() + 6)
      } else {
        // list view - 默认显示未来30天
        startDate = new Date()
        endDate = new Date()
        endDate.setDate(endDate.getDate() + 30)
      }

      const startStr = startDate.toISOString().split('T')[0]
      const endStr = endDate.toISOString().split('T')[0]

      // 获取发布计划
      const response = await fetch(
        `${API_URL}/api/content-strategy/schedules?start_date=${startStr}&end_date=${endStr}`
      )
      if (response.ok) {
        const data = await response.json()
        setSchedules(data)
      }

      // 获取概览
      const overviewResponse = await fetch(`${API_URL}/api/content-strategy/schedules/overview`)
      if (overviewResponse.ok) {
        const data = await overviewResponse.json()
        setOverview(data)
      }
    } catch (error) {
      console.error('获取数据失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const handlePrev = () => {
    const newDate = new Date(currentDate)
    if (viewMode === 'month') {
      newDate.setMonth(newDate.getMonth() - 1)
    } else if (viewMode === 'week') {
      newDate.setDate(newDate.getDate() - 7)
    }
    setCurrentDate(newDate)
  }

  const handleNext = () => {
    const newDate = new Date(currentDate)
    if (viewMode === 'month') {
      newDate.setMonth(newDate.getMonth() + 1)
    } else if (viewMode === 'week') {
      newDate.setDate(newDate.getDate() + 7)
    }
    setCurrentDate(newDate)
  }

  const handleToday = () => {
    setCurrentDate(new Date())
  }

  const openCreateModal = (date?: string) => {
    setEditingSchedule(null)
    setFormData({
      title: '',
      description: '',
      scheduled_date: date || new Date().toISOString().split('T')[0],
      scheduled_time: '08:00',
      platform: 'wechat',
      remind_before: 30
    })
    setShowModal(true)
  }

  const openEditModal = (schedule: Schedule) => {
    setEditingSchedule(schedule)
    setFormData({
      title: schedule.title,
      description: schedule.description || '',
      scheduled_date: schedule.scheduled_date,
      scheduled_time: schedule.scheduled_time,
      platform: schedule.platform,
      remind_before: schedule.remind_before
    })
    setShowModal(true)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const url = editingSchedule
        ? `${API_URL}/api/content-strategy/schedules/${editingSchedule.id}`
        : `${API_URL}/api/content-strategy/schedules`
      
      const method = editingSchedule ? 'PUT' : 'POST'
      
      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      })

      if (response.ok) {
        setShowModal(false)
        fetchData()
      } else {
        alert('保存失败')
      }
    } catch (error) {
      console.error('保存失败:', error)
      alert('保存失败')
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm('确定要删除这个发布计划吗？')) return
    
    try {
      const response = await fetch(`${API_URL}/api/content-strategy/schedules/${id}`, {
        method: 'DELETE'
      })
      
      if (response.ok) {
        fetchData()
      } else {
        alert('删除失败')
      }
    } catch (error) {
      console.error('删除失败:', error)
      alert('删除失败')
    }
  }

  // 获取某天的发布计划
  const getSchedulesForDate = (date: Date) => {
    const dateStr = date.toISOString().split('T')[0]
    return schedules.filter(s => s.scheduled_date === dateStr)
  }

  // 渲染月视图
  const renderMonthView = () => {
    const year = currentDate.getFullYear()
    const month = currentDate.getMonth()
    
    const firstDay = new Date(year, month, 1)
    const lastDay = new Date(year, month + 1, 0)
    const daysInMonth = lastDay.getDate()
    const startDayOfWeek = firstDay.getDay()
    
    const days = []
    
    // 空白天数
    for (let i = 0; i < startDayOfWeek; i++) {
      days.push(<div key={`empty-${i}`} className="h-32 bg-slate-50/50" />)
    }
    
    // 实际天数
    for (let day = 1; day <= daysInMonth; day++) {
      const date = new Date(year, month, day)
      const daySchedules = getSchedulesForDate(date)
      const isToday = new Date().toDateString() === date.toDateString()
      
      days.push(
        <div
          key={day}
          className={`h-32 border border-slate-100 p-2 cursor-pointer transition-colors hover:bg-slate-50 ${
            isToday ? 'bg-violet-50/50' : ''
          }`}
          onClick={() => openCreateModal(date.toISOString().split('T')[0])}
        >
          <div className="flex items-center justify-between mb-1">
            <span className={`text-sm font-medium ${isToday ? 'text-violet-600' : 'text-slate-700'}`}>
              {day}
            </span>
            {isToday && (
              <span className="text-xs px-2 py-0.5 rounded-full bg-violet-100 text-violet-600">
                今天
              </span>
            )}
          </div>
          <div className="space-y-1">
            {daySchedules.slice(0, 3).map(schedule => (
              <div
                key={schedule.id}
                className={`text-xs px-2 py-1 rounded text-white truncate ${platformColors[schedule.platform] || 'bg-slate-400'}`}
                onClick={(e) => {
                  e.stopPropagation()
                  openEditModal(schedule)
                }}
              >
                {schedule.scheduled_time} {schedule.title}
              </div>
            ))}
            {daySchedules.length > 3 && (
              <div className="text-xs text-slate-400 pl-2">
                +{daySchedules.length - 3} 更多
              </div>
            )}
          </div>
        </div>
      )
    }
    
    return (
      <div className="grid grid-cols-7 gap-px bg-slate-200 border border-slate-200 rounded-xl overflow-hidden">
        {['日', '一', '二', '三', '四', '五', '六'].map(day => (
          <div key={day} className="bg-slate-50 py-2 text-center text-sm font-medium text-slate-600">
            {day}
          </div>
        ))}
        {days}
      </div>
    )
  }

  // 渲染周视图
  const renderWeekView = () => {
    const days = []
    const dayNames = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
    
    // 获取本周开始日期
    const startOfWeek = new Date(currentDate)
    const day = startOfWeek.getDay()
    const diff = startOfWeek.getDate() - day + (day === 0 ? -6 : 1)
    startOfWeek.setDate(diff)
    
    for (let i = 0; i < 7; i++) {
      const date = new Date(startOfWeek)
      date.setDate(date.getDate() + i)
      const daySchedules = getSchedulesForDate(date)
      const isToday = new Date().toDateString() === date.toDateString()
      
      days.push(
        <div
          key={i}
          className={`border-l first:border-l-0 border-slate-200 min-h-96 ${isToday ? 'bg-violet-50/30' : ''}`}
        >
          <div className={`p-3 text-center border-b border-slate-200 ${isToday ? 'bg-violet-50' : 'bg-slate-50'}`}>
            <p className={`text-sm font-medium ${isToday ? 'text-violet-600' : 'text-slate-600'}`}>
              {dayNames[date.getDay()]}
            </p>
            <p className={`text-lg font-bold ${isToday ? 'text-violet-700' : 'text-slate-900'}`}>
              {date.getDate()}
            </p>
          </div>
          <div className="p-2 space-y-2">
            {daySchedules.map(schedule => (
              <div
                key={schedule.id}
                className={`p-3 rounded-xl cursor-pointer hover:shadow-md transition-shadow ${platformColors[schedule.platform] || 'bg-slate-400'} text-white`}
                onClick={() => openEditModal(schedule)}
              >
                <p className="font-medium text-sm">{schedule.title}</p>
                <p className="text-xs opacity-90 mt-1">{schedule.scheduled_time}</p>
              </div>
            ))}
            <button
              onClick={() => openCreateModal(date.toISOString().split('T')[0])}
              className="w-full py-2 border-2 border-dashed border-slate-300 rounded-xl text-slate-400 hover:border-violet-400 hover:text-violet-500 transition-colors text-sm"
            >
              + 添加计划
            </button>
          </div>
        </div>
      )
    }
    
    return <div className="grid grid-cols-7 gap-0 bg-white rounded-xl border border-slate-200 overflow-hidden">{days}</div>
  }

  // 渲染列表视图
  const renderListView = () => {
    const sortedSchedules = [...schedules].sort((a, b) => 
      new Date(a.scheduled_date + ' ' + a.scheduled_time).getTime() - 
      new Date(b.scheduled_date + ' ' + b.scheduled_time).getTime()
    )
    
    return (
      <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden">
        <div className="divide-y divide-slate-100">
          {sortedSchedules.map(schedule => (
            <div key={schedule.id} className="p-4 flex items-center gap-4 hover:bg-slate-50 transition-colors">
              <div className={`w-12 h-12 rounded-xl flex items-center justify-center text-white ${platformColors[schedule.platform] || 'bg-slate-400'}`}>
                <CalendarDays className="w-6 h-6" />
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-3">
                  <h4 className="font-medium text-slate-900">{schedule.title}</h4>
                  <span className={`px-2 py-0.5 rounded-full text-xs text-white ${statusColors[schedule.status]}`}>
                    {statusLabels[schedule.status]}
                  </span>
                  {schedule.remind_before > 0 && (
                    <span className="flex items-center gap-1 text-xs text-slate-500">
                      <Bell className="w-3 h-3" />
                      提前{schedule.remind_before}分钟提醒
                    </span>
                  )}
                </div>
                <div className="flex items-center gap-4 text-sm text-slate-500 mt-1">
                  <span>{schedule.scheduled_date} {schedule.scheduled_time}</span>
                  <span>•</span>
                  <span>{platformNames[schedule.platform]}</span>
                  {schedule.article_title && (
                    <>
                      <span>•</span>
                      <span className="text-violet-600">关联文章: {schedule.article_title}</span>
                    </>
                  )}
                </div>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => openEditModal(schedule)}
                  className="p-2 rounded-lg hover:bg-slate-200 text-slate-500 transition-colors"
                >
                  <Edit2 className="w-4 h-4" />
                </button>
                <button
                  onClick={() => handleDelete(schedule.id)}
                  className="p-2 rounded-lg hover:bg-red-50 text-slate-500 hover:text-red-500 transition-colors"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
          {sortedSchedules.length === 0 && (
            <div className="p-12 text-center text-slate-400">
              <Calendar className="w-16 h-16 mx-auto mb-4 opacity-30" />
              <p>暂无发布计划</p>
              <button
                onClick={() => openCreateModal()}
                className="mt-4 px-4 py-2 bg-violet-500 text-white rounded-xl text-sm hover:bg-violet-600 transition-colors"
              >
                创建第一个计划
              </button>
            </div>
          )}
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-50">
      {/* 头部 */}
      <div className="bg-white border-b border-slate-200 sticky top-0 z-30">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center">
                <Calendar className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-semibold text-slate-900">内容日历</h1>
                <p className="text-sm text-slate-500">规划和管理您的内容发布计划</p>
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              {/* 视图切换 */}
              <div className="flex bg-slate-100 rounded-xl p-1">
                {[
                  { id: 'month', label: '月', icon: LayoutGrid },
                  { id: 'week', label: '周', icon: CalendarDays },
                  { id: 'list', label: '列表', icon: List }
                ].map((view) => (
                  <button
                    key={view.id}
                    onClick={() => setViewMode(view.id as any)}
                    className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                      viewMode === view.id
                        ? 'bg-white text-violet-600 shadow-sm'
                        : 'text-slate-600 hover:text-slate-900'
                    }`}
                  >
                    <view.icon className="w-4 h-4" />
                    {view.label}
                  </button>
                ))}
              </div>
              
              <button
                onClick={() => openCreateModal()}
                className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-violet-500 to-purple-600 text-white text-sm font-medium hover:opacity-90 transition-opacity"
              >
                <Plus className="w-4 h-4" />
                新建计划
              </button>
            </div>
          </div>
        </div>
        
        {/* 日期导航 */}
        <div className="max-w-7xl mx-auto px-6 pb-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <button
                  onClick={handlePrev}
                  className="p-2 rounded-xl hover:bg-slate-100 text-slate-600 transition-colors"
                >
                  <ChevronLeft className="w-5 h-5" />
                </button>
                <h2 className="text-lg font-semibold text-slate-900 min-w-[140px] text-center">
                  {currentDate.getFullYear()}年{currentDate.getMonth() + 1}月
                </h2>
                <button
                  onClick={handleNext}
                  className="p-2 rounded-xl hover:bg-slate-100 text-slate-600 transition-colors"
                >
                  <ChevronRight className="w-5 h-5" />
                </button>
              </div>
              <button
                onClick={handleToday}
                className="px-3 py-1.5 rounded-lg bg-slate-100 text-slate-600 text-sm font-medium hover:bg-slate-200 transition-colors"
              >
                今天
              </button>
            </div>
            
            {/* 统计概览 */}
            {overview && (
              <div className="flex items-center gap-4 text-sm">
                <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-violet-50 text-violet-700">
                  <Clock className="w-4 h-4" />
                  今日 {overview.today_scheduled} 条
                </div>
                <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-blue-50 text-blue-700">
                  <Calendar className="w-4 h-4" />
                  本周 {overview.week_scheduled} 条
                </div>
                <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-emerald-50 text-emerald-700">
                  <CheckCircle className="w-4 h-4" />
                  待发布 {overview.total_pending} 条
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* 主内容区 */}
      <div className="max-w-7xl mx-auto px-6 py-6">
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="w-8 h-8 border-2 border-violet-500 border-t-transparent rounded-full animate-spin" />
          </div>
        ) : (
          <>
            {viewMode === 'month' && renderMonthView()}
            {viewMode === 'week' && renderWeekView()}
            {viewMode === 'list' && renderListView()}
          </>
        )}
      </div>

      {/* 创建/编辑弹窗 */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" onClick={() => setShowModal(false)} />
          <div className="relative w-full max-w-lg bg-white rounded-2xl shadow-2xl overflow-hidden">
            <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
              <h3 className="text-lg font-semibold text-slate-900">
                {editingSchedule ? '编辑发布计划' : '新建发布计划'}
              </h3>
              <button
                onClick={() => setShowModal(false)}
                className="p-2 rounded-lg hover:bg-slate-100 text-slate-400 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">计划标题</label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => setFormData({...formData, title: e.target.value})}
                  className="w-full px-4 py-2 rounded-xl border border-slate-200 focus:border-violet-400 focus:ring-2 focus:ring-violet-100 outline-none transition-all"
                  placeholder="输入计划标题"
                  required
                />
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">发布日期</label>
                  <input
                    type="date"
                    value={formData.scheduled_date}
                    onChange={(e) => setFormData({...formData, scheduled_date: e.target.value})}
                    className="w-full px-4 py-2 rounded-xl border border-slate-200 focus:border-violet-400 focus:ring-2 focus:ring-violet-100 outline-none transition-all"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">发布时间</label>
                  <input
                    type="time"
                    value={formData.scheduled_time}
                    onChange={(e) => setFormData({...formData, scheduled_time: e.target.value})}
                    className="w-full px-4 py-2 rounded-xl border border-slate-200 focus:border-violet-400 focus:ring-2 focus:ring-violet-100 outline-none transition-all"
                    required
                  />
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">发布平台</label>
                <div className="grid grid-cols-4 gap-2">
                  {Object.entries(platformNames).map(([key, name]) => (
                    <button
                      key={key}
                      type="button"
                      onClick={() => setFormData({...formData, platform: key})}
                      className={`px-3 py-2 rounded-xl text-sm font-medium transition-all ${
                        formData.platform === key
                          ? 'bg-violet-500 text-white'
                          : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                      }`}
                    >
                      {name}
                    </button>
                  ))}
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">提前提醒</label>
                <select
                  value={formData.remind_before}
                  onChange={(e) => setFormData({...formData, remind_before: parseInt(e.target.value)})}
                  className="w-full px-4 py-2 rounded-xl border border-slate-200 focus:border-violet-400 focus:ring-2 focus:ring-violet-100 outline-none transition-all"
                >
                  <option value={0}>不提醒</option>
                  <option value={15}>15分钟前</option>
                  <option value={30}>30分钟前</option>
                  <option value={60}>1小时前</option>
                  <option value={1440}>1天前</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">备注（可选）</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({...formData, description: e.target.value})}
                  className="w-full px-4 py-2 rounded-xl border border-slate-200 focus:border-violet-400 focus:ring-2 focus:ring-violet-100 outline-none transition-all resize-none h-20"
                  placeholder="添加备注信息..."
                />
              </div>
              
              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="flex-1 px-4 py-2.5 rounded-xl border border-slate-200 text-slate-700 font-medium hover:bg-slate-50 transition-colors"
                >
                  取消
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-2.5 rounded-xl bg-gradient-to-r from-violet-500 to-purple-600 text-white font-medium hover:opacity-90 transition-opacity"
                >
                  {editingSchedule ? '保存修改' : '创建计划'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
