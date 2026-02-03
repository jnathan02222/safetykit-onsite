from integrations.wikipedia import Wikipedia
import asyncio
from integrations.inspired import Inspired


async def main():
    await Inspired().sync()


if __name__ == "__main__":
    asyncio.run(main())
