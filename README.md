# Shadowrocket AI Rules

面向 Shadowrocket 的 AI 与 Google 生态分流配置。

## 路由目标

- ChatGPT / OpenAI：日本节点
- Gemini / Google AI Studio / NotebookLM：美国节点
- Google 生态：美国节点
- Claude、Grok、Perplexity、OpenRouter：美国节点
- Apple 与中国大陆网站：直连
- 其他境外流量：通用代理

## 主配置地址

```text
https://raw.githubusercontent.com/wwwenh17/shadowrocket-ai-rules/main/shadowrocket-ai.conf
```

## 使用方法

1. 在 Shadowrocket 的配置页面添加上述 URL。
2. 下载并使用该配置。
3. 在代理组中检查 `🇯🇵 ChatGPT` 和 `🇺🇸 Google AI` 是否正确识别节点。
4. 节点名称最好包含 `日本/东京/大阪/JP/Japan` 或 `美国/洛杉矶/圣何塞/US/USA`。
5. 设置 → 代理：`Proxy Type = None`，保持 TUN 模式。
6. 设置 → UDP：开启转发、开启“禁用 STUN”，超时设为 30 秒。

## 注意

- 本仓库不存储机场订阅、节点密码、UUID、Token 或个人信息。
- TLS ClientHello 指纹属于节点级设置，建议在节点详情中设为 `Chrome`。
- Shadowrocket 会在“使用配置/编译配置”时更新远程规则；配置本身可通过 `update-url` 更新。
- 若自动策略组未识别节点，请手动进入策略组选择对应日本或美国节点。

## 文件结构

```text
shadowrocket-ai.conf
rules/openai.list
rules/google-ai.list
rules/google-global.list
rules/ai-us.list
CHANGELOG.md
```

## 当前版本

v1.0.0
