<div align="center">

# FastAPI Microservice Framework

**全异步、契约驱动的 Python 微服务业务脚手架**

> **状态：公开开源 / Alpha** — 免费查看与使用；欢迎 Issue 与建议。接口仍可能变动。  
> 贡献方式：Fork → Pull Request（需维护者审核合并）。详见 [CONTRIBUTING.md](CONTRIBUTING.md)。

FastAPI · SQLAlchemy 2 (async) · Celery · Outbox · Redis · MySQL · JWT

![Python](https://img.shields.io/badge/python-3.14+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-async-009688)
![Celery](https://img.shields.io/badge/Celery-5.6-37814A)
![uv](https://img.shields.io/badge/managed%20by-uv-DE5FE9)
![License](https://img.shields.io/badge/license-MIT-green)

</div>

---

## 简介

这是一套面向业务团队的 Python 微服务框架。它把 **数据库会话、鉴权、跨服务调用、异步任务（含 Outbox）、统一响应、异常处理** 这些基础设施全部收进框架层，业务代码只需要关心业务本身：

```python
from contract.product.product_error_code import ProductErrorCode

class ProductService:
    product_crud = ProductCRUD()
    inventory_client = inventory()          # 跨服务客户端：失败自动降级为 None

    @classmethod
    async def get_by_id(cls, params: GetProductByIdParams) -> ProductDetailReadModel:
        product = await cls.product_crud.get_by_id(params.id)   # Session 由中间件注入
        if product is None:
            raise DomainError(code=ProductErrorCode.NOT_FOUND, msg="商品不存在")

        inv = await cls.inventory_client.by_product_id(...)     # 不用 try / 判断状态码
        return ProductDetailReadModel(..., quantity=inv.quantity if inv else 0)
```

没有 `try/except`，没有 `session.commit()`，没有 `if resp.status_code != 200`。

仓库自带示例服务：`iam`（用户与认证）、`product`（商品 + 订单）、`inventory`（库存），覆盖登录鉴权、跨服务 RPC、Celery + Outbox 最终一致投递。

## 特性

- **全异步**：FastAPI + SQLAlchemy `AsyncSession` + asyncmy，从 HTTP 到数据库全链路 `async/await`。
- **请求级事务**：`DBSessionMiddleware` 为每个请求创建 Session，成功自动提交、异常自动回滚；CRUD 层通过 ContextVar 取用，无需层层传参。
- **契约驱动**：`contract/` 集中存放跨服务 DTO、枚举、错误码、任务名；服务之间只共享契约，不共享实现。
- **类型安全的 RPC**：基于 [fastapi-typed-client](https://pypi.org/project/fastapi-typed-client/) 从各服务路由生成强类型客户端，IDE 补全、返回类型都在。
- **可降级调用**：默认客户端失败时返回 `None`，业务不写 `try`；需要强一致时用 `.strict()`，异常交给全局处理。
- **双模鉴权**：信任网关注入的 `X-User-Id`，网关没解析时服务自行校验 JWT；公开接口用 `Depends(allow_anonymous)` 声明，没有路径白名单。
- **原生 async 的 Celery**：自定义 `AsyncIOPool`，任务直接写 `async def`，`autoretry_for`、`self.request` 均可正常使用；任务名前缀自动路由到对应服务队列。
- **Outbox 可靠投递**：业务同事务写入本服务 `outbox_message`，commit 后即时投递；Beat 每分钟补投，失败最多 3 次后标 `DEAD`，可人工重投。
- **统一响应与异常**：`Response[T]` 统一包装；`DomainError`（必须带错误码）、`RpcError`、参数校验、未知异常分别映射为一致的 JSON 结构，附带 `trace_id`。
- **缓存装饰器**：`@redis_cache.cache(...)` / `@redis_cache.invalidate(...)`，支持空值缓存、TTL 抖动、可选的防击穿锁。
- **按服务隔离的迁移**：基于 Alembic 封装，每个服务独立版本历史，自动发现模型。
- **现代工具链**：Python 3.14、uv 管理依赖、Ruff 统一代码风格。

## 架构

### 系统拓扑

```
                         ┌───────────────────────┐
           Client ─────► │   API Gateway (可选)   │  校验 JWT，注入 X-User-Id
                         └───────────┬───────────┘
              ┌──────────────────────┼──────────────────────┐
              ▼                      ▼                      ▼
       ┌─────────────┐        ┌─────────────┐        ┌─────────────┐
       │ iam_service │        │ product_svc │  RPC   │inventory_svc│
       │    :9001    │        │    :9002    │ ─────► │    :9003    │
       └──────┬──────┘        └──────┬──────┘        └──────┬──────┘
              │                      │ 投递任务              │ 投递任务
              │                      ▼                      ▼
              │               ┌─────────────────────────────────────┐
              │               │         Redis (Celery Broker)        │
              │               └──────────────────┬──────────────────┘
              │                                  ▼  队列 inventory
              │                          ┌───────────────┐
              │                          │ Celery Worker │
              │                          └───────┬───────┘
              ▼                                  ▼
       ┌──────────────────────────────────────────────────┐
       │                      MySQL                       │
       └──────────────────────────────────────────────────┘
```

### 分层

每个业务模块按五层组织，依赖方向自上而下：

| 层 | 职责 | 不应该做的事 |
|---|---|---|
| **View** | 声明路由、接收 DTO、返回 `Response[T]` | 写业务逻辑 |
| **Service** | 业务编排：调用 Domain、CRUD、其他服务，投递异步任务 | 直接拼 SQL |
| **Domain** | 纯业务规则：校验、计算、状态流转，抛 `DomainError` | 访问数据库或网络 |
| **CRUD** | 数据访问，继承 `BaseCRUD` | 业务判断 |
| **Model** | SQLAlchemy 表定义，继承 `BaseTableModel` | — |

### 一次请求经过什么

```
HTTP Request
  │
  ├─ DBSessionMiddleware   创建 Session；成功 commit，异常 rollback
  ├─ AuthMiddleware        解析身份（网关 Header 或 Bearer JWT），无凭证且非豁免接口返回 401
  ├─ TracingMiddleware     生成 / 透传 X-Trace-Id，记录慢请求
  ├─ CORSMiddleware
  │
  ▼
View → Service → Domain / CRUD
  │
  ▼
异常处理器：DomainError / RpcError / ValidationError / HTTPException / Exception → 统一 JSON
```

## 快速开始

### 环境要求

- Python 3.14+（当前被 `fastapi-typed-client>=0.2` 卡住：该库要求 ≥3.14；Celery 本身支持 3.13。若要降到 3.13，需换 RPC 客户端方案或等上游放宽版本。）
- [uv](https://docs.astral.sh/uv/)
- MySQL 8.x
- Redis 6+

### 1. 安装依赖

```bash
git clone https://github.com/CHOS1NONER/fastapi-microservice-framework.git
cd fastapi-microservice-framework
uv sync
```


### 2. 配置

```bash
cp .env.example .env
```

至少修改数据库连接和 JWT 密钥：

```ini
MYSQL_DB_URL=mysql+asyncmy://root:password@127.0.0.1:3306/test?charset=utf8mb4
REDIS_HOST=localhost
JWT_SECRET_KEY=please_change_me
```

**不会**在启动时自动建表。空库请先对各服务执行迁移（见[数据库迁移](#数据库迁移)），例如：

```bash
uv run python scripts/migrator.py init -s iam
uv run python scripts/migrator.py -s iam generate "init"
uv run python scripts/migrator.py -s iam up
```

### 3. 启动服务

在仓库根目录分别启动：

```bash
uv run python services/iam/main.py         # http://127.0.0.1:9001/iam_service/docs
uv run python services/product/main.py     # http://127.0.0.1:9002/product_service/docs
uv run python services/inventory/main.py   # http://127.0.0.1:9003/inventory_service/docs
```

### 4. 启动 Celery Worker（含 Outbox Beat）

```bash
uv run celery -A services.product.celery_worker worker -B -Q product -l info
uv run celery -A services.inventory.celery_worker worker -B -Q inventory --concurrency=20 -l info
```

Worker 已指定 `AsyncIOPool`，无需 `--pool`；`-B` 启用每分钟 Outbox 补投。

> 跨服务 RPC 默认经由 `INTRANET_GATEWAY_URL` 转发。本地没有网关时，可降级调用会返回 `None`，不影响服务启动和单服务接口调试。

## 项目结构

```
.
├── common/                        # 框架层（业务无关）
│   ├── core/                      #   ServiceBootstrap、BaseServiceSettings、运行时上下文
│   ├── base/                      #   BaseTableModel、BaseCRUD
│   ├── db/                        #   DatabaseManager、@transactional、迁移工具
│   ├── middleware/                #   DB Session、Tracing、全局异常处理
│   ├── auth/                      #   AuthMiddleware、allow_anonymous、require_auth、CurrentUser
│   ├── tasks/                     #   Celery 应用、Worker 装配、AsyncIOPool
│   ├── cache/                     #   Redis 缓存装饰器
│   └── utils/                     #   JWT、日志、密码、雪花 ID、异常类型
│
├── contract/                      # 跨服务契约：DTO、枚举、错误码、任务名
├── clients/                       # 跨服务客户端
│   ├── __init__.py                #   对外只导出 iam / product / inventory
│   └── generated/                 #   fastapi-typed-client 生成，勿手改
│
├── services/                      # 业务服务
│   ├── iam/                       #   用户 + 登录认证
│   ├── product/                   #   商品
│   └── inventory/                 #   库存
│       ├── main.py                #     HTTP 服务入口
│       ├── config.py              #     服务配置
│       ├── celery_worker.py       #     Celery Worker 入口
│       └── inventory/
│           ├── models/  crud/  domain/  service/  view/
│           └── tasks.py           #     异步任务
│
├── scripts/generate_clients.py    # 生成跨服务客户端
├── docs/                          # 专题文档
├── pyproject.toml
└── .env.example
```

## 使用指南

### 新增一个服务

**1. 配置** `services/order/config.py`

```python
from common.core.base_settings import BaseServiceSettings

class Settings(BaseServiceSettings):
    SERVICE_NAME: str = "order_service"
    HTTP_PORT: int = 9004

settings = Settings()
```

**2. 入口** `services/order/main.py`

```python
from common.core.service_bootstrap import ServiceBootstrap
from services.order.config import settings
from services.order.order.view.order_view import router as order_router

bootstrap = ServiceBootstrap(settings, service_file=__file__)
app = bootstrap.create_app()
app.include_router(order_router, prefix="/api", tags=["order"])

if __name__ == "__main__":
    bootstrap.run()
```

`ServiceBootstrap` 负责数据库连接池、日志、中间件、异常处理器、OpenAPI 鉴权声明、`/health` 健康检查和优雅关闭。需要额外的启动逻辑时覆盖 `on_startup` / `on_shutdown`，需要额外中间件时覆盖 `register_middlewares`。

**3. 业务模块** 按 `models/ → crud/ → domain/ → service/ → view/` 组织。

### 编写接口

接口统一用 `POST` + JSON Body，返回 `Response[T]`：

```python
from fastapi import APIRouter, Depends
from common.auth import require_auth
from contract.g_dto import Response

router = APIRouter(dependencies=[Depends(require_auth)])

@router.post("/product/add")
async def add(req_data: ProductAddParams) -> Response[ProductModel]:
    return Response(data=await ProductService.add(req_data))
```

业务失败直接抛 `DomainError`，框架会转成统一的错误响应：

```python
raise DomainError(msg=f"商品名称已存在: {params.product_name}")
```

### 鉴权

`AuthMiddleware` 的判定顺序：

1. 有 `X-User-Id`（网关注入或 RPC 透传）：直接采信。
2. 否则有 `Authorization: Bearer <token>`：服务自行校验 JWT，无效返回 401。
3. 都没有：只有声明了 `allow_anonymous` 的接口放行，其余返回 401。

```python
from common.auth import CurrentUser, allow_anonymous, require_auth

public_router = APIRouter(dependencies=[Depends(allow_anonymous)])   # 公开接口
router = APIRouter(dependencies=[Depends(require_auth)])             # 需要登录

@router.post("/me")
async def me(user: CurrentUser) -> Response[...]:                    # 注入当前用户
    ...
```

IAM 服务提供 `POST /api/auth/login` 与 `POST /api/auth/refresh`，采用 access / refresh 双 Token。详见 [docs/auth.md](docs/auth.md)。

### 跨服务调用

改了路由或 DTO 后重新生成客户端：

```bash
uv run python scripts/generate_clients.py
```

调用方：

```python
from clients import inventory

class ProductService:
    inventory_client = inventory()             # 可降级：失败返回 None
    inventory_strict = inventory.strict()      # 必须成功：失败抛异常，由全局处理器响应

    async def detail(cls, ...):
        inv: InventoryModel | None = await cls.inventory_client.by_product_id(params)
        quantity = inv.quantity if inv else 0
```

当前用户身份会自动透传给下游服务。详见 [docs/rpc.md](docs/rpc.md)。

### 异步任务（Celery）

**定义任务**：放在模块的 `tasks.py`，任务名的前缀就是队列名。

```python
# services/inventory/inventory/tasks.py
class InventoryTask:
    @staticmethod
    @celery_app.task(
        name="inventory.record_flow",          # 自动路由到队列 inventory
        autoretry_for=(Exception,), retry_backoff=True, max_retries=5,
    )
    @transactional                              # 任务级事务：成功提交、异常回滚
    async def record_flow(payload: dict):
        params = InventoryFlowRecordParams(**payload)
        if await flow_crud.get_one_by_fields(flow_no=params.flow_no):
            return                              # 幂等：重复投递直接跳过
        await flow_crud.create(**params.model_dump())
```

**投递任务**：

```python
# 可靠投递（推荐）：与业务同事务写本服务 outbox_message，commit 后投 Celery
from common.db.outbox import outbox
await outbox.enqueue(
    task_name="inventory.init_inventory",
    payload=payload.model_dump(mode="json"),
    message_id=f"inventory.init:{product_id}",
)

# 可丢投递：不落库，直接打 Broker
await InventoryTask.record_flow.async_delay(flow.model_dump(mode="json"))
```

Outbox 状态：`PENDING` → 投递成功 `SENT`；失败累计 `retry_count`，满 3 次 → `DEAD`（可 `outbox.retry(message_id)` 人工重投）。Celery Beat 每分钟扫本库 PENDING。

**Worker 入口**（加 `-B` 启用 Outbox 定时补投）：

```bash
uv run celery -A services.product.celery_worker worker -B -Q product -l info
uv run celery -A services.inventory.celery_worker worker -B -Q inventory -l info
```

几条约定：

- 参数只传可 JSON 序列化的数据，DTO 先 `model_dump(mode="json")`。
- Celery 保证"至少执行一次"，任务必须幂等。
- 任务名上线后不要修改，队列里可能还有旧名字的消息。
- 改了任务代码需要重启 Worker；开发环境可以消费多个队列：`-Q inventory,product`（不写 `-Q` 只会消费默认队列）。

### 缓存

```python
from common.cache.redis_cache import CacheKey, redis_cache

@redis_cache.cache(CacheKey("product:{product_id}"), ttl=300, protect_stampede=True)
async def get_product(product_id: int) -> ProductModel | None: ...

@redis_cache.invalidate(CacheKey("product:{product_id}"))
async def update_product(product_id: int, ...): ...
```

### 数据库迁移

基于 Alembic 封装，每个服务独立维护迁移历史：

```bash
uv run python scripts/migrator.py init -s iam            # 初始化（每个服务一次）
uv run python scripts/migrator.py -s iam generate "init" # 对比模型生成脚本
uv run python scripts/migrator.py -s iam up              # 升级到最新
uv run python scripts/migrator.py -s iam down 1          # 回滚 1 步
```

也可用 `uv run python -m common.db.migrator ...`。详见 [docs/migrations.md](docs/migrations.md)。

## 统一响应

成功：

```json
{ "code": 200, "msg": "", "data": { } }
```

失败：

```json
{ "code": -1, "message": "商品不存在", "trace_id": "6f1c..." }
```

| 场景 | HTTP 状态码 | `code` |
|---|---|---|
| 成功 | 200 | `200` |
| 业务失败（`DomainError`） | 200 | `-1` 或自定义错误码 |
| 下游服务失败（`RpcError`） | 200 | 下游返回的错误码 |
| 未登录 / Token 无效 | 401 | 无，响应体为 `{"detail": "Unauthorized"}` |
| 参数校验失败 | 422 | `422`，附带 `errors` |
| 未知异常 | 500 | `500` |

## 配置项

所有配置由 `BaseServiceSettings` 从仓库根目录的 `.env` 读取，环境变量优先；各服务在自己的 `config.py` 中覆盖默认值。

| 配置 | 默认值 | 说明 |
|---|---|---|
| `SERVICE_NAME` | 由服务定义 | 服务名，同时作为 docs 路径前缀与日志目录 |
| `HTTP_PORT` | 由服务定义 | 监听端口 |
| `WORKERS` | `1` | uvicorn 进程数 |
| `MYSQL_DB_URL` | — | 数据库连接串（asyncmy 驱动） |
| `DB_POOL_SIZE` / `DB_MAX_OVERFLOW` | `20` / `40` | 连接池大小 |
| `REDIS_HOST` / `REDIS_PORT` | `localhost` / `6379` | Redis 地址 |
| `CELERY_BROKER_URL` | `redis://{REDIS_HOST}:{REDIS_PORT}/1` | Celery Broker，留空使用默认值 |
| `INTRANET_GATEWAY_URL` | `http://127.0.0.1:9080` | 跨服务调用的内网网关地址 |
| `JWT_SECRET_KEY` | `change_me_in_production` | JWT 签名密钥，所有服务必须一致 |
| `JWT_ALGORITHM` | `HS256` | 签名算法 |
| `JWT_ACCESS_EXPIRE_MINUTES` | `1440` | access_token 有效期（分钟） |
| `JWT_REFRESH_EXPIRE_MINUTES` | `10080` | refresh_token 有效期（分钟） |

## 生产部署建议

- **Celery Broker 使用独立的 Redis 实例**，配置 `maxmemory-policy noeviction` 并开启 AOF，避免队列被淘汰或重启丢失。
- **替换 `JWT_SECRET_KEY`**，并确保网关、IAM 与各服务使用同一个密钥。
- 表结构一律用迁移管理（启动时 `create_all` 已关闭）。
- 可靠异步请走 Outbox；`DEAD` 消息需监控并人工重投。

## 开发

```bash
uv sync                          # 同步依赖
uv add <package>                 # 新增依赖
uvx ruff check .                 # 代码检查
uvx ruff check . --fix           # 自动修复
```

## 文档

| 文档 | 内容 |
|---|---|
| [docs/auth.md](docs/auth.md) | 登录、续签、Token 类型、网关配合 |
| [docs/rpc.md](docs/rpc.md) | 客户端生成与调用方式 |
| [docs/migrations.md](docs/migrations.md) | 按服务隔离的数据库迁移 |

## 路线图

- [x] Outbox + after_commit + Beat 定时重投（最多 3 次）
- [ ] Docker Compose 一键启动 MySQL / Redis / 全部服务
- [ ] 单元测试与 CI
- [ ] OpenTelemetry 链路追踪

## 贡献

欢迎：

- 提 **Issue**（问题、想法、踩坑经验）
- 提 **Pull Request**（需维护者 Review 后才会合并）

外部协作者**不能**直接 push 到本仓库，也没有管理权限；只能 Fork 后发 PR。完整说明见 [CONTRIBUTING.md](CONTRIBUTING.md)。

提交前请确保 `uvx ruff check .` 通过；提交信息建议遵循 [Conventional Commits](https://www.conventionalcommits.org/zh-hans/)。

## 许可证

[MIT](LICENSE) — 免费使用、修改与分发；保留版权声明即可。

## 致谢

- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Celery](https://docs.celeryq.dev/)
- [fastapi-typed-client](https://pypi.org/project/fastapi-typed-client/)
- [uv](https://docs.astral.sh/uv/) / [Ruff](https://docs.astral.sh/ruff/)
