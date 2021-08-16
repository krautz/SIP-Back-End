import aiohttp
import asyncio

from collections import defaultdict

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
    user_items = []
    for api_item in user_items_api_response["descriptions"]:
        if api_item["tradable"] == 1:
            user_items.append({
                "app_id": api_item["appid"],
                "class_id": api_item["classid"],
                "market_hash_name": api_item["market_hash_name"],
                "name": api_item["market_name"],
            })

    # get ammount of each user items, mapped by item classid
    user_items_quantities = defaultdict(lambda: 0)
    for api_asset in user_items_api_response["assets"]:
        class_id = api_asset["classid"]
        user_items_quantities[class_id] += int(api_asset["amount"])

    # add to user items the amount of each item
    for user_item in user_items:
        class_id = user_item["class_id"]
        user_item["amount"] = user_items_quantities[class_id]

    return user_items
