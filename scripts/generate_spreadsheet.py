import asyncio
import pandas as pd

from datetime import datetime
from time import time

from steamapi.inventory import get_user_inventory
from steamapi.item_price import add_items_price


async def main():
    # variables to be threated as input in the future
    steam_id = 76561198066658320
    app_ids = [730]
    item_names_language = "portuguese"
    currency = 7  # reminder - with html mode only USD is possible
    item_price_source = "html"  # reminder only html does not rate limit with used sleep time
    item_price_retrieval_mode = "linear"  # reminder - parallel will rate limit you
    spreadsheet_name = "cs_go_items_prices" + ".xlsx"

    # get user's inventory
    user_items = []
    for app_id in app_ids:
        user_items += await get_user_inventory(steam_id, app_id, item_names_language)

    # filter out unwanted items
    user_filtered_items = []
    for item in user_items:
        add = input(
            f"Would you like to add {item['name']} (app {item['app_id']}) to the spreadsheet?" "(answer with y or n) "
        )
        if add == 'y':
            user_filtered_items.append(item)

    # retrieve price for filtered items
    await add_items_price(
        user_filtered_items, currency, item_price_source, item_price_retrieval_mode
    )

    # set the result as a dataframe and write to xlsx file
    items_data_frame = pd.DataFrame(user_filtered_items)
    items_data_frame["price_total"] = items_data_frame["price_unitary"] * items_data_frame["amount"]
    items_data_frame = items_data_frame.append(
        {
            "amount": items_data_frame["amount"].sum(),
            "app_id": "---",
            "market_hash_name": "---",
            "name": "Sum of all items",
            "price_unitary": "---",
            "price_total": items_data_frame["price_total"].sum(),
            "price_date": datetime.utcnow().strftime("%Y-%m-%d"),
            "price_date_timestamp": int(time())
        },
        ignore_index = True
    )
    items_data_frame.to_excel(spreadsheet_name, index=False)

if __name__ == "__main__":
    asyncio.run(main())
