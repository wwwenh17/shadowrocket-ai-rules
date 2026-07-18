# Shadowrocket AI Rules

面向 Shadowrocket 的 AI 与 Google 生态分流配置。当前版本：**v1.1.0**。

## 路由目标

- ChatGPT / OpenAI：日本节点
- Gemini / Google AI Studio / NotebookLM：美国节点
- Google 全生态：美国节点
- Claude、Grok、Perplexity、OpenRouter：美国节点
- Apple 与中国大陆网站：直连
- 其他境外流量：通用代理

## 主配置地址

```text
https://raw.githubusercontent.com/wwwenh17/shadowrocket-ai-rules/main/shadowrocket-ai.conf
```

## v1.1 的设计原则

1. **本地规则只做补充**：仓库内保留少量 AI 域名覆盖规则。
2. **主体采用成熟上游**：OpenAI、Gemini、Google、Claude、Apple、ChinaMax 使用 blackmatrix7 的 Shadowrocket 专用规则。
3. **窄规则优先**：OpenAI/Gemini 等 AI 规则位于 Google、Apple、ChinaMax 之前，避免被宽泛规则抢先命中。
4. **不使用激进广告拦截或 MITM**：降低银行、登录、支付、推送和 App 功能异常风险。
5. **使用 Shadowrocket 原生字段**：采用 `tun-excluded-routes`，避免旧配置中的非标准别名。
6. **策略组不滥用 `use=true`**：只有明确写入订阅名称时才应启用 `use=true`。

## 导入方法

1. Shadowrocket → 配置 → 右上角 `＋`。
2. 粘贴主配置地址并下载。
3. 点击配置文件 → 使用配置。
4. 首页下拉或进入配置详情，检查策略组。

应出现：

```text
🇯🇵 日本自动
🇺🇸 美国自动
🌍 境外自动
🇯🇵 ChatGPT
🇺🇸 Google AI
🇺🇸 AI 服务
🚀 通用代理
```

## 节点命名要求

自动分组依赖节点名称。建议节点名称至少包含以下任一关键词：

```text
日本 / 东京 / 大阪 / JP / Japan / Tokyo / Osaka
美国 / 洛杉矶 / 圣何塞 / 西雅图 / US / USA / United States
```

若策略组为空，进入 `🇯🇵 ChatGPT` 或 `🇺🇸 Google AI` 手动选择节点，并把机场实际节点命名截图提交，以便调整正则。

## Shadowrocket 建议设置

- 设置 → 代理：`Proxy Type = None`
- 设置 → UDP：开启转发
- 设置 → UDP：开启“禁用 STUN”
- UDP 超时：30 秒
- 节点 TLS ClientHello 指纹：优先 `Chrome`
- IPv6：默认关闭；确认机场与本地网络 IPv6 稳定后再开启

## DNS

主配置使用：

```text
h3://dns.alidns.com/dns-query
https://doh.pub/dns-query#no-h3
```

这是为了保证配置启动阶段可稳定解析。Shadowrocket 对代理类域名通常通过代理服务器远程解析；不建议在未验证节点可用前，只配置可能被阻断的境外 DoH。

## 更新机制

- 主配置通过 `update-url` 更新。
- 远程规则在“使用配置 / 编译配置 / 更新配置”时刷新。
- 上游规则由成熟项目持续维护；本仓库仅维护个性化路由与补充域名。

## 安全边界

- 仓库不存储机场订阅、节点密码、UUID、Token 或个人信息。
- 不启用 HTTPS 解密，不安装 MITM 证书。
- 不默认加入大规模广告拦截、重写脚本或隐私拦截，避免误杀。

## 文件结构

```text
shadowrocket-ai.conf
rules/openai.list
rules/google-ai.list
rules/ai-us.list
scripts/validate.py
.github/workflows/validate.yml
CHANGELOG.md
```
