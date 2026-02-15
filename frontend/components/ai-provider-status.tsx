'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { API_ENDPOINTS, fetchAPI } from '@/lib/api'
import {
  CheckCircle2,
  XCircle,
  Star,
  Bot,
  RefreshCw,
  AlertCircle,
  ChevronRight,
  Settings,
} from 'lucide-react'

// AI提供商配置接口
interface AIProvider {
  provider: string
  name: string
  description: string
  icon: string
  has_api_key: boolean
  is_enabled: boolean
  is_default: boolean
  is_configured: boolean
  model: string
  base_url: string
}

// 状态概览接口
interface StatusOverview {
  total_providers: number
  configured_count: number
  enabled_count: number
  has_recommended: boolean
  recommended_provider: string | null
  recommended_name: string | null
}

export function AIProviderStatus() {
  const [providers, setProviders] = useState<AIProvider[]>([])
  const [overview, setOverview] = useState<StatusOverview | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // 获取配置状态
  const fetchStatus = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await fetchAPI(API_ENDPOINTS.providersStatus)
      if (data.success) {
        setProviders(data.providers || [])
        setOverview(data.overview || null)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '获取配置状态失败')
      console.error('获取AI提供商状态失败:', err)
    } finally {
      setLoading(false)
    }
  }

  // 初始加载
  useEffect(() => {
    fetchStatus()
  }, [])

  // 获取已配置和未配置的提供商
  const configuredProviders = providers.filter((p) => p.has_api_key)
  const unconfiguredProviders = providers.filter((p) => !p.has_api_key)

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Bot className="h-5 w-5" />
            <span>AI提供商配置状态</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <RefreshCw className="h-6 w-6 animate-spin text-muted-foreground" />
            <span className="ml-2 text-muted-foreground">加载中...</span>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Bot className="h-5 w-5" />
            <span>AI提供商配置状态</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center space-x-2 text-destructive">
            <AlertCircle className="h-5 w-5" />
            <span>{error}</span>
          </div>
          <Button onClick={fetchStatus} variant="outline" size="sm" className="mt-4">
            <RefreshCw className="mr-2 h-4 w-4" />
            重试
          </Button>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Bot className="h-5 w-5" />
            <CardTitle>AI提供商配置状态</CardTitle>
          </div>
          <Button onClick={fetchStatus} variant="ghost" size="sm">
            <RefreshCw className="h-4 w-4" />
          </Button>
        </div>
        <CardDescription>
          查看和管理您的AI提供商配置，已配置的提供商会优先推荐
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* 状态概览 */}
        {overview && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-muted/50 p-4 rounded-lg text-center">
              <div className="text-2xl font-bold text-primary">{overview.total_providers}</div>
              <div className="text-sm text-muted-foreground">支持提供商</div>
            </div>
            <div className="bg-green-50 dark:bg-green-950/20 p-4 rounded-lg text-center">
              <div className="text-2xl font-bold text-green-600">{overview.configured_count}</div>
              <div className="text-sm text-muted-foreground">已配置</div>
            </div>
            <div className="bg-blue-50 dark:bg-blue-950/20 p-4 rounded-lg text-center">
              <div className="text-2xl font-bold text-blue-600">{overview.enabled_count}</div>
              <div className="text-sm text-muted-foreground">已启用</div>
            </div>
            <div className="bg-purple-50 dark:bg-purple-950/20 p-4 rounded-lg text-center">
              <div className="text-2xl font-bold text-purple-600">
                {overview.has_recommended ? '✓' : '-'}
              </div>
              <div className="text-sm text-muted-foreground">
                {overview.has_recommended ? overview.recommended_name : '未设置'}
              </div>
            </div>
          </div>
        )}

        {/* 推荐提供商 */}
        {overview?.has_recommended && (
          <div className="bg-gradient-to-r from-purple-50 to-blue-50 dark:from-purple-950/20 dark:to-blue-950/20 border border-purple-200 dark:border-purple-800 p-4 rounded-lg">
            <div className="flex items-center space-x-3">
              <div className="bg-purple-100 dark:bg-purple-900 p-2 rounded-full">
                <Star className="h-5 w-5 text-purple-600 dark:text-purple-400" />
              </div>
              <div className="flex-1">
                <h4 className="font-medium text-purple-900 dark:text-purple-100">
                  推荐提供商: {overview.recommended_name}
                </h4>
                <p className="text-sm text-purple-700 dark:text-purple-300">
                  系统将优先使用此提供商进行AI内容生成
                </p>
              </div>
              <Button variant="outline" size="sm" asChild>
                <a href="/settings">
                  <Settings className="mr-2 h-4 w-4" />
                  配置
                </a>
              </Button>
            </div>
          </div>
        )}

        {/* 已配置的提供商 */}
        {configuredProviders.length > 0 && (
          <div>
            <h4 className="text-sm font-medium mb-3 flex items-center">
              <CheckCircle2 className="mr-2 h-4 w-4 text-green-600" />
              已配置的提供商 ({configuredProviders.length})
            </h4>
            <div className="space-y-2">
              {configuredProviders.map((provider) => (
                <div
                  key={provider.provider}
                  className={`flex items-center justify-between p-3 rounded-lg border ${
                    provider.is_default
                      ? 'bg-purple-50 dark:bg-purple-950/20 border-purple-200 dark:border-purple-800'
                      : 'bg-green-50 dark:bg-green-950/20 border-green-200 dark:border-green-800'
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <span className="text-xl">{provider.icon}</span>
                    <div>
                      <div className="flex items-center space-x-2">
                        <span className="font-medium">{provider.name}</span>
                        {provider.is_default && (
                          <Badge variant="default" className="text-xs">
                            <Star className="mr-1 h-3 w-3" />
                            默认
                          </Badge>
                        )}
                        {provider.is_enabled ? (
                          <Badge variant="secondary" className="text-xs">
                            已启用
                          </Badge>
                        ) : (
                          <Badge variant="outline" className="text-xs">
                            已禁用
                          </Badge>
                        )}
                      </div>
                      <div className="text-sm text-muted-foreground">
                        {provider.description} • {provider.model}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <CheckCircle2 className="h-5 w-5 text-green-600" />
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 未配置的提供商 */}
        {unconfiguredProviders.length > 0 && (
          <div>
            <h4 className="text-sm font-medium mb-3 flex items-center">
              <XCircle className="mr-2 h-4 w-4 text-muted-foreground" />
              未配置的提供商 ({unconfiguredProviders.length})
            </h4>
            <div className="space-y-2">
              {unconfiguredProviders.map((provider) => (
                <div
                  key={provider.provider}
                  className="flex items-center justify-between p-3 rounded-lg border bg-muted/30 border-muted"
                >
                  <div className="flex items-center space-x-3">
                    <span className="text-xl">{provider.icon}</span>
                    <div>
                      <div className="font-medium">{provider.name}</div>
                      <div className="text-sm text-muted-foreground">{provider.description}</div>
                    </div>
                  </div>
                  <Button variant="ghost" size="sm" asChild>
                    <a href="/settings" className="flex items-center">
                      去配置
                      <ChevronRight className="ml-1 h-4 w-4" />
                    </a>
                  </Button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 无配置提示 */}
        {configuredProviders.length === 0 && (
          <div className="bg-yellow-50 dark:bg-yellow-950/20 border border-yellow-200 dark:border-yellow-800 p-4 rounded-lg">
            <div className="flex items-start space-x-3">
              <AlertCircle className="h-5 w-5 text-yellow-600 dark:text-yellow-400 mt-0.5" />
              <div>
                <h4 className="font-medium text-yellow-900 dark:text-yellow-100">尚未配置AI提供商</h4>
                <p className="text-sm text-yellow-700 dark:text-yellow-300 mt-1">
                  您需要先配置至少一个AI提供商才能使用AI写作功能。点击下方按钮前往设置页面。
                </p>
                <Button className="mt-3" size="sm" asChild>
                  <a href="/settings">前往配置</a>
                </Button>
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

export default AIProviderStatus