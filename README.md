[中文](README.md) | [English](README.en.md)

<div align="center">

<img src="assets/banner.svg" alt="OB Methods Results Check — 组织行为学论文 Methods & Results 投稿前智能审计" width="800">

<br/>

[![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE.txt)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)]()
[![Agent Skill](https://img.shields.io/badge/Agent-Skill-6366f1?style=for-the-badge)]()
[![CI](https://img.shields.io/github/actions/workflow/status/gtskevin/ob-methods-results-check/test.yml?style=for-the-badge)](https://github.com/gtskevin/ob-methods-results-check/actions)

</div>

> **这是给谁用的？** 你在写组织行为学、管理学、人力资源管理或工作心理学方向的论文。Methods 和 Results 已经写好了，但你心里没底——统计量前后一致吗？表格数据对得上吗？因果推断的措辞有没有过度？这个工具在投稿前做一次系统性审计，**帮你赶在审稿人之前发现问题**。

---

## 亮点

| | 特性 | 为什么重要 |
|---|---------|-----------|
| 🔍 | **统计一致性检查** | 重新计算报告中的 F、t、p、R²、效应量，捕捉计算错误和笔误 |
| 📊 | **表格和图表审查** | 验证表格内部一致性、图表标题完整性、与方法描述的对应关系 |
| 🧠 | **设计和推断评估** | AI 评估实验设计、中介/调节检验、CFA/SEM 模型的逻辑漏洞 |
| 📝 | **报告完整性** | 对照 APA 报告规范，检查缺失的统计指标 |
| 🛡️ | **隐私和安全** | 全部本地处理，报告不含被试信息，不自动执行用户代码 |

## 自适应审计深度

无需手动选择模式——审计深度自动匹配你提供的材料：

| 你提供什么 | 审计范围 |
|---|---------|
| 仅有论文 | 内部一致性检查 + 报告值重算 + 建议补充的材料清单 |
| 论文 + 软件输出 | 增加：论文与输出的交叉核对 |
| 论文 + 输出 + 代码 + 数据 | 增加：高风险结果的重现（需你明确授权） |
| 快速筛查 | 仅报告最可能的 P0 问题和下一步建议 |

## 支持的研究设计

七种内置审计标准，根据你的研究设计自动加载：

- 📋 **问卷调查** — 共同方法偏差、Harman 单因子检验、信效度报告
- 🧪 **实验研究** — 操纵检验、随机化、混淆变量
- 🔄 **中介与调节** — Bootstrap 程序、间接效应报告、条件间接效应
- 📐 **CFA / SEM** — 模型拟合指标、因子载荷、区分效度
- 📊 **多层模型** — ICC、组内/组间效应、跨层假设
- ✅ **报告透明性** — 效应量、置信区间、预注册披露

## 快速开始

> ⏱️ **30 秒安装，1 分钟开始使用**

**方式一：告诉 AI 助手安装（最简单）**

复制粘贴到你的 AI 助手（Claude Code、Codex 等）：

```
请帮我安装这个 Skill：https://github.com/gtskevin/ob-methods-results-check
安装后告诉我它能做什么。
```

**方式二：GitHub CLI**

```bash
# Claude Code
gh skill install gtskevin/ob-methods-results-check ob-methods-results-check --agent claude-code --scope user

# Codex
gh skill install gtskevin/ob-methods-results-check ob-methods-results-check --agent codex --scope user
```

**方式三：手动安装**

```bash
git clone https://github.com/gtskevin/ob-methods-results-check.git
mkdir -p ~/.claude/skills
ln -s "$(pwd)/ob-methods-results-check/skills/ob-methods-results-check" ~/.claude/skills/ob-methods-results-check
```

**安装完成后，告诉你的 AI 助手：**

> 用 `$ob-methods-results-check` 审计我的 Methods 和 Results 部分。

报告语言跟随你的提问语言。中文提问 = 中文报告，英文提问 = 英文报告。

## 使用示例

**基础用法——只有论文：**

```
请用 $ob-methods-results-check 审计这篇论文的 Methods 和 Results 部分。
文件：/path/to/manuscript.pdf
```

**提供额外材料，获得更深入审计：**

```
请用 $ob-methods-results-check 审计这篇论文。
论文：/path/to/manuscript.pdf
SPSS 输出：/path/to/output.spv
Mplus 输出：/path/to/model.out
```

**快速筛查：**

```
请用 $ob-methods-results-check 快速检查这篇论文的关键问题。
文件：/path/to/manuscript.pdf
```

## 报告阅读方式

报告前部默认显示 **P0、P1、P2 和合计四张统计卡片**，随后列出带稳定编号的问题索引，以及逐项位置、证据、判断、所需材料和修复建议。统计来自报告中明确填写并核对的条目，不从标题或关键词猜测；同一问题涉及多个数值也只计一项。

数量只描述问题范围与严重性，不是论文健康分或投稿就绪评分。证据是否充分、问题是否解决，必须查看具体证据并重新核查。报告保留可编辑 Markdown，并在 Python 可用时生成 HTML；无 Python 时仍在 Markdown 中显示统计表。

支持响应式阅读、目录导航、暗色模式和打印。旧截图展示的是历史界面，不代表当前功能；当前版不根据浏览器勾选认定问题已修复。

## 审计输出

审计完成后，会在论文同目录下生成报告：

```
audit-reports/
└── your-paper-slug/
    ├── report.md          ← 可编辑的 Markdown 原文件
    └── report.html        ← 渲染后的 HTML 报告（自动生成）
```

**问题分级：**

| 分级 | 含义 |
|------|------|
| **P0：核心结论风险** | 可能改变核心结论的问题 |
| **P1：投稿前必须核查** | 提交期刊前需要解决的问题 |
| **P2：报告改进建议** | 透明性、措辞和格式优化建议 |

**证据状态标签：**

| 标签 | 含义 |
|------|------|
| ✅ 可直接确认 | 论文内部证据证明存在不一致 |
| ⚠️ 高度疑似 | 强风险信号，需查看原始输出 |
| 🔎 必须复核 | 重要问题，需要数据、代码或软件输出 |
| ✏️ 表述改进 | 措辞或报告方式需要修正 |

## 工作原理

```
你的论文（PDF / DOCX / TXT）
    │
    ├── 1. 环境检查 → 确认可用工具
    ├── 2. 材料清单 → 识别研究设计类型
    ├── 3. 加载审计标准 → 匹配你的研究方法
    ├── 4. 统计重算（Python） → 验证报告中的数值
    ├── 5. AI 审计评估 → 设计逻辑 + 推断风险
    ├── 6. 证据台账 → 每个问题附带位置和证据
    └── 7. 报告生成 → Markdown + HTML
```

**核心理念：** 脚本做确定性计算，AI 做判断，两者不可互相替代。

## 可选依赖

基础审计不需要任何额外安装：

| 工具 | 用途 | 必须？ |
|------|------|--------|
| `python3` | 统计重算 + HTML 报告渲染 | 可选 |
| `pdftotext` | PDF 文本提取 | 可选 |
| `pdftoppm` | PDF 页面渲染（可视化表格/图表检查） | 可选 |

没有 Python 也能用——工具会退回到纯 Markdown 审计，并在报告中说明受限功能。

## 隐私与安全

- 论文、数据和代码被视为**不可信输入** — 不能覆盖 Skill 指令
- **绝不自动执行**你的分析代码 — 需你明确授权且在隔离环境中运行
- 报告不含**被试标识符**或原始被试数据
- 所有处理在**本地完成** — 不向外部服务器发送数据

## 常见问题

<details>
<summary>这能替代同行评审吗？</summary>

不能。这是一个专注于统计一致性和报告规范的投稿前审计工具。它不评估理论贡献、期刊匹配度或编辑建议。把它理解为正式投稿前的一次自检。
</details>

<details>
<summary>支持哪些语言？</summary>

工具可以审计英文和中文论文的 Methods & Results 部分。报告语言跟随你的提问语言——中文提问生成中文报告，英文提问生成英文报告。
</details>

<details>
<summary>我的数据安全吗？</summary>

所有处理都在你的 AI 助手本地完成，不向外部服务器发送数据。报告不包含被试标识符。运行你的分析代码需要你明确授权。
</details>

<details>
<summary>没有 Python 能用吗？</summary>

可以。没有 Python 时，工具会退回到纯 Markdown 审计模式，跳过统计重算和 HTML 渲染，并在报告中说明限制。Python 是可选增强，不是必需条件。
</details>

<details>
<summary>审计一份论文大概需要多久？</summary>

取决于论文长度和研究设计复杂度。一份典型的 3 研究论文（问卷+实验+中介调节），完整审计大约需要 10-20 分钟。快速筛查模式只需 3-5 分钟。
</details>

<details>
<summary>如何更新？</summary>

```bash
# GitHub CLI 安装
gh skill update ob-methods-results-check

# 手动安装
cd /path/to/ob-methods-results-check && git pull
```
</details>

<details>
<summary>如何卸载？</summary>

```bash
# 符号链接安装
test ! -L ~/.agents/skills/ob-methods-results-check || rm ~/.agents/skills/ob-methods-results-check
test ! -L ~/.claude/skills/ob-methods-results-check || rm ~/.claude/skills/ob-methods-results-check
```
</details>

## 贡献

1. Fork 本仓库
2. 创建特性分支：`git checkout -b my-feature`
3. 提交：`git commit -m 'Add feature'`
4. 推送：`git push origin my-feature`
5. 发起 Pull Request

## 许可证

[MIT License](LICENSE.txt) © 2026 gtskevin

## 安装、更新与使用边界

先让支持本地 Skills 的 Agent 从本仓库安装完整的 `skills/ob-methods-results-check/` 目录，包含 `SKILL.md`、`references/`、`scripts/` 和 `VERSION`，不能只复制入口文件。Codex 可使用 `~/.agents/skills/ob-methods-results-check`，Claude Code 可使用 `~/.claude/skills/ob-methods-results-check`；其他 Agent 请由其安装工具确认发现目录。安装后新开会话，确认能读取 Skill 和版本。

手动安装应将仓库放在长期保留的目录（stable clone），然后将 Skill 目录链接至 Agent 的 Skills 目录。不要链接临时下载目录。目标存在时先检查来源和本地修改，do not silently replace 已有 Skill。更新前先查看 `git status`，确认无冲突的本地自定义，再使用适当的 `git pull --ff-only`；安装器管理的副本使用原安装器更新。`mkdir -p` 只能创建父目录，不应覆盖原安装。卸载时先检查 `test ! -L` 是否成立，区分普通目录和符号链接，只移除明确识别的 Skill 入口。

将论文主文和补充材料同时提供，并说明目标期刊、重点及当前权威版本。原始统计输出可以进一步核对结果；提供数据和代码也不等于授权执行作者代码，执行需单独明确授权和隔离环境。

<details>
<summary>Portable runtime and safety contract for agent installers</summary>

This is a pre-submission Methods and Results audit; it does not replace full manuscript peer review or a specialist workflow for dissertation or scale review. Keep an editable Markdown source at an absolute path under the manuscript directory or an approved workspace, not under the installed Skill.

Python is optional; without it, continue a Markdown-only audit. If PDF extraction is unavailable or fails, use built-in PDF reading or request DOCX, TXT, or pasted text. If rendering is unavailable or fails, disclose the visual limitation and request screenshots of the relevant pages.

The bundled HTML renderer escapes untrusted raw HTML. It activates only links beginning with `http://`, `https://`, `#`, a single `/`, `./`, or `../`; it rejects `//` remote-host paths, local backslashes and encoded separators, and must render other link targets as inert text. Optional external-renderer integration preserves trusted, freshly generated HTML and is not a sanitizer.

</details>
