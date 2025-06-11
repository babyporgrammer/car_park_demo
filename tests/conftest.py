# tests/conftest.py
import pytest
from utils.rate_limit import limiter        # 你项目里唯一的 Limiter 实例

# ---------- 工具函数 ---------- #
def _flush_storage():
    """
    尝试把 MemoryStorage/WrappedStorage 清零。
    不同版本 slowapi / limits 的实现稍有差异，所以逐个兜底。
    """
    store = getattr(limiter, "storage", None) or getattr(limiter, "_storage", None)
    if store is None:
        return

    # 1) 新版 limits 有 reset()/flush()
    for m in ("reset", "flush", "clear_all"):
        if hasattr(store, m):
            getattr(store, m)()
            return

    # 2) 直接操作底层 dict
    for attr in ("_storage", "storage"):
        d = getattr(store, attr, None)
        if isinstance(d, dict):
            d.clear()
            return

@pytest.fixture(autouse=True)
def rate_limit_handling(request, monkeypatch):
    """
    • 默认：限流保持 **开启**，但在测试前后把计数器清零，避免跨测试串号
    • 若测试打标记 @pytest.mark.no_rate_limit → 关闭限流（开启端点功能测试）
    """
    want_disabled = request.node.get_closest_marker("no_rate_limit") is not None

    # ---------- ❶ 关闭 / 打开开关 ---------- #
    if hasattr(limiter, "enabled"):
        # 官方提供的总闸门（slowapi >=0.1.9)
        original_enabled = limiter.enabled
        limiter.enabled = not want_disabled
    else:
        # 老版本无 enabled，就把 limit(...) 装饰器挂的 runtime check stub 掉
        if want_disabled:
            # decorator 在导入时已包好，只能把“检查函数”替换成 no-op
            for attr in ("_check_request_limit", "_evaluate_limits",
                         "check_request_limit", "_check_request"):
                if hasattr(limiter, attr):
                    monkeypatch.setattr(limiter, attr,
                                        lambda *a, **kw: None, raising=True)
                    break

    # ---------- ❷ 每次测试前清零计数器 ---------- #
    _flush_storage()

    yield                             # ---- 运行测试 ----

    # ---------- ❸ 还原限流状态 & 再清一次 ---------- #
    _flush_storage()
    if hasattr(limiter, "enabled"):
        limiter.enabled = original_enabled
