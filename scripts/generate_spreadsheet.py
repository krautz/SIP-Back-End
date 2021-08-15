import asyncio

from steamapi.inventory import get_user_inventory


async def main():
    user_items = await get_user_inventory(76561198066658320, 730, "portuguese")

    import json
    print(json.dumps(user_items, indent=4, sort_keys=True))

if __name__ == "__main__":
    asyncio.run(main())
