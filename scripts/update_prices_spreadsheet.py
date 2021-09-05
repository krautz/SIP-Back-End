import asyncio
import pandas as pd
import argparse

from scripts.common import write_items_to_excel
from steamapi.item_price import add_items_price


async def main(
    excel_file_name,
    item_names_language,
    currency,
    item_price_source,
    item_price_retrieval_mode,
):
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
    # creates an argparse object to parse command line option
    parser = argparse.ArgumentParser(description = "Build spreadsheet with an user's desired items")
    parser.add_argument(
        "excel_file_name",
        help = "Which file name to use. Do not add extension to it, .xlxs will be used. 'prices' is the default value",
        type = str,
    )
    parser.add_argument(
        '--item_names_language',
        dest = "item_names_language",
        help = "Language to display item names ('portuguese' (default), 'english')",
        type = str,
        default = "portuguese",
    )
    parser.add_argument(
        "--currency",
        dest = "currency",
        help = "Currency to retrive prices (default: 7 -> BRL). Reminder: 'html' fetch mode will only retrieve prices in USD",
        type = int,
        default = 7,
    )
    parser.add_argument(
        "--item_price_source",
        dest = "item_price_source",
        help = "How to retrive prices. Options: overview, history or html. Note: use html always",
        type = str,
        default = "html",
    )
    parser.add_argument(
        "--item_price_retrieval_mode",
        dest = "item_price_retrieval_mode",
        help = "How to trigger requests to steam API: linear (default) or parallel (will rate limit you)",
        type = str,
        default = "linear",
    )

    # waits for command line input
    # (proceeds only if it is validated against the options set before)
    args = parser.parse_args()

    # validate provided input
    if args.item_names_language not in ["english", "portuguese"]:
        print("Invalid chosen language, choose either 'english' or 'portuguese'")
        exit()
    if args.item_price_source not in ["html", "overview", "history"]:
        print("Invalid chosen language, choose either 'html', 'overview' or 'history'")
        exit()
    if args.item_price_retrieval_mode not in ["linear", "parallel"]:
        print("Invalid chosen language, choose either 'linear' or 'parallel'")
        exit()

    # start async loop
    asyncio.run(main(
        args.excel_file_name + ".xlsx",
        args.item_names_language,
        args.currency,
        args.item_price_source,
        args.item_price_retrieval_mode,
    ))
