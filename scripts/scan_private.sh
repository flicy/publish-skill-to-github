#!/usr/bin/env bash
# scan_private.sh — 发布前私密信息扫描
# 用法: bash scripts/scan_private.sh <skill-dir>
# 扫描本地路径、token、邮箱、微信/腾讯临时文件痕迹。
# 发现匹配时退出码 1，无匹配时退出码 0。

set -euo pipefail

TARGET="${1:-.}"

if [ ! -d "$TARGET" ]; then
  echo "错误: 目录不存在: $TARGET" >&2
  exit 2
fi

# 转义 $HOME 中的正则特殊字符
HOME_PATTERN=$(printf '%s' "$HOME" | sed 's/[.[\*^$()+?{}|]/\\&/g')

# token 模式（拆分避免自身匹配）
TOKEN_PATTERN='s''k-[A-Za-z0-9]{20,}|g''ho_[A-Za-z0-9_]+'

# 邮箱模式
EMAIL_PATTERN='[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}'

# 微信/腾讯临时文件痕迹（拆分避免自身匹配）
CHAT_TMP_PATTERN='x''wechat|R''WTemp|com\.ten''cent'

COMBINED="$HOME_PATTERN|$CHAT_TMP_PATTERN|$TOKEN_PATTERN|$EMAIL_PATTERN"

echo "扫描目录: $TARGET"
echo "模式: 本地路径 / token / 邮箱 / 微信临时文件"
echo "---"

# 优先用 rg，回退到 grep
if command -v rg &>/dev/null; then
  MATCHES=$(rg -n --no-heading "$COMBINED" "$TARGET" \
    --glob '!.git' --glob '!*.tar.gz' --glob '!node_modules' 2>/dev/null || true)
else
  MATCHES=$(grep -rn -E "$COMBINED" "$TARGET" \
    --exclude-dir=.git --exclude-dir=node_modules 2>/dev/null || true)
fi

if [ -n "$MATCHES" ]; then
  echo "⚠️  发现可能的私密信息:"
  echo ""
  echo "$MATCHES"
  echo ""
  echo "请逐条检查后再发布。"
  exit 1
else
  echo "✅ 未发现私密信息痕迹。"
  exit 0
fi
