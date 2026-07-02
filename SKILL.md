---
name: publish-skill-to-github
description: Use when a user wants to publish a local Agent Skill, SKILL.md package, coding-agent capability, plugin-like folder, or reusable agent workflow to GitHub, including README polish, validation, gh auth login, repository creation, commit, push, and remote verification.
---

# Publish Skill To GitHub

## 中文版本

### 核心原则

这个 skill 用于把本地 Agent Skill / `SKILL.md` 能力包发布成一个可复用的 GitHub 仓库。默认目标是“公开、可安装、可验证、可复用”，不是只把文件随手推上去。

如果用户要求“帮我上传到 GitHub”“创建仓库并推送”“把这个 skill 发布出去”“以后所有窗口都能自动做这个流程”，使用本 skill。

### 工作流

1. **确认发布对象**
   - 找到要发布的目录。优先使用用户明确给出的目录；否则在当前工作区寻找包含 `SKILL.md` 的包。
   - 只发布目标包本身，不把旁边无关目录一起提交。
   - 如果目标目录名与 `SKILL.md` frontmatter 的 `name` 不一致，优先把仓库目录改成 skill name。

2. **整理 GitHub-ready 包**
   - 必须有 `SKILL.md`。
   - 建议包含 `README.md`、`LICENSE`、`.gitignore`。
   - 如果支持 Codex/OpenAI UI，保留 `agents/openai.yaml`。
   - 如果支持 WorkBuddy/CodeBuddy 风格元数据，可以保留 `skill.yml`，但核心入口仍是 `SKILL.md`。
   - README 应说明：这个 skill 是什么、适合什么、用户输入什么、用户得到什么、安装方式、快速开始、质量与安全、许可证。
   - 如果当前项目要求 Markdown 双语，所有 Markdown 必须包含中文和英文版本。

3. **本地验证**
   - 运行 skill validator（如果存在）：

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" <skill-dir>
```

   - 解析 YAML：

```bash
ruby -e 'require "yaml"; Dir["**/*.{yml,yaml}"].each { |f| YAML.load_file(f) }; puts "yaml ok"'
```

   - 扫描私密信息：

```bash
HOME_PATTERN=$(printf '%s' "$HOME" | sed 's/[.[\*^$()+?{}|]/\\&/g')
TOKEN_PATTERN='s''k-[A-Za-z0-9]{20,}|g''ho_[A-Za-z0-9_]+'
EMAIL_PATTERN='[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}'
CHAT_TMP_PATTERN='x''wechat|R''WTemp|com\\.ten''cent'
rg -n "$HOME_PATTERN|$CHAT_TMP_PATTERN|$TOKEN_PATTERN|$EMAIL_PATTERN" <skill-dir>
```

4. **GitHub 登录**
   - 检查：

```bash
gh auth status
```

   - 如果未登录，运行：

```bash
printf 'Y\n' | gh auth login -h github.com -p https -w
```

   - 把终端输出的一次性 code 和 `https://github.com/login/device` 告诉用户，让用户在浏览器完成授权。
   - 授权后再次运行 `gh auth status`，必须看到正确账号。
   - 如果设备码流程能生成 code，但最后 `github.com/login/oauth/access_token` 超时，说明当前 shell 访问 GitHub 网页登录端点不稳定。改用 token fallback，不要继续无限重试：

```bash
gh auth login --with-token
```

   - 让用户只在终端提示里粘贴 GitHub PAT，不要把 token 发到聊天里。创建公开仓库和 push 通常需要 `repo` 范围或等价细粒度权限。
   - 如果 `api.github.com` 能通，但 `github.com/login/device` 或 `github.com/login/oauth/access_token` 指向某个慢 IP 超时，先尝试临时 CONNECT 代理，不要改系统 `/etc/hosts`：

```bash
cd <skill-dir>
python3 scripts/github_connect_proxy.py
HTTPS_PROXY=http://127.0.0.1:18080 HTTP_PROXY=http://127.0.0.1:18080 gh auth login -h github.com -p https -w
```

   - 代理只在当前终端会话中使用；登录和 push 完成后停止代理进程。

5. **初始化 Git 并创建仓库**
   - 在目标 skill 目录内操作：

```bash
git init
git add README.md SKILL.md LICENSE .gitignore agents references skill.yml
git commit -m "Initial release"
gh repo create <owner>/<repo> --public --source . --remote origin --push
```

   - 如果仓库已存在，改用：

```bash
git remote add origin https://github.com/<owner>/<repo>.git
git push -u origin main
```

   - 不要使用 `git add -A`，除非确认目录里所有文件都属于发布包。
   - 如果 `git push` 因 `github.com` DNS/IP 超时失败，临时带上同一个代理环境变量：

```bash
HTTPS_PROXY=http://127.0.0.1:18080 HTTP_PROXY=http://127.0.0.1:18080 git push -u origin main
```

6. **远端验证**
   - 验证仓库存在：

```bash
gh repo view <owner>/<repo> --web=false
```

   - 验证远端文件：

```bash
gh api repos/<owner>/<repo>/contents
```

   - 最终回复必须给出仓库 URL、提交 SHA、验证命令结果摘要，以及任何没有完成的事项。

### README 写法

README 可以参考成熟开源项目的节奏，但不要复制长段文本。推荐结构：

- 项目名
- 语言切换提示或中英双语结构
- 一句话定位
- 徽章
- 产品/skill 解决什么问题
- 适合什么场景
- 一句话需求进来时怎么处理
- 用户需要输入什么
- 用户会得到什么
- 与普通搜索/普通生成有什么不同
- 典型场景
- 默认能力
- 仓库结构
- 安装
- 快速开始
- 质量与安全
- 许可证

### 常见风险

