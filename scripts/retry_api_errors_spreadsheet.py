import argparse
import asyncio
from datetime import datetime

from data_exporters.pandas_excel_exporter import PandasExcelExporter
from data_readers.excel_reader import ExcelReader
from external_apis.steam.api import SteamAPI


async def main(excel_file_name: str):
    # check if we can get prices for most recent sheet
    excel_reader = ExcelReader(excel_file_name)
    most_recent_sheet = excel_reader.get_most_recent_date_sheet_name()
    today_date = datetime.utcnow().strftime("%Y-%m-%d")
    if most_recent_sheet != today_date:
        print(
            f"ABORTING. Can only check for api errors on current date ({today_date}). ",
            f"Most recent sheet is from {most_recent_sheet}",
        )
        return

    # get items with errors
    items = excel_reader.get_items()
    items_with_api_error = [item for item in items if item.api_error == "yes"]

    # all items succeeded -> stop
    if len(items_with_api_error) == 0:
        print(f"No items on current date ({today_date}) had API errors")
        return

    # retrieve price for items with error
    steam_api = SteamAPI()
    items_with_api_error_with_price = await steam_api.items.add_items_price(items_with_api_error)

    # reconciliate items
    items_without_error = [item for item in items if item.api_error == "no"]
    updated_items = items_without_error + items_with_api_error_with_price
    updated_items_sorted = sorted(updated_items, key=lambda item: f"{item.app_id}-{item.name}")

    # export data
    excel_exporter = PandasExcelExporter(excel_file_name)
    excel_exporter.export_today_items(updated_items_sorted)


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
