#!/bin/bash
# cli-anything-godzilla GitHub 发布脚本

set -e

REPO_NAME="cli-anything-godzilla"
GITHUB_USER="fengchenzxc"
REPO_URL="https://github.com/${GITHUB_USER}/${REPO_NAME}.git"

echo "=== cli-anything-godzilla 发布脚本 ==="
echo ""

# 检查是否已登录 GitHub CLI
if command -v gh &> /dev/null; then
    echo "检测到 GitHub CLI..."

    # 检查认证状态
    if gh auth status &> /dev/null; then
        echo "✓ 已认证 GitHub CLI"

        # 创建远程仓库
        echo "创建 GitHub 仓库..."
        gh repo create ${REPO_NAME} --public --description "CLI harness for Godzilla Security Testing Tool" --source=. --remote=origin

        # 推送代码
        echo "推送代码到 GitHub..."
        git push -u origin main

        # 创建 release
        echo "创建 v1.0.0 release..."
        gh release create v1.0.0 --title "v1.0.0 - Initial Release" --notes-file - <<EOF
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

\`\`\`bash
pip install cli-anything-godzilla
\`\`\`

或从源码安装：

\`\`\`bash
git clone https://github.com/${GITHUB_USER}/${REPO_NAME}.git
cd ${REPO_NAME}
pip install -e .
\`\`\`

### 快速开始

\`\`\`bash
# 启动 REPL 模式
cli-anything-godzilla

# 查看帮助
cli-anything-godzilla --help

# 创建新项目
cli-anything-godzilla project new my-project
\`\`\`

### 文档

- [English README](cli_anything/godzilla/README.md)
- [中文 README](cli_anything/godzilla/README_CN.md)
EOF

        echo ""
        echo "✓ 发布成功！"
        echo "仓库地址: https://github.com/${GITHUB_USER}/${REPO_NAME}"
        exit 0
    else
        echo "✗ 未认证 GitHub CLI"
        echo "请运行: gh auth login"
        exit 1
    fi
fi

# 手动发布步骤
echo "未检测到 GitHub CLI，请按以下步骤手动发布："
echo ""
echo "步骤 1: 在 GitHub 上创建仓库"
echo "  访问: https://github.com/new"
echo "  仓库名: ${REPO_NAME}"
echo "  描述: CLI harness for Godzilla Security Testing Tool"
echo "  设置为: Public"
echo "  不要初始化 README (我们已经有了)"
echo ""
echo "步骤 2: 添加远程仓库并推送"
echo "  git remote add origin ${REPO_URL}"
echo "  git push -u origin main"
echo ""
echo "步骤 3: 创建 Release"
echo "  访问: https://github.com/${GITHUB_USER}/${REPO_NAME}/releases/new"
echo "  标签: v1.0.0"
echo "  标题: v1.0.0 - Initial Release"
echo ""
echo "=== 完成 ==="
