import argparse
import asyncio

from data_exporters.pandas_excel_exporter import PandasExcelExporter
from external_apis.steam.api import SteamAPI


async def main(steam_id: int, app_ids: list[int], item_names_language: str, excel_file_name: str):
    # get user's inventory
    steam_api = SteamAPI()
    user_items = []
    for app_id in app_ids:
        app_items = await steam_api.inventory.get_user_app_items(steam_id, app_id, item_names_language)
        user_items.extend(app_items)
    sorted(user_items, key=lambda item: f"{item['app_id']}-{item['name']}")

    # filter out unwanted items
    user_filtered_items = []
    for item in user_items[:3]:
        add = input(
            f"Would you like to add {item['name']} (app {item['app_id']}) to the spreadsheet?" "(answer with y or n) "
        )
        if add == "y":
            user_filtered_items.append(item)

    # retrieve price for filtered items
    user_filtered_items_with_price = await steam_api.items.add_items_price(user_filtered_items)

    # export data
    excel_exporter = PandasExcelExporter(excel_file_name)
    excel_exporter.export_today_items(user_filtered_items_with_price)


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
            args.excel_file_name + ".xlsx",
        )
    )
