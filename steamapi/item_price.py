import aiohttp
import asyncio
import json

from datetime import datetime
from time import time

from steamapi.constants import (
    BASE_URL,
    ITEM_PRICE_HISTORY_URL,
    ITEM_PRICE_OVERVIEW_URL,
    ITEM_PRICE_MARKET_HMTL_URL,
    CURRENCIES,
)


##
# Functions to get the price of a single item
##
async def _add_item_price_from_history(session, item, currency):
    """
    Request Steam API item price history through history API.
    This API provides the median sold value of each day for old days and median sold value per hour
    on recent days (last 2~3 months)
    Add it to item dict in-place.
    The problem of this approach is that it needs the user to be logged in the browser to work :(
    (it uses login cookies to work)

    :param session: asyncIO session to make the request
    :param item: item dictionary with app_id and market_hash_name keys.
    :param currency: currency to retrieve the price.

    :returns: nothing (set the price in-place on each item dict).
    """
    # set item price url
    item_price_url = ITEM_PRICE_HISTORY_URL.format(
        app_id = item["app_id"],
        market_hash_name = item["market_hash_name"],
        currency = currency,
    )

    # set item price date and timestamp
    item["price_date"] = datetime.utcnow().strftime("%Y-%m-%d")
    item["price_date_timestamp"] = int(time())

    # request item price and in-place add it to the item dict
    async with session.get(item_price_url) as response:
        api_response = await response.json()
        if api_response and api_response.get("success"):
            item["price_unitary"] = api_response["prices"][-1][1]
            item["api_error"] = "no"
        else:
            item["price_unitary"] = 0
            item["api_error"] = "yes"
            print(f"status: {response.status}")
            print(f"Error retrieving price {item['name']} - {item['market_hash_name']}")


async def _add_item_price_from_overview(session, item, currency):
    """
    Request Steam API item last sold lowest price through overview API.
    Add it to item dict in-place.
    The problem of this approach is that steam rate limit requests pretty quickly :(

    :param session: asyncIO session to make the request
    :param item: item dictionary with app_id and market_hash_name keys.
    :param currency: currency to retrieve the price.

    :returns: nothing (set the price in-place on each item dict).
    """
    # set item price url
    item_price_url = ITEM_PRICE_OVERVIEW_URL.format(
        app_id = item["app_id"],
        market_hash_name = item["market_hash_name"],
        currency = currency,
    )

    # set item price date and timestamp
    item["price_date"] = datetime.utcnow().strftime("%Y-%m-%d")
    item["price_date_timestamp"] = int(time())

    # request item price and in-place add it to the item dict
    async with session.get(item_price_url) as response:
        api_response = await response.json()
        if api_response and api_response.get("success"):
            item["price_unitary"] = float(api_response["median_price"].split()[1])
            item["api_error"] = "no"
        else:
            item["price_unitary"] = 0
            item["api_error"] = "yes"
            print(f"status: {response.status}")
            print(f"Error retrieving price {item['name']} - {item['market_hash_name']}")


async def _add_item_price_from_market_html(session, item, currency = None):
    """
    Request Steam web market item lsiting.
    There, we can extract the price history from the html.
    Add it to item dict in-place.
    The problem with

    :param session: asyncIO session to make the request
    :param item: item dictionary with app_id and market_hash_name keys.
    :param currency: currency to retrieve the price. This is not working. Just keeping it to make
                     all add functions with the same ammount of parameters

    :returns: nothing (set the price in-place on each item dict).
    """
    # set item price url
    item_price_url = ITEM_PRICE_MARKET_HMTL_URL.format(
        app_id = item["app_id"],
        market_hash_name = item["market_hash_name"],
    )

    # set item price date and timestamp
    item["price_date"] = datetime.utcnow().strftime("%Y-%m-%d")
    item["price_date_timestamp"] = int(time())

    # request item price and in-place add it to the item dict
    async with session.get(item_price_url) as response:
        api_response = await response.text()
        history_start_index = api_response.find("[[")
        history_end_index = api_response.find("\"]];")

        if history_start_index != -1 and history_end_index != -1:
            item_price_history = json.loads(api_response[history_start_index:history_end_index+3])
            item["price_unitary"] = item_price_history[-1][1]
            item["api_error"] = "no"
        else:
            item["price_unitary"] = 0
            item["api_error"] = "yes"
            print(f"status: {response.status}")
            print(f"Error retrieving price {item['name']} - {item['market_hash_name']}")


