import asyncio
import os

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
    
    # Clear existing proxies
    existing = await storage.get_all()
    for proxy in existing:
        await storage.remove(proxy)
    print(f"Removed {len(existing)} existing proxies from {key}")
    
    # Load new proxies
    count = 0
    if os.path.exists(file):
        with open(file, "r", encoding="utf8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    try:
                        proxy = Proxy(proxy=line)
                        await storage.add(proxy)
                        count += 1
                        print(f"Added proxy: {proxy}")
                    except Exception as e:
                        print(f"Failed to add proxy {line}: {e}")
    else:
        print(f"Warning: File {file} not found!")
    
    print(f"Successfully filled {count} proxies for {key}")


async def main():
    redis = RedisConnector.create(
        host=EnvVar.get("REDIS_HOST"),
        port=EnvVar.get("REDIS_PORT"),
        db=EnvVar.get("REDIS_DB"),
        password=EnvVar.get("REDIS_PASSWORD"),
    )
    
    await fill_proxies(redis, _STEAM_PROXIES, _STEAM_PROXIES_KEY)
    await fill_proxies(redis, _CSMONEY_PROXIES, _CSMONEY_PROXIES_KEY)


if __name__ == "__main__":
    asyncio.run(main())