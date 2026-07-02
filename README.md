# Publish Skill To GitHub

简体中文 | English below

> 把本地 Agent Skill / `SKILL.md` 能力包整理成可发布、可安装、可验证的 GitHub 仓库。

[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](./LICENSE)
[![Agent Skill](https://img.shields.io/badge/agent--skill-SKILL.md-blue.svg)](./SKILL.md)
[![GitHub repo](https://img.shields.io/badge/github-flicy%2Fpublish--skill--to--github-black.svg)](https://github.com/flicy/publish-skill-to-github)

Publish Skill To GitHub 是一个面向 coding agent 的发布工作流 skill。它帮助 Agent 把本地 skill 包从“能在本机用”推进到“能公开发布、被别人安装、被远端验证”的状态。

它覆盖：

- 确认要发布的 skill 目录
- 补齐 GitHub-ready 文件
- 校验 `SKILL.md`、YAML、脚本和 Markdown
- 检查 GitHub CLI 登录
- 处理 `gh auth login` 设备码登录
- 处理 GitHub DNS/IP 超时的临时代理 fallback
- 创建 GitHub 仓库
- 提交、推送和远端验证

## 适合什么场景

如果你希望：

- 把一个本地 `SKILL.md` 包上传到 GitHub
- 创建公开 skill 仓库并推送首个版本
- 给 Codex、Claude Code、QClaw/OpenClaw、CodeBuddy/WorkBuddy 等 agent 发布同一份能力包
- 在发布前自动检查 README、LICENSE、`.gitignore`、元数据和私密信息
- 遇到 `github.com` DNS/IP 超时时仍能完成 `gh auth login` 或 `git push`

那么这个 skill 就很适合你。

## 用户需要输入什么

最小输入：

| 字段 | 示例 |
|---|---|
| skill 路径 | `/path/to/my-skill/SKILL.md` 或 `/path/to/my-skill` |
| GitHub owner | `flicy`、组织名或当前登录账号 |
| 仓库名 | 通常与 `SKILL.md` 的 `name` 一致 |

推荐补充：

| 字段 | 示例 |
|---|---|
| 可见性 | public / private |
| README 风格 | 简洁说明、开源项目风格、参考某个仓库 |
| 兼容平台 | Codex、Claude Code、QClaw/OpenClaw、CodeBuddy/WorkBuddy |
| 是否需要更新已有仓库 | 新建仓库或推送到已有仓库 |

## 用户会得到什么

- 一个 GitHub-ready skill 包。
- 一份中英双语 README。
- 本地验证结果：skill validator、YAML 解析、脚本编译、私密信息扫描。
- GitHub 仓库 URL。
- 本地和远端 commit SHA。
- 远端文件列表验证结果。
- 如果失败，得到明确阻塞原因和可继续操作的命令。

## 一句话需求进来，它怎么接住

用户可以直接说：

```text
用 publish-skill-to-github 把 /path/to/my-skill 上传到 GitHub。
```

Agent 会先确认目标包，只在该 skill 目录内初始化 Git，不会把父目录里无关文件一起提交。

| 当前状态 | Agent 怎么做 |
|---|---|
| 只有 `SKILL.md` | 补 README、LICENSE、`.gitignore` 和必要元数据 |
| 已经有 README | 按公开仓库口径检查和润色 |
| `gh` 未登录 | 运行 `gh auth login -h github.com -p https -w` |
| 设备码登录超时 | 使用临时 CONNECT 代理或 `gh auth login --with-token` fallback |
| 仓库不存在 | `gh repo create <owner>/<repo> --public --source . --remote origin --push` |
| 仓库已存在 | 添加 remote 或更新现有 remote 后 push |

## 默认能力

- **范围隔离**：只发布目标 skill 包，不提交相邻目录。
- **公开化 README**：说明产品能力和用户价值，不暴露内部制作过程。
- **跨 Agent 兼容**：默认保留 `SKILL.md` 作为核心入口，可选保留 `agents/openai.yaml` 和 `skill.yml`。
- **安全扫描**：发布前扫描本地路径、邮箱、token 和客户资料痕迹。
- **登录恢复**：支持 GitHub 设备码、PAT fallback 和临时 CONNECT 代理。
- **远端验证**：仓库创建后检查 metadata、文件列表、分支和 commit SHA。

## 仓库结构

```text
publish-skill-to-github/
├── SKILL.md
├── README.md
├── LICENSE
├── skill.yml
├── agents/
│   └── openai.yaml
└── scripts/
    └── github_connect_proxy.py
```

## 安装

### Codex

```bash
git clone https://github.com/flicy/publish-skill-to-github.git
cp -R publish-skill-to-github ~/.codex/skills/publish-skill-to-github
```

### Claude Code

```bash
git clone https://github.com/flicy/publish-skill-to-github.git
mkdir -p ~/.claude/skills
cp -R publish-skill-to-github ~/.claude/skills/publish-skill-to-github
```

### QClaw / OpenClaw

```bash
git clone https://github.com/flicy/publish-skill-to-github.git
# 按你的 QClaw / OpenClaw skills 搜索路径复制本目录，入口保持 SKILL.md。
```

### CodeBuddy / WorkBuddy 相关 coding agent

```bash
git clone https://github.com/flicy/publish-skill-to-github.git
mkdir -p .codebuddy/skills
cp -R publish-skill-to-github .codebuddy/skills/publish-skill-to-github
```

## 快速开始

```text
使用 publish-skill-to-github，把 /path/to/my-skill 发布到 flicy/my-skill。
```

更完整的提示词：

```text
使用 publish-skill-to-github，把 /path/to/my-skill 发布到 GitHub。
owner: flicy
repo: my-skill
visibility: public
README: 参考成熟开源项目结构，中英双语。
```

## 质量与安全

- 不要把 GitHub token 发到聊天里；只粘贴到终端提示中。
- 发布前必须检查私有路径、邮箱、token、客户资料和内部项目名。
- 如果 Markdown 文档更新，保持中文和英文两个版本。
- 如果临时启动 `github_connect_proxy.py`，登录和 push 完成后停止进程。

## 许可证

MIT — 见 [LICENSE](./LICENSE)

---

## English Version

> Package a local Agent Skill / `SKILL.md` capability as a publishable, installable, and verifiable GitHub repository.

[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](./LICENSE)
[![Agent Skill](https://img.shields.io/badge/agent--skill-SKILL.md-blue.svg)](./SKILL.md)
[![GitHub repo](https://img.shields.io/badge/github-flicy%2Fpublish--skill--to--github-black.svg)](https://github.com/flicy/publish-skill-to-github)

Publish Skill To GitHub is a release workflow skill for coding agents. It helps an agent move a local skill package from “works on this machine” to “published, installable, and verified remotely.”

It covers:

- identifying the target skill directory
- preparing GitHub-ready files
- validating `SKILL.md`, YAML, scripts, and Markdown
- checking GitHub CLI authentication
- handling `gh auth login` device-code login
- using a temporary proxy fallback for GitHub DNS/IP timeouts
- creating a GitHub repository
- committing, pushing, and remote verification

## When To Use

Use this skill when you want to:

- upload a local `SKILL.md` package to GitHub
- create a public skill repository and push the first version
- publish one capability package for Codex, Claude Code, QClaw/OpenClaw, CodeBuddy/WorkBuddy, and similar agents
- check README, LICENSE, `.gitignore`, metadata, and private traces before publishing
- recover from `github.com` DNS/IP timeouts during `gh auth login` or `git push`

## What The User Should Provide

Minimum input:

| Field | Example |
|---|---|
| Skill path | `/path/to/my-skill/SKILL.md` or `/path/to/my-skill` |
| GitHub owner | `flicy`, an organization, or the logged-in account |
| Repository name | Usually the same as the `name` in `SKILL.md` |

Recommended additions:

| Field | Example |
|---|---|
| Visibility | public / private |
| README style | concise, open-source style, or based on a reference repo |
| Compatible agents | Codex, Claude Code, QClaw/OpenClaw, CodeBuddy/WorkBuddy |
| Existing repository | create a new repository or push to an existing one |

## What The User Gets

- A GitHub-ready skill package.
- A bilingual README.
- Local validation results: skill validator, YAML parsing, script compilation, private-trace scan.
- GitHub repository URL.
- Local and remote commit SHA.
- Remote file-list verification.
- If something fails, a clear blocker and exact continuation command.

## How It Handles A One-Line Request

The user can say:

```text
Use publish-skill-to-github to upload /path/to/my-skill to GitHub.
```

The agent confirms the target package and initializes Git only inside that skill directory, avoiding unrelated parent-directory files.

| Current state | Agent action |
|---|---|
| Only `SKILL.md` exists | Add README, LICENSE, `.gitignore`, and useful metadata |
| README exists | Review and polish it for public repository use |
| `gh` is unauthenticated | Run `gh auth login -h github.com -p https -w` |
| Device-code login times out | Use the temporary CONNECT proxy or `gh auth login --with-token` fallback |
| Repository does not exist | Run `gh repo create <owner>/<repo> --public --source . --remote origin --push` |
| Repository exists | Add or update remote, then push |

## Default Capabilities

- **Scope isolation**: Publish only the target skill package.
- **Public README polish**: Explain capability and user value, not internal creation history.
- **Cross-agent compatibility**: Keep `SKILL.md` as the core entry point, with optional `agents/openai.yaml` and `skill.yml`.
- **Safety scan**: Scan local paths, emails, tokens, and customer-data traces before publishing.
- **Authentication recovery**: Support GitHub device-code login, PAT fallback, and temporary CONNECT proxy.
- **Remote verification**: Check repository metadata, file list, branch, and commit SHA after upload.

## Repository Structure

```text
publish-skill-to-github/
├── SKILL.md
├── README.md
├── LICENSE
├── skill.yml
├── agents/
│   └── openai.yaml
└── scripts/
    └── github_connect_proxy.py
```

## Installation

### Codex

```bash
git clone https://github.com/flicy/publish-skill-to-github.git
cp -R publish-skill-to-github ~/.codex/skills/publish-skill-to-github
```

### Claude Code

```bash
git clone https://github.com/flicy/publish-skill-to-github.git
mkdir -p ~/.claude/skills
cp -R publish-skill-to-github ~/.claude/skills/publish-skill-to-github
```

### QClaw / OpenClaw

```bash
git clone https://github.com/flicy/publish-skill-to-github.git
# Copy this directory into your QClaw / OpenClaw skills search path. Keep SKILL.md as the entry point.
```

### CodeBuddy / WorkBuddy-related coding agents

```bash
git clone https://github.com/flicy/publish-skill-to-github.git
mkdir -p .codebuddy/skills
cp -R publish-skill-to-github .codebuddy/skills/publish-skill-to-github
```

## Quick Start

```text
Use publish-skill-to-github to publish /path/to/my-skill to flicy/my-skill.
```

A fuller prompt:

```text
Use publish-skill-to-github to publish /path/to/my-skill to GitHub.
owner: flicy
repo: my-skill
visibility: public
README: bilingual, open-source style.
```

## Quality And Safety

- Do not send GitHub tokens in chat; paste them only into terminal prompts.
- Before publishing, scan for private paths, emails, tokens, customer data, and internal project names.
- If Markdown docs are updated, keep both Chinese and English versions.
- If `github_connect_proxy.py` is started temporarily, stop it after login and push finish.

## License

MIT — see [LICENSE](./LICENSE)
