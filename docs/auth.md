# 认证与鉴权 - 登录 / 续签 / Token 校验

## 概述

采用 **OAuth2 风格的双 Token 机制**，由 IAM 服务统一签发：

- **登录**：账号密码换取 `access_token`（默认 1 天）+ `refresh_token`（默认 7 天）
- **续签**：`access_token` 过期后，用 `refresh_token` 换取新的令牌
- **校验**：网关可解析并注入身份 header；微服务**不完全依赖网关**——没有 header 时自行校验 JWT

公开接口用 `Depends(allow_anonymous)` 标记豁免；其余无凭证一律 401。需要拿当前用户时再用 `Depends(require_auth)` / `CurrentUser`。

## 职责划分

| 角色 | 职责 | 说明 |
|---|---|---|
| **IAM 服务** | 签发 / 续签 token | `POST /api/auth/login`、`POST /api/auth/refresh`（`allow_anonymous`） |
| **API 网关（APISIX）** | 可选：校验 access_token 并注入 `X-User-Id` / `X-Account` | 网关未注入时，微服务自验 Bearer |
| **各微服务** | 中间件解析身份；路由用 `Depends` 决定是否必须登录 | 见下方 |

## 微服务鉴权

### 中间件

`AuthMiddleware`：

1. 若有 `X-User-Id`（网关或 RPC 透传）→ 写入 `AuthContext`
2. 否则若有 `Authorization: Bearer` → 自验 JWT；失败 → **401**
3. 仍无身份 → 仅豁免接口放行，否则 **401**

豁免方式：路由挂 `Depends(allow_anonymous)`（不是路径字符串白名单）。`/health`、docs 等框架路径内置放行。

### 路由依赖

```python
from fastapi import APIRouter, Depends
from common.auth import allow_anonymous, require_auth, CurrentUser

# 公开接口
router = APIRouter(dependencies=[Depends(allow_anonymous)])

# 需登录（并可注入当前用户）
router = APIRouter(dependencies=[Depends(require_auth)])

@router.post("/xxx")
async def xxx(user: CurrentUser, ...):
    ...
```

## Token 类型

定义见 `common/utils/jwt_helper.py` 的 `TokenType`：

| 类型 | 值 | 默认有效期 | 用途 |
|---|---|---|---|
| `USER_TOKEN` | `user` | 1 天 | 用户访问令牌（access_token） |
| `REFRESH_TOKEN` | `refresh` | 7 天 | 续签令牌，仅用于换取新 access_token |
| `SERVICE_TOKEN` | `service` | 15 分钟 | 微服务间调用 |
| `BFF_TOKEN` | `bff` | 60 分钟 | BFF 调用微服务 |

access_token 的载荷（claims）包含：`user_id`、`account`、`user_name`、`client`、`type`、`iat`、`iss`、`exp`。

## 登录流程

```
Client (账号 + 密码 + client)
  │  POST /api/auth/login
  ▼
LoginService.login
  ├─ UserService.get_user_auth_by_account(account)
  ├─ verify_password + UserDomain.is_enabled
  └─ _issue_tokens()
  ▼
返回 access_token + refresh_token + expires_in + user_id + account
```

## 续签流程

```
Client (refresh_token)
  │  POST /api/auth/refresh
  ▼
LoginService.refresh
  ├─ jwt_helper.verify_refresh_token(refresh_token)
  └─ _issue_tokens()  # 轮换 refresh_token
  ▼
返回新的 access_token + refresh_token + expires_in
```

## 请求上下文透传（RPC）

```
外网请求 → 网关(可选解析) → 微服务A → 微服务B(RPC)
                │               │            │
                └── X-User-Id ──┴── 透传 ────┘
                    X-Account
```

- `common/auth/context.py`：`AuthContext`；RPC 通过 `get_auth_headers()` / `to_headers()` 透传

## 接口契约

### POST /api/auth/login

请求 `LoginRequest`：`account` / `password` / `client`

响应 `LoginResponse`：`access_token` / `refresh_token` / `token_type` / `expires_in` / `user_id` / `account`

### POST /api/auth/refresh

请求 `RefreshRequest`：`refresh_token`

响应 `RefreshResponse`：新的双 token + `expires_in`

## 网关（APISIX）配置要点

1. **放行登录 / 续签**：网关侧可不校验这两个路径的 access_token。
2. **其它路由**：可校验 access_token 并注入 `X-User-Id`、`X-Account`；即使未注入，微服务也会自验 Bearer。
3. **密钥一致**：网关与 IAM / 各服务的 `JWT_SECRET_KEY` 一致。

## 配置项

| 配置 | 默认值 | 说明 |
|---|---|---|
| `JWT_SECRET_KEY` | `change_me_in_production` | 签名密钥（生产需替换） |
| `JWT_ALGORITHM` | `HS256` | 签名算法 |
| `JWT_ACCESS_EXPIRE_MINUTES` | `1440` | access_token 有效期 |
| `JWT_REFRESH_EXPIRE_MINUTES` | `10080` | refresh_token 有效期 |
