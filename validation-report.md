# Validation Report

验证日期：2026-08-07。本报告针对当前本地草案生成，未提交、未推送。

## 已执行

| 检查项 | 结果 | 说明 |
| --- | --- | --- |
| Shadowrocket 配置结构 | 通过 | `[General]`、`[Proxy Group]`、`[Rule]`、唯一 `FINAL,节点选择` |
| 本地规则格式 | 通过 | 35 个 `.list` 文件，规则类型和域名格式有效 |
| Mihomo Rule Provider | 通过 | 28 个 Provider，`behavior: classical` 与 `payload` 存在，无 Provider 内重复 |
| Mihomo/OpenClash 模板 | 通过 | 策略组、Provider 路径、规则优先级均匹配 |
| YAML 语法 | 通过 | Ruby YAML parser 成功读取模板、Provider 与分类结果 |
| 节点分类器 | 通过 | 美国 GPT、香港 Netflix、日本 IIJ、未知节点样例均符合预期 |
| 路由模拟 | 通过 | 10/10：ChatGPT、OpenAI API、Gemini、YouTube、Netflix、GitHub、Apple、eplus、工商银行、支付宝 |
| 敏感信息扫描 | 通过 | 未发现订阅 Token、密码、UUID、Cookie、私钥 |
| MITM/重写检查 | 通过 | 未启用 `[MITM]`、`[URL Rewrite]`、脚本或重写 |

## 外部依赖说明

GitHub Actions 保留远端规则 URL 与 LOWERTOP 兼容性检查，但设置为 `continue-on-error: true`。网络、限流或上游临时变更不会阻断本地确定性校验；失败仍会在 Actions 日志中显示，供人工维护。

## 代表性路由

| 测试域名 | 目标策略 |
| --- | --- |
| `chatgpt.com` / `platform.openai.com` | `🤖 AI` |
| `gemini.google.com` | `🤖 AI` |
| `youtube.com` | `📺 YouTube` |
| `netflix.com` | `🎬 Netflix` |
| `github.com` | `🐱 GitHub` |
| `icloud.com` | `🍎 Apple` |
| `eplus.jp` | `🇯🇵 Japan-Media` |
| `icbc.com.cn` | `💰 Finance` |
| `alipay.com` | `💳 Payment` |
