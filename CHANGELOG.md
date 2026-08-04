# Changelog

## v1.2.1 — 2026-08-04

- Spotify 策略组新增 `DIRECT` 选项，保留原有代理为默认选择
- 同步远程版本中 Grok 的新加坡节点选项
- 核对 blackmatrix7 与 LOWERTOP 最新更新；现有远程规则引用无需调整
- 增加 Spotify 必须包含 `DIRECT` 的静态校验

## v1.2.0 — 2026-07-31

- AI 服务改为 OpenAI、Gemini、Claude、Grok、Copilot 独立策略组和独立本地补充规则
- AI 策略默认优先“美国 AI 优选”，按当前订阅中的美国 AI 专线命名匹配，并回退至普通美国节点
- 新增 GitHub、Google、流媒体、通信、社交、Microsoft、OneDrive 等独立策略组
- 加入保守的 AdvertisingLite、Privacy、Hijacking 规则集，保持无 MITM、无脚本、无重写
- 国内服务使用 ChinaMax 与 GEOIP,CN,DIRECT；最终兜底固定为 FINAL,节点选择
- 扩展静态校验：策略组引用、唯一 FINAL、重复规则、Copilot/Gemini 顺序、敏感字段与 MITM/重写状态
- 修复 GitHub Actions 远程校验范围，仅检查 RULE-SET 地址；新增每日 LOWERTOP 参考配置兼容性检查

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
