# Migration Report

审计日期：2026-08-07（本地静态审计）。本报告仅记录仓库内可验证的现状；未将任何订阅、凭据或用户数据发送至外部服务。

## 1. 当前仓库结构

```text
shadowrocket-ai-rules/
├── .github/workflows/validate.yml
├── rules/
│   ├── *-Custom.list（7 个 Shadowrocket 本地覆盖规则集）
├── scripts/validate.py
├── shadowrocket-ai.conf
├── README.md
└── CHANGELOG.md
```

当前产物只有 Shadowrocket 主配置与其本地 `.list` 覆盖规则；没有 Mihomo Rule Provider、OpenClash/Mihomo 模板、节点分类工具或 YAML 校验流程。

## 2. 当前规则分类与数量

本地 `rules/*.list` 共 30 条有效规则（不含注释和空行）：

| 分类 | 文件 | 有效规则数 | 当前用途 |
| --- | --- | ---: | --- |
| OpenAI | `OpenAI-Custom.list` | 7 | OpenAI/ChatGPT 补充域名 |
| Google AI | `Gemini-Custom.list` | 7 | Gemini、AI Studio、NotebookLM 补充域名 |
| 局域网/直连 | `Direct-Custom.list` | 8 | localhost、`.local` 与 RFC1918/保留网段 |
| Claude | `Claude-Custom.list` | 3 | Claude/Anthropic |
| Grok | `Grok-Custom.list` | 3 | Grok/xAI |
| Copilot | `Copilot-Custom.list` | 2 | Microsoft/GitHub Copilot |
| 拒绝 | `Reject-Custom.list` | 0 | 仅注释占位 |

`shadowrocket-ai.conf` 另引用 26 个上游 `RULE-SET`，覆盖 LAN、广告/隐私/劫持、AI、开发、影音、社交、Apple、Microsoft、Google 与 ChinaMax。

## 3. 重复、无效与格式审计

- 本地有效规则未发现逐行重复。
- `scripts/validate.py` 已通过；本地规则类型均在校验器允许集合内。
- 未发现敏感订阅、Token、密码、UUID 或私钥字段。
- 未发现 `[MITM]` 或 `[URL Rewrite]` 段。
- `Reject-Custom.list` 为空并非格式错误，作为保守拒绝规则的安全占位可保留。
- 现有 `DOMAIN-SUFFIX,generativelanguage.googleapis.com` 可被严格语义理解，但它与 `DOMAIN` 相比覆盖范围更宽；本次迁移将不改写该既有历史规则。

## 4. GitHub Actions 风险分析

本地静态校验可通过，当前无法从仓库内容证明 GitHub Actions 已失败。现有工作流的潜在失败点是外部依赖：

1. 每日对所有远端 `RULE-SET` 逐条执行 HTTP 请求；任一上游临时限流、网络抖动、重定向变化或 GitHub Raw 不可用都会使工作流失败。
2. LOWERTOP 参考兼容性检查要求其公开示例持续含有一组固定字段；该项目调整示例字段会造成与本仓库功能无关的失败。
3. 工作流没有验证 YAML Provider 或模板，因此新增 Mihomo/OpenClash 产物后存在覆盖盲区。

## 5. 可保留内容

- 原始 `shadowrocket-ai.conf`、全部 `rules/*-Custom.list`、README 的安全边界以及无 MITM/脚本/重写原则。
- AI 窄规则先于 Google/Microsoft 宽规则的设计。
- Apple 与国内服务优先直连、Spotify 可切换 `DIRECT` 的保守策略。
- 现有 Python 静态校验器和 GitHub Actions 的本地校验入口。

## 6. 建议修改方案

推荐采用“新增兼容层，保留 Shadowrocket 入口”的渐进方案：

1. 保留原有 `rules/*.list` 与 `shadowrocket-ai.conf`，仅补充新的分类目录和引用。
2. 新增小型、可审查的 `providers/*.yaml`，全部使用 Mihomo `classical` `payload` 格式；规则限定为高置信域名和私网 CIDR，不使用 `DOMAIN-KEYWORD,bank` 等宽匹配。
3. 新增 `templates/config-template.yaml`：只提供策略组、Rule Provider、规则顺序和 `proxy-providers` 占位，不包含订阅 URL 或凭据，适用于 Mihomo/OpenClash 导入后人工填写订阅地址。
4. 新增离线 `proxy-provider-analysis` 工具：读取本地 Mihomo 订阅 YAML，不联网、不探测节点 IP；按节点名称、Emoji、中文/英文地区和服务标签输出 `node-classification.yaml`。IP 归属地仅预留显式离线输入字段，避免擅自向第三方提交节点地址。
5. 扩展验证脚本，校验 Shadowrocket、Rule Provider、Mihomo 模板、规则优先级、重复域名、域名格式和代表性路由模拟；工作流改为对本仓库产物执行确定性验证，将上游可用性检查设为非阻断信息项。

该方案的优势是可回退、低误伤且不复制第三方大规则库；局限是 Provider 只覆盖列出的高置信服务，普通大陆服务仍沿用成熟的 ChinaMax/GEOIP 路径。
