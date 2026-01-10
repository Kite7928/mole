'use client'

import { useState } from 'react'
import { 
  BarChart3, 
  Brain, 
  Image as ImageIcon, 
  Github, 
  TrendingUp, 
  Search, 
  Zap, 
  GitPullRequest,
  Activity,
  Settings,
  CheckCircle
} from 'lucide-react'

export default function IntegrationsPage() {
  const [activeTab, setActiveTab] = useState('data-analysis')

  const tabs = [
    { id: 'data-analysis', name: '数据分析', icon: BarChart3 },
    { id: 'domestic-ai', name: '国内AI', icon: Brain },
    { id: 'image-generation', name: '图片生成', icon: ImageIcon },
    { id: 'github', name: 'GitHub', icon: Github },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
      {/* Header */}
      <div className="border-b bg-white/80 dark:bg-slate-800/80 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-slate-900 dark:text-white mb-2">
                API 集成管理
              </h1>
              <p className="text-slate-600 dark:text-slate-400">
                管理和配置所有第三方API集成
              </p>
            </div>
            <button className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl hover:shadow-lg hover:shadow-indigo-500/30 transition-all duration-300">
              <Settings size={20} />
              配置API
            </button>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="max-w-7xl mx-auto px-6 py-6">
        <div className="flex gap-2 mb-8 overflow-x-auto pb-2">
          {tabs.map((tab) => {
            const Icon = tab.icon
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-3 px-6 py-3 rounded-xl transition-all duration-300 whitespace-nowrap ${
                  activeTab === tab.id
                    ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-lg shadow-indigo-500/30'
                    : 'bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 border border-slate-200 dark:border-slate-700'
                }`}
              >
                <Icon size={20} />
                <span className="font-semibold">{tab.name}</span>
              </button>
            )
          })}
        </div>

        {/* Content */}
        <div className="space-y-6">
          {activeTab === 'data-analysis' && <DataAnalysisSection />}
          {activeTab === 'domestic-ai' && <DomesticAISection />}
          {activeTab === 'image-generation' && <ImageGenerationSection />}
          {activeTab === 'github' && <GitHubSection />}
        </div>
      </div>
    </div>
  )
}

// 数据分析部分
function DataAnalysisSection() {
  return (
    <div className="space-y-6">
      {/* 百度指数 */}
      <div className="bg-white/95 dark:bg-slate-800/95 backdrop-blur-xl rounded-2xl p-6 border border-slate-200 dark:border-slate-700 shadow-sm">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500/20 to-blue-600/20 flex items-center justify-center">
              <TrendingUp className="text-blue-600 dark:text-blue-400" size={24} />
            </div>
            <div>
              <h3 className="text-xl font-bold text-slate-900 dark:text-white">百度指数</h3>
              <p className="text-sm text-slate-600 dark:text-slate-400">获取关键词搜索趋势数据</p>
            </div>
          </div>
          <div className="flex items-center gap-2 px-4 py-2 bg-green-100 dark:bg-green-500/10 rounded-lg">
            <CheckCircle className="text-green-600 dark:text-green-400" size={16} />
            <span className="text-sm font-medium text-green-600 dark:text-green-400">已配置</span>
          </div>
        </div>

        <div className="space-y-4">
          <div className="flex gap-3">
            <input
              type="text"
              placeholder="输入关键词（多个关键词用逗号分隔）"
              className="flex-1 px-4 py-3 rounded-xl bg-slate-100 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition-all text-slate-900 dark:text-white"
            />
            <button className="px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-xl hover:shadow-lg hover:shadow-blue-500/30 transition-all duration-300 font-medium">
              <Search size={20} />
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
            <div className="p-4 rounded-xl bg-blue-50 dark:bg-blue-500/10 border border-blue-200 dark:border-blue-500/20">
              <p className="text-sm text-slate-600 dark:text-slate-400 mb-1">平均指数</p>
              <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">1,234</p>
            </div>
            <div className="p-4 rounded-xl bg-green-50 dark:bg-green-500/10 border border-green-200 dark:border-green-500/20">
              <p className="text-sm text-slate-600 dark:text-slate-400 mb-1">趋势</p>
              <p className="text-2xl font-bold text-green-600 dark:text-green-400">↑ 15%</p>
            </div>
            <div className="p-4 rounded-xl bg-purple-50 dark:bg-purple-500/10 border border-purple-200 dark:border-purple-500/20">
              <p className="text-sm text-slate-600 dark:text-slate-400 mb-1">峰值</p>
              <p className="text-2xl font-bold text-purple-600 dark:text-purple-400">2,456</p>
            </div>
          </div>
        </div>
      </div>

      {/* 微信指数 */}
      <div className="bg-white/95 dark:bg-slate-800/95 backdrop-blur-xl rounded-2xl p-6 border border-slate-200 dark:border-slate-700 shadow-sm">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-green-500/20 to-green-600/20 flex items-center justify-center">
              <Activity className="text-green-600 dark:text-green-400" size={24} />
            </div>
            <div>
              <h3 className="text-xl font-bold text-slate-900 dark:text-white">微信指数</h3>
              <p className="text-sm text-slate-600 dark:text-slate-400">获取微信生态内关键词热度</p>
            </div>
          </div>
          <div className="flex items-center gap-2 px-4 py-2 bg-yellow-100 dark:bg-yellow-500/10 rounded-lg">
            <span className="text-sm font-medium text-yellow-600 dark:text-yellow-400">未配置</span>
          </div>
        </div>

        <div className="space-y-4">
          <div className="flex gap-3">
            <input
              type="text"
              placeholder="输入关键词（多个关键词用逗号分隔）"
              className="flex-1 px-4 py-3 rounded-xl bg-slate-100 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition-all text-slate-900 dark:text-white"
            />
            <button className="px-6 py-3 bg-gradient-to-r from-green-600 to-green-700 text-white rounded-xl hover:shadow-lg hover:shadow-green-500/30 transition-all duration-300 font-medium">
              <Search size={20} />
            </button>
          </div>
        </div>
      </div>

      {/* 微博热搜 */}
      <div className="bg-white/95 dark:bg-slate-800/95 backdrop-blur-xl rounded-2xl p-6 border border-slate-200 dark:border-slate-700 shadow-sm">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-orange-500/20 to-orange-600/20 flex items-center justify-center">
              <Zap className="text-orange-600 dark:text-orange-400" size={24} />
            </div>
            <div>
              <h3 className="text-xl font-bold text-slate-900 dark:text-white">微博热搜</h3>
              <p className="text-sm text-slate-600 dark:text-slate-400">实时获取微博热门话题</p>
            </div>
          </div>
          <button className="px-4 py-2 bg-gradient-to-r from-orange-600 to-orange-700 text-white rounded-lg hover:shadow-lg hover:shadow-orange-500/30 transition-all duration-300 text-sm font-medium">
            刷新热搜
          </button>
        </div>

        <div className="space-y-3">
          {[
            { title: '人工智能', score: 98, trend: 'up' },
            { title: 'ChatGPT', score: 92, trend: 'stable' },
            { title: '科技创新', score: 87, trend: 'up' },
            { title: '数字化转型', score: 82, trend: 'down' },
          ].map((item, index) => (
            <div key={index} className="flex items-center justify-between p-4 rounded-xl bg-orange-50 dark:bg-orange-500/5 border border-orange-200 dark:border-orange-500/20 hover:bg-orange-100 dark:hover:bg-orange-500/10 transition-all cursor-pointer">
              <div className="flex items-center gap-4">
                <span className="text-lg font-bold text-orange-600 dark:text-orange-400 w-8">{index + 1}</span>
                <span className="font-medium text-slate-900 dark:text-white">{item.title}</span>
              </div>
              <div className="flex items-center gap-3">
                <span className="px-3 py-1 rounded-full bg-white dark:bg-slate-700 text-sm font-medium text-orange-600 dark:text-orange-400">
                  {item.score}
                </span>
                {item.trend === 'up' && <TrendingUp className="text-green-600 dark:text-green-400" size={16} />}
                {item.trend === 'down' && <TrendingUp className="text-red-600 dark:text-red-400" size={16} style={{ transform: 'rotate(180deg)' }} />}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

// 国内AI部分
function DomesticAISection() {
  return (
    <div className="space-y-6">
      <div className="bg-white/95 dark:bg-slate-800/95 backdrop-blur-xl rounded-2xl p-6 border border-slate-200 dark:border-slate-700 shadow-sm">
        <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-6">国内AI模型</h3>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[
            { name: '通义千问', provider: 'qwen', status: 'active', color: 'purple' },
            { name: 'ChatGPT', provider: 'gpt-4', status: 'active', color: 'green' },
            { name: 'Gemini', provider: 'gemini', status: 'active', color: 'blue' },
          ].map((model) => (
            <div key={model.provider} className="p-6 rounded-xl bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-700/50 dark:to-slate-800/50 border border-slate-200 dark:border-slate-700 hover:shadow-lg hover:shadow-indigo-500/10 transition-all duration-300">
              <div className="flex items-center justify-between mb-4">
                <Brain className={`text-${model.color}-600 dark:text-${model.color}-400`} size={32} />
                <div className={`px-3 py-1 rounded-full text-xs font-medium ${
                  model.status === 'active'
                    ? 'bg-green-100 dark:bg-green-500/10 text-green-600 dark:text-green-400'
                    : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-400'
                }`}>
                  {model.status === 'active' ? '已启用' : '未启用'}
                </div>
              </div>
              <h4 className="text-lg font-bold text-slate-900 dark:text-white mb-2">{model.name}</h4>
              <p className="text-sm text-slate-600 dark:text-slate-400 mb-4">
                {model.provider === 'qwen' && '阿里云通义千问大语言模型'}
                {model.provider === 'gpt-4' && 'OpenAI的GPT-4模型'}
                {model.provider === 'gemini' && 'Google的Gemini Pro模型'}
              </p>
              <button className="w-full py-2 rounded-lg bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-medium hover:shadow-lg hover:shadow-indigo-500/30 transition-all duration-300">
                测试模型
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

// 图片生成部分
function ImageGenerationSection() {
  return (
    <div className="space-y-6">
      <div className="bg-white/95 dark:bg-slate-800/95 backdrop-blur-xl rounded-2xl p-6 border border-slate-200 dark:border-slate-700 shadow-sm">
        <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-6">图片生成服务</h3>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[
            { name: 'DALL-E', provider: 'dalle', status: 'active', color: 'green' },
            { name: 'Midjourney', provider: 'midjourney', status: 'inactive', color: 'purple' },
            { name: 'Stable Diffusion', provider: 'stable-diffusion', status: 'inactive', color: 'blue' },
          ].map((service) => (
            <div key={service.provider} className="p-6 rounded-xl bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-700/50 dark:to-slate-800/50 border border-slate-200 dark:border-slate-700 hover:shadow-lg hover:shadow-indigo-500/10 transition-all duration-300">
              <div className="flex items-center justify-between mb-4">
                <ImageIcon className={`text-${service.color}-600 dark:text-${service.color}-400`} size={32} />
                <div className={`px-3 py-1 rounded-full text-xs font-medium ${
                  service.status === 'active'
                    ? 'bg-green-100 dark:bg-green-500/10 text-green-600 dark:text-green-400'
                    : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-400'
                }`}>
                  {service.status === 'active' ? '已启用' : '未启用'}
                </div>
              </div>
              <h4 className="text-lg font-bold text-slate-900 dark:text-white mb-2">{service.name}</h4>
              <p className="text-sm text-slate-600 dark:text-slate-400 mb-4">
                {service.provider === 'dalle' && 'OpenAI的文本到图像生成模型'}
                {service.provider === 'midjourney' && '强大的AI图像生成工具'}
                {service.provider === 'stable-diffusion' && '开源的图像生成模型'}
              </p>
              <button className="w-full py-2 rounded-lg bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-medium hover:shadow-lg hover:shadow-indigo-500/30 transition-all duration-300">
                生成图片
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

// GitHub部分
function GitHubSection() {
  return (
    <div className="space-y-6">
      <div className="bg-white/95 dark:bg-slate-800/95 backdrop-blur-xl rounded-2xl p-6 border border-slate-200 dark:border-slate-700 shadow-sm">
        <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-6">GitHub集成</h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div className="p-6 rounded-xl bg-gradient-to-br from-slate-800 to-slate-900 text-white">
            <div className="flex items-center justify-between mb-4">
              <Github size={32} />
              <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-green-500/20 text-green-400 text-xs font-medium">
                <CheckCircle size={12} />
                已连接
              </div>
            </div>
            <h4 className="text-lg font-bold mb-2">mole</h4>
            <p className="text-sm text-slate-400 mb-4">AI公众号自动写作助手</p>
            <div className="grid grid-cols-3 gap-4">
              <div>
                <p className="text-2xl font-bold">156</p>
                <p className="text-xs text-slate-400">Stars</p>
              </div>
              <div>
                <p className="text-2xl font-bold">42</p>
                <p className="text-xs text-slate-400">Forks</p>
              </div>
              <div>
                <p className="text-2xl font-bold">18</p>
                <p className="text-xs text-slate-400">Issues</p>
              </div>
            </div>
          </div>

          <div className="space-y-3">
            <button className="w-full p-4 rounded-xl bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 dark:hover:bg-slate-600 transition-all text-left">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <GitPullRequest className="text-purple-600 dark:text-purple-400" size={20} />
                  <span className="font-medium text-slate-900 dark:text-white">创建Pull Request</span>
                </div>
                <span className="text-slate-600 dark:text-slate-400">→</span>
              </div>
            </button>
            <button className="w-full p-4 rounded-xl bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 dark:hover:bg-slate-600 transition-all text-left">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Search className="text-blue-600 dark:text-blue-400" size={20} />
                  <span className="font-medium text-slate-900 dark:text-white">查看Issues</span>
                </div>
                <span className="text-slate-600 dark:text-slate-400">→</span>
              </div>
            </button>
            <button className="w-full p-4 rounded-xl bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 dark:hover:bg-slate-600 transition-all text-left">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Activity className="text-green-600 dark:text-green-400" size={20} />
                  <span className="font-medium text-slate-900 dark:text-white">查看提交记录</span>
                </div>
                <span className="text-slate-600 dark:text-slate-400">→</span>
              </div>
            </button>
          </div>
        </div>

        <div>
          <h4 className="text-lg font-bold text-slate-900 dark:text-white mb-4">最近的Pull Requests</h4>
          <div className="space-y-3">
            {[
              { title: '集成数据分析API', number: 123, status: 'open', author: 'user1' },
              { title: '优化前端性能', number: 122, status: 'merged', author: 'user2' },
              { title: '修复登录bug', number: 121, status: 'closed', author: 'user3' },
            ].map((pr) => (
              <div key={pr.number} className="flex items-center justify-between p-4 rounded-xl bg-slate-50 dark:bg-slate-700/50 border border-slate-200 dark:border-slate-700">
                <div className="flex items-center gap-4">
                  <GitPullRequest className={
                    pr.status === 'open' ? 'text-green-600 dark:text-green-400' :
                    pr.status === 'merged' ? 'text-purple-600 dark:text-purple-400' :
                    'text-red-600 dark:text-red-400'
                  } size={20} />
                  <div>
                    <p className="font-medium text-slate-900 dark:text-white">{pr.title}</p>
                    <p className="text-sm text-slate-600 dark:text-slate-400">
                      #{pr.number} · {pr.author}
                    </p>
                  </div>
                </div>
                <div className={`px-3 py-1 rounded-full text-xs font-medium ${
                  pr.status === 'open' ? 'bg-green-100 dark:bg-green-500/10 text-green-600 dark:text-green-400' :
                  pr.status === 'merged' ? 'bg-purple-100 dark:bg-purple-500/10 text-purple-600 dark:text-purple-400' :
                  'bg-red-100 dark:bg-red-500/10 text-red-600 dark:text-red-400'
                }`}>
                  {pr.status === 'open' ? 'Open' : pr.status === 'merged' ? 'Merged' : 'Closed'}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}