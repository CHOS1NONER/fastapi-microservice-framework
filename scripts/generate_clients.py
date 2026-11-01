"""从各服务 FastAPI app 生成 typed RPC 客户端。改 View 后执行: uv run python scripts/generate_clients.py"""

from __future__ import annotations

import ast
import importlib
import re
import sys
from pathlib import Path

from fastapi_typed_client import generate_fastapi_typed_client

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "clients" / "generated"

TARGETS = (
    ("services.iam.main:app", "IamClient", "iam_client.py"),
    ("services.product.main:app", "ProductClient", "product_client.py"),
    ("services.inventory.main:app", "InventoryClient", "inventory_client.py"),
)

_CONTRACT_MODULES = (
    "contract.g_dto",
    "contract.g_enum",
    "contract.auth.auth_dto",
    "contract.user.user_dto",
    "contract.product.product_dto",
    "contract.inventory.inventory_dto",
    "contract.order.order_dto",
)

_IMPORT_BLOCK_RE = re.compile(
    r"from\s+(?P<mod>[\w.]+)\s+import\s*\((?P<body>.*?)\)",
    re.DOTALL,
)
_GENERIC_IMPORT_RE = re.compile(r"^(?:Response|ListResult|PageResult)\[.+\]$")
_TYPE_NAME_RE = re.compile(r"\b([A-Z][A-Za-z0-9_]*)\b")
_SKIP_NAMES = frozenset(
    {
        "Any",
        "Literal",
        "HTTPStatus",
        "HTTPMethod",
        "FastAPIClientResult",
        "FastAPIClientUnexpectedStatus",
        "FastAPIClientUnexpectedBody",
        "FastAPIClientHTTPValidationError",
        "FastAPIClientExtensions",
        "Response",
    }
)


def _resolve_symbol(name: str) -> str | None:
    for mod_name in _CONTRACT_MODULES:
        mod = importlib.import_module(mod_name)
        if hasattr(mod, name):
            return mod_name
    return None


def _collect_type_names(expr: str) -> set[str]:
    return {
        name
        for name in _TYPE_NAME_RE.findall(expr)
        if name not in _SKIP_NAMES and name not in {"True", "False", "None"}
    }


def _fix_response_generics(source: str) -> str:
    """fastapi-typed-client 会把 Response[T] 写成非法 import，拆开并按符号归属补导入。"""
    if "from __future__ import annotations" not in source:
        source = "from __future__ import annotations\n\n" + source

    extras: dict[str, set[str]] = {}

    def rewrite(match: re.Match[str]) -> str:
        mod = match.group("mod")
        body = match.group("body")
        names = [n.strip().rstrip(",") for n in body.splitlines() if n.strip()]
        plain: list[str] = []
        saw_generic = False
        for name in names:
            if _GENERIC_IMPORT_RE.match(name):
                saw_generic = True
                for param in _collect_type_names(name):
                    owner = _resolve_symbol(param)
                    if owner:
                        extras.setdefault(owner, set()).add(param)
                continue
            plain.append(name)

        if mod.endswith(".g_dto") and saw_generic:
            items = ["Response", "ListResult", "PageResult", *plain]
            # 只保留本模块真实存在的符号
            g_dto = importlib.import_module("contract.g_dto")
            items = [n for n in dict.fromkeys(items) if hasattr(g_dto, n)]
            return "from contract.g_dto import (\n" + "".join(f"    {n},\n" for n in items) + ")"

        if not plain:
            return ""
        return f"from {mod} import (\n" + "".join(f"    {n},\n" for n in plain) + ")"

    fixed = _IMPORT_BLOCK_RE.sub(rewrite, source)

    # 正文里的嵌套泛型：Response[ListResult[UserModel]] 等
    for expr in re.findall(r"Response\[(?:[^\[\]]|\[[^\]]*\])+\]", fixed):
        for param in _collect_type_names(expr):
            owner = _resolve_symbol(param)
            if owner:
                extras.setdefault(owner, set()).add(param)

    header_end = fixed.find("\nclass ")
    header = fixed[:header_end] if header_end != -1 else fixed
    rest = fixed[header_end:] if header_end != -1 else ""

    for mod_name, names in sorted(extras.items()):
        existing = set()
        mod_match = re.search(
            rf"from\s+{re.escape(mod_name)}\s+import\s*\((.*?)\)",
            header,
            re.DOTALL,
        )
        if mod_match:
            existing = {
                n.strip().rstrip(",")
                for n in mod_match.group(1).splitlines()
                if n.strip()
            }
            missing = sorted(names - existing)
            if not missing:
                continue
            new_body = mod_match.group(1).rstrip() + "".join(f"\n    {n}," for n in missing) + "\n"
            header = (
                header[: mod_match.start(1)] + new_body + header[mod_match.end(1) :]
            )
        else:
            block = (
                f"from {mod_name} import (\n"
                + "".join(f"    {n},\n" for n in sorted(names))
                + ")\n"
            )
            header = header.rstrip() + "\n" + block + "\n"

    # 去掉被错误塞进错误模块的符号
    def scrub(match: re.Match[str]) -> str:
        mod = match.group("mod")
        body = match.group("body")
        kept = []
        for raw in body.splitlines():
            name = raw.strip().rstrip(",")
            if not name:
                continue
            owner = _resolve_symbol(name)
            if owner and owner != mod and name[0].isupper():
                continue
            kept.append(name)
        if not kept:
            return ""
        return f"from {mod} import (\n" + "".join(f"    {n},\n" for n in kept) + ")"

    header = _IMPORT_BLOCK_RE.sub(scrub, header)
    # 校验语法
    ast.parse(header + rest)
    return header + rest


def generate_one(app_import: str, title: str, filename: str) -> Path:
    out = OUT_DIR / filename
    generate_fastapi_typed_client(
        app_import,
        output_path=out,
        title=title,
        async_=True,
        import_client_base=True,
    )
    text = out.read_text(encoding="utf-8")
    out.write_text(_fix_response_generics(text), encoding="utf-8")
    return out


def main() -> int:
    sys.path.insert(0, str(ROOT))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "__init__.py").write_text(
        '"""fastapi-typed-client 生成，勿手改；重跑 scripts/generate_clients.py。"""\n',
        encoding="utf-8",
    )
    for app_import, title, filename in TARGETS:
        path = generate_one(app_import, title, filename)
        print(f"generated {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
