import asyncio
import logging
from stitch_integration.stitch_client import StitchMCPClient

logging.basicConfig(level=logging.DEBUG)

async def main():
    client = StitchMCPClient()
    available = await client.is_available()
    print("Stitch Available:", available)

if __name__ == "__main__":
    asyncio.run(main())
