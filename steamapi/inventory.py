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
    class_id_to_hash_name = {}
    for api_item in user_items_api_response["descriptions"]:
        if api_item["marketable"] == 1:
            item_class_id = api_item["classid"]
            item_market_hash_name = api_item["market_hash_name"]
            user_items[item_market_hash_name] = {
                "amount": 0,  # amount is present on api response assets. just initializing it.
                "app_id": api_item["appid"],  # game code that has the item
                "market_hash_name": item_market_hash_name,  # item 'id' to requst price later
                "name": api_item["market_name"],  # item human friendly name
            }
            class_id_to_hash_name[item_class_id] = item_market_hash_name

    # get amount of each user items
    for api_asset in user_items_api_response["assets"]:
        item_class_id = api_asset["classid"]
        item_market_hash_hame = class_id_to_hash_name.get(item_class_id)

        # skip items not present in user items (i.e. not tradable ones)
        if item_market_hash_hame:
            user_items[item_market_hash_hame]["amount"] += int(api_asset["amount"])

    return list(user_items.values())
