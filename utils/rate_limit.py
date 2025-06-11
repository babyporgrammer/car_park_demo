# rate_limit.py
from slowapi import Limiter
from slowapi.util import get_remote_address

# 如果想按 X-API-Key 限流，改 key_func：
# def key_by_api_key(request):
#     return request.headers.get("X-API-Key") or get_remote_address(request)
# limiter = Limiter(key_func=key_by_api_key, default_limits=["100/minute"])

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["60/minute"]   # 全局：每 IP 每分钟 60 次
)
