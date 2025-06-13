#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio

from common.env_var import EnvVar
from common.redis_connector import RedisConnector
from proxy_http.proxy import Proxy
from price_monitoring.storage.proxy import RedisProxyStorage

_STEAM_PROXIES = "utils_mount/steam_proxies.txt"
_CSMONEY_PROXIES = "utils_mount/csmoney_proxies.txt"
_STEAM_PROXIES_KEY = "steam_proxies"
_CSMONEY_PROXIES_KEY = "csmoney_proxies"


async def fill_proxies(redis, file, key):
    storage = RedisProxyStorage(redis, key)
    # Remove old proxies
    old_proxies = await storage.get_all()
    for proxy in old_proxies:
        await storage.remove(proxy)
    
    # Load new proxies
    new_proxies_count = 0
    with open(file, "r", encoding="utf8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            proxy = Proxy(proxy=line)
            await storage.add(proxy)
            new_proxies_count += 1
    
    print(f"Successfully filled {new_proxies_count} proxies for {key}")


async def main():
    redis = RedisConnector.create(
        host=EnvVar.get("REDIS_HOST"),
        port=EnvVar.get("REDIS_PORT"),  
        db=EnvVar.get("REDIS_DB"),
        password=EnvVar.get("REDIS_PASSWORD"),
    )
    for file, key in zip(
        [_STEAM_PROXIES, _CSMONEY_PROXIES], [_STEAM_PROXIES_KEY, _CSMONEY_PROXIES_KEY]
    ):
        await fill_proxies(redis, file, key)


if __name__ == "__main__":
    asyncio.run(main())