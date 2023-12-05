from httpx import AsyncClient

from external_apis.steam.inventory import SteamInventoryAPI
from external_apis.steam.items import SteamItemsAPI


class SteamAPI:
    def __init__(self, session: AsyncClient | None = None):
        self.session = session or AsyncClient()
        self.inventory = SteamInventoryAPI(self.session)
        self.items = SteamItemsAPI(self.session)
