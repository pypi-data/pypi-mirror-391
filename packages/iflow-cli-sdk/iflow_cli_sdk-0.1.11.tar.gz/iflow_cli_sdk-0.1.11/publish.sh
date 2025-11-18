#!/bin/bash

# iFlow SDK Python 发布脚本
# 用法: ./publish.sh [版本号]
# 例如: ./publish.sh 0.1.4

set -e  # 出错时停止执行

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}ℹ ${NC}$1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# 检查是否提供了版本号
if [ -z "$1" ]; then
    print_error "请提供版本号"
    echo "用法: ./publish.sh [版本号]"
    echo "例如: ./publish.sh 0.1.4"
    exit 1
fi

NEW_VERSION=$1

print_info "准备发布 iFlow SDK Python 版本 $NEW_VERSION"

# 1. 检查工作目录状态
print_info "检查 Git 状态..."
if [ -n "$(git status --porcelain)" ]; then
    print_warning "有未提交的更改："
    git status --short
    read -p "是否继续? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "取消发布"
        exit 1
    fi
fi

# 2. 更新版本号
print_info "更新版本号到 $NEW_VERSION..."
sed -i '' "s/^version = \".*\"/version = \"$NEW_VERSION\"/" pyproject.toml
print_success "版本号已更新"

# 3. 清理旧的构建文件
print_info "清理旧的构建文件..."
rm -rf dist/ build/ *.egg-info/
print_success "清理完成"

# 4. 安装/更新构建工具
print_info "检查构建工具..."
pip install --upgrade flit twine -q
print_success "构建工具已就绪"

# 5. 构建包
print_info "构建 Python 包..."
flit build
print_success "构建完成"

# 6. 检查构建的包
print_info "检查包的内容..."
echo "构建的文件："
ls -lh dist/

# 7. 使用 twine 检查包
print_info "运行 twine 检查..."
twine check dist/*
print_success "包检查通过"

# 8. 提交版本更改
print_info "提交版本更改..."
git add pyproject.toml
git commit -m "chore: bump version to $NEW_VERSION

- Fix import error in client.py
- Improve tool call message handling
- Add support for tool call arguments and output
- Update documentation for ToolCallMessage" || true

# 9. 创建 Git 标签
print_info "创建 Git 标签 v$NEW_VERSION..."
git tag -a "v$NEW_VERSION" -m "Release version $NEW_VERSION"
print_success "标签已创建"

# 10. 发布到 PyPI
print_info "准备发布到 PyPI..."
echo "将要发布以下文件："
ls -lh dist/

read -p "确认发布到 PyPI? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_info "发布到 PyPI..."

    # 使用提供的 token
    export TWINE_USERNAME="__token__"
    export TWINE_PASSWORD="pypi-AgEIcHlwaS5vcmcCJDVhZTUzMTM5LTFhOWMtNDRkMi1hZmJmLWQ2YjZmMDVmMTkwNQACKlszLCI3M2VjMzI5ZS02YjcxLTQ5OWQtYjY2Yy00YjJhODU4NjE4ZTAiXQAABiCkMpz9HGpXCPDZqNWuAeZQQ2MiprlTILj9B0s1RbWkhA"

    twine upload dist/*

    print_success "发布成功！"

    # 11. 推送到 Git 远程仓库
    print_info "推送到 Git 远程仓库..."
    git push origin main
    git push origin "v$NEW_VERSION"
    print_success "Git 推送完成"

    echo
    print_success "🎉 版本 $NEW_VERSION 已成功发布到 PyPI！"
    echo
    echo "用户可以通过以下命令安装："
    echo "  pip install iflow-cli-sdk==$NEW_VERSION"
    echo
    echo "或升级到最新版本："
    echo "  pip install --upgrade iflow-cli-sdk"
else
    print_warning "取消发布到 PyPI"
    print_info "包文件保留在 dist/ 目录中"
fi