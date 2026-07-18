# Changelog

## v1.1.0 — 2026-07-18

- 参考持续维护的 Shadowrocket 规则项目重新设计主配置
- OpenAI、Gemini、Google、Claude、Apple、ChinaMax 改用成熟上游规则
- 本地规则改为小型 overlay，仅补充个性化与新域名
- 修正 TUN 字段为 `tun-excluded-routes`
- 移除未指定订阅名称时容易踩坑的 `use=true`
- 强化日本、美国节点名称正则，降低 `US` 等短字符串误匹配
- Google AI 窄规则放在 Google 全生态宽规则之前
- DNS 改为稳定的 DoH3 + DoH 组合，并保留系统回退
- 保持无 MITM、无重写、无激进广告拦截的稳定路线
- 增加 GitHub Actions 配置与规则静态检查

## v1.0.0 — 2026-07-18

- 新增 Shadowrocket 主配置 `shadowrocket-ai.conf`
- ChatGPT / OpenAI 分流至日本策略组
- Gemini / Google AI Studio / NotebookLM 分流至美国策略组
- Google 生态分流至美国策略组
- Claude / Grok / Perplexity / OpenRouter 等分流至美国策略组
- Apple 与中国大陆流量直连
- 加入 DoH、DNS 劫持、UDP 不支持时拒绝及在线更新地址
- 新增独立规则文件，便于在线维护