ITEM_PRICE_SOURCE_TO_REQUESTER = {
    "html": _add_item_price_from_market_html,
    "history": _add_item_price_from_history,
    "overview": _add_item_price_from_overview,
}


##
# Function to get price for a batch of items
##
async def _add_items_price_parallel(items, currency = CURRENCIES["BRL"], source = "html"):
    """
    Request Steam API items last sold price and the date 'in parallel'.
    Add it to item dict in-place.
    The problem with this approach is that steam API returns 429 error - too many requests :(

    :param items: list of items dictionaries with app_id and market_hash_name keys.
    :param currency: currency to retrieve the price.
    :param source: source to get information from. One of "overview", "history", "html"

    :returns: nothing (set the price in-place on each item dict).
    """
    # retrieve item price requester
    item_price_requeter = ITEM_PRICE_SOURCE_TO_REQUESTER.get(source, "html")

    # obtain each item price in-place and 'in parallel'
    async with aiohttp.ClientSession() as session:
        tasks = []
        for item in items:
            tasks.append(
                asyncio.ensure_future(item_price_requeter(session, item, currency))
            )
        await asyncio.gather(*tasks)


async def _add_items_price_linear(items, currency = CURRENCIES["BRL"], source = "html"):
    """
    Request Steam API items last sold price and the date awaiting 11 second between requests.
    Add it to item dict in-place.

    :param items: list of items dictionaries with app_id and market_hash_name keys.
    :param currency: currency to retrieve the price.
    :param source: source to get information from. One of "overview", "history", "html"

    :returns: nothing (set the price in-place on each item dict).
    """
    # retrieve item price requester
    item_price_requeter = ITEM_PRICE_SOURCE_TO_REQUESTER.get(source, "html")

    # obtain each item price in-place and 'in parallel'
    async with aiohttp.ClientSession() as session:
        print(f"Requesting {len(items)} items")
        for index, item in enumerate(items):
            print(f"Requesting item {index + 1}/{len(items)}")
            await item_price_requeter(session, item, currency)

            # as per stackoverflow issues, api is limited to 20 requests / minute
            # using 11 seconds of delay between requests to play safe
            await asyncio.sleep(11)


##
# Exposed function to get price for a batch of items
##
async def add_items_price(
    items, currency = CURRENCIES["BRL"], source = "html", mode = "linear"
):
    """
    Proxy the desired way of requesting steam API, in parallel or linearly.

    :param items: list of items dictionaries with app_id and market_hash_name keys.
    :param currency: currency to retrieve the price.
    :param source: source to get information from. One of "overview", "history", "html"
    :param mode: how to retrieve info: in parallel or linearly.

    :returns: nothing (set the price in-place on each item dict).
    """
    if mode == "linear":
        await _add_items_price_linear(items, currency, source)
    elif mode == "parallel":
        await _add_items_price_parallel(items, currency, source)
    else:
        print("Invalid items price adder mode")

async def add_item_price(item, currency = CURRENCIES["BRL"], source = "html"):
    """
    Proxy the desired way of requesting steam API, in parallel or linearly.

    :param item: item dictionary with app_id and market_hash_name keys.
    :param currency: currency to retrieve the price.
    :param source: source to get information from. One of "overview", "history", "html"

    :returns: nothing (set the price in-place on each item dict).
    """
    # retrieve item price requester
    item_price_requeter = ITEM_PRICE_SOURCE_TO_REQUESTER.get(source)

    # obtain each item price in-place and 'in parallel'
    async with aiohttp.ClientSession() as session:
        await item_price_requeter(session, item, currency)

        # as per stackoverflow issues, api is limited to 20 requests / minute
        # using 11 seconds of delay between requests to play safe
        await asyncio.sleep(11)
