# utils/test_csmoney_api.py
import asyncio
import aiohttp
import json
from datetime import datetime


async def test_endpoint(session, url, description):
    """Test a CS.MONEY API endpoint"""
    print(f"\n{'='*60}")
    print(f"Testing: {description}")
    print(f"URL: {url}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Origin': 'https://cs.money',
        'Referer': 'https://cs.money/',
    }
    
    try:
        async with session.get(url, headers=headers, timeout=10) as response:
            print(f"Status: {response.status}")
            print(f"Headers: {dict(response.headers)}")
            
            if response.status == 200:
                data = await response.json()
                print(f"✓ Success! Response structure:")
                print(f"  Keys: {list(data.keys()) if isinstance(data, dict) else 'List response'}")
                if isinstance(data, dict):
                    for key, value in data.items():
                        if isinstance(value, list):
                            print(f"  {key}: List with {len(value)} items")
                        elif isinstance(value, dict):
                            print(f"  {key}: Dict with keys {list(value.keys())}")
                        else:
                            print(f"  {key}: {type(value).__name__}")
                return True
            else:
                text = await response.text()
                print(f"✗ Failed with status {response.status}")
                print(f"Response: {text[:200]}")
                
    except aiohttp.ClientConnectorError as e:
        print(f"✗ Connection error: {e}")
    except Exception as e:
        print(f"✗ Error: {type(e).__name__}: {e}")
    
    return False


async def discover_api():
    """Try to discover the current CS.MONEY API structure"""
    
    async with aiohttp.ClientSession() as session:
        # Test various possible endpoints
        endpoints = [
            # Old endpoints
            ("https://inventories.cs.money/5.0/load_bots_inventory/730?limit=10", "Old inventory API"),
            ("https://inventories.cs.money/", "Old inventory base"),
            
            # New possible endpoints
            ("https://cs.money/", "Main site"),
            ("https://api.cs.money/", "API base"),
            ("https://cs.money/api/", "Alternative API path"),
            ("https://cs.money/1.0/market/buy-orders?game=csgo&limit=10", "New market API v1"),
            ("https://cs.money/market/buy-orders?game=csgo&limit=10", "Market API without version"),
            ("https://cs.money/api/market/items?game=csgo&limit=10", "Market items API"),
            ("https://api.cs.money/market/items?game=csgo&limit=10", "API subdomain market items"),
            
            # GraphQL endpoints
            ("https://cs.money/graphql", "GraphQL endpoint"),
            ("https://api.cs.money/graphql", "API GraphQL endpoint"),
            
            # Wiki endpoints (for base prices)
            ("https://wiki.cs.money/graphql", "Wiki GraphQL endpoint"),
        ]
        
        working_endpoints = []
        
        for url, desc in endpoints:
            if await test_endpoint(session, url, desc):
                working_endpoints.append((url, desc))
                
        print(f"\n{'='*60}")
        print(f"Summary: {len(working_endpoints)}/{len(endpoints)} endpoints working")
        print("\nWorking endpoints:")
        for url, desc in working_endpoints:
            print(f"  ✓ {desc}: {url}")


async def test_with_proxy():
    """Test CS.MONEY API through proxy"""
    from proxy_http.proxy import Proxy
    from proxy_http.aiohttp_session_factory import AiohttpSessionFactory
    
    proxies = [
        "http://modeler_YxBu4X:Gr9ZSzHPb0Eq@62.109.29.75:11667",
        "http://modeler_vxakY5:yKDtbsh46ytZ@62.109.29.75:11668"
    ]
    
    print("\n" + "="*60)
    print("Testing with proxies...")
    
    for proxy_str in proxies:
        proxy = Proxy(proxy=proxy_str)
        session = AiohttpSessionFactory.create_session_with_proxy(proxy)
        
        try:
            await test_endpoint(
                session, 
                "https://cs.money/", 
                f"CS.MONEY via proxy {proxy_str}"
            )
        finally:
            await session.close()


async def main():
    print(f"CS.MONEY API Discovery Tool")
    print(f"Started at: {datetime.now()}")
    
    # Test direct connections
    await discover_api()
    
    # Test with proxies
    await test_with_proxy()


if __name__ == "__main__":
    asyncio.run(main())