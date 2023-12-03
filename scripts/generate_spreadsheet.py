import argparse
import asyncio

from data_exporters.pandas_excel_exporter import PandasExcelExporter
from steamapi.inventory import get_user_inventory
from steamapi.item_price import add_items_price


async def main(steam_id, app_ids, item_names_language, sort_by_name, excel_file_name):
    # get user's inventory
    user_items = []
    for app_id in app_ids:
        user_items += await get_user_inventory(steam_id, app_id, item_names_language)

    # sort items by name
    if sort_by_name:
        user_items.sort(key=lambda item: item["name"])

    # filter out unwanted items
    user_filtered_items = []
    for item in user_items[:3]:
        add = input(
            f"Would you like to add {item['name']} (app {item['app_id']}) to the spreadsheet?" "(answer with y or n) "
        )
        if add == "y":
            user_filtered_items.append(item)

    # retrieve price for filtered items
    await add_items_price(user_filtered_items)

    # sort items by app id
    user_filtered_items.sort(key=lambda item: item["app_id"])

    # export data
    excel_exporter = PandasExcelExporter(excel_file_name)
    excel_exporter.export_today_items(user_filtered_items)


if __name__ == "__main__":
    # creates an argparse object to parse command line option
    parser = argparse.ArgumentParser(description="Build spreadsheet with an user's desired items")
    parser.add_argument(
        "steam_id",
        help="Users's Steam id (search for 'ID Steam' on 'https://store.steampowered.com/account')",
        type=int,
    )
    parser.add_argument(
        "--app_ids",
        dest="app_ids",
        help="App ids to retrieve items from. CSGO is 730. Check all at 'https://steamdb.info/'",
        nargs="+",
        type=int,
        default=[730],
    )
    parser.add_argument(
        "--item_names_language",
        dest="item_names_language",
        help="Language to display item names ('portuguese' (default), 'english')",
        type=str,
        default="portuguese",
    )
    parser.add_argument(
        "--excel_file_name",
        dest="excel_file_name",
        help="Which file name to use. Do not add extension to it, .xlxs will be used. 'prices' is the default value",
        type=str,
        default="prices",
    )
    parser.add_argument(
        "--sort_by_name",
        dest="sort_by_name",
        help="Items are sorted by time the got in the inventory. Set this to true to sort by name",
        type=bool,
        default=False,
    )

    # waits for command line input
    # (proceeds only if it is validated against the options set before)
    args = parser.parse_args()

    # validate provided input
    if args.item_names_language not in ["english", "portuguese"]:
        print("Invalid chosen language, choose either 'english' or 'portuguese'")
        exit()

    # start async loop
    asyncio.run(
        main(
            args.steam_id,
            args.app_ids,
            args.item_names_language,
            args.sort_by_name,
            args.excel_file_name + ".xlsx",
        )
    )
