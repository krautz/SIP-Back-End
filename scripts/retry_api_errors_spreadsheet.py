import argparse
import asyncio
from datetime import datetime

import pandas as pd

from scripts.common import write_items_to_excel
from steamapi.item_price import add_item_price


async def main(excel_file_name):
    # get latest day spreadsheet name
    excel_file = pd.ExcelFile(excel_file_name)
    excel_file.sheet_names.sort()
    most_recent_day_sheet = excel_file.sheet_names[-2]

    # get today date
    today_date = datetime.utcnow().strftime("%Y-%m-%d")

    # most recent sheet is not from today -> abort
    if today_date != most_recent_day_sheet:
        print(
            f"ABORTING. Can only check for api errors on current date ({today_date}). ",
            f"Most recent spreadsheet is from {most_recent_day_sheet}",
        )
        return

    # read excel needed sheets into dataframes
    summary_df = excel_file.parse("Summary")
    items_df = excel_file.parse(most_recent_day_sheet)

    # remove summary line from items data frame
    number_of_lines = items_df.shape[0]
    items_df = items_df.drop([number_of_lines - 1])

    # turn the dataframes into list of dictionaries
    items = items_df.to_dict("records")
    summary = summary_df.to_dict("records")

    # retrieve price for items
    for item in items:
        if item["api_error"] == "yes":
            print(f"Re-requesting data for previous api error for item {item['name']}")
            await add_item_price(item)

    # write to xlsx file
    write_items_to_excel(items, summary, excel_file_name)


if __name__ == "__main__":
    # creates an argparse object to parse command line option
    parser = argparse.ArgumentParser(
        description="Retry to get item prices for api error items. This script can only be run if the most recent spreadsheet is from today date"
    )
    parser.add_argument(
        "excel_file_name",
        help="Which file name to use. Do not add extension to it, .xlxs will be used. 'prices' is the default value",
        type=str,
    )

    # waits for command line input
    # (proceeds only if it is validated against the options set before)
    args = parser.parse_args()

    # start async loop
    asyncio.run(main(args.excel_file_name + ".xlsx"))
