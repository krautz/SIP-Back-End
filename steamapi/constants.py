BASE_URL = "https://steamcommunity.com"

USER_INVENTOR_URL = BASE_URL + "/inventory/{steam_user_id}/{app_id}/2?l={language}&count=5000"

# NOTE
#       ITEM_PRICE_URL - Provides the lowest and median price. This route sometimes return null (not
#       sure why. but due to that, last resource was to use history route)
#
#       ITEM_PRICE_HISTORY_URL - Provides the price for all days per hour of each item, and this
#       request always succeeds. For old days it provides a single price for the day, for recent
#       days (i.e. last 2~3 months) it provides price per hour
#
#       ITEM_PRICE_MARKET_HMTL_URL - Provides the html market item listing source code. From there
#       we can extract the history of prices, but only in USD, because price configuration is
#       retrieved from logged in user cookies
ITEM_PRICE_OVERVIEW_URL = BASE_URL + "/market/priceoverview/?appid={app_id}&currency={currency}&market_hash_name={market_hash_name}"
ITEM_PRICE_HISTORY_URL = BASE_URL + "/market/pricehistory/?appid={app_id}&currency={currency}&market_hash_name={market_hash_name}"
ITEM_PRICE_MARKET_HMTL_URL = "https://steamcommunity.com/market/listings/{app_id}/{market_hash_name}"

CURRENCIES = {
    "BRL": 7,
    "EUR": 3,
    "USD": 1,
}
