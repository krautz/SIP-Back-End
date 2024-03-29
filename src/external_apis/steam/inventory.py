from copy import deepcopy

from httpx import AsyncClient

from external_apis.steam.constants import USER_INVENTOR_URL
from external_apis.steam.models import Inventory, InventoryAsset, InventoryDescription
from models.items import Item


class SteamInventoryAPI:
    def __init__(self, session: AsyncClient | None = None):
        self.session = session or AsyncClient()

    def _filter_marketable_items(
        self, inventory_descriptions: list[InventoryDescription]
    ) -> list[InventoryDescription]:
        """
        Filter user items to include only the ones that are marketable

        :param inventory_descriptions: user api inventory description from an app

        :returns: marketable items
        """
        return list(filter(lambda item: item.marketable == 1, inventory_descriptions))

    def _format_marketable_items(self, marketable_items: list[InventoryDescription]) -> dict[str, Item]:
        """
        Format marketable items to include only needed properties

        :param marketable_items: marketable items

        :returns: formatted items with only needed properties
        """
        formatted_items: dict[str, Item] = {}
        for item in marketable_items:
            formatted_items[item.market_hash_name] = Item(
                amount=0,  # amount is present on api response assets. just initializing it.
                app_id=item.app_id,  # game code that has the item
                market_hash_name=item.market_hash_name,  # item 'id' to requst price later
                name=item.market_name,  # item human friendly name
            )
        return formatted_items

    def _map_item_class_id_to_market_hash_name(self, marketable_items: list[InventoryDescription]) -> dict[str, str]:
        """
        Build a map of user items class id to market hash name

        :param marketable_items: marketable items

        :returns: formatted items with only needed properties
        """
        class_id_to_market_hash_name: dict[str, str] = {
            item.class_id: item.market_hash_name for item in marketable_items
        }
        return class_id_to_market_hash_name

    def _compute_items_amount(
        self,
        items: dict[str, Item],
        inventory_assets: list[InventoryAsset],
        item_class_id_to_market_hash_name: dict[str, str],
    ) -> dict[str, Item]:
        """
        Compute each item amount

        :param items: formatted items
        :param inventory_assets: user api items asset from an app
        :param item_class_id_to_market_hash_name: mapper of class_id to market_hash_name

        :returns: items with amount
        """
        items_with_amount = deepcopy(items)
        for inventory_asset in inventory_assets:
            market_hash_hame = item_class_id_to_market_hash_name.get(inventory_asset.class_id)
            if market_hash_hame:
                items_with_amount[market_hash_hame].amount += int(inventory_asset.amount)
        return items_with_amount

    async def get_user_app_indexed_items(
        self, steam_user_id: int, app_id: int, language: str = "english"
    ) -> dict[str, Item]:
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
        user_inventory = Inventory.model_validate(response.json())

        # format items
        marketable_items = self._filter_marketable_items(user_inventory.descriptions)
        item_class_id_to_market_hash_name = self._map_item_class_id_to_market_hash_name(marketable_items)
        formatted_marketable_items = self._format_marketable_items(marketable_items)
        items_with_amount = self._compute_items_amount(
            formatted_marketable_items, user_inventory.assets, item_class_id_to_market_hash_name
        )

        return items_with_amount

    async def get_user_app_items(self, steam_user_id: int, app_id: int, language: str = "english") -> list[Item]:
        """
        Get all user's marketable items for a given app

        :param steam_user_id: steam user id
        :param app_id: app id
        :param language: which language we should display the item names in the output sheet

        :returns: user's marketable app's items
        """
        items = await self.get_user_app_indexed_items(steam_user_id, app_id, language)
        return list(items.values())
