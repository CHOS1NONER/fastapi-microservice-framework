## 数据库迁移使用手册（按微服务隔离）

本手册说明本项目中基于 Alembic 封装的“按微服务独立迁移”方案的使用方式，适用于 `services/iam`、`services/product` 等所有微服务。

---

## 一、整体设计概览

- **按服务隔离**：每个微服务拥有独立的 `migrations/` 目录和版本历史。
- **自动发现模型**：只扫描当前服务目录下的 `models/` 目录，加载继承自 `Base` 的表模型。
- **服务级 DB 配置**：从 `services.<service>.main.settings.DB_URL` 动态获取数据库连接。
- **统一入口脚本**：`uv run python scripts/migrator.py`（等价于 `uv run python -m common.db.migrator`）。
- **启动不建表**：服务 / Worker 已关闭 `create_all`，空库必须先 `init` + `generate` + `up`。

目录关系示例：

- `common/db/migrator/`：迁移通用逻辑（CLI、配置、模型加载、模板）
- `services/iam/migrations/`：`iam` 服务的迁移目录
- `services/product/migrations/`：`product` 服务的迁移目录
- `common/db/outbox_model.py`：框架级 `outbox_message`；迁移模板会显式 import，随各服务迁移一并建表

---

## 二、快速开始（以 iam 服务为例）

### 1. 初始化迁移目录（每个服务只需一次）

```bash
uv run python -m common.db.migrator init -s iam
```

效果：

- 创建 `services/iam/migrations/`
- 复制模板：
  - `env.py`
  - `script.py.mako`
- 创建 `services/iam/migrations/versions/` 目录和 `.gitkeep`

### 2. 编写或修改模型

- 在 `services/iam/**/models/` 目录下新增或修改模型文件。
- 模型类需继承 `common.base.base_table_model.Base`（或其子类），否则不会被迁移系统识别。

### 3. 生成迁移脚本（自动对比 Model 与 DB）

```bash
uv run python -m common.db.migrator -s iam generate "init user table"
```

- 将在 `services/iam/migrations/versions/` 下生成一个新的迁移脚本。
- **务必打开脚本检查和调整**：尤其是涉及删除字段/表时，按“只加不删”规范人工修改。

### 4. 执行迁移（升级到最新）

```bash
uv run python -m common.db.migrator -s iam up
```

- 会连接 `iam` 服务对应的数据库，执行所有未执行的迁移，升级到最新版本（`head`）。

---

## 三、命令一览

所有命令默认入口为：

```bash
uv run python -m common.db.migrator <子命令> [参数]
```

也可以等价使用：

```bash
python -m common.db.migrator <子命令> [参数]
```

### 1. 列出所有微服务

```bash
uv run python -m common.db.migrator list
```

- 扫描 `services/` 目录下的子目录，打印可用服务名（例如 `iam`、`product`）。

### 2. 初始化服务迁移目录

```bash
uv run python -m common.db.migrator init -s iam
```

- 初始化指定服务的 `migrations/` 目录（只做一次）。

### 3. 自动生成迁移脚本

```bash
uv run python -m common.db.migrator -s iam generate "描述信息"
```

- 只对当前服务的模型与数据库结构做 diff，生成迁移脚本。
- 内部步骤：
  - 设置环境变量 `MIGRATE_SERVICE=iam`
  - 扫描 `services/iam` 下所有 `models` 目录，动态导入模型
  - 使用 `Base.metadata` 与当前数据库做对比（`autogenerate=True`）

> **建议**：生成后手动检查升级/降级逻辑，避免误删字段/表。

### 4. 执行所有待执行迁移（升级）

```bash
uv run python -m common.db.migrator -s iam up
```

- 等价于 Alembic 的 `upgrade head`。
- 实际会连库执行迁移脚本中的 `upgrade()`。

### 5. 回滚迁移（降级）

```bash
# 回滚最近 1 步
uv run python -m common.db.migrator -s iam down

# 回滚最近 3 步
uv run python -m common.db.migrator -s iam down 3

# 回滚到最初始版本（base）
uv run python -m common.db.migrator -s iam down base
```

- 内部转换为 Alembic 的：
  - `downgrade -1`
  - `downgrade -3`
  - `downgrade base`

### 6. 查看迁移历史

```bash
uv run python -m common.db.migrator -s iam history
```

- 展示当前服务的所有迁移版本及其顺序。

### 7. 查看当前版本

```bash
uv run python -m common.db.migrator -s iam current
```

- 显示当前数据库所处的 revision。

---

## 四、多服务与配置约定

### 1. 服务列表发现

- 通过 `common/db/migrator/config.py` 中的 `list_services()`：
  - 扫描 `services/` 目录下所有**非下划线开头**的子目录；
  - 作为可用服务名（如 `iam`、`product`）。

### 2. 每个服务必须提供的配置

在 `services/<service>/main.py` 中：

- 必须有一个 `settings` 对象；
- 且包含 `DB_URL` 属性，例如：

```python
DB_URL = "mysql+pymysql://user:password@host:3306/iam_db"
```

