# AI公众号自动写作助手 Pro - 自动部署脚本 (Windows PowerShell)
# 用途：帮助快速配置 GitHub Secrets 和环境变量

$ErrorActionPreference = "Stop"

Write-Host "🚀 AI公众号自动写作助手 Pro - 自动部署配置向导" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green
Write-Host ""

# 检查是否安装了 gh CLI
try {
    gh --version | Out-Null
    Write-Host "✅ GitHub CLI 已就绪" -ForegroundColor Green
} catch {
    Write-Host "❌ 错误：未找到 GitHub CLI (gh)" -ForegroundColor Red
    Write-Host "请先安装 GitHub CLI: https://cli.github.com/" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "安装命令：winget install GitHub.cli" -ForegroundColor Yellow
    exit 1
}

# 检查是否登录
try {
    gh auth status 2>&1 | Out-Null
} catch {
    Write-Host "⚠️  未登录 GitHub，正在进行登录..." -ForegroundColor Yellow
    gh auth login
}

Write-Host ""

# 选择部署方案
Write-Host "📋 请选择部署方案：" -ForegroundColor Cyan
Write-Host "  1) Vercel（推荐，最简单，免费额度大）"
Write-Host "  2) Railway（支持后台任务）"
Write-Host "  3) 自托管服务器（完全控制）"
Write-Host "  4) 混合部署（Vercel前端 + Railway后台）"
Write-Host ""
$deployChoice = Read-Host "请输入选项 (1-4)"

# 获取仓库名称
$repoInfo = gh repo view --json nameWithOwner | ConvertFrom-Json
$repoName = $repoInfo.nameWithOwner

switch ($deployChoice) {
    "1" {
        Write-Host "✨ 你选择了 Vercel 部署" -ForegroundColor Green
        Write-Host ""
        Write-Host "📝 需要配置以下环境变量：" -ForegroundColor Cyan
        Write-Host ""

        $openaiKey = Read-Host "OPENAI_API_KEY (OpenAI API密钥)"
        $wechatId = Read-Host "WECHAT_APP_ID (微信公众号AppID)"
        $wechatSecret = Read-Host "WECHAT_APP_SECRET (微信公众号密钥)"

        # 生成 SECRET_KEY
        $secretKey = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 64 | ForEach-Object {[char]$_})
        Write-Host "✅ 已自动生成 SECRET_KEY: $secretKey" -ForegroundColor Green

        Write-Host ""
        Write-Host "🎯 下一步操作：" -ForegroundColor Cyan
        Write-Host "1. 访问：https://vercel.com/new/clone?repository-url=https://github.com/$repoName"
        Write-Host "2. 在 Vercel 中配置以下环境变量："
        Write-Host "   OPENAI_API_KEY=$openaiKey" -ForegroundColor Yellow
        Write-Host "   WECHAT_APP_ID=$wechatId" -ForegroundColor Yellow
        Write-Host "   WECHAT_APP_SECRET=$wechatSecret" -ForegroundColor Yellow
        Write-Host "   SECRET_KEY=$secretKey" -ForegroundColor Yellow
        Write-Host "3. 在 Vercel Storage 中添加 Postgres 和 Redis"
        Write-Host ""
        Write-Host "💡 提示：以后只需 git push，Vercel 会自动部署！" -ForegroundColor Cyan

        # 复制配置到剪贴板
        $config = @"
OPENAI_API_KEY=$openaiKey
WECHAT_APP_ID=$wechatId
WECHAT_APP_SECRET=$wechatSecret
SECRET_KEY=$secretKey
"@
        $config | Set-Clipboard
        Write-Host "📋 环境变量已复制到剪贴板！" -ForegroundColor Green
    }

    "2" {
        Write-Host "✨ 你选择了 Railway 部署" -ForegroundColor Green
        Write-Host ""
        Write-Host "📝 需要配置以下环境变量：" -ForegroundColor Cyan
        Write-Host ""

        $openaiKey = Read-Host "OPENAI_API_KEY"
        $wechatId = Read-Host "WECHAT_APP_ID"
        $wechatSecret = Read-Host "WECHAT_APP_SECRET"

        $secretKey = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 64 | ForEach-Object {[char]$_})
        Write-Host "✅ 已自动生成 SECRET_KEY: $secretKey" -ForegroundColor Green

        Write-Host ""
        Write-Host "🎯 下一步操作：" -ForegroundColor Cyan
        Write-Host "1. 访问：https://railway.app/new/template?template=https://github.com/$repoName"
        Write-Host "2. Railway 会自动创建 Postgres 和 Redis"
        Write-Host "3. 配置以下环境变量："
        Write-Host "   OPENAI_API_KEY=$openaiKey" -ForegroundColor Yellow
        Write-Host "   WECHAT_APP_ID=$wechatId" -ForegroundColor Yellow
        Write-Host "   WECHAT_APP_SECRET=$wechatSecret" -ForegroundColor Yellow
        Write-Host "   SECRET_KEY=$secretKey" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "💡 提示：以后只需 git push，Railway 会自动部署！" -ForegroundColor Cyan

        # 复制配置到剪贴板
        $config = @"
