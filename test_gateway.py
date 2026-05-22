import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client

async def main():
    print("Connecting to ContextForge Gateway at http://localhost:4444/sse...")
    try:
        async with sse_client("http://localhost:4444/sse") as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                print("Connected! Calling tool...")
                result = await session.call_tool("search_company_database", {"ticker": "NVDA"})
                print(f"Tool Result: {result.content[0].text}")
    except Exception as e:
        import traceback
        traceback.print_exc()

asyncio.run(main())
