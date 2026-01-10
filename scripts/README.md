# 🛠️ 部署脚本使用指南

本小姐为你准备了一套完整的自动化部署脚本！(￣▽￣)／

## 📋 脚本列表

### 1. check-server.sh - 服务器环境检查脚本 ⭐

**用途：** 在部署前或部署后检查服务器环境是否满足要求

**何时使用：**
- ✅ 部署前 - 检查服务器是否满足最低要求
- ✅ 部署后 - 验证所有服务是否正常运行
- ✅ 故障排查 - 快速定位环境问题

**使用方法：**

```bash
# 方法 1：本地上传到服务器
scp scripts/check-server.sh your-user@your-server-ip:~/
ssh your-user@your-server-ip
chmod +x ~/check-server.sh
./check-server.sh

# 方法 2：直接在服务器下载
ssh your-user@your-server-ip
curl -O https://raw.githubusercontent.com/Kite7928/mole/main/scripts/check-server.sh
chmod +x check-server.sh
./check-server.sh
```

**检查内容：**
- 操作系统兼容性
- 系统资源（内存/磁盘/CPU）
- 必要软件（Docker/Git/curl）
- 网络和端口
- 防火墙配置
- 项目配置（如果已部署）
- SSH 密钥
- Docker 服务状态
- 服务可访问性

**输出示例：**
```
总检查项: 35
✅ 通过: 32
⚠️  警告: 3
❌ 失败: 0
通过率: 91%
```

---

### 2. setup-server.sh - 一键服务器环境配置脚本

**用途：** 自动配置服务器环境，安装所有必要的软件和依赖

**何时使用：**
- ✅ 第一次部署 - 在全新的服务器上快速配置环境
- ✅ 环境问题 - 当 check-server.sh 检测到多个失败项时

**使用方法：**

```bash
# SSH 登录到服务器
ssh your-user@your-server-ip

# 下载脚本
curl -O https://raw.githubusercontent.com/Kite7928/mole/main/scripts/setup-server.sh

# 添加执行权限
chmod +x setup-server.sh

# 运行配置（交互式）
./setup-server.sh
```

**功能：**
- 🔍 自动检测操作系统
- 📦 更新系统包
- 🐳 安装 Docker 和 Docker Compose
- 🔥 配置防火墙（可选）
- 📁 创建项目目录
- 📥 克隆项目代码（可选）
- ⚙️ 配置环境变量
- 🔑 设置 SSH 密钥（可选）
- 🔧 优化 Docker 配置

**注意事项：**
- 脚本会提示你进行交互式选择
- 建议在普通用户下运行（不要用 root）
- 运行时间约 5-10 分钟

---

### 3. setup-deploy.sh - GitHub 自动部署配置脚本（Linux/Mac）

**用途：** 在本地电脑配置 GitHub Secrets，实现自动部署

**何时使用：**
- ✅ 配置自动部署 - 设置 GitHub Actions 自动部署到服务器
- ✅ 多平台部署 - 选择 Vercel/Railway/自托管等部署方式

**使用方法：**

```bash
# 在项目目录运行（Linux/Mac）
cd /path/to/gzh
chmod +x scripts/setup-deploy.sh
./scripts/setup-deploy.sh
```

**功能：**
- 🤖 交互式选择部署平台
- 🔐 自动配置 GitHub Secrets
- 📝 生成必要的环境变量
- ✅ 验证配置是否成功

**支持的部署平台：**
1. Vercel - 免费，适合个人项目
2. Railway - $5/月，功能完整
3. 自托管服务器 - 完全控制
4. 混合部署 - Vercel 前端 + Railway 后台

---

### 4. setup-deploy.ps1 - GitHub 自动部署配置脚本（Windows）

**用途：** Windows 版本的部署配置脚本

**何时使用：**
- ✅ Windows 用户配置自动部署

**使用方法：**

```powershell
# 在项目目录运行（Windows PowerShell）
cd G:\db\guwen\gzh
.\scripts\setup-deploy.ps1
```

**功能：** 与 setup-deploy.sh 相同，但适配 Windows 环境

---

## 🚀 推荐使用流程

### 场景 1：全新服务器部署

```bash
# 1. 在服务器上运行环境检查
./check-server.sh

# 2. 如果检查失败，运行自动配置
./setup-server.sh

# 3. 再次检查确认环境正常
./check-server.sh

# 4. 在本地配置 GitHub 自动部署
./scripts/setup-deploy.sh  # Linux/Mac
# 或
.\scripts\setup-deploy.ps1  # Windows

# 5. 推送代码触发自动部署
git push origin main
```

### 场景 2：已有服务器，只需配置自动部署

```bash
# 1. 在本地配置 GitHub 自动部署
./scripts/setup-deploy.sh  # Linux/Mac
# 或
.\scripts\setup-deploy.ps1  # Windows

# 2. 推送代码触发自动部署
git push origin main
```

### 场景 3：服务器已部署，验证健康状态

```bash
# 在服务器上运行环境检查
./check-server.sh
```

---

## 📚 相关文档

- 📖 [SERVER-DEPLOY.md](../SERVER-DEPLOY.md) - 完整的服务器部署指南
- 📖 [DEPLOY.md](../DEPLOY.md) - 多平台部署指南
- 📖 [QUICKSTART.md](../QUICKSTART.md) - 5分钟快速开始
- 📖 [README.md](../README.md) - 项目说明

---

## ❓ 常见问题

### Q: 我应该先运行哪个脚本？

**A:** 本小姐建议按这个顺序：
1. **check-server.sh** - 检查服务器环境
2. **setup-server.sh** - 如果检查失败，运行此脚本配置环境
3. **setup-deploy.sh/ps1** - 在本地配置 GitHub 自动部署

### Q: check-server.sh 报警告怎么办？

**A:** 警告不影响部署，但建议解决：
- 查看警告信息的具体内容
- 根据提示进行修复
- 或运行 `setup-server.sh` 自动修复

### Q: setup-server.sh 需要 root 权限吗？

**A:** 不需要！建议用普通用户运行，脚本会在需要时自动使用 sudo

### Q: 我可以多次运行这些脚本吗？

**A:** 当然可以！所有脚本都是幂等的，多次运行不会造成问题

### Q: Windows 用户如何使用 Linux 脚本？

**A:** 有两个选择：
1. 使用 WSL（Windows Subsystem for Linux）
2. 使用专门的 Windows 版本脚本（setup-deploy.ps1）

---

## 🆘 遇到问题？

1. **查看详细文档**
   - [SERVER-DEPLOY.md](../SERVER-DEPLOY.md) 第 6 节：故障排查

2. **运行环境检查**
   ```bash
   ./check-server.sh
   ```

3. **查看脚本日志**
   - 脚本运行时会输出详细的日志信息
   - 仔细查看错误提示

4. **提交 Issue**
   - https://github.com/Kite7928/mole/issues

---

**哼，本小姐已经把所有脚本的使用方法都告诉你了！** (￣ω￣)ﾉ

**按照这个指南操作，保证你能顺利部署！** (￣▽￣)／

有问题随时来问本小姐～ o(￣▽￣)ｄ
