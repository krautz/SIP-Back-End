import asyncio
import argparse

from scripts.common import write_items_to_excel
from steamapi.inventory import get_user_inventory
from steamapi.item_price import add_items_price


async def main(
    steam_id,
    app_ids,
    item_names_language,
    currency,
    item_price_source,
    item_price_retrieval_mode,
    excel_file_name
):
    # get user's inventory
    user_items = []
    for app_id in app_ids:
        user_items += await get_user_inventory(steam_id, app_id, item_names_language)

    # sort items by name
    user_items.sort(key = lambda item: item["name"])

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

    # sort items by app id
    user_filtered_items.sort(key = lambda item: item["app_id"])

    # write to xlsx file
    write_items_to_excel(user_filtered_items, [], excel_file_name)

if __name__ == "__main__":
    # creates an argparse object to parse command line option
    parser = argparse.ArgumentParser(description = "Build spreadsheet with an user's desired items")
    parser.add_argument(
        "steam_id",
        help = "Users's Steam id (search for 'ID Steam' on 'https://store.steampowered.com/account')",
        type = int,
    )
    parser.add_argument(
        "--app_ids",
        dest = "app_ids",
        help = "App ids to retrieve items from. CSGO is 730. Check all at 'https://steamdb.info/'",
        nargs = "+",
        type = int,
        default = [730],
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
    parser.add_argument(
        "--excel_file_name",
        dest = "excel_file_name",
        help = "Which file name to use. Do not add extension to it, .xlxs will be used. 'prices' is the default value",
        type = str,
        default = "prices",
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
        args.steam_id,
        args.app_ids,
        args.item_names_language,
        args.currency,
        args.item_price_source,
        args.item_price_retrieval_mode,
        args.excel_file_name + ".xlsx"
    ))
