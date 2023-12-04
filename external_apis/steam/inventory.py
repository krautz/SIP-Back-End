from copy import deepcopy

from httpx import AsyncClient

from steamapi.constants import USER_INVENTOR_URL


class SteamInventoryAPI:
    def __init__(self):
        self.session = AsyncClient()

    def _filter_marketable_items(self, user_items_description: list[dict]) -> list[dict]:
        """
        Filter user items to include only the ones that are marketable

        :param user_items_description: user api items description from an app

        :returns: marketable items
        """
        return list(filter(lambda item: item["marketable"] == 1, user_items_description))

    def _format_marketable_items(self, marketable_items: list[dict]) -> dict[str, dict]:
        """
        Format marketable items to include only needed properties

        :param marketable_items: marketable items

        :returns: formatted items with only needed properties
        """
        formatted_items: dict[str, dict] = {}
        for item in marketable_items:
            item_market_hash_name = item["market_hash_name"]
            formatted_items[item_market_hash_name] = {
                "amount": 0,  # amount is present on api response assets. just initializing it.
                "app_id": item["appid"],  # game code that has the item
                "market_hash_name": item_market_hash_name,  # item 'id' to requst price later
                "name": item["market_name"],  # item human friendly name
            }
        return formatted_items

    def _map_item_class_id_to_market_hash_name(self, user_items: list[dict]) -> dict[str, str]:
        """
        Build a map of user items class id to market hash name

        :param marketable_items: marketable items

        :returns: formatted items with only needed properties
        """
        class_id_to_market_hash_name: dict[str, str] = {
            item["classid"]: item["market_hash_name"] for item in user_items
        }
        return class_id_to_market_hash_name

    def _compute_items_amount(
        self, items: dict[str, dict], user_items_asset: list[dict], item_class_id_to_market_hash_name: dict[str, str]
    ) -> dict[str, dict]:
        """
        Compute each item amount

        :param items: formatted items
        :param user_items_asset: user api items asset from an app
        :param item_class_id_to_market_hash_name: mapper of class_id to market_hash_name

        :returns: items with amount
        """
        items_with_amount = deepcopy(items)
        for item_asset in user_items_asset:
            item_asset_class_id = item_asset["classid"]
            market_hash_hame = item_class_id_to_market_hash_name.get(item_asset_class_id)
            if market_hash_hame:
                items_with_amount[market_hash_hame]["amount"] += int(item_asset["amount"])
        return items_with_amount

    async def get_user_app_indexed_items(
        self, steam_user_id: int, app_id: int, language: str = "english"
    ) -> dict[str, dict]:
        """
        Get all user's marketable items for a given app indexed by its hash name

        :param steam_user_id: steam user id
        :param app_id: app id
        :param language: which language we should display the item names in the output sheet

        :returns: user's marketable app's items indexed by its hash name
        """
        # request items
        url = USER_INVENTOR_URL.format(steam_user_id=steam_user_id, app_id=app_id, language=language)
        response = await self.session.get(url)
        assert response.status_code == 200
        user_app_items: list[dict] = response.json()

        # format items
        marketable_items = self._filter_marketable_items(user_app_items["descriptions"])
        item_class_id_to_market_hash_name = self._map_item_class_id_to_market_hash_name(marketable_items)
        formatted_marketable_items = self._format_marketable_items(marketable_items)
        items_with_amount = self._compute_items_amount(
            formatted_marketable_items, user_app_items["assets"], item_class_id_to_market_hash_name
        )

        return items_with_amount

    async def get_user_app_items(self, steam_user_id: int, app_id: int, language: str = "english") -> list[dict]:
        """
        Get all user's marketable items for a given app

        :param steam_user_id: steam user id
        :param app_id: app id
        :param language: which language we should display the item names in the output sheet

        :returns: user's marketable app's items
        """
        items = await self.get_user_app_indexed_items(steam_user_id, app_id, language)
        return list(items.values())
