class SteamItemsAPIException(Exception):
    def __init__(self, name: str, market_hash_name: str, status_code: int):
        self.name = name
        self.market_hash_name = market_hash_name
        self.status_code = status_code
        self.message = f"Error retrieving price for {self.name} ({self.market_hash_name}) - Status: {self.status_code}"
        super().__init__(self.message)

    def log(self):
        print(self.message)
