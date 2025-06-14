import asyncio
import aiohttp
from proxy_http.proxy import Proxy
from proxy_http.aiohttp_session_factory import AiohttpSessionFactory


async def test_proxy(proxy_str: str, test_url: str = "https://inventories.cs.money/"):
    """Test if proxy can connect to CS.MONEY"""
    print(f"\nTesting proxy: {proxy_str}")
    
    try:
        proxy = Proxy(proxy=proxy_str)
        session = AiohttpSessionFactory.create_session_with_proxy(proxy)
        
        async with session.get(test_url, timeout=30) as response:
            print(f"✓ Success! Status: {response.status}")
            print(f"  Headers: {dict(response.headers)}")
            return True
            
    except aiohttp.ClientProxyConnectionError as e:
        print(f"✗ Proxy connection error: {e}")
    except aiohttp.ClientConnectorError as e:
        print(f"✗ Connection error: {e}")
    except Exception as e:
        print(f"✗ Error: {type(e).__name__}: {e}")
    finally:
        if 'session' in locals():
            await session.close()
    
    return False


async def test_direct_connection(test_url: str = "https://inventories.cs.money/"):
    """Test direct connection without proxy"""
    print(f"\nTesting direct connection to: {test_url}")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(test_url, timeout=30) as response:
                print(f"✓ Direct connection success! Status: {response.status}")
                return True
    except Exception as e:
        print(f"✗ Direct connection failed: {type(e).__name__}: {e}")
    
    return False


async def main():
    print("CS.MONEY Proxy Tester")
    print("=" * 50)
    
    # Test direct connection first
    await test_direct_connection()
    
    # Test proxies
    proxies = [
        "http://modeler_YxBu4X:Gr9ZSzHPb0Eq@62.109.29.75:11667",
        "http://modeler_vxakY5:yKDtbsh46ytZ@62.109.29.75:11668"
    ]
    
    working_proxies = []
    for proxy in proxies:
        if await test_proxy(proxy):
            working_proxies.append(proxy)
    
    print(f"\n{len(working_proxies)}/{len(proxies)} proxies working")
    
    # Test alternative URLs
    print("\nTesting alternative URLs...")
    alt_urls = [
        "https://cs.money/",
        "https://google.com/",
        "https://steamcommunity.com/"
    ]
    
    for url in alt_urls:
        if working_proxies:
            await test_proxy(working_proxies[0], url)


if __name__ == "__main__":
    asyncio.run(main())