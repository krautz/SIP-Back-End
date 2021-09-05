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
    excel_file_name = "cs_go_items_prices" + ".xlsx"

    # get items and summary as dataframes
    excel_file = pd.ExcelFile(excel_file_name)
    summary_sheet_index = excel_file.sheet_names.index("Summary")
    any_date_sheet = excel_file.sheet_names[summary_sheet_index - 1]
    summary_df = excel_file.parse("Summary")
    items_df = excel_file.parse(any_date_sheet)

    # remove summary line from items data frame
    number_of_lines = items_df.shape[0]
    items_df = items_df.drop([number_of_lines - 1])

    # turn the dataframes into list of dictionaries
    items = items_df.to_dict('records')
    summary = summary_df.to_dict('records')

    # retrieve price for items
    await add_items_price(items, currency, item_price_source, item_price_retrieval_mode)

    # write to xlsx file
    write_items_to_excel(items, summary, excel_file_name)

if __name__ == "__main__":
    asyncio.run(main())