OPENAI_API_KEY=$openaiKey
WECHAT_APP_ID=$wechatId
WECHAT_APP_SECRET=$wechatSecret
SECRET_KEY=$secretKey
"@
        $config | Set-Clipboard
        Write-Host "📋 环境变量已复制到剪贴板！" -ForegroundColor Green
    }

    "3" {
        Write-Host "✨ 你选择了自托管服务器部署" -ForegroundColor Green
        Write-Host ""
        Write-Host "📝 需要配置 GitHub Secrets 用于自动部署" -ForegroundColor Cyan
        Write-Host ""

        $serverHost = Read-Host "服务器 IP 地址"
        $serverUser = Read-Host "SSH 用户名 (如 root)"
        $sshKeyPath = Read-Host "SSH 私钥路径 (如 C:\Users\YourName\.ssh\id_rsa)"

        # 读取 SSH 私钥
        if (-not (Test-Path $sshKeyPath)) {
            Write-Host "❌ SSH 私钥文件不存在: $sshKeyPath" -ForegroundColor Red
            exit 1
        }
        $sshKey = Get-Content $sshKeyPath -Raw

        # 可选：Docker Hub 配置
        $useDocker = Read-Host "是否需要推送到 Docker Hub? (y/n)"
        if ($useDocker -eq "y") {
            $dockerUser = Read-Host "Docker Hub 用户名"
            $dockerPass = Read-Host "Docker Hub 密码/Token" -AsSecureString
            $dockerPassPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($dockerPass))
        }

        # 设置 GitHub Secrets
        Write-Host ""
        Write-Host "🔐 正在设置 GitHub Secrets..." -ForegroundColor Cyan

        gh secret set SERVER_HOST -b $serverHost
        gh secret set SERVER_USER -b $serverUser
        gh secret set SERVER_SSH_KEY -b $sshKey

        if ($useDocker -eq "y") {
            gh secret set DOCKER_USERNAME -b $dockerUser
            gh secret set DOCKER_PASSWORD -b $dockerPassPlain
        }

        Write-Host "✅ GitHub Secrets 配置完成！" -ForegroundColor Green
        Write-Host ""
        Write-Host "🎯 下一步操作：" -ForegroundColor Cyan
        Write-Host "1. SSH 登录到服务器: ssh $serverUser@$serverHost"
        Write-Host "2. 安装 Docker: curl -fsSL https://get.docker.com | sh"
        Write-Host "3. 创建 .env 文件并配置环境变量"
        Write-Host "4. 推送代码到 main 分支触发自动部署"
        Write-Host ""
        Write-Host "💡 提示：以后只需 git push origin main，GitHub Actions 会自动部署到服务器！" -ForegroundColor Cyan
    }

    "4" {
        Write-Host "✨ 你选择了混合部署（最佳实践！）" -ForegroundColor Green
        Write-Host ""
        Write-Host "📝 配置说明：" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "前端 + API → Vercel："
        Write-Host "  访问：https://vercel.com/new/clone?repository-url=https://github.com/$repoName"
        Write-Host ""
        Write-Host "后台任务 → Railway："
        Write-Host "  访问：https://railway.app/new/template?template=https://github.com/$repoName"
        Write-Host ""
        Write-Host "💡 这种方案结合了两者的优势：" -ForegroundColor Cyan
        Write-Host "  - Vercel：全球 CDN，快速响应"
        Write-Host "  - Railway：长期运行任务，无冷启动"
    }

    default {
        Write-Host "❌ 无效的选项" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "==================================================" -ForegroundColor Green
Write-Host "🎉 配置完成！" -ForegroundColor Green
Write-Host ""
Write-Host "📚 更多信息请查看：" -ForegroundColor Cyan
Write-Host "  - 部署指南：./DEPLOY.md"
Write-Host "  - 项目文档：./README.md"
Write-Host ""
Write-Host "💬 遇到问题？提交 Issue：" -ForegroundColor Cyan
Write-Host "  https://github.com/$repoName/issues"
Write-Host ""
