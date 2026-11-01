# 贡献指南

欢迎提 Issue、讨论建议，以及提交 Pull Request。  
**只有仓库维护者可以合并代码**；外部协作者没有直接 push / 改设置的权限。

## 提建议 / 报问题

1. 先搜索是否已有同类 Issue。
2. 新建 Issue，尽量写清：场景、期望行为、实际行为、环境（Python / OS / 关键配置）。

## 提 Pull Request

1. Fork 本仓库，从 `main` 拉新分支。
2. 本地改完后执行：`uvx ruff check .`
3. 打开 PR，说明动机与改动点；关联相关 Issue（如有）。
4. 等待维护者 Review；按意见修改后再合并。

请不要：

- 直接向 `main` 强推（你也没有权限）
- 在一个 PR 里塞大量无关改动
- 提交 `.env`、密钥、本地数据库文件

提交说明建议遵循 [Conventional Commits](https://www.conventionalcommits.org/zh-hans/)

## 行为约定

友善交流即可。恶意 Issue、广告、人身攻击会被关闭。
