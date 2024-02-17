BASE_URL = "https://steamcommunity.com"

USER_INVENTOR_URL = BASE_URL + "/inventory/{steam_user_id}/{app_id}/2?l={language}&count=5000"

ITEM_PRICE_OVERVIEW_URL = (
    BASE_URL + "/market/priceoverview/?appid={app_id}&currency={currency}&market_hash_name={market_hash_name}"
)
ITEM_PRICE_HISTORY_URL = (
    BASE_URL + "/market/pricehistory/?appid={app_id}&currency={currency}&market_hash_name={market_hash_name}"
)
ITEM_PRICE_MARKET_HMTL_URL = BASE_URL + "/market/listings/{app_id}/{market_hash_name}"

CURRENCIES = {
    "BRL": 7,
    "EUR": 3,
    "USD": 1,
}

REQUEST_TIMEOUT = 30

REQUEST_AWAIT_INTERVAL = 12
