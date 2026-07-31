# Shadowrocket AI Rules

面向 Shadowrocket 的保守分流配置。当前版本：**v1.2.0**。

## 主配置地址

```text
https://raw.githubusercontent.com/wwwenh17/shadowrocket-ai-rules/main/shadowrocket-ai.conf
```

## 路由设计

- OpenAI、Gemini、Claude、Grok、Copilot：默认优先使用“美国 AI 优选”。
- “美国 AI 优选”：优先使用名称含 `US`（或美国标识）和 `AI专线` 的节点；本次已按当前订阅中的 `🇺🇸US·头等·AI专线` 命名适配。不可用时回退到普通美国节点。
- Gemini 在普通 Google 规则之前，Copilot 在普通 Microsoft 规则之前。
- GitHub、Google、流媒体、通信与社交服务均使用独立策略组。
- Apple 和国内服务默认直连，但可在策略组中手动改为代理。
- 广告、隐私和劫持拦截仅使用 `AdvertisingLite`、`Privacy`、`Hijacking` 三个上游规则集；不启用 MITM、HTTPS 解密、脚本或重写。
- 中国大陆域名使用 `ChinaMax`，最后以 `GEOIP,CN,DIRECT` 兜底；最终规则仅有 `FINAL,节点选择`。

## 导入与更新

1. Shadowrocket → 配置 → 右上角 `＋`。
2. 粘贴主配置地址并下载。
3. 点击配置文件 → 使用配置。
4. 后续通过“更新配置”刷新本仓库和上游规则。

## 策略组

基础组：`节点选择`、`自动选择`、`故障转移`、`美国 AI 优选`、各地区节点组。

业务组：`OpenAI`、`Gemini`、`Claude`、`Grok`、`Copilot`、`Google`、`GitHub`、`YouTube`、`Netflix`、`Disney+`、`Max`、`Spotify`、`TikTok`、`Telegram`、`社交媒体`、`Apple`、`Microsoft`、`OneDrive`、`国内服务`、`广告拦截`、`漏网之鱼`。

`OpenAI`、`Gemini`、`Claude`、`Grok` 和 `Copilot` 的首选项是“美国 AI 优选”；需要日本或其他地区时，进入对应策略组手动选择即可。

## 修改节点地区关键词

所有地区匹配正则都位于 `shadowrocket-ai.conf` 的 `[Proxy Group]`。

- `美国 AI 专线`：必须同时匹配美国标识和 `AI专线`、`AI 专线`、`AI线路` 或 `AI 线路`；用于高优先级 AI 业务。
- `美国节点`、`日本节点`、`香港节点`、`新加坡节点`、`台湾节点`：用于普通地区选择与回退。

当机场更改节点名称时，只修改相应 `policy-regex-filter`，不要填写订阅地址、Token、密码、UUID 或证书私钥。修改后运行：

```bash
python scripts/validate.py
```

若某地区组为空，先检查机场节点名称是否符合正则；AI 服务仍可在策略组中手动切换到可用的美国、日本或“节点选择”。

## 自定义规则

本仓库只维护少量补充域名，不复制大规模上游规则：

```text
rules/OpenAI-Custom.list
rules/Gemini-Custom.list
rules/Claude-Custom.list
rules/Grok-Custom.list
rules/Copilot-Custom.list
rules/Direct-Custom.list
rules/Reject-Custom.list
```

不同 AI 服务的补充规则分别映射到各自策略组，避免 Gemini、Claude 或 Grok 被错误归入 OpenAI。

## 安全边界

- 不存储机场订阅、节点密码、UUID、Token、Cookie、证书或个人信息。
- 不启用 `[MITM]`、HTTPS 解密、脚本和 URL Rewrite。
- 不加入破解、解锁或大规模去广告脚本。
- 出现广告误杀时，优先注释单条广告规则集后排查，不要添加过宽的自定义拒绝规则。

## 校验

`scripts/validate.py` 校验段落、策略组引用、规则顺序、重复规则、唯一 FINAL、敏感字段和 MITM/重写禁用状态。GitHub Actions 每日运行：验证所有 `RULE-SET` 地址仍可访问，并下载 LOWERTOP 的 `lazy_group.conf` 检查本配置依赖的语法和通用字段是否仍被其公开参考配置支持。该流程只报告上游兼容性，不会自动修改路由策略或提交文件。
