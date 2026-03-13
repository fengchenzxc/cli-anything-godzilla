# cli-anything-godzilla 发布指南

## 方法 1: 使用 GitHub CLI（推荐）

如果您能安装 GitHub CLI，这是最简单的方法：

```bash
# 安装 GitHub CLI
brew install gh

# 登录 GitHub
gh auth login

# 运行发布脚本
./publish.sh
```

## 方法 2: 手动发布

### 步骤 1: 创建 GitHub 仓库

1. 访问 https://github.com/new
2. 填写信息：
   - Repository name: `cli-anything-godzilla`
   - Description: `CLI harness for Godzilla Security Testing Tool`
   - 选择 **Public**
   - **不要**勾选 "Add a README file"
   - **不要**添加 .gitignore 或 license
3. 点击 "Create repository"

### 步骤 2: 推送代码

```bash
cd /private/tmp/哥斯拉402Godzilla/agent-harness

# 如果您有 Personal Access Token
git remote set-url origin https://<YOUR_TOKEN>@github.com/fengchenzxc/cli-anything-godzilla.git
git push -u origin main

# 或者使用 SSH（如果配置了）
git remote set-url origin git@github.com:fengchenzxc/cli-anything-godzilla.git
git push -u origin main
```

### 步骤 3: 创建 Release

1. 访问 https://github.com/fengchenzxc/cli-anything-godzilla/releases/new
2. 填写信息：
   - Tag: `v1.0.0`
   - Title: `v1.0.0 - Initial Release`
   - Description: 复制下面的内容

## Release 描述内容

```
## cli-anything-godzilla v1.0.0

CLI 命令行工具包，用于哥斯拉（Godzilla）WebShell 管理器的安全测试。

### 功能特性

- ✅ 完整的项目管理（创建、打开、保存、信息）
- ✅ Shell 管理（添加、查看、更新、删除、测试连接）
- ✅ 短 ID 支持（所有 shell 命令支持使用短 ID）
- ✅ C2 Profile 管理（加载和验证）
- ✅ 交互式 REPL 模式
- ✅ JSON 输出模式（便于 AI 代理集成）
- ✅ 兼容原版哥斯拉项目数据库

### 安装

```bash
pip install cli-anything-godzilla
```

或从源码安装：

```bash
git clone https://github.com/fengchenzxc/cli-anything-godzilla.git
cd cli-anything-godzilla
pip install -e .
```

### 快速开始

```bash
# 启动 REPL 模式
cli-anything-godzilla

# 查看帮助
cli-anything-godzilla --help

# 创建新项目
cli-anything-godzilla project new my-project
```

### 文档

- [English README](cli_anything/godzilla/README.md)
- [中文 README](cli_anything/godzilla/README_CN.md)
```

## 创建 Personal Access Token

如果您没有 Token，可以这样创建：

1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. 勾选 `repo` 权限
4. 点击 "Generate token"
5. 复制生成的 token（只显示一次！）
