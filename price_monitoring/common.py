from time import time
from typing import List

from aiohttp import ClientSession

from proxy_http.aiohttp_session_factory import AiohttpSessionFactory
from proxy_http.async_proxies_concurrent_limiter import AsyncSessionConcurrentLimiter
from proxy_http.proxy import Proxy


def create_limiter(proxies: List[Proxy]) -> AsyncSessionConcurrentLimiter:
    """Create a concurrent limiter with sessions for all proxies."""
    sessions = []
    
    # Add sessions with proxies
    for proxy in proxies:
        session = AiohttpSessionFactory.create_session_with_proxy(proxy)
        sessions.append(session)
    
    # If no proxies, add a direct connection session
    if not sessions:
        session = AiohttpSessionFactory.create_session()
        sessions.append(session)
    
    return AsyncSessionConcurrentLimiter(sessions, time())