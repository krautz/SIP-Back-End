import asyncio
import json
import re
from datetime import datetime
from time import time
from typing import Callable

from httpx import AsyncClient, RequestError

from external_apis.steam.constants import (
    CURRENCIES,
    ITEM_PRICE_HISTORY_URL,
    ITEM_PRICE_MARKET_HMTL_URL,
    ITEM_PRICE_OVERVIEW_URL,
)
from external_apis.steam.exceptions import SteamItemsAPIException
from models.items import AnyItem, ItemWithPrice


class SteamItemsAPI:
    def __init__(self, session: AsyncClient | None = None):
        self.session = session or AsyncClient()

    async def _get_price_from_history(self, item: AnyItem, currency: str) -> float:
        """
        Request Steam API item price through history API.
        This API provides the median sold value of each day for old days and median sold value per hour
        on recent days (last 2~3 months)

        The problem of this approach is that it needs the user to be logged in the browser to work :(
        (it uses login cookies to work)

        :param item: item dict.
        :param currency: currency to retrieve the price.

        :returns: item's price.
        """
        # set item price url
        url = ITEM_PRICE_HISTORY_URL.format(
            app_id=item.app_id,
            market_hash_name=item.market_hash_name,
            currency=currency,
        )

        # request item price
        try:
            response = await self.session.get(url)
        except RequestError as exc:
            message = exc.message if hasattr(exc, "message") else None
            raise SteamItemsAPIException(item.name, item.market_hash_name, f"Request Error: {message}") from exc

        # extract item price
        response_data: dict = response.json()
        if response_data and response_data.get("success"):
            return response_data["prices"][-1][1]
        raise SteamItemsAPIException(item.name, item.market_hash_name, response.status_code)

    async def _get_price_from_overview(self, item: AnyItem, currency: str) -> float:
        """
        Request Steam API item last sold lowest price through overview API.

        The problem of this approach is that steam rate limit requests pretty quickly :(

        :param item: item dictionary
        :param currency: currency to retrieve the price

        :returns: item price
        """
        # set item price url
        url = ITEM_PRICE_OVERVIEW_URL.format(
            app_id=item.app_id,
            market_hash_name=item.market_hash_name,
            currency=currency,
        )

        # request item price
        try:
            response = await self.session.get(url)
        except RequestError as exc:
            message = exc.message if hasattr(exc, "message") else None
            raise SteamItemsAPIException(item.name, item.market_hash_name, f"Request Error: {message}") from exc

        # extract item price
        response_data: dict = response.json()
        if response_data and response_data.get("success"):
            return float(response_data["median_price"].split()[1])
        raise SteamItemsAPIException(item.name, item.market_hash_name, response.status_code)

    async def _get_price_from_market_html(self, item: AnyItem, **kwargs) -> float:
        """
        Request Steam web market item listing.
        There, we can extract the price history from the html.

        :param item: item dictionary

        :returns: item price
        """
        # set item price url
        url = ITEM_PRICE_MARKET_HMTL_URL.format(
            app_id=item.app_id,
            market_hash_name=item.market_hash_name,
        )

        # request item price
        try:
            response = await self.session.get(url)
        except RequestError as exc:
            message = exc.message if hasattr(exc, "message") else None
            raise SteamItemsAPIException(item.name, item.market_hash_name, f"Request Error: {message}") from exc

        # extract item price
        match = re.search(r"var line1=(.*?);", response.text)
        if match:
            item_price_history = json.loads(match.group(1))
            return item_price_history[-1][1]
        raise SteamItemsAPIException(item.name, item.market_hash_name, response.status_code, extra=response.text)

    def get_item_price_getter(self, price_source: str) -> Callable[[dict, str], float]:
        """
        Returns the function to get an item price given the desired retrieve mode

        :param price_source: which source to retrieve the item price from

        :returns: function to retrieve the price
        """
        price_source_to_item_price_getter: dict[str, Callable[[dict, str], float]] = {
            "html": self._get_price_from_market_html,
            "history": self._get_price_from_history,
            "overview": self._get_price_from_overview,
        }
        return price_source_to_item_price_getter[price_source]

    async def add_price_to_item(
        self, item: AnyItem, currency: str | None = None, price_source: str = "html"
    ) -> ItemWithPrice:
        """
        Get an item's price and returns an updated item dict with price info

        :param item: item to get price from
        :param currency: in which currency to get price from
        :param price_source: which source to retrieve the item price from

        :returns: item dict with new price properties
        """
        price_getter = self.get_item_price_getter(price_source)
        price_date = datetime.utcnow().strftime("%Y-%m-%d")
        price_timestamp = int(time())
        price = None
        try:
            price = await price_getter(item=item, currency=currency)
        except SteamItemsAPIException as exc:
            exc.log()
        item_with_price = ItemWithPrice(
            app_id=item.app_id,
            name=item.name,
            amount=item.amount,
            market_hash_name=item.market_hash_name,
            price_date=price_date,
            price_date_timestamp=price_timestamp,
            price_unitary=price,
            api_error="yes" if price is None else "no",
        )
        return item_with_price

    async def _add_items_price_concurrently(
        self, items: list[AnyItem], currency: str = CURRENCIES["BRL"], price_source: str = "html"
    ) -> list[ItemWithPrice]:
        """
        Request Steam API items last sold price and the date concurrently.

        The problem with this approach is that steam API returns 429 error - too many requests :(

        :param items: list of items dictionaries
        :param currency: currency to retrieve the price
        :param price_source: which source to retrieve the item price from. One of "overview", "history", "html"

        :returns: items dictionary with price info
        """
        tasks = [asyncio.ensure_future(self.add_price_to_item(item, currency, price_source)) for item in items]
        return await asyncio.gather(*tasks)

    async def _add_items_price_serialized(
        self, items: list[AnyItem], currency: str = CURRENCIES["BRL"], price_source: str = "html"
    ) -> list[ItemWithPrice]:
        """
        Request Steam API items last sold price and the date awaiting 11 second between requests.
        As per stackoverflow issues, api is limited to 20 requests / minute
        hence, using 11 seconds of delay between requests to play safe

        :param items: list of items dictionaries
        :param currency: currency to retrieve the price
        :param price_source: which source to retrieve the item price from. One of "overview", "history", "html"

        :returns: items dictionary with price info
        """
        items_with_price = []
        print(f"Requesting {len(items)} items")
        for index, item in enumerate(items):
            print(f"Requesting item {index + 1}/{len(items)}")
            item_with_price = await self.add_price_to_item(item, currency, price_source)
            items_with_price.append(item_with_price)
            await asyncio.sleep(11)
        return items_with_price

    async def add_items_price(
        self,
        items: list[AnyItem],
        currency: str = CURRENCIES["BRL"],
        price_source: str = "html",
        retrieve_mode: str = "serialized",
    ) -> list[ItemWithPrice]:
        """
        Proxy the desired way of requesting steam API, concurrently or serialized.

        :param items: list of items dictionaries
        :param currency: currency to retrieve the price
        :param price_source: which source to retrieve the item price from. One of "overview", "history", "html"
        :param retrieve_mode: how to retrieve info. Either "serialized" or "concurrently".

        :returns: items dictionary with price info
        """
        retrieve_mode_to_price_adder: dict[str, Callable[[list[dict], str, str], list[dict]]] = {
            "serialized": self._add_items_price_serialized,
            "concurrently": self._add_items_price_concurrently,
        }
        price_adder = retrieve_mode_to_price_adder[retrieve_mode]
        return await price_adder(items, currency, price_source)
