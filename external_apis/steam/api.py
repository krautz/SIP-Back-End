from httpx import AsyncClient, Timeout

from external_apis.steam.constants import REQUEST_TIMEOUT
from external_apis.steam.inventory import SteamInventoryAPI
from external_apis.steam.items import SteamItemsAPI


class SteamAPI:
    def __init__(self, session: AsyncClient | None = None):
        self.session = session or AsyncClient(timeout=Timeout(REQUEST_TIMEOUT))
        self.inventory = SteamInventoryAPI(self.session)
        self.items = SteamItemsAPI(self.session)
