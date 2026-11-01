# 跨服务 RPC（fastapi-typed-client）

开发者只维护各服务 View。改路由或 DTO 后重新生成客户端：

```powershell
uv run python scripts/generate_clients.py
```

生成物在 `clients/generated/`，勿手改。

## 调用方式

- **可降级（默认）**：`inventory()` 返回 soft 客户端，失败为 `None`，业务不用 try：

```python
from clients import inventory

class ProductService:
    inventory_client = inventory()

    async def get_by_id(self, ...):
        inv = await self.inventory_client.by_product_id(params)
        quantity = inv.quantity if inv else 0
```

- **必须成功**：`inventory.strict()`，异常交给全局处理。

共享 `httpx2` 在 `clients` 模块内懒创建；进程退出时由 `ServiceBootstrap` 调用 `clients.aclose()`。