- `gh` 未登录：先启动网页登录，不要假装已经能推送。
- GitHub App 工具只能操作已有仓库：创建新仓库优先用 `gh repo create`。
- 工作区混杂：只在 skill 目录里初始化 Git，避免提交父目录里的无关文件。
- 私密信息泄露：发布前必须扫本地路径、账号、邮箱、token、客户资料。
- README 写得像内部说明：公开仓库 README 要说产品能力和用户价值，不要暴露内部工作流来源。

## English Version

### Core Principle

Use this skill to publish a local Agent Skill / `SKILL.md` package as a reusable GitHub repository. The default target is public, installable, verifiable, and reusable, not merely pushed somewhere.

Use this skill when the user asks to upload a skill to GitHub, create a repository and push it, publish a local agent capability, or make this release workflow reusable in future windows and projects.

### Workflow

1. **Identify the package**
   - Find the directory to publish. Prefer the user-provided path; otherwise search the current workspace for a package containing `SKILL.md`.
   - Publish only the target package, not unrelated neighboring directories.
   - If the directory name and `SKILL.md` frontmatter `name` differ, prefer renaming the repository directory to the skill name.

2. **Prepare a GitHub-ready package**
   - Require `SKILL.md`.
   - Recommend `README.md`, `LICENSE`, and `.gitignore`.
   - Keep `agents/openai.yaml` when the package supports Codex/OpenAI UI.
   - Keep `skill.yml` when the package supports WorkBuddy/CodeBuddy-style metadata, but keep `SKILL.md` as the core entry point.
   - README should explain what the skill is, when to use it, what the user provides, what the user receives, installation, quick start, quality/safety, and license.
   - If the current project requires bilingual Markdown, every Markdown document must include Chinese and English versions.

3. **Validate locally**
   - Run the skill validator when available:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" <skill-dir>
```

   - Parse YAML:

```bash
ruby -e 'require "yaml"; Dir["**/*.{yml,yaml}"].each { |f| YAML.load_file(f) }; puts "yaml ok"'
```

   - Scan for private traces:

```bash
HOME_PATTERN=$(printf '%s' "$HOME" | sed 's/[.[\*^$()+?{}|]/\\&/g')
TOKEN_PATTERN='s''k-[A-Za-z0-9]{20,}|g''ho_[A-Za-z0-9_]+'
EMAIL_PATTERN='[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}'
CHAT_TMP_PATTERN='x''wechat|R''WTemp|com\\.ten''cent'
rg -n "$HOME_PATTERN|$CHAT_TMP_PATTERN|$TOKEN_PATTERN|$EMAIL_PATTERN" <skill-dir>
```

4. **Authenticate GitHub**
   - Check:

```bash
gh auth status
```

   - If unauthenticated, run:

```bash
printf 'Y\n' | gh auth login -h github.com -p https -w
```

   - Give the user the one-time code and `https://github.com/login/device`; the user completes browser authorization.
   - After authorization, run `gh auth status` again and confirm the expected account.
   - If the device-code flow produces a code but later times out at `github.com/login/oauth/access_token`, the shell cannot reliably reach GitHub's browser-login endpoint. Use the token fallback instead of retrying forever:

```bash
gh auth login --with-token
```

   - Ask the user to paste the GitHub PAT only into the terminal prompt, never into chat. Creating a public repository and pushing usually requires the `repo` scope or equivalent fine-grained permissions.
   - If `api.github.com` works but `github.com/login/device` or `github.com/login/oauth/access_token` times out on a slow GitHub IP, try the temporary CONNECT proxy before editing system `/etc/hosts`:

```bash
cd <skill-dir>
python3 scripts/github_connect_proxy.py
HTTPS_PROXY=http://127.0.0.1:18080 HTTP_PROXY=http://127.0.0.1:18080 gh auth login -h github.com -p https -w
```

   - The proxy is only for the current terminal session. Stop it after login and push finish.

5. **Initialize Git and create the repository**
   - Work inside the target skill directory:

```bash
git init
git add README.md SKILL.md LICENSE .gitignore agents references skill.yml
git commit -m "Initial release"
gh repo create <owner>/<repo> --public --source . --remote origin --push
```

   - If the repository already exists, use:

```bash
git remote add origin https://github.com/<owner>/<repo>.git
git push -u origin main
```

   - Do not use `git add -A` unless every file in the directory is confirmed to belong to the package.
   - If `git push` fails because `github.com` DNS/IP times out, temporarily reuse the same proxy:

```bash
HTTPS_PROXY=http://127.0.0.1:18080 HTTP_PROXY=http://127.0.0.1:18080 git push -u origin main
```

6. **Verify the remote**
   - Verify repository metadata:

```bash
gh repo view <owner>/<repo> --web=false
```

   - Verify remote files:

```bash
gh api repos/<owner>/<repo>/contents
```

   - Final response must include the repository URL, commit SHA, validation summary, and any remaining work.

### README Pattern

Use mature open-source README structure as inspiration, but do not copy long passages. Recommended sections:

- Project name
- Language switch or bilingual structure
- One-line positioning
- Badges
- What problem the skill solves
- When to use it
- How a one-line request is handled
- What the user should provide
- What the user gets
- How it differs from ordinary search or generation
- Common scenarios
- Default capabilities
- Repository structure
- Installation
- Quick start
- Quality and safety
- License

### Common Risks

- `gh` is not authenticated: start browser login first instead of pretending push is possible.
- GitHub App tools may only write to existing repositories: prefer `gh repo create` for new repositories.
- Mixed workspace: initialize Git inside the skill directory only, avoiding unrelated parent-directory files.
- Private data leakage: scan for local paths, accounts, emails, tokens, and customer data before publishing.
- Internal-facing README: public README should explain product capability and user value, not internal workflow provenance.