迁移时会通过 `get_db_url_for_service(service_name)` 获取对应服务的 `DB_URL`。

### 3. 模型发现约定

- 仅扫描当前服务根目录下的所有 `models` 目录：
  - 例如 `services/iam/user/models/`、`services/product/order/models/` 等。
- 只导入该目录中的 `.py` 文件（排除 `__init__.py`）。
- 生成模块名类似 `services.iam.user.models.user`。
- 框架表 `outbox_message`（`common.db.outbox_model`）由迁移模板显式导入，不依赖服务目录扫描。

> **要点**：  
> - 业务模型文件要放在服务内的 `models/` 目录  
> - 模型类要继承 `Base`，才能被收集进 `Base.metadata`，被迁移系统识别  
> - 若某服务从不使用 Outbox，生成的迁移里仍可能出现 `outbox_message`（模板统一挂载）；可手工从脚本中删掉，或保留空表无妨

---

## 五、在线迁移与离线迁移

### 1. 在线迁移（Online）

- **目前通过本工具执行的所有 `up/down/history/current` 命令都是在线迁移**。
- 特点：
  - 使用 `engine_from_config` 建立真实数据库连接；
  - 在事务中执行迁移脚本中的 `upgrade()` / `downgrade()`；
  - 更新 Alembic 版本表（`alembic_version`）记录当前 revision。
- 适合：
  - 开发环境、本地环境；
  - 测试环境；
  - 对联机变更可接受的生产环境。

### 2. 离线迁移（Offline）

- 目标：不直接连数据库，而是**生成 SQL 语句**，由 DBA 审核和执行。
- 区分方式：
  - Alembic 通过 `context.is_offline_mode()` 判断；
  - 当以 `--sql` 模式调用 Alembic 时，进入离线模式，使用 `run_migrations_offline()`：
    - 不创建 DB 连接；
    - 把要执行的 SQL 输出为文本。
- 当前 CLI 暂未直接暴露 `--sql` 子命令，如需要，可扩展为：
  - `up-sql`：生成从当前版本升级到 `head` 的 SQL；
  - `down-sql`：生成回滚 SQL；
  - 然后重定向到文件，由 DBA 在生产库执行。

---

## 六、数据回填与“只加不删”的最佳实践

### 1. 结构迁移（只加不删）

**推荐生产环境遵守“只加不删（或只加不改）”的结构迁移原则：**

- 在迁移脚本的 `upgrade()` 中：
  - 只做 `create_table`、`add_column`、`add_index` 等“向前兼容”的操作；
- 对于自动生成的迁移：
  - 如果 Alembic 检测到模型里删了字段/表，可能会生成 `DROP COLUMN` / `DROP TABLE` 语句；
  - **务必人工删除这些危险操作**，保持迁移脚本安全。

### 2. 数据回填（Data Backfill）

- 支持在迁移脚本中直接写数据回填逻辑，例如：

```python
def upgrade():
    # 1. 结构变更
    op.add_column("user", sa.Column("nickname", sa.String(length=64), nullable=True))

    # 2. 数据回填
    conn = op.get_bind()
    conn.execute(sa.text("update user set nickname = username where nickname is null"))
```

- 适用：
  - 数据量中小的场景；
  - 可接受迁移执行一段时间的场景。
- 对于数据量特别大的表，建议：
  - 结构迁移只做“加字段”；
  - 回填逻辑在单独的离线任务/Job 中分批执行。

### 3. 双写与切读的配合

- “双写/切读”属于业务层策略，这套迁移系统不直接实现，但可以很好配合：
  - **第一阶段**：迁移只加新字段/新表，不动旧结构；
  - **第二阶段**：Service 写入同时写 old + new（双写），读仍从旧结构；
  - **第三阶段**：数据对账，逐步切读到新结构（业务开关控制）；
  - **第四阶段**：稳定后，再生成一次迁移脚本，在合适时机删除旧结构（或者保留不删）。

---

## 七、典型工作流示例

以一次“新增字段 + 回填 + 切读”为例：

1. **设计字段**  
   在 `services/iam/user/models/user.py` 中新增字段。

2. **生成迁移**  

   ```bash
   uv run python -m common.db.migrator -s iam generate "add user.nickname"
   ```

3. **编辑迁移脚本**  
   - 在 `upgrade()` 中：
     - 写 `op.add_column(...)`；
     - 写必要的数据回填 SQL；
   - 在 `downgrade()` 中：
     - 写可安全回滚的逻辑（本地/测试环境用），生产可视需要简化。

4. **执行迁移**

   ```bash
   uv run python -m common.db.migrator -s iam up
   ```

5. **业务上线双写**  
   修改 Service 层，写入同时更新旧字段和新字段。

6. **灰度切读**  
   通过配置开关控制读是否从新字段读取，对齐数据并做监控。

7. **清理旧结构（可选）**  
   确认新结构稳定后，再生成一次迁移，仅用于删除旧字段/旧表（或根据团队规范选择保留）。


