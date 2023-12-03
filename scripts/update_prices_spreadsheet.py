import argparse
import asyncio

import pandas as pd

from scripts.common import write_items_to_excel
from steamapi.item_price import add_items_price


async def main(excel_file_name, item_names_language):
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
    items = items_df.to_dict("records")
    summary = summary_df.to_dict("records")

    # retrieve price for items
    await add_items_price(items)

    # write to xlsx file
    write_items_to_excel(items, summary, excel_file_name)


if __name__ == "__main__":
    # creates an argparse object to parse command line option
    parser = argparse.ArgumentParser(
        description="Update today spreadsheet with most up to date prices or add a new spreadsheet if today date does not have it's own spreadsheet yet"
    )
    parser.add_argument(
        "excel_file_name",
        help="Which file name to use. Do not add extension to it, .xlxs will be used. 'prices' is the default value",
        type=str,
    )
    parser.add_argument(
        "--item_names_language",
        dest="item_names_language",
        help="Language to display item names ('portuguese' (default), 'english')",
        type=str,
        default="portuguese",
    )

    # waits for command line input
    # (proceeds only if it is validated against the options set before)
    args = parser.parse_args()

    # validate provided input
    if args.item_names_language not in ["english", "portuguese"]:
        print("Invalid chosen language, choose either 'english' or 'portuguese'")
        exit()

    # start async loop
    asyncio.run(main(args.excel_file_name + ".xlsx", args.item_names_language))
