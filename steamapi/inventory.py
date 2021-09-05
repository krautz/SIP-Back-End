import aiohttp
import asyncio

from steamapi.constants import BASE_URL, USER_INVENTOR_URL

async def get_user_inventory(steam_user_id, app_id, language = "english"):
    """
    Request Steam API an user's inventory items for a specific app.

    :param steam_user_id: user steam id, it can be found at https://store.steampowered.com/account/
    :param app_id: steam app id to retrieve items from. 730 is CS:GO.
    :param language: language to retrieve item names.

    :returns: list of dictionary with item data (name, quantity, id(market_hash_name))
    """
    # obtain user's inventory
    user_inventory_url = USER_INVENTOR_URL.format(
        steam_user_id = steam_user_id, app_id = app_id, language = language
    )
    async with aiohttp.ClientSession() as session:
        async with session.get(user_inventory_url) as response:
            user_items_api_response = await response.json()

    # get user tradable items
    user_items = {}
    for api_item in user_items_api_response["descriptions"]:
        if api_item["marketable"] == 1:
            item_class_id = api_item["classid"]
            user_items[item_class_id] = {
                "amount": 0,  # amount is present on api response assets. just initializing it.
                "app_id": api_item["appid"],  # game code that has the item
                "market_hash_name": api_item["market_hash_name"],  # item 'id' to requst price later
                "name": api_item["market_name"],  # item human friendly name
            }

    # get amount of each user items
    for api_asset in user_items_api_response["assets"]:
        item_class_id = api_asset["classid"]

        # skip items not present in user items (i.e. not tradable ones)
        if user_item := user_items.get(item_class_id):
            user_item["amount"] += int(api_asset["amount"])

    return list(user_items.values())
