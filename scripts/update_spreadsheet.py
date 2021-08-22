import asyncio
import pandas as pd

from scripts.common import write_items_to_excel
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

    # load spreadshet into dataframe
    items_data_frame = pd.read_excel(spreadsheet_name)

    # remove summary_line
    number_of_lines = items_data_frame.shape[0]
    items_data_frame = items_data_frame.drop([number_of_lines - 1])

    # turn the dataframe into an array of dictioanries
    items = items_data_frame.to_dict('records')

    # retrieve price for items
    await add_items_price(
        items, currency, item_price_source, item_price_retrieval_mode
    )

    # write to xlsx file
    write_items_to_excel(items, spreadsheet_name)

if __name__ == "__main__":
    asyncio.run(main())
